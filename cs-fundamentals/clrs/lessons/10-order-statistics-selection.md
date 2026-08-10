---
id: clrs/10
subject: clrs
title: Order statistics and selection in linear time
slug: order-statistics-selection
status: drafted
mastery:
seniority: senior
source: Introduction to Algorithms (CLRS), Chapter 9
prerequisites: [clrs/02, clrs/08]
created: 2026-08-10
updated: 2026-08-10
---

# Order statistics and selection in linear time

## TL;DR
Finding the k-th smallest element of an unsorted array (an "order statistic") doesn't
require sorting the whole array first — it can be done in expected Theta(n) time using
quickselect (a quicksort-style partition that only recurses into the side containing the
answer), and even in worst-case Theta(n) using the more elaborate median-of-medians
algorithm to guarantee a good pivot every time.

## The idea
Sorting the entire array to find, say, the median (Theta(n log n)) does far more work
than necessary — you only need one specific position's value, not the full order of every
element. Order-statistic selection asks: can you find the k-th smallest element without
fully sorting? The answer is yes, and the technique reuses quicksort's partitioning
scheme (`clrs/08`) with a crucial simplification: since you only care about *one* side of
each partition (whichever side contains position k), you only need to recurse into that
one side, not both — this halves (or better) the work compared to quicksort at every
level.

## How it works

