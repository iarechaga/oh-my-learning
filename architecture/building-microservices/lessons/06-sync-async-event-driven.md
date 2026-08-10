---
id: building-microservices/06
subject: building-microservices
title: "Synchronous vs Asynchronous and Event-Driven"
slug: sync-async-event-driven
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 5"
prerequisites: [building-microservices/03, building-microservices/05]
created: 2026-08-10
updated: 2026-08-10
---

# Synchronous vs Asynchronous and Event-Driven

## TL;DR
Synchronous communication (REST/RPC over HTTP or gRPC) is simple to reason about but chains availability and latency across every hop — a slow or down downstream service blocks the whole chain. Asynchronous, event-driven communication (via a message broker or event stream) decouples services in time, trading immediate consistency for resilience against downstream slowness, at the cost of embracing eventual consistency and more complex failure reasoning. Most production systems need both, chosen deliberately per interaction, not as a system-wide default.

## The idea
Lesson 05 introduced request-response vs. event-based communication conceptually. This lesson goes deep on the concrete mechanics: what actually happens over the wire, what the specific failure modes are, and how to reason quantitatively about the trade-off, since this is one of the decisions with the largest blast radius in a microservice system — get it wrong and you either build a fragile system prone to cascading failures, or you build a needlessly complex eventually-consistent system where a simple synchronous call would have sufficed.

## How it works

### Synchronous communication: REST/RPC over HTTP or gRPC

The caller sends a request and blocks (or at least logically waits) until it gets a response, an error, or a timeout. Two dominant concrete technologies:

- **REST over HTTP** (often HTTP+JSON) — resource-oriented, uses HTTP verbs and status codes, human-readable payloads, widely tooled, easy to debug with a browser or curl, but comparatively verbose (JSON parsing overhead, larger payloads) and its typing is only as strict as your discipline (schemas via OpenAPI are optional, not enforced by the wire format itself).
- **gRPC** — RPC-style, uses Protocol Buffers for a strongly-typed, binary, compact wire format over HTTP/2, supports streaming, and is significantly faster to (de)serialize than JSON at scale. The cost: less human-readable on the wire (you need tooling to inspect traffic), a steeper adoption curve (schema compilation step, cross-language codegen), and less ubiquitous browser/tooling support than plain REST.

Both are still fundamentally *synchronous request-response* at the semantic level even though the underlying transport (HTTP/2 for gRPC) supports multiplexing — the calling code is still waiting on an answer before it can proceed with its own logic.

### The core problem: latency and availability compound across a chain

This is the mechanical heart of the lesson. When Service A calls Service B synchronously, and B calls C synchronously to answer A:

