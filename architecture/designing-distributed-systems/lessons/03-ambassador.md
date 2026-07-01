---
id: designing-distributed-systems/03
subject: designing-distributed-systems
title: "The Ambassador Pattern"
slug: ambassador
status: drafted
mastery:
seniority: mid
source: "Designing Distributed Systems (Brendan Burns), Chapter 3"
prerequisites: [designing-distributed-systems/02]
created: 2026-07-01
updated: 2026-07-01
---

# The Ambassador Pattern

## TL;DR
The ambassador pattern puts a dedicated local proxy next to your application so the app can make outbound calls to `localhost` and ignore backend topology details. The ambassador owns where traffic goes and how it gets there: shard choice, service discovery, routing policy, and controlled experiments like canary splits. The result is simpler application code, faster policy changes, and better testability because network complexity moves out of business logic.

## The idea
When an application calls external systems directly, business code slowly fills with infrastructure decisions:
- Which host should I call?
- Which shard owns this key?
- What if this backend is unhealthy?
- Should I route 10% to a new version?

Those are real concerns, but they are not domain logic. They are integration logic.

The ambassador pattern isolates that integration logic in a separate container running on the same node (usually the same pod). The app talks to a local endpoint, usually `localhost:<port>`. The ambassador receives that local request, then decides where to send it in the outside world.

Think of this as a role split:
- App role: "I need customer 42" or "store order abc".
- Ambassador role: "That key maps to shard-2", "service-x currently resolves to these instances", "this request belongs to the 10% canary bucket".

This is why people sometimes confuse ambassador with sidecar: both run next to the app. The distinction is purpose.
- Sidecar pattern: adds capabilities to the app itself (for example local logging agent, config reloader, metrics helper).
- Ambassador pattern: brokers the app's outbound connections to external services.

So the ambassador is sidecar-like in placement, but different in responsibility. It is an outbound broker.

## How it works

### Local contract: the app only knows localhost
The first design decision is a strict local contract: the app never dials remote endpoints directly for that dependency. It always calls a local address exposed by the ambassador.

For example:
- App writes to `http://localhost:9000/orders`.
- App reads from `tcp://localhost:7000`.
- App uses gRPC at `localhost:50051`.

Behind that local contract, the ambassador can:
- resolve backend endpoints dynamically,
- choose a shard,
- apply retries and timeouts,
- route by policy,
- split traffic for experiments.

From the app's point of view, none of this exists. The app sees one local peer.

That separation gives you a strong engineering property: endpoint and routing policy changes no longer require touching business code.

### Canonical use 1: shard routing for data access
Many distributed stores partition data across shards. The app usually has a key (user ID, order ID, tenant ID), and one shard is the correct owner.

Without ambassador:
- app computes shard,
- app keeps shard map,
- app handles resharding transitions,
- app retries or falls back.

With ambassador:
- app sends request and key to local ambassador,
- ambassador computes shard from key,
- ambassador sends request to the right shard endpoint,
- ambassador handles map refresh and routing transitions.

The key principle is that shard ownership is infrastructure metadata. Put that metadata logic where it belongs.

### Canonical use 2: service brokering and discovery
In dynamic environments, backend instances come and go. Hardcoding hostnames in app code does not survive container scheduling and autoscaling.

An ambassador can watch service discovery sources (or receive updates from control plane tooling), maintain an active endpoint set, and pick an instance per request.

The app simply says "call payments" through localhost. The ambassador turns that intention into a concrete destination:
- `payments-v1-7c9f:8443`
- `payments-v1-41da:8443`
- `payments-v1-e201:8443`

The app remains stable while concrete targets evolve.

### Canonical use 3: experimentation and request splitting
A common rollout need is to send a small fraction of traffic to a new backend version while most traffic stays on stable.

Ambassador is a good home for this because traffic policy is centralized for that app instance:
- 90% to stable backend cluster,
- 10% to canary backend cluster.

You can change percentages in ambassador config without changing app logic. More importantly, experimentation policy is consistent for all outbound calls through that ambassador.

### Worked example 1 - topology and data path (ASCII diagram)
Suppose your app writes customer records and data is sharded into four database shards.

