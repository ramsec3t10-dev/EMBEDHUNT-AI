"""Data access for job ingestion and matching."""

import hashlib

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_ingestion import (
    CompanyBlacklist,
    CompanyWatchlist,
    JobDecision,
    JobListing,
    JobListingStatus,
    JobMatch,
)
from app.schemas.jobs import CompanyWatchlistCreate, ManualJobListingCreate
from app.services.job_scoring import estimate_salary_lpa, score_job


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_company_watchlist(self, req: CompanyWatchlistCreate) -> CompanyWatchlist:
        company = CompanyWatchlist(
            company_name=req.company_name,
            careers_url=req.careers_url,
            priority=req.priority,
            tags=req.tags,
        )
        self.db.add(company)
        await self.db.flush()
        await self.db.refresh(company)
        return company

    async def list_company_watchlist(self) -> list[CompanyWatchlist]:
        result = await self.db.execute(
            select(CompanyWatchlist)
            .where(CompanyWatchlist.is_active.is_(True))
            .order_by(CompanyWatchlist.priority.asc(), CompanyWatchlist.company_name.asc())
        )
        return list(result.scalars().all())

    async def blacklist_company(
        self,
        user_id: str,
        company_name: str,
        reason: str | None = None,
    ) -> CompanyBlacklist:
        existing = await self.db.execute(
            select(CompanyBlacklist).where(
                CompanyBlacklist.user_id == user_id,
                CompanyBlacklist.company_name == company_name,
            )
        )
        blacklist = existing.scalar_one_or_none()
        if blacklist:
            blacklist.is_active = True
            blacklist.reason = reason
            await self.db.flush()
            await self.db.refresh(blacklist)
            return blacklist

        blacklist = CompanyBlacklist(user_id=user_id, company_name=company_name, reason=reason)
        self.db.add(blacklist)
        await self.db.flush()
        await self.db.refresh(blacklist)
        return blacklist

    async def create_manual_listing_with_match(
        self,
        user_id: str,
        req: ManualJobListingCreate,
    ) -> tuple[JobListing, JobMatch]:
        source_job_id = self._manual_source_id(req)
        listing = JobListing(
            source_name="manual",
            source_job_id=source_job_id,
            source_url=req.source_url,
            company_name=req.company_name,
            title=req.title,
            location=req.location,
            work_mode=req.work_mode,
            salary_min_lpa=req.salary_min_lpa,
            salary_max_lpa=req.salary_max_lpa,
            description=req.description,
            required_skills=req.required_skills,
            status=JobListingStatus.MATCHED,
        )
        self.db.add(listing)
        await self.db.flush()
        await self.db.refresh(listing)

        score = score_job(req.title, req.description, req.required_skills)
        match = JobMatch(
            user_id=user_id,
            job_listing_id=listing.id,
            ai_score=score.score,
            salary_estimate=estimate_salary_lpa(req.salary_min_lpa, req.salary_max_lpa),
            resume_name="Primary embedded resume",
            explanation=score.explanation,
        )
        self.db.add(match)
        await self.db.flush()
        await self.db.refresh(match)
        return listing, match

    async def list_new_match_cards(self, user_id: str) -> list[tuple[JobListing, JobMatch]]:
        result = await self.db.execute(
            select(JobListing, JobMatch)
            .join(JobMatch, JobMatch.job_listing_id == JobListing.id)
            .where(JobMatch.user_id == user_id, JobMatch.decision.is_(None))
            .order_by(JobMatch.ai_score.desc(), JobListing.created_at.desc())
        )
        return list(result.all())

    async def decide_match(
        self,
        user_id: str,
        match_id: str,
        decision: JobDecision,
    ) -> JobMatch | None:
        result = await self.db.execute(
            select(JobMatch).where(JobMatch.id == match_id, JobMatch.user_id == user_id)
        )
        match = result.scalar_one_or_none()
        if not match:
            return None

        match.decision = decision
        if decision == JobDecision.APPROVED:
            listing_status = JobListingStatus.APPROVED
        else:
            listing_status = JobListingStatus.REJECTED
        await self.db.execute(
            update(JobListing)
            .where(JobListing.id == match.job_listing_id)
            .values(status=listing_status)
        )
        await self.db.flush()
        await self.db.refresh(match)
        return match

    @staticmethod
    def _manual_source_id(req: ManualJobListingCreate) -> str:
        fingerprint = "|".join(
            [
                req.company_name.lower(),
                req.title.lower(),
                req.source_url or "",
                req.location or "",
            ]
        )
        return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:32]
