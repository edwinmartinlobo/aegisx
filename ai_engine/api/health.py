"""Health check endpoints."""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from ..db.database import check_db_connection
from ..models.schemas import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """
    Check service health and database connectivity.

    Returns:
        HealthResponse: Service health status
    """
    try:
        db_status = "connected" if check_db_connection() else "disconnected"

        logger.info("Health check performed", extra={"database_status": db_status})

        return HealthResponse(
            status="healthy" if db_status == "connected" else "degraded",
            timestamp=datetime.utcnow(),
            version="0.1.0",
            database=db_status,
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service health check failed",
        )
