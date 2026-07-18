from pydantic import BaseModel, Field


class Reflection(BaseModel):
    summary: str
    successes: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    lessons: list[str] = Field(default_factory=list)
    candidate_memories: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
