"""Job ingestion and matching models."""

from enum import Enum
from typing import Optional

from sqlalchemy import Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class JobSourceKind(str, Enum):
    JOB_BOARD = "job_board"
    COMPANY_CAREERS = "company_careers"
    MANUAL = "manual"


class JobSourceStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class ScanRunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobListingStatus(str, Enum):
    NEW = "new"
    MATCHED = "matched"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLACKLISTED = "blacklisted"
    APPLIED = "applied"
    INTERVIEW = "interview"
    CLOSED = "closed"


class JobDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    SAVED = "saved"


class JobSource(BaseModel):
    __tablename__ = "job_sources"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    kind: Mapped[JobSourceKind] = mapped_column(
        SAEnum(JobSourceKind, name="job_source_kind_enum"),
        nullable=False,
    )
    status: Mapped[JobSourceStatus] = mapped_column(
        SAEnum(JobSourceStatus, name="job_source_status_enum"),
        default=JobSourceStatus.ACTIVE,
        nullable=False,
    )
    base_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class CompanyWatchlist(BaseModel):
    __tablename__ = "company_watchlist"

    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    careers_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class CompanyBlacklist(BaseModel):
    __tablename__ = "company_blacklist"
    __table_args__ = (
        UniqueConstraint("user_id", "company_name", name="uq_user_blacklisted_company"),
    )

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class JobScanRun(BaseModel):
    __tablename__ = "job_scan_runs"

    source_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    source_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[ScanRunStatus] = mapped_column(
        SAEnum(ScanRunStatus, name="scan_run_status_enum"),
        default=ScanRunStatus.QUEUED,
        nullable=False,
    )
    jobs_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class JobListing(BaseModel):
    __tablename__ = "job_listings"
    __table_args__ = (UniqueConstraint("source_name", "source_job_id", name="uq_source_job"),)

    source_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    source_job_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    work_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    salary_min_lpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max_lpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[JobListingStatus] = mapped_column(
        SAEnum(JobListingStatus, name="job_listing_status_enum"),
        default=JobListingStatus.NEW,
        nullable=False,
    )


class JobMatch(BaseModel):
    __tablename__ = "job_matches"
    __table_args__ = (UniqueConstraint("user_id", "job_listing_id", name="uq_user_job_match"),)

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    job_listing_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    ai_score: Mapped[int] = mapped_column(Integer, nullable=False)
    salary_estimate: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resume_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    resume_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision: Mapped[Optional[JobDecision]] = mapped_column(
        SAEnum(JobDecision, name="job_decision_enum"),
        nullable=True,
    )
