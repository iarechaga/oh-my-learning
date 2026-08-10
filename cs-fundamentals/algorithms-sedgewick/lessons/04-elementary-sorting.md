---
id: algorithms-sedgewick/04
subject: algorithms-sedgewick
title: Elementary sorting (selection, insertion, shellsort)
slug: elementary-sorting
status: drafted
mastery:
seniority: junior
source: Algorithms (Sedgewick, Wayne), Section 2.1
prerequisites: [algorithms-sedgewick/02, algorithms-sedgewick/03]
created: 2026-08-10
updated: 2026-08-10
---

# Elementary sorting (selection, insertion, shellsort)

## TL;DR
Selection sort always does Theta(n^2) comparisons regardless of input order; insertion
sort does Theta(n^2) worst case but only Theta(n) on nearly-sorted input, making it the
practical elementary sort of choice for such data; shellsort generalizes insertion sort
by first sorting widely-spaced subsequences (h-sorting), achieving sub-quadratic
performance with a remarkably simple modification.

## The idea
Before reaching for a Theta(n log n) sort (`clrs/08`, `algorithms-sedgewick/05`), it's
worth understanding the simple quadratic sorts thoroughly — not because they're the right
choice for large random data, but because (a) they illuminate exactly what "comparisons"
and "data movement" cost mean concretely, (b) insertion sort specifically is genuinely the
right choice for small or nearly-sorted arrays (used as the base case inside real
production sorts, including introsort's small-array cutoff), and (c) shellsort shows how
a small structural insight (sort at multiple spacings, not just adjacent elements) can
meaningfully beat quadratic time without needing a fundamentally different algorithmic
paradigm like divide and conquer.

## How it works

### Selection sort: always Theta(n^2), no matter what
Repeatedly find the minimum of the unsorted remainder and swap it into place. For each of
n positions, scan the remaining unsorted elements to find the minimum — this scan happens
regardless of whether the array is already sorted, reverse sorted, or random, because the
algorithm always checks every remaining element to find the true minimum. **~n^2/2
comparisons, always** (tilde notation, `algorithms-sedgewick/02`) — the input order has
zero effect on the comparison count. Data movement, however, is minimal: exactly n swaps
total (one per position), regardless of input — the cheapest possible data-movement cost
among comparison sorts, which matters specifically when swaps are expensive relative to
comparisons (e.g. sorting large records by a small key).

### Insertion sort: input-order-sensitive, from Theta(n) to Theta(n^2)
Build up a sorted prefix one element at a time: for each new element, shift it leftward
past every already-sorted element larger than it, until it finds its correct position.
**Worst case** (reverse-sorted input): every new element must shift past every previously
sorted element — ~n^2/2 compares and ~n^2/2 swaps (actually element-shifts, which
Sedgewick counts as "half exchanges" since each shift moves one element by one position,
about half as much data movement as a full swap). **Best case** (already-sorted input):
each new element requires exactly one comparison (against its immediate predecessor,
confirming it's already in place) and zero shifts — Theta(n) total, a dramatic
input-dependent difference selection sort never exhibits at all.

**Why "nearly sorted" specifically favors insertion sort.** Define an **inversion** as a
pair of elements out of relative order (i < j but array[i] > array[j]). Insertion sort's
running time is, more precisely, proportional to the number of inversions plus n (each
shift removes exactly one inversion) — so an array with few inversions (nearly sorted,
or made of a few sorted runs) sorts in close to linear time, regardless of overall size
n. This is a genuinely different and stronger characterization than "best/worst case,"
because it identifies exactly *which* structural property of the input (inversion count)
determines the actual cost.

### Shellsort: sorting at decreasing gaps
Shellsort generalizes insertion sort by first **h-sorting** the array for a sequence of
decreasing gap values h (e.g. using Knuth's increment sequence 1, 4, 13, 40, ...,
(3^k-1)/2), where "h-sorting" means running insertion sort on each of the h interleaved
subsequences formed by taking every h-th element, before finally h-sorting with h=1
(equivalent to a final full insertion-sort pass, but on an array already made much more
"nearly sorted" by the prior larger-gap passes).

**Why this helps.** A single element far out of place (e.g. the largest element sitting
near the front) costs insertion sort a long, slow one-position-at-a-time crawl to its
correct location — but an early large-gap h-sort can move that element most of the way to
its correct position in a single large jump, dramatically reducing the number of
inversions remaining by the time the final, smaller-gap passes run. **Complexity** with
Knuth's increments is known to be O(n^(3/2)) in the worst case (proven) and observed to
be close to O(n^(7/6)) empirically for typical inputs — genuinely sub-quadratic, though
not as good as Theta(n log n), achieved with an implementation only marginally more
complex than plain insertion sort (no auxiliary array, no recursion, in-place).

### Worked example, sketched
Array `[5, 1, 4, 2, 8, 3, 7, 6]`, gap sequence 4, 1 (a simplified example). h=4-sort:
compare and insertion-sort the four subsequences `(5,8)`, `(1,3)`, `(4,7)`, `(2,6)`
independently at spacing 4 — since all four pairs already happen to be in order here, no
swaps occur, but on a less-friendly input this step would move far-apart elements much
closer to their final relative positions in a single pass. h=1-sort: a standard full
insertion sort finishes the job, now operating on an array that (in general, not
necessarily this small toy example) has far fewer inversions than the original,
completing faster than a from-scratch insertion sort would have.

## Pros
- Selection sort's minimal, input-independent data movement (exactly n swaps) is valuable
  specifically when swap cost dominates comparison cost (e.g. sorting large records
  in-place).
- Insertion sort's Theta(n) best case on nearly-sorted data makes it the right practical
  choice for small arrays or incrementally-maintained sorted collections (appending a few
  new elements to an already-sorted array) — and it's exactly why production sorts
  (introsort, Timsort) switch to insertion sort below a small-size threshold.
- Shellsort achieves genuinely sub-quadratic performance with almost no implementation
  complexity beyond plain insertion sort — no auxiliary memory, no recursion — making it
  a reasonable choice when simplicity matters more than squeezing out the last bit of
  performance a full Theta(n log n) sort would provide.

## Cons
- All three are asymptotically worse than Theta(n log n) sorts for large, arbitrary-order
  input — none should be used as a general-purpose sort for large random data.
- Selection sort's complete insensitivity to input order means it never benefits from
  "nice" inputs the way insertion sort or shellsort do — it's the worst choice among the
  three whenever the input has any exploitable structure.
- Shellsort's performance is sensitive to the specific increment sequence chosen (some
  sequences, like the naive halving sequence 1,2,4,8,..., perform much worse than
  Knuth's), and no increment sequence achieves a proven Theta(n log n) bound — it remains
  a heuristically excellent, but not asymptotically optimal, choice.

## Alternatives
- **Mergesort / quicksort** (`algorithms-sedgewick/05`, `clrs/08`) — the right choice for
  large, arbitrary-order arrays needing genuinely Theta(n log n) performance.
- **Timsort** (Python's and Java's default sort for objects) — a production hybrid that
  specifically detects and exploits already-sorted runs (a direct descendant of
  insertion sort's inversion-sensitivity insight), combined with mergesort for the
  overall structure.

## When to use it
Use insertion sort for small arrays (as a sort in its own right, or as the base case
inside a larger divide-and-conquer sort) or for data known to be nearly sorted already
(e.g. incrementally appending a few new records to an already-sorted list). Use
shellsort when you want noticeably better than quadratic performance without the
implementation complexity or auxiliary memory of mergesort/quicksort. Use selection sort
only when minimizing swap count specifically matters more than comparison count.

## When NOT to use it
Don't use selection sort, insertion sort, or shellsort as the default sort for large,
arbitrary-order data where Theta(n log n) performance is needed and available — reach for
mergesort, quicksort, or a language's built-in sort instead. Don't assume shellsort's
good empirical performance translates into a competitive proven worst-case bound compared
to Theta(n log n) sorts.

## Key takeaways / mental model
Selection sort's cost is input-independent (always ~n^2/2 compares); insertion sort's
cost tracks the input's actual inversion count (near-linear on nearly-sorted data);
shellsort uses large-gap passes to cheaply remove long-distance inversions before a
final small-gap pass cleans up what's left, achieving sub-quadratic performance from
what's structurally still "just" repeated insertion sort.

## Self-check questions
1. Explain why selection sort always does ~n^2/2 comparisons regardless of input order,
   while insertion sort's comparison count varies dramatically with the input's inversion
   count.
2. Define "inversion" precisely, and explain why insertion sort's running time is
   proportional to the number of inversions plus n.
3. Walk through, conceptually, why an early large-gap h-sort in shellsort can move a
   badly-placed element most of the way to its correct position in a single pass, in a
   way plain insertion sort (gap=1 only) cannot.
4. Why do production divide-and-conquer sorts (introsort, Timsort) switch to plain
   insertion sort for small subarrays rather than continuing to recurse all the way down
   to single elements?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 2.1: "Elementary
  Sorts."
