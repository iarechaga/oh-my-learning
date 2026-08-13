---
id: multi-agent-orchestration/04
subject: multi-agent-orchestration
title: "Coordination Mechanisms: Shared State, Message Passing, and Task Lists"
slug: coordination-mechanisms
status: drafted
mastery:
seniority: senior
source: "Claude by Anthropic, Multi-agent coordination patterns: Five approaches and when to use them (2026); Anthropic Engineering, How we built our multi-agent research system (Jun 2025); AgentPatterns.ai, Orchestrator-Worker Pattern for AI Agent Development (2026); Redis, Multi-agent systems: Why coordinated AI beats going solo (2026)"
durability: durable
prerequisites: [multi-agent-orchestration/03]
created: 2026-08-10
updated: 2026-08-10
---

# Coordination Mechanisms: Shared State, Message Passing, and Task Lists

## TL;DR
Once a system has more than one agent working toward a shared goal, they need a concrete mechanism to avoid duplicating work, missing dependencies, or acting on stale information - and the choice of mechanism (funneling everything through one coordinator, publishing to shared storage, sending direct messages, or claiming work from a shared queue) is not interchangeable plumbing, it is a structural decision that determines the system's bottlenecks, debuggability, and failure modes.

## The idea
`multi-agent-orchestration/03` established that a lead agent or a fixed backbone decides *when* autonomy kicks in and *what* gets delegated. This lesson is one layer more concrete: once two or more agents are actually running - whether concurrently as in `multi-agent-orchestration/01`'s parallel case, or sequentially via repeated delegation as in `multi-agent-orchestration/02` - how do they actually know what has already been done, what still needs doing, and what each other found? Without an explicit answer to that question, multi-agent systems default to the worst case: agents silently duplicate each other's work, act on information another agent has since invalidated, or simply never learn something a sibling already discovered.

Coordination mechanisms are the infrastructure that answers this. They are not a single pattern with variants; they are genuinely different architectures with different bottlenecks, and picking one is a real design decision that should follow from the shape of the task - specifically, how independent the agents' work actually is, how much they need to see of each other's intermediate findings, and how much central visibility versus local autonomy the task can tolerate.

## How it works

### Orchestrator-subagent: all coordination flows through one agent
The simplest and most common pattern: a single lead agent decomposes the task, delegates pieces to subagents (the mechanism from `multi-agent-orchestration/02`), and every subagent reports back only to the orchestrator - subagents never talk to each other directly. The orchestrator holds the only coherent view of the whole task; each subagent only ever sees its own scoped piece.

**Worked example.** A lead agent researching "what are the top three risks in adopting technology X" spawns three subagents, one per candidate risk area (security, performance, ecosystem maturity), each with its own scoped briefing. Each subagent works independently and reports back to the orchestrator alone; subagent A investigating security has no visibility into what subagent B found about performance, and does not need it, because the risk areas are genuinely independent (per the test from `multi-agent-orchestration/01`). The orchestrator synthesizes all three reports into the final answer.

**Why this bottlenecks.** Because every subagent's output has to pass through the orchestrator - to be read, understood, and acted on by one context - the orchestrator's own processing capacity caps how much the whole system can absorb. Ten subagents reporting back simultaneously does not make the orchestrator's synthesis step ten times faster; it has to read and reconcile ten reports serially, in one context, which is exactly the single-agent context-load problem from `prompting-context-engineering/10`, now recurring at the orchestrator level. This pattern is the right default in most cases specifically because that bottleneck is well-understood and easy to reason about, not because it is the most scalable option - it isn't.

### Shared state (blackboard): agents read and write a common store
Instead of reporting to a central coordinator, agents coordinate through persistent shared storage - a database, a shared document, a set of files - that any agent can read from and write to. An agent checks the store for relevant information, does its work, and writes its findings back for others to find. No agent needs to know which other agents exist or what they are doing; coordination happens indirectly, through the shared state itself.

**Worked example.** Several research agents are investigating a spreading class of security vulnerabilities across a large codebase. Rather than routing every finding through one orchestrator, each agent writes what it finds directly to a shared findings document: "confirmed SQL injection risk in `orders.py:142`," "checked `users.py`, no issue found." An agent that starts investigating a file already covered can check the shared document first and skip redundant work; an agent whose finding in one file suggests a related pattern can note that pattern in the shared store for whichever agent investigates the next file to pick up. This is well suited to exactly this kind of collaborative discovery task, where agents genuinely build on each other's findings but do not need a central authority approving every step.

