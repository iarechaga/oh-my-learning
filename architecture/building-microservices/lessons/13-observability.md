---
id: building-microservices/13
subject: building-microservices
title: "Observability: Logs, Metrics, Tracing, Correlation IDs"
slug: observability
status: drafted
mastery: 
seniority: mid
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 10"
prerequisites: [building-microservices/06]
created: 2026-08-10
updated: 2026-08-10
---

# Observability: Logs, Metrics, Tracing, Correlation IDs

## TL;DR
A single user request in a microservices system can pass through many services, so understanding what happened requires stitching together signal from all of them — this is what a **correlation ID**, generated once at the entry point and passed through every downstream call, makes possible. The **three pillars** — logs, metrics, and traces — plus centralized log aggregation and distributed tracing move from "nice to have" in a monolith to operational necessities in a microservices system, because a single process's local logs and stack traces no longer tell the whole story.

## The idea
In a monolith, if a request fails, you look at one process's logs, maybe attach a debugger, and see the whole call stack from entry to error in one place. Once that same request is decomposed into calls across `api-gateway` → `order-service` → `payment-service` → `inventory-service` (Lesson 05, Lesson 06), a failure or a slow response could originate in any one of those services, and no single service's local logs show the whole picture — each only sees its own slice of the request.

This is the central problem observability tooling in microservices exists to solve: **how do you reconstruct "what happened to this one request" when the answer is scattered across N independently-deployed, independently-logging services?** Without deliberate tooling, debugging a production issue becomes "log into four different services' dashboards, guess at rough timestamps, and try to manually correlate entries that might be related" — slow, error-prone, and it gets worse as the service count grows. Newman is direct that observability tooling here is not a luxury or a "mature org" nice-to-have — it's baseline infrastructure a microservices system needs from early on, because the debugging pain it solves shows up immediately, not just at scale.

## How it works

### The three pillars: logs, metrics, traces

**Logs** — discrete, timestamped records of specific events ("order 4471 created," "payment authorization failed: card declined"). Good for detailed, ad hoc investigation of a specific event or error, but hard to use alone for understanding trends or cross-service flows unless aggregated and correlated (below).

**Metrics** — numeric measurements aggregated over time (request rate, error rate, latency percentiles, queue depth). Good for dashboards, alerting, and spotting trends ("error rate on `payment-service` has climbed from 0.1% to 4% over the last 10 minutes") but don't, by themselves, tell you the detailed story of any *individual* request.

**Traces** — a record of a single request's journey across multiple services, showing each service it touched, how long each hop took, and how the hops relate (sequential, parallel, nested). This is the pillar that's genuinely new in importance for microservices — in a monolith, a stack trace already shows you this within one process; in a distributed system, you need dedicated tooling (distributed tracing) to reconstruct the equivalent view across process and network boundaries.

Together, the three pillars answer different questions: metrics tell you *something is wrong and roughly where* (which service, which endpoint), traces tell you *the path a specific failing or slow request took*, and logs tell you *the detailed story at each specific point* along that path. You typically need all three together to go from "alert fired" to "root cause identified."

### Correlation IDs: the thread that ties it all together

A **correlation ID** is a unique identifier generated once, at the point a request first enters the system (e.g., at the API gateway, or at whichever service first receives an external request), and then explicitly propagated on every subsequent call the request triggers — passed as an HTTP header on synchronous calls, or embedded in the message/event payload on asynchronous ones (Lesson 06).

```
Client -> [api-gateway]      correlation-id: req-8f3a generated here
              |
              v
        [order-service]      correlation-id: req-8f3a  (passed through)
              |
              v
        [payment-service]    correlation-id: req-8f3a  (passed through)
              |
              v
        [inventory-service]  correlation-id: req-8f3a  (passed through)
```

Every service, when it logs anything related to handling this request, includes the correlation ID in that log line. The payoff: given a customer complaint ("my checkout failed around 2:15pm"), you find the relevant correlation ID (from the client, from an initial gateway log, or from a customer-facing error reference shown in the UI) and then query your centralized logging system (below) for every log line across every service carrying that exact correlation ID — instantly reconstructing the full, cross-service story of that one request, in order, without needing to guess at timestamps or manually cross-reference dashboards.

Correlation IDs are cheap to implement (generate a UUID, pass a header, log it consistently) and disproportionately valuable — Newman treats consistent correlation ID propagation as close to non-negotiable baseline practice for any microservices system, precisely because the alternative (manual timestamp-based guessing across services) doesn't scale even to a handful of services, let alone dozens.

### Centralized log aggregation

If each service's logs stay on its own local disk or in its own isolated logging backend, correlation IDs alone don't help much — you'd still need to separately query N different systems. **Centralized log aggregation** (e.g., an ELK/OpenSearch-style stack, or a managed logging platform) ships every service's logs to one searchable, centralized store, so a single query — "show me every log line with `correlation-id: req-8f3a`" — returns the full cross-service picture in one place, ordered by time, regardless of which of the N services produced each line.

This is what turns correlation IDs from "a nice idea" into a genuinely fast, practical debugging tool: the correlation ID is the join key, and centralized aggregation is the infrastructure that makes querying across services on that key actually possible.

### Distributed tracing

Distributed tracing goes a step further than "search logs by correlation ID": it explicitly models a request's journey as a tree (or graph) of **spans** — each span representing one unit of work in one service (e.g., "`order-service` handling this request," "`order-service` calling `payment-service`," "`payment-service`'s database query") — with parent/child relationships and precise timing for each. A **trace** is the whole tree for one request, typically keyed by the same kind of correlation/trace ID described above (many tracing systems, like those built on OpenTelemetry, use "trace ID" as the standard term for exactly this correlation ID).

