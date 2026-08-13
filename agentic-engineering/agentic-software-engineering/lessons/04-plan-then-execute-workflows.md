---
id: agentic-software-engineering/04
subject: agentic-software-engineering
title: "Plan-Then-Execute Workflows and Task Decomposition"
slug: plan-then-execute-workflows
status: drafted
mastery:
seniority: senior
source: "Anthropic, Building Effective AI Agents (Dec 2024, updated 2026); Anthropic, 2026 Agentic Coding Trends Report (2026); DEV Community, Varun Pratap Bhardwaj, Separation of Planning and Execution: The Key Pattern for Reliable AI Coding Agents (2026); arXiv 2601.07577, Beyond Entangled Planning: Task-Decoupled Planning for Long-Horizon Agents (Jan 2026); arXiv 2604.12147, From Plan to Action: How Well Do Agents Follow the Plan? (2026)"
durability: durable
prerequisites: [agentic-software-engineering/03]
created: 2026-08-10
updated: 2026-08-10
---

# Plan-Then-Execute Workflows and Task Decomposition

## TL;DR
Once a spec exists as the source of truth (`agentic-software-engineering/03`), a second, separate decision remains: does the agent go straight from spec to code, or does it first produce an explicit, human-reviewable plan - a sequence of small, ordered, individually reversible steps - and only start writing code after that plan is approved? Separating planning from execution turns a single large, hard-to-review change into a series of small, checkable ones, at the cost of an extra review round-trip and the risk that the plan itself is wrong in ways that are only visible once execution starts.

## The idea
A spec says *what* should be true when the work is done. It says nothing about *how* to get there in what order, or how to break a change that touches twelve files into pieces a reviewer can actually hold in their head. Left alone, an agent given a large spec and no further structure will typically attempt the whole change in one pass: write all twelve files, run the tests, and present one enormous diff. This is exactly the failure mode `multi-agent-orchestration/03`'s single-agentic-loop discussion warns about, one level down: a large, unstructured pass through a big problem is unpredictable, hard to steer mid-way, and - critically for code specifically - produces a diff too large for a human to review with any real confidence, however good the underlying model.

Plan-then-execute is the practice of inserting an explicit checkpoint between "the agent understands the spec" and "the agent starts writing code": the agent first produces a **plan** - an ordered list of concrete steps, each one small enough to review and reason about independently, each one leaving the codebase in a working (or at least comprehensible) state - and only proceeds to execution once that plan has been reviewed, corrected if necessary, and approved. This is the same "separate the structural decision from the content decision" idea `multi-agent-orchestration/03` applied to multi-agent systems, now applied to a single agent's own work on a single task: the plan fixes the *structure* of the change (what steps, in what order) before the agent starts filling in the *content* of each step (the actual code).

The idea did not originate with LLM agents. Classical AI planning research separated task decomposition from action execution decades before language models existed, precisely because interleaving the two in complex domains produces plans that look locally reasonable at each step but turn out to be globally inconsistent - a lesson that transfers directly to coding agents, where a step that looks fine in isolation can quietly assume a data model or interface that an earlier, unplanned improvisation already broke.

## How it works

### The two phases, concretely
**Planning phase:** given the spec, the agent reads the relevant parts of the codebase, then produces a plan artifact - not code, just a structured description of the intended sequence of changes. A good plan for a coding task typically includes: the list of files to be created or modified, what each step accomplishes, the order steps must happen in (and why - e.g. "the schema migration must land before the code that reads the new column"), and what should be true (which tests pass, what behavior is observable) after each step. No code is written during this phase.

**Execution phase:** a separate pass - often literally a new agent invocation, sometimes even a different agent or model tier, taking the approved plan as its entire brief - implements the plan step by step, checking each step's stated success criterion before moving to the next. If a step's outcome contradicts what the plan assumed (a test the plan expected to pass still fails, an interface turns out to have a different shape than the plan described), execution stops and returns to a human or back to planning, rather than improvising past the mismatch.

### Worked example: adding a new field to an API, unplanned vs. planned
A team needs to add a `discount_code` field: accepted on the checkout API, validated against an active-promotions table, persisted with the order, and surfaced in the order-history view. Given straight to an agent with no plan step, a typical result is one seven-file diff: the API schema, the validation logic, the database migration, the ORM model, the order-history query, the order-history template, and a new test file, all changed at once, submitted as a single PR. The reviewer has to reconstruct the dependency order themselves to check it makes sense (did the migration really need to run before the model change? does the validation actually run before persistence, or after?), and if something is wrong - say the migration is missing a default value for existing rows - the fix has to be untangled from six other simultaneous changes.

