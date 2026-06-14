"""
EMBEDHUNT AI — Job Model
Phase A: Foundation

Embedded-software-specific job model.
Fields designed around the Qualcomm/Bosch/NXP/Continental job taxonomy.
"""

from typing import Optional
from sqlalchemy import String, Boolean, Text, Integer, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum

from app.db.base import BaseModel


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class JobStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    FILLED = "filled"


class ExperienceLevel(str, Enum):
    ENTRY = "entry"          # 0-2 years
    MID = "mid"              # 2-5 years
    SENIOR = "senior"        # 5-10 years
    LEAD = "lead"            # 8+ years
    PRINCIPAL = "principal"  # 12+ years


class WorkMode(str, Enum):
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class Job(BaseModel):
    __tablename__ = "jobs"

    # ─── Identity ─────────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    posted_by: Mapped[str] = mapped_column(String(36), nullable=False)  # user_id of recruiter

    # ─── Description ──────────────────────────────────────────────────────────
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nice_to_have: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ─── Classification ───────────────────────────────────────────────────────
    job_type: Mapped[JobType] = mapped_column(
        SAEnum(JobType, name="job_type_enum"), default=JobType.FULL_TIME
    )
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        SAEnum(ExperienceLevel, name="exp_level_enum"), default=ExperienceLevel.MID
    )
    work_mode: Mapped[WorkMode] = mapped_column(
        SAEnum(WorkMode, name="work_mode_enum"), default=WorkMode.ONSITE
    )
    status: Mapped[JobStatus] = mapped_column(
        SAEnum(JobStatus, name="job_status_enum"), default=JobStatus.DRAFT
    )

    # ─── Location ─────────────────────────────────────────────────────────────
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ─── Compensation ─────────────────────────────────────────────────────────
    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(10), default="INR")
    salary_period: Mapped[str] = mapped_column(String(20), default="annual")  # annual | monthly
    is_salary_visible: Mapped[bool] = mapped_column(Boolean, default=True)

    # ─── Embedded-Specific ────────────────────────────────────────────────────
    required_skills: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Comma-separated: C, RTOS, CAN, AUTOSAR, Linux Kernel, etc."
    )
    embedded_domains: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Comma-separated: automotive, iot, medical, defense, semiconductor"
    )
    protocols: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Comma-separated: CAN, LIN, SPI, I2C, Ethernet, etc."
    )
    mcu_platforms: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Comma-separated: ARM Cortex-M, RISC-V, Snapdragon, etc."
    )
    years_of_experience_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    years_of_experience_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ─── Application ──────────────────────────────────────────────────────────
    application_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    application_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    application_deadline: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    application_count: Mapped[int] = mapped_column(Integer, default=0)

    # ─── AI Fields (populated by Phase C) ────────────────────────────────────
    embedding_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_embedding_ready: Mapped[bool] = mapped_column(Boolean, default=False)

    # ─── Source (for auto-scraped jobs in Phase C) ────────────────────────────
    source_portal: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_job_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    is_auto_scraped: Mapped[bool] = mapped_column(Boolean, default=False)

    # ─── Metrics ──────────────────────────────────────────────────────────────
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title} company_id={self.company_id}>"
