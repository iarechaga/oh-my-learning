---
id: multiprocessor-programming/04
subject: multiprocessor-programming
title: Scalable locks (TAS, TTAS, CLH, MCS, backoff)
slug: scalable-locks
status: drafted
mastery:
seniority: senior
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 7
prerequisites: [multiprocessor-programming/03]
created: 2026-08-10
updated: 2026-08-10
---

# Scalable locks (TAS, TTAS, CLH, MCS, backoff)

## TL;DR
Real production locks are built on the hardware atomic instruction **test-and-set** (or
compare-and-swap), but naive spinning on it causes catastrophic cache-coherence traffic
under contention. Test-and-test-and-set (TTAS) plus exponential backoff greatly reduces
that traffic; queue locks (CLH and MCS) go further by having each thread spin on its
*own* local memory location instead of a shared one, giving genuinely scalable behavior
even with dozens of contending threads.

## The idea
`multiprocessor-programming/03` proved mutual exclusion is achievable from plain reads
and writes alone, but those algorithms don't scale — bakery is O(n) per acquisition, and
even the O(log n) tournament lock touches many shared variables per acquisition. Real
hardware gives you a much more powerful primitive: an atomic **read-modify-write**
instruction like **compare-and-swap (CAS)** (detailed in `multiprocessor-programming/10`),
which lets you build a mutual exclusion lock in just a few lines. But the naive way of
using it — every waiting thread hammering the same shared memory location in a spin loop
— creates a new problem invisible in the correctness proofs: **contention**. On a cache-
coherent multiprocessor, every write to a shared cache line by any core invalidates that
line in every other core's cache, forcing them to refetch it over the shared bus/
interconnect. A tight spin loop on one shared word turns into a storm of cache-invalidation
traffic that can slow the *entire system* down, not just the lock's own throughput. This
lesson is about locks engineered specifically to avoid that storm.

## How it works

### Test-and-set (TAS): the naive baseline
The hardware `test-and-set(m)` instruction atomically writes `true` to memory location
`m` and returns `m`'s *previous* value, as one indivisible step. A spinlock built on it:

```
lock():
    while (test-and-set(locked) == true) { /* spin */ }
unlock():
    locked = false
```

Every iteration of the spin loop performs a **write** (`test-and-set` always writes,
regardless of the previous value), so every spinning thread continuously invalidates the
`locked` cache line for every other core, even while the lock is held and no thread could
possibly succeed. Under contention with many threads, this generates enormous bus traffic
and can make throughput *worse* as more threads compete — the opposite of what you want
from concurrency.

### Test-and-test-and-set (TTAS): read before you write
The fix: spin on a plain **read** first, and only attempt the atomic `test-and-set` once
the read suggests the lock might be free:

```
lock():
    while (true):
        while (locked == true) { /* spin reading, no writes */ }
        if (test-and-set(locked) == false) return  // got it
unlock():
    locked = false
```

While the lock is held, spinning threads only re-read a cached copy of `locked` (cache-
coherence protocols let all cores hold a shared *read-only* copy of a cache line cheaply
— no bus traffic on repeated reads of an unchanged line). Only when the lock actually
becomes free does contention briefly spike (every spinning thread's cache invalidates
simultaneously and they all race to `test-and-set`), but that spike is far shorter-lived
than TAS's constant hammering. TTAS is a strict improvement over TAS in practice, though
it still has a burst of contention right at lock release.

### Exponential backoff: spreading out the retry storm
TTAS's release-time burst — every waiter simultaneously retrying `test-and-set` — can
still be costly with many threads, because most of them will fail and have to retry
again. **Exponential backoff** adds a randomized delay after each failed attempt, doubling
(within a cap) on each successive failure:

```
lock():
    delay = MIN_DELAY
    while (true):
        while (locked == true) { /* spin reading */ }
        if (test-and-set(locked) == false) return
        sleep(random(0, delay))
        delay = min(delay * 2, MAX_DELAY)
```

**Worked example.** Eight threads all see the lock become free at once. Without backoff,
all eight immediately retry `test-and-set` — one wins, seven fail and immediately retry
again, repeating the storm. With backoff, the seven losers each wait a randomized delay
before retrying, spreading their retries out over time instead of all colliding again
immediately — dramatically reducing wasted contention. The trade-off: backoff adds latency
(a thread might wait longer than strictly necessary) and needs careful tuning of the
delay bounds — too small and it barely helps; too large and lightly-contended lock
acquisitions become needlessly slow.

### Queue locks: CLH
TTAS+backoff still has every thread spinning on the *same* shared `locked` variable (just
less often). **Queue locks** eliminate this entirely by having each thread spin on a
**different, thread-local** memory location, so a lock release only ever wakes up exactly
one waiting thread instead of causing a scramble among all of them.

**CLH lock mechanism.** Threads form an implicit linked list (via a shared tail pointer)
of "queue nodes," each holding a boolean `locked` field. To acquire:
1. Thread creates a new node with `locked = true`.
2. Atomically swaps itself in as the new tail, obtaining a reference to the *previous*
   tail node (its predecessor).
3. Spins on **its predecessor's** `locked` field (not its own, and not a single global
   variable) until it becomes `false`.

To release, a thread sets its **own** node's `locked` field to `false` — which wakes up
exactly the one thread spinning on that specific node, nobody else. Because each thread
spins on a distinct memory location, a release invalidates exactly one other core's
cache line, not all of them — this is the key scalability win. CLH nodes are conceptually
a linked list, but on cache-coherent (NUMA-flat) machines the predecessor's node might be
physically far away in memory, which is CLH's main practical weakness on NUMA hardware.

