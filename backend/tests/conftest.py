"""
EMBEDHUNT AI — pytest conftest.py
Sets up test environment variables before any imports.
"""

import os

os.environ["SECRET_KEY"] = "test-secret-key-minimum-32-characters-long!!"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"
os.environ["APP_ENV"] = "test"
os.environ["DEBUG"] = "true"
os.environ["LOG_FORMAT"] = "text"
