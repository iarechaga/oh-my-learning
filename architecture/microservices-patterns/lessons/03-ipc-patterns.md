---
id: microservices-patterns/03
subject: microservices-patterns
title: "Inter-Process Communication Patterns"
slug: ipc-patterns
status: drafted
mastery:
seniority: senior
source: "Microservices Patterns (Chris Richardson), Chapter 3"
prerequisites: [microservices-patterns/02]
created: 2026-07-01
updated: 2026-07-01
---

# Inter-Process Communication Patterns

## TL;DR
In a monolith, modules call each other in-process, so calls are fast and mostly
deterministic. In microservices, calls cross network and deployment boundaries, so
latency, partial failure, and contract evolution become core design concerns.

IPC is therefore an architecture decision, not a transport afterthought. Choosing
synchronous request/response (REST, gRPC) versus asynchronous messaging changes runtime
coupling, failure propagation, and how safely teams can evolve independently.

## The idea
When a monolith invokes a function, caller and callee share memory, process lifecycle,
and usually one deployed version. Failure modes exist, but they are mostly local and
visible in one stack trace.

When one microservice invokes another, the "function call" becomes distributed: DNS,
load balancer, service registry, serializer, network, and remote capacity are now in the
critical path. The request can fail before reaching callee, after callee processed, or
during response transmission.

Because of this, IPC style defines system behavior under load and failure. It controls
whether callers block, whether availability depends on immediate downstream health, and
how quickly new features can be added without coordinated releases.

## How it works

### Interaction styles
Before protocol selection, define interaction style. Three practical styles cover most
microservice communication patterns.

- One-to-one, synchronous request/response: caller waits for answer now.
- One-to-one, asynchronous request/async response: caller sends request and receives
  result later through callback channel, polling endpoint, or correlation workflow.
- One-to-many, asynchronous notification: producer publishes once and multiple consumers
  react independently.

These styles imply different coupling. Synchronous request/response has high temporal
coupling: both sides must be healthy now. Asynchronous styles reduce temporal coupling
but require explicit handling of eventual consistency and replay semantics.

### Synchronous IPC with REST and gRPC
Synchronous IPC is often used for query-like interactions and immediate validations.

REST is HTTP resource-oriented, JSON-friendly, and broadly interoperable. It is easy to
debug and practical for external consumers and polyglot teams.

gRPC is RPC-oriented, schema-first, and typically uses Protocol Buffers over HTTP/2.
It favors strong typing and lower serialization overhead, so it is often preferred for
high-volume internal calls.

Trade-offs:
- REST optimizes ecosystem compatibility and human readability.
- gRPC optimizes contract strictness and performance.
- Both are synchronous, so both share partial-failure exposure.

### Partial failure and resilience patterns
In distributed systems, partial failure is normal. A dependency might be up but slow,
or fail intermittently, or accept requests but time out responses.

Baseline resilience mechanics:

1) Timeouts
Every remote call must have explicit deadlines. Example split for 300 ms endpoint budget:
50 ms connect budget, 120 ms read budget, remaining budget for local processing.

2) Bounded retries
Retry only transient failures and cap attempts. Use jittered backoff to avoid retry
storms. Never blindly retry deterministic 4xx validation failures.

3) Circuit breaker
Open breaker after failure threshold, fail fast during cooldown, then probe in half-open
state. This prevents callers from exhausting threads on known-bad dependencies.

4) Fail fast
When dependency is unhealthy, return quickly with clear degraded behavior instead of
hanging until global timeout.

### Worked example 1 - sync REST call chain with circuit breaker
FTGO flow: `Order Service` validates credit with `Customer Service` during order create.

Configuration:
- Endpoint SLA: p95 <= 350 ms.
- Remote call timeout: 120 ms.
- Retries: max 1 with 30 ms jittered backoff.
- Breaker: open after 5 failures in rolling 20 requests, 10 s cooldown.

```text
Client
  |
  | POST /orders
  v
Order Service
  | local checks (20 ms)
  |---> [Breaker CLOSED] ---> Customer Service /customers/{id}/credit
  |         timeout 120 ms, retry max 1
  |<--- 200 OK (80 ms)
  | persist APPROVED
  v
Client <- 201 Created (~140 ms)

Failure burst:
Order Service -> 5/20 failures -> breaker OPEN
Order Service -> fail fast in ~2 ms
10 s later -> HALF-OPEN probes -> CLOSE if healthy
```

