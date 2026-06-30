---
id: hard-parts/02
subject: hard-parts
title: The Architecture Quantum and Static Coupling
slug: architecture-quantum-static-coupling
status: drafted
mastery:
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 2
prerequisites: [hard-parts/01]
created: 2026-06-30
updated: 2026-06-30
---

# The Architecture Quantum and Static Coupling

This lesson introduces the architecture quantum as the practical boundary for independent change, then uses static coupling and connascence to show how to discover that boundary in real systems.

## TL;DR
An architecture quantum is the real unit of independent delivery: everything that must change and deploy together. You find that boundary mainly through static coupling, then validate runtime behavior with dynamic coupling. If parts share strong static coupling, they are one quantum even if they live in separate repos.

## The idea
Lesson 01 established that architecture is trade-offs, not universal best practices. Chapter 2 gives a practical lens for those trade-offs: identify the smallest unit that can change safely on its own. That unit is the architecture quantum.

Many teams say "we are microservices" while still sharing schemas, hidden conventions, and release timing. The code is split, but the operational fate is shared. Quantum thinking exposes that mismatch.
Three guiding questions:
1. What can we deploy independently, including data changes?
2. Which dependencies force lockstep releases?
3. Does each boundary represent one cohesive business purpose?

If those answers are clear, your decomposition is meaningful. If not, you likely have accidental distribution.

## How it works

### Definition first: what is an architecture quantum?
An architecture quantum is an independently deployable artifact with:
1. High functional cohesion.
2. High static coupling inside the boundary.
3. Synchronous dynamic coupling for the runtime interactions defining that unit.

The key is "artifact," not "service" label. A quantum is a deployable boundary that includes code, contracts, and data dependencies needed to operate correctly.

Quick test:
- If I deploy this unit alone, can it remain correct without coordinating another deploy?
- If the answer is repeatedly no, your real quantum is larger than your diagram.
### Property 1: independently deployable artifact
Independently deployable means build, test, release, and rollback can happen without lockstep deployment with neighbors.

A frequent mistake is counting only binaries or containers. A real quantum includes what it needs to run, which often means owning its own operational data store.

Why data ownership matters:
- Shared tables force shared migration timing.
- Shared schema semantics force cross-team coordination.
- Forced coordination means no true deploy independence.

Deployability checklist:
1. One pipeline can produce a releasable artifact for this boundary.
2. API compatibility is managed at the edge.
3. Schema evolution does not require unrelated releases.
4. Rollback can happen locally.

### Property 2: high functional cohesion
High functional cohesion means internals serve one bounded domain purpose.

Good cohesion examples:
- "Ticket triage lifecycle."
- "Incident escalation workflow."

Low cohesion example:
- "Users plus billing plus notifications because one team owned it first."

A practical cohesion test: if this boundary disappeared, would one meaningful business capability disappear with it? If yes, cohesion is likely high.

### Property 3: high static coupling inside the quantum
Inside a quantum, high static coupling is expected because pieces should evolve together. Across quanta, high static coupling is dangerous because it breaks independent deployment.

Static coupling is how parts are wired before runtime:
- source dependencies
- shared contracts/schemas
- shared libraries with lockstep assumptions
- shared database tables
- compile-time type dependencies

Because static coupling is visible in code, schemas, and build graphs, you can reason about it at design/build time.

Dynamic coupling is runtime call behavior (ordering, latency, synchronicity, retries). This lesson references it, but lesson 03 covers it deeply.

### Static coupling vs dynamic coupling
Use them for different decisions.

| Dimension | Static coupling | Dynamic coupling |
| --- | --- | --- |
| Main question | How are parts wired? | How do parts interact at runtime? |
| Evidence | imports, schemas, shared DB, build graph | call chains, retries, latency, ordering |
| Visibility | design/build time | runtime/operations time |
| Boundary effect | sets deploy boundary | sets runtime coordination risk |
| Deep dive | this lesson | [03-dynamic-coupling.md](03-dynamic-coupling.md) |

Rule:
- Static coupling answers "can we change independently?"
- Dynamic coupling answers "can we fail independently at runtime?"

### Connascence: language for coupling strength
Connascence gives a precise vocabulary for coupling strength instead of vague statements like "these are somewhat tied together."

Static connascence forms (weakest to strongest):
1. Name
2. Type
3. Meaning (Convention)
4. Position
5. Algorithm

Dynamic connascence forms include Execution order, Timing, Value, and Identity. Those are runtime concerns and belong mostly to lesson 03.

