---
id: building-microservices/14
subject: building-microservices
title: "Resilience: Timeouts, Retries, Bulkheads, Circuit Breakers"
slug: resilience
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 12"
prerequisites: [building-microservices/06]
created: 2026-08-10
updated: 2026-08-10
---

# Resilience: Timeouts, Retries, Bulkheads, Circuit Breakers

## TL;DR
Every synchronous call between services is a place where a slow or failing dependency can cascade upward and take down callers that were themselves working fine. **Timeouts** bound how long you wait; **retries with backoff and jitter** handle transient failures without causing a retry storm; **circuit breakers** stop calling a consistently failing dependency, giving it room to recover; **bulkheads** isolate resource pools so one failing dependency can't exhaust resources needed by unrelated calls. Together, these are the core toolkit for containing the failure-cascade risk that Lesson 06 identified as the central cost of synchronous inter-service communication.

## The idea
Lesson 06 established the mechanical problem: synchronous call chains compound latency and multiply unavailability, and a slow (not even down — just slow) downstream service can exhaust a caller's resources and cascade the failure upward, potentially bringing down services that have no bug of their own. This lesson is the toolkit for containing that risk, borrowing heavily from Michael Nygard's *Release It!* (a text Newman cites directly), which catalogued these patterns from real production outages.

The unifying idea behind every pattern here: **a service should assume its dependencies will sometimes be slow or unavailable, and should be designed to degrade gracefully rather than fail catastrophically when that happens.** In a monolith, a function call either returns or throws, quickly, because there's no network in between. In a microservices system, a "call" can hang indefinitely, return slowly, or fail in ways a function call never does — and code that doesn't explicitly account for this treats the network as if it were as reliable as a function call, which it never is.

## How it works

### Timeouts: bound how long you'll wait

The most basic and most important control: never call a dependency without a timeout. Without one, a caller waiting on a hung or extremely slow dependency will hold its own resources (threads, connections) indefinitely, and — exactly as in Lesson 06's worked example — those held resources eventually run out, causing the caller to fail even unrelated requests that had nothing to do with the slow dependency.

