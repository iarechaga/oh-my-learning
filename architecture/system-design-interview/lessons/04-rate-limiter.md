---
id: system-design-interview/04
subject: system-design-interview
title: "Design a Rate Limiter"
slug: rate-limiter
status: drafted
mastery: 
seniority: mid
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 4"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03]
created: 2026-08-10
updated: 2026-08-10
---

# Design a Rate Limiter

## TL;DR
A rate limiter caps how many requests a client can make in a given time window,
protecting a service from abuse, runaway retries, or accidental traffic spikes. The
interview walkthrough below runs the standard framework — clarify, estimate,
high-level design, deep dive — landing on the token bucket algorithm as the default
choice, and on sharing rate-limit state via a centralized store like Redis as the hard
part once you have more than one server.

## The idea
Without a limit, a single misbehaving client (a buggy retry loop, a scraper, or a
malicious actor) can consume enough of a service's capacity to degrade it for every
other client. A rate limiter enforces a policy like "at most 100 requests per user per
minute" at the edge of the system, rejecting (or delaying) requests that exceed it
before they consume expensive downstream resources (database connections, compute).

This is a canonical "design X" interview question because it looks small but has real
depth: which algorithm to use, where to place the limiter, how to make it correct
across multiple servers, and what to return to the client, all have non-obvious
trade-offs.

## How it works

### Step 1: Clarify requirements
Before designing, pin down:
- **What are we limiting by?** Per user ID, per IP address, per API key, or a
  combination? (Assume: per user ID for authenticated requests, per IP for
  unauthenticated ones.)
- **What's the limit?** E.g., "10 requests per second," "10,000 requests per day."
  (Assume: configurable, but design for something like 100 req/min per user as a
  concrete number to reason about.)
- **What happens when a client is rate-limited?** Reject with an HTTP 429 status and
  informative headers, or queue/delay? (Assume: reject with 429.)
- **Where does it run?** As a library inside each app server, or as a standalone
  service/middleware (e.g., in an API gateway)? (Assume: a standalone component
  sitting in front of the app servers, since it needs to work across a fleet.)
- **Distributed correctness**: does the limit need to be exact, or is approximate
  enforcement (a client might sneak through slightly over the limit under race
  conditions) acceptable? (Assume: approximate is fine — this is the common real-world
  answer, and exact enforcement across distributed nodes is expensive.)

### Step 2: Back-of-the-envelope
Suppose the service handles 500,000 QPS at peak (per `system-design-interview/02`'s
method) across ~10 million active users. If the rate limiter needs to track a rolling
counter per user, that's 10 million keys. Each key needs, at minimum, a counter and a
timestamp — call it 50 bytes per key. Total: 10,000,000 × 50 bytes = 500 MB, which
comfortably fits in memory on a single well-provisioned cache node, and trivially fits
in a small Redis cluster. This number is what justifies keeping rate-limit counters in
an in-memory store like Redis rather than a disk-backed database — the state is small,
but it's read and written on nearly every request, so it must be fast.

### Step 3: High-level design
The rate limiter sits between the client and the app servers, most commonly as
middleware in an API gateway or as its own lightweight service that app servers call
before processing a request.

```
[Client] --> [API Gateway / Rate Limiter] --> [App Servers]
                       |
                       v
              [Shared Counter Store: Redis]
```

For each incoming request: identify the client (user ID or IP), look up/update their
counter in the shared store, and allow or reject based on the current count versus the
limit. The shared store is what makes this correct across multiple gateway instances —
without it, each instance would track its own counter and the effective limit would be
(configured limit) × (number of instances).

### Step 4: Deep dive — choosing an algorithm

**Token bucket.** Each client has a bucket that holds up to `capacity` tokens.
Tokens are added at a fixed `refill_rate` (e.g., 10 tokens/second) up to the capacity.
Each request consumes one token; if the bucket is empty, the request is rejected.

*Worked example:* capacity = 10, refill rate = 5 tokens/sec.
- t=0: bucket starts full (10 tokens). A client bursts 10 requests instantly — all 10
  succeed, bucket now at 0.
