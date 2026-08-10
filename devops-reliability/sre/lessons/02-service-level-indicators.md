---
id: sre/02
subject: sre
title: "Service Level Indicators (SLIs): Measuring User-Visible Behavior"
slug: service-level-indicators
status: drafted
mastery:
seniority: mid
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 4
prerequisites: [sre/01]
created: 2026-08-10
updated: 2026-08-10
---

# Service Level Indicators (SLIs): Measuring User-Visible Behavior

## TL;DR
A Service Level Indicator (SLI) is a carefully specified, quantitative measure of some aspect of the service that users actually experience — usually expressed as a ratio of good events to total valid events. Getting the SLI definition right (what counts as "good," what counts as "valid," measured where) is the foundation everything else in this subject — SLOs, error budgets, alerting — is built on; a sloppy SLI makes every downstream number meaningless.

## The idea
Every service emits huge amounts of telemetry: CPU usage, queue depth, GC pauses, disk I/O, request counts. Almost none of it is what the user actually cares about. A user doesn't know or care that CPU is at 85%; they care whether their request came back correctly and quickly. An SLI is the deliberate act of picking the small number of measurements that actually represent user-perceived quality, out of the much larger pile of things you *could* measure.

This matters because everything downstream depends on the SLI being right. An SLO (`sre/03`) is a target drawn on an SLI. An error budget (`sre/04`) is computed from how much the SLI has missed its SLO. An alert (`sre/07`) fires based on the SLI trending toward budget exhaustion. If the SLI measures the wrong thing — say, server-side error rate instead of what the client actually received — every one of those downstream mechanisms will faithfully compute nonsense with high confidence.

## How it works

### The canonical form: good events / valid events
Most SLIs are expressed as a ratio:

```
SLI = (number of "good" events) / (number of valid events) x 100%
```

Two decisions do all the work here: what counts as a "good" event, and what counts as a "valid" event (the denominator). Get either wrong and the ratio is meaningless even though it's technically well-formed.

**Worked example — availability SLI for an HTTP API.**
- Valid events: all HTTP requests that reached the load balancer and were not client-caused errors (e.g., excludes malformed requests with 4xx from bad client input, but includes everything the server was responsible for).
- Good events: requests that returned within SLA and with a non-5xx status code.
- If a service handled 10,000,000 valid requests in a day and 9,991,000 were good, the daily availability SLI is 9,991,000 / 10,000,000 = **99.91%**.

Note what's *not* in that number: requests measured only at the server, not the client. If the load balancer itself drops connections before they reach the server, a server-side-only SLI will report 100% availability while users see failures. This is why the book pushes hard on **measuring as close to the user as possible** — client-side or edge/load-balancer measurement over server-side application logs, whenever feasible.

### The four most common SLI categories
1. **Availability** — the fraction of time or requests the service was usably up. Usually `successful requests / total requests`.
2. **Latency** — the fraction of requests served faster than some threshold. Usually expressed as a percentile: "99% of requests complete in under 300ms," not an average (averages hide a bad tail; see the worked example below).
3. **Throughput/quality** — for pipeline or batch systems, the fraction of records processed correctly and on time, e.g. "99.5% of data-processing jobs complete within their scheduled window."
4. **Freshness** — for data or caching systems, the fraction of served data that is within an acceptable staleness bound, e.g. "99% of cached responses are less than 60 seconds old."

**Worked example — why percentiles, not averages, for latency.** Suppose a service serves 1,000 requests/minute: 950 of them in 50ms and 50 of them (the slow tail, often caused by cache misses, GC pauses, or retries) in 4,000ms. The mean latency is (950x50 + 50x4000)/1000 = 247.5ms — looks fine. But the p95 (the 950th-fastest request out of 1,000, sorted) is right at the boundary between fast and slow, and the p99 is deep in the slow tail at ~4,000ms. A latency SLI defined as "average response time" would completely hide that 5% of users are having a terrible experience; a percentile-based SLI ("95% of requests < 100ms") catches it immediately. This is why SRE practice almost always defines latency SLIs on percentiles (p50/p95/p99), never on the mean.

### Where you measure changes what you're actually measuring
Consider a mobile app calling a backend API through a CDN, a load balancer, and finally the application server. You could measure the SLI at any of these points:
- **Server-side application logs** — cheapest to instrument, but blind to anything that fails before the request reaches the app (DNS failures, TLS handshake failures, load-balancer 502s, client network drops).
- **Load balancer / edge logs** — captures more of the real failure surface, including requests that never reached the app tier.
- **Client-side instrumentation** — the most accurate representation of actual user experience (captures client-side rendering delays, retries, and network conditions the server never sees), but the most expensive to build and the least reliable to collect (client SDKs can be blocked, batched, or lost on flaky networks).

