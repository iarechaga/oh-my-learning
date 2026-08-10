---
id: multiprocessor-programming/09
subject: multiprocessor-programming
title: Consensus hierarchy and synchronization power
slug: consensus-hierarchy
status: drafted
mastery:
seniority: staff
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 5
prerequisites: [multiprocessor-programming/08]
created: 2026-08-10
updated: 2026-08-10
---

# Consensus hierarchy and synchronization power

## TL;DR
Herlihy's consensus hierarchy ranks shared-memory primitives by **consensus number**: the
maximum number of threads for which the primitive can solve wait-free consensus.
Read/write registers sit at level 1 (cannot solve consensus for even 2 threads without
help); test-and-set, swap, and fetch-and-add sit at level 2; compare-and-swap sits at
infinity (solves consensus for any number of threads) — a strict, provable ranking of
"synchronization power" that explains precisely why CAS became the primitive real
hardware and languages standardized on.

## The idea
`multiprocessor-programming/08`'s universal construction reduced "make any object
concurrent" to "solve consensus repeatedly." That reduction only matters if you can
actually answer: **which primitives can solve wait-free consensus, for how many
threads?** This isn't an implementation detail — it's a deep, provable structural fact
about a primitive's raw computational power, independent of any particular algorithm
built on top of it. Herlihy's landmark 1991 result organizes every common synchronization
primitive into a strict hierarchy by exactly this question, and the answer explains a
real historical/engineering fact: why register-based primitives (plain reads/writes) are
fundamentally insufficient for general concurrent programming no matter how cleverly
combined, while CAS is uniquely powerful enough to solve the general case.

## How it works

### The consensus number, defined precisely
A primitive (or object type) has **consensus number n** if:
1. It can be used to solve wait-free consensus among **n** threads (there exists an
   algorithm using any number of instances of this primitive, plus ordinary read/write
   registers, that lets n threads agree on a single value, wait-free).
2. It **cannot** solve wait-free consensus among **n+1** threads — no algorithm, however
   clever, using any number of instances of this primitive can achieve wait-free
   consensus for n+1 threads.