Without breaker, slow downstream can saturate caller resources and trigger cascading
failure. With breaker, failure remains explicit but bounded.

### Asynchronous messaging
Asynchronous IPC inserts a broker between producer and consumers. Producer does not wait
for consumers to complete work.

Core elements:
- Broker handles storage and routing.
- Producer publishes message with durable key/correlation metadata.
- Consumers process independently and at their own pace.

Common message intents:
- Command: asks one target to perform an action.
- Event: announces state change that already occurred.
- Document: shares data snapshot for projections or integration.

Topologies:
- Point-to-point queue: one consumer instance handles each message.
- Publish/subscribe topic: many consumer groups process same message independently.

This model lowers temporal coupling and helps absorb spikes, but requires idempotency,
deduplication strategy, and operational handling for poison messages and dead letters.

### Worked example 2 - async OrderCreated fan-out
FTGO creates order, then multiple services react asynchronously.

```text
1) Order Service
   - writes order O-10452 status=PENDING
   - publishes OrderCreated{orderId, customerId, total=42.50}

2) Broker topic: orders.events
   - stores event at offset 887311
   - fans out to subscriber groups

3) Kitchen Service consumes
   - creates ticket K-7781

4) Accounting Service consumes
   - creates receivable entry

5) Notification Service consumes
   - sends user push notification

6) Duplicate delivery case
   - Kitchen sees same event again
   - checks processed-event key (orderId + eventType)
   - if already handled, no-op
```

Producer stays stable even when new consumers are introduced later. That is a direct
coupling reduction benefit of pub/sub.

### API versioning and message format evolution
Independent deployment requires contracts that evolve safely.

For synchronous APIs:
- Prefer additive, backward-compatible changes first.
- Version explicitly (`/v2` or media-type strategy) only for true breaking changes.
- Run old and new versions in parallel during migration window.

For messages/events:
- Use schema governance and compatibility policy.
- Add optional fields before removing old ones.
- Never repurpose existing field meaning silently.

Semantic versioning gives a practical language:
- MAJOR - breaking contract change.
- MINOR - backward-compatible additive change.
- PATCH - no contract break, internal correction.

### Worked example 3 - backward-compatible v1 to v2 contract change
Initial FTGO contracts:
- REST `GET /orders/{id}` returns `{orderId, status, total}`.
- Event `OrderCreated` contains `{orderId, customerId, total}`.

New requirement: show delivery ETA and address nickname.

```text
Step A (compatible additive change)
REST v1 response adds optional estimatedDeliveryTime.
OrderCreated event adds optional deliveryProfile.nickname.
Old clients/consumers ignoring unknown fields keep working.

Step B (true breaking need)
Business replaces status string with lifecycle object.
Create REST /v2/orders/{id} returning lifecycle.phase + lifecycle.since.
Keep /v1 live for 90 days, monitor remaining /v1 traffic, then sunset.
```

Key principle: use additive evolution whenever possible. Reserve major version bumps for
changes that cannot be made backward-compatible.

### Service discovery
Service instances are ephemeral in autoscaled environments. Callers need dynamic lookup
instead of static host lists. A service registry tracks healthy instances.

Client-side discovery:
- Caller queries registry and chooses instance.
- Pros: direct control, no extra routing hop.
- Cons: each client library must implement discovery + balancing logic.

Server-side discovery:
- Caller sends to stable router/load balancer that resolves target instance.
- Pros: simpler clients, centralized routing policy.
- Cons: additional hop and operational dependency on routing layer.

Most production systems combine this with per-call resilience (timeouts, retries,
breakers), because discovery alone does not solve slow or overloaded dependencies.

### Why async messaging reduces coupling
Async messaging mainly reduces temporal coupling. Producer does not require consumer
availability at publish time as long as broker is available and durable.

It can also reduce location coupling in pub/sub because producer publishes to topic,
not to each consumer endpoint.

But it does not remove all coupling. Producer and consumer still share semantic contract
about event meaning and schema. Therefore, async lowers coupling, it does not eliminate
contract discipline.

## Pros
- **Temporal decoupling:** Async communication allows producer progress even when
  consumers are slow or temporarily unavailable.
