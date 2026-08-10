---
id: sre/09
subject: sre
title: Incident Command and Coordinated Response
slug: incident-command
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 13-14
prerequisites: [sre/08]
created: 2026-08-10
updated: 2026-08-10
---

# Incident Command and Coordinated Response

## TL;DR
Large incidents fail not because no one knows the fix, but because too many people try to fix it at once with no shared picture of what's been tried, who's doing what, and who's talking to whom. Incident Command structures response around clearly separated roles — Incident Commander (IC), Operations Lead, and Communications Lead — so that coordination itself doesn't become the bottleneck during the incident that matters most.

## The idea
A single engineer debugging their own service at 2am doesn't need process — they need a good runbook and clear thinking. But once an incident grows to involve multiple teams, multiple hypotheses being tested in parallel, and stakeholders (support, leadership, sometimes customers) who need updates, the coordination problem becomes as hard as the technical problem. Two classic failure patterns emerge without structure: **too many cooks** (three engineers independently try conflicting fixes on the same system, doubling the damage) and **the silent fix** (someone resolves the root cause but doesn't tell anyone, so others keep debugging a problem that's already gone, wasting time and creating confusion about whether it's really fixed).

Google's answer, adapted from the Incident Command System used in emergency services (firefighting, disaster response), is to formally separate the roles of *deciding what to do*, *doing the technical work*, and *communicating status* — so each can be done well without the people doing one blocking or duplicating the others.

## How it works

### The core roles
1. **Incident Commander (IC)** — owns the overall response. Does *not* necessarily do hands-on technical work themselves; their job is to maintain the big picture, make prioritization calls (which hypothesis to chase first, when to declare the incident resolved, when to escalate further), and ensure the other roles are staffed and functioning. The IC is the single point of authority during the incident — everyone else defers to the IC's calls even if they personally disagree, to avoid the incident dissolving into parallel, uncoordinated decision-making.
2. **Operations Lead (Ops Lead)** — directs the actual technical mitigation work: which engineers investigate which hypothesis, what changes get made, in what order. Reports status and blockers up to the IC rather than acting unilaterally on major changes.
3. **Communications Lead (Comms Lead)** — owns all external and cross-team updates: status page updates, messages to support/leadership, coordinating with other affected teams. This deliberately frees the IC and Ops Lead from being interrupted every few minutes by "what's the status" questions, which is often the single biggest hidden time-sink during a real incident.

For small incidents, one person may hold multiple roles (e.g., IC and Ops Lead combined); the roles scale up as the incident's severity and organizational reach grow, not as a fixed bureaucracy applied uniformly to every page.

### Worked example: a severity-1 incident timeline
A payments service starts failing 40% of transactions at 14:02. Trace how the roles engage:
- **14:03** — On-call engineer acknowledges the page, confirms real user impact (checks the golden-signal dashboard from `sre/07`), and declares an incident, paging in an IC per the escalation policy.
- **14:07** — IC arrives, does a 2-minute situation assessment (what's the blast radius, what's the current error-budget burn rate), and immediately assigns: the original on-call engineer becomes Ops Lead (they already have the most context), and pages a second engineer to take Comms Lead.
- **14:09** — Comms Lead posts an initial internal status update ("Payments service degraded, ~40% error rate, IC assigned, investigating") to the incident channel and support team, so support can start managing customer inquiries without pulling engineers away from the fix.
- **14:12-14:35** — Ops Lead directs two engineers to investigate two parallel hypotheses (a recent deploy vs. a downstream dependency outage) rather than letting them freelance independently; reports progress to the IC every ~10 minutes.
- **14:36** — One hypothesis confirmed (a bad deploy); IC makes the call to roll back rather than forward-fix, given the error-budget burn rate and uncertainty about a forward fix's risk (an application of `sre/04`'s budget-driven decision-making, escalated to real-time).
- **14:41** — Rollback completes, error rate returns to baseline. IC declares the incident mitigated (not yet closed — see below) and directs Comms Lead to post the resolution update.
- **14:41 onward** — IC keeps the incident open for a monitoring period (e.g., 30 minutes) to confirm the fix holds before formally closing, then hands off postmortem ownership (`sre/10`).

Notice what the role separation bought here: the two engineers debugging in parallel didn't each also have to context-switch into writing status updates: the Ops Lead didn't have to personally decide whether to roll back without any check — the IC, holding the whole picture including budget burn, made that call; and support had accurate, timely information without pulling an engineer off the technical work to answer them directly.

