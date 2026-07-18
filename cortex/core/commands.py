from uuid import UUID

from pydantic import BaseModel, Field


class Command(BaseModel):
    correlation_id: UUID
    run_id: UUID | None = None


class CreateGoal(Command):
    title: str = Field(min_length=1)
    description: str = ""
    priority: int = 0
    constraints: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class StartGoal(Command):
    pass


class CreatePlan(Command):
    pass


class RetrieveMemory(Command):
    pass


class ExecuteTool(Command):
    tool_name: str
    input: str
    confirmed: bool = False


class ReflectOnRun(Command):
    pass


class EvaluateRun(Command):
    pass


class StopRun(Command):
    pass
