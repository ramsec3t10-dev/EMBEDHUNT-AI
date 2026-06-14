"""
EMBEDHUNT AI — pytest conftest.py
Sets up test environment variables before any imports.
"""
import os
os.environ.setdefault("SECRET_KEY", "test-secret-key-minimum-32-characters-long!!")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("LOG_FORMAT", "text")