- **Controlled failure behavior:** Timeouts, retries, and breakers keep partial failures
  from cascading uncontrollably.
- **Independent deployability:** Contract versioning and compatible evolution reduce
  coordinated release pressure.
- **Scalable fan-out:** Pub/sub supports adding new downstream capabilities with minimal
  producer change.
- **Protocol flexibility:** REST and gRPC provide practical synchronous options for
  different interoperability and performance priorities.

## Cons
- **Operational overhead:** Brokers, registries, schema management, and tracing add
  platform complexity.
- **More failure modes:** Network and distributed runtime create issues absent in
  in-process monolith calls.
- **Consistency lag:** Async workflows often deliver eventual, not immediate,
  cross-service consistency.
- **Contract governance burden:** Poor API/message evolution can break many consumers.
- **Hybrid mental complexity:** Teams must reason across sync and async semantics in the
  same business flow.

## Alternatives
- **Shared database (anti-pattern)** - Services coordinate by reading/writing common
  tables instead of explicit IPC contracts; this lowers short-term effort but creates
  tight schema coupling and weak ownership boundaries.
- **gRPC over REST for sync** - Both are request/response; gRPC emphasizes schema and
  performance, while REST emphasizes broad compatibility and easier ad hoc debugging.
- **Direct async HTTP callbacks** - Producer posts directly to consumer webhooks without
  broker; simpler initially, but higher location/availability coupling than broker-based
  messaging.
- **Service mesh for discovery/resilience** - Moves discovery, retries, and breaker-like
  policies to infrastructure sidecars/proxies; reduces app code burden but increases
  platform and policy complexity.

## When to use it
Use synchronous IPC when caller needs immediate decision semantics inside one user
request, such as availability checks or policy validation.

Use asynchronous messaging when work can be processed later, when one action should
trigger multiple independent reactions, or when buffering is needed for burst handling.

Use service discovery whenever instances are dynamic and cannot be safely hardcoded.

## When NOT to use it
Do not introduce distributed IPC patterns inside a single-process monolith where direct
function calls already satisfy reliability and latency requirements.

Do not build long synchronous call chains for workflows that can tolerate delay; this
amplifies tail latency and failure propagation.

Do not adopt async messaging "by default" if team cannot yet run broker operations,
idempotent consumer design, and schema governance reliably.

## Key takeaways / mental model
Think of IPC as a coupling and failure-budget decision.

Synchronous request/response gives immediate answers but ties availability and latency
across services. Asynchronous messaging loosens temporal coupling and improves fan-out,
but introduces eventual consistency and operational discipline requirements.

Design for partial failure from day one: explicit timeouts, bounded retries, circuit
breakers, and dynamic discovery are baseline hygiene. Treat contract evolution as a
first-class engineering responsibility, not release-day cleanup.

If you keep one rule: choose IPC style by business timing needs and failure tolerance,
not by protocol popularity.

## Self-check questions
1. Your checkout endpoint has 400 ms p95 budget and calls three services synchronously.
   Which calls would you keep sync, which would you move async, and how would you set
   timeout and retry budgets to avoid cascading failure?
2. `Order Service` now must notify `Kitchen`, `Accounting`, and a new `Fraud` service.
   Compare one-to-many pub/sub versus direct synchronous fan-out and explain trade-offs
   in coupling, latency, and failure handling.
3. A mobile app still depends on `status` string, but backend wants lifecycle object.
   Propose a 90-day migration plan with versioning, monitoring, and sunset criteria.
4. During incident, one availability zone has high packet loss. With client-side
   discovery, what load-balancing and retry behavior should clients apply to avoid making
   the outage worse?
5. Your broker guarantees at-least-once delivery and duplicates caused double billing.
   Design an idempotent consumer strategy with concrete deduplication key and storage.
6. A team says "async means no coupling." Use temporal, location, and contract coupling
   to explain what async reduces and what still must be governed.

## References
- Microservices Patterns (Chris Richardson), Chapter 3: "Interprocess communication in a microservice architecture"
- [microservices-patterns/02 - Decomposition strategies](02-decomposition-strategies.md)
- [system-design/12 - API design and communication](../../system-design/lessons/12-api-design-communication.md)
- [ddia/06 - Encoding and schema evolution](../../ddia/lessons/06-encoding-and-schema-evolution.md)
