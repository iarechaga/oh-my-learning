---
id: designing-distributed-systems/05
subject: designing-distributed-systems
title: "Replicated Load-Balanced Services"
slug: replicated-load-balanced
status: drafted
mastery:
seniority: mid
source: "Designing Distributed Systems (Brendan Burns), Chapter 5"
prerequisites: [designing-distributed-systems/01]
created: 2026-07-01
updated: 2026-07-01
---

# Replicated Load-Balanced Services

## TL;DR
The simplest and most common multi-node serving pattern: run many identical, stateless copies of a service behind a load balancer. Because every replica can answer any request, you get horizontal scale (add replicas for more throughput) and availability (one replica dying does not take the service down) - but only if the replicas are truly stateless and only if the load balancer sends traffic exclusively to *ready* replicas, which is what readiness checks guarantee.

## The idea
A single server has a ceiling: finite CPU, memory, and connections. When demand exceeds one machine, or when one machine's failure would be an outage, you need more than one copy of your service running at once. The replicated load-balanced service is the pattern for that: **N identical instances of the same container image, fronted by a load balancer that spreads incoming requests across them.**

The pattern only works cleanly under one crucial condition: the replicas must be **stateless** - interchangeable. Any replica must be able to serve any request with the same result, because the load balancer may send request 1 to replica A and request 2 (from the same user) to replica C. If a replica keeps important state locally (a user's session in memory, a file it wrote to its own disk), the replicas are *not* interchangeable, the load balancer's spreading breaks correctness, and you have lost the whole benefit. So the pattern is really two ideas welded together: *replicate the service* and *push all state out of the replicas* (into a database, cache, or object store the replicas share).

Two properties fall out of this, and they are the reasons the pattern is everywhere:

1. **Scalability.** Throughput grows (roughly) linearly with the number of replicas. Twice the replicas, roughly twice the requests per second - up to the point where a shared downstream (the database) becomes the new bottleneck.
2. **Availability.** With replicas behind a balancer, the failure of one replica removes a fraction of capacity, not the whole service. The balancer simply stops routing to the dead one.

## How it works

### The building blocks: image, replica set, load balancer
Three pieces make up the pattern.

- **A stateless container image.** One image, run many times. "Stateless" means: no request-affecting data lives only inside a replica. Session data, uploaded files, counters - all of it lives in a shared backing store the replicas talk to.
- **A replica controller** (in Kubernetes, a Deployment/ReplicaSet). You declare "I want 5 replicas of this image" and the orchestrator keeps exactly 5 running: it starts new ones, restarts crashed ones, and reschedules ones whose node died.
- **A load balancer** in front. It owns one stable address (a virtual IP or DNS name) that clients use, and it distributes each incoming request to one of the healthy replicas (see [system-design/06 - DNS and Load Balancing](../../system-design/lessons/06-dns-load-balancing.md) for L4/L7 and the algorithms).

```text
                 +------------------+
   clients ----> |  Load Balancer   |   (one stable VIP/DNS)
                 +------------------+
                    |     |     |
        +-----------+     |     +-----------+
        v                 v                 v
   +---------+       +---------+       +---------+
   |Replica A|       |Replica B|       |Replica C|   (identical image)
   +---------+       +---------+       +---------+
        \                 |                 /
         \                v                /
          +------> shared DB / cache <-----+   (all state lives here)
```

### Readiness vs liveness: the two checks that make it safe
Replication is only safe if the load balancer never sends a request to a replica that cannot serve it. Two distinct health checks handle two distinct questions, and confusing them is a classic outage cause.

- **Liveness check:** "Is this replica *alive*, or is it wedged and should be killed?" If liveness fails, the orchestrator **restarts** the container. Liveness answers a restart decision.
- **Readiness check:** "Is this replica *ready to receive traffic right now*?" If readiness fails, the load balancer **stops sending it requests** (but does not kill it). Readiness answers a routing decision.

The difference is subtle but load-bearing. A replica that has just started may be *alive* (process running) but *not ready* (still loading a 2 GB model into memory, still warming its cache, still opening its DB pool). If the balancer routed to it the instant the process started, early users would get errors or timeouts. The readiness check gates traffic until the replica truly can serve. Likewise, a replica that has lost its database connection might be alive but temporarily not-ready; readiness pulls it out of rotation until it recovers, without a disruptive restart.

```text
liveness  FAIL -> orchestrator RESTARTS the container
readiness FAIL -> load balancer STOPS routing to it (no restart)
readiness PASS -> load balancer resumes routing
```

### Session state: the thing that breaks statelessness, and how to handle it
The hardest real-world wrinkle is user session state. Naively, a service stores "who is logged in" in the replica's memory. The moment you replicate, that breaks: the user logs in on replica A, their next request lands on replica C, which never saw them. Three ways out, in increasing order of "correct for this pattern":

1. **Session stickiness (affinity):** configure the balancer to pin a given client to the same replica (by cookie or IP hash). Simple, but it undermines the pattern - load spreads unevenly, and if that replica dies the user's session is gone. Use sparingly.
2. **Externalize session state:** move sessions into a shared store (Redis, a database). Every replica reads/writes sessions there, so any replica can serve any user. This is the standard answer and restores true statelessness.
3. **Stateless tokens:** put the session *in the request itself* as a signed token (e.g. a JWT). No server-side session at all; any replica validates the token locally. Best when it fits.

### Worked example 1: scaling throughput and the downstream ceiling
A service replica handles ~200 requests/second (rps) before its CPU saturates. Traffic is 700 rps.

1. One replica: 200 rps served, 500 rps queued or rejected. Bad.
2. Scale to 4 replicas behind the balancer with round-robin: 4 x 200 = 800 rps capacity > 700 rps demand. Each replica gets ~175 rps. Healthy.
3. Traffic grows to 1,600 rps. Scale to 8 replicas: 8 x 200 = 1,600. Still fine *at the service tier*.
4. But now the shared database, sized for ~1,000 rps of queries, is the bottleneck. Adding replica 9, 10, 11 does **not** help - they all pile onto the same saturated database.

The lesson: replication scales the *stateless* tier linearly, but the shared *stateful* downstream becomes the new ceiling. Beyond it you need a different tool - caching (to cut DB load), read replicas, or **sharding** the data (lesson 06).

### Worked example 2: a rolling deployment relying on readiness
You deploy a new version of the image across 4 replicas without downtime.

1. Orchestrator starts 1 new-version replica (now 5 total). Its **readiness** check fails while it loads - the balancer does not route to it yet, so no user hits a half-started replica.
2. New replica finishes warming; readiness passes; balancer adds it to rotation. Now 5 serving.
3. Orchestrator terminates 1 old replica. Before killing it, the replica is marked not-ready so the balancer **drains** it (stops new requests, lets in-flight ones finish). Down to 4, mixed versions.
4. Repeat until all 4 are the new version. At every step there are >= 4 ready replicas serving, so users see no outage.

Without a correct readiness check, step 1 would route real users to a replica still loading its model - a self-inflicted partial outage during every deploy.

### Worked example 3: a failure removes capacity, not the service
5 replicas, each 200 rps, serving 800 rps (160 rps each, comfortable).

1. Replica B's node crashes. The balancer's health check to B fails within a few seconds; B is removed from rotation.
2. Now 4 replicas share 800 rps = 200 rps each - exactly at capacity, tight but serving. No outage, just less headroom.
3. The orchestrator notices the ReplicaSet is below its desired count and schedules a replacement on a healthy node. The new replica boots, passes readiness, and rejoins - back to 5 replicas and comfortable headroom.

Contrast with a single un-replicated server: step 1 would be a full outage lasting until a human noticed and restarted something.

## Pros
- **Horizontal scalability:** throughput scales (near) linearly with replica count, up to the shared-downstream ceiling.
- **High availability:** losing a replica costs a fraction of capacity, not the service; the balancer routes around failures automatically.
- **Zero-downtime deploys:** rolling updates gated by readiness keep a healthy pool serving throughout.
- **Operational simplicity (for the pattern's class):** identical replicas are easy to reason about, autoscale, and replace - any one is disposable.

## Cons
- **Requires true statelessness:** local state (in-memory sessions, local disk) silently breaks correctness once traffic spreads across replicas.
- **Shared downstream becomes the bottleneck:** the database/cache the replicas share does not scale just because you added replicas.
- **Readiness/liveness must be correct:** a wrong or missing readiness check routes traffic to not-ready replicas; a wrong liveness check restart-loops healthy ones.
- **Even distribution is not guaranteed:** long-lived connections, uneven request cost, or sticky sessions can create hot replicas (see the load-balancing algorithms lesson).

## Alternatives
- **Vertical scaling (a bigger single server):** simpler, no distribution, but has a hard ceiling and remains a single point of failure.
- **Sharded services:** when replicas cannot be identical because the *data* is too big for one backing store or must be partitioned; each shard owns a slice of data (lesson 06).
- **Sharded + replicated (the common production shape):** replicate *within* each shard for availability and shard *across* for data scale - the two patterns composed.
- **Serverless functions:** the platform auto-replicates your handler per request/event; a managed form of this pattern for bursty, stateless work (lesson 08).

## When to use it
- Your service is (or can be made) stateless, and you need more throughput than one machine provides.
- You need availability - a single instance's failure must not be an outage.
- You want zero-downtime rolling deployments and easy autoscaling.
- Request load is spread across many independent requests rather than a few enormous stateful sessions.

## When NOT to use it
- The service is inherently stateful and the state cannot be externalized (e.g. an in-memory computation that is too large or too chatty to move to a shared store) - consider sharding instead.
- The dataset is too large for a single shared backing store, so replicas would all hammer an over-capacity database - shard the data first.
- Load is trivial and fits comfortably on one machine with acceptable failure risk - replication adds cost and a load balancer for no benefit.

## Key takeaways / mental model
Picture a bank of identical ticket windows fronted by a single "next available window" queue manager. Any clerk can serve any customer because none of them keeps your file in their own drawer (all files live in the shared back office). Add clerks to serve more customers; if one clerk goes home, the queue simply routes around them. Two rules of thumb:

1. **Replication scales only the stateless tier.** Push every request-affecting piece of state out of the replicas into a shared store, or the whole pattern quietly breaks. The shared store is your real scaling ceiling.
2. **Readiness gates traffic; liveness gates restarts.** Never let the load balancer route to a replica that says it is not ready, and never restart a replica that is merely warming up.

## Self-check questions
1. Why must replicas be stateless for a replicated load-balanced service to be correct, and what exactly goes wrong if a replica keeps session state in local memory?
2. Distinguish a liveness check from a readiness check. Which one controls load-balancer routing, and which one controls container restarts? Give a scenario where a replica should be alive but not-ready.
3. In worked example 1, why does adding replicas past 8 stop helping? What tools would you reach for once the shared database is the bottleneck?
4. Walk through how a rolling deployment avoids downtime, and explain the specific role the readiness check plays at each step.
5. Compare three ways to handle user sessions across replicas (stickiness, externalized store, stateless tokens). What does each cost, and which best preserves the pattern?
6. Given a service that is CPU-bound at 150 rps per replica and a traffic target of 1,200 rps with N+1 headroom for one failure, how many replicas would you run and why?

## References
- Designing Distributed Systems (Brendan Burns), Chapter 5: "Replicated Load-Balanced Services"
- [designing-distributed-systems/01 - Why Distributed Patterns](01-why-distributed-patterns.md)
- [system-design/06 - DNS and Load Balancing](../../system-design/lessons/06-dns-load-balancing.md)
