"""Job ingestion and dashboard endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.repositories.job_repository import JobRepository
from app.schemas.jobs import (
    CompanyBlacklistRequest,
    CompanyWatchlistCreate,
    CompanyWatchlistResponse,
    JobMatchCard,
    JobMatchDecisionRequest,
    ManualJobListingCreate,
    MockJobFeedResponse,
)
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get(
    "/mock-feed",
    response_model=MockJobFeedResponse,
    summary="Preview scored embedded jobs without external integrations",
)
async def mock_feed(db: AsyncSession = Depends(get_db)) -> MockJobFeedResponse:
    service = JobService(db)
    return MockJobFeedResponse(jobs=await service.mock_dashboard_feed())


@router.post(
    "/manual",
    response_model=JobMatchCard,
    status_code=status.HTTP_201_CREATED,
    summary="Create a manual job listing and score it for the current user",
)
async def create_manual_job(
    req: ManualJobListingCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> JobMatchCard:
    service = JobService(db)
    return await service.create_manual_match(user_id, req)


@router.get(
    "/matches/new",
    response_model=list[JobMatchCard],
    summary="List new undecided job matches for the dashboard",
)
async def list_new_matches(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[JobMatchCard]:
    service = JobService(db)
    return await service.list_new_matches(user_id)


@router.post(
    "/matches/{match_id}/decision",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Approve, reject, or save a matched job",
)
async def decide_match(
    match_id: str,
    req: JobMatchDecisionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = JobRepository(db)
    match = await repo.decide_match(user_id, match_id, req.decision)
    if not match:
        raise HTTPException(status_code=404, detail="Job match not found")


@router.post(
    "/blacklist",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Blacklist a company for the current user",
)
async def blacklist_company(
    req: CompanyBlacklistRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = JobRepository(db)
    await repo.blacklist_company(user_id, req.company_name, req.reason)


@router.post(
    "/companies/watchlist",
    response_model=CompanyWatchlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a company to the scanner watchlist",
)
async def add_company_watchlist(
    req: CompanyWatchlistCreate,
    db: AsyncSession = Depends(get_db),
) -> CompanyWatchlistResponse:
    repo = JobRepository(db)
    return await repo.add_company_watchlist(req)


@router.get(
    "/companies/watchlist",
    response_model=list[CompanyWatchlistResponse],
    summary="List configured company scanner targets",
)
async def list_company_watchlist(
    db: AsyncSession = Depends(get_db),
) -> list[CompanyWatchlistResponse]:
    repo = JobRepository(db)
    return await repo.list_company_watchlist()
