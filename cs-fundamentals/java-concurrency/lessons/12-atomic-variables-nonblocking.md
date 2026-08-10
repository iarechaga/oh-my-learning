---
id: java-concurrency/12
subject: java-concurrency
title: Atomic variables and nonblocking techniques
slug: atomic-variables-nonblocking
status: drafted
mastery:
seniority: senior
source: Java Concurrency in Practice (Goetz et al.), Chapter 15
prerequisites: [java-concurrency/03, java-concurrency/11]
created: 2026-08-10
updated: 2026-08-10
---

# Atomic variables and nonblocking techniques

## TL;DR
`AtomicInteger`, `AtomicLong`, `AtomicReference`, and friends update a single value
correctly under concurrent access without ever blocking a thread, using a hardware
instruction called **compare-and-swap (CAS)** instead of a lock. No thread waits for
another to release anything; a thread whose CAS fails simply retries. This scales
dramatically better than locking under contention on a single hot value, at the cost of
only protecting exactly one variable's worth of state per atomic instance.

## The idea
Every synchronizer in `java-concurrency/04` and `java-concurrency/11` works by
**blocking**: a thread that can't proceed goes to sleep until another thread wakes it.
Blocking has real costs - context switches, thread scheduling, and (under contention) a
whole queue of waiting threads, none of them doing useful work. For a single, simple
piece of shared state (a counter, a reference, a flag), there's a fundamentally different
approach: **compare-and-swap**, a CPU-level atomic instruction that lets a thread attempt
an update and immediately find out whether it succeeded - no blocking, no queueing,
because a "failed" attempt just means "someone else updated it first, read the new value
and try again," resolved entirely with a tight retry loop rather than a wait.

## How it works

### Compare-and-swap (CAS): the hardware primitive underneath
CAS takes three arguments: a memory location, an expected current value, and a new
value. Atomically (as a single, uninterruptible hardware operation): if the location's
current value equals the expected value, set it to the new value and report success;
otherwise, leave it unchanged and report failure (returning the actual current value, so
the caller can retry with fresh information). This is a single CPU instruction on modern
hardware (`CMPXCHG` on x86, load-linked/store-conditional on ARM) - not something the JVM
simulates with a lock underneath.

```java
// Conceptually, what AtomicInteger.incrementAndGet() does:
int prev, next;
do {
    prev = value;               // read the current value
    next = prev + 1;             // compute the desired new value
} while (!compareAndSet(value, prev, next));   // retry if someone beat us to it
return next;
```
If two threads race to increment the same `AtomicInteger`, one CAS succeeds; the other's
`compareAndSet` fails (because `value` no longer equals the `prev` it read), so it loops
back, re-reads the now-updated value, recomputes, and retries - typically succeeding on
the very next attempt, since the window for a second collision is a handful of CPU
cycles. This is the practical difference from locking: instead of the losing thread
*blocking*, it *retries immediately*, and under most contention levels that retry
succeeds fast enough that CAS-based atomics substantially outperform a lock doing the
same job.

### `AtomicInteger`, `AtomicLong`, `AtomicBoolean`, `AtomicReference`
```java
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();                       // atomic ++counter
counter.getAndIncrement();                        // atomic counter++
counter.addAndGet(5);                              // atomic counter += 5
counter.compareAndSet(expected, newValue);         // the raw primitive, exposed directly

AtomicReference<ImmutablePoint> position = new AtomicReference<>(new ImmutablePoint(0, 0));
position.updateAndGet(p -> p.translated(1, 0));    // atomic read-transform-write, retrying
                                                      // internally if another thread interleaves
```
`AtomicReference<T>` is the general-purpose version: any single reference can be updated
atomically, which combines naturally with the immutable-object idiom from
`java-concurrency/02` - build a whole new immutable object representing the next state,
then atomically swap the reference, so readers always see one complete, internally
consistent object with zero locking on the read path.

### Worked example: replacing a lock with CAS for a simple counter
```java
// Lock-based (java-concurrency/04)
public class LockedCounter {
    private final Object lock = new Object();
    private int value = 0;
    public void increment() { synchronized (lock) { value++; } }
    public int get() { synchronized (lock) { return value; } }
}
// CAS-based
public class AtomicCounter {
    private final AtomicInteger value = new AtomicInteger(0);
    public void increment() { value.incrementAndGet(); }
    public int get() { return value.get(); }    // no lock needed to read either
}
```
Functionally equivalent for this simple case, but under heavy contention from many
threads, `AtomicCounter` scales substantially better: no thread ever blocks or is
descheduled waiting for the lock; every thread is always making forward progress (either
succeeding immediately or retrying a handful of times).

