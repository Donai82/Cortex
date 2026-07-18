from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Event(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: UUID = Field(default_factory=uuid4)
    causation_id: UUID | None = None
    run_id: UUID = Field(default_factory=uuid4)
    source: str = "kernel"
    payload: dict[str, Any] = Field(default_factory=dict)


class GoalCreated(Event):
    event_type: str = "GoalCreated"


class GoalStarted(Event):
    event_type: str = "GoalStarted"


class PlanCreated(Event):
    event_type: str = "PlanCreated"


class MemoryRetrieved(Event):
    event_type: str = "MemoryRetrieved"


class DecisionMade(Event):
    event_type: str = "DecisionMade"


class ToolExecutionStarted(Event):
    event_type: str = "ToolExecutionStarted"


class ToolExecutionCompleted(Event):
    event_type: str = "ToolExecutionCompleted"


class ReflectionCompleted(Event):
    event_type: str = "ReflectionCompleted"


class EvaluationCompleted(Event):
    event_type: str = "EvaluationCompleted"


class RunCompleted(Event):
    event_type: str = "RunCompleted"


class RunFailed(Event):
    event_type: str = "RunFailed"


class RunStopped(Event):
    event_type: str = "RunStopped"
