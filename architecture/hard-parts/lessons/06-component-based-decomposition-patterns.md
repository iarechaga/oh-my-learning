---
id: hard-parts/06
subject: hard-parts
title: Component-Based Decomposition Patterns
slug: component-based-decomposition-patterns
status: drafted
mastery:
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 5
prerequisites: [hard-parts/05]
created: 2026-06-30
updated: 2026-06-30
---

# Component-Based Decomposition Patterns

## TL;DR
Component-based decomposition patterns are a repeatable path from a structured monolith to services with low migration risk. You improve internal structure first, then extract coarse domain services. The six patterns run in order, are iterative, and are controlled by fitness functions so the system stays shippable throughout.

## The idea
Teams often fail migration by starting with deployment topology: "we need microservices now." That skips a harder truth: if your internal boundaries are unclear, distributing code will only distribute confusion.

These patterns make decomposition a measured engineering loop instead of a one-time rewrite:

1. Discover and right-size components.
2. Consolidate shared domain behavior.
3. Flatten boundaries so components are true leaves.
4. Measure dependency complexity between components.
5. Group components into bounded domains.
6. Extract domains as coarse services.

The mindset is evolution, not revolution: keep shipping while structure improves.

## How it works
The six patterns below are intentionally ordered. Each pattern reduces uncertainty for the next one.

### 1) Identify and Size Components
What it does:
Finds components and measures their size by a stable metric (statements, files, or classes). It highlights outliers: god components that are too large and tiny components that are too trivial.

Why:
Balanced component size is not cosmetic. Huge components hide multiple responsibilities and create ownership bottlenecks. Tiny components increase indirection without meaningful isolation.

How:
1. Define component boundaries from package/namespace ownership.
2. Choose one size metric for trend stability.
3. Compute mean and standard deviation across components.
4. Flag components outside your allowed band.
5. Refactor outliers before service extraction.

Governing fitness function:

```
Alert when abs(component_size - mean_size) / mean_size > allowed_deviation_percent
```

Worked example:
1. Sysops Squad calculates mean size of Ticketing components at 415 statements.
2. Allowed deviation is 30 percent.
3. `ticket.assign` and `ticket.archive` fail the fitness function.
4. Team splits assignment policy logic out of `assign` and merges `archive` flow into `close`.

### 2) Gather Common Domain Components
What it does:
Finds shared domain behavior that is duplicated across multiple components and consolidates it into one explicit component.

Why:
Duplicated domain logic drifts over time, creating inconsistent behavior and unclear ownership.

How:
1. Inventory repeated business workflows (not generic utility helpers).
2. Verify they represent the same domain concept.
3. Create one shared domain component.
4. Replace duplicates with calls to that component.
5. Assign one owning team and interface contract.

Governing fitness function:

```
Alert when duplicated_domain_behavior_count > 0 for approved shared capabilities
```

Worked example:
1. Sysops Squad finds notification formatting and retry rules duplicated in assign, route, escalate, and close flows.
2. They create `ticket.notify` with one API for compose, route-channel, and retry-policy.
3. All four callers are migrated to use `ticket.notify`.
4. Notification defects drop because behavior is now consistent.

### 3) Flatten Components
What it does:
Ensures components are leaf nodes in the namespace tree. Removes active behavior that sits in parent nodes between components.

Why:
If parent nodes contain business behavior while hosting child components, boundaries blur and extraction seams become unstable.

How:
1. Draw the namespace tree for the target area.
2. Find parent nodes that both contain behavior and host child component nodes.
3. Move that parent behavior either down into real components or up into domain orchestration.
4. Enforce leaf-only component ownership in CI.

Governing fitness function:

```
Alert when namespace_node.has_domain_code == true AND namespace_node.has_component_children == true
```

Worked example (before/after tree):

Before:

```
ss.ticket
|-- shared      <- has live validation and notification logic
|   |-- assign
|   |-- route
|   `-- close
`-- reporting
```

After:

```
ss.ticket
|-- assign
|-- route
|-- close
|-- notify
|-- validate
`-- reporting
```

Result: every behavior-owning component is a leaf.

### 4) Determine Component Dependencies
What it does:
Maps afferent/efferent coupling between components and evaluates extraction difficulty from the shape of the graph.

Why:
A sparse graph usually means affordable extraction. Cycles and high fan-out predict expensive distributed complexity.

How:
1. Build a graph from static calls, events, and shared data dependencies.
2. Measure afferent coupling (incoming edges) and efferent coupling (outgoing edges).
3. Detect cycles and dependency hubs.
4. Reduce high-risk edges before extraction.

Governing fitness function:

```
Alert when component_dependency_cycle_count > 0
Alert when avg_cross_component_edges_per_component > edge_budget
```

Worked example (dependency sketch):

```
assign ---> policy ----> inventory
   |                       |
   v                       v
notify <------ route ---- reporting

