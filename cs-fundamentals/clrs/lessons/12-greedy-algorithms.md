---
id: clrs/12
subject: clrs
title: Greedy algorithms and exchange arguments
slug: greedy-algorithms
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapter 16
prerequisites: [clrs/11]
created: 2026-08-10
updated: 2026-08-10
---

# Greedy algorithms and exchange arguments

## TL;DR
A greedy algorithm builds a solution by repeatedly making the locally best choice
available at each step, never reconsidering it — far simpler and faster than dynamic
programming's "consider every subproblem choice," but only correct for problems that
provably satisfy the **greedy-choice property**. An exchange argument is the standard
proof technique for establishing that property: show that any optimal solution can be
transformed, without losing optimality, into one that includes the greedy choice.

## The idea
Dynamic programming (`clrs/11`) considers every possible choice at every subproblem,
because in general the locally best-looking choice might not lead to the globally best
outcome. For a special class of problems, though, a much stronger fact holds: making the
single best available choice right now, and never revisiting that decision, is
*guaranteed* to be part of some optimal overall solution. When this holds, you don't need
to explore alternatives at all — build the solution greedily, one irrevocable choice at a
time, and it's provably optimal. This is enormously cheaper than DP (often O(n log n),
dominated by a single sort, versus DP's typically higher-degree polynomial cost) — but
the entire method rests on first *proving* the greedy-choice property holds for your
specific problem, not just observing that a greedy strategy seems to work on a few
examples.

## How it works

### The two properties a problem must have
1. **Greedy-choice property** — a globally optimal solution can be reached by making a
   locally optimal (greedy) choice first, without needing to reconsider it later, once
   the remaining subproblem is solved optimally.
2. **Optimal substructure** (shared with DP, `clrs/11`) — an optimal solution to the
   problem contains optimal solutions to its subproblems.

Optimal substructure alone is not enough — DP-solvable problems that are *not*
greedy-solvable have optimal substructure but lack the greedy-choice property (the
locally best choice can lead to a strictly worse overall solution). The extra property
greedy needs, and the one that requires proof, is specifically #1.

### Worked example 1: activity selection
Given n activities, each with a start and finish time, select the maximum number of
mutually non-overlapping activities (a classroom-scheduling-style problem). **Greedy
strategy:** always pick the remaining activity with the **earliest finish time** among
those compatible with what's already selected, and never reconsider that pick.

