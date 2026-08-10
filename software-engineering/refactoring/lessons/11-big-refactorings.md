---
id: refactoring/11
subject: refactoring
title: Big Refactorings and Breaking Dependencies
slug: big-refactorings
status: drafted
mastery:
seniority: senior
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 5
prerequisites: [refactoring/01, refactoring/03]
created: 2026-08-10
updated: 2026-08-10
---

# Big Refactorings and Breaking Dependencies

## TL;DR
A large-scale refactoring (splitting a module, migrating an architecture, removing a deeply-entangled dependency) is not one big step done carefully — it's the same small-steps discipline from `refactoring/01`, sustained over a much longer sequence, with explicit intermediate states that are each fully working and shippable. The key skill is breaking a seemingly-monolithic large change into a long chain of small, individually safe ones, none of which requires the whole migration to be "done" before it delivers value.

## The idea
Every technique so far in this subject has operated at the scale of a single function, class, or small hierarchy. Real refactoring needs sometimes operate at a much larger scale — splitting a tangled module into two services, removing a company-wide dependency on a deprecated library, migrating a core data structure used across hundreds of call sites. The temptation at this scale is to treat it as fundamentally different from the small techniques already covered — requiring a dedicated branch, a long period of "in progress, don't touch," and a single, high-stakes merge at the end. Fowler's argument, directly connecting back to `refactoring/01`'s core discipline, is that this temptation should be resisted: **the same small-steps principle still applies, just sustained over a much longer sequence of individually complete, individually shippable increments** — the scale of the goal doesn't change the size of the safe individual step.

## How it works

### Branch by abstraction — the core technique for large, disruptive changes
When replacing a widely-used dependency or component (a legacy library, an old data access layer) with a new one, "branch by abstraction" avoids a long-lived feature branch entirely:
1. Introduce an abstraction layer (an interface) between callers and the current implementation, with the *existing* implementation behind it — this step alone changes nothing observable, and can be merged to the main branch immediately, verified by existing tests.
2. Build the *new* implementation behind the same abstraction, in parallel with the old one still active and in use — this can also be merged incrementally, since it's not yet wired in as the active implementation.
3. Switch callers over gradually — some via a feature flag, some via direct migration, verified in small batches — with the ability to roll back to the old implementation at any point if a problem surfaces, since it's still present and functional throughout the transition.
4. Once every caller has migrated and the new implementation has proven itself, remove the old implementation and the now-unnecessary abstraction layer (if it was purely transitional) entirely.

**Why this beats a long-lived feature branch.** A long-lived branch accumulates drift from the main branch the longer it lives, making the eventual merge increasingly risky and difficult the longer the migration takes — precisely the opposite of the small-steps safety property `refactoring/01` and `refactoring/03` establish. Branch by abstraction keeps every intermediate state on the main branch, individually tested, individually shippable, and never more than one small step from a known-good state — even though the *overall* migration might take weeks or months to fully complete.

### Breaking a dependency without waiting for the "ideal" decomposition
A common paralysis at this scale: waiting to start until you have a complete, confident plan for the perfect end-state architecture. Fowler's practical counter, echoing `philosophy-of-software-design/02`'s incremental-investment argument: start with the most obviously beneficial, safely-extractable piece *now*, even without a complete plan for everything else — each successfully extracted piece both delivers value on its own and teaches you more about the real shape of the remaining dependencies, informing the next step better than upfront planning alone could have.

**Worked example.** A monolithic order-processing module tangled with inventory, notification, and reporting logic, targeted for eventual decomposition into separate services (see `architecture/hard-parts`, `architecture/building-microservices` for the full architectural treatment). Rather than designing the complete target architecture before touching anything, start by extracting the most clearly-separable piece — say, notification logic, which has comparatively few, well-understood dependencies on the rest — using Extract Class/Move Function (`refactoring/06`) to pull it into its own module *within the same codebase and deployment* first, verified by tests at each step. Only once that extraction is stable and has clarified the real boundary do you consider whether it's ready to become an actual separate service — deferring the more disruptive, harder-to-reverse architectural step until you have concrete, tested evidence the boundary is real, rather than guessing at the full target architecture upfront.