With a plan-then-execute approach, the agent first proposes: **Step 1** - add the `discount_code` column via migration, nullable, with a rollback; **Step 2** - add the field to the ORM model and confirm existing tests still pass with the column present but unused; **Step 3** - add validation against the active-promotions table in the checkout API, behind a check that returns a clear 400 on an invalid code; **Step 4** - persist the validated code on order creation; **Step 5** - surface the field in the order-history view and its test. A human reviewer can approve or correct this five-line plan in under a minute - catching, for instance, that Step 1's migration should default existing rows to `NULL` explicitly rather than leaving it implicit, before any code exists. Execution then produces five small, individually reviewable diffs instead of one large one, and if Step 3's validation logic turns out wrong, the fix touches one file, not seven.

### Worked example: when the plan itself needs revision mid-execution
A plan for refactoring a payment module assumes, at the planning stage, that a `LegacyPaymentGateway` class is used in exactly one place. Step 3 of the plan is "delete `LegacyPaymentGateway` after migrating its one caller to the new interface." During execution, the agent discovers a second, indirect caller reached through a factory function the planning pass never traced. A pure single-pass agent might simply delete the class anyway, since deletion was "the plan," silently breaking the second caller. A plan-then-execute workflow with a working execution-time check instead treats this as a plan invalidation: the assumption the plan was built on ("exactly one caller") is now known to be false, so execution halts at Step 3, reports the discrepancy, and either a human or a fresh planning pass revises the plan (e.g., insert a new step to migrate the second caller first) before execution resumes. The value here is not that the agent never makes mistakes - it still missed the second caller during planning - but that the mistake surfaces as an explicit, visible checkpoint rather than silently propagating into a merged change.

### Task decomposition granularity: what makes a step "small enough"
Not every decomposition is useful. A plan with two steps ("write the feature," "write the tests") is barely more structured than no plan at all - each step is still too large to review meaningfully. A plan with fifty single-line steps is equally unhelpful in the other direction - the overhead of reviewing fifty checkpoints exceeds the overhead it was meant to save. The practical heuristic is the same "would the next step change if the last observation had come back differently" question from `multi-agent-orchestration/03`, applied to grain size: a step is well-sized when it corresponds to one independently verifiable unit of change - one migration, one endpoint's validation logic, one view's rendering - such that after that step, there is a concrete, checkable fact about the codebase (a test passes, an endpoint returns the right shape) that either holds or doesn't, and a reviewer can approve that one fact without having to hold the whole remaining plan in their head at the same time.

## Pros
- Converts one large, hard-to-review diff into a sequence of small, individually reviewable ones, directly addressing the "can a human actually verify this" problem that gets worse as agent-authored change volume grows (`agentic-software-engineering/05` covers the review side in depth).
- Surfaces planning mistakes (wrong assumptions about the codebase, a missed dependency, an ordering error) before any code is written, when they are cheapest to fix, rather than after execution has already produced a large diff built on the wrong assumption.
- Gives a human a natural, low-cost checkpoint to redirect the agent - correcting a five-line plan takes far less time and attention than reviewing and then requesting revisions on a completed seven-file change.
- Each step leaving the codebase in a working, comprehensible state makes it far easier to stop, resume, or hand off mid-task - a property async and autonomous execution (`agentic-software-engineering/06`) depends on directly.

## Cons
- Adds a review round-trip and real latency before any code exists; for genuinely small, low-risk changes this overhead is pure cost with no offsetting benefit.
- The plan can be wrong in ways only execution reveals (the second-caller example above) - plan-then-execute reduces this risk but does not eliminate it, and a plan approved with false confidence can be worse than no plan, since it creates an illusion of having already checked the work.
- Requires the reviewer to actually engage with the plan rather than rubber-stamping it; a plan approved without real scrutiny provides none of the benefit and still incurs the latency cost.
- Decomposing well is itself a skill the agent (or the human directing it) must have; a poorly granulated plan - too coarse or too fine - can cost more overhead than it saves, as described above.

