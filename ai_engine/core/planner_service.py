"""Core planning service with AI integration."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from .config import settings
from ..models.schemas import PriorityLevel, Task, TaskStatus

logger = logging.getLogger(__name__)


class PlannerService:
    """Service for generating weekly and daily plans."""

    def __init__(self):
        """Initialize planner service with prompt templates."""
        self.prompts_dir = Path(settings.PROMPTS_DIR)
        self._load_templates()

    def _load_templates(self) -> None:
        """Load prompt templates from files."""
        try:
            weekly_template_path = self.prompts_dir / "weekly_plan.txt"
            daily_template_path = self.prompts_dir / "daily_plan.txt"

            if weekly_template_path.exists():
                self.weekly_template = weekly_template_path.read_text()
            else:
                logger.warning("Weekly template not found, using default")
                self.weekly_template = "Generate a weekly plan for: {context}\nGoals: {goals}"

            if daily_template_path.exists():
                self.daily_template = daily_template_path.read_text()
            else:
                logger.warning("Daily template not found, using default")
                self.daily_template = "Generate a daily plan for: {context}\nGoals: {goals}"

        except Exception as e:
            logger.error(f"Failed to load templates: {str(e)}", exc_info=True)
            raise

    async def generate_weekly_plan(
        self,
        context: str,
        goals: List[str],
        constraints: List[str],
    ) -> List[Task]:
        """
        Generate a weekly plan based on context and goals.

        Args:
            context: Planning context
            goals: List of goals to achieve
            constraints: Planning constraints

        Returns:
            List of generated tasks
        """
        logger.info("Generating weekly plan", extra={"goals_count": len(goals)})

        tasks = []
        base_date = datetime.utcnow()

        for idx, goal in enumerate(goals):
            task = Task(
                id=idx + 1,
                title=goal,
                description=f"Weekly task: {goal}\nContext: {context[:100]}...",
                priority=self._determine_priority(idx, len(goals)),
                status=TaskStatus.PENDING,
                estimated_hours=8.0,
                due_date=base_date + timedelta(days=(idx % 7)),
                created_at=base_date,
                updated_at=base_date,
            )
            tasks.append(task)

        logger.info(f"Generated {len(tasks)} tasks for weekly plan")
        return tasks

    async def generate_daily_plan(
        self,
        context: str,
        goals: List[str],
        constraints: List[str],
    ) -> List[Task]:
        """
        Generate a daily plan based on context and goals.

        Args:
            context: Planning context
            goals: List of goals to achieve
            constraints: Planning constraints

        Returns:
            List of generated tasks
        """
        logger.info("Generating daily plan", extra={"goals_count": len(goals)})

        tasks = []
        base_date = datetime.utcnow()
        today_end = base_date.replace(hour=23, minute=59, second=59)

        for idx, goal in enumerate(goals):
            task = Task(
                id=idx + 1,
                title=goal,
                description=f"Daily task: {goal}\nContext: {context[:100]}...",
                priority=self._determine_priority(idx, len(goals)),
                status=TaskStatus.PENDING,
                estimated_hours=2.0,
                due_date=today_end,
                created_at=base_date,
                updated_at=base_date,
            )
            tasks.append(task)

        logger.info(f"Generated {len(tasks)} tasks for daily plan")
        return tasks

    def _determine_priority(self, index: int, total: int) -> PriorityLevel:
        """Determine task priority based on position."""
        if index == 0:
            return PriorityLevel.HIGH
        elif index < total / 2:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW
