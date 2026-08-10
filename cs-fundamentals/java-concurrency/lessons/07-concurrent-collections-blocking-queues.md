---
id: java-concurrency/07
subject: java-concurrency
title: Concurrent collections and blocking queues
slug: concurrent-collections-blocking-queues
status: drafted
mastery:
seniority: mid
source: Java Concurrency in Practice (Goetz et al.), Chapter 5
prerequisites: [java-concurrency/05]
created: 2026-08-10
updated: 2026-08-10
---

# Concurrent collections and blocking queues

## TL;DR
`java.util.concurrent` provides purpose-built thread-safe collections -
`ConcurrentHashMap`, `CopyOnWriteArrayList`, and the `BlockingQueue` family - that beat a
plain collection wrapped in your own locking on both correctness (they expose atomic
compound operations like `computeIfAbsent`) and performance (internally striped or
lock-free, instead of one coarse external lock). `BlockingQueue` additionally solves
thread hand-off: producer threads block when full, consumer threads block when empty, no
manual wait/notify required.

## The idea
`java-concurrency/05` showed that wrapping a plain `HashMap` in an external lock (or using
`Collections.synchronizedMap`) still leaves compound operations (check-then-act, iterate-
while-mutating) unsafe unless you hold that lock across the entire compound sequence -
and holding one coarse lock across everything kills scalability under contention.
`java.util.concurrent`'s collections were purpose-built to fix both problems: they provide
atomic versions of the compound operations you actually need, and they achieve
thread safety via internal designs (lock striping, copy-on-write, lock-free algorithms)
that scale far better than one external lock ever could.

## How it works

### `ConcurrentHashMap`: the default concurrent map
Internally partitions its keyspace so that different threads updating different keys
mostly don't contend with each other at all (historically via lock striping across
segments; current JDK implementations use finer-grained, largely lock-free
node-level synchronization) - unlike `Collections.synchronizedMap(new HashMap<>())`,
which serializes *every* access through one lock regardless of which keys are touched.

Critically, it exposes **atomic compound operations** that solve the exact check-then-act
hazard from `java-concurrency/01` and `java-concurrency/04` without you managing a lock:
```java
ConcurrentHashMap<String, Widget> cache = new ConcurrentHashMap<>();

// Atomic "insert only if absent" - no race window between check and insert.
Widget w = cache.putIfAbsent(key, new Widget(key));

// Atomic "compute on demand" - the mapping function runs at most once per key,
// even under concurrent calls for the same key (the "expensive lazy init" pattern).
Widget w2 = cache.computeIfAbsent(key, k -> expensiveCreate(k));

// Atomic conditional update.
cache.replace(key, oldWidget, newWidget);   // only replaces if current value == oldWidget
```
**Iteration is weakly consistent**, not fail-fast: iterating a `ConcurrentHashMap` while
another thread mutates it never throws `ConcurrentModificationException` (unlike a plain
`HashMap`), and is guaranteed to reflect the state at some point during the iteration,
but may or may not reflect updates made concurrently with the iteration itself. This is
usually exactly what you want (no crash, no external locking needed to iterate safely)
but means you cannot treat a concurrent iteration as an atomic snapshot.

**`size()` is not necessarily exact** under concurrent modification (it's an estimate for
performance reasons in some implementations/versions) - don't rely on it for anything
requiring precision under contention.

### `CopyOnWriteArrayList` / `CopyOnWriteArraySet`
Every mutating operation (`add`, `remove`, `set`) copies the entire underlying array and
atomically swaps the reference - readers always see a stable, unchanging snapshot with
zero locking overhead (a beneficial consequence of the immutability idiom from
`java-concurrency/02` applied to the collection's storage). Iterators never throw
`ConcurrentModificationException` and never reflect concurrent mutations (they iterate the
snapshot taken at iterator-creation time).

This trades write cost (every write is O(n), a full array copy) for read cost (reads are
plain array access, no locking, no CAS retry). **Only appropriate when reads vastly
outnumber writes** - e.g. a list of registered event listeners, rarely modified but
iterated on every event.

### `BlockingQueue`: thread hand-off, not just storage
A `BlockingQueue<E>` adds blocking semantics to a queue: `put(e)` blocks the calling
thread if the queue is full (for bounded implementations) until space is available;
`take()` blocks if the queue is empty until an element is available. This directly
implements the classic **producer-consumer pattern** without any manual
`wait`/`notify`/`Object.wait()` bookkeeping (`java-concurrency/11` covers what a
`BlockingQueue` is built from internally, for when you need to build your own
synchronizer).

```java
BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);   // bounded, capacity 100

// Producer thread
queue.put(task);     // blocks if queue is full - natural backpressure

// Consumer thread
Task t = queue.take(); // blocks if queue is empty - no busy-waiting/polling needed
```

**Bounded vs. unbounded, and why bounding matters.** `LinkedBlockingQueue` can be
constructed bounded or unbounded (default `Integer.MAX_VALUE` capacity - effectively
unbounded). An unbounded queue in a producer-consumer system with a producer faster than
its consumer will grow without limit, eventually exhausting heap memory - a slow-motion
`OutOfMemoryError`, not a fast, loud failure. A bounded queue converts that into
*backpressure*: producers naturally block (or, with `offer`, can be told immediately "no
room") once the consumer falls behind, which is almost always the behavior you actually
want in a real system (`java-concurrency/15` builds on this for resilient service design).

### Blocking queue implementations, compared

| Implementation | Backing | Bounded? | Notes |
|---|---|---|---|
| `ArrayBlockingQueue` | fixed array | always bounded | single lock for put/take; simple, predictable |
| `LinkedBlockingQueue` | linked nodes | optional | separate put/take locks - higher throughput under concurrent producers and consumers |
| `PriorityBlockingQueue` | binary heap | unbounded | orders by `Comparable`/`Comparator`, not FIFO |
| `SynchronousQueue` | none (zero capacity) | n/a | `put` blocks until a `take` is waiting to receive that exact element - a direct thread hand-off with no buffering at all |
| `DelayQueue` | heap of delayed elements | unbounded | elements only become available for `take()` after their configured delay expires - useful for scheduling/retry-after |

### Non-blocking variants: `offer`/`poll` with and without timeout
Every `BlockingQueue` also supports non-blocking (`offer(e)` returns `false` instead of
blocking if full; `poll()` returns `null` instead of blocking if empty) and timed
(`offer(e, timeout, unit)`, `poll(timeout, unit)`) variants - useful when unconditional
blocking isn't acceptable (e.g. you want to detect and log backpressure rather than
silently stall a thread forever).

### Worked example: a bounded producer-consumer pipeline
```java
BlockingQueue<LogEntry> pending = new ArrayBlockingQueue<>(1000);

// N producer threads (e.g. request handlers)
void logAsync(LogEntry e) {
    boolean accepted = pending.offer(e, 50, TimeUnit.MILLISECONDS);
    if (!accepted) metrics.increment("log.dropped");   // explicit backpressure handling
}

// 1 consumer thread (the actual disk-writing worker)
void run() {
    while (!Thread.currentThread().isInterrupted()) {
        LogEntry e = pending.take();   // blocks until work arrives
        writeToDisk(e);
    }
}
```
This pipeline decouples request-handling threads (fast, must not block on disk I/O) from
the actual write (slow). The bounded capacity plus a timed `offer` gives an explicit,
observable failure mode (a dropped/counted log entry) instead of either unbounded memory
growth or an indefinitely blocked request thread.

## Pros
- Atomic compound operations (`putIfAbsent`, `computeIfAbsent`, `replace`) remove entire
  classes of check-then-act bugs without any lock code in your own class.
- Internal lock striping / lock-free design scales far better under contention than one
  external lock around a plain collection.
- `BlockingQueue` implements producer-consumer hand-off correctly and efficiently without
  hand-written `wait`/`notify`.
- Weakly-consistent iteration means no `ConcurrentModificationException` risk during
  concurrent use, unlike plain collections.

## Cons
- Weakly-consistent iteration is not a snapshot guarantee - don't rely on
  `ConcurrentHashMap` iteration reflecting either all-before or all-after state for
  concurrent modifications.
- `CopyOnWriteArrayList`'s O(n) writes make it a poor fit for write-heavy workloads.
- An unbounded queue converts backpressure into a memory leak under sustained overload -
  almost always the wrong default for a production pipeline.
- `size()` on some concurrent collections/queues can be approximate or O(n) to compute
  precisely - don't use it as a fast, exact check in a hot path.

## Alternatives
- **Hand-rolled locking around a plain collection** (`java-concurrency/04`,
  `java-concurrency/05`) - only preferable when you need semantics no concurrent
  collection provides, and even then, usually better to compose from concurrent
  primitives than to lock a plain `HashMap`/`ArrayList` yourself.
- **`Exchanger`** (`java-concurrency/11`) - for a strict one-to-one, single-element
  hand-off between exactly two threads, rather than a general multi-producer/multi-
  consumer queue.
- **External message broker** (Kafka, RabbitMQ) - when the producer-consumer
  relationship needs to cross process/machine boundaries, persistence, or replay -
  `BlockingQueue` is strictly in-process, in-memory.

## When to use it
Default to `ConcurrentHashMap` for any shared mutable map and `BlockingQueue` (bounded,
almost always) for any in-process producer-consumer hand-off. Use
`CopyOnWriteArrayList` specifically for small, rarely-mutated, frequently-iterated
collections like listener lists.

## When NOT to use it
Don't use `CopyOnWriteArrayList` for a collection with frequent writes or a large element
count - the per-write copy cost dominates. Don't use an unbounded queue in a producer-
consumer pipeline unless you've deliberately decided unlimited buffering is acceptable
(rare) - default to bounded with an explicit backpressure policy. Don't rely on
`ConcurrentHashMap`'s weakly-consistent iteration where you need a true point-in-time
snapshot - build an immutable copy first if that's required.

## Key takeaways / mental model
Reach for `java.util.concurrent`'s collections before hand-rolling locks around a plain
collection - they give you atomic compound operations and better scalability for free.
For any producer-consumer relationship, `BlockingQueue` handles the blocking and hand-off
correctly; the design decision that matters most is bounded-vs-unbounded, because that's
really a decision about your backpressure policy under overload.

## Self-check questions
1. Why does `ConcurrentHashMap.computeIfAbsent` avoid the check-then-act race that a
   manual `if (!map.containsKey(k)) map.put(k, ...)` on any map would have?
2. Explain why `CopyOnWriteArrayList` is a poor choice for a collection with frequent
   writes, in terms of what happens on every mutating call.
3. What specifically goes wrong in a producer-consumer pipeline that uses an unbounded
   `LinkedBlockingQueue` when the producer is consistently faster than the consumer?
4. Compare `ArrayBlockingQueue` and `SynchronousQueue`: what does "capacity zero" mean
   for `SynchronousQueue`'s `put`/`take` semantics?

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 5:
  "Building Blocks."