This isn't "how hard is it to write an algorithm" — it is an absolute, information-
theoretic ceiling proven via rigorous adversary arguments (Herlihy's original proofs use
a technique showing that for n+1 threads, an adversarial scheduler can always find a
"bivalent" execution state — one that could still go either way — that the primitive
cannot resolve without more information than it's capable of encoding).

### Level 1: read/write registers
Plain atomic read/write memory (the baseline primitive from
`multiprocessor-programming/01`) has **consensus number 1** — it cannot solve wait-free
consensus for even 2 threads, no matter how many registers or how cleverly they're
combined. This is a genuinely surprising, deep result: all of
`multiprocessor-programming/03`'s classic locks (Peterson, bakery, tournament) are built
purely from read/write registers, and they achieve *mutual exclusion*, but mutual
exclusion is a fundamentally *weaker* problem than consensus — a lock only needs to
ensure threads don't overlap in a critical section; it doesn't need to make them agree on
a shared decided *value*. This is precisely why those classic algorithms, however
cleverly constructed, could never be extended into a wait-free consensus protocol no
matter how much cleverness is applied — the primitive itself has a hard ceiling.

### Level 2: test-and-set, swap, fetch-and-add, queue (enqueue/dequeue)
A cluster of primitives — **test-and-set**, **swap** (atomically exchange a register's
value), **fetch-and-add**, and even a FIFO **queue**'s enqueue/dequeue pair — all have
**consensus number 2**: each can solve wait-free consensus for exactly 2 threads (via
short, elegant algorithms — e.g. for test-and-set, the thread that "wins" the test-and-
set race decides its own proposed value, and the loser adopts the winner's value), but
none of them can solve consensus for 3 or more threads, however combined.

**Worked example: test-and-set solves 2-thread consensus.** Shared `flag` (initially
"unset") and two registers holding each thread's proposal. Thread i: write proposal to
`proposal[i]`; call `test-and-set(flag)`; if it returns "unset" (i.e. I was first), decide
my own proposal; if it returns "set" (someone beat me to it), read the *other* thread's
proposal register and decide that value instead. Exactly one thread wins the race
(test-and-set is atomic), so both threads always agree on the winner's proposed value —
consensus solved, wait-free, for 2 threads. No analogous trick exists for 3 threads with
only test-and-set — this is provable, not just "nobody's found one yet."

### Level infinity: compare-and-swap (and friends)
**Compare-and-swap (CAS)** — atomically compare a memory location's current value to an
expected value, and if they match, swap in a new value (returning whether the swap
succeeded) — has **consensus number infinity**: it solves wait-free consensus for *any*
number of threads n, no matter how large.

**Why CAS is unboundedly powerful.** The consensus algorithm is short: a single shared
register initialized to a sentinel "undecided" value. Every thread calls
`CAS(register, undecided, my_proposal)`. Exactly one thread's CAS succeeds (whichever
executes first — CAS is atomic, so only one comparison-against-"undecided" can ever
succeed); every thread, winner or loser, then simply reads the register's final value and
decides that — the winner reads back its own successfully-written proposal, and every
loser reads back the same value the winner wrote. This works identically regardless of
whether there are 2 threads or 2 million: CAS's atomic compare-then-swap encodes enough
information (specifically, "did *my* proposed old-value match what's actually there right
now") to resolve arbitrary-way contention in a single atomic step, which no level-2
primitive can do beyond 2 contenders.

Other primitives that also reach consensus number infinity include **load-linked/store-
conditional (LL/SC)** (a slightly different atomic primitive some architectures provide
instead of CAS, with essentially equivalent power) and, by the universal-construction
reduction (`multiprocessor-programming/08`), anything built *from* an infinite-consensus-
number primitive.

### Why this hierarchy matters practically
This is not an abstract curiosity — it directly explains a real hardware/language design
decision: **every mainstream CPU architecture provides CAS (or LL/SC) as a first-class
atomic instruction**, specifically because it is the minimal primitive powerful enough to
implement wait-free/lock-free algorithms for arbitrary numbers of threads. If hardware
had shipped only test-and-set (consensus number 2), lock-free data structures beyond
2-thread scenarios would be *provably impossible* to build directly from it — no amount
of clever algorithm design could compensate for the primitive's fundamental power ceiling.
This is why `multiprocessor-programming/10` (atomic primitives and ABA hazards) and
`multiprocessor-programming/11` (lock-free stacks/queues) are both built on CAS
specifically, not on test-and-set or fetch-and-add.

### A summary table
| Primitive | Consensus number | Can solve consensus for |
| --- | --- | --- |
| Atomic read/write register | 1 | 1 thread only (trivial — no contention) |
| Test-and-set, swap, fetch-and-add, FIFO queue | 2 | up to 2 threads |
| Compare-and-swap, LL/SC | infinity | any number of threads |

## Pros
- Gives an absolute, provable answer to "is this primitive powerful enough for my
  algorithm?" — not a matter of trying harder or being cleverer; below a primitive's
  consensus number, no algorithm exists, period.
- Directly explains real hardware design choices (why CAS/LL/SC are the primitives that
  matter for general lock-free programming) rather than leaving it as an unexplained
  historical accident.
- Composable with the universal construction (`multiprocessor-programming/08`): once you
  know a primitive has infinite consensus number, you immediately know it can build a
  wait-free version of *any* object, for *any* number of threads.

## Cons
- The hierarchy answers a specific theoretical question (wait-free consensus power); it
  says nothing directly about the *performance* of algorithms built on a given primitive
  — CAS being maximally powerful doesn't mean every CAS-based algorithm is fast (see
  `multiprocessor-programming/04`'s contention discussion, which is a performance concern
  orthogonal to this power hierarchy).
- Reasoning about consensus-number proofs (the adversary/bivalence arguments) is
  genuinely advanced material — most engineers use the *conclusion* (CAS is universally
  powerful) without needing to reproduce the proofs themselves.
- The hierarchy is specific to the wait-free consensus problem; other useful complexity
  measures for primitives (e.g. how efficiently a primitive supports a specific data
  structure) aren't captured by consensus number alone.

## Alternatives
- **Randomized consensus algorithms** — some randomized protocols can solve consensus
  probabilistically using only weaker (level-1 or level-2) primitives, sidestepping the
  deterministic hierarchy's hard ceiling at the cost of only probabilistic (not absolute)
  guarantees — a different trade-off than this lesson's deterministic hierarchy.
- **Message-passing consensus (distributed systems)** — a related but distinct problem
  (e.g. Paxos, Raft) solving agreement across machines with no shared memory at all,
  facing different impossibility results (like FLP) rather than this shared-memory
  hierarchy.

## When to use it
Use the consensus hierarchy as a design-time sanity check whenever you're evaluating
whether a given hardware/language primitive is even *theoretically* sufficient to build
the wait-free or lock-free algorithm you have in mind for an arbitrary number of threads
— if your only available primitive tops out at consensus number 2, stop and either narrow
your thread-count assumption or find a stronger primitive (CAS) before investing further
design effort.

## When NOT to use it
Don't invoke consensus-number reasoning for problems that don't actually require solving
general n-thread consensus — many practical concurrent algorithms (e.g. simple counters
via fetch-and-add, or 2-thread-only protocols) work perfectly well with weaker, level-2
primitives, and reaching for CAS "because it's more powerful" when a simpler, cheaper
primitive already suffices is unnecessary complexity for no benefit.

## Key takeaways / mental model
A primitive's consensus number is an absolute, provable ceiling on how many threads it
can help reach wait-free agreement — not an implementation detail but a fact about the
primitive's raw synchronization power. Registers top out at 1, test-and-set/swap/fetch-
and-add/queues top out at 2, and CAS (or LL/SC) is unboundedly powerful, solving
consensus for any n. This hierarchy is *why* CAS is the primitive real hardware
standardized on for building general-purpose lock-free/wait-free algorithms, and it's the
missing piece that makes `multiprocessor-programming/08`'s universal construction
concrete: "solve consensus" is only actually achievable at scale with a level-infinity
primitive like CAS.

## Self-check questions
1. Define consensus number precisely, and explain why it is a strict ceiling (not just
   "the best algorithm anyone's found so far").
2. Walk through why test-and-set can solve 2-thread consensus but (provably) cannot solve
   3-thread consensus — what breaks about the "winner decides, loser adopts" trick with a
   third contender?
3. Why do all of `multiprocessor-programming/03`'s classic lock algorithms, despite being
   built entirely from read/write registers, not contradict the claim that registers have
   consensus number 1?
4. Explain, using the consensus hierarchy, why real CPU architectures provide CAS or
   LL/SC as first-class instructions rather than relying solely on test-and-set or
   fetch-and-add.

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 5: "The Relative
  Power of Primitive Synchronization Operations."
