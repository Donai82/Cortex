from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class GoalStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Goal(BaseModel):
    goal_id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1)
    description: str = ""
    status: GoalStatus = GoalStatus.CREATED
    priority: int = 0
    created_at: datetime
    updated_at: datetime
    constraints: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    run_id: UUID | None = None
