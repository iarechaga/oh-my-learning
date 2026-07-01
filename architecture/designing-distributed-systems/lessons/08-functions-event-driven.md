---
id: designing-distributed-systems/08
subject: designing-distributed-systems
title: "Functions and Event-Driven Processing"
slug: functions-event-driven
status: drafted
mastery:
seniority: mid
source: "Designing Distributed Systems (Brendan Burns), Chapter 9 (FaaS and Event-Driven Processing)"
prerequisites: [designing-distributed-systems/05]
created: 2026-07-01
updated: 2026-07-01
---

# Functions and Event-Driven Processing

## TL;DR
Functions-as-a-Service (FaaS, "serverless") takes the unit of deployment down from a long-running service to a single stateless function that the platform runs on demand, one invocation per event, and scales from zero to thousands of parallel instances automatically. It shines for event-driven glue - "when X happens, run this small handler" - because you pay only per invocation and never manage servers. Its cost is real and specific: functions are ephemeral and stateless (no in-memory state survives), suffer cold-start latency, and get expensive and awkward when abused for steady, high-throughput, or long-running work that a normal service would handle better.

## The idea
Every serving pattern so far assumes a *long-running* process: a replica, a shard, a leaf - each boots, then sits waiting for requests for hours or days. That model is wasteful for work that is **occasional and bursty**. If a handler runs for 50 ms a few times a minute, keeping a replica (or several, for availability) alive 24/7 to serve it is mostly paying for idle time.

FaaS flips the model. You upload a **function** - a small piece of stateless code with a defined input and output - and the platform is responsible for running it *only when an event triggers it*, spinning up an instance per invocation, running to completion, and tearing it down. There are no servers you provision, no replicas you size, no idle capacity you pay for between events. Scaling is automatic and elastic: 1 event -> 1 instance; 10,000 simultaneous events -> up to thousands of instances in parallel, then back to **zero** when the events stop.

This fits hand-in-glove with **event-driven architectures**: systems built as "when this happens, do that." A file lands in object storage -> a function resizes it. A message arrives on a queue -> a function processes it. An HTTP request hits an endpoint -> a function answers it. The function is the reusable *reaction* to an event, and because it is tiny and stateless it is the smallest possible building block in this subject - smaller than a container, though it usually runs *in* one under the hood.

The pattern's appeal (zero idle cost, effortless scaling, tiny unit) and its constraints (ephemeral, stateless, cold starts, bad at long/steady work) come from the same design choice: the platform, not you, owns the process lifecycle, and it optimizes for "start fast, run briefly, disappear."

## How it works

### The execution model: triggered, ephemeral, one-shot
Three properties define how a function runs, and each drives a consequence you must design around.

1. **Event-triggered.** A function does not run on a schedule you keep alive; it runs because an *event source* fired - an HTTP request, a queue message, a storage change, a timer, a pub/sub topic. The platform wires the event source to your function.
2. **Ephemeral and stateless.** Each invocation gets a fresh (or reused) sandbox with no guaranteed memory of previous runs. You must not keep application state in the function's memory or local disk between invocations - it can vanish at any time. All state goes to an external store (a database, cache, or object store).
3. **One invocation per event (auto-scaled).** The platform runs one function instance per concurrent event and scales the instance count to match event volume, including down to zero when idle. You never choose a replica count.

```text
   event source                platform                  external state
  +-------------+   fires    +-----------+   read/write  +-------------+
  | queue / http| ---------> |  Function | <-----------> | DB / cache  |
  | storage /   |            | (1 inst   |               | object store|
  | timer       |            |  per event)|              +-------------+
  +-------------+            +-----------+
                              spins up on event,
                              runs, then disappears
```

### Cold starts: the latency you inherit for scaling to zero
Because instances disappear when idle, the *next* event after a quiet period has no warm instance waiting - the platform must create one: allocate a sandbox, load your code and runtime, initialize dependencies. That startup delay is a **cold start**, and it is added to that request's latency (often tens of milliseconds to a few seconds depending on runtime and package size). A subsequent event that reuses the still-warm instance is a **warm start** with no such penalty.

Cold starts are the direct price of scaling to zero, and they shape when FaaS is appropriate:

