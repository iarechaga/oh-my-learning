---
id: multiprocessor-programming/07
subject: multiprocessor-programming
title: "Progress guarantees: obstruction-free, lock-free, wait-free"
slug: progress-guarantees
status: drafted
mastery:
seniority: senior
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 3
prerequisites: [multiprocessor-programming/05]
created: 2026-08-10
updated: 2026-08-10
---

# Progress guarantees: obstruction-free, lock-free, wait-free

## TL;DR
Beyond correctness (linearizability), a concurrent algorithm makes a **progress**
promise: obstruction-free means a thread finishes if it eventually runs alone; lock-free
means the *system* always makes progress even if individual threads stall; wait-free
means *every* thread finishes in a bounded number of its own steps regardless of what
other threads do. These are strictly ordered guarantees (wait-free implies lock-free
implies obstruction-free), each strictly harder to achieve and generally costlier to
implement than the one before.

## The idea
`multiprocessor-programming/05` established what "correct" means for a concurrent
object (linearizability) — but correctness alone says nothing about whether operations
actually *finish*. A lock-based structure (`multiprocessor-programming/06`) can be
perfectly linearizable while a thread holding a lock is preempted mid-critical-section,
leaving every other thread blocked indefinitely — correct, but stuck. Progress
guarantees are the orthogonal axis: independent of whether the *answer* is right, how
strongly can you promise that operations *complete*, and under what adversarial
conditions? This distinction matters enormously in practice: a system where one stalled
thread (descheduled by the OS, or crashed) can freeze every other thread's operations on
a shared structure is fragile in ways a wait-free structure simply cannot be.

## How it works

### The progress spectrum, from weakest to strongest

