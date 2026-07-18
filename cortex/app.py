from fastapi import FastAPI

from cortex.api.routes import router_for
from cortex.bus import InMemoryEventBus
from cortex.core.clock import SystemClock
from cortex.evaluation import RuleBasedEvaluator
from cortex.goals import GoalManager
from cortex.kernel import CortexKernel, KernelPolicies
from cortex.memory import EpisodicMemory, SemanticMemory, WorkingMemory
from cortex.planning import SimplePlanner
from cortex.reasoning import FakeReasoningProvider
from cortex.reflection import SimpleReflectionEngine
from cortex.tools import EchoTool, ToolRegistry


def create_app() -> FastAPI:
    clock = SystemClock()
    goals = GoalManager(clock)
    registry = ToolRegistry()
    registry.register(EchoTool())
    kernel = CortexKernel(
        InMemoryEventBus(),
        goals,
        SimplePlanner(clock),
        WorkingMemory(),
        EpisodicMemory(),
        SemanticMemory(),
        FakeReasoningProvider(),
        registry,
        SimpleReflectionEngine(),
        RuleBasedEvaluator(),
        clock,
        KernelPolicies(),
    )
    app = FastAPI(title="Cortex", version="0.1.0")
    app.include_router(router_for(kernel))
    app.state.kernel = kernel
    return app


app = create_app()
