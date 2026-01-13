"""Error handling utilities for consistent error responses."""

import logging
from typing import NoReturn

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AegisXException(Exception):
    """Base exception for AegisX application."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        """Initialize exception with message and status code."""
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseError(AegisXException):
    """Exception for database-related errors."""

    def __init__(self, message: str):
        """Initialize database error."""
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidationError(AegisXException):
    """Exception for validation errors."""

    def __init__(self, message: str):
        """Initialize validation error."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class PlannerError(AegisXException):
    """Exception for planning service errors."""

    def __init__(self, message: str):
        """Initialize planner error."""
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_service_error(error: Exception, operation: str) -> NoReturn:
    """
    Handle service errors with consistent logging and HTTP responses.

    Args:
        error: The exception that occurred
        operation: Description of the operation that failed

    Raises:
        HTTPException: Appropriate HTTP exception
    """
    if isinstance(error, AegisXException):
        logger.error(
            f"Service error during {operation}",
            extra={"error": str(error), "status_code": error.status_code},
        )
        raise HTTPException(
            status_code=error.status_code,
            detail=error.message,
        )

    logger.error(
        f"Unexpected error during {operation}: {str(error)}",
        exc_info=True,
    )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Internal server error during {operation}",
    )
