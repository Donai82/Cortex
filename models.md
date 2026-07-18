# Cortex — Initial Project Setup

You are the lead software architect for **Cortex**, an open-source Cognitive Operating System.

## Vision

Cortex is not another AI agent framework.

It is a modular cognitive architecture that coordinates reasoning models, memory systems, planners, tools, goals, reflection, and evaluation.

The LLM is only one component inside Cortex. It must never become the central controller.

The **Kernel** is the central coordinator. It decides which subsystem should act, routes events, maintains execution state, and enforces boundaries between components.

The architecture must prioritize:

* Modularity
* Extensibility
* Testability
* Strong typing
* Clean interfaces
* Event-driven communication
* LLM-provider independence
* Deterministic testing
* Minimal coupling

The codebase should feel like an operating system for cognition rather than a chatbot.

---

## Technology

Use:

* Python 3.13+
* Poetry
* FastAPI
* Pydantic v2
* SQLAlchemy 2
* PostgreSQL support, optional for the first local run
* Redis support, optional for the first local run
* pytest
* pytest-asyncio
* Ruff
* mypy
* structlog
* httpx

Do not use LangChain, LangGraph, CrewAI, AutoGen, or another agent framework.

Keep dependencies minimal.

---

## Core Architectural Rule

The Kernel coordinates the system.

The Kernel must not contain domain intelligence, prompt logic, memory implementation details, or provider-specific code.

Its responsibilities are:

* Accept goals
* Maintain execution state
* Dispatch commands
* Route events
* Select subsystems
* Enforce execution limits
* Trigger reflection and evaluation
* Stop or pause workflows
* Record lifecycle transitions

The Kernel may ask a reasoning model for a decision, but the model is an adviser, not the controller.

The flow should resemble:

```text
User or API
    ↓
Goal Manager
    ↓
Kernel
    ├── Memory
    ├── Planner
    ├── Reasoning Provider
    ├── Tool Registry
    ├── Reflection
    └── Evaluation
```

---

## Project Structure

Create this structure:

```text
cortex/
├── __init__.py
├── app.py
│
├── api/
│   ├── __init__.py
│   ├── routes.py
│   └── schemas.py
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── events.py
│   ├── commands.py
│   ├── ids.py
│   ├── clock.py
│   └── exceptions.py
│
├── kernel/
│   ├── __init__.py
│   ├── kernel.py
│   ├── state.py
│   ├── lifecycle.py
│   └── policies.py
│
├── bus/
│   ├── __init__.py
│   ├── interface.py
│   └── in_memory.py
│
├── goals/
│   ├── __init__.py
│   ├── models.py
│   ├── interface.py
│   └── manager.py
│
├── planning/
│   ├── __init__.py
│   ├── models.py
│   ├── interface.py
│   └── simple.py
│
├── memory/
│   ├── __init__.py
│   ├── models.py
│   ├── interfaces.py
│   ├── working.py
│   ├── episodic.py
│   ├── semantic.py
│   └── consolidation.py
│
├── reasoning/
│   ├── __init__.py
│   ├── models.py
│   ├── provider.py
│   ├── fake.py
│   └── openrouter.py
│
├── tools/
│   ├── __init__.py
│   ├── models.py
│   ├── interface.py
│   ├── registry.py
│   └── echo.py
│
├── reflection/
│   ├── __init__.py
│   ├── models.py
│   ├── interface.py
│   └── simple.py
│
├── evaluation/
│   ├── __init__.py
│   ├── models.py
│   ├── interface.py
│   └── rule_based.py
│
└── observability/
    ├── __init__.py
    └── logging.py

tests/
├── unit/
├── integration/
└── fixtures/
```

Everything should be independently importable and replaceable.

---

## Events and Commands

Use explicit typed events and commands.

Commands represent requested actions.

Examples:

```text
CreateGoal
StartGoal
CreatePlan
RetrieveMemory
ExecuteTool
ReflectOnRun
EvaluateRun
StopRun
```

