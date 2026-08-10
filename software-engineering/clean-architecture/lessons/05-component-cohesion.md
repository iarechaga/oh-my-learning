---
id: clean-architecture/05
subject: clean-architecture
title: Component Cohesion (REP, CCP, CRP)
slug: component-cohesion
status: drafted
mastery:
seniority: senior
source: Clean Architecture (Robert C. Martin), Chapter 13
prerequisites: [clean-architecture/03]
created: 2026-08-10
updated: 2026-08-10
---

# Component Cohesion (REP, CCP, CRP)

## TL;DR
Three principles govern which classes should be grouped together into the same deployable component (a package, a library, a module boundary): the Reuse/Release Equivalence Principle (group what's released and versioned together), the Common Closure Principle (group what changes together, for the same reason — SRP applied to components), and the Common Reuse Principle (don't force consumers to depend on classes they don't actually use — ISP applied to components). The three pull in different directions, and the art of component design is balancing them deliberately.

## The idea
`clean-architecture/03`-`04` established SOLID at the class level. This lesson (and `clean-architecture/06`) scales the same underlying concerns — cohesion and coupling — up to the level of **components**: the actual units of deployment, versioning, and release (a package, a JAR, a gem, an npm module, a compiled library) that a real system is composed of. The question at this scale isn't "what should one class do" but "which classes belong together in the same deployable unit, and why."

## How it works

### REP — Reuse/Release Equivalence Principle
The granule of reuse is the granule of release: **classes and modules grouped into a component should be releasable together, as a single versioned unit, with a single changelog** — because anyone who reuses that component is implicitly relying on its entire current state being coherent and versioned as a whole, not a loose, independently-drifting bag of files that happen to be co-located.

**Practical implication.** If component `Reporting` contains both PDF-generation logic and unrelated tax-calculation logic, and a consumer only wants the tax-calculation piece, they're nonetheless forced to depend on, track, and upgrade the *entire* component's version — including changes to PDF generation they never asked for and don't care about. REP argues these should have been separate, independently-releasable components in the first place, precisely because they don't share a genuine "released together" relationship — this consumer only reuses part of what's bundled.

### CCP — Common Closure Principle (SRP for components)
Gather into a component those classes that change for the *same reasons*, at the *same times* — and separate into different components those that change for different reasons. This is directly SRP's "one actor" test (`clean-architecture/03`), scaled up: instead of asking "does this class serve one actor," ask **"do these classes, together, tend to need modification for the same underlying business or technical reason?"**

**Worked example.** If a specific regulatory change (say, a new tax jurisdiction rule) requires touching a `TaxCalculator`, a `TaxRateLookup`, and a `TaxReportFormatter` class together, every time that kind of change happens, CCP argues these three classes belong in the *same* component — because they're going to be modified, tested, and released together anyway, and keeping them in one component means that regulatory change touches exactly one component's version, not three separately-versioned ones that all happen to need a coordinated release simultaneously (which is more error-prone and harder to coordinate than releasing one component once).

### CRP — Common Reuse Principle (ISP for components)
Don't force a component's consumers to depend on classes they don't actually use. If component `Utils` bundles a `StringHelper` class that many consumers use, alongside a rarely-used `ImageProcessor` class that has heavy, volatile dependencies of its own (a specific image-processing library), every consumer of `StringHelper` is forced to also depend on (and be affected by version changes to, and forced to pull in the dependencies of) `ImageProcessor` — even if they never call it. CRP argues these should be separated into distinct components, precisely mirroring `clean-architecture/04`'s ISP concern, now applied to whole components' worth of classes rather than individual interface methods.

### The tension between the three — Martin's "component cohesion tension diagram"
These three principles pull in genuinely opposite directions, and Martin is explicit that no static, universal balance is correct — the right trade-off shifts over a project's life:
- **REP and CCP** push toward *larger* components (bundle more together for coherent, coordinated release and shared-reason-for-change).
- **CRP** pushes toward *smaller* components (split apart anything a consumer might not need, to avoid forcing unnecessary dependencies).

Overweighting REP/CCP (components too large) makes consumers depend on far more than they need — a CRP violation, with unnecessary coupling to unrelated volatility. Overweighting CRP (components too small, split for every possible independent-reuse scenario) makes coordinated changes across many tiny components a coordination nightmare — a CCP violation, since a single business reason for change now requires touching many separately-versioned components.

**The practical resolution Martin offers**: early in a project's life, lean toward CCP (favor developer productivity and ease of coordinated change, since reuse patterns aren't yet well understood) — then, as real, evidenced reuse patterns emerge (a specific subset of classes is genuinely reused independently by multiple consumers), split toward CRP where that evidence justifies it. This mirrors `refactoring/02`'s Rule of Three directly: don't split preemptively based on imagined future reuse, split once real, evidenced reuse patterns demand it.