The payoff over log-searching alone: a trace visualization shows you, at a glance, exactly which hop in the chain took the most time (a slow `payment-service` database query, say) and how the hops relate (sequential vs. parallel calls), which is exactly the kind of picture you need to diagnose the latency-chaining problem from Lesson 06 — "why did this checkout take 3 seconds?" is answered directly by looking at which span in the trace was slow, rather than manually reasoning about timestamps across separate log entries.

```
Trace req-8f3a  (total: 340ms)
  api-gateway            [====================================] 340ms
    order-service        [==============================]       310ms
      payment-service    [==============]                        140ms
        db-query               [========]                         80ms
      inventory-service               [========]                  80ms
```

(Here, `payment-service` and `inventory-service` were called in parallel by `order-service`, and `payment-service`'s database query was the single largest contributor to overall latency — exactly the kind of insight a trace view surfaces immediately that separate per-service logs would not.)

### Worked example: diagnosing a slow checkout

A customer reports checkout is slow. Without observability tooling: an engineer manually checks `order-service`'s dashboard (looks fine), then `payment-service`'s (looks fine), then `inventory-service`'s (looks fine) — because none of them individually show a problem in their own aggregate metrics, even though *this specific customer's* request was slow due to an unlucky combination (a slow database connection acquisition in `payment-service` that only affected a handful of requests, not enough to move the aggregate metric).

With observability tooling: the customer's error page shows a reference ID (the correlation ID). The engineer queries centralized logs for that ID, finds it took 3.1 seconds spanning `api-gateway` → `order-service` → `payment-service`, and — better still — pulls up the distributed trace for that exact request, immediately seeing that 2.6 of the 3.1 seconds were spent in a single span: `payment-service`'s database connection acquisition. The root cause is identified in minutes from one query, rather than hours of guessing across dashboards that each individually looked healthy.

## Pros
- **Correlation IDs** make it possible to reconstruct one request's full cross-service story, cheaply, and are simple to implement.
- **Centralized log aggregation** turns per-service logs into a single, queryable source of truth across the whole system.
- **Distributed tracing** shows exactly where time is spent and how services relate for a specific request, directly diagnosing the latency-chaining problem from Lesson 06.
- **Metrics and dashboards** catch systemic trends and drive alerting before an individual customer even reports an issue.

## Cons
- **Real infrastructure and ongoing cost** — running a centralized logging stack and a tracing backend, and instrumenting every service consistently, is nontrivial engineering and operational investment.
- **Requires discipline across every service and every team** — a single service that forgets to propagate the correlation ID, or logs inconsistently, breaks the chain for any request that passes through it.
- **Trace/log volume at scale is expensive** — sampling strategies (tracing only a percentage of requests, or 100% of errors and a sample of successes) are often necessary to keep storage and query costs manageable, which trades some completeness for cost.

## Alternatives
- **Per-service local logging with manual timestamp correlation** — the default absent any deliberate tooling; workable at very small scale (one or two services) but breaks down quickly as service count and traffic grow — this is precisely the pain observability tooling exists to eliminate.
- **APM (Application Performance Monitoring) platforms** — commercial, often more turnkey alternatives (or complements) to a self-hosted ELK/tracing stack, bundling logs, metrics, and tracing with less setup effort at the cost of vendor lock-in and often higher direct cost.

## When to use it
- From early in any microservices system's life — correlation IDs and basic centralized logging are cheap enough to build in from the start, and the debugging pain they solve appears immediately, not just "at scale."
- Distributed tracing becomes especially valuable once request chains regularly span 3+ services, where log-searching alone starts to require real manual reconstruction effort.

## When NOT to use it
- A very small, single-service (or two-service) system genuinely doesn't need the full centralized-aggregation/tracing infrastructure yet — local logs may be entirely adequate; but design in correlation ID propagation from the start anyway, since it costs almost nothing early and saves a painful retrofit later.

## Key takeaways / mental model
A microservices request is a relay race, not a solo sprint — no single service sees the whole thing, so you need a baton (the correlation ID) that's passed through every hand-off, and a finish-line camera (centralized logs plus distributed tracing) that can replay the whole race from that baton alone. Metrics tell you something's wrong and roughly where; a trace, keyed by the correlation ID, tells you exactly which hop was slow or failed; logs, joined on the same ID, give you the detailed story at each point. Build this in from early — it is baseline infrastructure, not a later-stage optimization.

## Self-check questions
1. Why doesn't a single service's local logs, however detailed, tell you the full story of a request that failed in a different, downstream service?
2. What is a correlation ID, where is it generated, and what specifically breaks if one service in the chain forgets to propagate it?
3. In the slow-checkout worked example, why did each individual service's own dashboard look healthy even though the customer's specific request was slow? What tool made the actual root cause visible?
4. What's the difference between what a metric tells you and what a distributed trace tells you, and why do you typically need both to fully diagnose a production issue?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 10: "Testing" and Chapter 11: "From Monitoring to Observability" (correlation ID, log aggregation, and distributed tracing discussion)
- Related: `system-design/15` (Observability) for the RED/USE methods and SLO/error-budget framing at the system-design level; `building-microservices/06` for the latency-chaining problem distributed tracing is used to diagnose.
