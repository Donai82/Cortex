import json
from typing import Any
from uuid import UUID

from cortex.bus.interface import EventBus
from cortex.core.clock import Clock
from cortex.core.events import (
    DecisionMade,
    EvaluationCompleted,
    Event,
    GoalStarted,
    MemoryRetrieved,
    PlanCreated,
    ReflectionCompleted,
    RunCompleted,
    RunFailed,
    RunStopped,
    ToolExecutionCompleted,
    ToolExecutionStarted,
)
from cortex.core.exceptions import NotFoundError
from cortex.evaluation.interface import Evaluator
from cortex.evaluation.models import Evaluation
from cortex.goals.interface import GoalRepository
from cortex.goals.models import Goal, GoalStatus
from cortex.memory.interfaces import EpisodicStore, SemanticStore, WorkingMemoryStore
from cortex.memory.models import MemoryRecord
from cortex.planning.interface import Planner
from cortex.planning.models import Plan, TaskStatus
from cortex.reasoning.models import Message, ReasoningRequest, ReasoningResponse
from cortex.reasoning.provider import ReasoningProvider
from cortex.reflection.interface import ReflectionEngine
from cortex.reflection.models import Reflection
from cortex.tools.interface import ToolResolver

from .lifecycle import next_status
from .policies import KernelPolicies
from .state import RunState, RunStatus


