---
id: devops-handbook/10
subject: devops-handbook
title: "Telemetry Foundations: Logs, Metrics, Traces, and Events"
slug: telemetry-foundations
status: drafted
mastery:
seniority: mid
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part IV
prerequisites: [devops-handbook/06]
created: 2026-08-10
updated: 2026-08-10
---

# Telemetry Foundations: Logs, Metrics, Traces, and Events

## TL;DR
Telemetry is the raw material the Second Way (fast feedback) runs on: logs (discrete records of what happened), metrics (aggregated numeric measurements over time), traces (the path of a single request across services), and events (significant state changes) each answer a different kind of question, and a production system needs all four to be genuinely observable rather than merely monitored.

## The idea
`devops-handbook/01` established that the Second Way requires feedback to flow from production back to the people who can act on it, fast. Telemetry is the concrete infrastructure that makes that feedback possible at all — without it, "how is production doing" is answered by guesswork or by waiting for a customer complaint. But not all telemetry answers the same question, and teams that collect only one type (commonly: just logs, or just a few high-level metrics) find themselves telemetry-rich but insight-poor, because the question they actually need answered ("why is this specific request slow") requires a type of data they never captured.

## How it works

### The four types and what each one is actually for
- **Logs** — discrete, timestamped records of specific events ("user 4521 login failed: invalid password, 14:32:07"). Best for answering "what exactly happened, in detail, at this specific point." Weak for answering aggregate questions ("how often does this happen") without additional processing.
- **Metrics** — numeric measurements aggregated over time (request count, error rate, p99 latency, CPU utilization, sampled every 10-60 seconds). Best for answering "how is the system doing right now, and how does that compare to a minute/hour/day ago" and for driving dashboards and alerts cheaply at scale. Weak for answering "why" — a metric shows *that* latency spiked, not which specific request or code path caused it.
- **Traces** — the recorded path of a single request as it flows through multiple services, with timing at each hop. Best for answering "where, in a multi-service call chain, did this specific slow or failed request spend its time." Weak (and expensive) if you try to trace every single request at high volume — usually sampled.
- **Events** — records of significant, discrete state changes worth correlating against everything else (a deploy happened, a feature flag flipped, an autoscaling event fired, a config changed). Best for answering "what changed right before this problem started" — the connective tissue that turns "latency spiked at 14:32" into "latency spiked at 14:32, two minutes after deploy #4521 went out."

### Worked example — using all four together to diagnose an incident
A dashboard metric shows p99 checkout latency jumped from 200ms to 1400ms at 14:30. That metric alone tells you *that* something's wrong and roughly *when* — but not *why* or *where*. Cross-referencing the **events** stream shows a deploy landed at 14:28, two minutes earlier — a strong first suspect. Pulling a **trace** for one of the slow requests shows the extra time is being spent in a call to the inventory service, not in checkout's own code. Searching the **logs** for that specific time window and service shows repeated "connection pool exhausted" errors from the inventory service. Put together: the 14:28 deploy (event) introduced a change that exhausts the inventory service's connection pool (log detail) under load, visible as elevated checkout latency (metric) specifically in the inventory-service hop of the request path (trace). No single telemetry type would have gotten you to that root cause alone — the metric found *that* something broke, the event found *when and likely why*, the trace found *where*, and the log found the *specific mechanism*.

### Cardinality and cost: why you can't just "log everything"
A common early mistake is treating telemetry collection as free and logging/tracing everything at maximum verbosity. In practice, high-cardinality data (a metric labeled per individual user ID, rather than aggregated) and full-volume tracing at high request rates both carry real storage and processing cost, and can even degrade the performance of the system being measured. The practical discipline: metrics stay low-cardinality and always-on (a handful of well-chosen dimensions: service, endpoint, status code); traces are sampled (e.g., 1% of normal traffic, but 100% of errors and slow requests — "tail-based sampling" that keeps the interesting cases); logs are structured (machine-parseable key-value fields, not free-text strings) so they're cheaply searchable later, but with retention policies that age out routine noise faster than diagnostic-relevant logs.

