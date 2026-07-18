from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from cortex.goals.models import Goal
from cortex.kernel.state import RunState


class GoalCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    priority: int = 0


class GoalResponse(Goal):
    pass


class RunResponse(RunState):
    pass


class EventRequest(BaseModel):
    event_type: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    run_id: UUID = Field(default_factory=uuid4)
    correlation_id: UUID = Field(default_factory=uuid4)
    source: str = "api"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
