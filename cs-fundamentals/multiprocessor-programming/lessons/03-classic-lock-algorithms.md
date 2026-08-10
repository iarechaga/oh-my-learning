---
id: multiprocessor-programming/03
subject: multiprocessor-programming
title: Classic lock algorithms (Peterson, bakery, tournament)
slug: classic-lock-algorithms
status: drafted
mastery:
seniority: senior
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 2
prerequisites: [multiprocessor-programming/02]
created: 2026-08-10
updated: 2026-08-10
---

# Classic lock algorithms (Peterson, bakery, tournament)

## TL;DR
Peterson's algorithm gives starvation-free mutual exclusion for exactly 2 threads using
only atomic reads/writes (no special hardware); the bakery algorithm generalizes this to
n threads with FIFO fairness by having threads "take a ticket"; the tournament algorithm
composes Peterson locks in a binary tree to get n-thread mutual exclusion with O(log n)
time instead of the bakery's O(n). Together they show that mutual exclusion is achievable
from nothing but plain reads and writes — no compare-and-swap needed — at the cost of
scalability.

## The idea
`multiprocessor-programming/02` defined what a correct lock must guarantee. This lesson
asks the constructive question: can you actually *build* one using only the atomic-
read/atomic-write baseline from `multiprocessor-programming/01` — no fancy hardware
instructions, just ordinary variables? The surprising answer is yes, and the three
algorithms here (Peterson, bakery, tournament) are the historical proof, each solving a
harder version of the problem than the last: first 2 threads, then n threads, then n
threads *efficiently*. They matter today less as production code (real systems use
hardware primitives like CAS, covered in `multiprocessor-programming/10`, which are
faster and simpler) and more because they build the proof technique and intuition you
need for every lock algorithm that follows, and because they demonstrate a deep result:
mutual exclusion needs no special hardware at all, only plain shared memory.

## How it works

### Peterson's algorithm (2 threads)
Two threads, A and B (indices 0 and 1). Shared state: `flag[2]` (boolean array,
initially false) and `turn` (an integer). Thread `i`'s code (`j` is the other thread):

```
flag[i] = true
turn = j
while (flag[j] && turn == j) { /* spin */ }
... critical section ...
flag[i] = false
```

**Intuition.** `flag[i] = true` announces "I want in." `turn = j` politely yields
priority to the other thread *if* both want in simultaneously. The spin condition
`flag[j] && turn == j` means "wait only if the other thread also wants in AND it was the
last one to yield priority" — if the other thread doesn't want in (`flag[j]` false), or if
*I* was the last one to set `turn` (meaning the other thread set `turn` to *me* more
recently, i.e., they yielded to me), I proceed immediately.

**Worked example — why it satisfies mutual exclusion.** Suppose both threads race to
enter at once. Both set their own flag true and then write to `turn` (whichever writes
last "wins" — say A writes `turn = B` last, i.e., after B already wrote `turn = A`). Now
`turn == B`. Thread A's spin condition is `flag[B] && turn == B` — both true, so A waits.
Thread B's spin condition is `flag[A] && turn == A` — `turn` is B, not A, so this is
false, and B proceeds. Exactly one thread (B) enters. If instead only one thread wants in
at all, the other's `flag` is false, so the spin condition is false immediately and the
requesting thread proceeds unimpeded — no unnecessary waiting when there's no contention.

Peterson's algorithm satisfies all three properties from `multiprocessor-programming/02`:
mutual exclusion (proof sketch above generalizes to a full contradiction proof),
deadlock-freedom, and even the stronger starvation-freedom (a thread can be passed over
at most once before `turn` flips back in its favor). Its fatal limitation: **it only
works for exactly 2 threads** — the `turn`/`flag` trick doesn't generalize directly to n
threads without a different construction.

### The bakery algorithm (n threads, FIFO fairness)
Named after the "take a numbered ticket" system at a bakery counter. Shared state:
`choosing[n]` (booleans) and `number[n]` (integers, one ticket number per thread). Thread
`i`'s code:

```
choosing[i] = true
number[i] = 1 + max(number[0], ..., number[n-1])
choosing[i] = false
for each other thread j:
    while (choosing[j]) { /* wait for j to finish choosing */ }
    while (number[j] != 0 && (number[j], j) < (number[i], i)) { /* spin */ }
... critical section ...
number[i] = 0
```

**Intuition.** Each thread computes a ticket number one higher than the current maximum
(mimicking a bakery's numbered-ticket dispenser, except there's no atomic dispenser here
— multiple threads can compute the *same* number simultaneously, which is why ties are
broken by thread ID via the pair comparison `(number[j], j) < (number[i], i)`). A thread
enters only once it has confirmed no other thread with a smaller (number, id) pair is
still waiting. The `choosing[i]` flag handles the race where thread i is *in the middle
of* computing its number when j reads it — j must wait for i to finish choosing before
trusting `number[i]`, otherwise j might read a stale/incomplete number and let two
threads with conflicting tickets both proceed.

**Why FIFO fairness.** Because entry order is strictly determined by (ticket number,
thread ID), and ticket numbers are handed out in the order threads arrive (each new
ticket is bigger than every ticket already handed out at the moment of computing it, since
`choosing[j]` is checked), the bakery algorithm gives **first-come-first-served ordering**
— strictly stronger than mere starvation-freedom, it's the bounded-waiting property
mentioned in `multiprocessor-programming/02`. This is bakery's headline advantage over
Peterson-style locks: not just "everyone eventually gets in" but "in the order they
asked."

