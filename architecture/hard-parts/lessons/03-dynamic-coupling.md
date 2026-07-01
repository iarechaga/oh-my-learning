---
id: hard-parts/03
subject: hard-parts
title: Dynamic Coupling
slug: dynamic-coupling
status: drafted
mastery:
seniority: senior
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 2
prerequisites: [hard-parts/02]
created: 2026-06-30
updated: 2026-06-30
---

# Dynamic Coupling

## TL;DR
Dynamic coupling describes how architecture quanta interact at runtime.
Use three dimensions to reason about each interaction: communication, consistency, and coordination.
The right design is a chosen trade-off point in this 3-D space, not a default.

## The idea
Lesson 02 covered static coupling: what gets packaged together, what gets deployed together, and where structural boundaries sit.

Dynamic coupling asks a different question: once those boundaries are running, how do quanta call one another under real traffic and failure?

If Checkout needs Payment, does Checkout block and wait, or publish work and continue?
If a downstream step fails, must all participants be mutually consistent now, or can they converge later?
Does one workflow driver coordinate all transitions, or do services react through events?

These choices shape latency, availability, operability, and incident behavior.
They are architecture decisions, not implementation details.

The model uses three spectra:
1. Communication: synchronous <-> asynchronous.
2. Consistency: atomic <-> eventual.
3. Coordination: orchestrated <-> choreographed.

The dimensions are largely orthogonal, so one choice from each axis can be combined with the others.
2 x 2 x 2 = 8 combinations, which is the basis for saga pattern variants studied in lesson 14.

## How it works
Treat every cross-quantum call as a deliberate coordinate choice.
Pick one point in the three-dimensional space; that point defines what you optimize and what risk you absorb.

### Communication dimension: synchronous vs asynchronous
Communication asks whether the caller blocks waiting for completion or continues after dispatch.

Synchronous means the caller waits for a response.
Common shapes are HTTP request/response, direct RPC, and unary gRPC.

Asynchronous means the caller sends a message/event and continues.
Common shapes are queues, event buses, and command topics.

### Synchronous: strengths and costs
Synchronous interactions are easy to reason about.
The call returns success/failure in one place.
Error handling is immediate and local.

But synchronous chains couple both latency and availability.
Every downstream hop adds waiting time, and every dependency can block user response.

#### Worked example A: availability multiplication in a sync chain
Suppose one user request needs four synchronous services,
each with 99.9% availability.

1. Per-service availability = 99.9% = 0.999.
2. Combined availability = 0.999 x 0.999 x 0.999 x 0.999.
3. 0.999^4 = 0.996005996001.
4. End-to-end availability is about 99.6006%.

So four "three-nines" components produce about 99.6% as a chain.
This is why deep synchronous dependencies quietly reduce reliability.

### Asynchronous: strengths and costs
Asynchronous interactions improve responsiveness.
The caller can acknowledge quickly while downstream work continues.
Queues and brokers can absorb bursts and smooth load.

The cost is complexity.
You need explicit handling for retries, idempotency, deduplication, ordering, poison messages, and delayed failure semantics.

The hardest part is not transport.
It is error handling after the caller already got a response.

### Worked example 1: Sysops Squad checkout and ticket flow
A Sysops Squad fan checkout needs Ticketing and Payment.
Assume these median latencies:

- Gateway overhead: 20 ms
- Checkout logic: 30 ms
- Ticketing call: 80 ms
- Payment authorization: 250 ms
- Response overhead: 20 ms

#### Variant 1: synchronous payment
1. Client sends `POST /checkout`.
2. Checkout reserves ticket synchronously.
3. Checkout calls Payment synchronously.
4. Checkout returns final success/failure.

Approx user latency:
20 + 30 + 80 + 250 + 20 = 400 ms.

If path availability is:
Gateway 99.95%,
Checkout 99.9%,
Ticketing 99.9%,
Payment 99.5%,
then combined path availability is:
0.9995 x 0.999 x 0.999 x 0.995 = 0.9925189944975,
about 99.2519%.

#### Variant 2: asynchronous event publication
1. Client sends `POST /checkout`.
2. Checkout validates and stores order intent.
3. Checkout publishes `OrderPlaced` or `TicketCreated`.
4. Checkout returns `202 Accepted` with order id.
5. Payment consumes event and processes later.
6. A status event updates order state.

Initial user latency can drop to roughly:
20 + 30 + 15 + 20 = 85 ms.

Responsiveness improves,
but final payment result is no longer immediate.
Product and operations must handle pending and failed states explicitly.

### Consistency dimension: atomic vs eventual
Consistency asks whether participants must be aligned when the interaction finishes, or can converge later.

Atomic consistency provides all-or-nothing semantics at interaction end, which is strong for correctness where invariants are strict.

Eventual consistency allows temporary divergence.
Participants converge later through retries, replays, and compensating actions.

### Atomic consistency trade-offs
Benefits:
- clear invariants,
- easier reasoning,
- fewer intermediate business states exposed.

Costs:
- distributed atomicity can reduce scale,
- it can increase latency,
- and it can reduce availability under partial failure.

A common pattern is local atomicity per service, with cross-service eventual consistency via sagas.

### Eventual consistency trade-offs
Benefits:
- better resilience under partitions and partial outages,
- better decoupling and independent scaling.

Costs:
- users and operators see intermediate states,
- reconciliation is required,
- correctness depends on idempotent, replay-safe handlers.

You must model states like `PENDING_PAYMENT`, `PAYMENT_FAILED`, and `COMPENSATING`, not only `COMPLETED`.

### Coordination dimension: orchestration vs choreography
Coordination asks who drives the workflow.

Orchestration means a central mediator tracks state and commands next steps.
Choreography means each service reacts to events without a central driver.

