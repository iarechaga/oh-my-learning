---
id: devops-handbook/11
subject: devops-handbook
title: Production Monitoring and Actionable Alerting
slug: monitoring-actionable-alerting
status: drafted
mastery:
seniority: senior
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part IV
prerequisites: [devops-handbook/10]
created: 2026-08-10
updated: 2026-08-10
---

# Production Monitoring and Actionable Alerting

## TL;DR
Monitoring turns telemetry (`devops-handbook/10`) into human attention; good monitoring alerts on symptoms that matter to users (not every internal fluctuation), routes each alert to whoever can actually act on it, and treats every alert that didn't require action as a bug in the alerting rule, not a tolerable false positive.

## The idea
Collecting telemetry is necessary but not sufficient — a system generating perfect metrics, traces, and logs that nobody looks at until a customer complains has the same practical blind spot as a system with no telemetry at all. Monitoring is the layer that decides which telemetry signals deserve a human's attention, when, and whose. Get this wrong in either direction and it fails: too little/too coarse monitoring misses real problems until customers report them; too much/too noisy monitoring buries real problems under alert fatigue, where engineers learn to ignore pages because most of them turn out to be nothing — arguably worse than no monitoring, because it creates false confidence that someone's watching.

## How it works

### Symptom-based alerting vs. cause-based alerting
The single highest-leverage design decision in alerting: alert on symptoms that directly affect users (elevated error rate, elevated latency, failed transactions) rather than on every possible internal cause (CPU at 85%, one of 12 replicas restarted, disk at 70%). Cause-based alerts generate noise because many internal fluctuations are self-healing or don't actually affect users — a CPU spike that autoscaling absorbs within 30 seconds shouldn't page anyone. Symptom-based alerts stay quiet exactly when nothing user-visible is wrong, even if internal metrics are fluctuating, and fire precisely when something a user would notice is actually happening.

**Worked example.** A service has 12 replicas; one restarts due to a routine deploy. A cause-based alert ("a replica restarted") fires immediately — but users noticed nothing, because the other 11 replicas absorbed the load with no error-rate increase. A symptom-based alert ("error rate > 1% for 5 minutes" or "p99 latency > 800ms for 5 minutes") stays silent, correctly, because nothing user-visible happened. If instead 8 of the 12 replicas failed simultaneously and error rate climbed to 15%, the symptom-based alert fires immediately and accurately — which is exactly the situation worth waking someone up for.

### Alert routing and ownership: getting feedback to the right person
The Handbook connects this directly to `devops-handbook/12`: an alert is only useful if it reaches someone who can act on the specific problem, ideally the team (or engineer) whose recent change is most likely responsible. A centralized ops team receiving every alert for every service, regardless of who owns the code, reproduces the slow, context-poor feedback loop the Second Way is meant to eliminate — that team has to escalate to the actual owning engineer anyway, adding a delay, and the owning engineer never develops the direct, painful feedback connection between their changes and production behavior that drives improvement.

### The alert-quality feedback loop: every noisy alert is a bug
A mature monitoring practice treats every page that didn't require a real action as a defect in the alerting rule, tracked and fixed with the same seriousness as a code bug — not shrugged off as "monitoring is just noisy." Teams that track this explicitly (a running ratio of "pages that led to real action" vs. "pages that were false alarms or self-resolved") can see alert quality as a measurable, improvable property, rather than an unavoidable cost of having monitoring at all.

**Worked example — tuning a noisy alert.** A "disk usage > 80%" alert fires every few days, and on investigation, the disk always self-heals within minutes as a routine log-rotation job runs — no human action was ever needed. Rather than accepting this as background noise, the team either raises the threshold (90%, since 80% never actually predicted a real problem), changes it to alert only if usage stays above 80% for 30+ minutes (filtering out the self-healing case), or removes it entirely in favor of a symptom-based alert on the actual failure mode disk exhaustion would eventually cause (write failures). Any of these converts a routinely-ignored alert into either a real signal or silence — both better than noise.

