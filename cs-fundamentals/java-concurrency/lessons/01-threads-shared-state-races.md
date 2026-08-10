---
id: java-concurrency/01
subject: java-concurrency
title: Threads, shared state, and race conditions
slug: threads-shared-state-races
status: drafted
mastery:
seniority: mid
source: Java Concurrency in Practice (Goetz et al.), Chapter 2
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Threads, shared state, and race conditions

## TL;DR
A thread is an independent path of execution inside one process, and multiple threads
in the same JVM share the same heap. That sharing is what makes concurrency useful
(threads can cooperate on the same data) and dangerous (uncoordinated access to that
data produces race conditions - bugs that depend on timing and may not show up in
testing at all).

## The idea
A modern server handles many requests "at once." One option is one process per request
(expensive: separate memory, separate heap, slow context switches, no easy way to share
a cache). Java's answer, like most languages, is **threads**: multiple executions inside
a single process, each with its own call stack and program counter, but all sharing the
same heap - the same objects, the same static fields, the same everything that isn't a
local variable.

That shared heap is the whole point of using threads instead of processes: a connection
pool, a cache, or a counter can live in one place and be used by every request-handling
thread without serialization or IPC. But "shared, mutable state" is also precisely the
condition under which uncoordinated access breaks. If two threads read-modify-write the
same field without coordination, the result depends on the exact interleaving of their
instructions at the CPU level - an interleaving Java's specification explicitly does not
guarantee, and the JIT compiler and CPU are both free to reorder for performance. The
result is a **race condition**: correctness of the outcome depends on the relative timing
of threads, and there's no way to know from reading the code alone which timing will win.

## How it works

### Threads vs. processes
A process has one or more threads; all threads within a process share the heap, static
fields, open file descriptors, and other process-level resources. Each thread has its own
call stack, its own set of local variables, and its own program counter. Creating a
thread is far cheaper than creating a process (no new address space to set up), which is
why request-per-thread server designs were viable long before request-per-process ones.

```java
Thread t = new Thread(() -> System.out.println("running on a new thread"));
t.start();      // schedules the thread; do NOT call t.run() directly - that just
                 // executes run() synchronously on the calling thread, no new thread at all.
```

### What "shared state" actually means
Any field reachable from more than one thread is shared state: an instance field on an
object referenced by multiple threads, any `static` field (inherently shared - there is
exactly one per class, visible to the whole JVM), or an element of a shared collection.
Local variables are never shared - each thread's stack is private - so a purely
local-variable computation is automatically thread-safe no matter how many threads run
it concurrently.

### Anatomy of a race condition: the counter example
```java
public class Counter {
    private int value = 0;
    public void increment() { value++; }   // looks atomic. It is not.
}
```
`value++` compiles to three separate steps: **read** `value` from memory into a register,
**increment** the register, **write** the register back to `value`. This is a classic
**check-then-act** / **read-modify-write** sequence, and it is not atomic - another
thread can execute its own read between this thread's read and write.

Concretely, with `value` starting at 0 and two threads (A, B) both calling `increment()`:

1. Thread A reads `value` (0) into its register.
2. Thread A is preempted before writing back (a context switch, a cache miss, anything).
3. Thread B reads `value` (still 0, A hasn't written yet) into its register.
4. Thread B increments its register to 1 and writes `value = 1`.
5. Thread A resumes, increments *its* register (which still holds the stale 0) to 1, and
   writes `value = 1`.

Two increments happened; `value` ended at 1, not 2. One update was **lost** - this
specific failure mode is called a **lost update**, the most common race condition
pattern in practice. Under light contention this might never surface in testing (the
window between read and write is nanoseconds); under production load with many threads
it becomes a near-certainty, which is exactly why race conditions are notorious for
passing code review and unit tests and then corrupting data in production.

### Race condition vs. data race - two related but distinct terms
A **race condition** is a correctness bug: the *program's outcome* depends on timing (the
lost-update example above). A **data race** is a specific, narrower JVM/language concept:
two threads access the same variable concurrently, at least one access is a write, and
there is no synchronization ordering the accesses (see `java-concurrency/03` for exactly
what "ordering" means via happens-before). Every data race is a potential race condition,
but not every race condition requires an unsynchronized data race in the technical sense
- a check-then-act sequence built entirely out of correctly-synchronized individual
operations (e.g. two separate synchronized method calls with a gap between them) can
still race, because synchronizing each *step* doesn't synchronize the *sequence*.

