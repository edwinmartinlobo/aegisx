"""Planning endpoints for week and day planning."""

import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from ..core.planner_service import PlannerService
from ..models.schemas import PlanRequest, PlanResponse
from ..utils.error_handler import handle_service_error

logger = logging.getLogger(__name__)
router = APIRouter()
planner_service = PlannerService()


@router.post("/week", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def plan_week(request: PlanRequest) -> PlanResponse:
    """
    Generate a weekly plan based on provided context and goals.

    Args:
        request: Planning request with context, goals, and constraints

    Returns:
        PlanResponse: Generated weekly plan with tasks

    Raises:
        HTTPException: If plan generation fails
    """
    try:
        logger.info(
            "Weekly plan requested",
            extra={
                "goals_count": len(request.goals),
                "has_constraints": request.constraints is not None,
            },
        )

        tasks = await planner_service.generate_weekly_plan(
            context=request.context,
            goals=request.goals,
            constraints=request.constraints or [],
        )

        plan_id = f"plan_week_{datetime.utcnow().strftime('%Y%m%d')}_{uuid4().hex[:8]}"

        logger.info(
            "Weekly plan generated successfully",
            extra={"plan_id": plan_id, "tasks_count": len(tasks)},
        )

        return PlanResponse(
            plan_id=plan_id,
            tasks=tasks,
            summary=f"Generated {len(tasks)} tasks for weekly planning",
            created_at=datetime.utcnow(),
        )

    except ValueError as e:
        logger.warning(f"Invalid request for weekly plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to generate weekly plan: {str(e)}", exc_info=True)
        handle_service_error(e, "weekly plan generation")


@router.post("/today", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def plan_today(request: PlanRequest) -> PlanResponse:
    """
    Generate a daily plan based on provided context and goals.

    Args:
        request: Planning request with context, goals, and constraints

    Returns:
        PlanResponse: Generated daily plan with tasks

    Raises:
        HTTPException: If plan generation fails
    """
    try:
        logger.info(
            "Daily plan requested",
            extra={
                "goals_count": len(request.goals),
                "has_constraints": request.constraints is not None,
            },
        )

        tasks = await planner_service.generate_daily_plan(
            context=request.context,
            goals=request.goals,
            constraints=request.constraints or [],
        )

        plan_id = f"plan_today_{datetime.utcnow().strftime('%Y%m%d')}_{uuid4().hex[:8]}"

        logger.info(
            "Daily plan generated successfully",
            extra={"plan_id": plan_id, "tasks_count": len(tasks)},
        )

        return PlanResponse(
            plan_id=plan_id,
            tasks=tasks,
            summary=f"Generated {len(tasks)} tasks for today's planning",
            created_at=datetime.utcnow(),
        )

    except ValueError as e:
        logger.warning(f"Invalid request for daily plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to generate daily plan: {str(e)}", exc_info=True)
        handle_service_error(e, "daily plan generation")
