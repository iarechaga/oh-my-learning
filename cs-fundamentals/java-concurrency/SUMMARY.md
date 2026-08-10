# Java Concurrency in Practice (Goetz et al.) - Subject Summary

A correctness-first, mechanism-by-mechanism recap of *Java Concurrency in Practice*
(Brian Goetz et al.), concept by concept - from what a race condition actually is, through
the Java Memory Model, task execution, and advanced synchronizers, to designing resilient
concurrent services.

**Progress note:** all 15 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded. This summary will gain depth
(especially on the concepts you find hard) as discussions happen - the "Focus areas"
section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
safety fundamentals first, then composing thread-safe classes and avoiding liveness
hazards, then execution frameworks, then advanced synchronization, then performance,
testing, and resilient service design.

## Safety fundamentals

- **[java-concurrency/01] Threads, shared state, and race conditions** - the lost-update
  interleaving on a plain `value++` and why race conditions can pass every test on a
  laptop and fail constantly in production. ([lesson](lessons/01-threads-shared-state-races.md))
- **[java-concurrency/02] Immutability, confinement, and thread safety basics** - the
  cheapest fixes for a race (don't allow mutation, don't allow sharing) and why unsafe
  publication of `this` from a constructor can leak a partially-built object to another
  thread. ([lesson](lessons/02-immutability-confinement-thread-safety.md))
- **[java-concurrency/03] Java Memory Model and happens-before** - why "the write should
  obviously be visible" is false without an explicit happens-before edge, and the eight
  rules (program order, monitor lock, volatile, thread start/join, interruption, final
  field, transitivity) that establish one. ([lesson](lessons/03-java-memory-model-happens-before.md))
- **[java-concurrency/04] Synchronization with intrinsic locks** - `synchronized` as
  mutual exclusion plus visibility in one mechanism, and why a lock only protects an
  invariant if every access, including reads, goes through it. ([lesson](lessons/04-synchronization-intrinsic-locks.md))

## Composing thread-safe classes and avoiding liveness hazards

- **[java-concurrency/05] Building and composing thread-safe classes** - identifying
  state and invariants before picking a synchronization policy, and why thread safety
  does not compose automatically once an invariant spans more than one already-safe
  field. ([lesson](lessons/05-composing-thread-safe-classes.md))
- **[java-concurrency/06] Liveness hazards: deadlock, starvation, livelock** - the
  circular-lock-ordering deadlock pattern, its fix via a consistent global lock order,
  and how starvation and livelock differ from deadlock on the "is anyone making progress"
  axis. ([lesson](lessons/06-liveness-hazards.md))

## Task execution and asynchronous results

- **[java-concurrency/07] Concurrent collections and blocking queues** - atomic compound
  operations (`computeIfAbsent`, `putIfAbsent`) that remove check-then-act races, and why
  bounding a `BlockingQueue` converts overload into explicit backpressure instead of a
  slow-motion memory leak. ([lesson](lessons/07-concurrent-collections-blocking-queues.md))
- **[java-concurrency/08] Task execution with Executor framework** - `ThreadPoolExecutor`'s
  exact task-arrival flow (new thread vs. queue vs. reject) and why the `Executors`
  convenience factories hide an unbounded queue or unbounded thread count behind an
  innocuous one-liner. ([lesson](lessons/08-executor-framework.md))
- **[java-concurrency/09] Callable, Future, and asynchronous result handling** - "start
  now, collect later" via `submit()`/`get()`, and how `CompletableFuture` composes
  dependent async steps without a thread blocked at every stage. ([lesson](lessons/09-callable-future-async-results.md))
- **[java-concurrency/10] Cancellation, interruption, and shutdown policies** - why Java
  has no safe way to forcibly stop a thread, and the one rule that matters most in
  practice: never swallow `InterruptedException` - propagate it or restore the flag.
  ([lesson](lessons/10-cancellation-interruption-shutdown.md))

## Advanced synchronization

- **[java-concurrency/11] Explicit locks, conditions, and advanced synchronizers** -
  `ReentrantLock`'s `tryLock`/timeouts/interruptibility beyond what `synchronized` can
  offer, multiple `Condition`s per lock, and the purpose-built synchronizers
  (`CountDownLatch`, `Semaphore`, `CyclicBarrier`, `Exchanger`) for common coordination
  shapes. ([lesson](lessons/11-explicit-locks-conditions-synchronizers.md))
- **[java-concurrency/12] Atomic variables and nonblocking techniques** - compare-and-swap
  as a retry-instead-of-block alternative to locking, the "immutable snapshot + atomic
  swap" pattern for multivariable state, and the ABA problem. ([lesson](lessons/12-atomic-variables-nonblocking.md))

## Performance, testing, and resilient service design

- **[java-concurrency/13] Performance and scalability under contention** - Amdahl's Law
  as a hard ceiling on parallel speedup set by the serial fraction, and reducing lock
  scope and granularity to shrink that fraction, always justified by measurement.
  ([lesson](lessons/13-performance-scalability-contention.md))
- **[java-concurrency/14] Testing and debugging concurrent Java programs** - separating
  safety tests from liveness tests, deliberately widening the interleaving window
  (oversubscription, repeated runs) to expose rare races, and tools like thread dumps and
  `jcstress`. ([lesson](lessons/14-testing-debugging-concurrency.md))
- **[java-concurrency/15] Designing cancellation-safe and resilient services** -
  synthesizing the subject into a production checklist: bounded queues with deliberate
  backpressure, isolated pools, universal timeouts, graceful shutdown, idempotency, and
  circuit breaking. ([lesson](lessons/15-cancellation-safe-resilient-services.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