### Parallel change (expand-contract) for changing a shared contract
A related technique specifically for changing a widely-depended-upon interface or data format (echoing `refactoring/09`'s Change Function Declaration migration, at a larger scale): **expand** by adding the new version alongside the old (both supported simultaneously), migrate all consumers to the new version incrementally, then **contract** by removing the old version once nothing depends on it anymore. This is the same three-phase shape as `refactoring/09`'s intermediate-step migration, scaled up to interfaces with many more consumers, often across team or even organizational boundaries, where a single, all-at-once cutover is operationally infeasible.

### Recognizing when a "big refactoring" is actually many independent small ones in disguise
A genuinely useful reframe: much of what looks like one large, scary refactoring is actually a long sequence of the *same* small, already-covered techniques from earlier lessons (Extract Function, Move Function, Extract Class, Change Function Declaration), applied repeatedly and in the right order — the "bigness" is really just the *count* of small steps needed, not a fundamentally different kind of activity requiring different tools or different levels of care per step.

## Pros
- Branch by abstraction and parallel change keep every intermediate state shippable and low-risk, even for migrations spanning weeks or months, avoiding the escalating risk of a long-lived feature branch.
- Starting with the most safely-extractable piece, rather than waiting for a complete plan, delivers incremental value and generates real evidence to inform later, harder decisions.
- Reframing a "big refactoring" as a long sequence of already-familiar small techniques makes an intimidating-sounding task concretely actionable using tools you already know.

## Cons
- Maintaining two parallel implementations (old and new) during a branch-by-abstraction or expand-contract migration has a real, ongoing cost — more code to maintain, more surface area for a bug in either version — for the duration of the transition.
- A migration lacking a clear target and success criteria can drift indefinitely, with the "old" implementation never actually fully retired, leaving the codebase permanently carrying both versions' cost with none of a completed migration's benefit.
- Large-scale dependency-breaking migrations, even done incrementally, require sustained organizational attention and priority over a potentially long period — a real coordination cost beyond what any single technique addresses.

## Alternatives
- **A dedicated, isolated rewrite** (echoing `refactoring/01`'s rewrite-vs-refactor distinction, at architectural scale) — sometimes genuinely the better choice when the existing implementation's behavior is poorly understood or poorly trusted enough that incremental, behavior-preserving migration isn't actually meaningful; see `refactoring/12` for that judgment call.
- **The Strangler Fig pattern** (see `architecture/evolutionary-architectures`) — a specifically architectural, system-level version of branch-by-abstraction, routing traffic gradually from an old system to a new one rather than migrating code within one codebase.
- **A "big bang" cutover on a dedicated maintenance window** — occasionally justified for genuinely small-blast-radius, low-consequence changes where the coordination overhead of an incremental migration exceeds the risk of a single, well-tested cutover — but generally the higher-risk choice this lesson's techniques are designed to avoid needing.

## When to use it
Use branch by abstraction or parallel change (expand-contract) for any large-scale change to a widely-depended-upon component or interface, especially when a long-lived feature branch or an all-at-once cutover would carry unacceptable risk. Start any large decomposition effort with the most safely-extractable, best-understood piece rather than waiting for a complete plan.

## When NOT to use it
Don't maintain a parallel old/new implementation indefinitely without a clear plan and forcing function to actually complete the contraction phase — that accumulates permanent double-maintenance cost with no corresponding benefit. Don't attempt an incremental migration when the existing behavior is so poorly understood or trusted that "preserve it exactly" isn't even a meaningful goal — that's a signal a more deliberate rewrite, informed by `refactoring/01`'s distinction, may be the better tool.

## Key takeaways / mental model
At any point during a large migration, ask: "if I stopped right now, is the system in a fully working, shippable state?" If yes, you're doing this safely, regardless of how much work remains. If no, break the current step down further until the answer is yes again.

## Self-check questions
1. Walk through applying branch by abstraction to replace a widely-used dependency in a hypothetical codebase, describing each of the four phases concretely.
2. Why does the book argue against waiting for a complete target-architecture plan before starting a large decomposition? What does starting with the most safely-extractable piece actually buy you?
3. Explain the risk of a long-lived feature branch for a large migration, and how branch by abstraction specifically avoids it.
4. Describe a migration you've seen (or can imagine) that stalled indefinitely with both old and new versions permanently coexisting. What would have prevented that?

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 5: "A Catalog of Refactorings" (Big Refactorings section) and supplementary material on branch by abstraction and parallel change.
- See also: `architecture/evolutionary-architectures` for the Strangler Fig pattern at architectural scale.
