---
id: phoenix-project/02
subject: phoenix-project
title: "Work as Flow: From Projects to Value Streams"
slug: work-as-flow-value-streams
status: drafted
mastery:
seniority: senior
source: The Phoenix Project (Kim, Behr, Spafford), Part 1
prerequisites: [phoenix-project/01]
created: 2026-08-10
updated: 2026-08-10
---

# Work as Flow: From Projects to Value Streams

## TL;DR
Most IT organizations manage work as a pile of disconnected projects, each with its own owner, its own budget, and its own deadline — nobody is responsible for how a unit of work actually *moves* from a business request to value delivered in production. Reframing work as **flow through a value stream** — a single, traceable path from "idea" to "running in production, delivering value" — is what makes bottlenecks, queues, and hidden work visible enough to manage at all. You cannot apply the Theory of Constraints (`phoenix-project/03`) or WIP limits (`phoenix-project/04`) to work you cannot see moving through a system.

## The idea
At Parts Unlimited, work arrives in IT from many directions — the Phoenix Project's feature backlog, urgent unplanned fixes, compliance remediation, routine maintenance — and each stream is tracked, if at all, by a different manager using a different spreadsheet, with no shared unit of measurement and no visibility into how requests actually flow (or stall) between teams. Bill's early diagnostic work in the book is essentially reverse-engineering a *value stream map*: tracing a single change (a Brent-authored payroll fix, or a Phoenix deployment) from the moment someone decided it was needed to the moment it was verified running correctly in production, and discovering that the change spent the overwhelming majority of its lifecycle not being worked on, but *waiting* — in a queue for a review, in a queue for a change-approval meeting, in a queue for Brent's attention because he is the only person who understands a particular subsystem.

This is the core reframe this lesson teaches: **IT work is not a portfolio of independent projects; it is a continuous flow of value-delivering changes through a shared system**, and every change — a feature, a bug fix, an infrastructure change, a security patch — moves through the same handful of stages (development, review, testing, deployment, verification) regardless of which "project" it's nominally attached to. Once you see work this way, questions that were previously unanswerable become answerable: how long does a typical change take from request to production (lead time)? Where does it spend the most time waiting rather than being worked on? How many changes are in flight at once, and is that number even known?

This lesson is a direct extension of `phoenix-project/01`: making work visible as flow is the concrete first step toward the systems-level view that lesson argues for. You cannot diagnose a systemic bottleneck (`phoenix-project/03`) in a system whose work you cannot even enumerate.

## How it works

### Mapping a value stream: from request to running in production
A value stream map for a software change typically has stages like: **idea/request -> prioritization -> design/development -> code review -> QA/testing -> change approval -> deployment -> production verification**. The critical practice is recording, for a real change, the *elapsed* time at each stage versus the *active work* time — because in an unmanaged system these two numbers diverge enormously.

**Worked example.** Suppose a mid-sized SaaS company traces a single "add a new billing field" change end to end: the ticket is filed on Monday, sits in an unprioritized backlog for 9 days before anyone picks it up, takes 4 hours of actual development, then waits 3 days for a code reviewer with bandwidth, takes 20 minutes to review, then waits 6 days for a slot in the weekly Change Advisory Board meeting, gets approved, then waits 2 days for the next deployment window, and takes 15 minutes to deploy and verify. Total elapsed time: 21 days. Total active work time: under 5 hours. The value-stream map makes visible what a project-list view never would: over 99% of this change's lifecycle was queueing, not working, and the two biggest queues (the unprioritized backlog and the weekly CAB meeting) are structural, not caused by any individual's slowness.

This is the single most important insight flow-mapping produces: **lead time is dominated by wait time, not work time**, almost always. Teams that try to speed up delivery by making developers code faster are optimizing the 5 hours, when the leverage is in the 21 days.

### Value streams cut across "projects," which is why they're hard to see by default
Parts Unlimited's org chart and project structure actively hide the value stream: the Phoenix Project team, the "keep the lights on" ops team, and the security/compliance team each see only their own slice of a change's journey, and no single person or dashboard shows the whole path. A change that starts as a Phoenix feature request might require an ops team deployment slot, a security team sign-off, and a DBA's migration review — four different "projects" from four different teams' point of view, but one continuous value stream from the customer's point of view. Managing by project instead of by value stream means each team locally optimizes its own piece (the dev team ships code fast, the ops team minimizes deploy risk by batching changes into rare, large windows) in ways that can actively *worsen* the end-to-end flow, because nobody owns the whole path.

**Worked example.** The ops team at Parts Unlimited, trying to reduce their own risk, batches deployments into a single large weekly window instead of deploying continuously. Locally, this looks responsible — fewer deployment events, more time to review each one. Globally, it means every change, regardless of size or risk, now inherits up to a 6-day queue before it can even attempt deployment, which is exactly the kind of local optimization that damages the end-to-end value stream discussed in `phoenix-project/03`'s treatment of constraints, and the batching itself increases the size and risk of each deployment (more changes bundled together means a failure is harder to isolate) — the opposite of the intended effect.

