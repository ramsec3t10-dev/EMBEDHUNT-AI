"""Tests for job ingestion and dashboard scoring."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.schemas.jobs import CompanyWatchlistCreate, ManualJobListingCreate
from app.services.job_connectors import MockEmbeddedJobConnector
from app.services.job_scoring import estimate_salary_lpa, score_job, split_keywords


class TestJobScoring:
    def test_embedded_job_scores_high(self):
        result = score_job(
            title="Embedded Software Engineer",
            description="RTOS firmware for ARM Cortex automotive devices",
            required_skills="Embedded C, RTOS, CAN, SPI, I2C",
        )

        assert result.score >= 80
        assert "rtos" in result.matched_keywords
        assert "Matched embedded profile keywords" in result.explanation

    def test_non_embedded_job_scores_lower(self):
        result = score_job(
            title="Frontend Engineer",
            description="Build React user interfaces",
            required_skills="React, CSS, TypeScript",
        )

        assert result.score < 60

    def test_salary_estimate(self):
        assert estimate_salary_lpa(16, 22) == "16-22 LPA"
        assert estimate_salary_lpa(16, None) == "16+ LPA"
        assert estimate_salary_lpa(None, None) == "Market estimate pending"

    def test_split_keywords(self):
        assert split_keywords("CAN, SPI; I2C\nRTOS") == ["can", "spi", "i2c", "rtos"]


class TestJobSchemas:
    def test_company_watchlist_normalizes_name(self):
        req = CompanyWatchlistCreate(company_name="  Texas   Instruments  ")
        assert req.company_name == "Texas Instruments"

    def test_manual_listing_normalizes_title(self):
        req = ManualJobListingCreate(
            company_name=" Qualcomm ",
            title="  Embedded   Software   Engineer ",
        )
        assert req.company_name == "Qualcomm"
        assert req.title == "Embedded Software Engineer"


class TestMockConnector:
    @pytest.mark.asyncio
    async def test_mock_connector_returns_embedded_jobs(self):
        jobs = await MockEmbeddedJobConnector().fetch_jobs()

        assert len(jobs) == 3
        assert jobs[0].company_name == "Qualcomm"
        assert jobs[0].salary_min_lpa == 16


class TestJobsApi:
    @pytest.mark.asyncio
    async def test_mock_feed_returns_dashboard_cards(self):
        import app.db.session as db_session
        from app.main import app as fastapi_app

        async def override_get_db():
            yield None

        fastapi_app.dependency_overrides[db_session.get_db] = override_get_db

        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app),
            base_url="http://test",
        ) as client:
            resp = await client.get("/api/v1/jobs/mock-feed")

        fastapi_app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["jobs"]) == 3
        assert data["jobs"][0]["ai_score"] >= data["jobs"][1]["ai_score"]
        assert {"company_name", "title", "ai_score", "salary_estimate"} <= set(data["jobs"][0])
