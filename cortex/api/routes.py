from uuid import UUID

from fastapi import APIRouter, HTTPException

from cortex.core.events import Event
from cortex.core.exceptions import CortexError
from cortex.goals.models import Goal
from cortex.kernel.kernel import CortexKernel
from cortex.kernel.state import RunState

from .schemas import EventRequest, GoalCreateRequest, GoalResponse, RunResponse


def router_for(kernel: CortexKernel) -> APIRouter:
    router = APIRouter()

    @router.get("/")
    async def root() -> dict[str, str]:
        return {"name": "Cortex", "version": "0.1.0"}

    @router.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.post("/goals", response_model=GoalResponse)
    async def create_goal(request: GoalCreateRequest) -> Goal:
        return await kernel.submit_goal(request.title, request.description, request.priority)

    @router.get("/goals", response_model=list[GoalResponse])
    async def list_goals() -> list[Goal]:
        return await kernel.goals.list()

    @router.get("/goals/{goal_id}", response_model=GoalResponse)
    async def get_goal(goal_id: UUID) -> Goal:
        try:
            return await kernel.goals.get(goal_id)
        except CortexError as exc:
            raise HTTPException(404, str(exc)) from exc

    @router.post("/goals/{goal_id}/run", response_model=RunResponse)
    async def start(goal_id: UUID) -> RunState:
        try:
            return await kernel.start_run(goal_id)
        except CortexError as exc:
            raise HTTPException(404, str(exc)) from exc

    @router.get("/runs/{run_id}", response_model=RunResponse)
    async def get_run(run_id: UUID) -> RunState:
        try:
            return await kernel.get_run_state(run_id)
        except CortexError as exc:
            raise HTTPException(404, str(exc)) from exc

    @router.get("/runs/{run_id}/events", response_model=list[Event])
    async def get_run_events(run_id: UUID) -> list[Event]:
        try:
            return await kernel.get_run_events(run_id)
        except CortexError as exc:
            raise HTTPException(404, str(exc)) from exc

    @router.post("/runs/{run_id}/step", response_model=RunResponse)
    async def step(run_id: UUID) -> RunState:
        try:
            return await kernel.step(run_id)
        except CortexError as exc:
            raise HTTPException(400, str(exc)) from exc

    @router.post("/runs/{run_id}/stop", response_model=RunResponse)
    async def stop(run_id: UUID) -> RunState:
        try:
            return await kernel.stop_run(run_id)
        except CortexError as exc:
            raise HTTPException(404, str(exc)) from exc

    @router.post("/events")
    async def event(request: EventRequest) -> dict[str, str]:
        published = Event(
            event_type=request.event_type,
            timestamp=request.timestamp,
            correlation_id=request.correlation_id,
            run_id=request.run_id,
            source=request.source,
            payload=request.payload,
        )
        await kernel.bus.publish(published)
        return {"accepted": published.event_type, "event_id": str(published.event_id)}

    return router
