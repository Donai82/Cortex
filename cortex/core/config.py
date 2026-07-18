from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from cortex.reasoning.models import ModelRole


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    openrouter_api_key: str | None = None
    model_fast: str = ""
    model_reasoning: str = ""
    model_reflection: str = ""
    model_evaluation: str = ""
    model_consolidation: str = ""
    database_url: str = "postgresql+asyncpg://cortex:cortex@localhost:5432/cortex"
    redis_url: str = "redis://localhost:6379/0"
    kernel_max_steps: int = Field(default=20, ge=1)
    kernel_max_tool_calls: int = Field(default=10, ge=0)
    kernel_max_reasoning_calls: int = Field(default=10, ge=0)
    kernel_timeout_seconds: float = Field(default=300, gt=0)
    kernel_max_cost_usd: float = Field(default=1.0, ge=0)
    kernel_require_confirmation_for_side_effects: bool = True
    openrouter_timeout_seconds: float = Field(default=30.0, gt=0)
    openrouter_max_retries: int = Field(default=2, ge=0, le=5)
    openrouter_backoff_seconds: float = Field(default=0.25, ge=0)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def resolve_model(self, role: ModelRole) -> str:
        """Resolve a role-specific model, falling back to the reasoning model."""
        configured = getattr(self, f"model_{role.value}", "")
        if not isinstance(configured, str):
            configured = ""
        configured = configured.strip()
        if configured:
            return configured
        reasoning = self.model_reasoning.strip()
        return reasoning or "openai/gpt-4o-mini"
