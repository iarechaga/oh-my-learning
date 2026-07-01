---
id: hard-parts/05
subject: hard-parts
title: Architectural Decomposition
slug: architectural-decomposition
status: drafted
mastery:
seniority: senior
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 4
prerequisites: [hard-parts/02, hard-parts/04]
created: 2026-06-30
updated: 2026-06-30
---

# Architectural Decomposition

## TL;DR
Architectural decomposition is how you split a monolith into clearer boundaries without halting delivery. The first decision is not "which service first"; it is "is this codebase decomposable at all?" If yes, pick the path that matches reality: component-based decomposition for seamful systems, tactical forking for big balls of mud.

## The idea
Teams often fail decomposition because they start with target diagrams instead of current structure. They draw future services, assign owners, and only then discover the current code has no safe cut lines.

Architectural decomposition should start as diagnosis, not extraction.

You answer two questions in order:

1. Is the codebase even decomposable?
2. If yes, which approach should we use: component-based decomposition or tactical forking?

That order is the core lesson. If you skip Question 1, you can spend months trying to extract components that are structurally inseparable in their current state. If you skip Question 2, you can choose a migration style that adds unnecessary risk.

The practical mindset is:

- Measure structural signals.
- Classify the current architecture honestly.
- Choose the least risky approach that keeps the application shippable.

## How it works
Decomposition is not one migration event. It is a sequence of decision loops: assess, choose approach, execute an increment, and reassess.

### Step 1: ask the two gating questions
Question 1 asks whether clean boundaries can be found or created with acceptable effort.

- If the code has discernible module seams, decomposition by extraction is feasible.
- If dependencies are tangled everywhere and responsibilities are smeared across layers, clean extraction may be impractical.

Question 2 picks the migration style.

- Component-based decomposition when seams exist (or can be sharpened in place).
- Tactical forking when the code is an unstructured big ball of mud.

You are not optimizing for elegance first. You are optimizing for survivable progress.

### Step 2: measure decomposability with coupling and balance metrics
Use component-level metrics to avoid pure intuition.

#### Afferent coupling (Ca)
- Definition: number of incoming dependencies.
- Formula: Ca = number of components that depend on this component.
- What it tells you: high Ca means this component has many consumers and changes can ripple broadly.

#### Efferent coupling (Ce)
- Definition: number of outgoing dependencies.
- Formula: Ce = number of components this component depends on.
- What it tells you: high Ce means this component is highly dependent on others and harder to isolate.

#### Abstractness (A)
- Definition: ratio of abstract elements to all elements in a component.
- Formula: A = abstract elements / total elements.
- Range: 0..1.
- What it tells you: A near 0 is concrete-heavy; A near 1 is abstraction-heavy.

#### Instability (I)
- Definition: structural volatility based on outgoing vs incoming dependencies.
- Formula: I = Ce / (Ce + Ca).
- Range: 0..1.
- What it tells you:
  - I = 0 means maximally stable (depended upon, depends on little).
  - I = 1 means maximally unstable (depends on many, depended upon by few).

#### Distance from the main sequence (D)
- Definition: distance to the ideal balance between abstractness and instability.
- Formula: D = |A + I - 1|.
- What it tells you: D near 0 indicates healthier balance; larger D indicates imbalance and architectural tension.

### Step 3: interpret the A-I space
The main sequence is the line A + I = 1 on an Abstractness vs Instability chart.

- Components close to this line are typically better positioned.
- Components far from it often indicate design friction.

Two named risk zones matter.

#### Zone of pain
- Region: low A and low I.
- Meaning: stable and concrete.
- Why painful: many components rely on concrete code that is hard to change safely.

#### Zone of uselessness
- Region: high A and high I.
- Meaning: abstract and unstable.
- Why useless: abstractions exist, but little depends on them, so indirection gives low value.

ASCII plot:

```text
A (Abstractness)
1.0 |                                x  Zone of Uselessness
    |                             x
    |                          x
    |                       x
0.5 |--------------------x--------------------  Main sequence (A + I = 1)
    |                 x
    |              x
    |           x
    |        x
0.0 | x  Zone of Pain
    +------------------------------------------
      0.0               I (Instability)    1.0
```

