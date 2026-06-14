"""
EMBEDHUNT AI — Phase A Test Suite
Tests for: Auth endpoints, Security module, Config validation
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# ─── Unit Tests: Security ─────────────────────────────────────────────────────


class TestPasswordHashing:
    def test_hash_is_not_plain(self):
        from app.core.security import hash_password

        plain = "MySecurePass1"
        hashed = hash_password(plain)
        assert hashed != plain
        assert len(hashed) > 40

    def test_verify_correct_password(self):
        from app.core.security import hash_password, verify_password

        plain = "MySecurePass1"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_reject_wrong_password(self):
        from app.core.security import hash_password, verify_password

        hashed = hash_password("CorrectPass1")
        assert verify_password("WrongPass1", hashed) is False

    def test_different_hashes_same_password(self):
        """bcrypt uses salts — same password never produces same hash."""
        from app.core.security import hash_password

        plain = "SamePassword1"
        hash1 = hash_password(plain)
        hash2 = hash_password(plain)
        assert hash1 != hash2


class TestJWTTokens:
    def test_create_and_decode_access_token(self):
        from app.core.security import TokenType, UserRole, create_access_token, decode_token

        token = create_access_token("user-123", UserRole.CANDIDATE)
        payload = decode_token(token, TokenType.ACCESS)
        assert payload["sub"] == "user-123"
        assert payload["role"] == "candidate"
        assert payload["type"] == "access"

    def test_create_and_decode_refresh_token(self):
        from app.core.security import TokenType, create_refresh_token, decode_token

        token = create_refresh_token("user-456")
        payload = decode_token(token, TokenType.REFRESH)
        assert payload["sub"] == "user-456"

    def test_wrong_token_type_raises(self):
        from fastapi import HTTPException

        from app.core.security import TokenType, UserRole, create_access_token, decode_token

        access_token = create_access_token("user-789", UserRole.RECRUITER)
        with pytest.raises(HTTPException) as exc_info:
            decode_token(access_token, TokenType.REFRESH)  # Wrong type!
        assert exc_info.value.status_code == 401

    def test_tampered_token_raises(self):
        from fastapi import HTTPException

        from app.core.security import TokenType, UserRole, create_access_token, decode_token

        token = create_access_token("user-000", UserRole.CANDIDATE)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException):
            decode_token(tampered, TokenType.ACCESS)

    def test_email_verify_token(self):
        from app.core.security import TokenType, create_email_verify_token, decode_token

        token = create_email_verify_token("test@example.com")
        payload = decode_token(token, TokenType.EMAIL_VERIFY)
        assert payload["sub"] == "test@example.com"
        assert payload["type"] == "email_verify"


class TestUserRole:
    def test_role_hierarchy(self):
        from app.core.security import ROLE_HIERARCHY, UserRole

        assert ROLE_HIERARCHY[UserRole.PLATFORM_ADMIN] > ROLE_HIERARCHY[UserRole.COMPANY_ADMIN]
        assert ROLE_HIERARCHY[UserRole.COMPANY_ADMIN] > ROLE_HIERARCHY[UserRole.RECRUITER]
        assert ROLE_HIERARCHY[UserRole.RECRUITER] > ROLE_HIERARCHY[UserRole.CANDIDATE]


# ─── Unit Tests: Schemas ──────────────────────────────────────────────────────


class TestRegisterRequestSchema:
    def _make_valid(self, **overrides):
        from app.schemas.auth import RegisterRequest

        data = {
            "email": "ram@embedhunt.ai",
            "username": "ram_srihari",
            "password": "Bosch2024!",
            "first_name": "Ram",
            "last_name": "Sri Hari",
        }
        data.update(overrides)
        return RegisterRequest(**data)

    def test_valid_registration(self):
        req = self._make_valid()
        assert req.email == "ram@embedhunt.ai"
        assert req.username == "ram_srihari"

    def test_username_normalised_to_lowercase(self):
        req = self._make_valid(username="RAM_SRIHARI")
        assert req.username == "ram_srihari"

    def test_short_username_fails(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            self._make_valid(username="ab")

    def test_invalid_username_chars(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            self._make_valid(username="ram srihari")  # space not allowed

    def test_weak_password_no_uppercase(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            self._make_valid(password="lowercase1!")

    def test_weak_password_no_digit(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            self._make_valid(password="NoDigitPass!")

    def test_weak_password_too_short(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            self._make_valid(password="Ab1!")

    def test_invalid_email(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            self._make_valid(email="not-an-email")


# ─── Unit Tests: Config ───────────────────────────────────────────────────────


class TestConfig:
    def test_settings_loaded(self):
        from app.core.config import settings

        assert settings.APP_NAME == "EMBEDHUNT AI"
        assert settings.API_V1_PREFIX == "/api/v1"

    def test_is_development(self):
        from app.core.config import settings

        # In test environment, APP_ENV defaults to development
        assert settings.APP_ENV in ("development", "test")


# ─── Integration Tests (require DB — use mocks for CI) ───────────────────────


class TestAuthEndpoints:
    """
    These tests mock the DB layer.
    Full integration tests (with real DB) run in: tests/integration/
    """

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Health endpoint must always return 200."""
        import app.db.session as db_session

        db_session.check_db_connection = AsyncMock(return_value=True)
        from app.main import app as fastapi_app

        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        import app.db.session as db_session

        db_session.check_db_connection = AsyncMock(return_value=True)
        from app.main import app as fastapi_app

        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app), base_url="http://test"
        ) as client:
            resp = await client.get("/")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_invalid_register_returns_422(self):
        import app.db.session as db_session

        db_session.check_db_connection = AsyncMock(return_value=True)
        from app.main import app as fastapi_app

        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "bad-email",
                    "username": "x",
                    "password": "weak",
                    "first_name": "A",
                    "last_name": "B",
                },
            )
        assert resp.status_code == 422
        data = resp.json()
        assert "details" in data

    @pytest.mark.asyncio
    async def test_me_without_token_returns_403(self):
        import app.db.session as db_session

        db_session.check_db_connection = AsyncMock(return_value=True)
        from app.main import app as fastapi_app

        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 403
