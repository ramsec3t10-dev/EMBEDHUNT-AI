"""
EMBEDHUNT AI — Logging Module
Phase A: Foundation

Production-grade structured logging using structlog.
Features:
- JSON output in production, colored console in development
- Automatic correlation ID injection (for distributed tracing)
- Request context binding
- Audit logging for security events
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional
import structlog
from structlog.types import EventDict, WrappedLogger

from app.core.config import settings

# ─── Correlation ID Context ───────────────────────────────────────────────────

# Thread/async-safe context variable for request correlation
_correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    return _correlation_id_ctx.get() or str(uuid.uuid4())


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    cid = correlation_id or str(uuid.uuid4())
    _correlation_id_ctx.set(cid)
    return cid


# ─── Custom Processors ────────────────────────────────────────────────────────

def add_correlation_id(logger: WrappedLogger, method: str, event_dict: EventDict) -> EventDict:
    """Inject correlation ID into every log event."""
    event_dict["correlation_id"] = get_correlation_id()
    return event_dict


def add_app_context(logger: WrappedLogger, method: str, event_dict: EventDict) -> EventDict:
    """Inject app-level context into every log event."""
    event_dict["app"] = settings.APP_NAME
    event_dict["version"] = settings.APP_VERSION
    event_dict["env"] = settings.APP_ENV
    return event_dict


def drop_color_message_key(logger: WrappedLogger, method: str, event_dict: EventDict) -> EventDict:
    """Remove uvicorn's color_message to keep logs clean."""
    event_dict.pop("color_message", None)
    return event_dict


# ─── Setup ────────────────────────────────────────────────────────────────────

def setup_logging() -> None:
    """
    Initialize structlog with the appropriate renderer for the environment.
    Call once at application startup.
    """

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        add_correlation_id,
        add_app_context,
        drop_color_message_key,
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.LOG_FORMAT == "json" or settings.is_production:
        # Production: pure JSON — ready for Datadog, CloudWatch, Loki
        renderer = structlog.processors.JSONRenderer()
    else:
        # Development: human-readable with colors
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to route through structlog
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ExtraAdder(),
            *shared_processors,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    # Silence noisy third-party loggers
    for noisy in ["uvicorn.access", "sqlalchemy.engine", "alembic"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a named logger. Use this everywhere instead of logging.getLogger."""
    return structlog.get_logger(name)


# ─── Audit Logger ─────────────────────────────────────────────────────────────

class AuditLogger:
    """
    Dedicated logger for security-sensitive events.
    These events are always logged at INFO level regardless of LOG_LEVEL.
    In production, these should be routed to a separate, tamper-evident sink.
    """

    def __init__(self):
        self._logger = get_logger("audit")

    def log(
        self,
        event: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        outcome: str = "success",
        **kwargs,
    ) -> None:
        self._logger.info(
            event,
            audit=True,
            user_id=user_id,
            resource=resource,
            action=action,
            outcome=outcome,
            **kwargs,
        )

    def login(self, user_id: str, ip: str, success: bool) -> None:
        self.log(
            "user_login",
            user_id=user_id,
            action="login",
            outcome="success" if success else "failure",
            ip=ip,
        )

    def token_refresh(self, user_id: str) -> None:
        self.log("token_refresh", user_id=user_id, action="token_refresh")

    def password_changed(self, user_id: str) -> None:
        self.log("password_changed", user_id=user_id, action="password_change")

    def role_changed(self, target_user_id: str, by_user_id: str, new_role: str) -> None:
        self.log(
            "role_changed",
            user_id=target_user_id,
            action="role_change",
            by=by_user_id,
            new_role=new_role,
        )


audit_logger = AuditLogger()
