---
id: staff-engineers-path/06
subject: staff-engineers-path
title: Navigating ambiguity with incremental execution plans
slug: navigating-ambiguity
status: drafted
mastery:
seniority: senior
source: The Staff Engineer's Path (Tanya Reilly), Chapter 4 - "Understanding, then Planning"
prerequisites: [staff-engineers-path/03]
created: 2026-08-10
updated: 2026-08-10
---

# Navigating ambiguity with incremental execution plans

## TL;DR
Big, ambiguous problems can't be planned end-to-end up front — the right response is to break the work into small, sequenced, checkpointed increments, each of which reduces uncertainty and produces something of value on its own, rather than betting everything on one large plan that assumes you already understand the problem correctly.

## The idea
Ambiguous problems (a vague mandate like "improve platform reliability" or "modernize the data layer") resist the planning techniques that work for well-understood ones. If you try to write a complete, detailed project plan for something genuinely ambiguous, you're forced to guess at details you can't actually know yet — and the plan becomes a work of fiction that quietly diverges from reality the moment execution starts. Worse, a big-bang plan defers all learning to the very end: you only discover your assumptions were wrong after months of investment, when it's expensive to change course.

Incremental execution inverts this: instead of planning the whole thing, you plan the *next* well-understood step, execute it, and use what you learn to plan the step after that. Each increment should be small enough to actually finish, produce something real (a working prototype, a validated assumption, a shipped partial improvement), and create a natural checkpoint to reassess before committing further.

## How it works

### From ambiguous mandate to a first concrete step
**Worked example.** A staff engineer is asked to "improve platform reliability" — a real mandate but far too vague to plan against directly. The temptation is to write a comprehensive reliability roadmap covering every service. Instead, the incremental approach:

1. **Narrow the ambiguity first, cheaply.** Spend a bounded amount of time (say, two weeks) just understanding: pull incident data for the last two quarters, interview the on-call engineers from the three most incident-prone teams. This step produces information, not a solution.
2. **Identify the smallest high-confidence next step.** The data shows that 60% of incidents trace back to one specific database's connection-pool exhaustion under load. Rather than committing to "fix reliability platform-wide," commit to "fix connection-pool exhaustion in the checkout database" — a concrete, scoped, plannable piece of the larger ambiguous goal.
3. **Execute that step and treat it as a probe, not just a fix.** Fixing it validates (or invalidates) the hypothesis that connection pooling is the dominant driver, and yields a template (a runbook, a pattern) that might generalize to the other incident-prone services.
4. **Checkpoint and replan.** After the fix ships and incidents drop, reassess: does the same pattern show up elsewhere? Was the hypothesis right? Only now plan the next increment, informed by real data from the first one — rather than a six-month roadmap built on a guess made in week one.

### Why small increments beat a big plan under ambiguity
- **Faster feedback** — each increment tests an assumption against reality quickly, instead of deferring that test to the end of a long plan.
- **Bounded downside** — if an increment reveals the hypothesis was wrong, you've lost weeks, not months, and you still have something shippable from the increment itself (the connection-pool fix was valuable on its own even if it hadn't generalized).
- **Maintains momentum and trust** — stakeholders see concrete progress every few weeks instead of silence followed by a single large deliverable at the end, which is both motivating and politically safer (see `staff-engineers-path/08` on why visible progress matters for alignment).
- **Preserves optionality** — because you haven't committed the whole budget/timeline up front, you can redirect based on what you learn, which a monolithic plan makes expensive or impossible.

### Sizing increments correctly
An increment that's too large reintroduces the big-plan problem (you're still guessing too far ahead); one that's too small produces so little information or value that the overhead of planning and checkpointing swamps the benefit. A reasonable rule of thumb: an increment should be sized so that, if your core hypothesis turns out wrong, you find out within roughly 2-4 weeks, and even if it's wrong, the increment itself was still worth doing.

## Pros
- Converts an unplannable, anxiety-inducing mandate into a sequence of concrete, executable steps — unblocking action instead of stalling in analysis.
- Surfaces wrong assumptions early and cheaply, before they're expensive to unwind.
- Produces continuous, visible progress, which sustains stakeholder confidence and your own team's morale through a long, uncertain initiative.

## Cons
- Without a periodically-revisited bigger picture, incremental execution can drift into a series of locally-reasonable steps that never add up to solving the actual ambiguous problem — "death by a thousand small, disconnected fixes."
- Constant checkpointing and replanning has real overhead; for a genuinely well-understood problem, incremental planning is slower than just planning it properly once.
- Stakeholders sometimes want a firm end-date and full scope up front (for external commitments, budget cycles); "we'll know more after the next increment" can be a hard sell to those audiences, requiring active expectation-setting.

## Alternatives
- **Big-bang / waterfall planning** — appropriate when the problem is genuinely well-understood and low-ambiguity (a well-scoped migration with a known target state); wrong tool for a genuinely ambiguous mandate, where the up-front plan would just be guessing dressed up as certainty.
- **Time-boxed spikes followed by full planning** — do a single bounded research spike, then commit to one full plan; a middle ground that reduces some ambiguity before committing, but still bets the rest of the plan on what one spike revealed, rather than continuously re-checking as you go.
- **OKR-driven quarterly planning** — set a directional objective and key results per quarter, without a detailed cross-quarter plan; similar spirit to incremental execution but operates at a coarser (quarterly) cadence rather than increment-by-increment.

## When to use it
Use incremental execution planning whenever the problem is genuinely ambiguous — you don't yet know the root cause, the right architecture, or even the full scope — and especially for open-ended mandates ("improve X," "modernize Y") handed to a staff-plus engineer without a pre-defined solution.

## When NOT to use it
Don't apply heavy incremental checkpointing to well-understood, low-ambiguity work — a known migration with a clear target state benefits more from a proper upfront plan than from artificially fragmenting it into "increments" that add process overhead without reducing any real uncertainty. Also be careful applying pure incrementalism to problems with a hard external deadline and low tolerance for a moving plan (a regulatory compliance deadline) — some upfront commitment to scope may be unavoidable even under ambiguity.

## Key takeaways / mental model
Under real ambiguity, you cannot plan your way to certainty — only execution generates the information a good plan needs. So: narrow the ambiguity cheaply, commit to the smallest high-confidence next step, ship it as something valuable in its own right, checkpoint, and replan with what you learned. Repeat. The plan is a rolling one-step-ahead artifact, not a fixed roadmap.

## Self-check questions
1. Take a vague mandate (real or hypothetical, e.g. "make onboarding faster") and identify a first concrete, plannable increment — not the whole solution, just the first step that would generate real information.
2. Why does a detailed six-month plan for a genuinely ambiguous problem tend to diverge from reality, even when written by a capable engineer?
3. How would you know an increment is sized correctly — not so big it's really just a disguised big-bang plan, not so small it produces no useful information?
4. Describe the risk of "death by a thousand small fixes" in incremental execution, and what practice prevents it.

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 4: "Understanding, then Planning".
