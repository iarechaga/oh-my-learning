---
id: learning-ddd/13
subject: learning-ddd
title: Evolutionary design and refactoring of contexts
slug: evolutionary-design-and-refactoring-of-contexts
status: drafted
mastery:
seniority: staff
source: Learning Domain-Driven Design (Vlad Khononov), Part III, Chapter 11 - "Evolving Boundaries" and Chapter 12 - "Design Heuristics"
prerequisites: [learning-ddd/02, learning-ddd/04, learning-ddd/12]
created: 2026-08-10
updated: 2026-08-10
---

# Evolutionary design and refactoring of contexts

## TL;DR
Bounded contexts, subdomain classifications, and architectural choices are never final - they should be treated as hypotheses, tested against real usage and organizational change, and deliberately revisited (split, merged, reclassified, re-architected) as the business and the team's understanding of it evolve. Khononov frames this as a core DDD discipline in its own right, not an admission of earlier failure: getting a boundary "wrong" at first is expected, and the goal is cheap, safe evolution, not perfect upfront prediction.

## The idea
Every design decision covered so far in this subject - subdomain classification (`learning-ddd/02`), bounded-context boundaries (`learning-ddd/03`), relationship patterns (`learning-ddd/04`), and architectural style (`learning-ddd/12`) - was made with the team's *current* understanding of the business, at a specific point in time. That understanding is always incomplete and always changing: a subdomain classified as "supporting" today might become the company's next core bet after a strategic pivot; a bounded context drawn too broadly early on (because the team hadn't yet seen the vocabulary diverge) becomes obviously wrong once real usage patterns and team growth expose the divergence. Evolutionary design treats this not as a failure to plan correctly the first time, but as the expected, healthy lifecycle of a domain model - and builds in the practices that make revisiting cheap rather than catastrophic.

This connects back to `learning-ddd/01`'s founding claim in a specific way: since design investment should track *current* business complexity and differentiation, and both of those genuinely change over time, the design itself must be able to change with them. A system that can't evolve its boundaries is a system that will eventually mismatch the business it serves, regardless of how well those boundaries were drawn on day one.

## How it works

### Starting broad, splitting later (context boundary evolution)
Khononov's practical guidance for a new system: start with fewer, coarser bounded contexts than you eventually expect to need, and split them as real evidence of divergence accumulates - rather than guessing at fine-grained boundaries upfront based on incomplete domain understanding. A boundary drawn too fine, too early, based on speculation rather than evidence, creates real coordination overhead (`learning-ddd/04`, `learning-ddd/11`) for a distinction that might not have actually mattered.

**Worked example - SaaS billing.** Early on, a single "Billing" bounded context handles both subscription management and usage metering, because the team doesn't yet have enough real usage data to know whether these two concerns will diverge in vocabulary or rate of change. Eighteen months later, usage metering has grown into a genuinely complex, fast-iterating core subdomain (new pricing models being tested monthly) while subscription management has stabilized into a slower-changing supporting concern - and the vocabulary has visibly diverged (`learning-ddd/05`'s signal from `learning-ddd/03`: "Plan" in Subscription Management no longer means the same thing engineers reach for when discussing rate-calculation logic). This is exactly the evidence that justifies splitting into two bounded contexts now, where speculating about the split at project kickoff, before this divergence was observable, would likely have guessed wrong.

