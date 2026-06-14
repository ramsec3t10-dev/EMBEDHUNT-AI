"""
EMBEDHUNT AI — Core Configuration
Phase A: Foundation

Production-grade settings management using Pydantic v2.
Every config value is typed, validated, and documented.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings class. Values are loaded from environment variables
    (or .env file). All sensitive values MUST be provided via environment —
    no hardcoded secrets, ever.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "EMBEDHUNT AI"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ─── Server ───────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # ─── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str  # MUST be set in env — no default
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ─── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host:port/db
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_ECHO: bool = False  # Set True only for SQL debugging

    # ─── Redis ────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_DEFAULT_TTL: int = 300  # seconds

    # ─── Celery ───────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ─── Email ────────────────────────────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM: str = "noreply@embedhunt.ai"
    EMAILS_FROM_NAME: str = "EMBEDHUNT AI"

    # ─── Object Storage (MinIO / S3) ──────────────────────────────────────────
    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_RESUMES: str = "embedhunt-resumes"
    S3_BUCKET_ASSETS: str = "embedhunt-assets"

    # ─── AI / Vector DB ───────────────────────────────────────────────────────
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536

    # ─── Rate Limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10

    # ─── Observability ────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json | text
    ENABLE_METRICS: bool = True
    SENTRY_DSN: Optional[str] = None

    # ─── Feature Flags ────────────────────────────────────────────────────────
    FEATURE_AUTO_APPLY: bool = False  # Phase C — off until AI pipeline ready
    FEATURE_AI_MATCHING: bool = False  # Phase C
    FEATURE_INTERVIEW_GEN: bool = False  # Phase C

    # ─── Computed Properties ──────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def database_url_sync(self) -> str:
        """Synchronous DB URL for Alembic migrations."""
        return self.DATABASE_URL.replace("+asyncpg", "")


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings singleton.
    Use this everywhere — do NOT instantiate Settings() directly.
    """
    return Settings()


# Convenience alias used throughout the codebase
settings = get_settings()
