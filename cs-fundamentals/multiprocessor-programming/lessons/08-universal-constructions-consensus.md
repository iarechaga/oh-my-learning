---
id: multiprocessor-programming/08
subject: multiprocessor-programming
title: Universal constructions with consensus primitives
slug: universal-constructions-consensus
status: drafted
mastery:
seniority: staff
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 6
prerequisites: [multiprocessor-programming/07]
created: 2026-08-10
updated: 2026-08-10
---

# Universal constructions with consensus primitives

## TL;DR
A universal construction is a generic recipe that takes *any* sequential object
(described just by its normal, single-threaded method implementations) and mechanically
produces a wait-free concurrent version of it, using a shared **consensus** object as the
core building block — threads agree, one operation at a time, on the single global
sequence of operations to apply, and each thread "helps" apply operations it didn't
itself propose so that no thread is ever left waiting on another.

## The idea
`multiprocessor-programming/06` showed hand-crafted concurrent data structures (lists,
skip lists) built with bespoke locking or CAS logic specific to each structure.
`multiprocessor-programming/07` established that wait-free is the strongest progress
guarantee, but designing a bespoke wait-free algorithm for every data structure you need
is a huge amount of specialized work. Universal constructions ask a more ambitious
question: is there a **single, generic technique** that turns *any* sequential object
(a stack, a queue, a hash table, anything with well-defined single-threaded semantics)
into a correct, wait-free concurrent object automatically, without hand-designing new
algorithmic tricks each time? The answer is yes, and the construction reveals something
deep: the entire problem of making an arbitrary object concurrent reduces to solving one
much narrower problem — **consensus** — repeatedly.

## How it works

### Consensus: the narrow core problem
A **consensus object** solves a deliberately minimal problem: n threads each propose a
value, and the consensus object outputs the **same single value** to all of them (one of
the proposed values — this is the "agreement" and "validity" property), and it does so
via each thread calling a single `decide(value)` method that returns the agreed-upon
value to everyone. Crucially, a *wait-free* consensus object guarantees every thread's
`decide()` call returns in a bounded number of steps, regardless of other threads'
behavior — no thread can be blocked waiting on another. `multiprocessor-programming/09`
goes deep on exactly which hardware primitives can and cannot implement wait-free
consensus for more than 2 threads; this lesson only needs the *existence* of a wait-free
consensus primitive as a building block, treating it as a black box.

### The universal construction: turning consensus into "any object"
The construction (Herlihy's classic universal construction) represents the shared
object's state as an immutable, ever-growing **linked list of applied operations** — each
list node is a "invocation record" plus a pointer to the resulting object state after
applying it. To perform an operation:
1. Thread builds a candidate new list node containing its own operation.
2. Thread reads the current "tail" pointer of the list to find the last-applied node.
3. Thread uses the shared **consensus object at that position in the list** to propose
   *which thread's node* gets to be linked in next — every thread contending for that
   same position proposes its own candidate node, and consensus picks exactly one winner,
   agreed upon by all.
4. Every thread (not just the winner) then applies the winning node's operation to its
   own local copy of the object state, sequentially replaying the list from the
   beginning if needed, and moves on to try to append its own operation at the next
   position if it wasn't the winner this round.

The key insight in step 4 is **helping**: even a thread whose own operation lost the
consensus race at this position doesn't wait idly — it immediately applies the *winning*
thread's operation to its own state (since the winning operation is now official, every
thread needs to know about it anyway) and then retries appending its own pending
operation at the *next* position. Every thread makes real progress on every round —
either its own operation got applied, or someone else's did and it moved forward in the
list — which is exactly what makes the whole construction wait-free: no thread is ever
stuck waiting on another thread's future action, because it can always compute the
current state itself by replaying the agreed-upon list of operations so far.

### Worked example: a universal stack from a sequential stack
Take an ordinary, single-threaded `push`/`pop` stack implementation (no concurrency logic
at all). To make it concurrent via the universal construction: represent the stack's
history as the growing linked list described above, where each node holds either a
`push(x)` or `pop()` invocation. Two threads, A wanting `push(5)` and B wanting `pop()`,
both race to append at the same list position.
1. Both build candidate nodes: A's node holds `push(5)`, B's holds `pop()`.
2. Both read the same current tail.
3. Both call `decide()` on the consensus object guarding this list position, proposing
   their own candidate node. Consensus agrees on exactly one — say A's `push(5)` wins.
4. A's node is now official. Both threads apply `push(5)` to their local replayed copy of
   the stack state. A is done (its operation was applied). B's `pop()` didn't get applied
   this round, so B immediately tries again at the *next* list position — this time
   B's `decide()` call for the next slot may well succeed uncontested, and B's `pop()`
   gets applied, correctly popping the 5 A just pushed (because B replayed the list up to
   and including A's node before proceeding).

The sequential stack implementation itself never had to know anything about threads,
locks, or CAS — the universal construction supplied all the concurrency machinery
generically, on top of an unmodified sequential object.

### Why this matters: reducing "any object" to "just consensus"
The deep result here is a reduction: **if you can build wait-free consensus among n
threads, you can build a wait-free concurrent version of literally any object** with a
well-defined sequential specification. This flips the universal-constructions question
into a much narrower, sharply-defined one: for which n and which hardware primitives
*can* you actually build wait-free consensus? That narrower question is exactly what
`multiprocessor-programming/09`'s consensus hierarchy answers — and the answer (some
primitives, like simple atomic registers, cannot solve consensus for more than 1 thread
in a wait-free way, while CAS can solve it for any number of threads) is what actually
determines whether a universal construction is buildable on a given piece of hardware at
all.

