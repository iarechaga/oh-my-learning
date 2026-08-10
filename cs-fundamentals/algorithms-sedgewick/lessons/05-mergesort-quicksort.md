---
id: algorithms-sedgewick/05
subject: algorithms-sedgewick
title: Mergesort and quicksort in practice
slug: mergesort-quicksort
status: drafted
mastery:
seniority: mid
source: Algorithms (Sedgewick, Wayne), Sections 2.2-2.3
prerequisites: [algorithms-sedgewick/04, clrs/03, clrs/08]
created: 2026-08-10
updated: 2026-08-10
---

# Mergesort and quicksort in practice

## TL;DR
Where CLRS proves mergesort's and quicksort's asymptotic complexity (`clrs/03`,
`clrs/08`), Sedgewick and Wayne focus on the concrete engineering that separates a
textbook implementation from a production-quality one: avoiding unnecessary array
allocation in mergesort, switching to insertion sort for small subarrays, detecting
already-sorted input cheaply, and choosing partitioning schemes and pivot strategies
that hold up on real, not just theoretical, inputs.

## The idea
Knowing mergesort is Theta(n log n) and quicksort is expected Theta(n log n) (`clrs/03`,
`clrs/08`) tells you the asymptotic story, but real implementations of both have a
surprising amount of engineering nuance that determines whether the *constant factor* is
excellent or mediocre — and constant factors are exactly what determines which sort wins
in practice among algorithms in the same asymptotic class. This lesson is about that
engineering layer: the specific, concrete optimizations Sedgewick and Wayne walk through
that turn a correct textbook algorithm into a fast one.

## How it works

### Mergesort: avoiding repeated array allocation
A naive recursive mergesort allocates a new auxiliary array at *every* merge call —
wasteful, since the total auxiliary space needed is Theta(n) regardless of recursion
depth, not Theta(n log n) worth of separate allocations. **The fix:** allocate a single
auxiliary array *once*, before recursion begins, and pass it down through every
recursive call — the merge step reads from and writes into designated ranges of this one
shared array. This doesn't change mergesort's asymptotic space complexity (still Theta(n)
auxiliary space) but meaningfully reduces real allocation overhead, which in most managed
runtimes (garbage-collected languages especially) has non-trivial constant cost per
allocation.

### Mergesort: switching to insertion sort for small subarrays
Recursing all the way down to single-element base cases has real overhead (function call
cost, and insertion sort's `algorithms-sedgewick/04` excellent performance on small
arrays makes recursing further pointless) — production mergesorts switch to plain
insertion sort once a subarray's size drops below a small cutoff (commonly around 7-15
elements, tuned empirically). This is the same insight introsort applies to quicksort
(`clrs/08`), applied symmetrically to mergesort.

