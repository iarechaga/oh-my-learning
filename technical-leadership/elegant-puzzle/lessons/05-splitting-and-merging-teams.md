---
id: elegant-puzzle/05
subject: elegant-puzzle
title: Splitting and merging teams as the organization evolves
slug: splitting-and-merging-teams
status: drafted
mastery:
seniority: staff
source: An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Splitting Teams" and "Merging Teams"
prerequisites: [elegant-puzzle/03, elegant-puzzle/04]
created: 2026-08-10
updated: 2026-08-10
---

# Splitting and merging teams as the organization evolves

## TL;DR
Teams outgrow their shape as the org scales: a team that grows past its coherent scope needs to split, and scattered, sub-critical-mass teams need to merge; both moves are routine maintenance, not crises, but each has a specific mechanics (how you draw the new boundary, how you sequence the transition) that determines whether it costs a few weeks of disruption or months of dysfunction.

## The idea
Team boundaries are not permanent. As headcount and scope grow, a team that once fit comfortably on the span/scope grid (`elegant-puzzle/03`) eventually exceeds it -- too many reports for one manager, or too much cognitive load for the group to hold coherently. The natural response is to split. The opposite failure also happens: reorgs, attrition, or over-eager splitting in the past leave you with several small teams each below the size needed to cover on-call, absorb attrition, or make meaningful roadmap progress -- these need to merge back into fewer, larger, more resilient teams. Larson treats both as expected, periodic maintenance operations on a growing org, with their own best practices, rather than as failures of the original design.

## How it works

### When to split
Signals it's time to split a team: the manager's span of control is chronically over the sustainable range (`elegant-puzzle/03`); the team's scope has grown to cover multiple genuinely distinct problem areas that no longer share much context; on-call load has grown to the point where the rotation is unsustainably frequent per person; or decision-making has visibly slowed because too many people need to weigh in on anything.

**How to draw the split boundary.** The best split follows an existing natural seam in the work -- a service boundary, a product-area boundary, a customer-segment boundary -- rather than an arbitrary headcount split (e.g., "first 5 alphabetically go to team A"). A split along a real technical or product seam means each new team inherits a coherent, self-contained scope and the interface between the two new teams can be well-specified (an API contract, a clear ownership line), whereas an arbitrary split leaves both new teams needing to constantly coordinate on shared, ill-defined territory -- Conway's Law again (`elegant-puzzle/04`): draw the org seam where you want the technical seam.

**Worked example.** A 14-person platform team owns both the internal deploy pipeline and the internal feature-flagging system. It splits into a 7-person Deploy team and a 7-person Flags team, following the existing service boundary between the two systems. Because the systems already had a clean API between them, the org split introduces almost no new coordination cost -- each new team's manager now has a sustainable span, and each team's on-call only pages for its own system. Contrast with a split that instead sent half of each existing squad's members to each new team regardless of what they'd been working on: both new teams would still need most people from the other team in the loop for a while, because expertise, not just headcount, got split without regard to the technical seam.

**Sequencing a split.** Announce the new boundary and rationale before individual assignments to reduce anxiety about "who's picking teams," give people input on which new team they land on where possible (motivation matters more than a perfectly even split), and expect a temporary velocity dip while the two new teams establish their own norms and interfaces -- budget for it rather than being surprised by it.

### When to merge
Signals it's time to merge: a team is chronically below the size needed to staff a sustainable on-call rotation (fewer than ~4-5 people usually can't sustain on-call without burning people out); a team can't make roadmap progress because any single person being out (vacation, illness) stalls the whole team; or several small teams have overlapping scope that used to be distinct but has converged, so they're now duplicating work and coordinating constantly anyway -- at which point formalizing the merge just names what's already true.

