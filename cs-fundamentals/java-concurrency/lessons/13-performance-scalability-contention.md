---
id: java-concurrency/13
subject: java-concurrency
title: Performance and scalability under contention
slug: performance-scalability-contention
status: drafted
mastery:
seniority: senior
source: Java Concurrency in Practice (Goetz et al.), Chapter 11
prerequisites: [java-concurrency/06, java-concurrency/12]
created: 2026-08-10
updated: 2026-08-10
---

# Performance and scalability under contention

## TL;DR
Adding threads only helps throughput up to the point where they start contending for the
same locks, caches, or CPU resources - past that point, more threads can make things
*slower*, not faster. Amdahl's Law quantifies why: the fraction of your workload that
must run serially caps the maximum possible speedup from parallelism, no matter how many
cores you throw at it. Reducing lock scope, lock granularity, and lock contention -
measured, not guessed - is the actual work of concurrent performance tuning.

## The idea
Every earlier lesson in this subject established *correctness* tools: locks, atomics,
concurrent collections. None of them are free - every one has a cost that scales with how
much threads actually contend for the same resource. This lesson is about the other axis
entirely: given correct code, how much does adding concurrency actually help, and where
does that help run out? The uncomfortable core fact: throughput doesn't scale linearly
with thread count past a certain point, and understanding why is what separates "add more
threads" folklore from disciplined performance engineering.

## How it works

### Amdahl's Law: the ceiling on parallel speedup
If a fraction **F** of a program's work must execute serially (cannot be parallelized -
e.g. a single lock every thread must pass through), and the rest **(1-F)** can be
perfectly parallelized across N threads/cores, the maximum possible speedup is:

```
speedup(N) = 1 / (F + (1-F)/N)
```

As N approaches infinity, `speedup(N)` approaches `1/F` - a hard ceiling determined
entirely by the serial fraction, independent of how many cores you add. Concretely: if
10% of your workload is serial (F = 0.1), the maximum possible speedup from *any* number
of additional cores is 10x - going from 10 cores to 1000 cores cannot beat that ceiling,
because 1000 cores still spend 10% of wall-clock time serialized through the same
bottleneck.

**Worked numbers.** F = 0.1 (90% parallelizable):
- N=1: speedup = 1.0 (baseline)
- N=10: speedup = 1 / (0.1 + 0.09) = 5.26x
- N=100: speedup = 1 / (0.1 + 0.009) = 9.17x
- N=infinity: speedup approaches 1/0.1 = 10x

Notice how little is gained going from N=10 to N=100 (5.26x to 9.17x) compared to N=1 to
N=10 - and going from N=100 to N=infinity only gains another 0.83x, ever. This is why
"just add more threads/cores" has rapidly diminishing returns, and why identifying and
shrinking the serial fraction **F** matters far more than adding raw parallelism once F is
non-trivial. In concurrent Java code, F is very often "time spent holding a shared lock" -
which is exactly the quantity `java-concurrency/04` through `java-concurrency/11`'s
scoping advice is trying to minimize.

### Where the serial fraction hides in real code
Every one of these is effectively a contribution to Amdahl's F:
- A `synchronized` block or `ReentrantLock` guarding a hot, frequently-accessed piece of
  shared state - every thread that needs it serializes through it.
- A single-threaded stage in an otherwise-parallel pipeline (e.g. all threads writing to
  one shared log file through one lock).
- Garbage collection pauses that stop all threads (a serial phase intrinsic to the JVM
  runtime, not your code, but still counted in F for the purposes of overall throughput).
- Contended I/O resources (a single database connection, a single network socket) shared
  across otherwise-independent worker threads.

### Lock contention: the direct performance cost
Contention is what happens when multiple threads try to acquire the same lock at
overlapping times. Under **low contention**, `synchronized`/`ReentrantLock` are cheap
(modern JVMs optimize the uncontended case aggressively). Under **high contention**,
throughput degrades sharply: threads block, get descheduled, and pay real OS-level
context-switch cost to be woken again later, and - critically - all of that overhead is
pure waste, work that produces no forward progress on the actual task. This is why
`java-concurrency/12`'s atomics (no blocking, retry instead) often substantially
outperform locks specifically under contention, even though both are equally cheap when
uncontended.

### Reducing lock scope: shrink what's inside the lock
```java
// Before: holds the lock across an expensive, unrelated computation
public synchronized void process(Data d) {
    Result r = expensiveComputation(d);   // doesn't touch shared state - shouldn't be locked
    sharedResults.add(r);                  // this is the only part that needs the lock
}
// After: lock scope shrunk to just the shared-state mutation
public void process(Data d) {
    Result r = expensiveComputation(d);    // runs concurrently across threads, no lock
    synchronized (this) {
        sharedResults.add(r);               // brief, minimal critical section
    }
}
```
This reduces the fraction of time any thread spends holding the lock, directly reducing
F and directly increasing the number of threads that can make progress on
`expensiveComputation` concurrently.

