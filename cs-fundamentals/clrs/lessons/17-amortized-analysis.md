---
id: clrs/17
subject: clrs
title: Amortized analysis techniques
slug: amortized-analysis
status: drafted
mastery:
seniority: senior
source: Introduction to Algorithms (CLRS), Chapter 17
prerequisites: [clrs/01]
created: 2026-08-10
updated: 2026-08-10
---

# Amortized analysis techniques

## TL;DR
Amortized analysis bounds the *average* cost per operation over a worst-case **sequence**
of operations on a data structure, even when individual operations occasionally cost much
more than that average — as long as expensive operations are provably rare enough that
they can't happen too often in a row. This is different from average-case (probabilistic)
analysis: amortized bounds require no assumption about randomness or input distribution
at all, only about the *sequence* of operations performed.

## The idea
Some data structures have operations whose worst-case single-call cost looks bad (e.g.
O(n)) but which, examined over any long sequence of calls, average out to something much
better (e.g. O(1) per call). A per-call worst-case analysis would report the pessimistic
O(n) bound and miss this entirely; a probabilistic average-case analysis would require an
assumption about input randomness that doesn't apply here (there's nothing random about a
dynamic array's resize pattern — it's entirely deterministic, and the amortized bound
holds for *every* possible sequence of operations, not just "most" of them). Amortized
analysis is the third tool that correctly captures this specific situation: a
deterministic, worst-case-over-sequences bound that's tighter than "just take the max
single-operation cost."

## How it works

### The three techniques
1. **Aggregate analysis** — directly sum the total cost of a worst-case sequence of n
   operations, then divide by n to get the amortized cost per operation.
2. **The accounting method** — assign each operation an amortized "charge" (possibly
   different from its actual cost); cheap operations are overcharged, banking credit;
   expensive operations draw down that banked credit to cover their actual cost. The
   bound is valid as long as the total banked credit never goes negative.
3. **The potential method** — define a potential function Phi over the data structure's
   state (intuitively, "stored-up credit" as a function of the structure's current
   configuration, not tied to specific past operations); an operation's amortized cost is
   its actual cost plus the *change* in potential it causes. The potential method is the
   most general and rigorous of the three, and the one CLRS ultimately favors for
   non-trivial cases.

### Worked example 1: the dynamic (growable) array, via aggregate analysis
A dynamic array starts empty and doubles its capacity (allocating a new array and copying
every existing element) whenever a PUSH would exceed current capacity. Most pushes are
O(1) (just write to the next free slot); a doubling push is O(current size), since every
existing element must be copied.

**Aggregate analysis over n pushes.** Doublings happen at sizes 1, 2, 4, 8, ..., up to
the largest power of 2 <= n — a geometric sequence. The total cost of all doubling copies
is 1 + 2 + 4 + ... + n/2 < n (a geometric series sums to less than twice its largest
term). Adding the n individual O(1) push costs (Theta(n) total), the **total cost of n
pushes is O(n) + O(n) = O(n)**. Dividing by n operations gives an **amortized cost of
O(1) per push** — even though some individual pushes cost O(n), the geometric spacing of
doublings means their total cost across the whole sequence is bounded by a constant
multiple of n, not by n times the number of doublings.

**Why doubling (not, say, adding a fixed increment) is essential to this result.** If
instead the array grew by a *fixed* increment k each time it filled up (rather than
doubling), there would be Theta(n/k) resizes, each costing O(n) in the worst case (a
resize near the end copies almost all n elements) — total cost Theta(n^2/k), giving
amortized cost Theta(n/k) per push, not O(1). **Geometric (multiplicative) growth is what
makes the resize costs form a convergent geometric series; linear (additive) growth does
not** — this is a genuinely important, easy-to-miss implementation detail behind why
every real dynamic-array implementation (Python lists, Java ArrayList, C++ vector) grows
by a multiplicative factor, not a fixed increment.

### Worked example 2: a binary counter, via the accounting/potential method
Incrementing a binary counter (flip bits from the rightmost 0 rightward, turning trailing
1s into 0s and that first 0 into a 1) costs, in the worst case, O(k) for a k-bit counter
(a counter transitioning like 0111 -> 1000 flips all 4 bits). Naive worst-case-per-
operation analysis over n increments would suggest O(nk) total. Accounting-method
argument: charge 2 units per increment — 1 unit pays for setting the new bit to 1, and 1
unit is "banked" on that bit as credit for the eventual cost of flipping it back to 0
later. Every bit-flip-to-0 is paid for out of the credit banked on that specific bit when
it was last set to 1 — credit never goes negative, since every bit that gets flipped to 0
was necessarily set to 1 (and charged its banked unit) at some earlier point. Total cost
over n increments: at most 2n (2 units charged per increment) — **amortized O(1) per
increment**, not O(k), despite individual increments occasionally costing the full O(k).

