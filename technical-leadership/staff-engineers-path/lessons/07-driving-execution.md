---
id: staff-engineers-path/07
subject: staff-engineers-path
title: Driving execution through collaboration and delegation
slug: driving-execution
status: drafted
mastery:
seniority: staff
source: The Staff Engineer's Path (Tanya Reilly), Chapter 5 - "Guiding a project to completion"
prerequisites: [staff-engineers-path/06]
created: 2026-08-10
updated: 2026-08-10
---

# Driving execution through collaboration and delegation

## TL;DR
Staff-scope projects are too large for one person to build, so execution shifts from "do the work" to "make sure the work gets done" — delegating pieces to the right owners, staying accountable for the outcome without micromanaging the how, and actively unblocking the project's bottlenecks (often social/organizational, not technical).

## The idea
A senior engineer driving a project usually does most of the building themselves; the project's success and their personal output are nearly the same thing. A staff engineer driving a cross-team project cannot do that — the project's scope exceeds what one person can build in the available time, and even if it didn't, doing it all yourself means the project's success depends entirely on your personal bandwidth, which doesn't scale and creates a single point of failure. Driving execution at staff scope means becoming the person who makes sure the *right things happen in the right order by the right people*, which is a different skill from being the person who does the most things.

This is uncomfortable for many engineers who got to staff level by being excellent individual builders: delegation feels like losing control, and it's genuinely true that delegated work is executed less precisely than you'd do it yourself. The trade is deliberate — you accept some loss of precision in exchange for parallelism and for growing the people you delegate to (connecting to `staff-engineers-path/11`).

## How it works

### What to delegate, and to whom
Not all delegation is equal. A useful split:
- **Delegate the well-specified, well-understood pieces widely** — once the direction is clear (see `staff-engineers-path/05`), most of the actual implementation should go to the team members closest to the code, who'll also grow from doing it.
- **Keep the highest-ambiguity, highest-risk pieces closer to yourself, at least initially** — the piece nobody yet knows how to do, or the piece where a wrong early decision is expensive to unwind, benefits from your direct involvement until it's de-risked enough to hand off (echoing the "reduce ambiguity before committing" idea from `staff-engineers-path/06`).
- **Delegate outward, not just downward** — driving execution isn't limited to your own reports or team; it includes getting other teams' engineers, who don't report to you and have their own priorities, to own pieces of the work. This requires influence rather than authority (see the sponsorship overlap in `staff-engineers-path/10`).

**Worked example.** A staff engineer is driving a project to migrate five services off a deprecated message queue. She does not personally migrate all five. Instead: she writes the migration guide and does the riskiest, least-understood first migration herself (surfacing the gotchas early, while they're cheapest to discover). She then delegates the remaining four migrations to each service's own team, giving them the guide, office hours, and a clear deadline — trusting them to execute the now-well-understood pattern, while she tracks progress and unblocks anyone who gets stuck (a team discovers their message schema has an undocumented dependency the guide didn't anticipate; she helps them resolve it and updates the guide for the next team).

### Staying accountable without doing the work
Delegation without accountability becomes abdication — "I asked the team to do it" is not the same as "it got done." A staff engineer driving execution typically:
- **Tracks progress visibly** (a shared tracking doc, a regular sync, a dashboard) so slippage is caught early rather than discovered at the deadline.
- **Removes blockers proactively** rather than waiting to be asked — the person driving execution often has more organizational context and standing to unblock a stuck team than the team has to unblock itself (e.g., escalating a cross-team resourcing conflict that an individual contributor on the team couldn't escalate alone).
- **Owns the outcome in front of stakeholders**, even for pieces they didn't personally build — if the project misses its date, "the other team was late" is rarely an acceptable answer from the person who was asked to drive it; part of driving execution is anticipating and managing that risk in the first place.

### The most common bottleneck is social, not technical
A large fraction of what slows down cross-team execution isn't a hard technical problem — it's misaligned priorities, unclear ownership, or a team that's nominally agreed to help but hasn't actually prioritized the work against their own roadmap. Driving execution well means noticing this kind of blocker (a team has "agreed" in a meeting but nothing has moved in three weeks) and addressing it directly — following up, escalating, or renegotiating scope — rather than treating it as a technical problem to route around.

## Pros
- Unlocks project scope far beyond what any one person could build alone, which is the entire point of staff-level execution.
- Delegation grows the people you delegate to, compounding the org's capability over time (directly feeds `staff-engineers-path/11`).
- Distributing ownership reduces the bus-factor risk of one person being the sole bottleneck for a large project.

## Cons
- Real loss of precision and speed on any individual piece — someone learning a pattern for the first time will be slower and make more mistakes than you would doing it yourself.
- Requires influence without authority for cross-team pieces, which is slower and less certain than directing your own reports, and can fail if you don't have enough standing or the relationship with the other team.
- Tracking and unblocking multiple delegated workstreams is genuinely time-consuming coordination overhead, easy to underestimate when planning your own calendar.

## Alternatives
- **Direct individual execution** — do the highest-leverage piece yourself and skip delegation entirely; appropriate for small-scope projects or when the project is genuinely too specialized/risky to hand off safely, but doesn't scale to staff-sized cross-team work.
- **Formal program/project management** — hand coordination to a dedicated PM/TPM while the staff engineer focuses purely on technical decisions; effective at scale, but the PM typically can't make the technical judgment calls about what to delegate vs. keep close, so the two roles work best together rather than as substitutes.
- **Fully autonomous team ownership (no central driver)** — let each team self-organize around a shared goal with no single accountable driver; works when teams already have strong alignment and trust, but tends to produce coordination gaps on genuinely cross-cutting projects that don't map cleanly onto any one team's ownership.

## When to use it
Drive execution through delegation whenever a project's scope genuinely exceeds one person's hands-on capacity, or whenever leaving execution entirely to one owner would create an unacceptable single point of failure or fail to grow the team's collective capability.

## When NOT to use it
Don't delegate the highest-risk, least-understood piece of a project before it's been de-risked — handing an ambiguous, high-stakes piece to someone without your context sets them up to fail and can cost more time (in rework and lost trust) than it saves. Also don't over-delegate on a small, well-scoped project where a single owner building it directly is simply faster and simpler.

## Key takeaways / mental model
At staff scope, your job shifts from "build the thing" to "make sure the thing gets built" — de-risk and personally handle the highest-ambiguity piece first, delegate the well-understood pieces widely (including to other teams), track progress visibly, remove blockers proactively, and stay accountable for the outcome even for parts you didn't personally build.

## Self-check questions
1. Describe a project (real or hypothetical) that's too large for one person. Which piece would you keep close to yourself first, and which pieces would you delegate immediately? Justify the split.
2. What's the difference between delegation and abdication? Give a concrete example of each in the same scenario.
3. A team you're depending on for a cross-team project has "agreed to help" but hasn't made progress in three weeks. What's your first move, and why is this framed as a social/organizational problem rather than a technical one?
4. Why does doing all the highest-leverage work yourself, even if you're the fastest person available, become a liability at staff scope?

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 5: "Guiding a project to completion".