### Queue locks: MCS
**MCS lock** (Mellor-Crummey and Scott) achieves the same goal — each thread spins on its
own location — via an *explicit* linked list instead of CLH's implicit one, which fixes
CLH's NUMA locality issue: each thread spins on a field of its **own** node (allocated
locally), not a predecessor's node that might be remote.

**Mechanism.** Each thread has a node with a `next` pointer and a `locked` flag.
1. Thread atomically swaps itself onto the shared tail pointer, getting the previous tail
   (its predecessor) if any.
2. If there was a predecessor, thread sets `locked = true` on its own node, then sets the
   predecessor's `next` pointer to point to itself, then spins on its **own** `locked`
   field.
3. To release: if the thread's own `next` pointer is still null, try to CAS the tail
   pointer back to null (meaning no one is waiting); if that fails (someone joined the
   queue between check and CAS) or `next` is already set, wait until `next` becomes
   visible, then set the successor's `locked = false`, waking exactly that one thread.

MCS is the standard choice for high-contention production locks (it's essentially what
Linux's `qspinlock` and many language runtimes' internal locks are inspired by) because it
combines: O(1) cache-coherence traffic per acquisition/release (each op touches at most a
constant number of cache lines), strict FIFO fairness (the queue order is the acquisition
order — starvation-free by construction), and good NUMA behavior (each thread spins
locally).

### Comparing the family
| Lock | Spins on | Cache traffic under contention | Fairness |
| --- | --- | --- | --- |
| TAS | shared `locked` | very high (write every iteration) | none |
| TTAS | shared `locked` | high burst at release, low while held | none |
| TTAS+backoff | shared `locked` | reduced burst (spread over time) | none |
| CLH | predecessor's node (implicit list) | O(1) per op, but remote memory on NUMA | FIFO |
| MCS | own node (explicit list) | O(1) per op, local memory | FIFO |

## Pros
- TTAS+backoff is a trivial, drop-in improvement over naive TAS with almost no added
  complexity — a "free" win any time TAS-based spinning is found in real code.
- Queue locks (CLH, MCS) give both scalability (O(1) traffic per operation regardless of
  n) and strong fairness (FIFO) simultaneously — a combination the classic algorithms in
  `multiprocessor-programming/03` couldn't achieve without O(n) or O(log n) cost.
- MCS in particular is the practical, production-grade choice underlying many real
  operating-system and language-runtime locks.

## Cons
- Queue locks add implementation complexity (explicit node management, careful handling
  of the release race in MCS) compared to a one-line TAS spinlock.
- CLH's implicit-list spinning-on-predecessor pattern performs poorly on NUMA machines
  where the predecessor's memory may be on a remote node — a real practical wrinkle MCS
  was designed to fix.
- All spin-based locks (this whole family) waste CPU cycles busy-waiting instead of
  yielding the core to other work — fine for very short critical sections, wasteful for
  long ones, where a blocking (OS-level sleep/wake) lock is usually preferable.

## Alternatives
- **Blocking locks (mutexes with OS-level sleep/wake)** — instead of spinning, a thread
  that can't acquire the lock yields the CPU to the OS scheduler and is woken when the
  lock becomes available; better for long critical sections or when there are more
  threads than cores, at the cost of context-switch latency, which spinning avoids for
  short critical sections.
- **Lock-free data structures** (`multiprocessor-programming/07`, `multiprocessor-programming/11`)
  — avoid the lock/unlock pattern entirely, sidestepping contention-under-a-lock issues at
  the cost of substantially harder algorithm design.

## When to use it
Use TTAS+backoff as the minimum acceptable spinlock whenever you must hand-roll one (TAS
alone should essentially never be used in production). Reach for MCS (or a library that
implements it, e.g. most modern OS kernels' internal locks) whenever contention is
expected to be significant — many threads, frequent acquisition — and fairness matters.
Spin locks in general are appropriate only when critical sections are short (a few
instructions) and you expect the wait to be brief.

## When NOT to use it
Don't use any spin lock (TAS, TTAS, CLH, MCS) when critical sections are long or when the
number of threads may exceed the number of available cores — spinning wastes CPU that
could be doing useful work or letting the actual lock holder run sooner; use a blocking
mutex instead. Don't use plain TAS in any performance-sensitive contended setting — it is
included here mainly as the illustrative baseline that TTAS improves upon, not as a
recommendation.

## Key takeaways / mental model
The scalability problem with naive spinlocks isn't correctness, it's cache-coherence
traffic: every spinning thread's repeated writes (TAS) or synchronized wake-up storm
(TTAS at release) generates cross-core memory traffic that scales badly. TTAS turns
spin-writes into spin-reads (cheap); backoff spreads out the release-time retry storm;
queue locks (CLH, MCS) eliminate shared-variable spinning altogether by having each
thread wait on its own private memory location, achieving O(1) traffic per operation plus
FIFO fairness — MCS is the gold-standard production design. This is the direct successor
to `multiprocessor-programming/03`'s read/write-only locks: same correctness goals, but
engineered for real multicore hardware's cache behavior.

## Self-check questions
1. Explain precisely why TAS causes more cache-coherence traffic than TTAS while a lock
   is held (not just at release) by a different thread.
2. Walk through what backoff changes about the retry storm at lock release, and identify
   one cost backoff introduces in exchange.
3. Compare CLH and MCS: what specific problem does MCS's explicit-node design solve that
   CLH's implicit-list design has, and why does that matter on NUMA hardware?
4. Given a system with 64 threads under heavy contention and short critical sections,
   which lock from this lesson would you choose and why — walk through the trade-offs you
   weighed.

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 7: "Spin Locks and
  Contention."