## Pros
- REP prevents forcing consumers into implicit dependence on a component's entire, potentially-unrelated contents by making "released together" an explicit, deliberate grouping decision.
- CCP minimizes the coordination cost of a single business/technical change by keeping everything that change touches within one component's version and release.
- CRP minimizes unnecessary coupling to volatility a consumer doesn't actually care about, directly limiting the blast radius of unrelated changes.

## Cons
- The three principles genuinely conflict, and there's no formula that resolves the tension universally — every component-boundary decision requires judgment about which principle matters more for that specific case, at that specific point in the project's life.
- Component boundaries, once established and consumed by other teams/systems, are expensive to change later (unlike a purely internal class boundary) — getting the initial CCP/CRP balance wrong has a higher cost to correct than a wrong class-level decision.
- Applying CRP proactively, before real reuse evidence exists, risks the same premature-splitting cost `pragmatic-programmer/05` and `refactoring/02` warn against at the class level, now at the more expensive component level.

## Alternatives
- **Team/ownership-based component boundaries** (echoing Conway's Law, see `architecture/building-microservices`) — organize components around team ownership rather than purely technical cohesion/coupling criteria, a common pragmatic real-world constraint layered on top of (or sometimes overriding) the pure REP/CCP/CRP analysis.
- **Monorepo with looser internal module boundaries** — defers some of the REP/CCP/CRP tension by not enforcing strict, separately-versioned component boundaries at all, trading some of their benefits for reduced cross-component coordination overhead.
- **Domain-driven bounded contexts** (see `domain-modeling/ddd-evans`) — a complementary, business-meaning-driven way to decide component/module boundaries, often aligning naturally with CCP's "changes together" criterion since a bounded context typically represents one coherent area of business change.

## When to use it
Apply CCP-leaning component grouping early in a project, when reuse patterns are still unknown, prioritizing ease of coordinated change. Apply CRP-driven splitting once specific evidence shows a subset of a component is genuinely, independently reused by consumers who don't need the rest.

## When NOT to use it
Don't split components preemptively based on imagined future independent-reuse scenarios with no current evidence — that's the component-level version of premature, speculative abstraction. Don't let REP/CCP's "bundle related things" instinct produce a single, enormous, low-CRP component that forces every consumer into unnecessary, unrelated dependencies just because everything happens to change at similar times for unrelated reasons.

## Key takeaways / mental model
For any component boundary decision, ask three questions: "would these classes be released and versioned together sensibly (REP)?", "do they tend to change together, for the same underlying reason (CCP)?", and "does every consumer of this component actually need everything in it (CRP)?" When the answers pull in different directions, lean toward CCP early in a project's life and toward CRP once real reuse evidence justifies splitting.

## Self-check questions
1. Using the tax-calculation example, explain why CCP argues for grouping `TaxCalculator`, `TaxRateLookup`, and `TaxReportFormatter` together, and what coordination cost that grouping avoids.
2. Describe a real or hypothetical component that violates CRP by forcing consumers to depend on unrelated, volatile classes they don't use. How would you split it?
3. Why does Martin recommend leaning toward CCP early in a project and toward CRP later, rather than picking one balance and sticking with it throughout the project's life?
4. Give an example of a component boundary that was split too early, before real reuse evidence justified it, and describe the coordination cost that premature split created.

## References
- Clean Architecture: A Craftsman's Guide to Software Structure and Design (Robert C. Martin), Chapter 13: "Component Cohesion".