Events represent facts that already happened.

Examples:

```text
GoalCreated
GoalStarted
PlanCreated
MemoryRetrieved
ToolExecutionStarted
ToolExecutionCompleted
ReflectionCompleted
EvaluationCompleted
RunCompleted
RunFailed
```

Use Pydantic models for all commands and events.

Every event must include:

* event_id
* event_type
* timestamp
* correlation_id
* causation_id
* run_id
* source
* payload

Do not use untyped dictionaries for core messages.

---

## Event Bus

Create an asynchronous event bus interface.

Implement an in-memory version for the first release.

Required functionality:

* Subscribe handlers by event type
* Publish events asynchronously
* Support multiple handlers
* Preserve handler registration order
* Isolate handler failures
* Log publication and handler failures
* Allow testing without network services

Do not require Redis for the initial implementation.

Prepare the interface so a Redis-backed bus can be added later without changing consumers.

---

## Kernel

Create a `CortexKernel` class.

The Kernel should receive its dependencies through constructor injection.

Suggested dependencies:

* EventBus
* GoalManager
* Planner
* WorkingMemory
* EpisodicMemory
* SemanticMemory
* ReasoningProvider
* ToolRegistry
* ReflectionEngine
* Evaluator
* Clock
* KernelPolicies

The Kernel must expose methods similar to:

```python
async def submit_goal(...)
async def start_run(...)
async def step(...)
async def stop_run(...)
async def get_run_state(...)
```

The Kernel should execute a bounded state machine.

Suggested lifecycle:

```text
CREATED
→ PLANNING
→ RETRIEVING_MEMORY
→ DECIDING
→ EXECUTING
→ REFLECTING
→ EVALUATING
→ COMPLETED
```

Also support:

```text
PAUSED
FAILED
CANCELLED
```

The first implementation may use a simple deterministic lifecycle.

Do not build autonomous infinite loops.

Every run must have configurable limits:

* Maximum steps
* Maximum tool calls
* Maximum reasoning calls
* Maximum elapsed time
* Maximum estimated cost

---

## Kernel Policies

Create a `KernelPolicies` model containing:

* max_steps
* max_tool_calls
* max_reasoning_calls
* timeout_seconds
* max_cost_usd
* require_confirmation_for_side_effects

Policies must be enforced by the Kernel, not by the LLM.

---

## Reasoning Provider

Create a provider-independent interface.

The rest of Cortex must never import OpenRouter-specific types.

Use typed request and response models.

Example responsibilities:

```python
class ReasoningProvider(Protocol):
    async def generate(self, request: ReasoningRequest) -> ReasoningResponse:
        ...
```

The request should support:

* messages
* model role
* response schema
* temperature
* maximum output tokens
* metadata

The response should include:

* structured content
* raw text
* model name
* provider name
* input tokens
* output tokens
* estimated cost
* latency
* finish reason

Implement:

* `FakeReasoningProvider`
* `OpenRouterReasoningProvider`

---

## Fake Reasoning Provider

The fake provider is essential.

It must:

* Work without internet access
* Return deterministic responses
* Support queued predefined responses
* Record received requests
* Simulate provider failures
* Simulate malformed responses
* Simulate latency
* Simulate token and cost metadata

All architecture tests must work using the fake provider.

---

## OpenRouter Provider

Implement a minimal OpenRouter provider using `httpx`.

Read configuration from environment variables.

Do not make live API calls during tests.

Handle:

* Authentication
* Timeouts
* HTTP errors
* Invalid JSON
* Missing response fields
* Rate limits
* Structured-output parsing
* Token usage metadata when available

Do not retry indefinitely.

Use bounded retries with exponential backoff.

---

## Model Roles

Do not hardcode one model for all tasks.

Support logical model roles:

```text
FAST
REASONING
REFLECTION
EVALUATION
CONSOLIDATION
```

Configuration should map each role to a model name.

Example:

