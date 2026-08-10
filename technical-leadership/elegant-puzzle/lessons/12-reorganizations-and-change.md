---
id: elegant-puzzle/12
subject: elegant-puzzle
title: Reorganizations and change management without chaos
slug: reorganizations-and-change
status: drafted
mastery:
seniority: principal
source: An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Reorganizations" and "Navigating Change"
prerequisites: [elegant-puzzle/04, elegant-puzzle/05]
created: 2026-08-10
updated: 2026-08-10
---

# Reorganizations and change management without chaos

## TL;DR
A reorg is a deliberate, costly intervention that should be justified by a clear structural problem it solves, executed with a tight, well-communicated timeline, and evaluated afterward against that original problem -- not a reflexive tool leadership reaches for whenever something feels wrong, because reorg fatigue is itself one of the most damaging things you can do to an organization's trust and productivity.

## The idea
Reorganizations are expensive: they cost weeks to months of reduced velocity while new teams build working norms and relationships (`elegant-puzzle/05`), and they cost trust -- employees who've been through several reorgs with unclear rationale become cynical about the next one, disengage from their current team ("why get attached, it'll change again"), and are more likely to leave. That cost means a reorg needs to be justified by a genuine structural problem -- a scope, span, or Conway's-Law mismatch (`elegant-puzzle/03`, `elegant-puzzle/04`) that a smaller, more targeted intervention (a single team split or merge, per `elegant-puzzle/05`) can't fix -- not used as a generic response to a vague sense that "something's not working," which usually has a much cheaper, more targeted fix if you actually diagnose it (`elegant-puzzle/02`).

## How it works

