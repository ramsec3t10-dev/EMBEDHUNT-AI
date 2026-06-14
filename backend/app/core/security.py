"""
EMBEDHUNT AI — Security Module
Phase A: Foundation

Handles all authentication and authorization:
- Password hashing (bcrypt)
- JWT token creation & verification
- Role-Based Access Control (RBAC)
- Token blacklisting via Redis
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from enum import Enum
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ─── Password Hashing ─────────────────────────────────────────────────────────

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # 12 rounds = ~250ms hash time (OWASP recommended)
)


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return pwd_context.verify(plain, hashed)


# ─── Roles ────────────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    COMPANY_ADMIN = "company_admin"
    PLATFORM_ADMIN = "platform_admin"


ROLE_HIERARCHY = {
    UserRole.PLATFORM_ADMIN: 4,
    UserRole.COMPANY_ADMIN: 3,
    UserRole.RECRUITER: 2,
    UserRole.CANDIDATE: 1,
}


# ─── JWT Tokens ───────────────────────────────────────────────────────────────

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"


def _create_token(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Internal token factory.
    Never call directly — use create_access_token / create_refresh_token.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,            # Subject (user ID)
        "type": token_type.value,  # Token type guard
        "iat": now,                # Issued at
        "exp": now + expires_delta,# Expiry
        "jti": str(uuid.uuid4()),  # JWT ID (for revocation)
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: str, role: UserRole) -> str:
    """Create a short-lived access token (30 min default)."""
    return _create_token(
        subject=user_id,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={"role": role.value},
    )


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token (7 days default)."""
    return _create_token(
        subject=user_id,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_email_verify_token(email: str) -> str:
    """Create a 24-hour email verification token."""
    return _create_token(
        subject=email,
        token_type=TokenType.EMAIL_VERIFY,
        expires_delta=timedelta(hours=24),
    )


def create_password_reset_token(email: str) -> str:
    """Create a 1-hour password reset token."""
    return _create_token(
        subject=email,
        token_type=TokenType.PASSWORD_RESET,
        expires_delta=timedelta(hours=1),
    )


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Raises:
        HTTPException 401 if token is invalid, expired, or wrong type.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # Type guard — prevent token type confusion attacks
        if payload.get("type") != expected_type.value:
            logger.warning("token_type_mismatch", expected=expected_type.value, got=payload.get("type"))
            raise credentials_exception

        if payload.get("sub") is None:
            raise credentials_exception

        return payload

    except JWTError as e:
        logger.warning("jwt_decode_error", error=str(e))
        raise credentials_exception


# ─── FastAPI Security Dependencies ────────────────────────────────────────────

bearer_scheme = HTTPBearer(auto_error=True)


async def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    """FastAPI dependency: extract and validate the Bearer token."""
    return decode_token(credentials.credentials, TokenType.ACCESS)


async def get_current_user_id(
    payload: dict = Depends(get_token_payload),
) -> str:
    """FastAPI dependency: returns the current authenticated user's ID."""
    return payload["sub"]


async def get_current_user_role(
    payload: dict = Depends(get_token_payload),
) -> UserRole:
    """FastAPI dependency: returns the current authenticated user's role."""
    role_str = payload.get("role", UserRole.CANDIDATE.value)
    return UserRole(role_str)


def require_role(*allowed_roles: UserRole):
    """
    FastAPI dependency factory for role-based access control.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role(UserRole.PLATFORM_ADMIN))])
    """
    async def _check(role: UserRole = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return role
    return _check


def require_min_role(min_role: UserRole):
    """
    FastAPI dependency: require a minimum role level (hierarchical check).

    Usage:
        @router.get("/", dependencies=[Depends(require_min_role(UserRole.RECRUITER))])
    """
    async def _check(role: UserRole = Depends(get_current_user_role)):
        if ROLE_HIERARCHY.get(role, 0) < ROLE_HIERARCHY.get(min_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Minimum role required: {min_role.value}",
            )
        return role
    return _check