```env
MODEL_FAST=
MODEL_REASONING=
MODEL_REFLECTION=
MODEL_EVALUATION=
MODEL_CONSOLIDATION=
```

The Kernel requests a role. The provider resolves the configured model.

---

## Goals

Create typed goal models.

A goal should contain:

* goal_id
* title
* description
* status
* priority
* created_at
* updated_at
* constraints
* success_criteria
* metadata

The first GoalManager may use in-memory storage.

Required operations:

* Create goal
* Retrieve goal
* List goals
* Update status
* Attach run ID
* Mark completed
* Mark failed

---

## Planning

Create a planner interface.

The first implementation should be a deterministic `SimplePlanner`.

It may convert a goal into a small list of typed tasks without using an LLM.

A plan should contain:

* plan_id
* goal_id
* tasks
* status
* version
* created_at

A task should contain:

* task_id
* title
* description
* task_type
* dependencies
* status
* assigned_module
* metadata

Do not implement advanced planning yet.

---

## Memory

Implement four separate concepts.

### Working Memory

Stores temporary run state.

Examples:

* Current goal
* Current plan
* Recent observations
* Intermediate tool results
* Current step

It should be automatically clearable when a run ends.

### Episodic Memory

Stores events and experiences.

Examples:

* What action occurred
* What result followed
* Whether it succeeded
* Which run produced it

### Semantic Memory

Stores durable facts and abstractions.

Examples:

* Known facts
* Learned preferences
* Stable rules
* Confidence and provenance

### Consolidation Engine

Defines how episodic memories may later become semantic memories.

For now:

* Create the interface
* Implement a conservative rule-based placeholder
* Do not update model weights
* Do not perform automatic fine-tuning
* Do not claim that learning has occurred unless a durable memory was explicitly created

All memory records should include provenance, confidence, timestamps, and source run IDs.

Use in-memory repositories initially.

Prepare interfaces for database-backed implementations later.

---

## Tools

Create a plugin-style tool system.

Each tool must define:

* name
* description
* input schema
* output schema
* side-effect classification
* required permissions
* async execute method

Implement:

* `Tool` interface
* `ToolRegistry`
* `EchoTool` example

Side-effect classifications:

```text
NONE
READ
WRITE
EXTERNAL_COMMUNICATION
DESTRUCTIVE
```

The Kernel must enforce confirmation policies for tools with side effects.

The LLM must never bypass Kernel permission checks.

Adding a new tool should not require editing Kernel internals.

---

## Reflection

Create a reflection interface.

The initial `SimpleReflectionEngine` should produce a typed reflection from:

* Goal
* Plan
* Events
* Tool results
* Final status

A reflection should include:

* summary
* successes
* failures
* lessons
* candidate_memories
* confidence

The first implementation may be deterministic and rule-based.

Do not use a live LLM by default.

---

## Evaluation

Create an evaluator interface.

Implement a rule-based evaluator that checks:

* Did the run complete?
* Were limits respected?
* Did required tasks finish?
* Were side-effect policies obeyed?
* Were errors handled?
* Were success criteria satisfied where mechanically testable?

Return:

* score
* passed
* reasons
* metrics

Keep evaluation separate from reflection.

---

## API

Create FastAPI endpoints:

```text
GET  /
GET  /health
POST /goals
GET  /goals
GET  /goals/{goal_id}
POST /goals/{goal_id}/run
GET  /runs/{run_id}
POST /runs/{run_id}/step
POST /runs/{run_id}/stop
POST /events
```

Use typed request and response schemas.

The API must not expose internal exceptions or stack traces.

Return meaningful error responses.

---

## Configuration

Use Pydantic Settings.

Create `.env.example` containing:

```env
APP_ENV=development
LOG_LEVEL=INFO

OPENROUTER_API_KEY=

MODEL_FAST=
MODEL_REASONING=
MODEL_REFLECTION=
MODEL_EVALUATION=
MODEL_CONSOLIDATION=

DATABASE_URL=postgresql+asyncpg://cortex:cortex@localhost:5432/cortex
REDIS_URL=redis://localhost:6379/0

KERNEL_MAX_STEPS=20
KERNEL_MAX_TOOL_CALLS=10
KERNEL_MAX_REASONING_CALLS=10
KERNEL_TIMEOUT_SECONDS=300
KERNEL_MAX_COST_USD=1.00
KERNEL_REQUIRE_CONFIRMATION_FOR_SIDE_EFFECTS=true
```

The application must start without PostgreSQL, Redis, or an API key by using in-memory components and the fake reasoning provider.

---

## Logging and Observability

Use structlog.

Every important operation should produce structured logs.

Include where applicable:

* event_id
* run_id
* goal_id
* correlation_id
* module
* action
* status
* latency
* model
* token usage
* estimated cost
* error type

Never log API keys or sensitive prompt contents by default.

---

## Testing

Create comprehensive tests.

### Unit tests

Cover:

* Event models
* Command models
* In-memory event bus
* GoalManager
* SimplePlanner
* WorkingMemory
* EpisodicMemory
* SemanticMemory
* ConsolidationEngine
* FakeReasoningProvider
* ToolRegistry
* Kernel policies
* Run lifecycle transitions
* Reflection engine
* Rule-based evaluator

### Integration tests

Cover:

* Submit goal through API
* Start a run
* Execute deterministic plan
* Invoke fake reasoning provider
* Execute EchoTool
* Store episodic memory
* Produce reflection
* Produce evaluation
* Complete run
* Reject side-effecting tool without confirmation
* Stop a run
* Fail cleanly when limits are exceeded

Tests must not require:

* Internet access
* OpenRouter credentials
* PostgreSQL
* Redis

All tests should pass immediately after generation.

---

## Developer Experience

Create:

* `README.md`
* `CONTRIBUTING.md`
* `.env.example`
* `.gitignore`
* `pyproject.toml`
* `Makefile`
* `docker-compose.yml`
* GitHub Actions workflow

The Makefile should include:

```text
install
run
test
lint
format
typecheck
check
```

GitHub Actions should run:

* Ruff
* mypy
* pytest

The initial Docker Compose file may prepare PostgreSQL and Redis, but the local app must not depend on them.

---

## README

The README must include:

* Cortex vision
* Why the Kernel is separate from the LLM
* Architecture overview
* Lifecycle diagram
* Module descriptions
* Installation
* Running locally
* Running tests
* Environment configuration
* Adding a reasoning provider
* Adding a tool
* Adding a memory implementation
* Current limitations
* Roadmap

Include this architectural statement prominently:

> The Kernel governs execution. Models provide reasoning. Tools perform actions. Memory preserves experience.

Also make clear that Cortex is an experimental cognitive architecture, not AGI.

---

## Implementation Rules

Follow these rules throughout:

* Prefer protocols and composition over deep inheritance
* Use dependency injection
* Use async interfaces where I/O may later occur
* Type all public APIs
* Avoid global mutable state
* Avoid circular imports
* Keep modules small
* Keep business logic outside FastAPI routes
* Use UTC timestamps
* Use UUIDs for identifiers
* Use enums for bounded states
* Validate every external input
* Make all side effects explicit
* Keep model output untrusted until validated
* Never let an LLM directly mutate Kernel state
* Never let an LLM directly execute a tool
* Never let provider-specific logic leak into other modules
* Do not implement speculative advanced features
* Do not add placeholders that pretend to work
* Clearly mark intentionally minimal implementations

---

## Deliverable

Generate the complete initial repository implementation.

After creating the files:

1. Run formatting.
2. Run Ruff.
3. Run mypy.
4. Run pytest.
5. Fix all errors.
6. Show a concise summary of what was created.
7. List any intentional limitations.
8. Do not stop until the generated foundation passes its checks.

Focus on producing a small, reliable, extensible foundation rather than an impressive but fragile demo.