### Aggregate vs. accounting vs. potential: when to reach for which
**Aggregate analysis** is the simplest and most direct when you can compute the total
cost of a sequence outright (as in the dynamic array example) — but it only gives you the
*average*, not a per-operation-type breakdown, which matters if different operation types
have genuinely different costs. **The accounting method** lets you assign different
amortized charges to different operation types (useful when a data structure supports
several distinct operations with different actual costs) and is often more intuitive to
reason about informally. **The potential method** is the most rigorous and general —
it handles cases (especially structures with complex, interacting operations) where
constructing a clean, per-item "banked credit" accounting story is awkward, by instead
defining one global potential function over the entire structure's state and mechanically
deriving each operation's amortized cost from how much it changes that potential.

## Pros
- Gives a *deterministic*, worst-case-over-sequences guarantee — unlike average-case
  probabilistic analysis, it requires no assumption about input randomness, and holds for
  literally every possible sequence of operations, adversarial or not.
- Frequently reveals that a data structure with an occasionally-expensive-looking
  operation is, in fact, just as efficient overall (amortized O(1)) as one with a
  uniformly cheap operation — directly justifying real, widely-used designs (dynamic
  arrays, splay trees, the union-find structure in `clrs/18`).
- The potential-method machinery generalizes cleanly to complex structures where a direct
  aggregate sum would be difficult to compute by hand.

## Cons
- Amortized bounds say nothing about any *individual* operation's latency — a single
  doubling push in a dynamic array is still genuinely O(n) at that moment, which matters
  for real-time or latency-sensitive systems even if the long-run average is fine (this
  is precisely why some systems pre-allocate or avoid dynamic resizing in latency-critical
  code paths).
- Choosing a good potential function (for the potential method) is a creative,
  problem-specific step with no fully mechanical recipe — a poorly chosen potential
  function can make the analysis needlessly hard or fail to produce a tight bound.
- Amortized analysis applies to a specific data structure's *own* internal operation
  sequence — it does not, by itself, say anything about probabilistic average-case
  behavior under random inputs (a different, complementary question, `clrs/04`).

## Alternatives
- **Worst-case per-operation analysis** (`clrs/01`) — simpler and gives a hard guarantee
  for every single operation, appropriate when individual-operation latency (not just
  long-run average) genuinely matters, at the cost of reporting a pessimistic bound for
  structures like dynamic arrays where it doesn't reflect typical behavior.
- **Probabilistic/average-case analysis** (`clrs/04`) — answers a different question
  (expected cost under an assumed input distribution or the algorithm's own randomness),
  complementary to, not a substitute for, amortized analysis.
- **Redesigning for worst-case-per-operation guarantees** — e.g. incremental/lazy
  rehashing schemes that spread a hash table's resize cost across many subsequent
  operations instead of paying it all at once, trading amortized simplicity for a
  genuinely bounded worst-case-per-operation guarantee.

## When to use it
Use amortized analysis whenever a data structure has operations with genuinely variable
cost across a sequence (dynamic arrays, splay trees, union-find with path compression)
and you want to characterize the structure's *overall* efficiency across realistic usage,
not just the worst single call.

## When NOT to use it
Don't rely on an amortized bound as a guarantee for latency-sensitive systems where any
individual operation's worst-case cost matters (e.g. a hard real-time system where a
single O(n) resize pause is unacceptable regardless of how rare it is) — there, a
worst-case-per-operation-guaranteed design (or pre-allocation to avoid the expensive
operation entirely) is the appropriate tool instead.

## Key takeaways / mental model
Amortized analysis answers "what's the true average cost per operation across a
worst-case sequence?" — a deterministic, sequence-based bound, not a probabilistic one.
Geometric (not linear) growth is what makes dynamic-array resizing amortized O(1); the
potential method's "stored credit as a function of structure state" is the general tool
for proving such bounds rigorously when a direct sum is awkward.

## Self-check questions
1. Explain, using the geometric series argument, why doubling a dynamic array's capacity
   gives amortized O(1) push, while growing by a fixed increment does not.
2. Using the accounting method's "charge 2, bank 1" argument for the binary counter,
   explain precisely why the banked credit can never go negative across any sequence of
   increments.
3. Give a concrete scenario (e.g. a real-time system) where an amortized O(1) guarantee
   is insufficient and a worst-case-per-operation O(1) guarantee is actually required —
   what design change would you make to the dynamic array to get that stronger guarantee?
4. Why is amortized analysis a fundamentally different question from probabilistic
   average-case analysis (`clrs/04`), even though both produce an "average" cost figure?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 17: "Amortized
  Analysis."