legacy callback: inventory -> assign (cycle)
```

1. Sysops Squad detects a cycle via legacy callback.
2. They replace callback with an event consumed by Ticketing orchestration.
3. Cycle count becomes zero, reducing extraction risk.

### 5) Create Component Domains
What it does:
Groups related components into larger domains aligned with bounded contexts.

Why:
This creates practical service candidates. Going directly to tiny services is usually too fine-grained too early.

How:
1. Cluster components by shared business language and lifecycle.
2. Keep high cohesion inside each domain.
3. Minimize dependencies across domains.
4. Define domain-level ownership and data boundaries.

Governing fitness function:

```
cross_domain_dependency_ratio = cross_domain_edges / total_edges
Alert when cross_domain_dependency_ratio > allowed_ratio
```

Worked example:

+---------------------+--------------------------------------+
| Domain              | Components                           |
+---------------------+--------------------------------------+
| ticketing           | assign, route, notify, close         |
| operations-policy   | policy, escalation-rules             |
| asset-inventory     | inventory, maintenance, reservations |
+---------------------+--------------------------------------+

`ticketing` has strong internal cohesion and acceptable external edges, so it becomes the first extraction candidate.

### 6) Create Domain Services
What it does:
Physically extracts a component domain into a separately deployable service. Start coarse-grained at the domain level; refine granularity later.

Why:
Coarse extraction gives independent deployability without immediate service sprawl.

How:
1. Select one mature domain with clean seams.
2. Extract domain code, storage ownership, and deployment pipeline.
3. Publish explicit API/event contracts to remaining monolith parts.
4. Validate reliability, latency, and release independence.
5. Repeat domain by domain.

Governing fitness function:

```
Alert when extracted_domain_release_is_blocked_by_unrelated_domain_changes
Alert when extracted_domain_sla_breach_rate > sla_error_budget
```

Worked example:
1. Sysops Squad extracts Ticketing as one service, not four microservices.
2. Internal components remain assign, route, notify, close.
3. Monolith calls Ticketing API for ticket lifecycle operations.
4. Team gains independent deploys with limited new network boundaries.
5. Finer splits are postponed until granularity analysis (see lesson 07).

### End-to-end worked example: Sysops Squad Ticketing through all six patterns
This sequence keeps the monolith releasable.

Initial state:
1. Ticketing logic is spread across `ss.ticket.*` and `ss.ops.*`.
2. Duplicate notification logic appears in four flows.
3. `ss.ticket.shared` contains parent-level behavior.
4. Component dependency graph includes at least one cycle.

Phase A - Identify and size:
1. Measure statements per component; mean size = 415, allowed deviation = 30 percent.
2. `assign` is too large and `archive` is too small, so the team refactors outliers.

Phase B - Gather common domain components:
1. Consolidate notification behavior into `ticket.notify` and remove duplicate retry/template code.
2. Define one owner and one contract for notification behavior.

Phase C - Flatten components:
1. Remove active code from `ss.ticket.shared` and create `ticket.notify` and `ticket.validate` as leaf components.
2. Verify no parent namespace has both domain code and component children.

Before tree:

```
ss.ticket
|-- shared
|   |-- assign
|   |-- route
|   `-- close
`-- reporting
```

After tree:

```
ss.ticket
|-- assign
|-- route
|-- close
|-- notify
|-- validate
`-- reporting
```

Phase D - Determine dependencies:
1. Build graph from call traces and static imports.
2. Remove inventory callback that created cycle back to assign, then recompute coupling metrics.

Dependency sketch after cleanup:

```
assign ---> policy
   |          |
   v          v
notify      inventory
   ^
   |
route ----> reporting
```

Phase E - Create component domains:
1. Group assign/route/notify/close into Ticketing; keep policy in Operations-Policy and inventory in Asset-Inventory.
2. Track cross-domain edge ratio in CI.

Phase F - Create domain services:
1. Extract Ticketing as a separately deployable service with explicit contracts to the monolith.
2. Migrate traffic gradually with rollback and continue all fitness functions after cutover.

Why this remains low-risk: no big-bang rewrite, measurable pass/fail criteria, continuous delivery, and reversibility at each step.

Iteration loop:
```
Measure -> Refactor -> Re-measure -> Extract one domain -> Stabilize -> Repeat
```

## Pros
- Reduces migration risk through incremental, reversible change.
- Keeps teams shipping while decomposition happens.
- Uses objective metrics and fitness functions instead of debates.
- Encourages coarse-first extraction, avoiding premature service sprawl.

## Cons
- Requires discipline to maintain measurement and CI fitness checks.
- Can feel slower than a visible rewrite in early phases.
- Dependency analysis can miss runtime paths if observability is weak.
- Poorly designed fitness functions can drive wrong behavior.

## Alternatives
- **Big-bang service rewrite** - Faster visible split, but much higher delivery and reliability risk.
- **Modular monolith only** - Often best for small teams and stable workloads; no network complexity added.
- **Capability-first extraction without component cleanup** - Useful for urgency, but usually creates boundary debt.

## When to use it
Use this approach when your monolith is still structurally workable but team coordination and release coupling are becoming painful. It is ideal for safer, domain-by-domain migration without halting delivery.

## When NOT to use it
Do not use this full process for very small systems where one team can manage a modular monolith cheaply. Also do not extract services when dependencies are still highly cyclic. Keep refactoring in-monolith until flattening and dependency fitness functions are stable.

## Key takeaways / mental model
Think of these patterns as preparing clean blocks before moving them into separate buildings. If blocks are oversized, duplicated, nested, or tightly glued, moving them apart creates cracks. Safe order: size, consolidate, flatten, map dependencies, group into domains, then extract domain services. Fitness functions are the guardrails.

## Self-check questions
1. Why is pattern order important, and what can go wrong if you extract services before flattening components?
2. A component is 60 percent above mean size. What does that signal, and what should happen before extraction?
3. How do you distinguish duplicated domain behavior from a shared utility helper?
4. What does a high cross-domain dependency ratio imply about domain boundaries?
5. Why is coarse-grained domain extraction recommended before fine-grained service splitting?
6. In the Sysops Squad Ticketing example, which fitness function would most directly detect boundary regression after extraction?
## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 5
- [05-architectural-decomposition.md](05-architectural-decomposition.md)
- [07-service-granularity.md](07-service-granularity.md)
