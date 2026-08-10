---
id: phoenix-project/04
subject: phoenix-project
title: WIP Limits and Reducing Multitasking Damage
slug: wip-limits-multitasking
status: drafted
mastery:
seniority: senior
source: The Phoenix Project (Kim, Behr, Spafford), Part 2
prerequisites: [phoenix-project/03]
created: 2026-08-10
updated: 2026-08-10
---

# WIP Limits and Reducing Multitasking Damage

## TL;DR
Starting more work in parallel feels like progress but, past a small number of concurrent items, it actively reduces total throughput: context-switching overhead compounds, everything's lead time grows, and nothing finishes. Limiting **work in process (WIP)** — capping how many items a person, team, or stage is allowed to have active at once — is the concrete mechanism for the "subordinate everything else to the constraint" step of Theory of Constraints (`phoenix-project/03`). At Parts Unlimited, uncapped WIP funneled onto Brent (and onto the whole organization generally) is what turns a bottleneck into a catastrophe.

## The idea
Multitasking on knowledge work is not like running two loads of laundry at once, where switching costs nothing. Every time an engineer switches from Task A to Task B, there's real cost to reload context — where was I, what was I about to do, what was the state of my reasoning — and that cost is paid again switching back to A. This isn't a minor inefficiency; it compounds nonlinearly as the number of concurrent tasks grows, because each additional task doesn't just add its own switching cost, it multiplies the number of possible switches between all tasks.

Parts Unlimited runs Brent, and effectively the whole IT organization, with no WIP limits: anyone can escalate anything to him at any time, every manager treats their own request as top priority, and Brent ends up mid-task on five things simultaneously, finishing none of them promptly, each one bleeding into the others' mental context. The book dramatizes this concretely — Brent is pulled from a Phoenix deployment crisis into a payroll emergency into a security incident, sometimes within the same hour, and *nothing* actually gets resolved quickly because he never has enough uninterrupted time on any one thing to finish it.

This lesson gives the concrete practice — a hard cap on concurrent work items — that turns ToC's "subordinate everything else to the constraint" from a principle into something you can actually enforce day to day.

## How it works

### Why multitasking cost is nonlinear, not linear
Imagine three independent tasks, A, B, and C, each of which takes exactly 10 hours of focused, uninterrupted work to complete.

**Sequential (WIP = 1):** A finishes at hour 10, B at hour 20, C at hour 30. Average time-to-completion across the three: (10+20+30)/3 = 20 hours.

**Fully interleaved (WIP = 3, switching every hour):** each task gets roughly equal attention, but none finishes until all three are nearly done — approximately hour 28-30 each, once you add realistic context-switch overhead (commonly cited estimates put switching cost at 15-20+ minutes of degraded focus per switch; even a conservative 10% overhead per switch matters at this frequency). Average time-to-completion: roughly 29 hours instead of 20 — every task finishes *later* on average, and the first task to actually deliver value (A) finishes dramatically later (29 vs. 10 hours) even though total *work* didn't increase.

This is the core, often-surprising result: **interleaving doesn't just cost some fixed overhead — it delays every single task's completion, including the ones that would have finished first if left alone**, while providing zero benefit unless something about the work genuinely requires parallel progress (rare for most engineering tasks).

### WIP limits as the enforcement mechanism
A WIP limit is a hard, visible cap: "this stage of the pipeline (or this person, or this team) may have at most N items actively in progress; a new item cannot start until an existing one finishes or is explicitly deprioritized." This is the mechanic behind Kanban boards' column limits, and it is what the book's fictional "Brent's queue" desperately needs and initially lacks.

**Worked example.** Suppose an SRE on-call rotation currently allows anyone in the company to directly Slack-message the on-call engineer with "quick questions," escalations, and non-incident requests, alongside actual incidents. On a typical day the on-call engineer has 1 real incident plus 6 "quick" interruptions, each costing roughly 20 minutes of context loss even when the interruption itself takes 5 minutes, because of the reload cost getting back into the incident. Introducing a WIP limit — a rule that the on-call engineer works exactly one thing at a time, with all non-incident requests routed to an async queue reviewed twice a day — doesn't reduce the total amount of work; it removes the interleaving tax. In this scenario, incident resolution time might drop from an observed 3 hours (constantly interrupted) to under 45 minutes (uninterrupted), and the 6 "quick questions" still get answered, just batched, without silently degrading incident response the whole time.

### Setting WIP limits in practice
A WIP limit has to be low enough to force explicit trade-off decisions, but not so low it starves a stage of work entirely. A common practical heuristic (borrowed from Kanban practice) is roughly one to two items in progress per person at any given stage — enough to avoid idle time while someone waits on a dependency, but far below the "10 things open at once" state that's common in unmanaged environments. The number should come from real observed queue and cycle-time data (per `phoenix-project/02`'s flow metrics), not a guess: if cycle time is high and WIP is high, tightening the limit and watching cycle time drop is direct evidence the limit was helping, not hurting.