### Dashboards: designed for a specific question, not a wall of everything
Good dashboards are built around a specific audience and question ("is checkout healthy right now" for an on-call engineer; "how is delivery trending this quarter" for a director) rather than displaying every available metric on one screen. A dashboard trying to serve every audience at once typically serves none of them well — the on-call engineer has to hunt through irrelevant panels during an incident, and the director has to interpret raw operational metrics that don't map to business outcomes.

**Worked example — an on-call dashboard.** A well-designed on-call dashboard for a checkout service shows, at a glance: current error rate vs. its normal baseline, p50/p99 latency vs. baseline, request volume, and a timeline of recent deploys and flag changes overlaid on the same time axis (connecting directly to `devops-handbook/10`'s events). During an incident, the engineer can see in one screen whether the problem correlates with a recent change, without switching between five different tools.

## Pros
- Symptom-based alerting keeps the signal-to-noise ratio high, which preserves engineers' trust in alerts and their willingness to respond promptly.
- Routing alerts to the owning engineer, not a generic ops queue, closes the feedback loop fast enough for the engineer to actually learn from and fix the underlying issue (feeding `devops-handbook/12`).
- Treating every false-positive page as a bug to fix creates a continuously improving alerting system instead of a permanently noisy one.

## Cons
- Symptom-based alerting requires knowing, in advance, what "user-visible harm" looks like for each service — some novel failure modes won't map cleanly to an existing symptom threshold and may go undetected until a new alert is designed after the fact.
- Alert tuning is genuinely ongoing work; a set-and-forget alerting configuration decays into noise (as usage patterns and system behavior shift) or blind spots (as new failure modes emerge) without regular review.
- Routing every alert to the specific owning engineer requires clear service ownership boundaries — in systems with murky or shared ownership, this practice breaks down into "who do we even page" ambiguity during an incident.

## Alternatives
- **Cause-based (internal-metric) alerting as the primary strategy** — the direct alternative this lesson argues against as a primary approach; still useful as a secondary, lower-urgency signal (e.g., a non-paging warning) for catching problems before they become symptom-visible, but poor as the primary paging mechanism due to noise.
- **Centralized NOC (network operations center) triage** — a human team watches dashboards and manually decides who to escalate to; can work at very large scale with dedicated staffing, but reintroduces a slower, more indirect feedback path than direct routing to owning engineers.
- **SLO-based alerting with error budgets** (see `sre/03`, `sre/04`) — a more formalized, statistically grounded version of symptom-based alerting: alert based on the rate of error-budget consumption relative to a defined objective, rather than a fixed threshold — a natural next step once symptom-based alerting is established.

## When to use it
Design alerting around user-visible symptoms and route directly to owning engineers for any production service where a delayed or ignored real incident has meaningful cost — which is nearly every production service serving real traffic.

## When NOT to use it
Don't alert on every internal metric fluctuation "just in case" — that's precisely the anti-pattern that produces alert fatigue and erodes trust in the whole system. Don't route every alert to a centralized team by default if service ownership is clear enough to route directly — the extra hop costs time and weakens the engineer's direct feedback connection to their own changes.

## Key takeaways / mental model
Ask of every alert: "if this fires and nobody does anything different because of it, was the alert wrong?" If the honest answer is usually yes, it's a symptom of a badly tuned rule, not an acceptable cost of monitoring — treat it as a bug and fix it with the same rigor as a code defect.

## Self-check questions
1. Using the replica-restart example, explain concretely why a cause-based alert fires in a situation a symptom-based alert correctly stays silent for, and why that difference matters for on-call sustainability.
2. Why does routing an alert to a centralized ops team, rather than the owning engineer, weaken the Second Way's feedback loop specifically, not just add latency?
3. Describe the process this lesson recommends for handling a chronically noisy alert. Why is "just ignore it, we know it's nothing" the wrong response even when the team is usually right that it's nothing?
4. Design (in prose) two alerts for a hypothetical payments service — one that should page immediately and one that should only generate a non-paging warning — and justify the difference using the symptom-based framing.

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part IV: "The Second Way: Technical Practices of Feedback."
- See also: `devops-handbook/10` (telemetry foundations this monitoring is built on) and `sre/07` (Google SRE's parallel treatment of monitoring and alerting design).
