"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PriorityLevel(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task status options."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class Task(BaseModel):
    """Task model with strict typing."""

    id: Optional[int] = Field(default=None, description="Task ID")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Task description")
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Task priority")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    estimated_hours: Optional[float] = Field(default=None, ge=0.0, le=168.0, description="Estimated hours")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for the API",
                "priority": "high",
                "status": "pending",
                "estimated_hours": 4.0,
            }
        }
    }


class PlanRequest(BaseModel):
    """Request model for planning endpoints."""

    context: str = Field(..., min_length=1, max_length=5000, description="Planning context")
    goals: List[str] = Field(..., min_items=1, max_items=10, description="List of goals")
    constraints: Optional[List[str]] = Field(default=None, max_items=10, description="Planning constraints")

    @field_validator("goals")
    @classmethod
    def validate_goals(cls, v: List[str]) -> List[str]:
        """Validate that goals are not empty strings."""
        if any(not goal.strip() for goal in v):
            raise ValueError("Goals cannot be empty strings")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "context": "I need to prepare for a product launch",
                "goals": ["Complete marketing materials", "Setup infrastructure", "Train support team"],
                "constraints": ["Launch date is next Friday", "Budget is limited"],
            }
        }
    }


class PlanResponse(BaseModel):
    """Response model for planning endpoints."""

    plan_id: str = Field(..., description="Unique plan identifier")
    tasks: List[Task] = Field(..., description="Generated task list")
    summary: str = Field(..., description="Plan summary")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Plan creation time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "plan_id": "plan_20260112_abc123",
                "tasks": [],
                "summary": "Generated 5 tasks for weekly planning",
                "created_at": "2026-01-12T10:00:00Z",
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "timestamp": "2026-01-12T10:00:00Z",
                "version": "0.1.0",
                "database": "connected",
            }
        }
    }