The ordering matters because stronger forms usually imply higher coordination cost and larger failure blast radius when boundaries are distant.

### The three connascence properties
Assess coupling with three properties:

1) Strength
- How invasive is coordinated change?
- Rename is weak; shared algorithm logic across systems is strong.

2) Locality
- How far apart are coupled elements?
- Strong coupling can be acceptable when local (same module/team/deployable).
- Strong coupling is risky when distant (cross-team/cross-service).

3) Degree
- How many elements are coupled?
- Two coupled modules are easier than twelve services coupled by one hidden convention.

Guideline:
- Minimize total connascence.
- Convert strong connascence to weaker forms when possible.
- Keep unavoidable strong connascence local.

### Worked example 1: shared ticket table forces one quantum
Scenario (Sysops Squad):
- Service A: Ticket Intake API.
- Service B: Ticket Workflow API.
- Both read/write the same `ticket` table.
- Both depend on shared `ticket-domain-model` library.

ASCII view:

+---------------------------------------------------------------+
| Declared split                                                |
|                                                               |
| +----------------------+     +-----------------------------+  |
| | Service A            |     | Service B                   |  |
| | Ticket Intake API    |     | Ticket Workflow API         |  |
| +----------+-----------+     +-------------+---------------+  |
|            |                               |                  |
|            +-------------+   +-------------+                  |
|                          |   |                                |
|                   +------v---v------+                         |
|                   | Shared DB schema |                         |
|                   | table: ticket    |                         |
|                   +------------------+                         |
|                                                               |
| Shared library: ticket-domain-model (used by A and B)         |
+---------------------------------------------------------------+

Step-by-step reasoning:
1. Team A renames `ticket.priority` to `ticket.severity`.
2. Shared schema migration touches both services.
3. Service B breaks unless updated in the same release window.
4. Shared model library change also requires coordinated version updates.
5. Therefore A and B are not independently deployable.
6. Real quantum includes A + B + shared schema + shared library.

Takeaway: two repos or two containers do not guarantee two quanta.

### Worked example 2: connascence of Name (weak)
Scenario: Service A publishes JSON field `assignedTo`; Service B consumes it.

Change: introduce `assignee` as the new field.

Steps:
1. Producer adds `assignee`, keeps `assignedTo` temporarily.
2. Consumer updates mapping to `assignee`.
3. Contract tests verify both during migration.
4. Producer removes old field after migration window.

Why this is weak:
- Coupling is explicit and lexical.
- Tooling and tests catch mismatch early.
- Migration is usually mechanical and low risk.

### Worked example 3: connascence of Meaning (dangerous at distance)
Scenario:
- Intake Service sends `status=7`.
- Escalation Service interprets `7` as "escalated."
- Meaning is undocumented convention.

Failure sequence:
1. Intake team reuses `7` for "awaiting-customer."
2. No compile-time break in Escalation Service.
3. Runtime behavior silently drifts; wrong escalations fire.
4. Incident appears as domain confusion, not obvious integration error.

Why risky:
- Strength is higher than Name because semantics are implicit.
- Locality is poor (cross-service).
- Degree grows as more consumers rely on code `7`.

Safer redesign:
1. Replace magic number with explicit enum string.
2. Publish versioned schema with semantic definitions.
3. Add contract tests for allowed values.
4. Treat semantic changes as versioned API changes.

### Worked example 4: monolith vs microservices through quantum lens
A monolith is usually one quantum because modules and data deploy together.

Microservices can be many quanta only when boundaries are truly independent.

Monolith (typically one quantum):

+-----------------------------------------------------------+
| Quantum M1                                                |
| +---------------+ +---------------+ +-------------------+ |
| | Orders module | | Billing module| | Support module    | |
| +---------------+ +---------------+ +-------------------+ |
| Shared process + shared operational database              |
+-----------------------------------------------------------+

Microservices (possible multiple quanta):

+----------------------------+   +----------------------------+
| Quantum Q1: Orders service |   | Quantum Q2: Billing        |
| + own DB                   |   | service + own DB           |
+----------------------------+   +----------------------------+

+----------------------------+
| Quantum Q3: Support        |
| service + own DB           |
+----------------------------+

Reasoning:
1. Monolith modules often ship as one release artifact -> one quantum.
2. Microservice style does not guarantee independent quanta.
3. Shared operational schema between services collapses boundaries.
4. Real architecture quality is about coupling boundaries, not service count.

### Practical method for identifying quantum boundaries
Use this in architecture reviews:

1. List candidate boundaries (modules/services/components).
2. Map static dependencies:
   - shared tables/schemas
   - shared mutable contracts
   - shared libraries requiring lockstep versions
   - compile-time cross-dependencies
3. Classify connascence between each pair.
4. Evaluate Strength, Locality, Degree.
5. Draw provisional quanta around strongly coupled sets.
6. Run deploy thought experiment: "Can this ship alone this week?"
7. If no, either merge boundary or weaken coupling form.

Workshop table template:

| Pair | Dominant connascence | Strength | Locality | Degree | Same quantum? |
| --- | --- | --- | --- | --- | --- |
| Intake <-> Workflow | Meaning + schema | medium-high | distant | 2+ | likely yes |
| Controller <-> DTO (same service) | Name/Type | low | local | low | acceptable |
| Two repos sharing algorithm logic | Algorithm | high | distant | medium | reconsider |

### How to weaken static coupling without fake decoupling
Pattern 1: separate data ownership
- Before: two services write one table.
- After: one service owns data; others use API/events.

Pattern 2: make semantics explicit
- Before: hidden status-code conventions.
- After: enum schema + versioned contract + tests.

Pattern 3: keep strong coupling local
- Algorithm connascence inside one codebase can be fine.
- The same connascence across distant services is brittle.

Pattern 4: use shared libraries carefully
- Shared kernel is acceptable only with clear ownership and evolution rules.
- Broad shared libs often become release-coupling traps.

### Why this concept matters
The quantum is the real meaning of "independent" in architecture. Most decomposition and data decisions are boundary decisions about quanta:
- Should this stay an internal module or become a service?
- Should this schema be owned here or split?
- Should we share code or duplicate thin mappings with explicit contracts?

Without this lens, teams often build distributed monoliths: many deployables, one effective quantum.

## Pros
- Gives a concrete unit for "independent" beyond style labels like monolith/microservices.
- Exposes hidden coupling, especially shared-schema coupling, early.
- Connascence improves architectural conversations with precise language.
- Connects design choices to delivery outcomes: coordination cost, rollback scope, blast radius.
- Encourages healthy decomposition: strong coupling local, weaker coupling across boundaries.

## Cons
- Can be misused as a rigid formula instead of a trade-off model.
- Coupling assessment still needs judgment; teams may score boundaries differently.
- Over-focusing on static coupling may hide runtime risks from dynamic coupling.
- Premature boundary optimization can slow delivery in early product phases.
- Some domains require intentional shared constraints, so full separation is not always ideal.

## Alternatives
- **DDD bounded contexts**: excellent semantic boundary tool, but does not automatically guarantee deployable independence.
- **Module dependency graphs**: great for compile-time structure and cycles, weaker for data ownership analysis.
- **Team Topologies framing**: optimizes for team cognitive load and ownership; complements, not replaces, quantum analysis.
- **Change-coupling mining from git history**: empirical view of what changes together; useful but backward-looking.

## When to use it
Use this lens when splitting a monolith, designing service boundaries, or diagnosing repeated coordinated releases that should not be necessary. It is especially valuable when shared data ownership is muddy and teams claim independence that operations does not observe.
## When NOT to use it
Do not force quantum analysis as heavy process for tiny internal tools where one deployable unit is clearly enough. Also avoid optimizing for "more quanta" as a vanity metric; extra boundaries can add operational overhead without business benefit.

If your primary issue is runtime propagation, latency, retries, or orchestration behavior, focus on dynamic coupling analysis in lesson 03.
## Key takeaways / mental model
Treat the architecture quantum as the atomic unit of safe change: whatever must be changed, tested, and deployed together is one quantum, regardless of repo count or container count.

Use connascence as your coupling meter:
- weaker forms (Name, Type) are easier across boundaries,
- stronger forms (Meaning, Position, Algorithm) should stay local,
- risk depends on strength + locality + degree together.

If two "services" share operational data and hidden semantics, they are likely one quantum in disguise.

## Self-check questions
1. Define architecture quantum and explain its three properties in your own words.
2. Why does a shared `ticket` table usually collapse two services into one quantum?
3. In what sense is connascence of Name weaker than connascence of Meaning?
4. Give one example where strong connascence is acceptable and one where it is dangerous due to locality.
5. How would you audit an existing system to discover actual quanta instead of declared services?
6. Why is service count a poor proxy for architectural independence?
## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 2
- [01-tradeoffs-no-best-practices.md](01-tradeoffs-no-best-practices.md)
- [03-dynamic-coupling.md](03-dynamic-coupling.md)