```text
                  same node / same pod
+----------------------------------------------------------+
|                                                          |
|   +--------------------+      localhost:7000             |
|   | customer-api app   |  --------------------------+    |
|   | (business logic)   |                            |    |
|   +--------------------+                            v    |
|                                           +------------------------+
|                                           | ambassador container    |
|                                           | shard + route broker    |
|                                           +-----------+------------+
|                                                       |
+-------------------------------------------------------|--------------+
                                                        |
                                             outbound network
                                                        |
             +----------------+  +----------------+  +----------------+  +----------------+
             | db shard-0     |  | db shard-1     |  | db shard-2     |  | db shard-3     |
             | 10.0.1.10:5432 |  | 10.0.1.11:5432 |  | 10.0.1.12:5432 |  | 10.0.1.13:5432 |
             +----------------+  +----------------+  +----------------+  +----------------+
```

The app only knows `localhost:7000`. The ambassador knows shard mapping and remote addresses.

### Worked example 2 - step-by-step sharded write/read trace
Assume four shards and shard index computed as `hash(customer_id) mod 4`.

Mapping table at this moment:
- shard-0 -> `10.0.1.10:5432`
- shard-1 -> `10.0.1.11:5432`
- shard-2 -> `10.0.1.12:5432`
- shard-3 -> `10.0.1.13:5432`

Now trace two requests.

1) Write request:
1. App receives `PUT /customers/42` with payload `{name: "Ana"}`.
2. App forwards to local ambassador at `localhost:7000/customers/42`.
3. Ambassador extracts key `42`.
4. Ambassador computes `hash(42) mod 4 = 2`.
5. Ambassador selects shard-2 endpoint `10.0.1.12:5432`.
6. Ambassador sends translated write to shard-2.
7. Shard-2 acknowledges success.
8. Ambassador returns success to app.
9. App returns HTTP 200 to caller.

2) Read request:
1. App receives `GET /customers/42`.
2. App forwards read to `localhost:7000/customers/42`.
3. Ambassador computes the same shard index `2`.
4. Ambassador routes read to shard-2.
5. Shard-2 returns `{id: 42, name: "Ana"}`.
6. Ambassador returns data to app.
7. App returns response to caller.

Notice what the app never did:
- it never tracked shard endpoints,
- it never implemented hash-to-shard code,
- it never handled shard topology updates.

That logic can now evolve independently in ambassador config or implementation.

### Worked example 3 - 10% canary split with concrete counts
Assume this app sends outbound `POST /authorize` requests to a payment service.

Policy in ambassador:
- 90% route to `payments-stable`.
- 10% route to `payments-canary`.

In one minute, app generates 2,000 authorize requests through localhost.

Expected distribution by policy:
- stable: `2,000 x 0.90 = 1,800` requests.
- canary: `2,000 x 0.10 = 200` requests.

A realistic observed minute might be:
- stable: 1,792
- canary: 208

Small variance is normal depending on routing algorithm (random, weighted round robin, hash bucket). The key outcome is that canary receives enough traffic to generate signal while exposure is bounded.

If canary error rate spikes, operations can set split to 0% canary in ambassador policy. App code stays untouched.

### Testing benefit: point ambassador at local test doubles
A major practical benefit is testability.

In local integration tests, you can run:
- app container,
- ambassador container,
- fake backend(s) or mock service(s).

Then configure ambassador to route to local test doubles instead of real remote systems.

Example test setup:
- app calls `localhost:9000/payments/authorize`.
- ambassador routes to `mock-payments:8080`.
- test asserts app behavior for success, timeout, or error responses.

The app test does not need production discovery servers, real shard clusters, or canary infrastructure. You exercise outbound behavior through the same local contract used in production.

### Operational considerations that matter in practice
The ambassador pattern is simple in principle, but quality depends on implementation details:

1. Failure handling policy
   - define retries, timeouts, and circuit-breaking behavior at ambassador layer.
   - avoid hidden retries that violate app expectations for idempotency.

2. Observability
   - emit metrics per upstream target and per route decision.
   - log decision context (selected shard, selected backend pool, canary bucket).

