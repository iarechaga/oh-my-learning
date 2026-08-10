---
id: sre/14
subject: sre
title: Handling Overload and Cascading Failure
slug: overload-cascading-failure
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 21-22
prerequisites: [sre/07, sre/11]
created: 2026-08-10
updated: 2026-08-10
---

# Handling Overload and Cascading Failure

## TL;DR
Cascading failures happen when a system's own failure-handling behavior — retries, timeouts, restarts — amplifies an initial, often small, problem into a much larger one, typically by concentrating load onto already-struggling servers faster than they can shed it. The core defenses (load shedding, circuit breakers, and controlled retries with backoff and jitter) all work the same way: they make the system fail a *little*, on purpose and early, to prevent it from failing *completely*, later and everywhere.

## The idea
Most severe, multi-hour outages don't start as one big failure — they start as a small one that the system's own reaction to the problem turns into a big one. A handful of servers get slow (maybe a GC pause, maybe a downstream dependency hiccup); clients waiting on those servers time out and retry; the retries add more load onto a system that's already struggling, which makes it slower, which causes more timeouts and more retries — a positive feedback loop that can take a system from "5% of servers briefly slow" to "100% of servers overloaded and unresponsive" in minutes, entirely from the system's own defensive behavior.

The book's key insight is that this is a systemic, architectural problem, not a bug in any single component — every individual retry, every individual timeout, every individual auto-restart is locally reasonable ("if my request fails, try again"), but the aggregate effect of thousands of clients all reasoning the same way, at the same time, against the same struggling backend, is what causes the cascade. Defending against it requires designing the system's failure-handling behavior explicitly, not just hoping each component's local logic composes safely.

## How it works

### The retry storm
**Worked example.** A backend service normally serves 10,000 requests/second comfortably. A brief network blip causes 5% of requests (500/sec) to time out. Each client is configured to retry immediately on timeout. Those 500 retries land back on the same backend within the same second, on top of the next second's normal 10,000 requests — the backend now sees 10,500 requests/second, some fraction of which also fail under the added load, generating more retries. If this feedback loop isn't broken, the retry volume can grow geometrically: 500 -> ~550 -> ~700 -> ... within a few iterations, the backend is overwhelmed by retry traffic alone, long after the original network blip has resolved — the system is now failing because of its own reaction to a failure that's already over.

### Thundering herd on recovery
A related pattern occurs specifically at the moment a failed dependency *recovers*. **Worked example.** A cache cluster goes down for 3 minutes; during that time, every request that would have hit the cache instead falls through to the origin database, which was sized assuming a 95% cache hit rate (only 5% of traffic normally reaches it). The moment the cache comes back online, it's completely empty (cold), so the *first wave* of requests after recovery still all miss the cache and hit the database directly — the "herd" of traffic that should have been absorbed by a warm cache instead thunders into the database at nearly 100% miss rate, potentially causing a second, self-inflicted outage caused by the recovery itself.

### Defense 1: load shedding
Load shedding means deliberately, explicitly rejecting some requests when a server is near its capacity limit, rather than trying to serve every request and degrading everyone's response equally as saturation climbs. **Worked example.** A server configured to shed load once its request queue exceeds 500 pending items starts returning fast, cheap `503 Service Unavailable` responses to new requests beyond that threshold, rather than accepting them, queuing them further, and eventually timing them out slowly (which wastes the server's time on requests it will fail anyway, and wastes the client's time waiting for a slow failure instead of a fast one it can react to immediately). Shedding the least valuable fraction of traffic protects the server's ability to serve the rest well — a server serving 80% of requests successfully and shedding 20% fast is far healthier than one serving 100% of requests slowly and unreliably.

### Defense 2: circuit breakers
A circuit breaker is a client-side (or gateway-side) mechanism that stops sending requests to a dependency once that dependency's failure rate crosses a threshold, "opening the circuit" for a cooldown period before allowing a small number of test requests through to check if the dependency has recovered ("half-open" state). **Worked example.** A client calling a downstream service sees its error rate exceed 50% over the last 10 seconds; the circuit breaker opens, and for the next 30 seconds the client fails fast locally (returns an error immediately, without even attempting the network call) instead of sending requests that would likely fail anyway and add load to an already-struggling dependency. After 30 seconds, the breaker allows a small trickle of test requests through; if they succeed, the circuit closes and normal traffic resumes gradually; if they still fail, the cooldown extends. This directly prevents the retry-storm dynamic by cutting off the source of retry pressure at the client, rather than letting every client independently keep hammering a struggling backend.

### Defense 3: retries with exponential backoff and jitter
When a retry genuinely is appropriate, it should never be immediate and uniform across all clients. **Exponential backoff** means each successive retry waits longer than the last (e.g., 1s, 2s, 4s, 8s), reducing the retry rate over time rather than sustaining it. **Jitter** means randomizing the exact wait time within that growing window (e.g., a random value between 0 and the backoff ceiling) so that many clients that failed at the same moment don't all retry at exactly the same moment, which would just recreate a synchronized spike. **Worked example.** 1,000 clients all experience a timeout in the same second. Without jitter, if they all use a fixed 2-second backoff, all 1,000 retry simultaneously 2 seconds later, recreating the exact spike. With jitter (each client picks a random backoff between 0 and 2 seconds), the same 1,000 retries spread out over a 2-second window — roughly 500/second instead of 1,000 in a single instant — a much gentler, more absorbable load pattern for the recovering backend.