### Structured vs. unstructured logging — a small but consequential design choice
Unstructured: `"User 4521 failed login at 14:32:07 from IP 10.2.3.4"` — readable by a human, painful to query at scale ("show me all failed logins from this IP range in the last hour" requires regex parsing). Structured: `{event: "login_failed", user_id: 4521, ip: "10.2.3.4", ts: "14:32:07"}` — instantly queryable, aggregable, and joinable against other structured data, at the modest cost of being slightly less pleasant to eyeball directly in a raw file. The Handbook's practical recommendation is to log in structured form by default in any system past a small scale, specifically because it's what makes the "how often does this happen across the whole fleet" class of question answerable without ad hoc scripting.

## Pros
- Together, the four telemetry types let you answer both the "what/when" question (metrics, events) and the "why/where" question (traces, logs) that neither answers alone.
- Structured, well-designed telemetry is the concrete infrastructure the Second Way's feedback loop depends on — without it, `devops-handbook/11` and `devops-handbook/12` have nothing reliable to build on.
- Correlating events (deploys, flag flips) against metrics turns "something broke around 2:30" into "something broke two minutes after this specific deploy," collapsing diagnosis time dramatically.

## Cons
- High-cardinality metrics and unsampled full-volume tracing carry real cost (storage, query performance, and sometimes measurable overhead on the system being observed) if not deliberately managed.
- Telemetry sprawling across multiple disconnected tools (metrics in one system, logs in another, traces in a third, with no shared identifiers to correlate them) recreates the "insight-poor despite data-rich" problem this lesson describes, just with more tooling.
- Collecting the right telemetry requires instrumenting code deliberately (adding trace spans, structured log fields, meaningful metric labels) — it's not free by default, and retrofitting it onto an already-large system is real, ongoing work.

## Alternatives
- **Logs-only monitoring** — the common starting point for many systems; cheap to start, but structurally can't answer aggregate "how is the system doing overall right now" questions without significant post-hoc processing, which is exactly why metrics exist as a complementary type, not a replacement.
- **APM (application performance monitoring) suites** — commercial platforms that bundle metrics, traces, and sometimes logs into one correlated tool; trades some flexibility and cost control for integration convenience and faster time-to-value than assembling telemetry pipelines from separate open tools.
- **Synthetic monitoring (scripted, periodic probes of key user flows)** — a complementary, not competing, practice: catches "is the service even reachable and functioning" from an outside-in perspective, independent of the inside-out telemetry types this lesson covers.

## When to use it
Instrument all four telemetry types deliberately for any production service beyond a trivial scale — the marginal cost of adding structured logs, a few well-chosen metrics, and sampled tracing at build time is far lower than retrofitting them during an active incident when you discover you can't answer "why."

## When NOT to use it
Don't chase maximum telemetry volume/cardinality as a goal in itself — a system drowning in unsampled traces and high-cardinality metrics that nobody can afford to query effectively is worse in practice than a smaller, well-curated, cheaply-queryable telemetry set. Don't treat any single telemetry type as sufficient on its own; a team that only has dashboards (metrics) and no traces or structured logs will hit a wall the first time they need to know *why*, not just *that*.

## Key takeaways / mental model
Metrics tell you *that* and *when* something's wrong, cheaply, at scale. Events tell you *what changed* right before it. Traces tell you *where* in a multi-service path the problem lives. Logs tell you the *specific mechanism*. A genuinely observable system needs all four working together and cross-referenced by shared identifiers (timestamps, request IDs, deploy IDs) — not just more of any single one.

## Self-check questions
1. Using the checkout-latency incident example, explain what would have been missing from the diagnosis if the team had only metrics and logs, with no events stream and no tracing.
2. Why does the lesson argue that "just log everything at maximum detail" is not actually a safe default, despite seeming like the most thorough option?
3. Explain the practical difference between structured and unstructured logging, and why the difference matters more as a system's request volume grows.
4. A team has excellent dashboards (metrics) but no distributed tracing. Describe a realistic incident scenario where that gap would specifically prevent them from finding the root cause quickly.

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part IV: "The Second Way: Technical Practices of Feedback."
- See also: `devops-handbook/11` (monitoring and alerting, built on top of this telemetry) and `sre/*` (Google's SRE treatment of SLIs derived from the same telemetry foundations).
