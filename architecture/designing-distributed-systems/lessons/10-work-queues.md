---
id: designing-distributed-systems/10
subject: designing-distributed-systems
title: "Work Queue Systems"
slug: work-queues
status: drafted
mastery:
seniority: mid
source: "Designing Distributed Systems (Brendan Burns), Chapter 10 (Work Queue Systems)"
prerequisites: [designing-distributed-systems/05]
created: 2026-07-01
updated: 2026-07-01
---

# Work Queue Systems

## TL;DR
A work queue is the fundamental *batch* pattern: a finite pile of independent work items is placed in a queue, and a pool of interchangeable workers pulls items off and processes them in parallel until the queue is empty. It decouples *how much work exists* from *how fast you process it* - add workers to go faster - and it is the backbone of every "process a big list of tasks" system (resize 1M images, send 500k emails, run 10k reports). The whole pattern hinges on items being independent and idempotent, because a worker can die mid-item and its work will be handed to another worker, so any item may be processed more than once.

## The idea
The serving patterns (lessons 05-09) answer *requests* that arrive continuously and must be answered now. A different, enormous class of work is not request-shaped: it is a **finite batch of tasks** you want to grind through as fast as practical, where each task is independent and no user is waiting synchronously for a specific one. Examples: thumbnail every image in a bucket, transcode a backlog of videos, send a marketing blast to every subscriber, recompute recommendations for every user.

For this, the work queue pattern splits the system into two decoupled halves connected by a queue:

- **A source of work** puts items into a **queue** (a durable list of tasks).
- **A pool of workers** independently pulls items from the queue, processes each, and marks it done.

The decoupling is the whole point: the rate at which work is *produced* is separated from the rate at which it is *consumed*. If you have 1,000,000 items and one worker does 10/second, it takes ~28 hours; add 100 identical workers and it takes ~17 minutes. You scale throughput by scaling the worker pool, with no change to the producer and no coordination between workers - each just grabs the next item.

The pattern is deliberately simple, and its simplicity depends on a strict assumption: **items are independent** (processing one does not depend on another) and **idempotent** (safe to process more than once). Both fall out of the failure model below - a worker can crash after taking an item but before finishing, so that item must be safely reassignable and re-runnable.

## How it works

### The shared work queue and the competing-consumers pattern
The core is one queue and many workers reading from it - the "competing consumers" arrangement (contrast with pub/sub fan-out, where every subscriber gets a copy; here each item goes to exactly one worker). See [system-design/11 - Pub/Sub and distributed queues](../../system-design/lessons/11-pubsub-distributed-queues.md) for the queue-vs-topic distinction.

```text
   producer(s)            queue                worker pool
  +-----------+   push   +----------------+   pull   +--------+
  | enqueue   | -------> | [t1 t2 t3 ...   | ------>  |Worker A|
  | tasks     |          |     tN ]       |          |Worker B|
  +-----------+          +----------------+          |Worker C|
                          each item to exactly         ...
                          ONE worker (compete)      +--------+
                                                    (add workers
                                                     -> more speed)
```

Workers are identical and stateless (like a [replicated service](05-replicated-load-balanced.md), but pulling work instead of receiving pushed requests). Because they pull, the system is naturally load-balanced and self-throttling: a worker only takes a new item when it has finished the last one, so fast workers do more and slow workers do less, automatically.

### The visibility-timeout / lease: how the queue survives worker death
The subtle machinery is what happens when a worker takes an item and then dies. A correct work queue does **not** delete an item the instant a worker picks it up. Instead it uses a **lease** (in SQS terms, a *visibility timeout*):

1. A worker *claims* an item; the queue marks it invisible to other workers for a lease period (say 60 s) but keeps it.
2. The worker processes the item. If it finishes, it sends an explicit **acknowledgement (delete)**, and only then does the queue remove the item.
3. If the worker crashes (or takes longer than the lease), it never acks. When the lease expires, the queue makes the item **visible again**, and another worker picks it up.

```text
Worker A: claim(t7)---process---X (crash, no ack)
queue:    t7 invisible for 60s ............ lease expires -> t7 visible again
Worker B:                                    claim(t7)---process---ack -> deleted
```

This guarantees **at-least-once** processing: no item is lost, because an unacknowledged item always comes back. The price is that an item may be processed *more than once* (the crashed worker A might have completed the side effects just before dying, then B redoes them) - which is exactly why items must be idempotent.