**Blocking (baseline, not itself a "progress guarantee").** Lock-based algorithms
(`multiprocessor-programming/02` through `multiprocessor-programming/04`,
`multiprocessor-programming/06`'s coarse/fine-grained/optimistic/lazy list variants) can
have a thread's progress depend entirely on another thread's cooperation — if the lock
holder is preempted, crashes, or is simply slow, waiters are stuck no matter how fast
they themselves could otherwise run. This is the failure mode every stronger progress
guarantee below eliminates to different degrees.

**Obstruction-free.** A thread is guaranteed to complete its operation **if it eventually
runs alone for long enough** (no other threads take steps during that window) — even
though in general, with other threads active, it might be perpetually interrupted and
forced to abort/retry forever. This is a surprisingly weak guarantee in practice: an
adversarial scheduler that never gives any single thread an uninterrupted window can
cause **livelock** — every thread keeps making individual steps, none of them ever
completes, an infinite retry loop where the system is "moving" (unlike deadlock) but no
operation ever finishes. Obstruction-freedom typically requires an added **contention
manager** (e.g., randomized or exponential backoff before retrying) bolted on top to make
livelock unlikely in practice, but the core algorithm alone doesn't rule it out.

**Lock-free.** A stronger guarantee: **the system as a whole always makes progress** —
at any point, if you look far enough into the future, *some* thread's operation will
complete, even if any specific thread might be perpetually overtaken by others (this is
the exact same "system-wide, not per-thread" pattern as deadlock-freedom versus
starvation-freedom from `multiprocessor-programming/02`). Lock-free algorithms typically
achieve this via a CAS-retry loop (`multiprocessor-programming/10`): a thread attempts an
atomic update, and if it fails (another thread's concurrent update won the race), it
retries — but crucially, **every failed CAS means some other thread's operation
succeeded**, so the system is guaranteed to be making progress even though the specific
retrying thread might, in a bad-luck adversarial schedule, keep losing indefinitely
(theoretically possible, though vanishingly unlikely in practice with real schedulers).

**Wait-free.** The strongest guarantee: **every thread completes its operation within a
bounded number of its own steps**, regardless of the speed or scheduling of any other
threads — no thread can ever be starved, not even in the worst adversarial case. This
eliminates livelock entirely (unlike obstruction-free) and eliminates the "individual
thread could theoretically starve forever" gap that lock-free leaves open. Wait-free
algorithms are correspondingly the hardest to design and often the most expensive to run
(more bookkeeping per operation to guarantee the bound), which is why they are reserved
for cases where starvation is genuinely unacceptable (real-time systems, cross-thread
"helping" protocols like the universal constructions in `multiprocessor-programming/08`).

### The strict implication ordering
Wait-free implies lock-free implies obstruction-free — each stronger guarantee is a
strict superset of promises made by the weaker ones:
```
wait-free  ⊂  lock-free  ⊂  obstruction-free  ⊂  blocking (no guarantee)
(strongest)                                              (weakest / none)
```
An algorithm can always be *weakened* trivially (a wait-free algorithm is automatically
lock-free and obstruction-free too), but going the other direction — strengthening an
obstruction-free algorithm into a lock-free one, or a lock-free one into wait-free — is
real, often substantial, extra design work, not automatic.

### Worked example: a CAS-based counter across the spectrum
Consider a shared counter's `increment()`.
- **Blocking version**: acquire a lock, read-modify-write, release. If the lock holder is
  preempted mid-critical-section, every other thread waiting on `increment()` is stuck
  until the OS reschedules the holder.
- **Lock-free version**: loop `do { old = counter.get(); } while (!CAS(counter, old, old+1))`.
  If thread A's CAS fails because thread B's concurrent CAS succeeded first, A retries —
  but note B's `increment()` *did* complete, so the counter's value moved forward: the
  system made progress even though A individually had to retry. If threads keep
  colliding, some thread's CAS always wins each round, so the counter always moves
  forward — lock-free, not blocking.
- **Wait-free version**: give each thread a pre-allocated slot in an array; `increment()`
  writes to the thread's own slot (contention-free, no retry needed at all), and `get()`
  sums all slots. Every thread's `increment()` finishes in one bounded step, no matter
  what other threads do — genuinely wait-free, though at the cost of `get()` now needing
  to read n slots instead of one shared word (a classic progress-guarantee-for-performance
  trade-off).

### Why obstruction-free needs a contention manager in practice
Obstruction-freedom's "completes if it eventually runs alone" clause is dangerously weak
on its own: two threads that keep interrupting each other symmetrically (each undoing
progress the other made, then getting interrupted in turn) can loop forever, technically
satisfying the obstruction-free contract (neither is ever *proven* unable to finish if
given a clear run) while never actually finishing in the schedule that actually occurs.
Real obstruction-free algorithms pair the core logic with a **contention manager** — a
policy (e.g. randomized exponential backoff, similar in spirit to
`multiprocessor-programming/04`'s lock backoff) that makes such adversarial coincidences
statistically unlikely, converting a theoretical liveness gap into a practically
negligible one, though not a provable bound the way lock-free/wait-free give you.

## Pros
- The spectrum gives a precise vocabulary for a real, practically important distinction:
  "does this algorithm degrade gracefully if a thread is preempted/crashes mid-operation?"
  — a question every concurrent system design eventually has to answer.
- Lock-free and wait-free algorithms are immune to the specific failure mode where a
  single stalled/crashed thread (holding a lock) freezes every other thread — a real,
  serious operational risk for lock-based systems (e.g. in real-time or fault-tolerant
  contexts).
- The strict implication ordering gives a clear cost/benefit ladder: you can choose the
  weakest guarantee that satisfies your actual requirements rather than over- or under-
  engineering.

## Cons
- Stronger progress guarantees generally cost more: more retries under contention (lock-
  free), or more bookkeeping/helping machinery (wait-free) — performance in the common
  (uncontended) case is often worse than an equivalent well-tuned lock, even though worst-
  case behavior is much better.
- Wait-free algorithms in particular are notoriously difficult to design correctly; many
  wait-free constructions for non-trivial data structures are academically significant
  results, not routine engineering.
- Progress guarantees say nothing about linearizability or vice versa — you still need
  the correctness proof from `multiprocessor-programming/05` on top of the progress
  proof; the two are separate, both-required obligations.

## Alternatives
- **Blocking locks** (`multiprocessor-programming/04`) remain the pragmatic default for
  most application code — the extra complexity of lock-free/wait-free design is only
  worth it when the specific failure modes it prevents (priority inversion, a stalled
  thread freezing others) are real operational risks.
- **Universal constructions** (`multiprocessor-programming/08`) offer a different angle:
  a generic recipe to turn *any* sequential object into a wait-free (or lock-free)
  concurrent one via consensus primitives, rather than hand-designing a bespoke
  progress-guaranteed algorithm per data structure.

## When to use it
Reach for lock-free algorithms when you need the system to keep making progress even if
individual threads are frequently preempted (e.g. in an environment with more threads
than cores, or unpredictable scheduling) but occasional individual-thread retries are
acceptable. Reach for wait-free specifically when starvation of any single thread is
unacceptable — real-time systems with hard per-operation deadlines, or contexts (like
signal handlers, or cross-thread helping protocols) where a thread genuinely cannot be
allowed to depend on another thread's cooperation to finish.

## When NOT to use it
Don't reach for lock-free or wait-free designs by default — for most application-level
code with short critical sections and low-to-moderate contention, a well-implemented lock
(`multiprocessor-programming/04`) is simpler to write, easier to reason about, and often
just as fast in practice; the added design and maintenance complexity of lock-free/wait-
free code is real and should be spent only where the specific guarantees are actually
needed.

## Key takeaways / mental model
Progress guarantees answer "does this operation finish, and under what adversarial
conditions?" — a question orthogonal to correctness (linearizability). Obstruction-free
only promises completion in isolation (vulnerable to livelock without a contention
manager); lock-free promises the *system* always progresses even if individual threads
can theoretically starve; wait-free promises *every* thread finishes in bounded steps no
matter what. The ordering wait-free ⊂ lock-free ⊂ obstruction-free is strict, and moving
up the ladder is real engineering work, not free — pick the weakest guarantee that
actually matches your failure-mode tolerance.

## Self-check questions
1. Explain the difference between lock-free and wait-free using the "system progress"
   versus "every thread's progress" framing, and give an example of a lock-free but not
   wait-free algorithm.
2. Why is obstruction-freedom alone vulnerable to livelock, and what practical mechanism
   is typically added to make it usable?
3. Walk through the CAS-retry counter example: explain precisely why a failed CAS for one
   thread still counts as "system progress" under the lock-free definition.
4. A payments system cannot tolerate any single request being starved indefinitely, even
   under heavy concurrent load. Which progress guarantee would you require, and why would
   a merely lock-free algorithm be insufficient?

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 3: "Concurrent
  Objects" (progress conditions).
