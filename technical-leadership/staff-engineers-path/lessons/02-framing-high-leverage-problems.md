---
id: staff-engineers-path/02
subject: staff-engineers-path
title: Finding and framing high-leverage problems
slug: framing-high-leverage-problems
status: drafted
mastery:
seniority: staff
source: The Staff Engineer's Path (Tanya Reilly), Chapter 2 - "Three maps"
prerequisites: [staff-engineers-path/01]
created: 2026-08-10
updated: 2026-08-10
---

# Finding and framing high-leverage problems

## TL;DR
Staff engineers are not handed a backlog — they are expected to find the problems worth solving. High-leverage problem-finding means deliberately scanning beyond your own team for gaps nobody owns, translating "vague discomfort" into a crisply framed problem statement, and checking the problem is worth your scarce time *before* you commit to it.

## The idea
Below staff level, someone else usually decides what you work on: a manager, a ticket, a roadmap item. At staff level, a meaningful fraction of your job is *deciding what deserves attention in the first place* — and that's a genuinely different skill from executing well on a given task. Many capable senior engineers stall at the staff transition not because they can't solve hard problems, but because they wait for a hard problem to be assigned to them, and it never is: the org expects *them* to notice it.

The risk on the other side is just as real: staff engineers have significant latitude, and latitude without discipline turns into chasing whatever is personally interesting, or whatever squeaks loudest, rather than what actually moves the needle. "High-leverage" is the filter — a problem is high-leverage when the org-wide cost of it staying unsolved is large relative to the cost of you solving it.

## How it works

### Where high-leverage problems hide
They rarely show up as a ticket titled "high-leverage problem." They show up as symptoms:
- **Recurring pain across teams** — three different teams have each built their own retry/backoff logic against the same flaky downstream service; each team's engineers assume it's just "how this API is."
- **Things everyone complains about but nobody owns** — "the deploy pipeline is flaky" said in every team's retro for two quarters, with no team lead having deploy-pipeline ownership in their charter.
- **Silent risk** — a single-region database that would take the whole company down in an outage, currently invisible because it hasn't failed yet.
- **Org boundaries where problems fall through the cracks** — anything that needs two teams' cooperation to fix tends to get permanently deprioritized by both, since it's not clearly either team's job.

**Worked example.** Say you notice three teams independently maintaining ad-hoc feature-flag systems, each buggy in a different way, each costing an engineer-week per quarter in flag-related incidents. No single team is "responsible" for feature flagging — it's cross-cutting infrastructure that fell through the org chart's cracks. That's a textbook high-leverage candidate: the aggregate cost (3 teams x recurring incidents) is large, the fix (one shared, well-built flagging service) is bounded, and nobody else is going to notice this pattern because no single team sees all three instances.

### Framing: turning a vague pain into a crisp problem statement
Noticing pain isn't enough — you need to *frame* it so other people can evaluate, prioritize, and eventually help solve it. A good problem frame answers:
1. **What's the actual cost of the status quo?** (quantify where you can: engineer-hours lost, incidents per quarter, dollars, latency)
2. **Who is affected, and how broadly?** (one team vs. the whole org changes urgency and who needs to buy in)
3. **What does "solved" look like?** (a fuzzy complaint like "flags are annoying" isn't actionable; "a shared flagging service with audit logs and a kill switch, adopted by all consumer-facing teams" is)
4. **Why now, and why you?** (staff engineers have to justify spending scarce organizational attention — "this has been bad for two years and nobody's picked it up" is a weaker case than "the cost just tripled because we're onboarding three new teams this quarter")

**Before framing:** "Feature flags are a mess." (Not actionable — nobody can prioritize a feeling.)
**After framing:** "Three teams have independently built feature-flag systems; incident review shows 4 flag-related outages in Q2 totaling 6 hours of downtime across teams. A shared, audited flagging service would eliminate the duplicated build cost (~3 engineer-months total) and the inconsistent-behavior risk. Proposing we build one centrally-owned service this half, sponsored by Platform, adopted incrementally by the three teams." (Actionable — a leader can say yes or no to this.)

### Checking it's actually worth solving
Not every pain point is worth your time, even if the framing is crisp. Reilly's heuristic: weigh **cost of the problem x how many people it affects** against **cost of solving it x opportunity cost of what else you'd do instead**. A problem that's mildly annoying to one team is not high-leverage even if it's easy to frame nicely; a problem that's expensive across the whole org is high-leverage even if solving it is hard, *because the alternative — leaving it unsolved — is more expensive still*.

## Pros
- Surfaces problems that would otherwise never get organizational attention, because no single team has both the visibility and the mandate to see them.
- A crisp problem frame is reusable: it becomes the seed of the technical-direction document (`staff-engineers-path/05`) and the pitch you'll make to secure sponsorship (`staff-engineers-path/10`).
- Builds the "sees around corners" reputation that is a large part of how staff-level judgment gets recognized informally.

## Cons
- Problem-finding is unstructured, open-ended work; it's easy to spend weeks scanning for problems and produce nothing, which reads as unproductive to a results-oriented manager unless you communicate the process.
- The instinct to fix everything you notice is a trap — most staff engineers who burn out chasing every cross-team pain point learn this the hard way, hence the explicit "is it worth it" filter.
- Quantifying cost is often genuinely hard (how do you price "developer frustration" or "risk of an outage that hasn't happened yet"?) — imprecise estimates can be gamed or dismissed.

## Alternatives
- **Manager/roadmap-assigned problems** — the default mode for non-staff engineers; lower autonomy but also lower risk of misjudging leverage; appropriate when you're new to a team/org and don't yet have the context to judge leverage well.
- **Incident-driven prioritization** — let problems surface themselves via outages/postmortems rather than proactively scanning; reactive rather than anticipatory, and by definition finds problems only after they've already cost something.
- **Formal architecture review boards** — a structured, committee-based process for surfacing and vetting cross-team technical problems; more overhead and slower, but spreads the "what's worth solving" judgment across more people rather than resting on one staff engineer's instinct.

## When to use it
Use deliberate problem-finding when you have staff-level scope (visibility across multiple teams) and the organization doesn't have a strong existing mechanism for surfacing cross-cutting technical debt or risk. It's especially valuable in fast-growing orgs, where yesterday's reasonable local decisions compound into today's cross-team mess faster than anyone tracks.

## When NOT to use it
Don't apply this if you're new to a team or org — you don't yet have the pattern-recognition to reliably distinguish "genuinely high-leverage" from "annoying but locally contained," and swooping in to "fix" something you don't yet understand the history of is a fast way to burn trust. Also skip it when a problem is already clearly someone else's mandate (a team explicitly owns it and is actively working it) — parachuting in duplicates effort and can look like a vote of no confidence.

## Key takeaways / mental model
High-leverage problem-finding = scan for pain that crosses team boundaries -> frame it as cost x scope x "what solved looks like" -> weigh that against your own scarce time before committing. The framing step is what turns "I noticed something annoying" into "I found something the org needs to fix," and that translation is most of the actual skill.

## Self-check questions
1. Think of a recurring complaint at your own company (or a past one) that no single team owns. Frame it using the four-question structure (cost, scope, "solved" definition, why now/why you).
2. Why is "I noticed X is annoying" not yet a usable problem statement, even if X really is a problem? What's missing?
3. A colleague spots a legitimate cross-team pain point but a team is already actively fixing it. Should they still get involved? What should they do instead?
4. Describe the trade-off a staff engineer is implicitly making when they choose to spend a month framing and pitching a shared-infrastructure fix instead of shipping three months of feature work on their own team.

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 2: "Three maps".
