from cortex.core.clock import Clock
from cortex.goals.models import Goal

from .models import Plan, Task


class SimplePlanner:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    async def create_plan(self, goal: Goal) -> Plan:
        return Plan(
            goal_id=goal.goal_id,
            created_at=self._clock.now(),
            tasks=[Task(title=goal.title, description=goal.description, task_type="goal")],
        )
