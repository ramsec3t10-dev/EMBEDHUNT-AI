"""
EMBEDHUNT AI — FastAPI Application Entry Point
Phase A: Foundation

This is the main application factory.
Features configured here:
- CORS middleware
- Request correlation ID injection
- Structured logging middleware
- Prometheus metrics
- Health endpoints
- Exception handlers
- API router mounting
"""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import get_logger, set_correlation_id, setup_logging
from app.db.session import check_db_connection

# Initialize logging before anything else
setup_logging()
logger = get_logger(__name__)


# ─── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info(
        "embedhunt_starting",
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
    )

    # Startup checks
    db_ok = await check_db_connection()
    if not db_ok:
        logger.error("startup_db_check_failed")
        # In production, you might want to raise here
    else:
        logger.info("startup_db_ok")

    logger.info("embedhunt_ready", host=settings.HOST, port=settings.PORT)
    yield

    logger.info("embedhunt_shutting_down")


# ─── App Factory ──────────────────────────────────────────────────────────────


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
## EMBEDHUNT AI — The Autonomous Career Engine

The only platform that doesn't just find you embedded engineering jobs — it applies for them.

### Key Features
- 🔍 **Semantic Job Matching** — AI scores every job 0-100 against your profile
- 📄 **Auto Resume Customization** — Tailored per job, per company
- 🤖 **Autonomous Application** — You approve, AI submits
- 📊 **Gap Analysis** — Know exactly what skills to learn next
- 🎯 **Interview Generator** — AI-crafted questions based on the JD

### Authentication
All protected endpoints require a Bearer token obtained from `/api/v1/auth/login`.
        """,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ─── Middleware ───────────────────────────────────────────────────────────

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID", "X-Request-ID"],
    )

    # Gzip compression for responses > 1KB
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ─── Request Middleware ───────────────────────────────────────────────────

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        """Inject correlation ID from header or generate a new one."""
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        set_correlation_id(correlation_id)

        start_time = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )

        return response

    # ─── Exception Handlers ───────────────────────────────────────────────────

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Return clean validation errors (not FastAPI's default verbose format)."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
            errors.append({"field": field, "message": error["msg"]})

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation Error",
                "details": errors,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Catch-all handler — never expose raw stack traces in production."""
        logger.error("unhandled_exception", error=str(exc), path=request.url.path, exc_info=True)

        if settings.is_production:
            message = "An internal error occurred. Our team has been notified."
        else:
            message = str(exc)

        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal Server Error", "detail": message},
        )

    # ─── Health Endpoints ─────────────────────────────────────────────────────

    @app.get("/health", tags=["System"], summary="Health check")
    async def health():
        """Simple liveness probe. Used by Docker/K8s."""
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    @app.get("/health/ready", tags=["System"], summary="Readiness check")
    async def readiness():
        """Deep readiness check — verifies DB connectivity."""
        db_ok = await check_db_connection()
        status_code = 200 if db_ok else 503
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ready" if db_ok else "not_ready",
                "checks": {
                    "database": "ok" if db_ok else "error",
                },
            },
        )

    @app.get("/", tags=["System"], include_in_schema=False)
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
        }

    # ─── Routes ───────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


# ─── App Instance ─────────────────────────────────────────────────────────────
app = create_application()