### Quickselect: the natural first algorithm
Given array A and target rank k (1-indexed, k=1 is the minimum), partition A around a
pivot exactly as quicksort does, obtaining a pivot index p (0-indexed) such that
everything before p is <= the pivot and everything after is > it. Compare p+1 (the
pivot's 1-indexed rank) to k:
- If p+1 == k, the pivot itself is the answer — done.
- If k < p+1, the k-th smallest is in the left partition — recurse only into A[0..p-1]
  with the same k.
- If k > p+1, the k-th smallest is in the right partition — recurse only into
  A[p+1..end] with adjusted target k' = k - (p+1).

**Why this is faster than quicksort in expectation, not just by a constant factor.**
Quicksort recurses into *both* sides after every partition, giving the familiar
T(n) = T(size of left) + T(size of right) + Theta(n) recurrence. Quickselect recurses
into only *one* side, giving T(n) = T(size of the relevant side) + Theta(n). With a
random pivot (expected constant-fraction split), this recurrence solves via the
recursion-tree method to Theta(n): work at the top level is Theta(n), the next level is a
constant fraction of that (say Theta(n/2) in the balanced case), the level after that a
constant fraction again, and so on — a geometric series that sums to Theta(n) total,
not Theta(n log n), because there is only ever *one* branch being pursued, not two
branches whose combined width stays n at every level (as in quicksort's recursion tree).

### The worst case, and why randomization matters here too
Exactly as in quicksort, an adversarial or unlucky pivot choice (always picking the
smallest or largest remaining element) makes quickselect degrade: T(n) = T(n-1) + Theta(n)
solves to Theta(n^2). Randomized pivot selection (`clrs/04`) makes this expected-case-only
degenerate behavior vanishingly unlikely for any given input, giving expected Theta(n)
regardless of input — the same argument as randomized quicksort, applied here.

### Median-of-medians: a worst-case-guaranteed Theta(n) algorithm
For applications that cannot tolerate even a low-probability Theta(n^2) worst case
(unlike sorting, where introsort's fallback to heapsort handles this — see `clrs/08`),
CLRS presents a deterministic pivot-selection scheme, **median-of-medians**, that
guarantees a good-enough split every single time:
1. Divide the n elements into groups of 5.
2. Find the median of each group (a fixed, tiny amount of work per group — sorting 5
   elements is O(1)).
3. Recursively find the median **of those group medians** — this recursive call is the
   clever part, using the *same* selection algorithm on a much smaller array (n/5
   elements).
4. Use that median-of-medians as the pivot for partitioning the original array.

**Why this guarantees a good split.** The median-of-medians is provably guaranteed to be
greater than at least 3/10 of the elements and less than at least 3/10 of the elements
(a somewhat involved but mechanical counting argument over the groups-of-5 structure),
so partitioning around it always produces a split no worse than roughly 30/70 — good
enough for the Master method (or recursion-tree summation) to still give Theta(n), never
degrading to Theta(n^2), regardless of the input.

**The recurrence:** T(n) = T(n/5) [finding the median of medians] + T(7n/10) [worst-case
recursing into the larger of the two guaranteed-30/70 partitions] + Theta(n) [the group-
median-finding and partitioning work]. Because 1/5 + 7/10 = 9/10 < 1, the work
strictly shrinks by a constant factor at each level even summing *both* recursive calls,
so this recurrence (solvable by the more general Akra-Bazzi-style substitution method,
since it doesn't fit the plain Master method's single-recursive-call shape) also solves
to Theta(n) — worst case, not just expected case.

### Comparing the two selection algorithms
| Algorithm | Worst case | Expected case | In practice |
| --- | --- | --- | --- |
| Quickselect (random pivot) | Theta(n^2) | Theta(n) | Simpler, smaller constant, almost
always used |
| Median-of-medians | Theta(n) | Theta(n) | Larger constant factor, more complex, rarely
used directly outside guaranteeing worst-case bounds |

In practice, quickselect (or a hybrid, "introselect," analogous to introsort's fallback
strategy) is almost always preferred — median-of-medians exists primarily as a proof
that Theta(n) worst-case selection is *possible* and as a building block in a few
specialized worst-case-sensitive contexts, not as an everyday tool.

## Pros
- Selection in Theta(n) (expected via quickselect, or worst-case via median-of-medians)
  is strictly cheaper than the Theta(n log n) full sort you'd otherwise reach for to
  answer a single order-statistic question.
- Quickselect reuses the exact partitioning logic from quicksort — no new mechanism
  needed, just a change in which side(s) to recurse into.
- Median-of-medians proves that a hard, adversary-proof Theta(n) worst-case bound is
  achievable for selection, which matters for algorithms and proofs that need this
  specific worst-case guarantee (e.g. certain worst-case-optimal geometric algorithms).

## Cons
- Quickselect shares quicksort's real (if rare, with randomization) Theta(n^2) worst
  case — unacceptable in a hard-real-time or adversarial-input context without the
  median-of-medians fallback.
- Median-of-medians has a large constant factor (the groups-of-5 processing, the extra
  recursive call for the medians themselves) that makes it slower in practice than
  quickselect for the overwhelming majority of real workloads, despite the better
  worst-case bound.
- Selection destructively reorders the input array in place (like quicksort's
  partitioning) — if the original order must be preserved, a copy is needed first.

## Alternatives
- **Full sort, then index** (Theta(n log n)) — simpler to reason about and appropriate
  when you need more than one order statistic, or need the array sorted for other
  reasons anyway; wasteful if you only need one order statistic from an otherwise-unused
  array.
- **A min-heap or max-heap of size k** (`clrs/07`) — for finding the top-k (not just the
  single k-th) elements from a large or streaming dataset, Theta(n log k) using a
  bounded heap is often preferable to full selection or sorting, especially when k is
  much smaller than n and the data arrives as a stream.

## When to use it
Use quickselect whenever you need exactly one order statistic (median, k-th smallest,
90th percentile) from an array and don't need the array fully sorted otherwise — a very
common case in statistics, data analysis, and algorithms needing a "typical value"
without a full ranking.

## When NOT to use it
Don't use plain quickselect where a hard worst-case time bound is mandatory (real-time
or adversarial-input contexts) without either randomization or a median-of-medians
fallback. Don't use selection at all if you need more than a small, fixed number of
order statistics — at that point, sorting once (Theta(n log n)) and then indexing
repeatedly is simpler and not meaningfully worse.

## Key takeaways / mental model
Selection is quicksort's partitioning idea with the second recursive branch pruned away
— since you only need one side's answer, you only need to descend into one side, which
is what turns Theta(n log n) into Theta(n) (a geometric, not logarithmic, sum of work
across levels). Median-of-medians trades a much larger constant factor for a
mathematically guaranteed 30/70-or-better split every time, eliminating the Theta(n^2)
worst case entirely.

## Self-check questions
1. Explain precisely why quickselect's recurrence T(n) = T(size of one side) + Theta(n)
   solves to Theta(n) via a geometric series, while quicksort's
   T(n) = T(left) + T(right) + Theta(n) solves to Theta(n log n) instead — what's the
   structural difference between the two recursion trees?
2. Why does median-of-medians use groups of exactly 5 (not, say, groups of 3)? (Hint:
   think about what fraction of elements are provably above/below the median-of-medians
   for different group sizes, and how that fraction interacts with the recurrence's
   convergence.)
3. Given that median-of-medians guarantees Theta(n) worst case, why is quickselect (with
   its Theta(n^2) worst case) still the default choice in most real implementations?
4. Describe a scenario where finding the top-k elements via a bounded heap
   (Theta(n log k)) would be preferable to running full selection k times or sorting the
   whole array.

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 9: "Medians and
  Order Statistics."
