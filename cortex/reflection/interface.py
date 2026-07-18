from typing import Protocol

from cortex.goals.models import Goal
from cortex.planning.models import Plan

from .models import Reflection


class ReflectionEngine(Protocol):
    async def reflect(
        self, goal: Goal, plan: Plan, events: list[str], tool_results: list[str], final_status: str
    ) -> Reflection: ...
