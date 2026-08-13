---
id: multi-agent-orchestration/05
subject: multi-agent-orchestration
title: "Orchestration Architecture Patterns: Graph-Based, Role-Based, and Deterministic-Script Approaches"
slug: orchestration-architecture-patterns
status: drafted
mastery:
seniority: senior
source: "TrueFoundry: What Is Multi-Agent Orchestration? A Complete Guide (2026); TrueFoundry: Best Multi-agent Orchestration Frameworks in 2026; arXiv:2606.26924 A Deterministic Control Plane for LLM Coding Agents (2026); arXiv:2605.09894 Deterministic vs. LLM-Controlled Orchestration for COBOL-to-Python Modernization (2026); arXiv:2604.11378 From Agent Loops to Structured Graphs: A Scheduler-Theoretic Framework for LLM Agent Execution (2026)"
durability: durable
prerequisites: [multi-agent-orchestration/04]
created: 2026-08-10
updated: 2026-08-10
---

# Orchestration Architecture Patterns: Graph-Based, Role-Based, and Deterministic-Script Approaches

## TL;DR
Once you know you need coordination mechanisms (lesson 04), you still have to decide *who owns the decision of what happens next*: an explicit state machine the model traverses (graph-based), a set of agents negotiating from assigned personas (role-based), or plain code that calls agents as functions and never lets a model choose the next step (deterministic-script). These are architecture-level control-flow patterns, not products - the same three patterns re-appear under new framework names every year, and picking correctly means asking "who decides the next step, and can I prove what it will do before it runs?"

## The idea
Lesson 04 established the coordination primitives - shared state, message passing, task lists - that agents use to exchange information. This lesson is one level up: given those primitives, *what decides which agent acts next, and how much of that decision is made in advance versus improvised at runtime?*

That single question splits almost every multi-agent system built in 2026 into three architectural families, independent of which specific framework or vendor implements them:

1. **Graph-based orchestration** - the set of possible transitions is drawn out *before* execution as a directed graph (nodes = agents or steps, edges = allowed transitions, some edges conditional on state). The model chooses *which* branch to take at a decision node, but it cannot invent an edge that was not in the graph.
2. **Role-based orchestration** - agents are assigned a persona (a role, a goal, a scope of responsibility) and a model - often a "manager" or "planner" agent - decides at runtime which agent to invoke next and what to hand it, without a pre-drawn map of every possible path.
3. **Deterministic-script orchestration** - ordinary code (not a model) owns every control-flow decision: which agent runs, in what order, with what input, under what condition. Agents are invoked as functions with typed inputs and outputs; no model, anywhere in the system, decides *what happens next* - only *what the output of this one call is*.

The three are not tiers of sophistication - they are a genuine trade-off along one axis: **how much of the "what happens next" decision is made by a model, versus fixed in advance by a human-authored structure.** More model-decided control flow buys adaptability to situations the designer didn't anticipate; less model-decided control flow buys predictability, auditability, and testability. Nothing about this trade-off is specific to any one product - it is the same trade-off that traditional software has always faced between a rules engine and a hard-coded pipeline, now applied to a component (the LLM) whose "rules" are probabilistic.

## How it works

