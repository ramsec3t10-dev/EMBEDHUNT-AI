"""
EMBEDHUNT AI — Resume Model
Phase A: Foundation
"""

from enum import Enum
from typing import Optional

from sqlalchemy import Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class ResumeStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    PARSE_FAILED = "parse_failed"
    EMBEDDING_READY = "embedding_ready"


class Resume(BaseModel):
    __tablename__ = "resumes"

    # ─── Ownership ────────────────────────────────────────────────────────────
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)  # "My Qualcomm Resume"
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    # ─── File ─────────────────────────────────────────────────────────────────
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_name: Mapped[str] = mapped_column(String(300), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_type: Mapped[str] = mapped_column(String(50), default="pdf")

    # ─── Processing ───────────────────────────────────────────────────────────
    status: Mapped[ResumeStatus] = mapped_column(
        SAEnum(ResumeStatus, name="resume_status_enum"),
        default=ResumeStatus.UPLOADED,
    )

    # ─── Parsed Content ───────────────────────────────────────────────────────
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    parsed_experience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    parsed_education: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    parsed_certifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ─── AI Fields ────────────────────────────────────────────────────────────
    embedding_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_embedding_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skill_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ─── Auto-customize tracking ──────────────────────────────────────────────
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_for_job_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    def __repr__(self) -> str:
        return f"<Resume id={self.id} user_id={self.user_id} name={self.name}>"