**Worked example — the visible cost of exceeding it.** Parts Unlimited's Phoenix Project rollout fails partly because dozens of last-minute changes are crammed in simultaneously right before the deadline — nobody enforces a limit on how many in-flight changes the deployment can carry. Post-incident, tracing the failure shows the actual root cause wasn't any single change; it was that so many changes were in flight simultaneously that no one could reason about their combined interaction effects, and testing coverage per change effectively collapsed because attention was smeared across all of them. A WIP limit on "changes allowed in a single release" (a direct ancestor of `devops-handbook/03`'s small-batch-size discipline) would have forced explicit sequencing and made each change's risk individually assessable.

### The psychological resistance to WIP limits
The hardest part of introducing WIP limits is rarely mechanical — it's organizational. Refusing to start new work when someone senior asks for it, in favor of finishing what's already committed, requires real authority and a shared, visible agreement (ideally from leadership) that this is the policy, not a personal choice by the engineer being asked. Without that backing, WIP limits collapse under the first urgent-sounding request, exactly the failure mode Bill has to fight against repeatedly at Parts Unlimited as he tries to protect Brent's time.

## Pros
- Reduces the hidden, nonlinear tax of context-switching, improving both average completion time and the completion time of the *first* items to finish — a rare case where a constraint (the limit itself) makes the system faster, not slower.
- Makes overcommitment visible and forces explicit prioritization decisions ("if this WIP slot is full, what gets pushed out to make room?") instead of silent, invisible degradation of everything in flight.
- Directly operationalizes the ToC "subordinate" step (`phoenix-project/03`) by preventing new work from piling onto an already-saturated constraint.

## Cons
- Requires real organizational discipline and backing to hold the line when a senior stakeholder wants "just this one exception" — a WIP limit that bends under pressure provides no protection at all.
- Setting the limit too low starves a stage of work and creates idle time waiting on dependencies; setting it too high provides no real protection — tuning it takes real data and iteration.
- Visible WIP limits can create short-term political friction, since some requests will now visibly wait rather than being silently (and inefficiently) worked on in parallel — stakeholders used to "everything gets started immediately" may perceive the limit as a service degradation even though throughput improves.

## Alternatives
- **Prioritization without WIP caps** — rank work by priority but still allow unlimited concurrent starts; better than no prioritization at all, but doesn't prevent the interleaving tax, since low-priority items still get *started* and left half-finished, still costing context-switches.
- **Time-boxing/batching (e.g., fixed sprints)** — commit to a fixed set of work for a period and refuse new work mid-period; a related but coarser-grained control than a continuous WIP limit, common in Scrum, and useful when work arrives in genuinely batchable units.
- **Dedicated interrupt/on-call role** — assign one person (or a rotation) to absorb all unplanned interruptions so the rest of the team can maintain a stable WIP; a common real-world hybrid that combines with WIP limits rather than replacing them (this is the mechanism behind the SRE on-call worked example above).

## When to use it
Apply WIP limits wherever a person, team, or pipeline stage regularly has multiple items open simultaneously and cycle time is worse than expected given the actual work volume — the classic sign is "everyone is busy, nothing is finishing." It's especially critical at any identified constraint (`phoenix-project/03`), where uncapped WIP has the most damaging, compounding effect on total system throughput.

## When NOT to use it
Don't impose rigid WIP limits on genuinely independent, non-competing work that doesn't share a constrained resource or a person's attention — if two engineers on two unrelated projects with no shared dependency both have one item in progress each, there's no interleaving cost to manage. Also avoid using a WIP limit as an excuse to simply refuse urgent, genuinely critical work — the limit should trigger an explicit trade-off conversation (what gets deprioritized to make room), not a blanket refusal; a rule with no escape valve for real emergencies will be circumvented rather than respected.

## Key takeaways / mental model
Every item you start without finishing something else first is quietly taxing everything already in flight — multitasking doesn't add capacity, it subtracts it, and the tax grows faster than the number of tasks. Cap concurrent work explicitly, low enough to force real trade-off decisions, and treat "started but not finished" as a cost to be minimized, not evidence of productivity.

## Self-check questions
1. Using the sequential-vs-interleaved worked example, explain why the *first* task to complete finishes so much later under interleaving even though total work didn't change.
2. A team lead says "we can't set WIP limits, urgent requests come in constantly and we have to respond." How would you redesign the system (without simply ignoring urgent work) so WIP limits and urgent responsiveness coexist?
3. Why does a WIP limit need explicit organizational backing (not just a team's private agreement) to actually hold under pressure? What happens if it doesn't have that backing?
4. Given a pipeline stage with high WIP and high cycle time, how would you use flow data (per `phoenix-project/02`) to decide what the WIP limit should be, and how would you know afterward whether you set it correctly?

## References
- The Phoenix Project (Kim, Behr, Spafford), Part 2.
- See also `phoenix-project/03` (Theory of Constraints, which WIP limits operationalize) and `devops-handbook/03` (small batch sizes and limiting work in process), which extends this into concrete delivery-pipeline practice.
