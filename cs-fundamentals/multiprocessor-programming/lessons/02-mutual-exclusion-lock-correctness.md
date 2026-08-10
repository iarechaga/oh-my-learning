---
id: multiprocessor-programming/02
subject: multiprocessor-programming
title: Mutual exclusion and lock correctness criteria
slug: mutual-exclusion-lock-correctness
status: drafted
mastery:
seniority: mid
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 2
prerequisites: [multiprocessor-programming/01]
created: 2026-08-10
updated: 2026-08-10
---

# Mutual exclusion and lock correctness criteria

## TL;DR
Mutual exclusion means at most one thread executes a critical section at a time. A
correct lock must guarantee three properties simultaneously — **mutual exclusion**,
**deadlock-freedom**, and **starvation-freedom** — and the precise definitions of these
properties (not just "it seems to work") are what let you prove an algorithm correct
instead of merely testing it and hoping.

## The idea
`multiprocessor-programming/01` showed that compound operations like `counter++` have a
race window: a gap between reading and writing during which another thread can interleave
and corrupt the result. Mutual exclusion is the general solution pattern: wrap the
compound operation in a **critical section**, and ensure only one thread can be "inside"
that critical section at any moment. Everyone else who wants in must wait.

The catch is that "make everyone else wait" is easy to get wrong in ways that don't show
up in casual testing. A lock that occasionally lets two threads in at once is unsafe. A
lock that sometimes lets *no one* in — all contenders wait forever — is a **deadlock**. A
lock that always makes progress *for someone* but perpetually skips over one unlucky
thread is starving that thread, which is a correctness failure of a subtler kind (the
system as a whole isn't stuck, but that one thread's request is never honored). This
lesson defines these properties precisely, because "seems to work when I tried it" is
worthless as a correctness argument in the adversarial, fully-asynchronous model from
`multiprocessor-programming/01`.

## How it works

### The critical section problem
A **critical section** is a block of code accessing a shared resource that must not be
concurrently entered by more than one thread. A lock (mutual exclusion algorithm)
provides two operations, conventionally `lock()` and `unlock()`, that a thread calls
before and after its critical section:

```
lock.lock()
... critical section ...
lock.unlock()
```

The rest of a thread's code (not touching the shared resource) is its **non-critical
section**, which the lock places no constraints on.

### The three correctness properties

**1. Mutual exclusion (safety).** At any point in time, at most one thread is executing
its critical section. This is the property everything else exists to protect — violating
it reintroduces exactly the lost-update race from `multiprocessor-programming/01`.

**2. Deadlock-freedom (liveness, weak form).** If some thread calls `lock()` and is never
able to enter its critical section, then *other threads must be completing infinitely
many critical sections* — i.e., the system as a whole is never stuck with everyone
waiting and nobody progressing. Deadlock-freedom does **not** promise any particular
thread will ever get in; it only forbids *global* freezing where every contender waits
forever with no one making progress. A classic deadlock example (two locks acquired in
opposite order by two threads, each holding one and waiting for the other) violates even
this weak property — the whole system stalls.

**3. Starvation-freedom (liveness, strong form).** Every thread that calls `lock()`
eventually enters its critical section — no individual thread waits forever, even if
others keep succeeding. Starvation-freedom implies deadlock-freedom (if every individual
thread eventually gets in, the system obviously isn't globally stuck) but not vice versa:
an algorithm can be deadlock-free while still letting one unlucky thread lose every race
against faster rivals indefinitely.

**Worked example: why deadlock-freedom is weaker than starvation-freedom.** Imagine a
lock implemented so that whichever thread happens to write to a shared "next" variable
last wins access, and losers immediately retry. If thread A and thread B alternate races
and always beat thread C's stalled retries (perhaps C is scheduled on a slower core, or
just loses every coin flip under an adversarial scheduler), the system overall keeps
making progress — A and B keep completing critical sections — so it's deadlock-free. But
C never gets in. That's starvation: a real, if_subtle, correctness failure that
deadlock-freedom alone does not rule out.

### Additional desirable properties

**Bounded waiting / FIFO fairness.** A stronger fairness notion than starvation-freedom:
once a thread signals intent to enter (e.g. by taking a queue position), the number of
other threads that can enter *before* it is bounded (ideally, in strict first-come-first-
served order). This is what `multiprocessor-programming/03`'s bakery algorithm and
`multiprocessor-programming/04`'s queue locks (CLH/MCS) explicitly provide, whereas a
simple test-and-set lock does not.

