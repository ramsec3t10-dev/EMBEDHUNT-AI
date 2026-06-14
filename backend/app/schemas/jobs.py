"""Schemas for job ingestion, matching, and dashboard cards."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.job_ingestion import JobDecision, JobSourceKind, JobSourceStatus


class JobSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    kind: JobSourceKind
    status: JobSourceStatus
    base_url: Optional[str] = None


class CompanyWatchlistCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    careers_url: Optional[str] = Field(default=None, max_length=1000)
    priority: int = Field(default=100, ge=1, le=1000)
    tags: Optional[str] = None

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class CompanyWatchlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_name: str
    careers_url: Optional[str] = None
    is_active: bool
    priority: int
    tags: Optional[str] = None


class CompanyBlacklistRequest(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    reason: Optional[str] = Field(default=None, max_length=500)

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class ManualJobListingCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=300)
    source_url: Optional[str] = Field(default=None, max_length=1000)
    location: Optional[str] = Field(default=None, max_length=255)
    work_mode: Optional[str] = Field(default=None, max_length=50)
    salary_min_lpa: Optional[float] = Field(default=None, ge=0)
    salary_max_lpa: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = None
    required_skills: Optional[str] = None

    @field_validator("company_name", "title")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.strip().split())


class JobListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_name: str
    source_url: Optional[str] = None
    company_name: str
    title: str
    location: Optional[str] = None
    work_mode: Optional[str] = None
    salary_min_lpa: Optional[float] = None
    salary_max_lpa: Optional[float] = None
    currency: str
    required_skills: Optional[str] = None


class JobMatchDecisionRequest(BaseModel):
    decision: JobDecision


class JobMatchCard(BaseModel):
    match_id: Optional[str] = None
    job_id: str
    company_name: str
    title: str
    source_name: str
    source_url: Optional[str] = None
    location: Optional[str] = None
    ai_score: int
    salary_estimate: str
    resume_used: str
    explanation: str
    required_skills: list[str] = Field(default_factory=list)


class MockJobFeedResponse(BaseModel):
    jobs: list[JobMatchCard]
