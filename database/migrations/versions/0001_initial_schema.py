"""Initial application schema.

Revision ID: 0001
Revises:
Create Date: 2026-06-14
"""

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


user_role_enum = sa.Enum(
    "CANDIDATE",
    "RECRUITER",
    "COMPANY_ADMIN",
    "PLATFORM_ADMIN",
    name="user_role_enum",
)
resume_status_enum = sa.Enum(
    "UPLOADED",
    "PARSING",
    "PARSED",
    "PARSE_FAILED",
    "EMBEDDING_READY",
    name="resume_status_enum",
)
job_type_enum = sa.Enum("FULL_TIME", "PART_TIME", "CONTRACT", "INTERNSHIP", "FREELANCE", name="job_type_enum")
exp_level_enum = sa.Enum("ENTRY", "MID", "SENIOR", "LEAD", "PRINCIPAL", name="exp_level_enum")
work_mode_enum = sa.Enum("ONSITE", "REMOTE", "HYBRID", name="work_mode_enum")
job_status_enum = sa.Enum("DRAFT", "ACTIVE", "PAUSED", "CLOSED", "FILLED", name="job_status_enum")
job_source_kind_enum = sa.Enum(
    "JOB_BOARD",
    "COMPANY_CAREERS",
    "MANUAL",
    name="job_source_kind_enum",
)
job_source_status_enum = sa.Enum("ACTIVE", "PAUSED", "DISABLED", name="job_source_status_enum")
scan_run_status_enum = sa.Enum("QUEUED", "RUNNING", "SUCCEEDED", "FAILED", name="scan_run_status_enum")
job_listing_status_enum = sa.Enum(
    "NEW",
    "MATCHED",
    "APPROVED",
    "REJECTED",
    "BLACKLISTED",
    "APPLIED",
    "INTERVIEW",
    "CLOSED",
    name="job_listing_status_enum",
)
job_decision_enum = sa.Enum("APPROVED", "REJECTED", "SAVED", name="job_decision_enum")


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("github_url", sa.String(length=500), nullable=True),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_premium", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.String(length=50), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False),
        sa.Column("locked_until", sa.String(length=50), nullable=True),
        sa.Column("email_verify_token", sa.String(length=500), nullable=True),
        sa.Column("password_reset_token", sa.String(length=500), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "companies",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("company_size", sa.String(length=50), nullable=True),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("headquarters", sa.String(length=200), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("domains", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_name"), "companies", ["name"], unique=False)
    op.create_index(op.f("ix_companies_slug"), "companies", ["slug"], unique=True)

    op.create_table(
        "jobs",
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("slug", sa.String(length=300), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("posted_by", sa.String(length=36), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("responsibilities", sa.Text(), nullable=True),
        sa.Column("nice_to_have", sa.Text(), nullable=True),
        sa.Column("job_type", job_type_enum, nullable=True),
        sa.Column("experience_level", exp_level_enum, nullable=True),
        sa.Column("work_mode", work_mode_enum, nullable=True),
        sa.Column("status", job_status_enum, nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("salary_min", sa.Float(), nullable=True),
        sa.Column("salary_max", sa.Float(), nullable=True),
        sa.Column("salary_currency", sa.String(length=10), nullable=False),
        sa.Column("salary_period", sa.String(length=20), nullable=False),
        sa.Column("is_salary_visible", sa.Boolean(), nullable=False),
        sa.Column("required_skills", sa.Text(), nullable=True),
        sa.Column("embedded_domains", sa.Text(), nullable=True),
        sa.Column("protocols", sa.Text(), nullable=True),
        sa.Column("mcu_platforms", sa.Text(), nullable=True),
        sa.Column("years_of_experience_min", sa.Integer(), nullable=True),
        sa.Column("years_of_experience_max", sa.Integer(), nullable=True),
        sa.Column("application_url", sa.String(length=1000), nullable=True),
        sa.Column("application_email", sa.String(length=255), nullable=True),
        sa.Column("application_deadline", sa.String(length=50), nullable=True),
        sa.Column("application_count", sa.Integer(), nullable=False),
        sa.Column("embedding_id", sa.String(length=100), nullable=True),
        sa.Column("is_embedding_ready", sa.Boolean(), nullable=False),
        sa.Column("source_portal", sa.String(length=100), nullable=True),
        sa.Column("source_job_id", sa.String(length=200), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("is_auto_scraped", sa.Boolean(), nullable=False),
        sa.Column("view_count", sa.Integer(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_company_id"), "jobs", ["company_id"], unique=False)
    op.create_index(op.f("ix_jobs_slug"), "jobs", ["slug"], unique=True)
    op.create_index(op.f("ix_jobs_title"), "jobs", ["title"], unique=False)

    op.create_table(
        "resumes",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("file_url", sa.String(length=1000), nullable=False),
        sa.Column("file_name", sa.String(length=300), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("file_type", sa.String(length=50), nullable=False),
        sa.Column("status", resume_status_enum, nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("parsed_skills", sa.Text(), nullable=True),
        sa.Column("parsed_experience", sa.Text(), nullable=True),
        sa.Column("parsed_education", sa.Text(), nullable=True),
        sa.Column("parsed_certifications", sa.Text(), nullable=True),
        sa.Column("embedding_id", sa.String(length=100), nullable=True),
        sa.Column("is_embedding_ready", sa.Boolean(), nullable=False),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("skill_score", sa.Float(), nullable=True),
        sa.Column("is_auto_generated", sa.Boolean(), nullable=False),
        sa.Column("generated_for_job_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resumes_user_id"), "resumes", ["user_id"], unique=False)

    op.create_table(
        "job_sources",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("kind", job_source_kind_enum, nullable=False),
        sa.Column("status", job_source_status_enum, nullable=False),
        sa.Column("base_url", sa.String(length=1000), nullable=True),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_sources_name"), "job_sources", ["name"], unique=True)

    op.create_table(
        "company_watchlist",
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("careers_url", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_company_watchlist_company_name"), "company_watchlist", ["company_name"], unique=False)

    op.create_table(
        "company_blacklist",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "company_name", name="uq_user_blacklisted_company"),
    )
    op.create_index(op.f("ix_company_blacklist_company_name"), "company_blacklist", ["company_name"], unique=False)
    op.create_index(op.f("ix_company_blacklist_user_id"), "company_blacklist", ["user_id"], unique=False)

    op.create_table(
        "job_scan_runs",
        sa.Column("source_id", sa.String(length=36), nullable=True),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("status", scan_run_status_enum, nullable=False),
        sa.Column("jobs_found", sa.Integer(), nullable=False),
        sa.Column("jobs_imported", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_scan_runs_source_id"), "job_scan_runs", ["source_id"], unique=False)

    op.create_table(
        "job_listings",
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("source_job_id", sa.String(length=255), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("work_mode", sa.String(length=50), nullable=True),
        sa.Column("salary_min_lpa", sa.Float(), nullable=True),
        sa.Column("salary_max_lpa", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("required_skills", sa.Text(), nullable=True),
        sa.Column("status", job_listing_status_enum, nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_name", "source_job_id", name="uq_source_job"),
    )
    op.create_index(op.f("ix_job_listings_company_name"), "job_listings", ["company_name"], unique=False)
    op.create_index(op.f("ix_job_listings_source_name"), "job_listings", ["source_name"], unique=False)
    op.create_index(op.f("ix_job_listings_title"), "job_listings", ["title"], unique=False)

    op.create_table(
        "job_matches",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("job_listing_id", sa.String(length=36), nullable=False),
        sa.Column("ai_score", sa.Integer(), nullable=False),
        sa.Column("salary_estimate", sa.String(length=100), nullable=True),
        sa.Column("resume_id", sa.String(length=36), nullable=True),
        sa.Column("resume_name", sa.String(length=255), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("decision", job_decision_enum, nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_listing_id", name="uq_user_job_match"),
    )
    op.create_index(op.f("ix_job_matches_job_listing_id"), "job_matches", ["job_listing_id"], unique=False)
    op.create_index(op.f("ix_job_matches_user_id"), "job_matches", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_job_matches_user_id"), table_name="job_matches")
    op.drop_index(op.f("ix_job_matches_job_listing_id"), table_name="job_matches")
    op.drop_table("job_matches")
    op.drop_index(op.f("ix_job_listings_title"), table_name="job_listings")
    op.drop_index(op.f("ix_job_listings_source_name"), table_name="job_listings")
    op.drop_index(op.f("ix_job_listings_company_name"), table_name="job_listings")
    op.drop_table("job_listings")
    op.drop_index(op.f("ix_job_scan_runs_source_id"), table_name="job_scan_runs")
    op.drop_table("job_scan_runs")
    op.drop_index(op.f("ix_company_blacklist_user_id"), table_name="company_blacklist")
    op.drop_index(op.f("ix_company_blacklist_company_name"), table_name="company_blacklist")
    op.drop_table("company_blacklist")
    op.drop_index(op.f("ix_company_watchlist_company_name"), table_name="company_watchlist")
    op.drop_table("company_watchlist")
    op.drop_index(op.f("ix_job_sources_name"), table_name="job_sources")
    op.drop_table("job_sources")
    op.drop_index(op.f("ix_resumes_user_id"), table_name="resumes")
    op.drop_table("resumes")
    op.drop_index(op.f("ix_jobs_title"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_slug"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_company_id"), table_name="jobs")
    op.drop_table("jobs")
    op.drop_index(op.f("ix_companies_slug"), table_name="companies")
    op.drop_index(op.f("ix_companies_name"), table_name="companies")
    op.drop_table("companies")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
