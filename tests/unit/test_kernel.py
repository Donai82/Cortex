from datetime import UTC, datetime
from uuid import UUID

import pytest

from cortex.bus import InMemoryEventBus
from cortex.core.events import Event
from cortex.evaluation import RuleBasedEvaluator
from cortex.goals import GoalManager
from cortex.kernel import CortexKernel, KernelPolicies, RunStatus
from cortex.memory import EpisodicMemory, SemanticMemory, WorkingMemory
from cortex.memory.models import SemanticFact
from cortex.planning import SimplePlanner
from cortex.reasoning import FakeReasoningProvider
from cortex.reasoning.models import ReasoningResponse
from cortex.reflection import SimpleReflectionEngine
from cortex.tools import EchoTool, ToolRegistry
from cortex.tools.interface import Tool
from cortex.tools.models import SideEffect


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 1, 1, tzinfo=UTC)


def make_kernel(
    policies: KernelPolicies | None = None,
    provider: FakeReasoningProvider | None = None,
    extra_tool: Tool | None = None,
) -> CortexKernel:
    clock = FixedClock()
    tools = ToolRegistry()
    tools.register(EchoTool())
    if extra_tool is not None:
        tools.register(extra_tool)
    return CortexKernel(
        InMemoryEventBus(),
        GoalManager(clock),
        SimplePlanner(clock),
        WorkingMemory(),
        EpisodicMemory(),
        SemanticMemory(),
        provider or FakeReasoningProvider(),
        tools,
        SimpleReflectionEngine(),
        RuleBasedEvaluator(),
        clock,
        policies or KernelPolicies(),
    )


async def run_to_terminal(kernel: CortexKernel, run_id: UUID) -> None:
    for _ in range(8):
        await kernel.step(run_id)


@pytest.mark.asyncio
async def test_kernel_runs_all_phases_and_records_events() -> None:
    kernel = make_kernel()
    goal = await kernel.submit_goal("hello")
    run = await kernel.start_run(goal.goal_id)
    await run_to_terminal(kernel, run.run_id)

    result = await kernel.get_run_state(run.run_id)
    assert result.status == RunStatus.COMPLETED
    assert result.evaluation_score == 1
    assert result.reflection_summary == "Run for hello completed"
    records = await kernel.episodic.for_run(run.run_id)
    assert {record.content for record in records} >= {
        "GoalStarted",
        "PlanCreated",
        "MemoryRetrieved",
        "DecisionMade",
        "ToolExecutionCompleted",
        "ReflectionCompleted",
        "EvaluationCompleted",
        "RunCompleted",
    }
    assert await kernel.working.get(run.run_id, "goal") is None


@pytest.mark.asyncio
async def test_decision_receives_retrieved_memory_and_event_payloads_are_audited() -> None:
    kernel = make_kernel()
    await kernel.semantic.add(
        SemanticFact(
            content="delivery reliability matters",
            source="test",
            timestamp=FixedClock().now(),
            subject="supplier",
            predicate="criterion",
            object="delivery reliability",
        )
    )
    goal = await kernel.submit_goal("compare suppliers")
    run = await kernel.start_run(goal.goal_id)
    for _ in range(4):
        await kernel.step(run.run_id)

    request = kernel.reasoning.requests[0]
    assert "delivery reliability matters" in request.messages[1].content
    events = await kernel.get_run_events(run.run_id)
    memory_event = next(event for event in events if event.event_type == "MemoryRetrieved")
    assert memory_event.payload == {"facts": 1}
    records = await kernel.episodic.for_run(run.run_id)
    record = next(record for record in records if record.content == "MemoryRetrieved")
    assert record.metadata == {"facts": 1}


@pytest.mark.asyncio
async def test_policy_failure_is_terminal_and_does_not_raise() -> None:
    kernel = make_kernel(KernelPolicies(max_reasoning_calls=0))
    goal = await kernel.submit_goal("limited")
    run = await kernel.start_run(goal.goal_id)
    for _ in range(3):
        result = await kernel.step(run.run_id)
    assert result.status == RunStatus.FAILED
    assert "reasoning" in (result.error or "")
    assert await kernel.working.get(run.run_id, "goal") is None


@pytest.mark.asyncio
async def test_stop_clears_working_memory_and_publishes_event() -> None:
    kernel = make_kernel()
    goal = await kernel.submit_goal("stop me")
    run = await kernel.start_run(goal.goal_id)
    await kernel.step(run.run_id)
    stopped = await kernel.stop_run(run.run_id)
    assert stopped.status == RunStatus.CANCELLED
    assert await kernel.working.get(run.run_id, "goal") is None
    assert (await kernel.episodic.for_run(run.run_id))[-1].content == "RunStopped"


@pytest.mark.asyncio
async def test_side_effecting_tool_requires_confirmation() -> None:
    class WriteTool(EchoTool):
        name = "write"
        side_effect = SideEffect.WRITE

    provider = FakeReasoningProvider(
        responses=[
            ReasoningResponse(
                raw_text="write",
                structured_content={"tool_name": "write", "input": "danger"},
                model_name="fake",
                provider_name="fake",
            )
        ]
    )
    kernel = make_kernel(provider=provider, extra_tool=WriteTool())
    goal = await kernel.submit_goal("protected")
    run = await kernel.start_run(goal.goal_id)
    for _ in range(4):
        result = await kernel.step(run.run_id)
    assert result.status == RunStatus.FAILED
    assert "confirmation" in (result.error or "")


@pytest.mark.asyncio
async def test_event_bus_publishes_typed_event() -> None:
    bus = InMemoryEventBus()
    seen: list[Event] = []

    async def handler(event: Event) -> None:
        seen.append(event)

    await bus.subscribe("external", handler)
    await bus.publish(Event(event_type="external"))
    assert seen[0].event_type == "external"