**No assumptions about the number of threads (n) or hardware support** beyond what the
algorithm explicitly declares — some lock algorithms (like Peterson's, in
`multiprocessor-programming/03`) only work for exactly 2 threads and need generalization
to work for n; others assume specific hardware instructions (compare-and-swap, as covered
in `multiprocessor-programming/10`) that not all algorithms require.

### Verifying correctness: proof sketch pattern
A rigorous mutual-exclusion proof typically argues by contradiction: assume two threads
are simultaneously in their critical sections, then trace the sequence of reads/writes
each must have performed to get there, and show this sequence is impossible given the
algorithm's logic (e.g., "thread A wrote `turn = B` before checking `flag[B]`, so if B
was also inside, B must have read `turn == A` at some point after A set it to B — a
contradiction"). `multiprocessor-programming/03` walks through this style of proof
concretely for Peterson's algorithm.

## Pros
- Precise definitions (mutual exclusion, deadlock-freedom, starvation-freedom) let you
  *prove* an algorithm correct for all interleavings, not just the ones observed in
  testing — testing concurrent code is notoriously bad at finding rare race windows.
- The framework composes: any algorithm proven to satisfy these properties can be reused
  as a building block (e.g., protecting an arbitrary critical section) without needing to
  re-reason about the specific shared resource inside.
- Separating safety (mutual exclusion) from liveness (deadlock/starvation-freedom) makes
  it clear that a "safe but stuck" lock and an "always moving but occasionally unfair"
  lock are different failure categories requiring different fixes.

## Cons
- Precise proofs are labor-intensive; most working engineers rely on well-known,
  pre-proven algorithms (this subject's later lessons) rather than proving new locks
  correct from scratch.
- Starvation-freedom and bounded waiting often cost real performance (more bookkeeping,
  more memory traffic) compared to weaker deadlock-free-only locks — see
  `multiprocessor-programming/04`'s discussion of the fairness/scalability trade-off.
- These properties say nothing about *performance under contention* — a starvation-free
  lock can still be catastrophically slow if many threads hammer it simultaneously
  (`multiprocessor-programming/04` covers why and what to do about it).

## Alternatives
- **Lock-free / wait-free algorithms** (`multiprocessor-programming/07`) — sidestep
  mutual exclusion entirely by ensuring correctness without ever blocking a thread on
  another; a fundamentally different approach with its own trade-offs (much harder to
  design correctly, but immune to the "one stalled thread blocks everyone" failure mode
  locks have).
- **Transactions / software transactional memory** (`multiprocessor-programming/13`) —
  lets the programmer write code as if it always has exclusive access, with the runtime
  detecting conflicts and retrying, trading explicit lock management for a different
  (sometimes simpler, sometimes costlier) correctness model.

## When to use it
Reach for mutual exclusion whenever a critical section performs multiple related reads
and writes to shared state that must appear atomic to other threads (e.g., updating two
related fields together, or a compound "check-then-act" sequence) — locking is the most
directly understandable tool, and starvation-freedom is worth insisting on whenever
fairness among threads matters (e.g., a shared resource serving user-facing requests
where one client should never be perpetually starved).

## When NOT to use it
Don't reach for full mutual exclusion when a single atomic hardware operation (compare-
and-swap, fetch-and-add — `multiprocessor-programming/10`) already solves the problem
directly (e.g., a simple counter increment) — locking adds unnecessary blocking overhead
for something that doesn't need a critical section at all. Also avoid locks acquired in
inconsistent order across different code paths — that's the classic recipe for deadlock,
which even the weakest correctness property here forbids.

## Key takeaways / mental model
A correct lock is not just "usually keeps two threads apart" — it must provably satisfy
mutual exclusion (safety: never two threads inside at once), deadlock-freedom (the system
as a whole always keeps moving), and ideally starvation-freedom (every individual thread
eventually gets in). Deadlock-freedom is strictly weaker than starvation-freedom: a lock
can keep the system moving overall while starving one specific thread forever. These
three properties are the yardstick every lock algorithm in this subject
(`multiprocessor-programming/03`, `multiprocessor-programming/04`) is measured against.

## Self-check questions
1. Define mutual exclusion, deadlock-freedom, and starvation-freedom in your own words,
   and explain precisely why starvation-freedom implies deadlock-freedom but not the
   reverse.
2. Construct a scenario (in prose) where a lock is deadlock-free but not starvation-free.
3. Why is "I tested this lock with 10 threads for an hour and it worked" insufficient
   evidence of correctness in the fully asynchronous model from
   `multiprocessor-programming/01`?
4. What's the difference between a safety property and a liveness property, and which
   category does each of the three correctness criteria fall into?

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 2: "Mutual
  Exclusion."