3. Configuration rollout safety
   - treat route and discovery config as deployable artifacts.
   - use staged rollout and rollback for policy changes.

4. Consistency of shard function
   - if multiple ambassadors route to shards, hash and mapping rules must be identical.
   - configuration skew causes hard-to-debug read/write divergence.

5. Resource overhead
   - each ambassador consumes CPU and memory.
   - in dense clusters, this can be non-trivial and must be budgeted.

These concerns do not negate the pattern. They show that the ambassador is now part of your data path and should be engineered as production software.

## Pros
- Keeps business code focused on domain behavior instead of backend topology.
- Centralizes outbound routing logic for a given app instance.
- Enables dynamic shard/discovery/routing updates without app code changes.
- Supports controlled experiments (for example 10% canary) close to call site.
- Improves testability by preserving a stable localhost contract.
- Makes multi-backend policies explicit and easier to audit.

## Cons
- Adds another hop and component in critical outbound path.
- Consumes extra CPU/memory per app instance.
- Misconfiguration can cause broad routing incidents.
- Debugging now spans app plus ambassador behavior.
- Policy can become fragmented if each service builds ambassador rules differently.
- Requires discipline around versioning and config rollout.

## Alternatives
- **Put sharding/discovery logic in the app**: fewer runtime components, but business code becomes infrastructure-heavy and harder to evolve safely.
- **A client-side library**: reusable within one language ecosystem, but still links policy to application release cycles and can drift across services.
- **A remote/standalone proxy or API gateway**: centralizes policy strongly, but may be farther from app context and can become a shared bottleneck.
- **A service mesh data-plane proxy**: powerful standardized traffic management, but introduces mesh complexity and broader platform dependencies.

## When to use it
Use ambassador when outbound integration policy is non-trivial and changes often.

Good signals:
- You must route requests to shards based on key ownership.
- You must discover or broker dynamic backend instances.
- You need weighted traffic splitting for canary experiments.
- Multiple apps need the same outbound policy shape.
- You want app code to depend on stable localhost contracts.

It is especially useful for mid-size systems where direct remote calls are now too complex, but full platform-level mesh adoption is not yet justified.

## When NOT to use it
Do not use ambassador by default for every dependency.

Avoid it when:
- Outbound target is single, static, and operationally simple.
- The app's direct client already solves discovery/routing cleanly with low complexity.
- Latency budget is extremely tight and each extra hop matters.
- Team cannot operate additional proxy/config infrastructure safely.
- You need globally consistent policy managed centrally across all services, where a dedicated gateway or mesh may fit better.

A useful rule: if the complexity you remove from the app is smaller than the complexity you add in operating ambassadors, do not adopt the pattern there.

## Key takeaways / mental model
Use this mental model:

1. Ambassador is an outbound broker next to the app.
2. The app speaks intent to localhost, not topology to remote systems.
3. Ambassador translates intent into concrete destination and routing policy.
4. This separation keeps domain code clean and integration policy evolvable.

In one line: the app decides what it wants; the ambassador decides where and how to get it.

## Self-check questions
1. Your service currently computes shard IDs in application code. What concrete maintenance and failure risks does that create, and which of those would move to an ambassador?
2. In a system with four shards, if `hash(key) mod 4` maps key `customer-42` to shard-2, describe the exact data path from app to shard and back when using an ambassador.
3. You run a 10% canary split and receive 5,000 outbound requests in five minutes. What request counts do you expect per backend, and what level of variance is acceptable?
4. If canary errors spike, what should change immediately in ambassador policy, and why is this safer than shipping a hotfix in app code?
5. Compare ambassador with a client library for service discovery: where does each place change management burden, and how does that affect release velocity?
6. Give a concrete scenario where ambassador is the wrong choice, then explain which alternative would be simpler and why.

## References
- Designing Distributed Systems (Brendan Burns), Chapter 3: "The Ambassador Pattern"
- [designing-distributed-systems/02 - The Sidecar Pattern](02-sidecar.md)
- [system-design/04 - Consistent hashing](../../system-design/lessons/04-consistent-hashing.md)