This chart does not replace judgment, but it makes hidden structural problems visible.

### Step 4: classify architecture shape
Now decide whether you are dealing with a seamful monolith or a big ball of mud.

#### Signs of a big ball of mud
- High coupling in all directions (high Ce and high Ca across many areas).
- Domain rules scattered across controllers, data scripts, jobs, and utility classes.
- Frequent cycles between pseudo-modules.
- Shared helpers that quietly contain business behavior.
- Any attempted extraction forces broad, unrelated code edits.

Interpretation: decomposability by direct extraction is low.

#### Signs of discernible seams
- Components have concentrated responsibilities.
- Dependency flow is mostly directional.
- Contracts exist and are used consistently.
- Many changes remain within bounded component areas.

Interpretation: decomposability is good enough for incremental extraction.

### Step 5: choose one of two decomposition approaches

#### Approach A: component-based decomposition
This is extraction by preparation.

1. Refactor inside the monolith to sharpen component boundaries.
2. Reduce hidden coupling and make dependencies explicit.
3. Extract one component into a service.
4. Keep the remaining monolith deployable after each step.

Why this is often preferred:
- Controlled risk and easier rollback paths.
- Lower temporary duplication.
- Cleaner long-term architecture.

Cost profile:
- More upfront refactoring discipline.
- Early progress can look slow to non-technical stakeholders.

The detailed pattern loop is in [06-component-based-decomposition-patterns.md](06-component-based-decomposition-patterns.md).

#### Approach B: tactical forking
This is decomposition by subtraction.

1. Clone the full monolith once per target service.
2. In each clone, delete everything not needed for that service.
3. Keep deleting until each clone converges to a focused service.
4. Stabilize interfaces and clean duplication over time.

Why teams use it:
- Easy to start when code is deeply tangled.
- Deleting from a tangle is often easier than surgical extraction.
- Can create momentum when in-place refactoring is blocked.

Cost profile:
- Significant short-term duplication.
- Messier intermediate state.
- Requires a later consolidation phase to avoid permanent entropy.

### Worked example 1: compute I and D with real numbers
Sysops Squad evaluates a component named TicketRules.

Given:
- Ce = 2
- Ca = 8
- A = 0.3

Compute Instability I:

1. I = Ce / (Ce + Ca)
2. I = 2 / (2 + 8)
3. I = 2 / 10
4. I = 0.2

Compute Distance D:

1. D = |A + I - 1|
2. D = |0.3 + 0.2 - 1|
3. D = |-0.5|
4. D = 0.5

Interpretation:
- I = 0.2 means relatively stable.
- A = 0.3 means concrete-heavy.
- D = 0.5 is far from main sequence, so this component is imbalanced.

Practical call: treat it as near the zone of pain and decouple before extraction.

### Worked example 2: Sysops Squad scenario with usable seams
Scenario A: a reasonably structured incident platform.

Observed facts:
1. Packages are clear: alerts, escalation, notification, billing.
2. Some cycles exist, but dependency flow is mostly directional.
3. Multiple components sit near D <= 0.2.
4. Most feature work stays inside a bounded component.

Decision:
1. Decomposable? Yes.
2. Approach? Component-based decomposition.

Execution:
1. Harden notification component boundaries in-place.
2. Extract notification service.
3. Route monolith calls via explicit contract.
4. Repeat for next component.

Rationale: lower risk, less duplication, cleaner long-term architecture.

### Worked example 3: Sysops Squad scenario with inherited tangle
Scenario B: inherited 12-year-old monolith.

Observed facts:
1. Business rules appear in controllers, SQL scripts, cron jobs, and utility packages.
2. Global state is common.
3. Circular dependencies are widespread.
4. Coupling is high in both directions across most areas.
5. Extraction attempts break unrelated features.

Decision:
1. Decomposable by clean extraction now? Not safely.
2. Approach? Tactical forking.

