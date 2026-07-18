Phase 1: get one complete cognitive loop working

Build one narrow workflow end to end:

Goal
→ retrieve memory
→ create plan
→ choose action
→ execute tool
→ evaluate result
→ reflect
→ store memory
→ finish

Use a simple task such as:

Research three suppliers and produce a recommendation.

At first, use only:

one API-based LLM
one planner
one memory backend
two or three tools
one evaluator
one reflection step

The objective is reliability, not intelligence.

Phase 2: define a benchmark before improving it

Create perhaps 30–50 repeatable tasks that test the architecture.

Examples:

use relevant memory
ignore irrelevant memory
revise a failed plan
stop after exceeding a budget
ask permission before sending an email
recover from a broken tool
reject contradictory memories
complete a multi-step task
avoid repeating an already failed action

Measure:

task success
cost
latency
number of LLM calls
tool failures
memory retrieval accuracy
policy violations

Without this benchmark, you will not know whether Cortex is improving or merely becoming more complicated.

Phase 3: build the first real memory system

Start with inspectable external memory, not weight updates.

Use three stores:

Working memory
- current task state
- temporary observations

Episodic memory
- what happened
- action taken
- outcome
- timestamps

Semantic memory
- durable facts
- confidence
- provenance

The important part is not storage. It is retrieval and consolidation.

The first consolidation rule can be conservative:

one observation
→ episodic memory only

repeated consistent observations
→ candidate semantic memory

validated candidate
→ durable semantic fact

Do not let the model freely turn every reflection into permanent knowledge.

Phase 4: compare Cortex with a normal agent

Create a baseline agent:

LLM
→ tools
→ response

Then run the same benchmark against:

Baseline agent
versus
Cortex Kernel architecture

Cortex should prove at least one advantage:

higher completion rate
fewer repeated mistakes
lower token use
better safety
improved performance after accumulating experience
easier debugging

If it cannot beat the baseline, you need to simplify or redesign it.

Phase 5: add real learning from experience

Only after memory is working should you test whether the system becomes better over repeated tasks.

For example:

Run 1:
The agent chooses a poor supplier.

Reflection:
Delivery reliability was ignored.

Memory:
Supplier reliability should be part of comparisons.

Run 20:
The system automatically checks delivery reliability.

This is the first major milestone:

Cortex performs better on later tasks because of earlier experience.

That does not require changing model weights yet.

Phase 6: introduce specialist models

Once the loop works, assign different model roles:

Fast model
- classification
- extraction
- routing

Reasoning model
- planning
- difficult decisions

Evaluation model
- judge output quality

Consolidation model
- propose durable memories

Then test whether specialists improve quality enough to justify their cost.

The Kernel should route by capability rather than provider name.

Phase 7: add a safe skill system

A useful experience should sometimes become a reusable procedure rather than a fact.

Example:

Experience:
Supplier comparison required the same six checks repeatedly.

Skill:
compare_supplier(
    price,
    specification,
    logistics,
    reliability,
    payment_terms,
    certification
)

Skills should be:

versioned
testable
inspectable
reversible
permission-controlled

The system should never silently generate executable code and trust it permanently.

Phase 8: test neural or weight-based memory later

Only after the external-memory system has clear limitations should you investigate:

LoRA adapters
test-time training
fast weights
latent memory modules
periodic distillation

You first need a dataset of real Cortex experiences and a benchmark. Otherwise, you would be changing weights without knowing what improvement means.

The immediate next development milestone

I would call it:

Cortex Milestone 1 — Closed Cognitive Loop

Requirements:

1. User submits a goal
2. Kernel creates a run
3. Memory retrieval occurs
4. Planner creates typed tasks
5. Kernel selects a tool
6. Tool executes
7. Evaluator scores the result
8. Reflection produces candidate lessons
9. Episodic memory is stored
10. Run completes with full audit history

Use the fake provider first, then replayed responses, then a real API model.

The first real test should not be an open-ended assistant. It should be one constrained workflow where every action and decision can be inspected.

The most important question after the initial code exists is:

Can Cortex complete the same task twice and perform better the second time because it remembered the first?

That is where it begins to become meaningfully different from OpenClaw-style orchestration or a standard agent framework.