- Fine for asynchronous, background, or bursty work where an occasional extra second does not matter.
- Painful for latency-critical synchronous user requests, where a cold start makes some users randomly slow. Mitigations exist (provisioned/warm instances kept alive, smaller packages, lighter runtimes), but "keep instances warm" partly gives back the zero-idle-cost benefit.

### Statelessness forces state outward - and demands idempotency
Since nothing survives between invocations, every function is stateless by construction; state lives in external stores. Two consequences:

- **No local caching across invocations** (reliably). A warm instance *might* reuse a cached value, but you cannot depend on it - design as if each call starts fresh.
- **Idempotency is usually required.** Most event sources deliver **at-least-once** (a queue may redeliver a message; a storage notification may fire twice). So a function must be safe to run more than once for the same event - check-then-act, dedup keys, conditional writes - exactly like an idempotent queue consumer (this connects directly to work queues, lesson 10, and pub/sub semantics in [system-design/11](../../system-design/lessons/11-pubsub-distributed-queues.md)).

### The cost model: pay-per-invocation, and when it inverts
FaaS billing is per *invocation* and per *resource-time* (memory x duration). This makes the economics sharply different from a running service:

- **Cheap when idle or bursty:** at low or spiky volume, you pay ~nothing between events. A service would bill for 24/7 replicas regardless.
- **Expensive when steady and high-volume:** at sustained high request rates, per-invocation pricing can exceed the flat cost of a few always-on replicas that are busy anyway. There is a crossover point where "just run a service" is cheaper.
- **Bad for long-running work:** you pay for the whole duration, and platforms cap function runtime (often minutes). A 30-minute job is both costly and may hit the timeout - use a batch job or a normal worker instead.

### Worked example 1: image thumbnailing on upload (the ideal fit)
A photo app must generate a thumbnail whenever a user uploads an image.

1. A user uploads `photo.jpg` to object storage. The storage service emits an `ObjectCreated` event.
2. The platform triggers the `makeThumbnail` function, passing the object key. It spins up an instance (cold if none is warm).
3. The function reads `photo.jpg` from storage, resizes it, and writes `photo_thumb.jpg` back to storage. It keeps *no* state locally.
4. The function returns; the instance is torn down (or kept briefly warm for the next upload).
5. During a marketing spike, 5,000 photos upload in a minute -> the platform runs up to thousands of `makeThumbnail` instances in parallel, then scales to zero when the spike ends.

Why it fits: work is event-driven, bursty, short, stateless, and tolerant of an occasional cold-start delay. You never provisioned or paid for idle capacity, and it absorbed a huge burst automatically.

### Worked example 2: at-least-once delivery forces idempotency
A function processes `OrderPlaced` messages from a queue and charges the customer.

1. Message `order=ORD-88` arrives; the platform invokes `chargeCustomer`.
2. The function charges the card and writes the order... but the network drops before it acknowledges the message.
3. The queue, seeing no ack, **redelivers** `order=ORD-88`; the platform invokes `chargeCustomer` again.
4. Naive version: the customer is charged twice - a bug caused entirely by the ephemeral, at-least-once model.
5. Correct version: the function first attempts to insert `ORD-88` into a `processed_orders` table with `order_id` as primary key inside a transaction. On the redelivery, the insert fails with a unique-constraint violation, so the function skips the charge and simply acknowledges. Exactly one charge despite two invocations.

The example shows that FaaS does not remove distributed-systems concerns - it inherits them; statelessness + at-least-once *requires* idempotent handlers.

### Worked example 3: cold start makes it the wrong tool for a hot synchronous path
An API endpoint that must respond in under 100 ms at p99 is implemented as a function.

- At steady traffic, warm instances handle most requests in ~20 ms. Fine.
- Traffic dips for a few minutes overnight; instances scale to zero.
- The next user request has no warm instance -> a cold start adds ~800 ms -> that user waits ~820 ms, blowing the 100 ms budget.
- Because scale-downs happen continually, a fraction of users randomly hit cold starts all day - an unpredictable p99.

Options: keep N instances provisioned/warm (which reintroduces the always-on cost you were avoiding and edges you back toward just running a [replicated service](05-replicated-load-balanced.md)), shrink the package/runtime to cut cold-start time, or accept that a latency-critical synchronous API is a poor FaaS fit and run it as a normal service. The right call is often the last one - which is exactly *when NOT to use* the pattern.

