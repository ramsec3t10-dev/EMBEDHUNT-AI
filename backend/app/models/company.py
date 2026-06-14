"""
EMBEDHUNT AI — Company Model
Phase A: Foundation
"""

from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class Company(BaseModel):
    __tablename__ = "companies"

    # ─── Identity ─────────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ─── Details ──────────────────────────────────────────────────────────────
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "51-200"
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    headquarters: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # ─── Contact ──────────────────────────────────────────────────────────────
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ─── Platform Status ──────────────────────────────────────────────────────
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ─── Embedded-specific tags ───────────────────────────────────────────────
    domains: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Comma-separated: automotive, iot, medical, defense, semiconductor",
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name}>"