Setting the timeout value is itself a real design decision, not a default to leave at "whatever the HTTP client ships with" (which is often "no timeout" or an unreasonably long one): too short, and you abort calls that would have succeeded just a little later, generating unnecessary failures; too long, and you don't bound the damage fast enough. A reasonable starting point is based on the dependency's own observed latency distribution (Lesson 13's metrics/tracing tell you this directly) — e.g., set the timeout a bit above the dependency's p99 latency, then tune based on real production behavior, rather than guessing.

### Retries with backoff and jitter — and the retry storm danger

Many failures are transient — a momentary network blip, a brief GC pause on the other end — and simply retrying the call a moment later often succeeds. But a **naive retry** (retry immediately, in a tight loop, with no delay) is dangerous specifically *because* it's so easy to reach for: if a dependency is struggling because it's overloaded, every caller retrying immediately just adds more load to the already-struggling service, making the underlying problem worse, not better — this is a **retry storm**, and it has caused real, well-documented production outages where a retry mechanism turned a minor blip into a full outage.

The standard mitigation:
- **Exponential backoff** — wait progressively longer between retry attempts (e.g., 100ms, then 200ms, then 400ms, then 800ms), giving the struggling dependency increasing room to recover rather than hitting it again immediately.
- **Jitter** — add randomness to the backoff delay (e.g., a random value between 0 and the computed backoff, rather than the exact computed value) so that many callers who all started retrying at roughly the same moment (because they all just experienced the same failure) don't all retry again at exactly the same moment, which would just recreate a synchronized spike of load — jitter spreads the retries out in time instead of them landing in lockstep.
- **A retry limit** — cap the number of attempts; retrying forever is not resilience, it's a slow-motion resource leak and a way to keep amplifying load on a struggling dependency indefinitely.

**Worked example.** `order-service` calls `inventory-service`, which is momentarily overloaded and returning a 503. Without backoff/jitter: every one of `order-service`'s 200 concurrent request handlers retries after a fixed 50ms delay, all landing back on `inventory-service` at almost exactly the same instant — a synchronized spike that's just as bad as the original load, likely triggering another wave of failures and retries, compounding. With exponential backoff and jitter: each handler's retry delay is randomized around a growing base delay, so the 200 retries spread out over a window instead of landing as one spike, giving `inventory-service` genuine breathing room to work through its backlog and recover.

### Circuit breakers: stop calling a dependency that's clearly failing

Retries help with brief, transient blips, but they're the wrong tool when a dependency is failing *consistently*, not transiently — in that case, every retry is wasted effort that adds load to an already-struggling service and adds latency to the caller (who now waits through the retry attempts before ultimately failing anyway). The **circuit breaker** pattern (named after the electrical device) addresses this by tracking the failure rate of calls to a dependency and, once it crosses a threshold, "opening the circuit" — failing fast, immediately, without even attempting the call — for a cooldown period, then cautiously testing whether the dependency has recovered.

Three states:

```
        failures exceed threshold
   CLOSED  -------------------------->  OPEN
     ^                                    |
     |                                    | cooldown timer expires
     | success                            v
     +------------------  HALF-OPEN <-----+
                     (trial requests)
                failure -> back to OPEN
```

- **Closed** — normal operation; calls pass through to the dependency; the breaker tracks the failure rate.
- **Open** — the failure rate crossed the threshold; calls fail immediately (without even attempting the network call) for a cooldown period, giving the dependency room to recover and sparing the caller from wasting time/resources on calls very likely to fail anyway.
- **Half-open** — after the cooldown, the breaker allows a small number of trial calls through. If they succeed, the breaker closes (resumes normal operation); if they fail, it reopens and the cooldown restarts.

**Worked example.** `checkout-service` calls `recommendation-service` (a "customers also bought" widget) as part of building the checkout page. `recommendation-service` starts failing consistently due to an unrelated database issue. Without a circuit breaker, every checkout request still waits out the full timeout calling `recommendation-service` before falling back to a default, wasting real latency budget on calls almost certain to fail. With a circuit breaker: after a handful of consecutive failures, the breaker opens; for the next 30 seconds, `checkout-service` skips calling `recommendation-service` entirely and immediately uses a fallback (an empty or generic recommendations list) — checkout stays fast, and `recommendation-service` isn't burdened with load it can't currently handle. After 30 seconds, a trial call checks whether `recommendation-service` has recovered, and the breaker closes again once it has.

### Bulkheads: isolate resource pools

Named after the watertight compartments in a ship's hull — if one compartment floods, the bulkheads keep the flooding contained to that one section instead of sinking the whole ship. Applied to software: **isolate the resources (thread pools, connection pools) used to call different dependencies, so that one dependency's failure exhausting its own resource pool can't also exhaust the resources needed for calls to unrelated dependencies.**

**Worked example.** `order-service` calls both `payment-service` and `inventory-service`, and both share a single, undifferentiated pool of 50 outbound HTTP connections. `payment-service` becomes very slow (but not down); calls to it start holding connections for a long time. Because the connection pool is shared, all 50 connections can end up tied up waiting on the slow `payment-service`, leaving zero connections available for calls to the perfectly healthy `inventory-service` — `inventory-service` calls now fail too, not because anything is wrong with `inventory-service`, but purely because of shared resource exhaustion caused by an unrelated dependency. This is exactly the cascading-failure mechanism from Lesson 06, now traced to its resource-level root cause.

With bulkheads: `order-service` maintains *separate* connection pools — say, 25 dedicated to `payment-service` calls and 25 dedicated to `inventory-service` calls. Now `payment-service`'s slowness can exhaust its own 25-connection pool (calls to `payment-service` do start failing/queuing), but `inventory-service`'s dedicated 25-connection pool is completely unaffected — `inventory-service` calls keep succeeding normally. The failure is contained to the compartment it originated in, exactly as a ship's bulkheads contain flooding.

### How the patterns combine

These patterns are complementary, not alternatives to each other — a well-defended synchronous call typically uses several together: a timeout bounds each individual attempt; a small number of retries with backoff and jitter handle transient blips within that timeout budget; a circuit breaker stops attempting calls altogether once failures become persistent rather than transient; and bulkheads ensure that whatever resource cost this dependency's failure incurs stays contained to calls targeting that dependency, not shared with calls to unrelated, healthy dependencies.

## Pros
- **Timeouts** prevent indefinite resource holding on a hung dependency — the single most important, lowest-cost control.
- **Retries with backoff/jitter** recover from transient failures automatically without amplifying load into a retry storm.
- **Circuit breakers** stop wasting time and resources on calls very likely to fail, and give a struggling dependency room to recover.
- **Bulkheads** contain a dependency's failure to the resources dedicated to calling it, protecting calls to unrelated, healthy dependencies.

## Cons
- **Real implementation and tuning effort** — timeout values, retry counts/backoff parameters, circuit breaker thresholds, and bulkhead pool sizes all need to be chosen deliberately and revisited as traffic and dependency behavior change, not set once and forgotten.
- **Adds complexity to every call site** (or requires a shared library/service mesh to apply consistently) — inconsistent application across a codebase (some calls protected, others not) leaves gaps that undermine the whole strategy.
- **Fallback behavior needs real design thought** — "what do we show when the circuit is open?" (an empty state, a cached/stale value, a generic default) is a product decision, not just an engineering one, and a poorly chosen fallback can itself cause problems (e.g., silently showing stale pricing).

## Alternatives
- **Service mesh (e.g., sidecar-proxy based infrastructure)** — implements timeouts, retries, and circuit breaking at the infrastructure layer (a sidecar proxy alongside each service) rather than in each service's own application code, giving consistent behavior across the whole system without every team re-implementing the same logic — a common way to apply these patterns uniformly at scale, at the cost of additional infrastructure to run and operate.
- **Load shedding** — a related but distinct technique: rather than protecting a *caller* from a slow dependency, a service under heavy load deliberately rejects some incoming requests early (before doing expensive work) to protect its own capacity for the requests it can actually serve well; complementary to, not a replacement for, the caller-side patterns in this lesson.

## When to use it
- Every synchronous call between services should have, at minimum, an explicit, deliberately-chosen timeout — this is close to non-negotiable baseline practice.
- Retries with backoff/jitter for calls where transient failure is plausible and a brief delay is acceptable (most calls, though not all — see below).
- Circuit breakers for calls to dependencies whose availability genuinely varies and where "fail fast with a fallback" is preferable to "wait out the timeout every time."
- Bulkheads whenever a service calls multiple independent dependencies and you want one dependency's failure to not affect calls to the others.

## When NOT to use it
- Don't retry non-idempotent operations (e.g., "charge this payment") blindly without additional safeguards (idempotency keys) — a naive retry of a call that partially succeeded server-side but timed out on the client side can cause a duplicate charge; retries need to be paired with idempotency design for write operations, not applied uniformly to every call type.
- Don't set circuit breaker thresholds so aggressively that normal, brief blips trip the breaker constantly (a "flapping" circuit) — this can make a healthy dependency appear unavailable more often than it actually is, and needs tuning against real observed failure patterns (Lesson 13's metrics).

