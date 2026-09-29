"""
Structured logging setup using structlog.

structlog gives us:
- JSON-formatted logs in production (machine-readable for log aggregators)
- Human-readable colored logs in development
- Automatic context binding (request ID, user ID, org ID)
"""

import logging
import sys

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """
    Configure structlog and the standard library logging.

    Call this once at application startup in main.py.
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure standard library logging to route through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Processors are applied in order to each log event
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_production:
        # JSON output for production log aggregators (e.g., Datadog, CloudWatch)
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Human-readable colored output for local development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(), # Standard library factory
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Get a structlog bound logger for a module."""
    return structlog.get_logger(name)
