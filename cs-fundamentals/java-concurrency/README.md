# Java Concurrency in Practice

This subject teaches how to build correct and maintainable concurrent Java code under
real JVM constraints. It starts with safety and the Java Memory Model, then moves into
task execution, cancellation, performance, and composing robust thread-safe components.

**Source book:** *Java Concurrency in Practice* - Brian Goetz, Tim Peierls, Joshua Bloch, Joseph Bowbeer, David Holmes, and Doug Lea (Addison-Wesley, 2006).

**Seniority baseline:** senior (lessons range mid->senior).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`java-concurrency/<NN>`* (e.g. *"discuss `java-concurrency/03`"*). Ordered by dependency: correctness fundamentals first, then execution frameworks and lifecycle concerns, then performance and advanced patterns.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Threads, shared state, and race conditions | mid | drafted | — | — | [lesson](lessons/01-threads-shared-state-races.md) | — |
| 02  | Immutability, confinement, and thread safety basics | mid | drafted | — | — | [lesson](lessons/02-immutability-confinement-thread-safety.md) | — |
| 03  | Java Memory Model and happens-before | senior | drafted | — | — | [lesson](lessons/03-java-memory-model-happens-before.md) | — |
| 04  | Synchronization with intrinsic locks | mid | drafted | — | — | [lesson](lessons/04-synchronization-intrinsic-locks.md) | — |
| 05  | Building and composing thread-safe classes | senior | drafted | — | — | [lesson](lessons/05-composing-thread-safe-classes.md) | — |
| 06  | Liveness hazards: deadlock, starvation, livelock | senior | drafted | — | — | [lesson](lessons/06-liveness-hazards.md) | — |
| 07  | Concurrent collections and blocking queues | mid | drafted | — | — | [lesson](lessons/07-concurrent-collections-blocking-queues.md) | — |
| 08  | Task execution with Executor framework | mid | drafted | — | — | [lesson](lessons/08-executor-framework.md) | — |
| 09  | Callable, Future, and asynchronous result handling | mid | drafted | — | — | [lesson](lessons/09-callable-future-async-results.md) | — |
| 10  | Cancellation, interruption, and shutdown policies | senior | drafted | — | — | [lesson](lessons/10-cancellation-interruption-shutdown.md) | — |
| 11  | Explicit locks, conditions, and advanced synchronizers | senior | drafted | — | — | [lesson](lessons/11-explicit-locks-conditions-synchronizers.md) | — |
| 12  | Atomic variables and nonblocking techniques | senior | drafted | — | — | [lesson](lessons/12-atomic-variables-nonblocking.md) | — |
| 13  | Performance and scalability under contention | senior | drafted | — | — | [lesson](lessons/13-performance-scalability-contention.md) | — |
| 14  | Testing and debugging concurrent Java programs | senior | drafted | — | — | [lesson](lessons/14-testing-debugging-concurrency.md) | — |
| 15  | Designing cancellation-safe and resilient services | senior | drafted | — | — | [lesson](lessons/15-cancellation-safe-resilient-services.md) | — |

**Cross-subject prerequisites** (recommended): `multiprocessor-programming/05` for linearizability basics and `multiprocessor-programming/07` for lock-free progress guarantees.

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` · `mid` · `senior` · `staff` · `principal` - the band whose job the concept anchors.
