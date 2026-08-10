---
id: clean-architecture/06
subject: clean-architecture
title: Component Coupling (ADP, SDP, SAP)
slug: component-coupling
status: drafted
mastery:
seniority: senior
source: Clean Architecture (Robert C. Martin), Chapter 14
prerequisites: [clean-architecture/05]
created: 2026-08-10
updated: 2026-08-10
---

# Component Coupling (ADP, SDP, SAP)

## TL;DR
The Acyclic Dependencies Principle forbids cycles in the component dependency graph — a cycle makes every component in the loop effectively one giant, un-independently-releasable unit, defeating the purpose of having components at all. The Stable Dependencies Principle says depend in the direction of stability (volatile components should depend on stable ones, never the reverse). The Stable Abstractions Principle says a component's stability should correlate with its abstractness — the most stable components should also be the most abstract, so they're stable *because* they're easy to extend without modifying, not merely because nobody dares touch them.

## The idea
`clean-architecture/05` addressed which classes belong in the same component; this lesson addresses how components should relate to *each other* — specifically, the shape and direction of the dependency graph between components, which turns out to matter enormously for how independently different parts of a system can actually be built, tested, and released.

## How it works

### ADP — Acyclic Dependencies Principle
The dependency graph between components must have no cycles. If component `A` depends on `B`, `B` depends on `C`, and `C` depends back on `A`, these three components are no longer independently releasable — a change to any one of them potentially requires rebuilding and re-verifying all three together, because none of them can be said to have a stable, independently-testable version relative to the others. Cycles effectively **merge multiple "components" into one giant component in practice**, even though they're nominally packaged separately — undermining REP (`clean-architecture/05`), since you can no longer meaningfully release any one of them on its own.

