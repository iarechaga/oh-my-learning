---
id: staff-engineer/09
subject: staff-engineer
title: Running critical initiatives across multiple teams
slug: running-critical-initiatives
status: drafted
mastery:
seniority: staff
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 7 ("Running an initiative")
prerequisites: [staff-engineer/03, staff-engineer/06, staff-engineer/07]
created: 2026-08-10
updated: 2026-08-10
---

# Running critical initiatives across multiple teams

## TL;DR
Running a multi-team initiative is a distinct skill from either individual technical execution or single-team tech-leading: it requires an explicit plan with named owners and milestones, continuous unblocking of other people's work rather than doing the work yourself, and honest, frequent status communication — because the initiative can fail from coordination breakdown even when every individual team's engineering is excellent.

## The idea
A single-team project fails, when it fails, mostly for technical reasons: the design was wrong, the estimate was wrong, someone got sick. A multi-team initiative can fail for those same reasons, but it can also fail in ways that have nothing to do with any team's engineering quality: two teams interpret a shared dependency differently and build incompatible pieces, no one notices a blocking issue on Team C until Team A and B are already waiting on it, or the initiative slowly loses executive priority because nobody is reporting status upward and it silently gets deprioritized in people's heads even though it's never formally cancelled.

This means the staff-plus engineer running a critical initiative is doing a fundamentally different job than being an excellent individual contributor on it. The core activity shifts from "solve technical problems personally" to "make sure the right technical problems get solved, by the right people, in the right order, with visibility for anyone who needs it" — closer to project management than to engineering in the narrow sense, even though the domain expertise that got you the role is still essential for knowing which technical problems actually matter.

## How it works

### Build an explicit plan, not just a shared understanding
A plan that exists only as a shared mental model among the initial few people who discussed it degrades badly as the initiative grows past those people — new contributors joining later have no record to consult, and even the original participants' memories of "what we agreed" quietly drift apart over months. A written plan, however imperfect, that names milestones, owners, and dependencies gives everyone (including people who join later) something concrete to check against and correct rather than silently reinterpret.

**Worked example — a plan skeleton for a multi-team migration:**
```
Initiative: Migrate service X from legacy datastore to new datastore
Sponsor: VP Eng (executive-level backing, resolves priority conflicts)
Owner: staff engineer (this lesson's protagonist) — coordinates, not sole executor

Milestone 1 (wk 1-3):  Schema mapping finalized — Owner: Team A lead
Milestone 2 (wk 2-6):  Dual-write path built and shadow-tested — Owner: Team B
Milestone 3 (wk 4-8):  Read-path migrated behind a flag — Owner: Team A
Milestone 4 (wk 8-10): Legacy datastore decommissioned — Owner: Team C (owns legacy infra)

Cross-team dependency: Milestone 3 blocked on Milestone 1's schema sign-off from Team C's
downstream consumer, which has not yet reviewed the proposed schema as of week 1.
```
Writing the dependency explicitly (the last line) is what turns a hidden risk into a trackable, chaseable item — without it, that dependency likely surfaces as a surprise in week 4 instead of a flagged risk in week 1.

### Spend your time unblocking, not executing
On a multi-team initiative, the staff engineer's highest-leverage use of time is almost never writing code personally — it's identifying and clearing whatever is currently the slowest-moving dependency. This might mean a technical deep-dive to unstick a specific hard problem one team is stuck on, a conversation to resolve a disagreement between two teams' approaches before it becomes a blocking argument, or escalating a resourcing conflict to the sponsor because no one below executive level can resolve it. The skill is continuously re-asking "what is the single thing most likely to slow this initiative down right now?" and going there, rather than defaulting to whatever technical problem is personally most interesting.

### Communicate status honestly and regularly
A multi-team initiative that goes quiet for a month, even if it's actually on track, reads to stakeholders as at-risk or abandoned — and a multi-team initiative that's genuinely behind but reports "green" status to avoid an uncomfortable conversation loses trust catastrophically the moment the truth surfaces, usually right when it's too late to recover cleanly. Larson's guidance is blunt: report real status, including bad news, early and often — a yellow or red status raised early is a solvable problem; the same status hidden until the deadline is a crisis.