### At-least-once + idempotency (not exactly-once)
Just like message queues generally, work queues give at-least-once delivery, and true exactly-once across a crash boundary is impractical. So the standard, correct design is **at-least-once delivery paired with idempotent workers**. A worker must produce the same end state whether it runs an item once or five times:

- Use a dedup/processed-marker keyed by item ID (insert-if-absent inside the transaction that does the work).
- Or make the operation naturally idempotent (writing a derived file at a deterministic path; a conditional/upsert write).

If work is *not* idempotent (e.g. "increment a counter," "charge a card") the naive queue will double-count on redelivery; you must add an idempotency key or a processed-set to make it safe.

### Tuning the lease: too short re-runs, too long stalls
The lease length is the key knob and mirrors the leader-election TTL trade-off (lesson 09):

- **Too short:** a worker that is legitimately still processing a slow item exceeds the lease; the queue re-releases the item and a *second* worker starts it while the first is still going - duplicate work and wasted capacity.
- **Too long:** when a worker really does crash, its item stays invisible for the full lease before anyone retries, stalling that item's completion.
- **Rule of thumb:** set the lease comfortably above the worst-case processing time for an item (or have long-running workers *extend* the lease with periodic heartbeats), so healthy slow work is never re-released but a true crash still recovers reasonably fast.

### Poison items and the dead-letter queue
Some items will fail every time - a corrupt input, a bug that only that item triggers (a "poison pill"). Without protection, such an item is retried forever: worker takes it, fails, lease expires, next worker takes it, fails... consuming capacity and never draining. The fix is a **retry limit + dead-letter queue (DLQ)**: after N failed attempts, move the item to a separate DLQ for human inspection instead of retrying it, so the poison item stops blocking throughput while the rest of the batch flows.

### Worked example 1: draining a 1,000,000-image thumbnail batch, and scaling it
You must thumbnail 1,000,000 images; each takes ~1 s of worker time.

1. A producer enqueues 1,000,000 items (each is an image key). This is fast - just writing task references.
2. Start 10 workers. Aggregate rate ~10 items/s -> ~100,000 s -> ~27.8 hours. Correct but slow.
3. Scale the pool to 200 workers (identical image, more instances). Rate ~200/s -> ~5,000 s -> ~83 minutes. No producer change, no worker coordination - throughput scaled with pool size.
4. As the queue drains toward empty, idle workers simply get nothing on their next pull and can be scaled back down to zero. The batch has a natural end (queue empty), unlike a serving system that runs forever.

The example shows the defining property: *finite work + scale the consumer pool to hit a deadline.* Sizing is arithmetic - to finish 1M 1-second items in 30 minutes you need ~556 workers (`1,000,000 / 1,800 s`).

### Worked example 2: a worker crash, recovered via the lease
Worker C claims item `img-4471` (visibility timeout 60 s) and begins resizing.

1. 20 s in, worker C's node dies. It never acked, so `img-4471` is *not* deleted - it is just invisible.
2. At 60 s the lease expires; the queue makes `img-4471` visible again.
3. Worker F pulls `img-4471`, resizes it, writes `img-4471_thumb.jpg` to a deterministic path, and acks. The queue deletes it.
4. Idempotency check: writing to the *same deterministic path* means even if C had finished the file microseconds before dying, F simply overwrites identical output - no harm. The item is completed exactly once *in effect*, though processed by two workers.

Contrast a non-idempotent version ("append a row to a report table with no dedup"): C might have appended before dying, then F appends again -> a duplicate row. That is the bug the idempotency requirement exists to prevent.

### Worked example 3: a poison item and the DLQ
A batch of 500,000 records includes one malformed record `rec-999` that throws a parse error every time.

1. Worker takes `rec-999`, throws, does not ack; lease expires; another worker takes it, throws... it loops.
2. Without a DLQ, `rec-999` is retried endlessly, permanently occupying a worker slot on each cycle and never draining - and if several such poison items exist, they erode throughput.
3. With a retry limit of 5: the queue tracks delivery count; after the 5th failed attempt, `rec-999` is moved to the DLQ and stops being redelivered.
4. The other 499,999 records drain normally; an operator later inspects the DLQ, fixes or discards `rec-999`. Throughput is protected from the poison item.

