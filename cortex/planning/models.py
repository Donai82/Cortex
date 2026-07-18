from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    title: str
    description: str = ""
    task_type: str = "general"
    dependencies: list[UUID] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    assigned_module: str = "kernel"
    metadata: dict[str, str] = Field(default_factory=dict)


class Plan(BaseModel):
    plan_id: UUID = Field(default_factory=uuid4)
    goal_id: UUID
    tasks: list[Task]
    status: str = "created"
    version: int = 1
    created_at: datetime