### The multivariable invariant limitation
A single `AtomicXxx` only atomically updates *one* variable. The moment an invariant
spans two fields (`java-concurrency/05`'s `min <= max` example), a single atomic cannot
enforce it - you'd need either a lock spanning both fields, or to combine both values into
one immutable object referenced by a single `AtomicReference`:
```java
public final class Range {                              // immutable
    final int min, max;
    Range(int min, int max) { this.min = min; this.max = max; }
}
private final AtomicReference<Range> range = new AtomicReference<>(new Range(0, 0));
public void observe(int value) {
    Range prev, next;
    do {
        prev = range.get();
        next = new Range(Math.min(prev.min, value), Math.max(prev.max, value));
    } while (!range.compareAndSet(prev, next));   // retry if another thread updated first
}
```
This pattern - read the current immutable snapshot, compute a new immutable snapshot,
CAS the reference, retry on failure - generalizes the "immutable object + atomic swap"
idea to arbitrarily complex multivariable state, as long as the *whole* update can be
expressed as "compute new snapshot from old snapshot," with no dependency on anything
outside the snapshot itself.

### `AtomicStampedReference` / `AtomicMarkableReference`: the ABA problem
Plain CAS has a subtle hazard called the **ABA problem**: thread T1 reads value A, gets
preempted; thread T2 changes the value from A to B and back to A before T1 resumes; T1's
CAS succeeds (the value *is* A again) even though the value changed twice in between -
which is invisible to a plain CAS, but can matter if the intermediate change had side
effects T1's logic assumed couldn't have happened (a classic case: a lock-free stack pop
that reads the top node, gets preempted, and the node gets popped and freed and a
different node happens to get allocated at the same reference by chance). `
AtomicStampedReference<T>` fixes this by pairing the reference with an integer "stamp"
that's incremented on every update, so a CAS can require both the reference *and* the
stamp to match - detecting the A-to-B-to-A round trip even though the reference alone
looks unchanged. `AtomicMarkableReference<T>` is the simpler variant pairing a reference
with a single boolean mark, useful for lock-free data structures that need a
"logically deleted" flag on a node.

### `LongAdder`: better than `AtomicLong` under very high contention
Under extremely high contention (many threads all incrementing the same counter at once),
even CAS retries can start colliding frequently enough to hurt throughput - every
thread's retry loop keeps re-colliding with everyone else's. `LongAdder` (Java 8+)
addresses this by internally striping the counter across multiple cells, letting
different threads usually update different cells with no contention at all, and only
summing across cells when `sum()` is actually called. This trades read cost (`sum()` is
O(number of stripes), not O(1)) for dramatically better write throughput under very high
contention - the recommended default over `AtomicLong` specifically for hot counters (
metrics, request counts) written far more often than read.

## Pros
- No blocking, no context switches, no thread ever queued waiting - typically much
  higher throughput than a lock for simple, single-variable updates under contention.
- Read operations (`get()`) require no synchronization overhead at all beyond a
  `volatile` read.
- Composes naturally with immutability (`java-concurrency/02`): "new immutable
  snapshot + atomic swap" scales the technique to more complex state without a lock.

## Cons
- Only protects one variable (or one reference) per atomic instance - cannot express a
  multivariable invariant directly; you must fold the state into one immutable object and
  atomically swap the whole thing, which isn't always natural or cheap to construct.
- Retry loops can, under pathological contention, spin many times before succeeding (
  though this is rare and usually still cheaper than blocking) - `LongAdder` exists
  specifically because even CAS retries have a contention ceiling.
- The ABA problem is a real, subtle hazard in hand-rolled lock-free data structures using
  plain `AtomicReference`, easy to overlook without the stamped/markable variants.
- Building correct lock-free algorithms beyond simple counters and reference swaps
  (e.g. a lock-free queue or stack) is genuinely hard to get right by hand; prefer
  battle-tested `java.util.concurrent` collections (`java-concurrency/07`) over writing
  your own.

## Alternatives
- **`synchronized` / `ReentrantLock`** (`java-concurrency/04`, `java-concurrency/11`) -
  simpler to reason about for multivariable invariants, and the right choice whenever the
  update logic doesn't cleanly reduce to a single CAS-able value or immutable snapshot.
- **`LongAdder`/`LongAccumulator`** - specifically for high-contention counters/accumulate
  operations where even `AtomicLong`'s CAS retries become a bottleneck.
- **Concurrent collections** (`java-concurrency/07`) - `ConcurrentHashMap` and friends
  already use CAS and lock-free techniques internally; prefer them over hand-rolling a
  similar structure with raw atomics.

## When to use it
Use atomics for a single shared counter, flag, or reference where updates are simple
(increment, compare-and-set, or "compute new immutable value from old") and you want to
avoid locking overhead - especially under contention where lock-based code has already
been shown (by measurement, `java-concurrency/13`) to be a bottleneck.

## When NOT to use it
Don't reach for raw atomics to protect an invariant spanning multiple independent fields
unless you fold them into one immutable object updated via a single `AtomicReference` CAS
loop - otherwise you'll reproduce `java-concurrency/05`'s multivariable-invariant bug.
Don't hand-roll a lock-free data structure from scratch when a proven
`java.util.concurrent` collection already does the job. Don't switch from a lock to an
atomic without evidence (profiling, `java-concurrency/13`) that lock contention was
actually the bottleneck - premature "lock-free" rewrites add real complexity for no
measured benefit.

## Key takeaways / mental model
CAS trades blocking for retrying: a thread that loses a race tries again immediately
instead of sleeping, which scales better under contention but only for a single
variable's worth of state at a time. "New immutable snapshot, CAS the reference, retry on
failure" is the general pattern for extending atomics beyond simple counters.

## Self-check questions
1. Explain, step by step, what happens when two threads call `incrementAndGet()` on the
   same `AtomicInteger` at nearly the same time - does either one block?
2. Why can't a single `AtomicInteger` and a single separate `AtomicInteger` together
   enforce an invariant like `min <= max`, even though each individually is thread-safe?
3. Describe the ABA problem in your own words, and explain what `AtomicStampedReference`
   adds to prevent it.
4. When would you choose `LongAdder` over `AtomicLong`, and what read-side cost does that
   choice introduce?

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 15:
  "Atomic Variables and Nonblocking Synchronization."
