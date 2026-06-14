"""
EMBEDHUNT AI — Database Base
Phase A: Foundation

SQLAlchemy 2.0 declarative base with common mixins.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base."""

    pass


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at to any model.
    Timestamps are always stored in UTC.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """Mixin that adds a UUID primary key."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )


class BaseModel(UUIDMixin, TimestampMixin, Base):
    """
    Abstract base model — use this for all EMBEDHUNT entities.
    Provides: UUID PK, created_at, updated_at.
    """

    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dict (for logging/debugging, not for API responses)."""
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
