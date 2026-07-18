from uuid import UUID

from cortex.core.clock import Clock
from cortex.core.exceptions import NotFoundError

from .models import Goal, GoalStatus


class GoalManager:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._goals: dict[UUID, Goal] = {}

    async def create(
        self,
        title: str,
        description: str = "",
        priority: int = 0,
        constraints: list[str] | None = None,
        success_criteria: list[str] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Goal:
        now = self._clock.now()
        goal = Goal(
            title=title,
            description=description,
            priority=priority,
            created_at=now,
            updated_at=now,
            constraints=constraints or [],
            success_criteria=success_criteria or [],
            metadata=metadata or {},
        )
        self._goals[goal.goal_id] = goal
        return goal

    async def get(self, goal_id: UUID) -> Goal:
        if goal_id not in self._goals:
            raise NotFoundError(f"Goal {goal_id} not found")
        return self._goals[goal_id]

    async def list(self) -> list[Goal]:
        return list(self._goals.values())

    async def update_status(self, goal_id: UUID, status: GoalStatus) -> Goal:
        goal = await self.get(goal_id)
        updated = goal.model_copy(update={"status": status, "updated_at": self._clock.now()})
        self._goals[goal_id] = updated
        return updated

    async def attach_run(self, goal_id: UUID, run_id: UUID) -> Goal:
        goal = await self.get(goal_id)
        updated = goal.model_copy(update={"run_id": run_id, "updated_at": self._clock.now()})
        self._goals[goal_id] = updated
        return updated

    async def mark_completed(self, goal_id: UUID) -> Goal:
        return await self.update_status(goal_id, GoalStatus.COMPLETED)

    async def mark_failed(self, goal_id: UUID) -> Goal:
        return await self.update_status(goal_id, GoalStatus.FAILED)