Execution:
1. Fork monolith for Service A (incident intake).
2. Delete unrelated billing/reporting/admin paths.
3. Stabilize and deploy Service A.
4. Repeat for Service B and Service C.
5. Schedule deduplication and shared-contract cleanup after services stabilize.

Rationale: subtraction is safer than precision surgery in a dense tangle.

### ASCII comparison table

```text
+------------------------+--------------------------------------+--------------------------------------+
| Dimension              | Component-based decomposition        | Tactical forking                     |
+------------------------+--------------------------------------+--------------------------------------+
| Starting point         | Monolith with visible seams          | Big ball of mud with weak seams      |
| Effort profile         | Refactor-first, then extract         | Delete-first, then stabilize         |
| Risk                   | Lower and more controlled            | Higher integration/duplication risk  |
| Code duplication       | Low to moderate                      | High in early and mid phases         |
| End-state cleanliness  | Usually cleaner                      | Messy first, clean later if managed  |
| When to choose         | Structure exists and can be hardened | Extraction is unsafe or impractical  |
+------------------------+--------------------------------------+--------------------------------------+
```

## Pros
- Prevents architecture programs from running on wishful thinking.
- Gives objective language for discussing migration readiness.
- Improves approach selection by linking structure to risk.
- Supports incremental delivery rather than big-bang rewrites.
- Helps teams explain trade-offs to technical and non-technical stakeholders.

## Cons
- Metrics can be gamed or over-interpreted.
- Requires clear component boundaries to measure consistently.
- Tactical forking creates heavy temporary duplication.
- Component-based decomposition can feel slow initially.
- Either path requires disciplined ownership to complete cleanup.

## Alternatives
The primary decision is component-based decomposition vs tactical forking, but two contextual alternatives matter.

1. Component-based decomposition
- Choose when seams exist.
- Refactor in place, then extract.
- Optimizes for controlled risk and cleanliness.

2. Tactical forking
- Choose when seams are missing and extraction is brittle.
- Clone and delete to form service boundaries by subtraction.
- Optimizes for fast start in tangled systems.

3. Do nothing (stay monolithic)
- Valid only when current delivery and maintainability are acceptable.
- Avoids migration cost now but preserves long-term coupling debt.

4. Strangler-fig incremental replacement
- Build new capabilities outside the monolith and route traffic gradually.
- Can complement either approach above.
- Useful when edge-by-edge replacement is safer than immediate core decomposition.

## When to use it
Use architectural decomposition when team scale, delivery cadence, or domain complexity outgrows a tightly coupled monolith. Typical triggers are high cross-team merge friction, long regression cycles, inability to release capabilities independently, and persistent cognitive overload from broad coupling.

Use the two-question gate whenever you are planning modernization, domain ownership redesign, or service extraction strategy. It is especially useful when leadership pressure is high and execution risk must be made explicit.

## When NOT to use it
Do not decompose because of trend pressure alone. If the monolith is stable, small-team friendly, and meeting business goals, decomposition can add operational burden without proportional value.

Also do not pick an approach before measurement. Starting extraction or forking without coupling analysis often leads to a hybrid mess: duplicated code, unclear ownership, and little delivery improvement.

## Key takeaways / mental model
Treat decomposition like surgical triage.

First assess whether precision surgery is possible (component-based decomposition) or whether emergency stabilization by subtraction is safer (tactical forking). Ca, Ce, A, I, and D are your vital signs.

The best approach is not the most fashionable one. It is the one that moves architecture forward while keeping the system shippable.

## Self-check questions
1. Why is "is this codebase decomposable" the first question, not "which service should we extract first"?
2. A component has Ce = 6 and Ca = 2. Compute I and explain what it implies about stability.
3. What does D = |A + I - 1| tell you that I alone does not?
4. Explain the zone of pain and zone of uselessness using A and I values.
5. Why can tactical forking be the better engineering choice in a big ball of mud?
6. How can strangler-fig replacement complement either decomposition approach?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 4
- [02-architecture-quantum-static-coupling.md](02-architecture-quantum-static-coupling.md)
- [04-architectural-modularity.md](04-architectural-modularity.md)
- [06-component-based-decomposition-patterns.md](06-component-based-decomposition-patterns.md)