**Why "earliest finish time" and not, say, "shortest duration" or "earliest start
time"?** This is exactly where the exchange argument does its work. Consider any optimal
solution that does *not* start by picking the activity with the globally earliest finish
time, call it a_1; instead it starts with some other compatible activity a_k. Because
a_1 finishes no later than a_k (by choice of a_1 as earliest-finishing), swapping a_k out
for a_1 in that optimal solution cannot break compatibility with anything after
(everything scheduled after a_k in the original solution starts at or after a_k's finish
time, which is >= a_1's finish time, so it remains compatible with a_1 too) — this
produces another solution, of exactly the same size, that *does* include a_1. This is the
exchange argument in full: it shows a_1 can always be swapped in without loss, so *some*
optimal solution includes the greedy choice, which is exactly the greedy-choice property.
Having shown this, the remaining problem (selecting among activities compatible with a_1)
is a smaller instance of the same problem — optimal substructure — so recursing the same
greedy rule on it is justified. Sorting by finish time once, then scanning and greedily
picking compatible activities, gives Theta(n log n) total.

**Why "shortest duration" fails, with a concrete counterexample.** Activities
(1,10), (0,2), (3,5), (6,8) — the shortest-duration greedy picks (3,5) first (duration 2,
tied with (0,2)), potentially blocking a better packing. In fact picking (0,2), (3,5),
(6,8) gives 3 non-overlapping activities, while a shortest-duration-first tiebreak could
plausibly still work here, but perturbing the numbers slightly makes shortest-duration
provably suboptimal in general — the point of working an exchange argument is precisely
that "earliest finish time" is the rule that's *provably* always safe to commit to, while
"shortest duration" has no such proof (and indeed admits counterexamples on other
instances).

### Worked example 2: Huffman coding
Given a set of characters and their frequencies, build a variable-length prefix-free
binary encoding minimizing total encoded length. **Greedy strategy:** repeatedly take the
two *least frequent* remaining nodes (initially, individual characters; later, merged
subtrees), merge them into a new subtree whose frequency is their sum, and repeat until
one tree remains. **Why this is optimal (sketch of the exchange argument):** in any
optimal prefix-free code, the two least-frequent characters must be siblings at the
deepest level of the tree (if they weren't, swapping them with whatever *is* at the
deepest level cannot increase — and can only decrease or maintain — the total encoded
length, since deeper positions cost more bits and should hold less-frequent, not
more-frequent, characters). This licenses treating the two least-frequent nodes as a
merged unit and recursing — again, optimal substructure plus a proven greedy-choice
property. This is implemented efficiently using a min-heap (`clrs/07`): repeatedly
extract-min twice, merge, insert the merged node back — Theta(n log n) total for n
characters.

### The general exchange-argument recipe
1. Propose a greedy rule (the specific "always pick the X-est option" criterion).
2. Assume, for contradiction or by direct construction, an optimal solution that doesn't
   start with the greedy choice.
3. Show that the greedy choice can be **exchanged** into that solution — swapped in for
   whatever it displaces — without making the solution worse (often by showing the
   displaced element could always have gone wherever the greedy choice's slot allows,
   since the greedy choice was picked precisely because it's least constraining or most
   favorable).
4. Conclude some optimal solution includes the greedy choice (the greedy-choice property),
   then argue the remaining problem after committing to that choice is a smaller instance
   of the same problem (optimal substructure), justifying recursion/iteration of the same
   rule.

### Where greedy fails: 0/1 knapsack
Given items with weights and values and a capacity limit, choosing whole items only
(not fractions) to maximize value without exceeding capacity does *not* admit a working
greedy rule — "pick highest value-per-weight ratio first" fails on instances where a
slightly-lower-ratio combination of items fits the remaining capacity better than a
higher-ratio item that, once taken, wastes leftover capacity no other item fits into
exactly. (Contrast this with the **fractional** knapsack problem, where items can be
split — there, the value-per-weight-ratio greedy rule *is* provably correct via an
exchange argument, because fractional flexibility eliminates the "wasted leftover
capacity" failure mode.) 0/1 knapsack requires dynamic programming (`clrs/11`) instead,
precisely because the greedy-choice property fails to hold once items are indivisible.

## Pros
- Where the greedy-choice property provably holds, greedy algorithms are typically far
  simpler to implement and faster to run than the corresponding DP solution (often
  O(n log n), dominated by one sort, vs. DP's higher-degree polynomial time).
- The exchange-argument proof technique, once learned, transfers across a wide range of
  problems (scheduling, encoding, minimum spanning trees `clrs/15`, certain graph
  problems) as the standard way to establish correctness.
- A correctly proven greedy algorithm requires no backtracking, no revisiting of earlier
  decisions, and no large auxiliary table — often O(1) or O(n) extra space beyond the
  input.

## Cons
- The greedy-choice property is not visually obvious and must be *proven*, not assumed —
  a plausible-looking greedy rule that hasn't been proven correct is not a legitimate
  algorithm, just a heuristic that might be silently wrong on some inputs (0/1 knapsack's
  ratio-greedy failure is the classic cautionary example).
- Greedy provides no mechanism for "undoing" an earlier choice if it later turns out
  suboptimal — this is precisely the property that must be proven never to occur before
  trusting the algorithm.
- Different plausible greedy rules for the same problem can give different (and only one,
  or none, provably correct) results — picking the wrong criterion (duration instead of
  finish time, in activity selection) produces a fast but silently incorrect algorithm.

## Alternatives
- **Dynamic programming** (`clrs/11`) — the fallback whenever the greedy-choice property
  cannot be established (or is shown to fail, as in 0/1 knapsack) but optimal
  substructure still holds; always correct where DP applies, at higher time/space cost
  than a working greedy solution.
- **Local search / metaheuristics** (`algorithm-design/11`) — for problems where neither
  greedy nor exact DP is tractable (e.g. large NP-hard instances), accepting an
  approximate rather than exact optimum.
- **Linear/integer programming relaxations** — for combinatorial optimization problems
  where a greedy rule can't be proven, formulating and solving (or approximating) an
  LP/ILP is a more general, if computationally heavier, alternative.

## When to use it
Use a greedy algorithm only after identifying a specific selection rule *and* proving
(typically via an exchange argument) that it satisfies the greedy-choice property for
your exact problem — activity/interval scheduling, Huffman coding, and minimum spanning
tree construction (`clrs/15`) are classic, well-established examples.

## When NOT to use it
Don't apply a greedy rule to a problem without proof, based only on it "seeming to work"
on a handful of examples — verify with an exchange argument or find a counterexample
first. Don't use greedy for problems structurally similar to 0/1 knapsack (indivisible
choices with a shared, limited resource) unless you've specifically confirmed the
greedy-choice property survives the indivisibility constraint.

## Key takeaways / mental model
Greedy is DP with an extra, provable guarantee: the locally best choice is always part of
some optimal solution, so you never need to keep other options open. The exchange
argument is the proof pattern: show any optimal solution can be rearranged, without loss,
to include the greedy choice. When you can't construct that argument (or can construct a
counterexample instead), the problem needs DP, not greedy.

## Self-check questions
1. Walk through the exchange argument for activity selection: why does swapping in the
   earliest-finishing compatible activity never break compatibility with the rest of an
   assumed-optimal solution?
2. Construct a small counterexample showing that "always pick the shortest-duration
   remaining activity" is not a valid greedy rule for activity selection.
3. Explain, using the exchange-argument sketch for Huffman coding, why the two
   least-frequent nodes must be at the deepest level of an optimal prefix-free code tree.
4. Why does the greedy value-per-weight-ratio rule work for fractional knapsack but fail
   for 0/1 knapsack? What specific step of the exchange argument breaks when items become
   indivisible?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 16: "Greedy
  Algorithms."
