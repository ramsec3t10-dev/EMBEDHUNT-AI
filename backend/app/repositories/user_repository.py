"""
EMBEDHUNT AI — User Repository
Phase A: Foundation

Repository pattern: all DB queries for the User model live here.
Services call repositories — never raw SQLAlchemy in service layer.
"""

from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Data access layer for the User model."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        await self.db.flush()  # Get ID without committing
        await self.db.refresh(user)
        logger.info("user_created", user_id=user.id, email=user.email, role=user.role)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username.lower())
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        result = await self.db.execute(
            select(User.id).where(User.email == email.lower())
        )
        return result.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        result = await self.db.execute(
            select(User.id).where(User.username == username.lower())
        )
        return result.scalar_one_or_none() is not None

    async def update_last_login(self, user_id: str) -> None:
        from datetime import datetime, timezone
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                last_login_at=datetime.now(timezone.utc).isoformat(),
                failed_login_attempts=0,
                locked_until=None,
            )
        )

    async def increment_failed_login(self, user_id: str) -> int:
        result = await self.db.execute(
            select(User.failed_login_attempts).where(User.id == user_id)
        )
        current = result.scalar_one_or_none() or 0
        new_count = current + 1
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(failed_login_attempts=new_count)
        )
        return new_count

    async def set_email_verify_token(self, user_id: str, token: str) -> None:
        await self.db.execute(
            update(User).where(User.id == user_id).values(email_verify_token=token)
        )

    async def verify_email(self, user_id: str) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True, email_verify_token=None)
        )

    async def set_password_reset_token(self, user_id: str, token: str) -> None:
        await self.db.execute(
            update(User).where(User.id == user_id).values(password_reset_token=token)
        )

    async def update_password(self, user_id: str, password_hash: str) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash, password_reset_token=None)
        )
