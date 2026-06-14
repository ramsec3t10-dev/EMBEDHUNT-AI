"""
EMBEDHUNT AI — Auth API Router
Phase A: Foundation

Endpoints:
  POST /auth/register
  POST /auth/login
  POST /auth/refresh
  POST /auth/verify-email
  POST /auth/forgot-password
  POST /auth/reset-password
  GET  /auth/me
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new EMBEDHUNT AI account. A verification email will be sent.",
)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    service = AuthService(db)
    return await service.register(req)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login",
    description="Authenticate with email and password. Returns access and refresh tokens.",
)
async def login(
    req: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    client_ip = request.client.host if request.client else "unknown"
    service = AuthService(db)
    return await service.login(req, client_ip=client_ip)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new token pair.",
)
async def refresh_token(
    req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    return await service.refresh_tokens(req.refresh_token)


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address",
)
async def verify_email(
    req: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = AuthService(db)
    return await service.verify_email(req.token)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
)
async def forgot_password(
    req: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = AuthService(db)
    return await service.forgot_password(req.email)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password with token",
)
async def reset_password(
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = AuthService(db)
    return await service.reset_password(req.token, req.new_password)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the authenticated user's profile. Requires Bearer token.",
)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)
