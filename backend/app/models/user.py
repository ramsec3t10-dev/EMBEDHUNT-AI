"""
EMBEDHUNT AI — User Model
Phase A: Foundation
"""

from typing import Optional, List
from sqlalchemy import String, Boolean, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.core.security import UserRole


class User(BaseModel):
    __tablename__ = "users"

    # ─── Identity ─────────────────────────────────────────────────────────────
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # ─── Profile ──────────────────────────────────────────────────────────────
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ─── Access Control ───────────────────────────────────────────────────────
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role_enum"),
        default=UserRole.CANDIDATE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ─── Auth Metadata ────────────────────────────────────────────────────────
    last_login_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email_verify_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ─── Relationships (Phase B will expand these) ────────────────────────────
    # resumes = relationship("Resume", back_populates="user", lazy="selectin")
    # applications = relationship("Application", back_populates="candidate", lazy="selectin")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
