"""
EMBEDHUNT AI — Auth Service
Phase A: Foundation

All authentication business logic lives here.
Repository handles DB, service handles business rules, API handles HTTP.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_email_verify_token,
    create_password_reset_token,
    decode_token,
    TokenType,
    UserRole,
)
from app.core.config import settings
from app.core.logging import get_logger, audit_logger
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    TokenResponse,
    UserResponse,
    MessageResponse,
)

logger = get_logger(__name__)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


class AuthService:
    """
    Orchestrates all authentication operations.
    Stateless — instantiated per-request with a DB session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def register(self, req: RegisterRequest) -> AuthResponse:
        """Register a new user. Sends verification email (when email is configured)."""

        # Check uniqueness
        if await self.repo.email_exists(req.email.lower()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )
        if await self.repo.username_exists(req.username.lower()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This username is already taken",
            )

        # Create user
        user = await self.repo.create(
            email=req.email.lower(),
            username=req.username.lower(),
            password_hash=hash_password(req.password),
            first_name=req.first_name.strip(),
            last_name=req.last_name.strip(),
            role=req.role,
            is_active=True,
            is_verified=False,  # Requires email verification
        )

        # Generate email verification token
        verify_token = create_email_verify_token(user.email)
        await self.repo.set_email_verify_token(user.id, verify_token)

        # TODO: Send verification email (Phase B — email service)

        audit_logger.log("user_registered", user_id=user.id, role=user.role.value)

        # Issue tokens immediately (user can use app, but some features gated on verify)
        return self._build_auth_response(user, message="Registration successful. Please verify your email.")

    async def login(self, req: LoginRequest, client_ip: str = "unknown") -> AuthResponse:
        """Authenticate user. Enforces account lockout after repeated failures."""

        user = await self.repo.get_by_email(req.email.lower())

        # Generic error — don't reveal whether email exists
        auth_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

        if not user:
            logger.warning("login_failed_no_user", email=req.email, ip=client_ip)
            raise auth_error

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Contact support.",
            )

        # Check lockout
        if user.locked_until:
            locked_dt = datetime.fromisoformat(user.locked_until)
            if datetime.now(timezone.utc) < locked_dt:
                minutes_left = int((locked_dt - datetime.now(timezone.utc)).total_seconds() / 60) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Account locked due to too many failed attempts. Try again in {minutes_left} minutes.",
                )

        # Verify password
        if not verify_password(req.password, user.password_hash):
            failed = await self.repo.increment_failed_login(user.id)
            audit_logger.login(user.id, client_ip, success=False)

            if failed >= MAX_FAILED_ATTEMPTS:
                lockout_until = (datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)).isoformat()
                from sqlalchemy import update
                from app.models.user import User
                await self.db.execute(
                    update(User).where(User.id == user.id).values(locked_until=lockout_until)
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed attempts. Account locked for {LOCKOUT_DURATION_MINUTES} minutes.",
                )

            raise auth_error

        # Success
        await self.repo.update_last_login(user.id)
        audit_logger.login(user.id, client_ip, success=True)

        return self._build_auth_response(user, message="Login successful")

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Exchange a valid refresh token for a new access + refresh token pair."""
        payload = decode_token(refresh_token, TokenType.REFRESH)
        user_id = payload["sub"]

        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated",
            )

        audit_logger.token_refresh(user_id)

        return TokenResponse(
            access_token=create_access_token(user.id, user.role),
            refresh_token=create_refresh_token(user.id),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def verify_email(self, token: str) -> MessageResponse:
        """Verify a user's email address using the token sent to their inbox."""
        payload = decode_token(token, TokenType.EMAIL_VERIFY)
        email = payload["sub"]

        user = await self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_verified:
            return MessageResponse(message="Email already verified")

        await self.repo.verify_email(user.id)
        audit_logger.log("email_verified", user_id=user.id)

        return MessageResponse(message="Email verified successfully")

    async def forgot_password(self, email: str) -> MessageResponse:
        """Initiate password reset flow. Always returns success (prevents email enumeration)."""
        user = await self.repo.get_by_email(email.lower())
        if user:
            token = create_password_reset_token(user.email)
            await self.repo.set_password_reset_token(user.id, token)
            # TODO: Send reset email (Phase B)
            logger.info("password_reset_requested", user_id=user.id)

        # Always return success — don't reveal if email exists
        return MessageResponse(message="If an account with that email exists, you will receive a password reset link.")

    async def reset_password(self, token: str, new_password: str) -> MessageResponse:
        """Reset a user's password using the token from their email."""
        payload = decode_token(token, TokenType.PASSWORD_RESET)
        email = payload["sub"]

        user = await self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await self.repo.update_password(user.id, hash_password(new_password))
        audit_logger.password_changed(user.id)

        return MessageResponse(message="Password reset successfully. You can now log in with your new password.")

    # ─── Internal ─────────────────────────────────────────────────────────────

    def _build_auth_response(self, user, message: str = "Success") -> AuthResponse:
        return AuthResponse(
            tokens=TokenResponse(
                access_token=create_access_token(user.id, user.role),
                refresh_token=create_refresh_token(user.id),
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            ),
            user=UserResponse.model_validate(user),
            message=message,
        )