### Orchestration trade-offs
Benefits:
- one place to reason about process state,
- easier end-to-end visibility,
- clearer ordering and compensation control.

Costs:
- potential bottleneck,
- central dependency risk,
- coordinator availability is critical.

### Choreography trade-offs
Benefits:
- distributed control,
- fewer centralized bottlenecks,
- strong service autonomy.

Costs:
- harder global observability,
- emergent behavior can surprise,
- cross-service debugging is harder.

Lesson 13 dives deep into this axis.
Here we focus on how it fits dynamic coupling.

### Worked example 2: three-axis combination map (2 x 2 x 2)
Each interaction picks one side from each axis.
That produces eight combinations, which align with saga pattern names in lesson 14.

```
+----+---------------+-------------+---------------+--------------------------------+
| #  | Communication | Consistency | Coordination  | Mapping note                   |
+----+---------------+-------------+---------------+--------------------------------+
| 1  | Sync          | Atomic      | Orchestrated  | Saga variant named in lesson14 |
| 2  | Sync          | Atomic      | Choreographed | Saga variant named in lesson14 |
| 3  | Sync          | Eventual    | Orchestrated  | Saga variant named in lesson14 |
| 4  | Sync          | Eventual    | Choreographed | Saga variant named in lesson14 |
| 5  | Async         | Atomic      | Orchestrated  | Saga variant named in lesson14 |
| 6  | Async         | Atomic      | Choreographed | Saga variant named in lesson14 |
| 7  | Async         | Eventual    | Orchestrated  | Saga variant named in lesson14 |
| 8  | Async         | Eventual    | Choreographed | Saga variant named in lesson14 |
+----+---------------+-------------+---------------+--------------------------------+
```

Do not memorize this as taxonomy.
Use it to force explicit decisions.

### Worked example 3: why async error handling is the crux
Consider this event-driven flow:

1. Checkout returns `202` for order `O-731`.
2. `OrderPlaced(O-731)` is emitted.
3. Inventory reserves seats.
4. Payment retries fail after timeout budget.

The client already saw acceptance.
So a later failure must be handled as a business process, not as a synchronous exception.

Without explicit handling,
you may keep inventory reserved without payment,
or expose contradictory order states.

A safe design typically includes:
1. Mark order `PAYMENT_FAILED`.
2. Emit `ReleaseInventory(O-731)`.
3. Notify user with a retry/payment-recovery path.
4. Ensure idempotent consumers for duplicate events.
5. Trace all steps by correlation id.

This is the core lesson:
asynchronous systems are defined by delayed failure behavior.

## Pros
### Why this three-dimension model is powerful
- It turns vague architecture discussions into explicit decisions.
- It avoids false binaries like "sync or async" as a complete answer.
- It exposes trade-offs directly in terms of latency, availability, and operability.
- It scales from a single endpoint to system-wide interaction mapping.
- It creates common language across teams and design reviews.

## Cons
### Limits/pitfalls
- The model can look simple while hiding hard implementation work.
- Teams may name coordinates but ignore idempotency, retries, and reconciliation.
- The axes are mostly orthogonal, not perfectly independent in real platforms.
- Over-modeling small local flows can add ceremony with little value.
- Success still depends on fundamentals: observability, ownership, and operations maturity.

## Alternatives
- **Sync-vs-async only**: a useful starter model,
  but incomplete because it ignores consistency and coordination.
- **Strong-vs-eventual consistency only**: useful for data semantics,
  but incomplete for runtime call behavior and workflow control.
- **Orchestration-vs-choreography only**: useful for control topology,
  but incomplete without communication and consistency semantics.
- **Technology defaults ("just REST" or "just events")**:
  easy to adopt,
  but often hide trade-offs until production incidents reveal them.

## When to use it
Use this model whenever interactions cross service/quantum boundaries,
especially when:
1. SLOs are strict.
2. Multiple teams share the workflow.
3. Business invariants are critical.
4. Failure recovery must be explicit before coding.

## When NOT to use it
Do not force full 3-axis analysis for trivial local calls
inside one process and one transaction boundary.

If a use case is a simple local function plus one DB commit, full classification may be unnecessary overhead.

Also, do not treat the model as a substitute for execution discipline.
Without telemetry,
idempotency,
and incident readiness,
coordinates alone do not make systems reliable.

## Key takeaways / mental model
Dynamic coupling is runtime behavior;
static coupling is structural arrangement.

For each distributed interaction,
choose a coordinate in three dimensions:
communication,
consistency,
coordination.

There is no universally correct coordinate.
There are only trade-offs aligned to business priorities.

Mental model:
design the failure path first,
because runtime architecture is mostly about what happens when one step fails late.

## Self-check questions
1. How does dynamic coupling differ from static coupling from lesson 02?
2. Why does a synchronous chain reduce end-to-end availability even with high-availability services?
   Recompute the 4 x 99.9% example.
3. In the Sysops Squad checkout flow,
   what do you gain and lose when moving from synchronous payment to `OrderPlaced`?
4. Give one situation where atomic consistency is required,
   and one where eventual consistency is acceptable.
5. Why is delayed error handling the hardest part of asynchronous systems,
   and what controls make it safe?
6. How can orchestration/choreography be independent from sync/async,
   yet still influence overall behavior?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 2
- [02-architecture-quantum-static-coupling.md](02-architecture-quantum-static-coupling.md)
- [13-distributed-workflows-orchestration-choreography.md](13-distributed-workflows-orchestration-choreography.md)
- [14-transactional-sagas.md](14-transactional-sagas.md)
- [09-replication-lag-and-consistency.md](../../ddia/lessons/09-replication-lag-and-consistency.md)
