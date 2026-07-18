from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RunStatus(StrEnum):
    CREATED = "created"
    PLANNING = "planning"
    RETRIEVING_MEMORY = "retrieving_memory"
    DECIDING = "deciding"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunState(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    goal_id: UUID
    status: RunStatus = RunStatus.CREATED
    steps: int = 0
    tool_calls: int = 0
    reasoning_calls: int = 0
    started_at: datetime
    error: str | None = None
    estimated_cost_usd: float = 0.0
    reflection_summary: str | None = None
    evaluation_score: float | None = None
