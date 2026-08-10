---
id: staff-engineers-path/12
subject: staff-engineers-path
title: Building communities of practice across teams
slug: communities-of-practice
status: drafted
mastery:
seniority: staff
source: The Staff Engineer's Path (Tanya Reilly), Chapter 6 - "Good Influence" (building community)
prerequisites: [staff-engineers-path/09, staff-engineers-path/11]
created: 2026-08-10
updated: 2026-08-10
---

# Building communities of practice across teams

## TL;DR
A community of practice is a voluntary, cross-team group organized around a shared technical domain (e.g., "backend reliability," "frontend accessibility") rather than around an org chart — it spreads knowledge, standards, and mutual support horizontally, at a scale no single mentoring relationship or top-down mandate can reach.

## The idea
Mentoring and sponsorship (`staff-engineers-path/10`, `staff-engineers-path/11`) work one relationship at a time; quality bars (`staff-engineers-path/09`) work by encoding judgment into artifacts everyone can read. Communities of practice add a third mechanism: peer-to-peer knowledge flow across team boundaries, sustained by the members themselves rather than by one staff engineer's direct effort. Once established, a healthy community keeps generating value — new members get onboarded by existing members, questions get answered by whoever has the relevant expertise that week, standards get refined by consensus — without requiring the founder to personally drive every interaction.

This matters because a lot of valuable knowledge is scattered unevenly across an org: the person who deeply understands database indexing strategy is on team A, the person who's fought hardest with a flaky test suite is on team B, and without a deliberate cross-team forum, these people never find each other, and each team relearns the other's hard-won lessons from scratch.

## How it works

### What makes a community of practice actually work
- **A real shared problem or interest, not a mandate** — people show up because the topic genuinely matters to their own work, not because they were told to attend. A "reliability guild" attracts people who are on-call and in pain; a guild invented top-down with no organic pull tends to wither after the first few meetings.
- **Low-friction, recurring cadence** — a regular (biweekly/monthly) meeting, a persistent chat channel, or both; frequency low enough to sustain, high enough to stay relevant.
- **Concrete artifacts, not just talk** — the most durable communities produce something: a shared runbook, a set of adopted standards, an internal newsletter of lessons learned. Discussion alone tends to feel good but leave no lasting trace; a shared artifact is what a new member can consume even if they never attend a meeting.
- **Distributed ownership** — a founder who starts the community deliberately hands off facilitation over time (rotating who runs each session, delegating the wiki's upkeep); a community that only functions when one specific person is present is fragile and hasn't actually achieved the cross-team scaling it was meant to.

**Worked example.** A staff engineer notices that database performance problems keep independently surfacing across four different teams, each rediscovering the same handful of anti-patterns (missing indexes on high-cardinality columns, unbounded `IN` clauses) the hard way. Rather than personally reviewing every team's queries (which doesn't scale, see `staff-engineers-path/07`), she starts a monthly "data performance" community of practice: a 30-minute open session where anyone can bring a real query/schema problem, plus a shared doc of anti-patterns and fixes that grows from real cases discussed. After the first few sessions, engineers from different teams start answering each other's questions in the group chat before the next meeting even happens — the knowledge is now flowing peer-to-peer, not routed through her. A year later, she's stepped back from running it; two engineers from different teams now co-facilitate, and the anti-patterns doc is referenced in onboarding for new hires.

### The founder's job shrinks over time, on purpose
The measure of a successful community of practice is that it becomes less dependent on its founder, not more. A staff engineer who's still the one answering every question and running every session two years in has built a following, not a community — the scaling promise (knowledge flowing without requiring the founder's personal bandwidth) hasn't actually materialized.

## Pros
- Spreads knowledge across team boundaries at a scale no individual mentoring relationship or personal review bandwidth can reach.
- Self-sustaining once healthy — value keeps accruing (onboarding new members, answering questions, refining standards) without requiring proportional ongoing effort from the founder.
- Surfaces talent and expertise that would otherwise stay siloed inside one team, and gives quieter experts a low-stakes venue to be recognized across the org.

## Cons
- Genuinely hard to bootstrap — many well-intentioned communities of practice fail to gain critical mass and quietly die after a few meetings, especially if started top-down without organic interest.
- Requires real, sustained facilitation effort in the early stages before it can run on its own, which competes directly with a staff engineer's other execution work.
- Can drift into a talking shop that produces discussion but no durable artifact or actual behavior change, if nobody actively steers it toward concrete outputs.

## Alternatives
- **Formal working groups / committees with a charter and deliverables** — more structured, with explicit accountability and output requirements; better suited to a bounded, time-limited decision (e.g., "pick our logging standard") than to ongoing, open-ended knowledge-sharing, which benefits from a community's more organic, voluntary participation.
- **Centralized platform/enablement teams** — a dedicated team owns and pushes out standards/tooling top-down rather than relying on peer-driven, voluntary knowledge flow; more consistent and better resourced, but doesn't capture the same peer-to-peer, bottom-up expertise-sharing a community of practice does, and can feel imposed rather than owned by its users.
- **One-off cross-team knowledge-sharing events (a single tech talk, a hackathon)** — lower commitment, easier to organize, but produces a one-time spike of shared knowledge rather than the sustained, compounding flow a recurring community produces.

## When to use it
Start a community of practice when you notice the same class of problem being independently rediscovered across multiple teams, and there's genuine grassroots interest (people already informally asking each other about it) that a structured forum would amplify rather than manufacture from nothing.

## When NOT to use it
Don't start one top-down, for a topic with no organic pull, expecting attendance to follow from a calendar invite alone — it won't sustain. And don't keep personally running a community indefinitely; if you're still the sole facilitator after a year, that's a signal to actively recruit co-facilitators rather than a sign the community doesn't need you to step back.

## Key takeaways / mental model
A community of practice turns one-to-one knowledge sharing into many-to-many, scaling past what any individual's mentoring bandwidth could reach — but only if it has genuine grassroots pull, produces durable artifacts (not just conversation), and the founder deliberately hands off ownership so the community outlives their personal involvement.

## Self-check questions
1. Identify a technical topic in your org where the same problem seems to be independently rediscovered by multiple teams. What early signal would tell you this has genuine grassroots interest, versus being a topic only you care about?
2. Why does a community of practice that produces no durable artifact (just recurring discussion) tend to be less valuable than one that does, even if the discussions themselves are good?
3. Describe what "success" looks like for a community of practice's founder two years in, in terms of their own ongoing involvement. Why is a founder who's still indispensable actually a sign of partial failure?
4. Compare a community of practice to a formal working group with a charter. When would you reach for each?

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 6: "Good Influence" (building community).