**Bakery's cost.** Entering the critical section requires reading `number[j]` and
`choosing[j]` for *every other thread* — O(n) work per lock acquisition regardless of
contention. Ticket numbers also grow unboundedly over the lock's lifetime unless
periodically reset, which real implementations must handle carefully (using bounded
integers requires wraparound-safe comparison logic).

### The tournament algorithm (n threads, O(log n))
Bakery's O(n) per-acquisition cost doesn't scale. The tournament algorithm fixes this by
arranging `n` threads as leaves of a binary tree of Peterson locks (assume n is a power of
2 for simplicity). Each internal tree node is an independent 2-thread Peterson lock.

**Mechanism.** To enter the critical section, thread `i` first "wins" the Peterson lock
at its leaf-level pairing against its sibling leaf, then the *winner* of that match
competes at the next level up against the winner of the sibling subtree's match, and so
on up to the root — exactly like a single-elimination sports tournament bracket. Only the
overall root-level winner enters the critical section; all others are blocked spinning at
whichever level they lost. On exit, the thread releases the locks it acquired going *up*
the tree, in reverse order.

**Worked example with 4 threads (A, B, C, D).** Leaf round: A vs. B on one Peterson lock,
C vs. D on another — say A and D win their leaf matches. Root round: A vs. D on the root
Peterson lock — say A wins. A enters the critical section. B is blocked spinning at the
leaf level (lost immediately to A); C is blocked spinning at the leaf level (lost to D);
D is blocked spinning at the root level (lost to A after already winning its own leaf).
Depth of the tree is `log2(n)`, so a thread does at most `log2(n)` Peterson-lock
acquisitions to enter — versus bakery's O(n) — a direct scalability win.

**Trade-off versus bakery.** Tournament trades away bakery's strict FIFO ordering (the
tournament bracket structure doesn't guarantee first-come-first-served — a thread that
arrives later but wins its local matches quickly can still overtake an earlier arrival
stuck losing repeatedly) in exchange for O(log n) acquisition cost instead of O(n). It
still inherits starvation-freedom from the underlying Peterson locks (a losing thread
can't be passed over forever, because the `turn` mechanism inside each Peterson node
eventually favors it) but loses the precise arrival-order guarantee.

## Pros
- All three are constructed from nothing but atomic reads/writes — no special hardware
  instruction required, proving mutual exclusion is achievable at the most primitive
  level.
- Peterson's algorithm is small enough to fully hand-prove correct — an excellent vehicle
  for learning the proof technique used throughout this subject.
- Bakery gives strong FIFO fairness; tournament gives much better scalability while still
  guaranteed starvation-free.

## Cons
- None of these scale well to many-core hardware in practice: bakery is O(n) per
  acquisition; tournament's O(log n) is better but each level is still a full Peterson
  lock with its own memory traffic, and every level touches shared state, causing
  cache-coherence traffic that hardware-primitive-based locks (`multiprocessor-programming/04`)
  avoid more cleverly.
- Peterson's algorithm fundamentally caps out at 2 threads; it must be composed (as in
  tournament) or replaced (as in bakery) to handle more.
- Bakery's unbounded ticket numbers are an implementation headache in real (fixed-width
  integer) systems — need explicit wraparound handling.

## Alternatives
- **Hardware-primitive locks (TAS, TTAS, CLH, MCS)** — `multiprocessor-programming/04`
  covers locks built on compare-and-swap or similar atomic hardware instructions, which
  dominate these classic algorithms in real-world performance and are what production
  systems actually use.
- **Lock-free algorithms** (`multiprocessor-programming/07`, `multiprocessor-programming/11`)
  — avoid locking (and its associated blocking/priority-inversion risk) entirely, a
  fundamentally different strategy from all three algorithms here.

## When to use it
Study Peterson's algorithm to internalize the mutual-exclusion proof technique — it is
the cleanest, smallest example to hand-trace. Reach for the bakery algorithm's *idea*
(not necessarily its literal implementation) whenever you need provable FIFO fairness
without hardware atomics available. Use the tournament construction's *idea* — composing
small, well-understood locks into a scalable tree — as a general pattern applicable
beyond locking (e.g., tournament-style reduction/aggregation trees appear elsewhere in
concurrent algorithm design).

## When NOT to use it
Do not deploy Peterson, bakery, or tournament locks as literal production code on modern
hardware — hardware CAS-based locks (`multiprocessor-programming/04`) are simpler to
implement correctly, faster in practice, and don't require reasoning about n-thread
generalizations built from primitive read/write-only constructions. These classic
algorithms' value today is pedagogical and historical, not a recommended implementation
choice.

## Key takeaways / mental model
Peterson solves 2-thread starvation-free mutual exclusion via `flag`+`turn` yielding.
Bakery generalizes to n threads with strict FIFO ordering via a numbered-ticket scheme,
at O(n) cost per acquisition. Tournament composes Peterson locks into a binary bracket to
get O(log n) acquisition cost, sacrificing bakery's strict FIFO ordering. All three prove
that shared-memory mutual exclusion needs no special hardware — only atomic reads and
writes — which is a foundational result even though production locks use hardware
primitives instead (`multiprocessor-programming/04`).

## Self-check questions
1. Walk through Peterson's algorithm's mutual-exclusion proof: if both threads are
   simultaneously inside their critical sections, derive the contradiction.
2. Why does the bakery algorithm need the separate `choosing[i]` flag in addition to
   `number[i]` — what specific race does it prevent?
3. Compare bakery and tournament on acquisition cost and on fairness guarantee — which
   would you pick for a system with 64 threads and why?
4. Why can't Peterson's `flag`/`turn` trick be directly generalized to n threads without
   either a different algorithm (bakery) or composing multiple Peterson locks
   (tournament)?

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 2: "Mutual
  Exclusion."
