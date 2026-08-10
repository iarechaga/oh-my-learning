# The Art of Multiprocessor Programming - Subject Summary

A correctness-first tour of concurrent algorithm design, from the shared-memory model
through lock-based structures to nonblocking algorithms and advanced synchronization,
following Herlihy and Shavit's *The Art of Multiprocessor Programming*.

**Progress note:** all 13 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded. This summary will gain depth
(especially on the concepts you find hard) as discussions happen - the "Focus areas"
section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
the shared-memory model and mutual exclusion first, then correctness and lock-based
structures, then progress guarantees and consensus, then nonblocking algorithms and
advanced synchronization.

## Foundations: shared memory and mutual exclusion

- **[multiprocessor-programming/01] Concurrency model and shared-memory assumptions** -
  the fully asynchronous, adversarial-scheduler model every algorithm in this subject is
  proven correct under, and why compound operations like `counter++` have a race window
  even though single reads/writes are atomic. ([lesson](lessons/01-concurrency-model-shared-memory.md))
- **[multiprocessor-programming/02] Mutual exclusion and lock correctness criteria** -
  the precise definitions of mutual exclusion, deadlock-freedom, and starvation-freedom,
  and why deadlock-freedom is strictly weaker than starvation-freedom.
  ([lesson](lessons/02-mutual-exclusion-lock-correctness.md))
- **[multiprocessor-programming/03] Classic lock algorithms (Peterson, bakery,
  tournament)** - proving mutual exclusion is achievable from plain atomic reads/writes
  alone, from Peterson's 2-thread lock to bakery's FIFO n-thread ticket scheme to
  tournament's O(log n) binary-bracket composition. ([lesson](lessons/03-classic-lock-algorithms.md))
- **[multiprocessor-programming/04] Scalable locks (TAS, TTAS, CLH, MCS, backoff)** -
  why naive test-and-set spinlocks collapse under contention via cache-coherence
  traffic, and how TTAS, exponential backoff, and queue locks (CLH, MCS) fix it while
  adding FIFO fairness. ([lesson](lessons/04-scalable-locks.md))

## Correctness and concurrent structures

- **[multiprocessor-programming/05] Linearizability and correctness of concurrent
  objects** - the composable correctness criterion for concurrent data structures:
  every execution must be explainable by some sequential reordering respecting program
  order and real-time ordering. ([lesson](lessons/05-linearizability-correctness.md))
- **[multiprocessor-programming/06] Concurrent linked lists and skip lists** - the
  coarse-to-lazy locking progression (coarse-grained, fine-grained, optimistic, lazy)
  that pushes synchronization cost off reads and onto writes, extended to skip lists for
  O(log n) ordered search. ([lesson](lessons/06-concurrent-lists-skip-lists.md))
- **[multiprocessor-programming/07] Progress guarantees: obstruction-free, lock-free,
  wait-free** - the strict ladder of liveness promises beyond correctness, and why
  obstruction-freedom alone is vulnerable to livelock without a contention manager.
  ([lesson](lessons/07-progress-guarantees.md))

## Consensus and universal synchronization power

- **[multiprocessor-programming/08] Universal constructions with consensus primitives**
  - the generic recipe that turns any sequential object into a wait-free concurrent one
  via repeated consensus and cross-thread helping. ([lesson](lessons/08-universal-constructions-consensus.md))
- **[multiprocessor-programming/09] Consensus hierarchy and synchronization power** -
  Herlihy's proof that primitives have an absolute consensus-number ceiling (registers at
  1, test-and-set/FAA at 2, compare-and-swap at infinity), explaining why hardware
  standardized on CAS. ([lesson](lessons/09-consensus-hierarchy.md))

## Nonblocking algorithms in practice

- **[multiprocessor-programming/10] Atomic primitives (CAS, FAA) and ABA hazards** - the
  CAS-retry loop pattern and the ABA problem, where a value cycling A->B->A defeats a
  naive compare-and-swap's staleness check. ([lesson](lessons/10-atomic-primitives-aba.md))
- **[multiprocessor-programming/11] Lock-free stacks and queues** - Treiber's stack and
  its elimination-backoff variant, and the Michael-Scott queue's two-step enqueue with
  cross-thread helping to advance a lagging tail pointer. ([lesson](lessons/11-lock-free-stacks-queues.md))
- **[multiprocessor-programming/12] Memory reclamation (hazard pointers, epochs)** - how
  to safely free an unlinked node with no lock to coordinate the check, via per-node
  hazard-pointer publication or coarser epoch-based batching.
  ([lesson](lessons/12-memory-reclamation.md))
- **[multiprocessor-programming/13] Software transactional memory and composable
  synchronization** - optimistic, rollback-on-conflict atomic blocks that compose freely
  by nesting, closing a gap locks cannot close in general - at the cost of wasted work on
  abort and incompatibility with irrevocable side effects like I/O.
  ([lesson](lessons/13-software-transactional-memory.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
