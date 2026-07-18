from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ModelRole(StrEnum):
    FAST = "fast"
    REASONING = "reasoning"
    REFLECTION = "reflection"
    EVALUATION = "evaluation"
    CONSOLIDATION = "consolidation"


class Message(BaseModel):
    role: str
    content: str


class ReasoningRequest(BaseModel):
    messages: list[Message]
    role: ModelRole = ModelRole.REASONING
    response_schema: dict[str, Any] | None = None
    temperature: float = 0.0
    max_output_tokens: int = 256
    metadata: dict[str, str] = Field(default_factory=dict)


class ReasoningResponse(BaseModel):
    structured_content: dict[str, Any] | None = None
    raw_text: str
    model_name: str
    provider_name: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    latency_ms: float = 0.0
    finish_reason: str = "stop"