## Pros
- **Throughput decoupled from work volume:** scale the worker pool to process a fixed backlog as fast as you need; producer is unaffected.
- **Automatic load balancing and self-throttling:** pull-based workers each take the next item only when free, so fast workers do more with no coordination.
- **Fault tolerance via leases:** an item whose worker dies is automatically reassigned; nothing is lost (at-least-once).
- **Simple and elastic:** identical stateless workers are trivial to add, remove, or autoscale on queue depth; the batch has a natural end (empty queue).

## Cons
- **At-least-once, not exactly-once:** items can be processed more than once, so non-idempotent work double-counts unless you add dedup.
- **Requires independent, idempotent items:** tasks that depend on each other or on ordering do not fit the pattern.
- **Lease tuning is fiddly:** too short causes duplicate processing of slow items; too long delays recovery after a real crash.
- **Poison items need handling:** without a retry limit + DLQ, a permanently-failing item is retried forever and erodes throughput.

## Alternatives
- **FaaS / event-driven functions:** for bursty, event-triggered items, let the platform run one function per item and scale to zero - less control over concurrency but no worker fleet to manage (lesson 08).
- **Batch processing frameworks (MapReduce/Spark):** when items are *not* independent and require shuffles, joins, or multi-stage aggregation across the whole dataset, a batch framework fits where a flat work queue does not (see [ddia/14 - Batch processing](../../ddia/lessons/14-batch-processing.md)).
- **Streaming / continuous processing:** for an unbounded, never-ending flow rather than a finite batch, a stream processor is the right tool (event-driven batch is lesson 11).
- **Synchronous request/response:** when a caller must get the result of *this specific task* immediately, do it inline instead of queueing it for a worker pool.

## When to use it
- You have a large, finite set of independent tasks to process, and no single caller is synchronously waiting on a specific one.
- You want to hit a throughput target or deadline by scaling workers, decoupled from how fast items are produced.
- Each task can be made idempotent so at-least-once processing is safe.
- Work is spiky or backlog-shaped and benefits from buffering (enqueue now, process at a sustainable rate).

## When NOT to use it
- Tasks depend on each other or require global ordering/aggregation - use a batch framework or coordinated pipeline instead.
- The work is not idempotent and cannot be made so - at-least-once will double-apply effects.
- A caller needs the specific result immediately and synchronously - use request/response, not a queue.
- Volume is tiny and one-off - a queue and worker pool is unnecessary machinery.

## Key takeaways / mental model
Think of a warehouse with a single inbox of order slips and a room of identical pickers. Each picker grabs the next slip, fills the order, and drops the slip in the "done" bin - add pickers to clear the inbox faster, and no picker needs to talk to another. But a picker might collapse holding a slip, so a slip is only torn up once the order is confirmed done; an un-confirmed slip goes back in the inbox after a timeout for someone else. Two rules of thumb:

1. **A work queue turns "how much work" into "how many workers."** Sizing is arithmetic (items / rate / workers), and the batch ends when the queue is empty.
2. **Leases give at-least-once, so items must be idempotent.** A worker can die mid-item and the item will be re-run; design deterministic/dedup'd side effects, tune the lease above worst-case item time, and send poison items to a DLQ after N tries.

## Self-check questions
1. What decoupling does a work queue provide, and how do you use it to hit a deadline for a fixed backlog? Show the sizing arithmetic for finishing 2,000,000 two-second items in one hour.
2. Explain the visibility-timeout/lease mechanism step by step. Why does the queue *not* delete an item the moment a worker claims it, and what guarantee does that provide?
3. Why is a work queue at-least-once rather than exactly-once, and what must a worker do to stay correct under redelivery? Give an idempotent and a non-idempotent example.
4. What goes wrong if the lease is too short? Too long? How do long-running workers avoid the "too short" failure without setting a huge global lease?
5. What is a poison item, why does it threaten throughput, and how does a retry limit + dead-letter queue solve it?
6. You have 800,000 independent report tasks (~3 s each) that must finish within 20 minutes, and each task appends a row to a summary table. How many workers do you need, and what must you add to make the appends safe under worker crashes?

## References
- Designing Distributed Systems (Brendan Burns), Chapter 10: "Work Queue Systems"
- [designing-distributed-systems/05 - Replicated Load-Balanced Services](05-replicated-load-balanced.md)
- [system-design/11 - Pub/Sub and distributed queues](../../system-design/lessons/11-pubsub-distributed-queues.md)