**Worked example of honest status reporting.** "Milestone 2 is two weeks behind because Team B's dual-write implementation surfaced an unexpected data-consistency edge case; we're adding one week to Milestone 2 and pulling one engineer from a lower-priority Team B project to help close the gap. This pushes the overall timeline by roughly one week; sponsor has been notified and is fine with the tradeoff." This names the problem, the concrete mitigation, and the actual impact — the alternative of "Milestone 2 slightly delayed, working on it" gives a reader nothing to act on and no reason to trust the initiative is actually under control.

### Handle the moment priorities conflict
Cross-team initiatives inevitably compete with each team's own local priorities — a team asked to contribute an engineer to Milestone 2 has its own roadmap commitments that engineer was also needed for. This conflict cannot usually be resolved by the initiative owner alone (per `staff-engineer/07`, they don't have authority over that team), which is exactly why a real executive sponsor, secured before the initiative starts, matters: the sponsor is the person with the actual authority to say "yes, deprioritize that for two weeks," so the initiative owner's job is surfacing the conflict clearly and quickly, not personally resolving something outside their authority.

## Pros
- Directly delivers the kind of high-leverage, cross-team, judgment-heavy work that defines staff-plus impact (`staff-engineer/01`, `staff-engineer/03`).
- A written plan and honest status cadence create an auditable trail that protects the initiative (and its owner) if priorities or personnel change mid-initiative.
- Builds exactly the sponsor relationships and organizational trust (`staff-engineer/05`, `staff-engineer/07`) that compound into future influence.

## Cons
- Emotionally and organizationally taxing — the job is disproportionately about naming bad news, chasing other people's blockers, and resolving disagreements, which is a different (and for some engineers, less enjoyable) kind of work than hands-on technical execution.
- Success depends heavily on factors partly outside the owner's control — a weak or absent executive sponsor, or a team whose manager simply won't prioritize the ask, can stall an otherwise well-run initiative.
- Risk of the owner becoming a single point of failure if the plan and status live only in their head rather than in a shared, written artifact.

## Alternatives
- **A dedicated technical program manager (TPM) handling coordination, paired with a staff engineer for technical direction** — splits the coordination and technical-judgment halves of this role across two people; common at larger companies, and can work well, but requires the TPM and staff engineer to coordinate closely themselves, and doesn't remove the need for someone with real technical judgment to be deeply involved.
- **Fully decentralized coordination (no single owner, teams self-organize via a shared channel)** — lower overhead for small, low-stakes cross-team efforts; tends to break down for genuinely critical, deadline-bound, multi-team initiatives where the coordination failure modes described in this lesson are exactly what's at stake.
- **Top-down mandate from an executive with no staff-engineer coordination layer** — an executive can simply order teams to align; faster in theory, but skips the technical judgment about sequencing, dependencies, and risk that a staff-plus owner brings, and tends to produce technically worse outcomes even when the mandate succeeds politically.

## When to use it
Take on this role when an initiative genuinely spans multiple teams, has real executive-level priority (needs a sponsor), and needs someone with enough technical depth to make sequencing and risk judgment calls that a pure program manager couldn't make alone.

## When NOT to use it
Don't apply this level of coordination overhead (formal plans, milestone tracking, regular status reports) to work that's genuinely single-team or low-stakes — for that scope, the lighter-weight Tech Lead pattern from `staff-engineer/02` is the right amount of process, and over-formalizing small efforts wastes everyone's time.

## Key takeaways / mental model
Think of yourself as the initiative's air-traffic controller, not its pilot: your job is to know where every plane (team/workstream) is, spot the one about to cause a collision (a blocking dependency or conflict), and clear it — not to personally fly every plane. And an air-traffic controller who goes quiet for a month is a bigger risk to the airport than one who reports a minor delay honestly every day.

## Self-check questions
1. Describe a multi-team initiative you've observed that struggled or failed. Using this lesson's framework, was the failure technical, or was it a coordination failure (unclear plan, no real sponsor, late/dishonest status)?
2. In the worked migration example, why does writing down the Milestone 3 dependency on Team C's schema review matter more than simply knowing about it informally?
3. Explain why Larson argues that reporting "yellow/red" status early is safer for the initiative owner than reporting "green" status that later turns out to have been optimistic. What's the trust mechanism at play?
4. Why can't the initiative owner alone resolve a resourcing conflict between the initiative and a contributing team's local priorities? What has to be true before the initiative even starts for that conflict to be resolvable?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 7: "Running an initiative."
