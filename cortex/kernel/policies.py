from pydantic import BaseModel, Field


class KernelPolicies(BaseModel):
    max_steps: int = Field(default=20, ge=1)
    max_tool_calls: int = Field(default=10, ge=0)
    max_reasoning_calls: int = Field(default=10, ge=0)
    timeout_seconds: float = Field(default=300, gt=0)
    max_cost_usd: float = Field(default=1, ge=0)
    require_confirmation_for_side_effects: bool = True
