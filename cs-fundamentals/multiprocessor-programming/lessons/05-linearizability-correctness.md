---
id: multiprocessor-programming/05
subject: multiprocessor-programming
title: Linearizability and correctness of concurrent objects
slug: linearizability-correctness
status: drafted
mastery:
seniority: senior
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 3
prerequisites: [multiprocessor-programming/02]
created: 2026-08-10
updated: 2026-08-10
---

# Linearizability and correctness of concurrent objects

## TL;DR
Linearizability is the standard correctness criterion for a concurrent object: every
concurrent execution must be equivalent to *some* sequential execution that preserves
each thread's own operation order and respects real-time ordering (if operation A
finishes before operation B starts, A must appear before B in the equivalent sequential
order). It gives a precise, composable way to say "this concurrent queue/stack/counter
behaves correctly" without having to reason about every possible interleaving by hand.

## The idea
`multiprocessor-programming/02` defined correctness for *locks* (mutual exclusion,
deadlock/starvation-freedom). But locks are a means, not an end — what programmers
actually want is confidence that a **shared data structure** (a queue, a stack, a hash
table) behaves sensibly when accessed concurrently. "Sensibly" needs a precise
definition, because with concurrent operations overlapping in time, questions like "what
value does this read return?" don't have an obvious single answer the way they do in
sequential code.

Linearizability answers this by reducing the concurrent case to the sequential case you
already understand: a concurrent history of operations is correct if you can find *some*
way to order all the operations into a single sequential timeline, one at a time, such
that (a) the object behaves correctly under its normal sequential specification in that
order, and (b) the ordering doesn't violate anything threads could actually observe
(each thread's own operations stay in its own order, and if one operation was fully
complete before another started in real time, the ordering must respect that too). If
such a sequential ordering exists, the concurrent execution is linearizable — and
crucially, it *looks* to every observer as if it happened atomically at some single point
in time between when it was invoked and when it returned.

## How it works

### Histories, invocations, and responses
A concurrent execution is recorded as a **history**: a sequence of **invocation** events
(a thread calls a method, e.g. `enqueue(5)`) and **response** events (the method returns,
e.g. `enqueue` returns `void`, or `dequeue` returns `5`). Because threads run
concurrently, invocations and responses from different threads can interleave in the
history — that's exactly what makes reasoning about it hard.

An operation's **duration** is the real-time interval from its invocation to its
response. Two operations are **concurrent** (overlapping) if their durations overlap at
all; otherwise one is **sequential-before** the other (fully finishes before the other
starts).

### The linearizability definition
A history H is **linearizable** if there exists a permutation of H's operations — a
**linearization** — such that:
1. The linearization is a valid *sequential* history for the object (each operation, taken
   one at a time in this order, obeys the object's normal sequential specification — e.g.
   a queue's `dequeue` returns whatever the earliest not-yet-dequeued `enqueue`d value
   was).
2. The linearization respects **each thread's own program order** (if thread T invoked
   op1 before op2 in its own code, op1 appears before op2 in the linearization).
3. The linearization respects **real-time order across threads**: if operation A's
   response happened-before operation B's invocation in real time (A fully completed
   before B even started), then A must appear before B in the linearization.

Point 3 is the crux and what makes linearizability strictly *local* and composable: you
never need to inspect an object's internals to check whether combining it with other
linearizable objects preserves correctness — linearizability of each object individually
guarantees the whole system's history is linearizable too (this composability is exactly
why it's the standard criterion, not an incidental nicety).

### The linearization point
In practice, proving an implementation linearizable usually means identifying, for each
method, a single instant in time — the **linearization point** — at which the operation
"appears to take effect" atomically, even though the method's actual code executes over
an interval with multiple steps. Often the linearization point is a specific line of
code: e.g., for a lock-free queue built on CAS (`multiprocessor-programming/10`,
`multiprocessor-programming/11`), the linearization point of `enqueue` is typically the
successful CAS that links the new node into the structure — everything before it is
"setup" and everything after is "cleanup," but the object's abstract state changes at
exactly that CAS.

**Worked example.** Two threads operate on a shared queue, initially empty.
- Thread A: `enqueue(1)` starts at time 0, returns at time 5.
- Thread B: `enqueue(2)` starts at time 2 (while A's enqueue is still in progress), returns
  at time 4.
- Thread A: `dequeue()` starts at time 6, returns `2` at time 8.

Is this linearizable? A's `enqueue(1)` and B's `enqueue(2)` overlap in time (concurrent),
so either order between them is allowed by real-time constraints. A's `dequeue()` starts
strictly after both enqueues finished, so it must come after both in the linearization.
Try the order: enqueue(2), enqueue(1), dequeue() -> dequeue returns 2 (the first thing
enqueued in this order) — matches the observed return value of 2. This is a valid
linearization (it obeys FIFO queue semantics, respects each thread's own order, and
respects the real-time constraint that both enqueues preceded the dequeue), so the history
is linearizable, **even though `enqueue(2)` doesn't correspond to "the second call in
real wall-clock order"** — because the two enqueues were concurrent, either order is a
legitimate explanation of the observed behavior.

**A non-linearizable example.** Same setup, but suppose the dequeue instead returned `1`
in an implementation where the *only* possible correct FIFO orderings would have required
enqueue(1) to precede enqueue(2) *and* the actual code guarantees enqueue(2) definitely
completed-before dequeue started with no legal reordering producing 1 first under FIFO —
if no permutation respecting rules 2 and 3 can explain the returned value, the history is
not linearizable, and that's a genuine bug in the implementation (a stale read, a lost
update, or a misordered pointer swing).