### Declaring an incident: the threshold question
A common failure mode is *not declaring* an incident early enough — engineers try to fix a growing problem solo for 20-30 minutes before finally looping others in, by which point the error budget (`sre/04`) has taken much more damage than if response had been coordinated from the start. The book's guidance: err toward declaring an incident (and thus activating IC structure) too early rather than too late — the cost of a brief, unnecessary IC engagement is small; the cost of a slow, uncoordinated response to a real severity-1 incident is not. A useful trigger: if you're not confident you can resolve it solo within roughly 5-10 minutes, declare and get an IC involved.

### Handoffs across shifts or timezones
Long-running incidents (spanning many hours) need IC handoffs just like on-call shift handoffs (`sre/08`): a documented state transfer (what's been tried, what's ruled out, current hypothesis, current error-budget burn) so the incoming IC doesn't restart the investigation from zero. Skipping this handoff is a common source of duplicated, wasted effort on incidents that outlast a single person's shift.

## Pros
- Prevents the two classic large-incident failure modes (conflicting parallel fixes, silent unreported fixes) by giving exactly one person authority over prioritization and giving status communication a dedicated owner.
- Scales cleanly: a one-person incident and a fifty-person, cross-org incident use the same role structure, just with more people filling more roles.
- Frees the technically-engaged responders from interruption by status-update requests, which meaningfully speeds up actual mitigation time.

## Cons
- Adds process overhead that's genuinely wasteful for small, quickly-resolved incidents where a single engineer really can fix it alone in a few minutes.
- Only works if the org has trained, available people willing and able to step into IC/Comms/Ops roles under pressure — an untrained "IC" who doesn't actually direct the response provides none of the structure's benefit.
- The IC's authority model requires organizational buy-in that people will actually defer to the IC's calls even when they disagree in the moment — without that norm, the structure collapses back into unstructured debate during the incident.

## Alternatives
- **No formal roles, ad hoc "whoever's on-call handles it"** — zero overhead for genuinely small incidents, but scales poorly and is exactly the setup that produces the too-many-cooks and silent-fix failure modes once an incident grows.
- **Single "incident owner" with no role separation** — better than nothing, but re-concentrates the coordination, technical-direction, and communication burden on one person, recreating the interruption problem the IC/Ops/Comms split is designed to solve.
- **Fully centralized NOC-driven incident management** — a dedicated operations center owns coordination for all incidents across many teams; can provide consistent process at large scale, but the coordinators often have less deep technical context than the responding engineers, trading context for consistency.

## When to use it
Activate IC structure for any incident with real, ongoing user impact where resolution isn't obviously imminent within a few minutes, and especially for anything spanning multiple teams or with visible external impact. Err toward declaring early.

## When NOT to use it
Don't impose full IC/Ops/Comms role separation on a trivial, quickly-self-resolved issue (e.g., a single failed health check that auto-recovers in seconds) — the overhead of assembling roles exceeds the incident's actual severity. Scale the structure to the incident, not the other way around.

## Key takeaways / mental model
Separate *deciding* (IC), *doing* (Ops Lead), and *communicating* (Comms Lead) so none of the three blocks the others during the moment that matters most. When in doubt about whether to declare an incident, declare it — the cost of an unnecessary IC engagement is small compared to the cost of an uncoordinated response to a real one.

## Self-check questions
1. Two engineers, working independently without an IC, each push a different config change to try to fix the same degraded service within minutes of each other. Using this lesson's framework, name the failure mode and explain what role, if assigned earlier, would have prevented it.
2. Why does the book recommend the IC not necessarily do hands-on technical work themselves? What specific coordination failure does that separation prevent?
3. A minor incident (one service briefly degraded, auto-recovers in 90 seconds, no user reports) gets a full IC/Ops/Comms activation anyway. Is this appropriate? Explain the trade-off using this lesson's cost framing.
4. Describe what information a mid-incident IC handoff (say, at a shift boundary 6 hours into an unresolved incident) must contain, and what could go wrong for the incoming IC if any of it is missing.

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 13 ("Emergency Response") and Chapter 14 ("Managing Incidents").
- See also: `sre/08` (on-call, which feeds the initial responder into incident command) and `sre/10` (postmortems, the learning loop that follows every significant incident).
