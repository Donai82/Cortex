from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    memory_id: UUID = Field(default_factory=uuid4)
    content: str
    source: str
    source_run_id: UUID | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticFact(MemoryRecord):
    subject: str
    predicate: str
    object: str