- t=0 to t=1: bucket refills by 5 tokens (5 tokens/sec × 1 sec) → bucket at 5.
- A single request at t=1 succeeds (bucket → 4).
- If the client tries 10 more requests immediately at t=1, only 4 succeed; the other 6
  are rejected until more tokens accumulate.

This allows short bursts up to `capacity` while enforcing a steady-state average rate
of `refill_rate`, which matches how real traffic behaves (bursty, not perfectly smooth)
and is why token bucket is the most common default choice in production systems (e.g.,
AWS API Gateway, Stripe's API).

**Leaky bucket.** Requests enter a fixed-size FIFO queue ("bucket") and are processed
("leak out") at a constant rate; if the queue is full, new requests are dropped.
Unlike token bucket, this smooths bursts into a constant output rate rather than
allowing them through — useful when the downstream system genuinely cannot handle
bursts (e.g., a fixed-capacity worker pool), but adds latency for legitimate bursty
clients since requests wait in the queue.

**Fixed window counter.** Count requests in a fixed time window (e.g., "requests this
calendar minute"); reset the counter at each window boundary. Simple to implement, but
has a **boundary burst problem**: a client can send `limit` requests in the last
millisecond of one window and `limit` more in the first millisecond of the next,
achieving 2x the intended rate in a short span.

*Worked example:* limit = 100 req/min, window = [12:00:00, 12:01:00).
- A client sends 100 requests at 12:00:59.9 (all allowed — window 1's quota).
- The window resets at 12:01:00. The same client immediately sends 100 more requests at
  12:01:00.1 (all allowed — window 2's quota).
- Result: 200 requests within a ~200ms span, double the intended 100/min rate.

**Sliding window log.** Store a timestamp for every request per client; on each new
request, discard timestamps older than the window and count what remains. This is
precise (no boundary burst problem) but memory-expensive — it stores one entry per
request, not one counter per client, which does not fit the 500 MB budget from Step 2
at this system's scale (10M users × many requests each, rather than 10M fixed-size
counters).

**Sliding window counter.** A practical compromise: keep a counter for the current
fixed window and the previous one, and estimate the sliding-window count as a weighted
average, assuming requests in the previous window were evenly distributed.

*Worked example:* limit = 100/min. Previous window (12:00-12:01) had 80 requests.
Current window (12:01-12:02) has had 30 requests so far, and we're 40% of the way
through the current window (at 12:01:24).
`estimated count = current_window_count + previous_window_count × (1 - elapsed_fraction)`
`= 30 + 80 × (1 - 0.4) = 30 + 48 = 78`, which is under the 100 limit, so the request is
allowed. This approximates the sliding window log's precision at fixed-window's memory
cost (two counters per client instead of a list of timestamps), which is why it's the
book's recommended default when boundary bursts matter but sliding-window-log's memory
cost is unacceptable.

| Algorithm | Memory per client | Handles bursts | Precision | Complexity |
| --- | --- | --- | --- | --- |
| Token bucket | O(1) (2 fields) | Yes, up to capacity | Approximate at edges | Low |
| Leaky bucket | O(1) + queue | Smooths, doesn't allow | Approximate | Low-medium |
| Fixed window counter | O(1) | No (boundary burst) | Poor at boundaries | Very low |
| Sliding window log | O(n) requests | Yes | Exact | High (memory) |
| Sliding window counter | O(1) (2 fields) | Yes | Approximate, good | Medium |

### Step 5: Deep dive — making it work across multiple servers
The shared-store approach (Step 3) is the standard fix, but introduces its own hard
problems:

- **Race conditions.** Two concurrent requests from the same user both read the current
  counter as 99 (limit 100), both increment, and both are allowed — even though only
  one should have been, since after the first increment the count should be 100. Fix
  with atomic operations (Redis's `INCR` is atomic) or a Lua script that reads,
  checks, and increments in a single atomic step.
- **Latency of the shared store.** Every request now pays the round-trip cost to Redis
  (recall from `system-design-interview/02`: ~0.5 ms same-datacenter, negligible
  compared to typical request latency, but it's an added dependency and a new failure
  mode).
- **What if Redis is down?** Decide a fail-open (allow all requests, prioritizing
  availability) or fail-closed (reject all requests, prioritizing protection) policy.
  Fail-open is more common in practice, since a rate limiter's job is to protect against
  abuse, not to be the reason the whole service goes down.

### Step 6: Returning useful information to the client
A well-designed rate limiter returns HTTP headers alongside a 429 (or even on
successful requests) so clients can back off intelligently: `X-RateLimit-Limit`,
`X-RateLimit-Remaining`, `X-RateLimit-Retry-After`. This turns the rate limiter from a
hard wall into a signal well-behaved clients can use to self-regulate, reducing the
number of rejected requests over time.

## Pros
- Protects backend resources from being overwhelmed by any single client, whether
  malicious or accidentally misbehaving (e.g., a retry storm).
- Can be layered — a coarse global limit at the API gateway plus a finer per-endpoint
  limit closer to expensive operations.
- Token bucket specifically allows legitimate bursty usage patterns without raising the
  sustained-rate limit.

## Cons
- Adds a new dependency (the shared counter store) and a new failure mode.
- Approximate algorithms (token bucket, sliding window counter) can let a client
  slightly exceed the nominal limit under specific timing conditions — acceptable for
  most use cases, not for hard financial/safety limits.
- Coarse limiting (e.g., per-IP only) can unfairly penalize many legitimate users behind
  a shared NAT/proxy IP, or fail to stop an attacker who rotates IPs.

## Alternatives
- **No rate limiting, rely on infrastructure auto-scaling** — works for cost-tolerant
  traffic spikes but doesn't stop abuse or protect a specific downstream dependency
  (e.g., a third-party API with its own hard limit) that can't itself auto-scale.
- **Circuit breakers and load shedding** — react to a service already being overloaded,
  rather than proactively capping per-client usage; complementary to, not a replacement
  for, rate limiting (see `system-design/14`).
- **Quotas (e.g., "1,000 calls per day" billing tiers)** — a longer-window, often
  business-driven limit, frequently implemented as a rate limiter with a very long
  window rather than a fundamentally different mechanism.

## When to use it
Any public-facing API, any endpoint that's expensive to serve (search, write-heavy
endpoints, anything hitting a slow downstream dependency), and any system where a small
number of clients could otherwise starve the rest.

## When NOT to use it
Internal, trusted, low-volume service-to-service calls within a single team's system
usually don't need a full distributed rate limiter — a simpler concurrency limit or
none at all may suffice, and adding one is unnecessary operational overhead. Also avoid
overly aggressive limits on legitimate power users without a tiered plan — this is a
product decision as much as a technical one, and should be clarified in Step 1, not
assumed.

## Key takeaways / mental model
Picture a bucket that refills at a steady drip (token bucket): it lets you spend a
burst of saved-up tokens quickly, but caps you to the drip rate over time. The hard
part of the interview is never "which algorithm" in isolation — it's making the chosen
counter correct and fast when read and written by many servers at once, which is why
the deep dive centers on a shared, atomic, in-memory store.

## Self-check questions
1. Why does the fixed window counter allow up to 2x the intended rate at window
   boundaries, and how does the sliding window counter mitigate this without storing
   every request timestamp?
2. A client bursts 20 requests instantly against a token bucket with capacity 10 and
   refill rate 2/sec. How many succeed immediately, and how long until the client can
   send 5 more successfully?
3. Why must the "read counter, check limit, increment counter" sequence be atomic in a
   distributed rate limiter, and what specifically goes wrong if it isn't?
4. When would you choose fail-open vs. fail-closed if the shared Redis store becomes
   unavailable, and what does each choice prioritize?
5. Why is per-IP rate limiting alone insufficient for many real-world systems, and what
   would you combine it with?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 4
- Cross-reference: `system-design/14` (rate limiting and resilience) for algorithm
  detail from the general system-design angle.