### Linearizability vs. sequential consistency
A closely related, weaker criterion is **sequential consistency**: there must exist some
sequential ordering respecting each thread's own program order (rule 2 above) — but
**without** the real-time constraint (rule 3). Sequential consistency permits operations
to be reordered even when one has clearly, observably finished before another started in
real time, as long as each thread's own internal order is preserved. This makes
sequential consistency **non-composable** (combining two sequentially-consistent objects
doesn't guarantee the combination is sequentially consistent) — which is precisely why
linearizability, not sequential consistency, is the standard for concurrent object
correctness in this subject. Sequential consistency shows up instead as a hardware/
memory-model concept (what guarantees a machine gives about instruction ordering), a
related but distinct topic from per-object correctness.

### Why linearizability matters for later lessons
Every algorithm from `multiprocessor-programming/06` onward (concurrent lists, lock-free
stacks and queues) is *proved* correct by identifying its linearization points — this is
the standard proof technique, and understanding it here is a prerequisite for following
those correctness arguments rather than taking them on faith.

## Pros
- Composable: linearizable objects can be combined freely and the composed system remains
  linearizable, without needing to reason about cross-object interactions — an essential
  property for building larger systems out of smaller verified pieces.
- Matches programmer intuition closely: it formalizes "each operation appears to happen
  instantaneously at some point between its call and return," which is exactly how most
  programmers already informally think about atomic operations.
- Gives concrete algorithms a rigorous proof obligation (identify the linearization
  points) rather than a vague "seems right" argument.

## Cons
- Proving linearizability formally can be intricate, especially for lock-free algorithms
  where the linearization point of one thread's operation can depend on *another
  thread's* subsequent action ("helping," seen in `multiprocessor-programming/07` and
  `multiprocessor-programming/09`).
- It is a strong, sometimes stricter-than-necessary guarantee; some applications can
  tolerate weaker consistency (e.g. eventual consistency in distributed systems) for
  better performance, making linearizability occasionally the wrong (over-strong) tool
  outside single-machine shared-memory contexts.
- Linearizability alone says nothing about *progress* (whether operations complete in
  bounded time) — that's an orthogonal concern covered by
  `multiprocessor-programming/07`'s progress guarantees.

## Alternatives
- **Sequential consistency** — weaker (no real-time constraint), non-composable, more
  often used as a hardware/memory-model guarantee than a per-object correctness criterion.
- **Quiescent consistency** — only requires ordering to be preserved among operations
  separated by a period of no concurrent activity ("quiescence"); weaker still, sometimes
  used for high-performance counters/pools where strict ordering isn't needed.
- **Serializability** (from database theory) — a similar-sounding but distinct criterion
  for transactions (groups of multiple operations), which doesn't require real-time
  ordering the way linearizability does — easy to confuse with linearizability but
  answering a different question (transactional correctness, not single-operation
  correctness).

## When to use it
Use linearizability as your default correctness bar whenever designing or evaluating a
concurrent data structure meant to be a drop-in, "acts just like the sequential version"
replacement — locks, queues, stacks, counters, hash tables intended for general use. It's
the right lens any time you need to *prove* (not just informally argue) that a concurrent
implementation is correct.

## When NOT to use it
Don't insist on linearizability when a weaker, cheaper consistency model would satisfy
the application's real needs and buy meaningfully better performance — e.g., some metrics/
counters or caches can tolerate quiescent consistency or even looser guarantees. Also
don't confuse it with the guarantees you get for free from a language's default memory
model — linearizability is a per-object *design* correctness criterion, not something
that comes automatically from "using atomics" without careful design (see
`multiprocessor-programming/10`).

## Key takeaways / mental model
A concurrent object is linearizable if every execution can be explained by *some*
sequential reordering of its operations that preserves each thread's own call order and
never contradicts real-time "this finished before that started" facts — equivalently,
every operation can be pinned to a single instantaneous linearization point between its
invocation and response. This is the correctness bar every concurrent data structure in
the rest of this subject is measured against, and it's what makes concurrent objects
composable building blocks rather than things you must re-verify every time you combine
them.

## Self-check questions
1. State the three conditions a linearization must satisfy, and explain why the real-time
   ordering condition is what makes linearizability composable (unlike sequential
   consistency).
2. Work through a short history of your own construction (2-3 overlapping operations on a
   shared counter or stack) and find a valid linearization, or show that none exists.
3. What is a "linearization point," and why is identifying it the standard technique for
   proving a lock-free algorithm correct?
4. How does linearizability differ from sequential consistency, and why does that
   difference matter for whether the two properties compose across multiple objects?

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 3: "Concurrent
  Objects."