### Name the specific problem before designing the new structure
Every reorg should be traceable to a specific, statable structural problem: "Team A and Team B's boundary doesn't match the technical seam between their systems, causing constant cross-team coordination on every feature" or "the current functional structure means no team owns end-to-end delivery of any customer-facing feature, so nothing ships without a four-team hand-off." If leadership can't state the specific problem the new structure solves, that's a strong signal the reorg is being done for other reasons (imitating another company's structure, a new leader wanting to "leave their mark," reacting to one bad quarter) rather than a genuine structural fix -- and those reorgs tend to produce a new, different set of problems without actually fixing anything, at real cost.

### Design against the specific problem, then check for new problems it introduces
Once the problem is named, design the new structure to solve it directly, then explicitly ask what new coordination costs or scope mismatches the new structure introduces -- every org shape trades one cost for another (`elegant-puzzle/04`), so the right question isn't "is this structure perfect" but "does this trade a smaller cost for a bigger one we're currently paying." **Worked example.** A company reorganizes from functional to product teams to fix slow end-to-end delivery. Before executing, leadership explicitly asks: what shared infrastructure will now lack a clear owner? They identify auth and billing as genuinely shared concerns, and proactively carve out a platform team for those, rather than discovering the gap six months later after five product teams have each built a divergent version.

### Timeline: fast and clearly bounded, not a slow bleed
A reorg that's announced but takes months to actually implement creates a prolonged limbo where nobody knows their real team, priorities, or manager -- productivity and morale suffer for the entire ambiguous period, often longer than the reorg itself would have cost if executed quickly. Larson's guidance: once the decision is made, execute on a short, clearly communicated timeline (days to a couple of weeks for the structural change itself, with a separate, expected settling-in period afterward), rather than a long, ambiguous transition.

### Communication: explain the why, not just the what
People tolerate structural change far better when they understand the specific problem it's solving, even if they personally dislike the outcome, than when a new structure is announced with no stated rationale -- unexplained change reads as arbitrary, which is what drives the cynicism and disengagement described above. Communicate the diagnosed problem, the new structure, and honestly, the new costs it introduces (don't pretend the new structure is a pure win with no trade-offs -- people who've lived through a reorg before will not believe that, and the credibility cost of an obviously spun announcement is worse than an honest one).

### Evaluate against the original problem, not vaguely
After the dust settles (give it the budgeted settling-in period, not a snap judgment in week one), check specifically whether the structural problem that justified the reorg actually improved -- did cross-team coordination on features actually drop, did the specific bottleneck actually clear -- rather than a vague "does this feel better." This closes the loop and, importantly, builds organizational credibility for the *next* reorg, because people can see that the last one was actually evaluated against what it promised, not just declared a success by fiat.

## Pros
- A reorg justified by a specific, named problem and executed on a tight timeline is far less disruptive than one that's vague, slow, or unexplained.
- Explaining the "why" preserves trust even among people who dislike the specific outcome, protecting the organization's ability to make future changes without triggering cynicism.
- Evaluating against the original stated problem creates real accountability and organizational learning about what reorgs actually accomplish.

## Cons
- Even a well-executed reorg has a real, unavoidable productivity dip while new teams build working relationships and norms -- there's no way to get the benefit without paying some of this cost.
- The discipline of "name the specific problem first" is easy to skip under pressure from a new leader or a board that wants visible action, and a reorg done quickly without that diagnosis tends to just move the problem rather than solve it.
- Honest communication about the new structure's trade-offs can itself create anxiety or pushback that a more optimistic, less-honest announcement would have avoided in the short term -- the long-term trust benefit isn't always obviously worth the short-term discomfort to leaders under pressure.

## Alternatives
- **Continuous, incremental team-boundary adjustment (no formal "reorg" event)** -- handle structural drift through frequent small splits/merges (`elegant-puzzle/05`) rather than periodic large reorgs; avoids the big disruptive event, but requires strong ongoing organizational-design attention that many companies don't sustain, and can still add up to reorg-fatigue if the small changes are frequent enough.
- **Reorg by imitation (adopt a well-known company's structure)** -- copy a structure that worked well elsewhere (e.g., "let's do Spotify squads"); fast to decide, avoids the harder diagnostic work, but skips the step of confirming the borrowed structure actually addresses your specific problem, and company-specific context (scale, product shape, culture) that made it work elsewhere often doesn't transfer.
- **Leadership-change-driven reorg** -- a new VP or CTO reorganizes as one of their first acts, independent of a specific diagnosed problem, often to establish authority or signal change; can occasionally surface real problems a fresh perspective catches, but is exactly the "no stated diagnosis" pattern this lesson warns is the most damaging kind of reorg.

## When to use it
Reorganize when you've diagnosed a genuine structural mismatch (span, scope, or Conway's-Law boundary problem) that a smaller, targeted split or merge can't address, and you can state specifically what will improve and how you'll know.

## When NOT to use it
Don't reorganize as a generic response to a vague feeling that something's wrong, to imitate another company's structure without checking it fits your specific problem, or as a new leader's default first move -- in all these cases, the diagnostic step from `elegant-puzzle/02` almost always reveals a smaller, cheaper, more targeted fix.

## Key takeaways / mental model
Before any reorg, force a one-sentence answer to "what specific structural problem does this solve, and how will we know it worked?" If that sentence is vague or missing, the reorg is not ready -- go do the diagnostic work first, and check whether a targeted split or merge would solve it at a fraction of the cost.

## Self-check questions
1. A new VP proposes a full reorg in their first month without pointing to a specific structural problem. What would you ask them before supporting it?
2. Design a one-paragraph communication for a hypothetical reorg that names the specific problem, the new structure, and honestly states a new cost it introduces. Why does including the cost matter?
3. Contrast a reorg executed over two weeks with clear communication versus one that's announced but drags out over three months in ambiguity. What specifically goes wrong in the second case that doesn't in the first?
4. Six months after a reorg, how would you evaluate whether it actually worked? What would "worked" concretely mean, tied back to the original diagnosis?

## References
- An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Reorganizations" and "Navigating Change", Part V.