### Reducing lock granularity: split one lock into several
```java
// Before: one lock guards two logically-independent maps
public class Registry {
    private final Object lock = new Object();
    private final Map<String, User> users = new HashMap<>();
    private final Map<String, Session> sessions = new HashMap<>();
    // every operation on EITHER map contends with every operation on the OTHER
}
// After: split into independent locks, since the two maps have no shared invariant
public class Registry {
    private final Object userLock = new Object();
    private final Object sessionLock = new Object();
    private final Map<String, User> users = new HashMap<>();
    private final Map<String, Session> sessions = new HashMap<>();
    // operations on users and sessions no longer contend with each other at all
}
```
This is only valid when the two pieces of state have no invariant spanning both
(`java-concurrency/05`) - splitting a lock that actually protects a joint invariant
reintroduces the exact multivariable-invariant bug that lesson covers. **Lock striping**
generalizes this further: instead of one lock per logically distinct piece of state,
partition *one* logical structure (e.g. a hash map) across N locks, each covering a
subset of the keyspace (e.g. by `hash(key) % N`) - which is conceptually what
`ConcurrentHashMap` (`java-concurrency/07`) does internally, letting operations on
different keys proceed with zero contention between them.

### Context switching and thread count
More threads than available CPU cores does not, in general, increase throughput for
CPU-bound work - it adds pure scheduling overhead (context switches, cache-line
evictions when a different thread's working set replaces the previous thread's data in
CPU cache) without adding any actual computation capacity. This is exactly why
`java-concurrency/08`'s pool-sizing advice differs so sharply between CPU-bound work
(pool size near core count) and I/O-bound work (pool size much larger, since blocked
threads aren't consuming CPU and more of them lets more I/O happen concurrently).

### Measure, don't guess
Concurrent performance intuition is notoriously unreliable - "this obviously needs a
lock split" or "this obviously needs more threads" is frequently wrong once measured.
The standard approach: benchmark under realistic load (ideally with a proper
microbenchmark harness like JMH, which correctly accounts for JIT warmup and avoids dead-
code elimination artifacts that make naive hand-rolled loop benchmarks misleading), use a
profiler capable of showing lock contention specifically (thread dumps showing `BLOCKED`
threads, or a profiler's contention/lock view), and change one thing at a time, re-
measuring after each change. **Never optimize a lock's scope or granularity without first
confirming, by measurement, that it is actually a contended bottleneck** - narrowing an
uncontended lock's scope adds code complexity for zero real throughput gain, and can
occasionally even hurt readability-driven correctness (more, smaller synchronized blocks
mean more places to keep the "guarded by" discipline from `java-concurrency/05` correct).

## Pros
- Amdahl's Law gives a principled, quantitative way to reason about the ceiling on
  parallel speedup before investing engineering effort chasing an impossible target.
- Lock-scope reduction and lock-splitting are usually cheap, low-risk changes once a
  genuine bottleneck is identified by measurement.
- Understanding contention explains *why* atomics (`java-concurrency/12`) and concurrent
  collections (`java-concurrency/07`) outperform naive locking under load, rather than
  taking it on faith.

## Cons
- Amdahl's Law assumes a fixed problem size and a clean serial/parallel split - real
  systems have more complex bottleneck interactions (I/O wait, GC pauses, cache effects)
  that a simple F doesn't fully capture on its own.
- Splitting locks or shrinking their scope without first confirming contention by
  measurement adds real complexity (more locks to reason about, more places the
  `@GuardedBy` discipline can drift) for no proven benefit.
- Benchmarking concurrent code correctly is genuinely hard - naive microbenchmarks are
  routinely misled by JIT warmup, dead-code elimination, and unrealistic load shapes.

## Alternatives
- **Accept the current throughput and scale horizontally instead** - when the serial
  fraction is dominated by something outside your control (a shared external database, a
  single downstream service), adding more processes/machines each running independent
  work can beat further squeezing a single process's internal concurrency.
- **Reduce shared state altogether** (`java-concurrency/02`, `java-concurrency/12`) -
  the deepest fix for contention is often not a better lock but no lock: confinement,
  immutability, or per-thread/per-partition state that never needs to be shared in the
  first place.

## When to use it
Apply this discipline (measure first, then reduce lock scope, then consider splitting
granularity, then consider lock-free alternatives) whenever profiling or production
metrics show threads spending significant time blocked or a system failing to scale with
added cores/threads despite headroom existing.

## When NOT to use it
Don't restructure locking based on intuition alone - measure contention first.
Don't split a lock that protects a genuine multivariable invariant just to reduce
contention - that reintroduces correctness bugs (`java-concurrency/05`) for a performance
gain that may not even materialize if the split pieces still need to be kept consistent
some other way.

## Key takeaways / mental model
Throughput has a ceiling set by whatever fraction of the work is serial - Amdahl's Law
makes that ceiling concrete and shows why "just add threads" has steeply diminishing
returns. The actual lever you control is shrinking that serial fraction: narrower lock
scope, finer lock granularity, or removing the need for shared state altogether - always
justified by measurement, never by intuition alone.

## Self-check questions
1. Using Amdahl's Law, compute the maximum possible speedup for a workload where 20% of
   the work is inherently serial, as the number of cores approaches infinity. What does
   this tell you about the value of going from 8 cores to 64 cores for this workload?
2. Explain the difference between reducing lock *scope* and reducing lock *granularity*,
   with an example of each.
3. Why can adding more threads than available CPU cores actively hurt throughput for a
   CPU-bound workload?
4. Why is "measure before optimizing" especially important for concurrent code, compared
   to single-threaded performance tuning?

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 11:
  "Performance and Scalability."