### Merging contexts that turned out not to need separation
The reverse move is equally legitimate: two bounded contexts drawn separately, based on an early guess, that turn out in practice to share vocabulary, change together constantly, and never developed the independent evolution the split was meant to enable, are strong candidates for merging back together - the ongoing cross-context coordination cost (`learning-ddd/11`'s integration overhead) isn't buying anything.

**Worked example - logistics.** Route Planning and Fleet Maintenance were split into separate bounded contexts at the outset, following a template from a previous project. In practice, the same small team owns both, every feature touches both, and the "vehicle capacity" concept turns out to be identical in both contexts' vocabulary with no real divergence ever emerging. Recognizing this, the team merges them back into one "Fleet Operations" bounded context, eliminating the integration overhead (an API layer, event contracts) that was maintained for a distinction that day-to-day work never actually needed.

### Reclassifying subdomains as strategy shifts
`learning-ddd/02` already flagged that classification is a snapshot, not permanent. Evolutionary design makes the *mechanics* of acting on a reclassification explicit: once a subdomain moves from supporting to core (or vice versa), its business-logic pattern (`learning-ddd/07`) and architecture (`learning-ddd/12`) should be deliberately migrated to match the new classification - not left in whatever state matched the old one.

**Worked example - e-commerce.** A "Recommendations" subdomain, originally generic (bought as an off-the-shelf plugin), becomes core after the company decides personalized merchandising is its next competitive bet. The evolutionary-design response is a deliberate migration: replace the off-the-shelf plugin with an in-house Domain Model (`learning-ddd/07`) built around the company's own product and behavioral data, wrapped in Ports & Adapters (`learning-ddd/12`) so the team can iterate on recommendation logic rapidly and safely - a substantial investment that would have been wasted a year earlier, when Recommendations was still correctly classified as generic.

### The Strangler Fig pattern for safe migration
When a bounded context (or its underlying architecture) needs to change substantially - splitting, merging, or migrating from one business-logic pattern to another - doing it as one large, risky rewrite is rarely the safest path. The Strangler Fig approach routes traffic/calls incrementally from the old implementation to the new one, feature by feature or use case by use case, so both can coexist during the transition and the team can validate each piece before fully cutting over, rather than betting the whole migration on one big-bang release.

**Worked example - healthcare.** Migrating Scheduling's conflict-resolution logic from a Transaction Script (`learning-ddd/07`) to a rich Domain Model (as the subdomain's complexity and stakes grew, per `learning-ddd/02`'s reclassification) is done use-case by use-case: "cancel appointment" is migrated and validated first, running in production alongside the old logic for other use cases, before "reschedule" and "resolve double-booking" follow - rather than attempting to rewrite the entire scheduling engine in one release and risking a production incident across every use case simultaneously.

### Design heuristics as ongoing diagnostic signals
Khononov catalogs recurring heuristics that signal a boundary or pattern has drifted out of alignment with reality and is due for evolutionary attention: persistent, high-friction coordination between two teams over "the same" model (a signal a bounded context is drawn too broadly for the team structure - connects to `learning-ddd/14`); a bounded context whose internal vocabulary has quietly split into two unrelated sub-vocabularies (a signal it should be split); two contexts whose APIs are called together in lockstep on almost every request (a signal they might be better merged, or at least reconsidered as a Partnership per `learning-ddd/04`); and a subdomain whose actual behavior no longer matches the complexity/differentiation profile it was classified under (the reclassification trigger above).

## Pros
- Removes the pressure to get every boundary perfectly right on the first attempt, which is an unrealistic bar given how incomplete early domain understanding always is - freeing teams to start simple and let real evidence guide refinement.
- Keeps the system's design aligned with the *current* state of the business rather than a frozen snapshot of an early, necessarily incomplete understanding.
- The Strangler Fig approach makes large structural changes (splits, merges, pattern migrations) safe and incremental rather than high-risk, all-or-nothing rewrites.
- Explicit heuristics give teams a repeatable, evidence-based way to notice drift, rather than relying on someone's vague unease that "this doesn't feel right anymore."

## Cons
- Requires ongoing discipline and time investment to actually revisit designs periodically - easy to neglect under delivery pressure, at which point drift accumulates silently until it becomes a crisis.
- Splitting or merging bounded contexts after data and code have grown around the old boundary is genuinely expensive (data migration, API contract changes, retraining team muscle memory) - evolutionary design reduces this cost relative to never revisiting, but doesn't eliminate it.
- Starting deliberately "too coarse" and splitting later can, if taken too far, become an excuse to never invest in proper boundaries at all, sliding into the Big Ball of Mud state `learning-ddd/04` warns about.
- Distinguishing genuine evidence of drift from noise (a single awkward sprint doesn't mean a boundary is wrong) requires judgment that newer teams may not yet have developed.

## Alternatives
- **Big upfront design (BUFD), fixed at project start** - lower risk of premature-optimization-driven mistakes from a rigid framework, but directly contradicts this lesson's premise: it locks in a necessarily incomplete early understanding and makes later correction expensive precisely because no evolutionary mechanism was built in.
- **Continuous, unstructured refactoring with no explicit heuristics or checkpoints** - can work for small teams with strong shared intuition, but doesn't scale to larger teams or longer-lived systems where drift needs to be named and discussed explicitly to be acted on.
- **Domain-Driven Design's "Big Ball of Mud" as a deliberate starting point**, with a planned later "extraction" once boundaries become clear - a more extreme version of "start broad, split later" sometimes advocated for very early-stage products; riskier because it defers *any* boundary discipline, not just fine-grained boundaries.

## When to use it
Build evolutionary review into a team's regular cadence (quarterly architecture reviews, or triggered by specific signals: a strategic pivot, persistent cross-team friction, or a subdomain's complexity visibly outgrowing its current classification). Use the Strangler Fig approach whenever a needed structural change is large enough that a big-bang rewrite would carry unacceptable risk.

## When NOT to use it
Don't treat every minor implementation grumble as evidence a boundary needs to change - evolutionary design responds to sustained, evidence-backed signals (the heuristics above), not to any single team's momentary friction with an otherwise sound design. Also avoid using "we can always evolve it later" as a justification for skipping the upfront analysis in `learning-ddd/02` through `learning-ddd/04` entirely - starting broad-but-deliberate is different from starting with no analysis at all.

## Key takeaways / mental model
Treat every bounded context, subdomain classification, and architectural choice as a hypothesis, not a verdict. Revisit them on a regular cadence and whenever a concrete heuristic signal appears (persistent cross-team friction, a diverging vocabulary, a subdomain outgrowing its classification), and when change is needed, prefer incremental, coexisting migration (Strangler Fig) over a risky big-bang rewrite.

## Self-check questions
1. Describe a bounded context or module you've worked on that was drawn correctly at the time but became a poor fit later. What changed - the business, the team, or the team's understanding?
2. Why does Khononov recommend starting with coarser, fewer bounded contexts and splitting later, rather than guessing at fine-grained boundaries upfront?
3. Walk through how the Strangler Fig pattern would apply to migrating one bounded context's business-logic pattern from Transaction Script to Domain Model without a risky big-bang rewrite.
4. Name two of the design heuristics from this lesson that would signal a bounded-context boundary needs to evolve, and explain what observable symptom each one produces in day-to-day team friction.

## References
- Learning Domain-Driven Design (Vlad Khononov), Part III, Chapter 11: "Evolving Boundaries" and Chapter 12: "Design Heuristics".
- Domain-Driven Design Distilled (Vaughn Vernon) - concise treatment of iterative boundary discovery, see `domain-modeling/ddd-distilled`.