- **Latency adds up.** A's total response time is at minimum its own processing time plus B's total response time (which itself includes C's). A synchronous chain of N hops has a total latency that is, in the worst case, the *sum* of every hop's latency, not the max.
- **Availability multiplies down.** If each service in a chain of N synchronous calls is independently available `p` percent of the time, the chain's overall availability is roughly `p^N` (each link must succeed for the whole chain to succeed). Four services each at 99.9% (`0.999^4 ≈ 0.996`) — the chain is only about 99.6% available, worse than any individual service. Ten services at 99.9% each drops the chain below 99%.
- **A slow downstream service blocks the whole chain**, not just its own callers, but its callers' callers, potentially all the way up. If C becomes slow (not down — slow), and A has no timeout on its call to B (which has no timeout on its call to C), A's request threads/connections can pile up waiting, and A itself can run out of capacity — a slow C has now taken down A, which C's team may never even know exists. This is precisely the failure mode Lesson 14 (resilience: timeouts, retries, bulkheads, circuit breakers) exists to defend against.

### Worked example: latency and availability math

Order placement requires `order-service` to synchronously call `inventory-service`, which synchronously calls `warehouse-service` to check physical stock.

- Typical latencies: `order-service` own logic 20ms, `inventory-service` own logic 30ms, `warehouse-service` own logic 50ms.
- Chained synchronously: total latency for the customer ≈ 20 + 30 + 50 = 100ms in the best case (ignoring network transit time, which adds further per-hop overhead).
- Now suppose `warehouse-service` has a bad day and its p99 latency balloons to 3 seconds. Every checkout that hits that slow path now takes over 3 seconds, and if `inventory-service` has, say, a connection pool of 50 threads and checkout volume is high, those threads fill up waiting on `warehouse-service` — `inventory-service` starts rejecting or queuing *unrelated* requests it could otherwise have served instantly, because its capacity is consumed waiting on the slow dependency. The failure has now spread from `warehouse-service` to `inventory-service` to (potentially) `order-service`, none of which had anything wrong with their own code.
- Availability: if `order-service`, `inventory-service`, and `warehouse-service` are each independently 99.9% available, the synchronous chain's effective availability for checkout is roughly `0.999 × 0.999 × 0.999 ≈ 0.997`, i.e., about 2.6 hours of extra downtime per year compared to a single 99.9% service, purely from chaining.

### Asynchronous, event-driven communication: message brokers and event streams

Instead of A calling B and waiting, A publishes a message describing what happened, and a broker (RabbitMQ, ActiveMQ — traditional message queues) or an event stream (Kafka, Kinesis — log-based, replayable, ordered-per-partition) takes responsibility for delivering it to whichever consumers are listening, whenever they're ready to process it.

- **Traditional message brokers/queues** typically deliver a message to a consumer and remove it once acknowledged; good fit for point-to-point work distribution (a job queue) or classic pub/sub fan-out.
- **Log-based event streams** (Kafka-style) retain events for a configurable retention window (or indefinitely), allow multiple independent consumers to read at their own pace and even replay history, and guarantee ordering *within* a partition — a strong fit when you want new consumers to be able to catch up on history, or want an authoritative, replayable log of "everything that happened."

The mechanical payoff: A's own request completes as soon as the message is durably published to the broker — it does not wait for B or C to process it. A's latency and availability are now decoupled from B's and C's entirely. If `warehouse-service` in the example above is having a bad day, `order-service` publishing `OrderPlaced` is unaffected; `warehouse-service` will process the backlog once it recovers, and the customer's checkout call itself stays fast.

The cost is that A no longer knows, at the moment its own call returns, whether B and C actually succeeded — the system is now **eventually consistent** rather than immediately consistent. Handling that (what does the UI show while inventory reservation is still pending? what happens if it ultimately fails?) is real design work, not free.

### Worked example: the same flow, both ways

**Synchronous version:** `order-service` receives "place order," calls `payment-service.authorize()` and waits, calls `inventory-service.reserve()` and waits, then returns `200 OK` with a confirmed order to the customer. If `inventory-service` is down, the whole checkout fails immediately and visibly — arguably a *good* thing here, since inventory failing to reserve genuinely should block the order.

**Asynchronous version:** `order-service` receives "place order," creates the order in a `PENDING` state, publishes `OrderPlaced`, and returns `202 Accepted` with an order ID immediately — the checkout call itself is fast and decoupled from payment/inventory availability. `payment-service` and `inventory-service` independently consume `OrderPlaced`, each doing their work and publishing `PaymentAuthorized`/`PaymentFailed` and `InventoryReserved`/`InventoryUnavailable`. A saga-coordinating piece of logic (Lesson 08) watches for these outcomes and moves the order to `CONFIRMED` or `CANCELLED`, notifying the customer (e.g., via a status page, push notification, or email) once the outcome is known.

Which is right depends on the actual requirement: if the business genuinely needs "tell the customer definitively, right now, whether the order succeeded" — including because a failed inventory reservation should block the order outright — synchronous is the more honest fit, and the failure mode above (chain blocks on a slow inventory service) is a resilience problem to solve with timeouts/circuit breakers (Lesson 14), not necessarily a reason to go async. If the business can tolerate "we'll confirm shortly" and the priority is protecting checkout latency/availability from downstream slowness, async is the better fit — but then eventual consistency, saga coordination (Lesson 08), and customer-facing "pending" states become real product requirements, not just implementation details.

## Pros
- **Synchronous (REST/gRPC)**: simple mental model, immediate answer, easy to debug (especially REST), mature tooling.
- **Asynchronous (brokers/streams)**: decouples caller's availability/latency from downstream services, naturally supports one-to-many fan-out, buffers load spikes (the broker absorbs a burst that a downstream consumer processes at its own pace), enables replay (log-based streams) for recovery or new consumers.

## Cons
- **Synchronous**: latency and availability compound across chained calls; a slow downstream service can exhaust caller resources and cascade upward without protection (Lesson 14).
- **Asynchronous**: eventual consistency requires real design work (what does the caller see in the interim?); requires broker/stream infrastructure with its own operational burden; harder to trace a single business operation across services without deliberate tooling (correlation IDs, Lesson 13); message ordering, duplicate delivery, and poison messages become real concerns to design for.

## Alternatives
- **Synchronous with strict resilience controls** — keep the simple request-response model but bound the blast radius with timeouts, circuit breakers, and bulkheads (Lesson 14), rather than switching to async purely to dodge cascading failure.
- **Hybrid: synchronous for the "must-answer-now" write path, async for everything downstream of it** — e.g., synchronously validate and accept an order (fast, bounded scope), then do the heavier multi-service fulfillment work asynchronously. This is extremely common in practice and captures most of the benefit of both styles.

## When to use it
- **Synchronous** when the caller cannot meaningfully proceed without the answer (e.g., "is this valid?"), the interaction is a simple read, or the business genuinely requires an immediate, definitive answer.
- **Asynchronous/event-driven** when downstream work can be decoupled in time from the triggering request, when you want to protect the caller's availability from a downstream service's problems, or when multiple independent consumers need to react to the same fact.

## When NOT to use it
- Don't use long synchronous chains (3+ hops) without resilience controls (Lesson 14) — this combination is one of the most common root causes of cascading production outages in microservice systems.
- Don't reach for async/event-driven purely because it feels more "microservices native" when the interaction genuinely needs an immediate, consistent answer — you'll pay the eventual-consistency and operational cost of a broker for no real benefit, and you'll need to build UX/product handling for a "pending" state that didn't need to exist.

## Key takeaways / mental model
Synchronous calls chain latency (additive) and multiply unavailability (`p^N`) across every hop — a slow link anywhere in the chain is felt everywhere upstream. Asynchronous, event-driven communication breaks that chain by decoupling the publisher's completion from the consumer's processing, at the cost of embracing eventual consistency and needing real infrastructure (a broker or event stream) plus real design work for "what do we show while we wait." Choose per-interaction based on whether an immediate, consistent answer is a genuine requirement or just a default assumption.

## Self-check questions
1. Four services are chained synchronously, each independently 99.95% available. Roughly what is the chain's overall availability, and why is it worse than any individual service's?
2. Why does a slow (not down) downstream service tend to be more dangerous to a synchronous caller than a downstream service that is cleanly down and fails fast?
3. In the asynchronous order-placement example, what new product/UX requirement does the system now have that the synchronous version didn't, and why?
4. When would you choose gRPC over plain REST+JSON for a synchronous interaction, and what do you give up?
5. A team switches a slow, occasionally-cascading synchronous call to async purely to "fix" the cascading failures, without changing anything about how the caller communicates the outcome to its own users. What have they likely broken, and what would have been a more targeted fix?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 5: "Microservice Communication Styles"
- Related: `building-microservices/14` (Resilience) for the timeout/circuit-breaker toolkit that makes synchronous chains safer; `ddia/11` (Transactions) and `ddia/09` (Replication Lag and Consistency) for the theory behind eventual consistency that async communication commits you to.
