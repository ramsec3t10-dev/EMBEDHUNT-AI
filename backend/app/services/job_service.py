"""Business logic for job dashboard and ingestion workflows."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_ingestion import ScanRunStatus
from app.repositories.job_repository import JobRepository
from app.schemas.jobs import JobMatchCard, JobScanRunResponse, ManualJobListingCreate
from app.services.job_connectors import MockEmbeddedJobConnector
from app.services.job_scoring import estimate_salary_lpa, score_job, split_keywords


class JobService:
    def __init__(self, db: AsyncSession):
        self.repo = JobRepository(db)

    async def create_manual_match(
        self,
        user_id: str,
        req: ManualJobListingCreate,
    ) -> JobMatchCard:
        listing, match = await self.repo.create_manual_listing_with_match(user_id, req)
        return JobMatchCard(
            match_id=match.id,
            job_id=listing.id,
            company_name=listing.company_name,
            title=listing.title,
            source_name=listing.source_name,
            source_url=listing.source_url,
            location=listing.location,
            ai_score=match.ai_score,
            salary_estimate=match.salary_estimate or "Market estimate pending",
            resume_used=match.resume_name or "Primary embedded resume",
            explanation=match.explanation or "",
            required_skills=split_keywords(listing.required_skills),
        )

    async def list_new_matches(self, user_id: str) -> list[JobMatchCard]:
        rows = await self.repo.list_new_match_cards(user_id)
        return [
            JobMatchCard(
                match_id=match.id,
                job_id=listing.id,
                company_name=listing.company_name,
                title=listing.title,
                source_name=listing.source_name,
                source_url=listing.source_url,
                location=listing.location,
                ai_score=match.ai_score,
                salary_estimate=match.salary_estimate or "Market estimate pending",
                resume_used=match.resume_name or "Primary embedded resume",
                explanation=match.explanation or "",
                required_skills=split_keywords(listing.required_skills),
            )
            for listing, match in rows
        ]

    async def mock_dashboard_feed(self) -> list[JobMatchCard]:
        connector = MockEmbeddedJobConnector()
        jobs = await connector.fetch_jobs()
        cards: list[JobMatchCard] = []
        for job in jobs:
            score = score_job(job.title, job.description, job.required_skills)
            cards.append(
                JobMatchCard(
                    job_id=job.source_job_id,
                    company_name=job.company_name,
                    title=job.title,
                    source_name=job.source_name,
                    source_url=job.source_url,
                    location=job.location,
                    ai_score=score.score,
                    salary_estimate=estimate_salary_lpa(job.salary_min_lpa, job.salary_max_lpa),
                    resume_used="Primary embedded resume",
                    explanation=score.explanation,
                    required_skills=split_keywords(job.required_skills),
                )
            )
        return sorted(cards, key=lambda card: card.ai_score, reverse=True)

    async def run_mock_scan(self) -> JobScanRunResponse:
        connector = MockEmbeddedJobConnector()
        run = await self.repo.create_scan_run(source_name=connector.source_name)
        jobs_imported = 0

        try:
            jobs = await connector.fetch_jobs()
            for job in jobs:
                _, created = await self.repo.upsert_external_listing(job)
                if created:
                    jobs_imported += 1

            finished = await self.repo.finish_scan_run(
                run_id=run.id,
                status=ScanRunStatus.SUCCEEDED,
                jobs_found=len(jobs),
                jobs_imported=jobs_imported,
            )
        except Exception as exc:
            finished = await self.repo.finish_scan_run(
                run_id=run.id,
                status=ScanRunStatus.FAILED,
                jobs_found=0,
                jobs_imported=jobs_imported,
                error_message=str(exc),
            )
            if finished is None:
                raise

        if finished is None:
            raise RuntimeError("Scan run disappeared before completion")

        return JobScanRunResponse.model_validate(finished)