### Pattern 1: graph-based orchestration - the state machine the model walks
In graph-based orchestration, a human designs a directed graph ahead of time: nodes represent units of work (often, but not always, a single agent's turn), and edges represent allowed transitions, frequently guarded by a condition evaluated against shared state. At runtime, the system is always at some node; a decision function (which may itself be an LLM call, or plain code) looks at the current state and picks which outgoing edge to follow.

**Worked example - a support-ticket triage graph.** Nodes: `classify`, `handle_billing`, `handle_technical`, `escalate_to_human`, `close`. Edges: `classify -> handle_billing` if the classification confidence for "billing" exceeds 0.8; `classify -> handle_technical` if the classification is "technical" with similar confidence; `classify -> escalate_to_human` if confidence for every category is below 0.5; `handle_billing -> close` if the billing agent reports resolution; `handle_billing -> escalate_to_human` if the billing agent reports it cannot resolve the issue after 2 attempts. Every one of those five transitions was decided by the designer before the system ever ran. The model's job at the `classify` node is to produce a classification and a confidence score - genuinely a judgment call - but it cannot cause the system to transition anywhere except one of the three edges leaving `classify`. If a ticket turns out to need a transition nobody anticipated (say, a hybrid billing-and-technical issue), the graph has no edge for it, and the run either gets stuck or falls through to the closest matching edge - a real limitation, not a hypothetical one.

> **Example (2026):** LangGraph models exactly this pattern - a directed graph of nodes and conditional edges defined before execution and traversed deterministically at runtime, with the graph structure itself checkpointable and inspectable independent of any one run. Named here only as one illustrative implementation of the pattern; the pattern predates and outlives any specific framework.

### Pattern 2: role-based orchestration - personas that negotiate
In role-based orchestration, the designer does not draw a graph. Instead, each agent is given a role definition (a persona, a goal, a set of tools, sometimes a "backstory" establishing its perspective), and a coordinating agent - often itself an LLM call, sometimes called a "manager" or "planner" - decides at runtime which agent to invoke next, based on the task and the roles available, not a pre-authored edge list.

**Worked example - a content-production team.** Roles: `researcher` (gathers facts, has web-search tool access), `writer` (drafts prose from research, no tool access), `editor` (reviews drafts against a style guide, can send work back to `writer`), `fact-checker` (verifies claims against sources, can send work back to `researcher`). A manager agent receives "write a 1,200-word article on X," and *decides* the sequence: it might invoke `researcher`, then `writer`, then `editor`, and if `editor` flags an unverified claim, it might invoke `fact-checker` next rather than looping straight back to `writer` - a sequencing decision nobody pre-specified as an edge, because the manager reasoned about it from the roles' descriptions and the current situation. This is the source of role-based orchestration's central strength and central risk in the same breath: it can handle a sequence nobody anticipated (a genuine advantage over the graph, which has no edge for the unanticipated case), but *which* sequence it picks is itself a probabilistic judgment call by a model, not a guarantee - the same manager agent given the same situation twice is not guaranteed to sequence it identically.

> **Example (2026):** CrewAI frames orchestration exactly this way - agents get a role, goal, backstory, and tool set, and can run in a designer-specified sequence or under a manager agent that delegates hierarchically at runtime. Reports from 2026 practitioner benchmarks note this role-context (role + goal + backstory resent on every call) carries a real, measurable token cost compared to a leaner call shape - a concrete illustration that the flexibility of role-based orchestration is not free. Named as one illustrative implementation, not the pattern's defining identity.

### Pattern 3: deterministic-script orchestration - agents as functions, code as the spine
In deterministic-script orchestration, the designer writes ordinary code - a script, a pipeline, a workflow function - that calls agents the way it would call any other function: pass typed input, get typed output back, and the *code* (not any model) decides what happens with that output, including whether to call another agent, retry, branch, or stop. No model anywhere in the control-flow path chooses "what happens next" - models are invoked purely to produce a value inside a step whose position in the sequence was fixed by the code.

**Worked example - a legacy-modernization pipeline.** A COBOL-to-Python migration tool: step 1, a `parser` agent extracts the COBOL program's control structure into a structured intermediate representation (an LLM call, but its *output* is validated against a schema by code, not judged by another model); step 2, ordinary code runs static analysis over that IR to compute a dependency order for translating each module; step 3, for each module in that fixed order, a `translator` agent produces Python and a `verifier` agent runs the translated module's output against the original COBOL module's output on a fixed test-input set - and *code*, not a model, decides pass/fail from that comparison and decides whether to retry the `translator` step or move to the next module. Nothing here is a model deciding the next step; the model produces values, and code owns the transitions entirely. Comparative work on exactly this migration task (arXiv:2605.09894, 2026) found deterministic orchestration produced consistently better worst-case correctness and lower run-to-run variance than letting an LLM decide the translation order and retry logic itself - the reliability gain came specifically from removing the model from the control-flow decision, not from a better model.

> **Example (2026):** the Claude Agent SDK's Tool Runner and comparable "orchestrator code calls agent, agent calls tool, code decides next call" harnesses illustrate this pattern in production coding-agent tooling. Named as one illustrative implementation; the underlying idea - code, not the model, owns control flow - is the durable part.

### Choosing among the three: the actual axis, not a popularity contest
The three patterns are not ranked best-to-worst - they answer different questions about the task:
- **Is the space of valid "next steps" enumerable in advance, and does getting an unanticipated transition wrong matter?** If yes to both, graph-based orchestration is worth the upfront design cost: you get an auditable map of every path the system can take, and conditional edges give you real branching without surrendering the guarantee that only anticipated paths are reachable.
- **Does the task genuinely benefit from a sequencing decision that no human could fully anticipate, and can you tolerate that sequencing decision being probabilistic and non-reproducible?** If yes, role-based orchestration's flexibility is buying something real - just budget for its token cost and its non-determinism as ongoing costs, not one-time design costs.
- **Is the sequence of steps actually fixed once you think about it (parse, then analyze, then translate, then verify - always in that order, for every input), and is the value you need from an LLM confined to producing an output at each already-fixed step?** If yes, deterministic-script orchestration is available and is strictly cheaper to test, debug, and reason about than either alternative, because control flow is ordinary code, not a probabilistic decision at all.

A well-designed system frequently mixes all three at different scopes: a deterministic script might own the top-level pipeline while one step inside it is a small graph, and one node inside *that* graph might delegate to a role-based sub-crew for a genuinely open-ended sub-task. The mistake is not choosing "the wrong one" globally - it's applying one pattern uniformly to a system whose sub-problems actually have different answers to the question above.

## Pros
- **Graph-based**: auditable, checkpointable, debuggable at the level of individual transitions; branching is real but bounded to pre-declared edges.
- **Role-based**: handles genuinely unanticipated sequencing without a redesign; the persona abstraction maps naturally onto how humans describe a team, which speeds up initial design.
- **Deterministic-script**: cheapest to test (ordinary unit/integration tests apply to the control flow itself), lowest run-to-run variance, and the strongest reliability guarantees, because no part of "what happens next" is probabilistic.

## Cons
- **Graph-based**: the graph has no edge for a transition nobody anticipated; extending it for a new case is a design change, not a runtime adaptation, and complex graphs become their own maintenance burden.
- **Role-based**: the manager's sequencing decision is itself a non-reproducible model output - the same input can legitimately produce a different valid sequence on two runs, which complicates debugging and testing; role-context resent on every call carries a real token/cost overhead.
- **Deterministic-script**: cannot adapt to a case the designer didn't write a branch for; every genuinely open-ended judgment call has to be pushed down into a single step's output rather than expressed as control flow, which can force awkward workarounds for tasks that are inherently exploratory.

## Alternatives
- **Single-agent loop with tool access (no orchestration architecture at all)** — when lesson 01's threshold for splitting into multiple agents isn't met, none of these three patterns applies; don't introduce orchestration architecture for a task one agent handles fine.
- **Pure event-driven / reactive architecture (agents subscribe to events, no central decision-maker of any kind)** — decentralizes further than role-based orchestration; preferable when agents are truly independent services with no single owner of sequencing, at the cost of the harder-to-reason-about behavior lesson 06 covers (emergent behavior from purely local decisions).
- **Human-in-the-loop workflow tooling with an LLM step embedded (e.g., a business-process/BPM engine calling a model at specific steps)** — inverts the framing: the orchestration substrate is not agent-first at all, it is a general workflow engine that happens to call a model as one of its steps; preferable when the surrounding process has other non-AI steps that matter equally (approvals, external system calls) and agent orchestration is not the main design problem.

## When to use it
Reach for graph-based orchestration when transitions are enumerable and auditability matters (regulated workflows, customer-facing systems where an unexpected path is itself a defect). Reach for role-based orchestration when the task's decomposition genuinely cannot be fully mapped in advance and some non-determinism in sequencing is an acceptable cost for adaptability (open-ended research or content tasks). Reach for deterministic-script orchestration whenever the actual sequence of steps is fixed regardless of input - which, on inspection, is a large share of real pipelines that look "agentic" on the surface but have a control flow a human could draw as a flowchart in five minutes.

## When NOT to use it
Do not reach for role-based orchestration by default because it "feels" the most agentic - if the sequence is actually fixed, a deterministic script achieves the same outcome with far less variance and far easier testing, and the role abstraction's token overhead is then pure cost with no matching benefit. Do not force a graph-based design onto a task whose valid transitions genuinely cannot be enumerated up front - you will spend the design budget building a graph that gets extended with a new edge every week, which is a sign the task wanted role-based delegation instead. And do not build any of the three where lesson 01's single-agent threshold was never crossed - orchestration architecture is a answer to "how do multiple agents coordinate," not a default starting posture.

## Key takeaways / mental model
Ask one question first: who decides what happens next - a pre-drawn graph, a model reasoning about roles at runtime, or code that never asks a model at all? That answer, not the framework name on the tin, is the architecture. Graph-based trades adaptability for auditability; role-based trades auditability and determinism for adaptability; deterministic-script gives up all in-flow adaptability for the strongest reliability guarantee available. Most real systems are not one pattern applied uniformly - they nest a deterministic spine around a graph around a role-based sub-crew, matched at each scope to whether that scope's "next step" question is actually enumerable, actually needs runtime judgment, or is actually already fixed.

## Self-check questions
1. You're designing a system that processes insurance claims: intake, fraud-scoring, either auto-approval or human review, then payout. A colleague proposes role-based orchestration because "it's the most flexible." Do you agree? Which pattern fits better, and why, given what you know about the claim workflow's actual branching?
2. A role-based crew (researcher -> writer -> editor -> fact-checker) is run twice on the identical input and produces two different agent-call sequences both times. Is this a bug? What would you check before concluding it needs to be "fixed," and what would fixing it even mean given the pattern's nature?
3. Sketch a system that nests all three patterns at different scopes: a top-level deterministic-script pipeline, a graph-based sub-step, and a role-based sub-crew inside one node of that graph. What real task might justify that nesting, and what would you lose if you flattened it to a single pattern throughout?
4. The COBOL-to-Python worked example found deterministic orchestration reduced run-to-run variance compared to LLM-controlled orchestration. Explain, in terms of who owns the "what happens next" decision, why that result is exactly what the pattern predicts rather than a surprise.
5. A graph-based support-ticket triage system keeps getting stuck on hybrid billing-and-technical tickets because no edge covers that case. Your colleague wants to "just let the classify node use its judgment to route anywhere." What pattern are they actually proposing switching to, and what would that trade away?

## References
- [TrueFoundry: What Is Multi-Agent Orchestration? A Complete Guide (2026)](https://www.truefoundry.com/blog/what-is-multi-agent-orchestration)
- [TrueFoundry: Best Multi-agent Orchestration Frameworks in 2026](https://www.truefoundry.com/blog/multi-agent-orchestration-frameworks)
- arXiv:2606.26924 - A Deterministic Control Plane for LLM Coding Agents (2026)
- arXiv:2605.09894 - Deterministic vs. LLM-Controlled Orchestration for COBOL-to-Python Modernization (2026)
- arXiv:2604.11378 - From Agent Loops to Structured Graphs: A Scheduler-Theoretic Framework for LLM Agent Execution (2026)
- `agentic-engineering/multi-agent-orchestration/lessons/04-coordination-mechanisms.md` (prerequisite: shared state, message passing, task lists as the primitives these patterns are built from)