## Alternatives
- **Single-pass execution with no explicit plan** — appropriate for genuinely small, well-understood changes (a one-line bug fix, a config value change) where the overhead of a separate planning checkpoint exceeds any benefit; per `agentic-software-engineering/02`, this is a controlled, deliberate choice, not the default absence of one.
- **Plan embedded inline, not reviewed separately** — some agent harnesses generate and display a plan as part of a single continuous session without a hard stop for human approval before execution; this captures some of the "structure the work" benefit but loses the explicit checkpoint where a human can catch a wrong assumption before code exists.
- **Iterative, unplanned exploration followed by a large review** — appropriate when the task is genuinely exploratory and the right decomposition is not knowable in advance (echoing the incident-response worked example in `multi-agent-orchestration/03`); forcing a plan onto a task whose shape cannot yet be known produces a plan that will be wrong, which is worse than no plan.

## When to use it
Use plan-then-execute for changes that are non-trivial in scope (touch multiple files, cross a module boundary, or involve an ordering constraint like a migration preceding the code that depends on it) and where the cost of a wrong assumption compounding through several steps is meaningfully higher than the cost of one extra review round-trip. It is especially valuable when execution will run with limited supervision (`agentic-software-engineering/06`), since the plan is often the only artifact a human reviews before the work happens unsupervised.

## When NOT to use it
Skip the explicit plan step for changes small and well-scoped enough that a plan would just restate the change itself (a one-line fix, a single well-understood function edit) - the round-trip cost then exceeds any benefit. Also avoid forcing a plan onto genuinely exploratory work where the right sequence of steps cannot be known until earlier steps' results are in hand; per the incident-response contrast in `multi-agent-orchestration/03`, that shape of task needs an adaptive loop, not a plan committed to in advance.

## Key takeaways / mental model
Plan-then-execute inserts one explicit checkpoint - a small, ordered, human-reviewable plan - between "the agent understands what to build" and "the agent starts building it," turning one large hard-to-review change into a sequence of small checkable ones. The core skill is decomposition granularity: a step should correspond to one independently verifiable fact about the codebase, not "half the feature" and not "one line." The plan is not infallible - execution can still reveal a wrong assumption - but a wrong assumption caught at an explicit checkpoint is far cheaper than the same assumption silently baked into a merged seven-file diff.

## Self-check questions
1. A teammate proposes skipping the planning step entirely for a database migration that touches three tables and two of the services that read them, arguing "the agent is fast enough that reviewing the final diff is just as quick." What would you say back, using the ordering-constraint argument from this lesson?
2. Take the `discount_code` worked example and describe what a *badly* granulated plan for the same task would look like at both extremes (too coarse, too fine), and why each extreme fails to deliver the benefit plan-then-execute is meant to provide.
3. In the `LegacyPaymentGateway` example, the plan's wrong assumption ("exactly one caller") was only discovered during execution, not during planning. What would you change about the planning phase itself to make that kind of miss less likely, and what limits how much planning can catch in advance?
4. Explain, in your own words, why plan-then-execute is described as "the same idea as `multi-agent-orchestration/03`, one level down" rather than a genuinely new concept - what is the structural decision being separated from the content decision in each case?
5. A reviewer approves a five-step plan in under thirty seconds, then spends twenty minutes reviewing the resulting diffs. What does this pattern suggest about whether the reviewer is actually getting the benefit this lesson claims plan-then-execute provides, and what would you change?

## References
- Anthropic, "Building Effective AI Agents" (December 2024, updated 2026) - https://www.anthropic.com/research/building-effective-agents
- Anthropic, "2026 Agentic Coding Trends Report" (2026) - https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf
- Varun Pratap Bhardwaj, DEV Community, "Separation of Planning and Execution: The Key Pattern for Reliable AI Coding Agents" (2026) - https://dev.to/varun_pratapbhardwaj_b13/separation-of-planning-and-execution-the-key-pattern-for-reliable-ai-coding-agents-5b53
- arXiv 2601.07577, "Beyond Entangled Planning: Task-Decoupled Planning for Long-Horizon Agents" (2026) - https://arxiv.org/pdf/2601.07577
- arXiv 2604.12147, "From Plan to Action: How Well Do Agents Follow the Plan?" (2026) - https://arxiv.org/html/2604.12147v1
