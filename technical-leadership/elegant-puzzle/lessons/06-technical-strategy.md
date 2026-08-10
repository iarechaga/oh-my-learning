---
id: elegant-puzzle/06
subject: elegant-puzzle
title: Technical strategy as a management instrument
slug: technical-strategy
status: drafted
mastery:
seniority: staff
source: An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Working with Technical Strategy" and "Writing an Engineering Strategy"
prerequisites: [elegant-puzzle/01]
created: 2026-08-10
updated: 2026-08-10
---

# Technical strategy as a management instrument

## TL;DR
A technical strategy is a written, specific set of choices about how the organization will solve a class of recurring problem -- it exists to make hard trade-offs once, explicitly, so individual teams don't each re-litigate the same decision under time pressure; a strategy that doesn't rule anything out (that everyone can agree with) isn't a strategy, it's a mission statement.

## The idea
Engineering orgs face the same category of decision repeatedly: which database to default to, how to handle service-to-service auth, how aggressively to pursue microservices versus a monolith, how to balance new features against tech debt paydown. Without an explicit strategy, each team re-decides these independently, usually under deadline pressure, which produces inconsistent answers across the org (one team picks Postgres, another picks Mongo, for no principled reason) and repeated, wasted debate (the same architecture argument happens in every team's design review). A written strategy is a management tool for amortizing that decision cost across the whole org: pay the cost of thinking hard once, in a document, so individual teams can move fast later without re-deriving the reasoning from scratch.

Larson's key insight is that a real strategy must have teeth -- it has to actually foreclose some options, because a document that endorses every reasonable choice ("we value quality and speed and innovation") gives teams no more guidance than having no strategy at all, while costing real effort to produce and looking, from the outside, like it did something.

## How it works

### Strategy has three parts: diagnosis, policy, action
Borrowing from Richard Rumelt's general strategy framing (which Larson draws on): a real strategy names (1) the specific problem or diagnosis ("our service-to-service calls have no consistent auth, leading to N incidents last quarter"), (2) a guiding policy that resolves it ("all internal services authenticate via mTLS through the shared service mesh; no service may implement its own auth"), and (3) concrete actions that follow from the policy ("Platform team ships the mesh by Q2; all teams must migrate by Q3; no new service may launch without it"). A document that only states values or aspirations without a specific diagnosis and a policy that rules something out is not yet a strategy.

**Worked example -- a bad strategy vs. a real one.**
- *Bad:* "We believe in building reliable, scalable, maintainable systems, and we encourage teams to choose the right tool for the job." (Rules nothing out; every team already agreed with this before the document existed.)
- *Real:* "New services default to our internal Postgres-as-a-service platform. Teams may request an exception only with documented evidence that Postgres cannot meet a specific, named requirement (e.g., a graph-native query pattern), reviewed by the architecture group. This exists because we spent 40% of our infra team's Q1 on maintaining five different database technologies with overlapping use cases." The second version names the actual problem, states a policy that a team could genuinely disagree with and be overruled on, and gives a concrete escalation path for the real exceptions.

### Strategy is written, not implied
An unwritten "strategy" that lives only in a leader's head isn't actually usable by the org -- every team has to independently guess at it, get it wrong sometimes, and get corrected after the fact, which is strictly worse than reading a document up front. Writing it down also forces the leader to notice the gaps and internal contradictions in their own thinking that stay invisible as long as the strategy remains a vague verbal impression.

### Distinguish strategy from vision and from a roadmap
A **vision** describes a desired future state ("every engineer can deploy independently with full confidence"). A **strategy** is the specific set of choices for getting there given today's constraints. A **roadmap** is the sequenced list of concrete work items that implement the strategy. Conflating them is a common failure: a document that's all vision gives no guidance on trade-offs; a document that's all roadmap (a list of projects) gives no reasoning for why those projects and not others, so it can't help anyone reason about a case the roadmap didn't anticipate.

### Strategy needs an explicit owner and a re-evaluation trigger
Because a strategy forecloses options, someone has to be accountable for defending it when teams push back (which they will, precisely because a real strategy rules out what some team wanted to do), and someone has to own noticing when the diagnosis that produced the strategy is no longer true, at which point the strategy needs to be explicitly revisited rather than silently ignored by whichever team finds it inconvenient.

## Pros
- Prevents the same expensive architectural debate from being re-fought independently on every team.
- Makes trade-offs and their reasoning visible and challengeable, instead of leaving them as an unstated assumption only the original author remembers.
- Gives new hires and new teams a fast way to understand "how we think here" without needing to sit in on months of design reviews.

## Cons
- Writing a real strategy (one with teeth) is politically harder than writing a vision statement, because it means telling some teams "no" in writing, which creates visible, attributable conflict that vague documents avoid.
- A strategy can ossify: if it's not revisited, it becomes a rule followed out of habit long after the diagnosis that justified it has changed (a special case of the "organizations are the way they are for a reason" fossil problem in `elegant-puzzle/02`).
- Strategy work competes directly with shipping features for a leader's time, and its payoff is diffuse and delayed, making it easy to deprioritize under quarterly pressure even though the cost of not having one compounds.

## Alternatives
- **Ad hoc, per-team technical decisions** -- no central strategy; fastest for any single team in isolation, but produces the inconsistency and repeated-debate costs described above at the org level.
- **Architecture Decision Records (ADRs) without an overarching strategy** -- document individual decisions as they're made, but without a unifying diagnosis/policy connecting them; better than nothing, but doesn't help a team facing a *new* decision the ADRs haven't covered yet, since there's no stated policy to extrapolate from.
- **Centralized architecture review board with no written strategy** -- a standing group makes case-by-case calls; ensures consistency of outcome but each team still has to petition the board for every decision instead of self-serving from a written policy, which doesn't scale and creates a queueing bottleneck (see `elegant-puzzle/01`'s Platform-team example).

## When to use it
Write a strategy when you notice the same class of technical decision being re-litigated across multiple teams, when inconsistent choices are creating real operational cost (multiple databases, multiple auth systems), or when scaling the org means you can no longer personally review every team's architectural choice.

## When NOT to use it
Don't write a strategy document for a one-off decision that only ever affects a single team, or before you actually understand the problem well enough to state a real diagnosis -- a premature strategy, written before the underlying problem is well understood, tends to produce exactly the toothless, everyone-agrees-with-it kind of document this lesson warns against.

## Key takeaways / mental model
Ask of any strategy document: "what would a reasonable team want to do that this document tells them not to?" If you can't answer that, it isn't a strategy yet -- go back and find the actual diagnosis and the policy that follows from it.

## Self-check questions
1. Take a "strategy" document you've seen at work (or imagine a typical one). Does it name a specific diagnosis and a policy that rules something out, or is it closer to a vision statement? How would you rewrite one sentence of it to give it teeth?
2. Explain the difference between vision, strategy, and roadmap using a concrete example from a domain you know.
3. A team pushes back on a strategy that forbids their preferred database choice. What does the strategy document need to have in place already so this conflict resolves productively instead of becoming a political fight?
4. Describe a technical strategy that was probably right when written but is now a fossil (an outdated rule still being followed). What would trigger you to revisit it?

## References
- An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Working with Technical Strategy" and "Writing an Engineering Strategy", Part III.
