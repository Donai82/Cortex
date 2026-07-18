from pydantic import BaseModel, Field


class Evaluation(BaseModel):
    score: float = Field(ge=0, le=1)
    passed: bool
    reasons: list[str] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