## Key takeaways / mental model
Treat every network call as something that can hang, fail slowly, or fail persistently — never assume it behaves like a local function call. Timeouts bound the damage of any single call; backoff-and-jitter retries absorb brief transient blips without piling on more load; circuit breakers stop wasting effort on a dependency that's clearly down, giving it room to recover; bulkheads make sure one dependency's trouble can't drain the resources needed for calls to a completely unrelated, healthy dependency. Used together, these are what actually let a system built from many networked services degrade gracefully instead of cascading into a full outage from one weak link.

## Self-check questions
1. Why is "no timeout" on a service-to-service call dangerous even if the dependency is only *occasionally* slow, not down?
2. Explain, using the retry-storm scenario, why naive retries without backoff and jitter can make an overloaded dependency's problem worse rather than better.
3. Walk through a circuit breaker's three states using the `checkout-service`/`recommendation-service` example — what triggers each transition?
4. Two services share one connection pool; a bulkhead pattern splits it into two dedicated pools. What specific failure mode does this prevent, and why doesn't a shared pool prevent it?
5. Why shouldn't you blindly apply automatic retries to a "charge this payment" call without additional design work?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 12: "Managing Failure" — resilience patterns for microservice communication
- Michael T. Nygard, *Release It!: Design and Deploy Production-Ready Software* (2nd ed., Pragmatic Bookshelf, 2018) — the original, detailed source for circuit breakers, bulkheads, and related stability patterns, cited directly by Newman.
- Related: `system-design/14` (Rate Limiting and Resilience) for the same toolkit framed at the system-design level; `building-microservices/06` for the latency/availability-chaining problem this toolkit exists to contain.
