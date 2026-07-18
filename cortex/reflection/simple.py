from cortex.goals.models import Goal
from cortex.planning.models import Plan

from .models import Reflection


class SimpleReflectionEngine:
    async def reflect(
        self, goal: Goal, plan: Plan, events: list[str], tool_results: list[str], final_status: str
    ) -> Reflection:
        passed = final_status == "completed"
        return Reflection(
            summary=f"Run for {goal.title} {final_status}",
            successes=["plan executed"] if passed else [],
            failures=[] if passed else ["run did not complete"],
            lessons=[],
            candidate_memories=[],
            confidence=1.0 if passed else 0.0,
        )