### Mergesort: skipping the merge when already ordered
Before merging two adjacent sorted halves, check whether the last element of the left
half is already <= the first element of the right half — if so, the two halves are
*already* in overall sorted order relative to each other, and the merge step can be
skipped entirely (just leave the array as-is). This costs one extra comparison per
merge call in the worst case, but on **partially sorted** input (a common real-world
case — data that's already mostly sorted, or made of a few long sorted runs), it can
dramatically reduce actual work, turning many of the recursion's merge steps into no-ops.

### Quicksort: the median-of-three pivot heuristic
Rather than randomizing the pivot (`clrs/04`, `clrs/08`) or always taking a fixed position
(vulnerable to adversarial or already-sorted input), Sedgewick's practical quicksort
often uses **median-of-three**: examine the first, middle, and last elements of the
subarray, and use their median as the pivot. This is cheaper than full randomization
(no random number generator call needed) and empirically avoids the worst-case behavior
on the specific input patterns (sorted, reverse-sorted) that a naive fixed-position pivot
is most vulnerable to — though, unlike true randomization, it does not give the same
rigorous input-independent expected-time guarantee, since a sufficiently adversarial
input *could* still be constructed against a known, deterministic median-of-three rule.

### Quicksort: handling duplicate keys with 3-way partitioning
Standard 2-way partitioning (`clrs/08`) degrades toward Theta(n^2) behavior when the
array contains many duplicate keys (every occurrence of the pivot's value ends up on one
side, producing a maximally unbalanced split when duplicates are common — e.g. sorting an
array where most elements share the same key). **Dijkstra's 3-way partitioning** (named
for Edsger Dijkstra, unrelated to Dijkstra's shortest-path algorithm) partitions into
*three* regions in a single pass — less than pivot, equal to pivot, greater than pivot —
using three pointers, so that every occurrence of the pivot's value is grouped together
and excluded entirely from both recursive calls. On an array with many duplicate keys,
this converts what would otherwise be Theta(n^2) behavior back down toward Theta(n) or
Theta(n log(n/k)) for k distinct key values with high multiplicity — a genuinely
important practical fix for a real, common failure mode (sorting data with few distinct
values, e.g. sorting people by a small set of categorical labels).

### Quicksort: switching to insertion sort for small subarrays (again)
The same small-subarray cutoff optimization from mergesort applies to quicksort's
recursion as well, for the identical reason: below a small size threshold, insertion
sort's low overhead beats continuing to recurse.

## Pros
- These engineering refinements meaningfully improve real-world constant factors without
  changing either algorithm's fundamental asymptotic complexity — genuinely "free"
  performance for the cost of moderate implementation complexity.
- 3-way partitioning specifically fixes a real, common failure mode (many duplicate keys)
  that plain 2-way partitioning handles poorly, converting a potential Theta(n^2) blowup
  back to near-linear behavior.
- The already-sorted-skip optimization in mergesort and the small-array insertion-sort
  cutoff in both algorithms are exactly the kind of "notice what real data looks like and
  exploit it" thinking that separates production sort implementations from textbook ones.

## Cons
- Median-of-three, unlike true randomization, doesn't provide a rigorous input-
  independent guarantee — a sufficiently adversarial, deliberately-constructed input
  targeting the specific median-of-three rule could still trigger worst-case behavior, a
  real concern if untrusted input is ever sorted this way.
- 3-way partitioning adds implementation complexity (three pointers and a more involved
  partitioning loop) compared to plain 2-way partitioning, and its benefit is only
  realized on inputs with meaningful key duplication — on inputs with all-distinct keys,
  it performs comparably to (not better than) standard 2-way partitioning.
- All these optimizations require careful, correct implementation — a bug in the
  small-array cutoff, the shared auxiliary array indexing, or the 3-way partition
  pointers can silently produce incorrect (not just slow) results, unlike the simpler
  textbook versions which are easier to verify correct by inspection.

## Alternatives
- **Plain textbook mergesort/quicksort** (`clrs/03`, `clrs/08`) — simpler to implement
  and verify correct, appropriate for learning or for contexts where the extra constant-
  factor performance isn't worth the added implementation complexity.
- **Language built-in sorts** — most production language runtimes (Java's `Arrays.sort`,
  Python's Timsort, C++'s introsort-based `std::sort`) already incorporate these and
  further optimizations; understanding this lesson explains *why* they're implemented the
  way they are, rather than motivating hand-rolling a competitor from scratch.
- **Timsort** — goes further than mergesort's already-sorted-skip optimization by
  actively detecting and merging naturally-occurring sorted runs in the input, achieving
  Theta(n) on already-sorted or few-runs input while remaining Theta(n log n) worst case.

## When to use it
Apply these optimizations (shared auxiliary array, small-array insertion-sort cutoff,
already-sorted-skip, 3-way partitioning) when implementing a sort for production use
where performance genuinely matters and the input characteristics (partial order,
duplicate-heavy keys) are known or suspected. Otherwise, prefer a well-tested standard-
library sort, which already includes these refinements.

## When NOT to use it
Don't hand-roll these optimizations into a from-scratch sort implementation for
production code when a standard-library sort already exists and is well-tested — the
correctness risk of a subtly buggy custom implementation usually outweighs any marginal
performance gain. Don't use median-of-three pivot selection (without randomization) in a
context where the input could be adversarially chosen against your specific
implementation.

## Key takeaways / mental model
Asymptotic complexity (`clrs/03`, `clrs/08`) tells you the shape of the growth curve;
these engineering refinements tell you how to make the constant factor small in
practice, by exploiting realistic input structure (partial order, duplicate keys, small
subarrays) that a purely asymptotic analysis is indifferent to.

## Self-check questions
1. Explain why allocating mergesort's auxiliary array once, outside the recursion, rather
   than at every merge call, doesn't change the algorithm's asymptotic space complexity
   but does reduce real overhead.
2. Walk through why plain 2-way quicksort partitioning degrades toward Theta(n^2)
   behavior on an array with many duplicate keys, and how 3-way partitioning fixes this.
3. Why does median-of-three pivot selection not provide the same rigorous guarantee as
   true randomization (`clrs/04`), even though it empirically avoids common worst-case
   input patterns?
4. Describe the already-sorted-skip optimization in mergesort's merge step, and explain
   what property of real-world data makes it valuable despite adding a small constant
   overhead to every merge call.

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Sections 2.2 ("Mergesort") and
  2.3 ("Quicksort").
