from datetime import UTC, datetime
from uuid import uuid4

import pytest

from cortex.bus import InMemoryEventBus
from cortex.core.events import Event
from cortex.goals import GoalManager
from cortex.planning import SimplePlanner
from cortex.reasoning import FakeReasoningProvider, ReasoningRequest
from cortex.reasoning.models import Message
from cortex.tools import EchoTool, ToolRegistry


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 1, 1, tzinfo=UTC)


@pytest.mark.asyncio
async def test_bus_order_and_isolation() -> None:
    bus = InMemoryEventBus()
    seen: list[str] = []

    async def bad(event: Event) -> None:
        raise RuntimeError

    async def good(event: Event) -> None:
        seen.append(event.event_type)

    await bus.subscribe("x", bad)
    await bus.subscribe("x", good)
    await bus.publish(
        Event(
            event_type="x",
            timestamp=FixedClock().now(),
            correlation_id=uuid4(),
            run_id=uuid4(),
            source="test",
        )
    )
    assert seen == ["x"]


@pytest.mark.asyncio
async def test_goals_planner_fake_and_tool() -> None:
    manager = GoalManager(FixedClock())
    goal = await manager.create("test")
    plan = await SimplePlanner(FixedClock()).create_plan(goal)
    assert plan.goal_id == goal.goal_id and plan.tasks[0].title == "test"
    provider = FakeReasoningProvider()
    response = await provider.generate(
        ReasoningRequest(messages=[Message(role="user", content="x")])
    )
    assert response.raw_text == "deterministic decision" and len(provider.requests) == 1
    registry = ToolRegistry()
    registry.register(EchoTool())
    assert (await registry.get("echo").execute("x")).output == "x"