**Breaking a cycle — the Dependency Inversion trick, applied at the component level.** Cycles are almost always broken using the exact same mechanism as `clean-architecture/04`'s DIP: if `A` depends on a concrete class in `C`, and `C` depends back on `A`, extract an interface (owned by `A` or by a new, separate component) that `C` implements — inverting `C`'s dependency so it points toward the interface (owned by `A`'s side) rather than `A` depending directly on `C`'s concrete implementation. This is DIP's exact mechanism, now applied specifically to untangle a component-level cycle rather than a single class-level dependency.

### SDP — Stable Dependencies Principle
Depend in the direction of stability: a component that's hard to change (many other components depend on it, so changing it has wide-reaching consequences) should never depend on a component that's easy to change (few or no dependents, so it changes freely) — because doing so would make the *stable* component indirectly fragile, inheriting instability from something volatile it depends on, defeating the entire purpose of that component being stable in the first place.

**Measuring stability, concretely.** Martin gives a computable metric: a component's stability is a function of its **fan-in** (how many other components depend on it — incoming dependencies) versus **fan-out** (how many other components it depends on — outgoing dependencies). High fan-in, low fan-out = stable (many things depend on it, it depends on little, so it's hard to justify changing and has few reasons to need to). Low fan-in, high fan-out = volatile (few or no dependents, depends on many things, so it's easy and low-risk to change).

**Worked example.** A core `OrderEntity` component, depended on by a dozen other components across the system (high fan-in), that itself depends on nothing else in the system (low fan-out), is highly stable by this metric — and SDP says it *should* stay that way: nothing about `OrderEntity` should ever depend on a volatile, frequently-changing component like a specific `EmailTemplateRenderer` that only one feature currently uses. If it did, every one of `OrderEntity`'s dozen dependents would be indirectly exposed to `EmailTemplateRenderer`'s volatility — a violation that would ripple far beyond what the actual coupling seems to warrant.

### SAP — Stable Abstractions Principle
A component's abstractness should increase with its stability. This connects SDP's stability metric to OCP (`clean-architecture/03`): **a component should be stable specifically because it's abstract and easy to extend without modification — not merely because it's stable in the sense that everyone's afraid to touch it.** A highly stable, highly *concrete* component is a genuine architectural problem: it's hard to change (many dependents) but also hard to *extend* without modification (it's concrete, not built around abstractions/interfaces), which is precisely the combination that produces the "it takes forever to make a change here" complaint from `legacy-code/06`, at the component-architecture scale.

**The combined metric Martin proposes.** Plotting components on a stability-versus-abstractness graph, well-designed components should cluster along what he calls the "main sequence" — a diagonal line where stability and abstractness track together. A component in the "zone of pain" (highly stable, but concrete — hard to change, hard to extend, and something many things depend on) is a genuine architectural liability. A component in the "zone of uselessness" (highly abstract, but volatile — an interface nobody actually depends on, changing constantly for no reason) represents wasted abstraction effort with no payoff.

## Pros
- ADP prevents component cycles from silently merging supposedly-independent components into one un-independently-releasable unit.
- SDP's fan-in/fan-out metric gives a concrete, computable way to check whether a proposed dependency direction is architecturally sound, rather than relying purely on intuition.
- SAP connects stability directly to OCP, giving a principled reason *why* the most depended-upon parts of a system should be built around abstractions rather than concrete details — directly motivating the dependency rule (`clean-architecture/08`).

## Cons
- Detecting and untangling a genuine component cycle, once it exists in a real, large system, can require a nontrivial DIP-based refactoring effort, similar in scale to `refactoring/11`'s big-refactoring techniques.
- Fan-in/fan-out metrics, while computable, don't capture every relevant dimension of "how risky is it to depend on this" (e.g., a component with low fan-in might still be extremely business-critical and risky to depend on carelessly, independent of the metric).
- Deliberately engineering a component toward the "main sequence" (matching abstractness to stability) requires ongoing architectural discipline and periodic review — components can drift away from this balance gradually, as dependents accumulate faster than the component's abstractness is deliberately increased to match.

## Alternatives
- **Layered architecture with enforced one-directional dependencies** (see `architecture/fundamentals`) — a coarser-grained, more prescriptive way to prevent cycles by construction (each layer may only depend on the layer below), rather than relying on continuous fan-in/fan-out measurement and case-by-case judgment.
- **Automated architectural fitness functions** (see `architecture/evolutionary-architectures`) — tooling that continuously checks for dependency cycles and enforces stability/abstractness rules automatically in CI, rather than relying purely on manual review and periodic architectural assessment.
- **Microservices with fully independent deployability** (see `architecture/building-microservices`) — sidesteps ADP's cycle concern at the level of shared libraries by making each service independently deployable with its own data, though inter-service dependency cycles remain a distinct, analogous risk at a different granularity.

## When to use it
Apply ADP whenever adding a new dependency between components — check whether it would create a cycle, and if so, break it via dependency inversion before proceeding. Apply SDP when deciding which direction a new dependency should point, using fan-in/fan-out as a concrete check. Apply SAP when a component's fan-in grows significantly, as a prompt to deliberately increase its abstractness to match, before it drifts into the "zone of pain."

## When NOT to use it
Don't obsess over precise fan-in/fan-out numbers for small systems where the dependency graph is simple enough to reason about directly without formal metrics. Don't force every component toward maximal abstractness regardless of its actual stability — a genuinely volatile, low-fan-in component has no need for SAP's abstractness discipline, since instability there is expected and fine.

## Key takeaways / mental model
For any dependency between two components, check three things: does adding it create a cycle (ADP)? does it point from something volatile toward something stable, never the reverse (SDP)? and if the depended-upon component is highly stable, is it also appropriately abstract, so its stability comes from being extensible rather than merely untouchable (SAP)?

## Self-check questions
1. Explain, using a concrete example, why a cycle among three components effectively merges them into one un-independently-releasable unit, even though they're packaged separately.
2. Compute (informally) the fan-in and fan-out for a component you're familiar with, and assess whether its actual dependencies respect SDP's "depend toward stability" rule.
3. Describe a component in the "zone of pain" (stable but concrete) from your own experience, and explain what increasing its abstractness would look like.
4. Walk through breaking a component-level dependency cycle using the DIP-based technique described in this lesson.

## References
- Clean Architecture: A Craftsman's Guide to Software Structure and Design (Robert C. Martin), Chapter 14: "Component Coupling".