## Pros
- **Zero idle cost / pay-per-use:** you pay only when events occur; nothing runs (or bills) between them.
- **Effortless elastic scaling:** the platform scales instances from zero to thousands automatically to match event volume, with no replica sizing.
- **No server management:** no provisioning, patching, or capacity planning of long-running hosts - the smallest operational surface of any pattern here.
- **Natural fit for event-driven glue:** the function is a clean, reusable reaction to an event, ideal for "when X, do Y" wiring between services.

## Cons
- **Cold-start latency:** scaling to zero means some invocations pay a startup penalty - bad for latency-critical synchronous paths.
- **Ephemeral and stateless:** no reliable in-memory/local state between invocations; all state must be externalized, and at-least-once delivery forces idempotent handlers.
- **Poor fit for long-running or steady high-volume work:** runtime caps and per-invocation pricing make long jobs fail or cost more than a plain service past a crossover volume.
- **Operational blind spots:** distributed tracing, local debugging, and reasoning about concurrency across thousands of transient instances are harder than with a fixed fleet.

## Alternatives
- **Replicated long-running service:** when work is steady, high-throughput, latency-critical, or long-running - a warm fleet avoids cold starts and is cheaper at sustained load (lesson 05).
- **Work queue with worker pool:** for high-volume asynchronous task processing where you want control over concurrency and throughput, a pool of long-lived workers pulling a queue is often better (lesson 10).
- **Batch / scheduled jobs:** for large finite computations or periodic heavy work, a batch job (or cron-triggered container) fits where a time-capped function does not (lessons 11-12).
- **Sidecar/ambassador in a service:** for cross-cutting concerns tied to a running app, a co-located container is a better home than a standalone function (lessons 02-03).

## When to use it
- The work is event-driven and bursty or infrequent, so paying only per invocation beats running idle replicas.
- Each unit of work is short, stateless, and can be made idempotent.
- You want automatic scale-to-zero and scale-out with no capacity planning.
- Occasional cold-start latency is acceptable (asynchronous/background work), or the traffic keeps instances warm enough.

## When NOT to use it
- The path is latency-critical and synchronous, where random cold starts violate the latency budget - run a warm service instead.
- The workload is steady and high-volume, past the crossover where per-invocation pricing exceeds a few busy always-on replicas.
- The task is long-running (minutes+) and risks the platform's execution timeout - use a batch job or worker.
- The work needs substantial in-memory state or cross-invocation caching that statelessness cannot provide.

## Key takeaways / mental model
Think of FaaS as motion-sensor lights instead of leaving the lights on all night. The light (function) switches on only when someone walks by (an event), stays on just long enough, and costs nothing while the hallway is empty (scale to zero) - but there is a brief flicker-to-full-brightness when it first triggers (cold start), and it is the wrong choice for a room you need brightly lit continuously (steady, latency-critical load). Two rules of thumb:

1. **FaaS trades idle cost for cold-start latency and statelessness.** Perfect for bursty, short, stateless, event-driven work; poor for hot synchronous paths, steady high volume, or long jobs - know the crossover.
2. **The platform owning the lifecycle does not repeal distributed-systems rules.** Externalize all state and make every handler idempotent, because event delivery is at-least-once and instances vanish without warning.

## Self-check questions
1. What are the three defining properties of the FaaS execution model, and what design consequence does each impose on your function code?
2. Why do cold starts exist, and precisely which kinds of workloads do they make FaaS a poor fit for? Name two mitigations and the benefit each gives back.
3. Why must most functions be idempotent? Walk through the double-charge scenario and the fix, and name the delivery guarantee that causes it.
4. Describe the FaaS cost model and the crossover point where a normal long-running service becomes cheaper. Give an example workload on each side of the crossover.
5. For the image-thumbnailing example, list every property that makes it an ideal FaaS fit, and change one property so that it would no longer be a good fit.
6. You need a synchronous API at p99 < 80 ms and also a nightly 40-minute data export. Which of these should be a function and which should not, and what would you use for the other? Justify both.

## References
- Designing Distributed Systems (Brendan Burns), Chapter 9: "Functions and Event-Driven Processing"
- [designing-distributed-systems/05 - Replicated Load-Balanced Services](05-replicated-load-balanced.md)
- [system-design/11 - Pub/Sub and distributed queues](../../system-design/lessons/11-pubsub-distributed-queues.md)