### Common race condition shapes
- **Lost update** - two threads read-modify-write the same field; one update overwrites
  the other (the counter example above).
- **Check-then-act** - "if (map.containsKey(k)) map.get(k) else compute-and-put" - another
  thread can insert between the check and the act, so the "guarantee" the check appeared
  to give is void by the time the act runs.
- **Read-then-write across multiple related fields** - e.g. updating a `min` and `max`
  field to keep an invariant (`min <= max`); another thread reading between the two writes
  can observe a temporarily broken invariant.

### Why this doesn't reliably show up in testing
The JVM, JIT compiler, and CPU are all permitted to reorder instructions and cache values
in registers as long as a *single-threaded* program's observable behavior is unchanged
(this is legal precisely because the JVM specification does not promise anything about
cross-thread visibility without explicit synchronization - see `java-concurrency/03`).
Under low contention on a fast machine the "unlucky" interleaving from the example above
might occur one time in a billion; a demo running on a laptop with two threads may never
hit it, while the same code under real concurrent load in production hits it constantly.
This is why "it passed my tests" is close to meaningless evidence for concurrent
correctness - you need to reason about the code's synchronization, not just run it.

## Pros
- Threads let a single process use multiple CPU cores and overlap I/O wait with useful
  work, which is the entire performance case for using threads at all.
- Shared heap access lets cooperating threads share caches, pools, and state cheaply,
  without serialization or inter-process communication overhead.

## Cons
- Any state reachable from more than one thread is a latent bug surface unless every
  access is properly coordinated - and "properly" is easy to get subtly wrong.
- Race condition bugs are timing-dependent, hard to reproduce, and frequently invisible
  under the light load of local testing while being near-certain under production
  traffic.
- Reasoning about interleavings by hand does not scale past a couple of threads and a
  couple of operations - which is exactly why the rest of this subject exists: to give
  disciplined tools (immutability, confinement, synchronization) instead of ad hoc
  reasoning.

## Alternatives
- **Single-threaded event loop** (e.g. Node.js-style) - avoids shared-state races
  entirely by construction (one thread, no concurrent access), at the cost of needing
  explicit async handling for I/O and no ability to use multiple cores from one loop.
- **Multi-process architecture** - sidesteps shared-heap races by not sharing a heap at
  all; trades that safety for the cost and complexity of inter-process communication for
  any data that does need to be shared.
- **Actor model / message passing** - threads (or lightweight actors) never share mutable
  state directly; they communicate exclusively via messages, which removes classic data
  races but introduces its own correctness concerns (message ordering, deadlocked mailbox
  chains).

## When to use it
Use plain Java threads (or, more commonly today, an `Executor`-managed thread pool - see
`java-concurrency/08`) whenever you need to overlap I/O-bound work, use multiple CPU
cores for CPU-bound work, or keep a long-running background task off the request path.

## When NOT to use it
Don't reach for raw shared mutable state as your first design. If the state can instead
be confined to one thread, made immutable, or restructured so threads communicate via a
thread-safe queue instead of a shared field, you eliminate the entire class of race-
condition bugs before you write a single lock - see `java-concurrency/02` for exactly how.

## Key takeaways / mental model
Threads share the heap; that sharing is the feature and the hazard. Any compound
operation on shared mutable state (read-modify-write, check-then-act) is not atomic
unless you make it so. A race condition's absence in testing is not evidence of its
absence in production - reason about the code, don't just run it.

## Self-check questions
1. Why does `value++` on a shared field require synchronization even though it looks
   like a single operation in source code?
2. Explain the lost-update interleaving on the two-thread counter example step by step,
   in your own words, without looking at the lesson.
3. What is the difference between a "race condition" and a "data race" as used in this
   lesson?
4. Why might a race condition never appear during unit testing on a laptop but appear
   reliably in production? What does this imply about how you should evaluate whether
   concurrent code is correct?

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 2:
  "Thread Safety."