**What this costs.** Removing the single point of failure (no one orchestrator has to process everything) comes at the cost of a real risk: without explicit termination conditions and conflict handling, agents can end up in reactive loops (agent A reacts to agent B's write, which triggers a reaction from agent C, which re-triggers agent A) or duplicate work anyway, if two agents check the store at nearly the same moment before either has written its result, and both proceed on the same task believing it unclaimed - a race condition analogous to any concurrent-write problem in distributed systems, just expressed through agent behavior instead of database transactions.

### Message passing (message bus): agents publish and subscribe to events
Agents communicate through an event-driven bus: an agent publishes a message to a topic, and any agent subscribed to that topic receives it, without either side needing to know about the other directly. This decouples agents from each other structurally - a new agent with a new capability can start receiving relevant work simply by subscribing to the right topic, with no rewiring of the agents that already exist.

**Worked example.** A customer-support system publishes every incoming ticket to a "new-ticket" topic. A triage agent subscribes and classifies each ticket, publishing the result to a "classified" topic. A billing-specialist agent and a technical-specialist agent each subscribe only to their relevant classification, picking up exactly the tickets that match. Adding a third specialist later - say, for account-security tickets - means only adding one new subscriber; nothing about the triage agent or the existing specialists needs to change.

**What this costs.** The same decoupling that makes the system easy to extend makes it hard to trace: because no agent has a direct view of who else is listening or what happens downstream of its own publish, following a single ticket's actual path through the system for debugging purposes requires reconstructing it after the fact from logs, rather than reading it off a single call stack the way an orchestrator-subagent trace can be read. Routing accuracy becomes the load-bearing correctness property - if a message is published to a topic no relevant agent is subscribed to, or subscribed to by the wrong agent, the failure can be silent (nothing errors, the work simply never happens) rather than loud.

### Shared task list: agents claim bounded work from a queue
A shared, structured list of discrete tasks - with explicit dependency tracking and some form of locking to prevent two agents claiming the same task - that multiple worker agents pull from. A worker claims an available (unclaimed, dependency-satisfied) task, works it autonomously, marks it complete, and claims the next one. Unlike subagents spun up per delegation (`multi-agent-orchestration/02`), these workers are commonly persistent across many task assignments, accumulating their own working context as they go rather than starting fresh each time.

**Worked example.** A large-scale migration task - update forty call sites to a new function signature - is represented as forty entries in a shared task list, some of which depend on others (a shared helper function must be migrated before the call sites that use it). Several worker agents pull unclaimed, dependency-satisfied tasks, lock them so no other worker claims the same one, do the migration, mark the task done, and pull the next. This captures real parallelism on genuinely independent chunks of a larger structurally-similar task, without needing a single orchestrator to hand out every single assignment one at a time.

**What this costs.** This pattern assumes the work genuinely decomposes into bounded, mostly-independent tasks with explicit (not implicit) dependencies - exactly the independence test from `multi-agent-orchestration/01`, now needing to be encoded as literal dependency edges in the task list rather than just reasoned about informally. It is a poor fit when workers need to share intermediate findings with each other mid-task rather than only at task completion - the task list tracks completion state, not the kind of rich, findings-level exchange the shared-state pattern is built for.

### Generator-verifier: a two-agent quality loop, not a scaling mechanism
Worth naming separately because it solves a different problem than the four patterns above: one agent (the generator) produces output, a second agent (the verifier) evaluates it against explicit criteria and either accepts it or routes feedback back to the generator for a revised attempt. This is not primarily about coordinating many agents' work across a large task; it is about using a second agent as a structured check on a first agent's output, most valuable when the output has explicit, checkable criteria (does this code pass the tests, does this document meet the compliance checklist) rather than open-ended quality.

**What this costs.** It can stall: if the generator is structurally unable to produce output that satisfies the verifier's criteria (the criteria are wrong, or the task is genuinely infeasible), the loop between them will not resolve on its own and needs an external circuit breaker - an iteration cap, or a human escalation path - the same termination discipline a single agentic loop needs (`tool-use-agentic-loop/03`).

### Choosing among them
The decision follows directly from the shape of the task, using questions that build on the independence test from `multi-agent-orchestration/01`:

| Question | Points toward |
|---|---|
| Is there one natural authority who should see the whole picture, and is the number of parallel workers small enough not to bottleneck it? | Orchestrator-subagent |
| Do agents need to build on each other's *findings*, not just avoid claiming the same *task*? | Shared state (blackboard) |
| Will the set of participating agents or capabilities grow or change over time, and is traceability less critical than extensibility? | Message passing (bus) |
| Is the work a large batch of bounded, mostly-independent units with explicit dependencies between some of them? | Shared task list |
| Is the core problem "is this one output good enough," not "how do many agents divide a large task"? | Generator-verifier |

## Pros
- **Orchestrator-subagent**: simplest to reason about and debug - one place holds the whole picture; well suited to short, clearly-scoped subtasks.
- **Shared state**: no single point of failure; supports opportunistic, non-linear collaboration where agents genuinely build on each other's discoveries.
- **Message passing**: highly extensible - new agents and capabilities plug in without rewiring existing ones.
- **Shared task list**: real parallelism on large batches of bounded, structurally similar work, with dependency tracking preventing out-of-order execution.
- **Generator-verifier**: a targeted, explicit quality gate for outputs with checkable correctness criteria.

## Cons
- **Orchestrator-subagent**: the orchestrator's own context and processing capacity is a hard ceiling on throughput; it is a serial bottleneck no matter how many subagents run in parallel underneath it.
- **Shared state**: race conditions on near-simultaneous reads/writes, and a real risk of reactive loops with no natural termination if not explicitly designed against.
- **Message passing**: hard to trace and debug after the fact; a routing mistake can fail silently instead of erroring.
- **Shared task list**: needs the work to genuinely decompose into bounded units with explicit dependencies; a poor fit for tasks needing rich mid-task findings exchange between workers.
- **Generator-verifier**: can stall indefinitely without an external cap if the generator cannot satisfy the verifier's criteria.

## Alternatives
- **No explicit coordination mechanism at all** — acceptable only when agents are so fully independent that they never need to know about each other's existence or output; anything short of that will reproduce duplicated work or missed dependencies without one of the mechanisms above.
- **A single agent with sequential subagent delegation** (`multi-agent-orchestration/02`) — sidesteps the coordination-mechanism question entirely by never having more than one agent active "in charge" at a time; appropriate when the task does not actually need concurrent multi-agent activity.
- **Specific vendor implementations of these patterns** (shared task lists with file locking, particular message-bus products, particular blackboard stores) — the concrete tooling landscape is covered in `landscape-snapshot/02`; this lesson covers the durable architectural patterns, not which product implements which one.

## When to use it
Use orchestrator-subagent as the default for most multi-agent tasks - it handles the widest range of problems with the most predictable failure surface. Reach for shared state when agents need to build on each other's intermediate findings during a collaborative investigation. Reach for message passing when the set of participating agents is expected to grow or change and extensibility matters more than easy traceability. Reach for a shared task list when the work is a large batch of bounded, mostly-independent units with real (not just assumed) dependencies between some of them. Reach for generator-verifier specifically when the problem is output quality against explicit criteria, not task decomposition at all.

## When NOT to use it
Do not reach for shared state or message passing by default "for scalability" when an orchestrator-subagent setup would never actually bottleneck at the task's real scale - both add real debugging and race-condition risk that is not worth paying for a bottleneck that was never going to matter. Do not use a shared task list for work that is not actually decomposable into bounded, mostly-independent units with explicit dependencies - forcing genuinely interdependent work through a task-claiming queue will produce workers claiming tasks they cannot correctly complete without information a sibling worker has not yet posted anywhere. Do not use generator-verifier as a substitute for genuine multi-agent task decomposition - it solves a narrower problem (is this one output correct) and does not, by itself, coordinate a large task across many agents.

## Key takeaways / mental model
There is no single "multi-agent coordination" mechanism - there are several genuinely different architectures (central authority, shared memory, decoupled messaging, claimable work queue, generator/checker pair), each with a different bottleneck and a different failure mode, and the choice among them should follow directly from how the specific task's agents actually need to relate to each other: does one agent need the whole picture, do agents need to see each other's findings mid-task, does the set of agents change over time, is the work bounded and batchable, or is the real question just "is this one output good enough." Picking the wrong mechanism does not just cost efficiency - it produces the exact coordination failures (duplicated work, missed dependencies, silent routing failures, unresolved reactive loops) covered in depth in `multi-agent-orchestration/06`.

## Self-check questions
1. A team is building a system where five specialist agents each monitor a different data source and need to alert a human the moment any of them detects an anomaly, with the set of monitored sources expected to grow over the next year. Which coordination mechanism fits best, and what specifically about "the set of sources will grow" drives that choice?
2. Explain concretely why an orchestrator-subagent pattern's bottleneck does not go away just by adding more subagents. What is actually the constrained resource?
3. A shared-state (blackboard) system for collaborative research starts exhibiting a pattern where two agents keep re-triggering each other's investigations in a loop that never terminates. Diagnose what is missing from the system's design, referencing the specific risk named in this lesson.
4. Compare a shared task list to shared state for a large-scale codebase migration where most of the four hundred call sites are independent, but a dozen of them depend on a shared helper being migrated first, and a handful require workers to compare notes on an emerging inconsistent pattern they are discovering as they go. Which single mechanism fits best, and what does it fail to handle - would you combine two mechanisms here, and why?
5. A generator-verifier loop for a code-generation task has been running for twenty iterations without converging. What does this observable symptom tell you about the task or the criteria, and what would you change?

## References
- Claude by Anthropic, "Multi-agent coordination patterns: Five approaches and when to use them" (2026) - https://claude.com/blog/multi-agent-coordination-patterns
- Anthropic Engineering, "How we built our multi-agent research system" (June 2025) - https://www.anthropic.com/engineering/multi-agent-research-system
- AgentPatterns.ai, "Orchestrator-Worker Pattern for AI Agent Development" (2026) - https://agentpatterns.ai/multi-agent/orchestrator-worker/
- Redis, "Multi-agent systems: Why coordinated AI beats going solo" (2026) - https://redis.io/blog/multi-agent-systems-coordinated-ai/
