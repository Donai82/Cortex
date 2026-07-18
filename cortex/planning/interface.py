from typing import Protocol

from cortex.goals.models import Goal

from .models import Plan


class Planner(Protocol):
    async def create_plan(self, goal: Goal) -> Plan: ...