The book's guidance: pick the measurement point that best approximates the user's actual experience given your budget, and be explicit in the SLI's definition about which point you chose — because two teams both claiming "99.9% availability" measured at different points are not comparable and will produce false confidence if conflated.

### Aggregation window and its effect on visibility
An SLI is always computed over a window (e.g., a rolling 5 minutes, 1 hour, or 28 days). Short windows are noisy but responsive (useful for alerting); long windows are stable but slow to reflect real change (useful for SLO compliance and error-budget tracking, see `sre/03` and `sre/04`). A single spike of 100% failure for 10 seconds barely dents a 28-day SLI but should be highly visible in a 5-minute SLI — this is exactly why alerting (`sre/07`) uses multiple aggregation windows in parallel rather than relying on one number.

## Pros
- Forces precision: writing down exactly what counts as "good" and "valid" surfaces disagreements about what "reliable" even means before an outage, not during one.
- Makes reliability comparable and trackable over time, since it reduces a messy system to one or a few well-defined numbers.
- Directly measurable by instrumentation most services already have (request logs, response codes, timers) — no new infrastructure usually required to get started.

## Cons
- Easy to pick a convenient-but-wrong SLI (e.g., server-side-only measurement) that looks good on a dashboard while users are actually unhappy.
- Reducing a complex user experience to one ratio necessarily discards information; a single "availability" SLI can mask a bad experience for a specific user segment (e.g., one geographic region) while the aggregate looks healthy.
- Requires ongoing instrumentation investment and discipline to keep the SLI's definition accurate as the system architecture changes (a new caching layer, a new CDN hop) — a stale SLI definition silently drifts from what users actually experience.

## Alternatives
- **Raw infrastructure metrics (CPU, memory, disk)** — easier to collect, but not user-centric; a healthy CPU graph says nothing about whether users are being served correctly. Useful as a diagnostic signal downstream of an SLI-based alert, not as the primary reliability measure.
- **Synthetic monitoring / uptime pings** — a simple external prober hitting a health-check endpoint; cheap and catches gross outages, but usually too coarse to represent real user-mix traffic and doesn't capture latency degradation or partial failures the way a request-ratio SLI does.
- **Full distributed tracing per request** — richer than an aggregate SLI (see exact request paths and where time was spent), but expensive to store and query at scale; typically used to *diagnose* an SLI breach, not to define the SLI itself.

## When to use it
Define SLIs for every service that has an SLO or is on a support/on-call rotation — this is the prerequisite step before any of the target-setting, error-budget, or alerting machinery in this subject can work. Prioritize the metric closest to what the user directly experiences (request success, response latency) over internal system health metrics.

## When NOT to use it
Don't over-invest in perfectly precise client-side SLIs for a low-stakes internal tool where nobody is paged and no SLO is tracked — the instrumentation cost isn't justified. Also avoid defining an SLI you can't reliably and cheaply compute in near-real-time; an SLI that requires an expensive nightly batch job to compute can't drive alerting or the fast feedback loop this subject depends on.

## Key takeaways / mental model
An SLI answers one question precisely: "of the requests/events that mattered, what fraction were good, measured as close to the user as we can afford?" Every word in that sentence is a deliberate choice (what counts as mattering, what counts as good, where you measure) — get those choices wrong and every later number (SLO compliance, error budget, alert threshold) inherits the error silently.

## Self-check questions
1. A team defines its SLI as "percentage of HTTP 200 responses out of all requests reaching the application server." Identify two ways this SLI could report 100% while real users are experiencing failures.
2. Explain, with a numeric example, why a mean-latency SLI can hide a serious user-facing problem that a p99-latency SLI catches.
3. You're asked to define an SLI for a nightly batch ETL pipeline (no live HTTP traffic). What would "good event" and "valid event" mean in that context, and which of the four SLI categories does it fall under?
4. Two teams both report "99.95% availability" for services that call each other. One measures at the load balancer, the other measures client-side from a mobile app. Why can't you directly compare these two numbers, and what would you ask each team before trusting a combined SLA claim?

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 4 ("Service Level Objectives").
- See also: `sre/03` (Service level objectives) for how SLIs become targets, and `devops-reliability/devops-handbook` (forthcoming) for the broader telemetry/feedback-loop practices SLIs feed into.