### Practical caveats
Universal constructions are a foundational *existence proof* and design lens more than a
direct engineering recommendation: replaying an ever-growing list of every operation
ever applied (step 4 above) is far slower than a hand-tuned, structure-specific lock-free
algorithm (`multiprocessor-programming/11`'s lock-free stacks/queues are dramatically
more efficient than a universal-construction-derived stack) because real hand-crafted
algorithms exploit structure-specific shortcuts the generic construction cannot know
about. In practice, universal constructions are used when no specialized algorithm is
known for a new object type, as a starting correctness baseline, or as a teaching/proof
tool — not as the default choice when a specialized wait-free or lock-free algorithm
already exists.

## Pros
- Proves, constructively, that wait-free concurrent versions of *any* sequential object
  exist as long as wait-free consensus is available — a foundational existence result
  that structures the entire field's later specialized-algorithm work.
- Cleanly separates two concerns: "how do I make this arbitrary object concurrent"
  (solved generically) versus "what hardware primitives can solve consensus" (a sharply
  defined, separately answerable question, tackled in `multiprocessor-programming/09`).
- The "helping" technique it introduces — a thread applies another's pending operation
  rather than waiting for it — recurs throughout the field's wait-free algorithm designs
  wherever true wait-freedom is required.

## Cons
- Performance is generally poor compared to specialized algorithms: replaying the entire
  operation history (or a growing prefix of it) per operation is far more expensive than
  a hand-tuned CAS loop operating directly on the structure's own internal representation.
- The "immutable, ever-growing list of every operation" representation has real memory
  costs unless combined with a memory-reclamation or snapshotting strategy
  (`multiprocessor-programming/12`) to bound how much history must be retained/replayed.
- It is a generic, one-size-fits-all technique; it cannot exploit structure-specific
  optimizations the way a bespoke lock-free stack or queue implementation
  (`multiprocessor-programming/11`) can.

## Alternatives
- **Hand-crafted lock-free/wait-free algorithms** (`multiprocessor-programming/11`) —
  structure-specific designs that are far more efficient in practice, at the cost of
  needing a new bespoke design (and correctness proof) for every new data structure.
- **Software transactional memory** (`multiprocessor-programming/13`) — another generic
  technique for building concurrent objects from sequential-looking code, using
  transactions with conflict detection and retry rather than consensus-based operation
  replay; generally easier to program against but with its own performance and semantic
  trade-offs.

## When to use it
Reach for the universal-construction *idea* (not necessarily its literal, slow
implementation) when you need a wait-free concurrent version of a brand-new object type
with no known specialized algorithm and no time to design/prove one from scratch — it
gives a correct, if not fast, starting point. It's also the right lens for teaching or
proving that wait-freedom is achievable in principle for an arbitrary object.

## When NOT to use it
Don't use a literal universal construction in a performance-sensitive production system
when a specialized lock-free or wait-free algorithm for your exact data structure already
exists (stacks and queues, `multiprocessor-programming/11`, are the common cases) — the
specialized algorithm will vastly outperform the generic operation-replay approach. Also
don't reach for it if your hardware/language doesn't provide an efficient primitive
capable of implementing wait-free consensus for your thread count in the first place —
check `multiprocessor-programming/09` first.

## Key takeaways / mental model
A universal construction reduces "make any sequential object concurrent" to "solve
consensus repeatedly, one operation at a time," via a shared, ever-growing list of
agreed-upon operations that every thread helps apply (even operations it didn't itself
propose), guaranteeing wait-freedom because no thread ever depends on another thread's
future cooperation to make progress. It is a foundational existence proof and a recurring
design pattern (helping), not typically the fastest real-world implementation choice —
that role goes to hand-crafted algorithms once one exists for your specific structure.

## Self-check questions
1. Explain the role "helping" plays in the universal construction's wait-freedom
   guarantee — what would go wrong (which progress guarantee would be lost) if a losing
   thread simply waited for the winner instead of applying the winner's operation itself?
2. Walk through the worked stack example and explain why B's `pop()` correctly returns 5
   even though A's `push(5)` won the first consensus round, not B's own operation.
3. Why does the universal construction reduce the entire "make X concurrent" problem to
   "solve consensus," and why does that reduction make `multiprocessor-programming/09`'s
   question (which primitives can solve consensus) so important?
4. Why is a literal universal construction rarely used directly in production systems,
   even though it's provably correct and wait-free?

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 6: "Universal
  Constructions."