**How to merge well.** Unlike a split, a merge usually needs one clear consolidated leader rather than trying to co-manage indefinitely -- pick the manager (or make an explicit, time-boxed decision process) early rather than leaving it ambiguous, since ambiguous leadership during a merge is exactly the kind of dual-authority problem matrix structures already struggle with (`elegant-puzzle/04`). Reconcile the two teams' differing norms and technical standards deliberately (which team's code review process wins? which team's on-call runbook?) rather than letting the larger or louder team's norms silently win by default, which breeds resentment in the absorbed team.

### Both operations cost transition time -- budget for it
Both splitting and merging temporarily reduce velocity: new teams need to build working norms, new managers need to build trust with reports they may not have managed before, and interfaces between newly-separated or newly-joined pieces of work need to be renegotiated. Larson's guidance: treat this as an expected, bounded cost (weeks, not indefinite), and communicate that expectation to stakeholders up front so a temporary dip isn't read as the reorg having failed.

## Pros
- Splitting on a schedule tied to real signals (span, scope, on-call load) prevents teams from silently degrading into the overload symptoms covered in `elegant-puzzle/03`.
- Merging keeps small teams from being permanently fragile (no on-call coverage, no roadmap resilience to one person's absence).
- Following existing technical seams when splitting keeps the resulting architecture clean instead of accidentally creating tangled ownership.

## Cons
- Both operations have real, if temporary, velocity and morale costs -- doing them too frequently ("reorg churn") erodes trust and prevents teams from ever settling into a stable working rhythm.
- A split along the wrong seam (arbitrary headcount split instead of a real technical boundary) can create more coordination overhead than it removes.
- A merge without a clear single leader recreates the matrix structure's dual-authority problem inside what was meant to be a simplification.

## Alternatives
- **Leave teams as-is and add process instead of splitting** -- e.g., add more explicit prioritization meetings to an overloaded team rather than splitting it; cheaper short-term, but doesn't address the underlying cognitive-load or span problem and tends to just add more overhead on top of an already-strained team.
- **Hire a second manager under the same team without splitting scope** -- creates two managers co-owning one team's scope; avoids drawing a new boundary, but usually recreates dual-authority confusion rather than resolving overload, since the scope (the actual source of cognitive load) hasn't shrunk.
- **Full reorg instead of a targeted split/merge** -- redesign the whole org's shape (`elegant-puzzle/12`) instead of one team's boundary; justified when the problem is org-wide, but a full reorg is far more disruptive than fixing a single team's boundary and shouldn't be reached for when the problem is local.

## When to use it
Split when a team's span or scope has genuinely outgrown what one manager or one coherent group can hold, following a real technical or product seam. Merge when small teams can't sustain on-call, can't absorb an absence without stalling, or have converged in scope. Treat both as routine, periodic maintenance as the org scales, not emergency interventions.

## When NOT to use it
Don't split or merge reactively in response to a single bad quarter or a single personality conflict -- those usually need a direct conversation or a smaller-scale fix, not a structural change. Don't split just because a team "feels big" without checking actual span/scope signals; a team can be large and still coherent if its scope genuinely is that large and the manager has the bandwidth for it.

## Key takeaways / mental model
Splits and merges are load-bearing maintenance, not failure signals. Split along real technical seams, not arbitrary headcount lines, to keep Conway's Law working for you instead of against you. Merges need one clear leader and a deliberate reconciliation of norms, not silent default to whichever team was bigger.

## Self-check questions
1. A 16-person team needs to split. Identify what "natural seam" you'd look for before drawing the new boundary, and explain why an even 8-8 headcount split without regard to that seam would be worse.
2. Two 3-person teams have overlapping scope and both struggle to cover on-call. Would you merge them? What's the first decision you'd need to make explicitly to avoid recreating a dual-authority problem?
3. Describe the temporary costs you'd expect after a well-executed split. How would you communicate that expectation to stakeholders so a velocity dip isn't misread as failure?
4. Give an example of a "reorg churn" scenario -- splitting or merging too frequently -- and what signal would tell you your org is doing this too often.

## References
- An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Splitting Teams" and "Merging Teams", Part II.
