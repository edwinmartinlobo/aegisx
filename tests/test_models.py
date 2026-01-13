"""Tests for Pydantic models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ai-engine"))

from models.schemas import PlanRequest, Task, PriorityLevel, TaskStatus


class TestPlanRequest:
    """Tests for PlanRequest model."""

    def test_valid_plan_request(self):
        """Test creating a valid plan request."""
        request = PlanRequest(
            context="Test context",
            goals=["Goal 1", "Goal 2"],
            constraints=["Constraint 1"],
        )
        assert request.context == "Test context"
        assert len(request.goals) == 2
        assert len(request.constraints) == 1

    def test_plan_request_without_constraints(self):
        """Test plan request without constraints is valid."""
        request = PlanRequest(
            context="Test context",
            goals=["Goal 1"],
        )
        assert request.constraints is None

    def test_plan_request_empty_context_fails(self):
        """Test that empty context fails validation."""
        with pytest.raises(ValidationError):
            PlanRequest(
                context="",
                goals=["Goal 1"],
            )

    def test_plan_request_empty_goals_fails(self):
        """Test that empty goals list fails validation."""
        with pytest.raises(ValidationError):
            PlanRequest(
                context="Test context",
                goals=[],
            )

    def test_plan_request_context_too_long_fails(self):
        """Test that context longer than max length fails."""
        with pytest.raises(ValidationError):
            PlanRequest(
                context="x" * 5001,
                goals=["Goal 1"],
            )

    def test_plan_request_too_many_goals_fails(self):
        """Test that more than 10 goals fails validation."""
        with pytest.raises(ValidationError):
            PlanRequest(
                context="Test context",
                goals=[f"Goal {i}" for i in range(11)],
            )


class TestTask:
    """Tests for Task model."""

    def test_valid_task_creation(self):
        """Test creating a valid task."""
        task = Task(
            title="Test task",
            description="Test description",
            priority=PriorityLevel.HIGH,
            status=TaskStatus.PENDING,
        )
        assert task.title == "Test task"
        assert task.priority == PriorityLevel.HIGH
        assert task.status == TaskStatus.PENDING

    def test_task_defaults(self):
        """Test task default values."""
        task = Task(title="Test task")
        assert task.priority == PriorityLevel.MEDIUM
        assert task.status == TaskStatus.PENDING
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_empty_title_fails(self):
        """Test that empty title fails validation."""
        with pytest.raises(ValidationError):
            Task(title="")

    def test_task_title_too_long_fails(self):
        """Test that title longer than max length fails."""
        with pytest.raises(ValidationError):
            Task(title="x" * 201)

    def test_task_invalid_estimated_hours_fails(self):
        """Test that invalid estimated hours fails validation."""
        with pytest.raises(ValidationError):
            Task(title="Test task", estimated_hours=-1)

        with pytest.raises(ValidationError):
            Task(title="Test task", estimated_hours=200)

    def test_task_priority_enum(self):
        """Test task priority enum values."""
        for priority in PriorityLevel:
            task = Task(title="Test task", priority=priority)
            assert task.priority == priority

    def test_task_status_enum(self):
        """Test task status enum values."""
        for status in TaskStatus:
            task = Task(title="Test task", status=status)
            assert task.status == status
