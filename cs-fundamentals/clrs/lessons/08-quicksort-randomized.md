---
id: clrs/08
subject: clrs
title: Quicksort and randomized partitioning
slug: quicksort-randomized
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapter 7
prerequisites: [clrs/02, clrs/03, clrs/04]
created: 2026-08-10
updated: 2026-08-10
---

# Quicksort and randomized partitioning

## TL;DR
Quicksort sorts in place by partitioning around a pivot (everything smaller to its left,
everything larger to its right), then recursively sorting each side. Its worst case is
Theta(n^2) (a consistently bad pivot choice, e.g. always the smallest or largest
element), but its expected case — especially with randomized pivot selection — is
Theta(n log n) with excellent real-world constant factors, which is why it's the default
general-purpose sort in most standard libraries despite the theoretically-worse worst
case compared to mergesort or heapsort.

## The idea
Quicksort is divide-and-conquer (`clrs/03`) applied to sorting with a twist: instead of
splitting the array in half by *position* (as mergesort does) and doing expensive
combine work, quicksort splits by *value* around a chosen pivot, so that once partitioned,
no combine step is needed at all — the two partitions are already correctly ordered
relative to each other. The entire algorithm's performance hinges on one question: how
balanced is the partition each pivot produces?

## How it works

### PARTITION, the core operation
Given a subarray and a chosen pivot (CLRS's Lomuto scheme picks the last element),
PARTITION rearranges the subarray in place so every element <= pivot comes before every
element > pivot, and returns the pivot's final index. This is done in a single left-to-
right scan maintaining an index boundary between "known <= pivot" and "not yet examined"
— Theta(n) for a subarray of size n, using only O(1) extra space (the rearrangement
happens via swaps within the array itself).

### QUICKSORT, recursively
QUICKSORT(A, lo, hi): if lo < hi, call PARTITION to get a pivot index p, then
recursively QUICKSORT(A, lo, p-1) and QUICKSORT(A, p+1, hi). No combine step is needed —
unlike mergesort, correctness of the whole array follows immediately once both sides are
individually sorted, because PARTITION already guaranteed every left-side element is
<= every right-side element.

### Why the worst case is Theta(n^2)
If PARTITION always produces a maximally unbalanced split (one side has 0 elements, the
other has n-1) — which happens, for Lomuto's last-element pivot, precisely on
already-sorted or reverse-sorted input — the recurrence becomes
T(n) = T(n-1) + T(0) + Theta(n) = T(n-1) + Theta(n). Summing this arithmetic series
(n + (n-1) + (n-2) + ... + 1) gives Theta(n^2), the same shape as insertion sort's worst
case, and for the same underlying reason: each pass only makes Theta(1) progress toward
finishing (peeling off exactly one element) while still doing Theta(n) work.

### Why the best/balanced case is Theta(n log n)
If PARTITION always splits evenly (or even just splits into two parts each some constant
fraction of n, e.g. a 9-to-1 split), the recurrence looks like T(n) = 2T(n/2) + Theta(n)
(perfectly balanced) or, more generally, any split with both parts a constant fraction of
n still gives a recursion tree of depth Theta(log n) with Theta(n) total work per level —
by the Master method (`clrs/02`), Theta(n log n) either way. **The key insight: you don't
need a perfectly even split for Theta(n log n) — any split that's a constant fraction
away from 0 (e.g. even a 99-to-1 split) still gives logarithmic depth**, because
repeatedly taking even 1% of the remaining elements still shrinks the problem
geometrically.

### Randomized quicksort: making the good case the typical case
As covered in `clrs/04`, choosing the pivot **uniformly at random** from the current
subarray (rather than always the last element) means the bad case (always picking an
extreme element) requires the random number generator itself to conspire against you —
vanishingly unlikely for any specific input, and impossible for an adversary who doesn't
control the random source to engineer in advance. The **expected** running time of
randomized quicksort, averaged over the algorithm's own random choices, is Theta(n log n)
for *every* input, including already-sorted ones — a strictly stronger and more useful
practical guarantee than deterministic quicksort's "Theta(n log n) for most permutations,
Theta(n^2) for a few specific bad ones."

### Why quicksort beats mergesort/heapsort in practice despite a worse worst case
Quicksort's constant factor is small: PARTITION does simple, mostly-sequential array
scans and swaps with excellent cache locality, and (unlike mergesort) it sorts **in
place**, needing no auxiliary array. Production implementations (introsort, used by
C++'s `std::sort` and many language runtimes) get the best of both worlds: run randomized
quicksort by default for its speed, but detect excessive recursion depth (a signal of a
degenerating, near-worst-case partition) and switch to heapsort (`clrs/07`, worst-case
Theta(n log n) guaranteed) for that portion — eliminating quicksort's Theta(n^2) worst
case entirely while keeping its typical-case speed.

## Pros
- Excellent real-world constant factors: in-place, cache-friendly, simple inner loop —
  usually the fastest general-purpose comparison sort in practice for random or
  randomized-pivot workloads.
- Randomization gives a strong, input-independent expected-time guarantee (Theta(n log n)
  for any input) without needing to know or assume anything about the input distribution.
- In-place: O(log n) auxiliary space for the recursion stack (with tail-call optimization
  on the larger partition), versus mergesort's O(n) auxiliary array.

## Cons
- Genuine Theta(n^2) worst case exists (adversarial input against a non-randomized pivot
  choice, or extraordinarily unlucky random draws even with randomization) — unacceptable
  where a hard worst-case time bound is required.
- Not stable: equal elements can be reordered relative to each other by the partitioning
  swaps.
- Recursion depth in the worst case is Theta(n), which can cause stack overflow on very
  large, badly-partitioned inputs without an explicit iterative implementation or
  recursion-depth safeguard (as introsort provides).

## Alternatives
- **Mergesort** — guaranteed Theta(n log n) worst case and stable, at the cost of O(n)
  auxiliary space and typically worse cache behavior/constant factor than quicksort.
- **Heapsort** (`clrs/07`) — guaranteed Theta(n log n) worst case and in-place, but not
  stable and typically slower in practice than quicksort due to worse cache locality.
- **Introsort** — the practical hybrid used by most standard libraries: quicksort by
  default, falling back to heapsort on excessive recursion depth, giving both quicksort's
  typical speed and heapsort's worst-case guarantee.

## When to use it
Use quicksort (specifically, randomized-pivot quicksort or a hybrid like introsort) as
the default general-purpose in-memory sort when average-case speed matters and a rare,
bounded-probability worst case is acceptable — which describes the large majority of
sorting workloads, and is exactly why it's the default in most language runtimes.

## When NOT to use it
Don't use plain (non-hybrid, non-randomized) quicksort where a hard worst-case time
guarantee is required, where input might be adversarially chosen (e.g. sorting
user-submitted data in a context where an attacker could exploit a predictable pivot
rule to trigger Theta(n^2) as a denial-of-service vector), or where stability is required
— use mergesort, heapsort, or introsort (which defends against exactly this) instead.

## Key takeaways / mental model
Quicksort's entire performance story is "how balanced is the partition?" — any constant-
fraction split gives Theta(n log n); a maximally unbalanced split every time gives
Theta(n^2). Randomizing the pivot choice converts "Theta(n^2) for specific bad inputs"
into "Theta(n^2) only for vanishingly unlucky random draws, regardless of input" — a
strictly better practical guarantee.

## Self-check questions
1. Derive why an even 9-to-1 split at every level still yields Theta(n log n) overall,
   using the recursion-tree intuition from `clrs/02`.
2. Explain precisely why Lomuto's last-element pivot produces Theta(n^2) on
   already-sorted input, and why randomizing the pivot choice fixes this for that
   specific input without changing the algorithm's worst-case existence.
3. Why is quicksort not stable? Give a two-element example with equal keys where their
   relative order changes.
4. Why does introsort switch to heapsort rather than mergesort when recursion depth
   exceeds a threshold, given that both guarantee Theta(n log n) worst-case time?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 7: "Quicksort."
