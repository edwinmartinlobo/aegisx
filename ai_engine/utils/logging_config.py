"""Structured logging configuration."""

import logging
import sys
from typing import Any, Dict

from ..core.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured data."""
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra"):
            log_data.update(record.extra)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "pathname"):
            log_data["file"] = f"{record.pathname}:{record.lineno}"

        parts = [f"{k}={v}" for k, v in log_data.items()]
        return " | ".join(parts)


def setup_logging() -> None:
    """Configure structured logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        StructuredFormatter(
            fmt="%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.info(
        "Logging configured",
        extra={
            "log_level": settings.LOG_LEVEL,
            "app_name": settings.APP_NAME,
        },
    )
