"""EMBEDHUNT AI — API v1 Router"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, jobs

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(jobs.router)

# Phase B will add:
# api_router.include_router(users.router)
# api_router.include_router(resumes.router)
# api_router.include_router(companies.router)

# Phase C will add:
# api_router.include_router(matching.router)
# api_router.include_router(interviews.router)
# api_router.include_router(applications.router)