### Defense 4: warming caches and staged recovery
To avoid the thundering-herd-on-recovery pattern, a recovering cache or dependency should come back online gradually rather than accepting full traffic immediately — e.g., a cache pre-warmed with the most commonly requested keys before being added back to the serving pool, or traffic ramped back onto a recovered backend in stages (similar in spirit to the staged rollout from `sre/12`, but for capacity recovery rather than code deployment) rather than switched on at 100% instantly.

### Putting it together: a worked cascading-failure timeline, defended vs. undefended
**Undefended:** A downstream payment-verification service gets slow (p99 latency jumps from 100ms to 3s) due to a database issue. Clients time out at 1s and retry immediately with no backoff. Retry volume triples within 90 seconds. The payment-verification service, now receiving 3x its normal load on top of already being slow, exhausts its connection pool and starts rejecting all requests, not just slow ones. Every service depending on payment verification now fails 100% of its own requests, and *their* clients start retrying too — the cascade has now spread one hop further, well beyond the service that was originally struggling.

**Defended:** The same initial slowdown occurs. Clients' circuit breakers open after the error rate crosses 50% over a 10-second window, cutting off most of the retry pressure within seconds. The retries that do occur use exponential backoff with jitter, spreading remaining load over time rather than concentrating it. The payment-verification service itself sheds load once its queue exceeds a threshold, returning fast failures rather than accepting requests it can't serve in time. The database issue still causes a real, visible SLO impact (`sre/04`'s budget is spent) — but it stays contained to a bounded, minutes-long degradation instead of cascading into a multi-hour, multi-service outage.

## Pros
- Load shedding, circuit breakers, and backoff-with-jitter are well-understood, broadly applicable patterns that directly break the specific feedback loops that turn small problems into large ones.
- Containing a failure's blast radius to its origin (rather than letting it cascade) directly protects the error budget of every *other* service in the dependency graph, not just the one that initially degraded.
- These defenses are largely orthogonal to the root cause of the original problem — they help regardless of whether the initial trigger was a bad deploy, a network blip, or a hardware failure.

## Cons
- Adds real complexity to client and server code (backoff logic, circuit-breaker state machines, load-shedding thresholds), and getting the thresholds wrong (too aggressive shedding, too slow a circuit breaker) can itself cause unnecessary failures during genuinely recoverable brief blips.
- Circuit breakers and load shedding can mask a real underlying problem from being immediately visible if not paired with good monitoring (`sre/07`) — a service silently shedding 30% of traffic "successfully" still represents a real SLO impact that needs to be seen and acted on.
- Requires coordination across teams to implement consistently — one team's well-behaved backoff logic doesn't help if another team's client retries immediately with no backoff against the same shared dependency.

## Alternatives
- **Simply overprovisioning capacity to absorb any retry storm** — can work for smaller-scale or bounded traffic patterns, but retry storms can in principle grow faster than any finite headroom can absorb (the feedback loop is multiplicative), and it does nothing to prevent the thundering-herd-on-recovery pattern.
- **Static rate limiting only, no adaptive shedding** — simpler to implement than dynamic load shedding, but a fixed rate limit doesn't adapt to the server's actual real-time capacity, so it can either under-protect (limit set too high) or unnecessarily reject traffic the server could actually handle (limit set too low, especially once conditions improve).
- **Manual incident response only (no automated defenses)** — relies on a human noticing and intervening (e.g., manually disabling a struggling dependency) fast enough to stop a cascade, which is rarely fast enough given how quickly retry storms compound (often faster than a human can be paged, diagnose, and act, per `sre/09`'s incident-command timelines).

## When to use it
Build load shedding, circuit breakers, and backoff-with-jitter into any service with meaningful internal or external dependencies, especially in an architecture with many services calling each other where a local failure has room to propagate. Prioritize these defenses on the highest-fan-in dependencies (shared services many others call), since that's where a retry storm has the most amplification potential.

## When NOT to use it
Don't over-engineer circuit-breaker and shedding logic for a simple, low-traffic internal tool with few dependents, where the operational complexity of the defenses exceeds any realistic cascading-failure risk. Also avoid tuning shedding/circuit-breaker thresholds so aggressively that normal, brief, self-resolving blips trigger unnecessary defensive behavior — that trades a rare severe problem for a frequent minor annoyance.

## Key takeaways / mental model
A cascading failure is the system's own defensive reflexes (retries, restarts) turning a small problem into a big one by concentrating load onto something already struggling. The fix is always some version of "fail fast and spread out": shed load explicitly rather than queuing until you time out slowly, cut off retry pressure with circuit breakers before it compounds, and when you do retry, back off and jitter so many clients don't recreate the exact spike that caused the problem in the first place.

## Self-check questions
1. A team's clients retry immediately (no backoff, no jitter) on any timeout. Walk through, step by step, how a brief 2-second network blip could turn into a 10-minute full outage, using the retry-storm mechanics from this lesson.
2. Explain why jitter is necessary in addition to exponential backoff — what specific failure mode does backoff alone not solve?
3. A cache cluster recovers from an outage and is immediately added back to the serving pool at 100% traffic. Predict what happens to the origin database, and propose a fix using this lesson's staged-recovery concept.
4. A service adds aggressive load shedding (rejecting requests once its queue exceeds 200) but has no alerting on the shed-request rate. What real problem could this configuration hide, and why is that dangerous even though the service "looks" healthy from the outside?

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 21 ("Handling Overload") and Chapter 22 ("Addressing Cascading Failures").
- See also: `sre/07` (monitoring, needed to see shed load and circuit-breaker activity) and `sre/11` (capacity planning, since undersized capacity is a common trigger for the initial overload that starts a cascade).
