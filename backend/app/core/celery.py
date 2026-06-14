"""Celery application entry point.

The first workers will run job-source scans and AI enrichment tasks. Keeping the app
definition small here lets Docker start a worker before task modules are added.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "embedhunt",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

# Celery's `-A app.core.celery` discovery looks for a conventional `app` symbol.
app = celery_app


@celery_app.task(name="app.core.celery.healthcheck")
def healthcheck() -> str:
    return "ok"