### From "percent complete" to "flow metrics"
Project-based tracking asks "what percent of the Phoenix Project is done?" — a number that is notoriously unreliable (famously, projects report 90% complete for months) because it measures effort claimed, not value delivered. Flow-based tracking asks different, more honest questions: **lead time** (idea to production, per change), **throughput** (changes completed per week), and **queue depth at each stage** (how many items are waiting at the review stage right now?). These are measurable from real system data (ticket timestamps, deployment logs) rather than self-reported estimates, and they expose problems — a growing queue at one stage, a lead time that's crept from 5 days to 20 — well before a project's nominal deadline arrives to reveal the trouble.

## Pros
- Converts an unmanageable pile of "projects" into a single, measurable pipeline, making bottlenecks and queues visible instead of hidden inside individual teams' private tracking.
- Replaces unreliable self-reported "percent complete" with objective flow metrics (lead time, throughput, queue depth) drawn from real system timestamps.
- Surfaces cross-team costs of local optimization (like the ops team's batched deployment window) that project-based views structurally cannot see.

## Cons
- Requires instrumentation and discipline most organizations don't already have (timestamped stage transitions, a shared definition of "done" per stage) — building this visibility is itself real, unglamorous work.
- Value-stream thinking can be uncomfortable politically, because it makes visible which team or stage is the actual bottleneck, which can feel like blame even when the goal is systemic, not personal (echoing `phoenix-project/01`'s caution against confusing the two).
- A value stream map is a snapshot; systems drift, and a map that isn't periodically re-validated against real data becomes a stale artifact that misleads rather than informs.

## Alternatives
- **Project portfolio management** — track work as a set of independent projects with their own budgets, timelines, and percent-complete status; simpler to set up and familiar to most organizations, but structurally blind to cross-team queueing and end-to-end lead time, which is exactly the blind spot that produced Parts Unlimited's crisis.
- **Kanban board per team** — each team visualizes its own work-in-progress; a real improvement over pure project tracking, but still fragments the picture unless boards are explicitly linked into one end-to-end value stream (a common mid-maturity state: good local visibility, no global visibility).
- **Full value stream mapping (Lean manufacturing practice)** — the complete, formal version of this lesson's technique, borrowed directly from Lean manufacturing (documenting every stage, every handoff, every wait time with real timestamped data); more rigorous and more effort than the lightweight tracing described above, and the version this lesson is a software-adapted subset of.

## When to use it
Use value-stream thinking whenever delivery feels slow or unpredictable but nobody can point to a single cause — it's the diagnostic step before you can apply Theory of Constraints (`phoenix-project/03`) or WIP limits (`phoenix-project/04`), because both require knowing where work actually queues. It's especially valuable when work crosses team boundaries (dev, security, ops, DBAs), since that's exactly where local optimization tends to damage the whole.

## When NOT to use it
Skip formal value-stream mapping for small, single-team efforts where the whole path from idea to production is already visible to everyone involved and queueing simply isn't a problem — the overhead of mapping and instrumenting flow isn't worth it at that scale. It's also not a substitute for the deeper prioritization and constraint-management work (`phoenix-project/03`, `phoenix-project/04`) — mapping the flow tells you where the problem is, but doesn't by itself fix it.

## Key takeaways / mental model
Trace one real unit of work, end to end, and measure elapsed time at every stage versus active work time at every stage. The gap between those two numbers is where your organization's real capacity is being lost, and it is almost always in queues between teams, not in anyone's individual work speed. This is operationalized into concrete delivery-pipeline practice in `devops-handbook/02` (value stream mapping) and `devops-handbook/03` (small batch sizes).

## Self-check questions
1. A team reports the Phoenix Project is "85% complete" for the third month running. What flow-based questions would you ask instead to get an honest picture of progress?
2. In the deployment-window worked example, the ops team's batching decision looked locally responsible but damaged the end-to-end value stream. Describe a decision from your own experience where local optimization by one team plausibly hurt a different team's or the overall system's flow.
3. Why is lead time usually dominated by wait time rather than active work time? What does that imply about where an engineering leader should spend improvement effort?
4. A change crosses four teams (dev, security, DBA, ops) before reaching production, and no single person can currently describe its full path. What is the first concrete step you'd take to make that value stream visible?

## References
- The Phoenix Project (Kim, Behr, Spafford), Part 1.
- See also `phoenix-project/03` (Theory of Constraints for IT operations) and `devops-handbook/02` (value stream mapping for software delivery), which operationalize this concept into concrete practice.
