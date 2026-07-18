# Cortex

> **The Kernel governs execution. Models provide reasoning. Tools perform actions. Memory preserves experience.**

Cortex is an experimental cognitive architecture, not AGI. It coordinates replaceable goals, planning, memory, reasoning providers, tools, reflection, and evaluation. The Kernel is separate from the LLM so policy, state, and bounded execution cannot be bypassed by model output.

## Architecture

`API -> Goal Manager -> Kernel -> Planner / Memory / Reasoning / Tools / Reflection / Evaluation`

Lifecycle: `CREATED -> PLANNING -> RETRIEVING_MEMORY -> DECIDING -> EXECUTING -> REFLECTING -> EVALUATING -> COMPLETED`

The `core` package contains typed messages and configuration. `bus` provides an asynchronous in-memory event bus. `memory`, `reasoning`, `tools`, `reflection`, and `evaluation` expose small protocols and local implementations.

## Installation and local run

Requires Python 3.13 and Poetry. Run `make install`, then `make run`. The default app uses only in-memory components and a deterministic fake provider; PostgreSQL, Redis, and OpenRouter are optional.

Run checks with `make check` or tests with `make test`. Configuration is documented in `.env.example`.

## Extension

Implement `ReasoningProvider` to add a provider, implement `Tool` and register it to add a tool, or implement the memory protocols for durable storage. No Kernel changes are required for those extensions.

## Limitations and roadmap

This initial release has in-memory persistence, a conservative consolidation placeholder, one deterministic planner, and a deliberately small lifecycle. Durable repositories, richer plans, authentication, and production deployment are future work.