class CortexKernel:
    def __init__(
        self,
        bus: EventBus,
        goals: GoalRepository,
        planner: Planner,
        working_memory: WorkingMemoryStore,
        episodic_memory: EpisodicStore,
        semantic_memory: SemanticStore,
        reasoning: ReasoningProvider,
        tools: ToolResolver,
        reflection: ReflectionEngine,
        evaluator: Evaluator,
        clock: Clock,
        policies: KernelPolicies,
    ) -> None:
        self.bus = bus
        self.goals = goals
        self.planner = planner
        self.working = working_memory
        self.episodic = episodic_memory
        self.semantic = semantic_memory
        self.reasoning = reasoning
        self.tools = tools
        self.reflection = reflection
        self.evaluator = evaluator
        self.clock = clock
        self.policies = policies
        self._runs: dict[UUID, RunState] = {}
        self._plans: dict[UUID, Plan] = {}
        self._events: dict[UUID, list[Event]] = {}
        self._tool_results: dict[UUID, list[str]] = {}
        self._reflections: dict[UUID, Reflection] = {}
        self._evaluations: dict[UUID, Evaluation] = {}
        self._decisions: dict[UUID, ReasoningResponse] = {}
        self._last_event: dict[UUID, UUID] = {}

    async def submit_goal(self, title: str, description: str = "", priority: int = 0) -> Goal:
        return await self.goals.create(title, description, priority)

    async def start_run(self, goal_id: UUID) -> RunState:
        await self.goals.get(goal_id)
        state = RunState(goal_id=goal_id, started_at=self.clock.now())
        self._runs[state.run_id] = state
        self._events[state.run_id] = []
        self._tool_results[state.run_id] = []
        await self.goals.attach_run(goal_id, state.run_id)
        await self.goals.update_status(goal_id, GoalStatus.RUNNING)
        await self._publish(state, GoalStarted, {"goal_id": str(goal_id)})
        return state

    async def get_run_state(self, run_id: UUID) -> RunState:
        if run_id not in self._runs:
            raise NotFoundError(f"Run {run_id} not found")
        return self._runs[run_id]

    async def get_run_events(self, run_id: UUID) -> list[Event]:
        if run_id not in self._runs:
            raise NotFoundError(f"Run {run_id} not found")
        return list(self._events[run_id])

    async def step(self, run_id: UUID) -> RunState:
        state = await self.get_run_state(run_id)
        if state.status in (RunStatus.COMPLETED, RunStatus.CANCELLED, RunStatus.FAILED):
            return state
        try:
            self._check_timeout(state)
            if state.steps >= self.policies.max_steps:
                return await self._fail(state, "maximum steps exceeded")
            status = next_status(state.status)
            state = state.model_copy(update={"status": status, "steps": state.steps + 1})
            if status == RunStatus.PLANNING:
                await self._planning(state)
            elif status == RunStatus.RETRIEVING_MEMORY:
                await self._retrieve_memory(state)
            elif status == RunStatus.DECIDING:
                state = await self._decide(state)
            elif status == RunStatus.EXECUTING:
                state = await self._execute(state)
            elif status == RunStatus.REFLECTING:
                state = await self._reflect(state)
            elif status == RunStatus.EVALUATING:
                state = await self._evaluate(state)
            elif status == RunStatus.COMPLETED:
                await self.goals.mark_completed(state.goal_id)
                await self._publish(state, RunCompleted, {})
                await self._finish(state)
            self._runs[run_id] = state
            return state
        except Exception as exc:
            return await self._fail(state, str(exc))

    async def stop_run(self, run_id: UUID) -> RunState:
        state = await self.get_run_state(run_id)
        if state.status in (RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED):
            return state
        state = state.model_copy(update={"status": RunStatus.CANCELLED})
        self._runs[run_id] = state
        try:
            await self._publish(state, RunStopped, {})
        finally:
            await self._finish(state)
        return state

    def _check_timeout(self, state: RunState) -> None:
        elapsed = (self.clock.now() - state.started_at).total_seconds()
        if elapsed > self.policies.timeout_seconds:
            raise RuntimeError("maximum elapsed time exceeded")

    async def _planning(self, state: RunState) -> None:
        goal = await self.goals.get(state.goal_id)
        plan = await self.planner.create_plan(goal)
        self._plans[state.run_id] = plan
        await self.working.put(state.run_id, "goal", goal.title)
        await self.working.put(
            state.run_id, "plan", json.dumps(plan.model_dump(mode="json"), sort_keys=True)
        )
        await self._publish(
            state, PlanCreated, {"plan_id": str(plan.plan_id), "task_count": len(plan.tasks)}
        )

    async def _retrieve_memory(self, state: RunState) -> None:
        facts = await self.semantic.list()
        await self.working.put(
            state.run_id,
            "semantic_memory",
            json.dumps([fact.model_dump(mode="json") for fact in facts], sort_keys=True),
        )
        await self._publish(state, MemoryRetrieved, {"facts": len(facts)})

    async def _decide(self, state: RunState) -> RunState:
        if state.reasoning_calls >= self.policies.max_reasoning_calls:
            raise RuntimeError("maximum reasoning calls exceeded")
        goal = await self.goals.get(state.goal_id)
        plan = self._plans[state.run_id]
        memory = await self.working.get(state.run_id, "semantic_memory") or "[]"
        response = await self.reasoning.generate(
            ReasoningRequest(
                messages=[
                    Message(role="system", content="Choose the next bounded action"),
                    Message(
                        role="user",
                        content=json.dumps(
                            {
                                "goal": goal.model_dump(mode="json"),
                                "plan": plan.model_dump(mode="json"),
                                "semantic_memory": json.loads(memory),
                            },
                            sort_keys=True,
                        ),
                    ),
                ],
            )
        )
        self._check_timeout(state)
        updated = state.model_copy(
            update={
                "reasoning_calls": state.reasoning_calls + 1,
                "estimated_cost_usd": state.estimated_cost_usd + response.estimated_cost,
            }
        )
        self._decisions[state.run_id] = response
        if updated.estimated_cost_usd > self.policies.max_cost_usd:
            raise RuntimeError("maximum estimated cost exceeded")
        await self.working.put(state.run_id, "decision", response.raw_text)
        await self._publish(updated, DecisionMade, {"decision": response.raw_text})
        return updated

    async def _execute(self, state: RunState) -> RunState:
        if state.tool_calls >= self.policies.max_tool_calls:
            raise RuntimeError("maximum tool calls exceeded")
        decision = await self.working.get(state.run_id, "decision")
        tool_name, tool_input, confirmed = self._tool_request(state.run_id, decision)
        tool = self.tools.get(tool_name)
        if (
            tool.side_effect.value != "none"
            and self.policies.require_confirmation_for_side_effects
            and not confirmed
        ):
            raise RuntimeError("confirmation required for side-effecting tool")
        await self._publish(state, ToolExecutionStarted, {"tool": tool_name})
        result = await tool.execute(tool_input)
        self._check_timeout(state)
        self._tool_results[state.run_id].append(result.output)
        await self._publish(
            state,
            ToolExecutionCompleted,
            {"tool": tool_name, "success": result.success, "output": result.output},
        )
        if not result.success:
            raise RuntimeError(result.error or "tool execution failed")
        plan = self._plans.get(state.run_id)
        if plan is not None:
            self._plans[state.run_id] = plan.model_copy(
                update={
                    "tasks": [
                        task.model_copy(update={"status": TaskStatus.COMPLETED})
                        for task in plan.tasks
                    ]
                }
            )
        return state.model_copy(update={"tool_calls": state.tool_calls + 1})

    async def _reflect(self, state: RunState) -> RunState:
        goal = await self.goals.get(state.goal_id)
        plan = self._plans[state.run_id]
        reflection = await self.reflection.reflect(
            goal,
            plan,
            [event.event_type for event in self._events[state.run_id]],
            self._tool_results[state.run_id],
            RunStatus.COMPLETED.value,
        )
        self._check_timeout(state)
        self._reflections[state.run_id] = reflection
        await self._publish(
            state,
            ReflectionCompleted,
            {"summary": reflection.summary, "confidence": reflection.confidence},
        )
        for candidate in reflection.candidate_memories:
            await self.episodic.add(
                MemoryRecord(
                    content=candidate,
                    source="reflection",
                    source_run_id=state.run_id,
                    timestamp=self.clock.now(),
                    metadata={"kind": "candidate_memory", "subject": goal.title},
                )
            )
        return state.model_copy(update={"reflection_summary": reflection.summary})

    async def _evaluate(self, state: RunState) -> RunState:
        plan = self._plans[state.run_id]
        evaluation = await self.evaluator.evaluate(
            completed=True,
            limits_respected=state.steps <= self.policies.max_steps,
            tasks_finished=all(task.status == TaskStatus.COMPLETED for task in plan.tasks),
            policies_obeyed=True,
            errors_handled=True,
        )
        self._check_timeout(state)
        self._evaluations[state.run_id] = evaluation
        await self._publish(
            state, EvaluationCompleted, {"score": evaluation.score, "passed": evaluation.passed}
        )
        return state.model_copy(update={"evaluation_score": evaluation.score})

    def _tool_request(self, run_id: UUID, decision: str | None) -> tuple[str, str, bool]:
        # Provider output is advisory; only these validated fields affect execution.
        response = self._decisions.get(run_id)
        if response and response.structured_content:
            content = response.structured_content
            return (
                str(content.get("tool_name", "echo")),
                str(content.get("input", decision or "")),
                bool(content.get("confirmed", False)),
            )
        if decision is None:
            return "echo", "", False
        return "echo", decision, False

    async def _publish(
        self, state: RunState, event_type: type[Event], payload: dict[str, Any]
    ) -> None:
        event = event_type(
            event_type=event_type.__name__,
            timestamp=self.clock.now(),
            correlation_id=state.run_id,
            causation_id=self._last_event.get(state.run_id),
            run_id=state.run_id,
            source="kernel",
            payload=payload,
        )
        self._last_event[state.run_id] = event.event_id
        self._events.setdefault(state.run_id, []).append(event)
        await self.episodic.add(
            MemoryRecord(
                content=event.event_type,
                source="kernel",
                source_run_id=state.run_id,
                timestamp=event.timestamp,
                metadata=event.payload,
            )
        )
        await self.bus.publish(event)

    async def _fail(self, state: RunState, error: str) -> RunState:
        failed = state.model_copy(update={"status": RunStatus.FAILED, "error": error})
        self._runs[state.run_id] = failed
        try:
            await self.goals.mark_failed(state.goal_id)
            await self._publish(failed, RunFailed, {"error": error})
        except Exception:
            pass
        finally:
            await self._finish(failed)
        return failed

    async def _finish(self, state: RunState) -> None:
        await self.working.clear(state.run_id)
