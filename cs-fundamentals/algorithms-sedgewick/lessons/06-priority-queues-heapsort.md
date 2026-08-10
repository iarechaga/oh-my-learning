---
id: algorithms-sedgewick/06
subject: algorithms-sedgewick
title: Priority queues and heapsort
slug: priority-queues-heapsort
status: drafted
mastery:
seniority: mid
source: Algorithms (Sedgewick, Wayne), Section 2.4
prerequisites: [algorithms-sedgewick/05, clrs/07]
created: 2026-08-10
updated: 2026-08-10
---

# Priority queues and heapsort

## TL;DR
Sedgewick and Wayne present the binary heap through its two core primitives, **swim**
(bubble up) and **sink** (bubble down), implemented directly on a 1-indexed array for
clean parent/child index arithmetic, and use it to build both a priority-queue API and
heapsort — with particular attention to heapsort's real-world weakness (poor cache
performance from non-sequential array access) compared to its excellent theoretical
profile.

## The idea
CLRS's heap treatment (`clrs/07`) proves the asymptotic bounds (MAX-HEAPIFY O(log n),
BUILD-MAX-HEAP Theta(n)) rigorously. Sedgewick's treatment covers the same structure but
names the two directions of repair explicitly as **swim** (an element moves up when it's
larger than its parent — used after insertion) and **sink** (an element moves down when
it's smaller than a child — used after removing the root), a naming convention that maps
directly and memorably onto the two operations' actual array-index movement, and pairs
this with an honest engineering assessment of heapsort's practical weaknesses despite its
strong asymptotic guarantees.

## How it works

### 1-indexing for clean arithmetic
Sedgewick's heap implementation stores the heap starting at array index 1 (leaving index
0 unused), because this makes the parent/child index arithmetic maximally simple: a node
at index k has parent at k/2 (integer division) and children at 2k and 2k+1 — no
off-by-one adjustments needed, unlike the 0-indexed formulas (parent at (i-1)/2, children
at 2i+1 and 2i+2) CLRS uses. This is a purely presentational/implementation choice with
no asymptotic consequence, but it meaningfully reduces the chance of off-by-one bugs when
implementing from scratch.

### Swim: restoring the heap property after insertion
Insert a new element at the end of the array (incrementing size), then **swim** it: while
it's larger than its parent (for a max-heap), swap it with its parent and repeat. This is
exactly CLRS's HEAP-INSERT bubble-up, O(log n) since the heap's height is Theta(log n).

### Sink: restoring the heap property after removal
Remove the root (the max), move the *last* element into the root's position, decrement
size, then **sink** it: while it's smaller than the larger of its two children, swap with
that larger child and repeat. This is exactly CLRS's HEAP-EXTRACT-MAX's post-swap
MAX-HEAPIFY call, O(log n).

**Why compare against the *larger* child specifically.** Sinking must always compare
against whichever child is larger (not just either child arbitrarily) — swapping with
the smaller child could leave the *other* child still larger than the newly-sunk element,
violating the heap property at that level. This is a small but easy-to-get-wrong detail
when implementing sink from scratch.

### Building a heap from an unordered array: the same Theta(n) result, viewed via sink
Sedgewick's construction calls **sink** on every non-leaf node from the middle of the
array back to the start — identical in structure and identical in resulting Theta(n)
complexity to CLRS's BUILD-MAX-HEAP (`clrs/07`), just named with "sink" terminology.
The same accounting argument applies: most nodes are near the bottom of the tree, where a
sink operation touches few levels, so despite each individual sink being worst-case
O(log n), the total across all calls sums to Theta(n), not Theta(n log n).

### Heapsort: in-place, but with a real practical cost
Build a heap (Theta(n)) from the array to be sorted, then repeatedly swap the root (the
current max) with the last element of the shrinking "heap" region and sink the new root
— n extractions, each O(log n), for Theta(n log n) total, entirely in-place with no
auxiliary array. This matches CLRS's presentation (`clrs/07`) exactly in mechanism and
complexity.

**The honest practical caveat Sedgewick emphasizes.** Despite heapsort's excellent
theoretical profile (in-place, worst-case-guaranteed Theta(n log n), unlike quicksort's
worst case or mergesort's O(n) auxiliary space), it performs **poorly in practice**
relative to a well-tuned quicksort, because the sink operation's array-access pattern
(index k, then 2k, then 4k, then 8k, ...) jumps across memory in a way that produces
far worse cache locality than quicksort's mostly-sequential partitioning scans. This is
exactly the kind of gap between asymptotic elegance and real hardware performance that
motivates the "cost model plus empirical validation" methodology from
`algorithms-sedgewick/02` — a purely asymptotic comparison would miss this entirely,
since heapsort and a well-tuned quicksort are both "Theta(n log n)-ish" but perform very
differently on real machines.

### The priority-queue API, and why it matters beyond sorting
Beyond heapsort, the swim/sink mechanism directly implements a full priority-queue ADT:
`insert` (append + swim), `delMax`/`delMin` (swap root to end, shrink, sink), and `max`/
`min` (peek at the root, O(1)). This ADT (not the sorting application) is the more common
real-world use of a heap: task schedulers, simulation event queues, and Dijkstra's/Prim's
algorithms (`clrs/14`, `clrs/15`) all use the priority-queue interface directly, with
heapsort itself being just one specific, secondary application of the same underlying
structure.

## Pros
- Swim/sink naming maps directly and memorably onto array-index movement direction,
  reducing implementation errors compared to less mnemonic naming.
- 1-indexing simplifies parent/child arithmetic to clean integer halving/doubling, a
  small but real reduction in off-by-one bug risk.
- Heapsort remains the standard fallback for guaranteeing worst-case Theta(n log n) with
  O(1) auxiliary space when quicksort's worst case or mergesort's auxiliary-space cost is
  unacceptable — exactly why introsort falls back to heapsort, not mergesort, for its
  worst-case guarantee.

## Cons
- Heapsort's cache-unfriendly access pattern makes it noticeably slower in practice than
  a well-tuned quicksort for typical, non-adversarial inputs, despite matching or beating
  quicksort's asymptotic worst-case guarantee.
- The priority-queue interface built directly on a heap doesn't support efficient
  arbitrary-element removal or search — only access to the current max/min, same
  limitation as CLRS's treatment (`clrs/07`).
- 1-indexing, while simplifying arithmetic, requires care when interfacing with
  0-indexed language arrays/collections (e.g. Java arrays, Python lists) — an
  implementation detail that must be handled consistently to avoid subtle bugs.

## Alternatives
- **Quicksort** (`algorithms-sedgewick/05`, `clrs/08`) — typically faster in practice due
  to better cache locality, at the cost of a (rare, with randomization/median-of-three) 
  Theta(n^2) worst case heapsort never exhibits.
- **Balanced search trees** (`clrs/09`) — needed instead of a heap when arbitrary search
  or ordered traversal, not just max/min access, is required.
- **Indexed priority queues** (a Sedgewick-specific extension, tracking each element's
  current heap position to support efficient priority updates) — needed for algorithms
  like Prim's and Dijkstra's that must decrease a specific, already-inserted element's
  key.

## When to use it
Use a binary heap (via swim/sink) whenever you need a priority-queue ADT — task
scheduling, event simulation, or as the underlying structure for Dijkstra's/Prim's
algorithms. Use heapsort specifically when an in-place, worst-case-guaranteed
Theta(n log n) sort is required and quicksort's rare worst case or mergesort's auxiliary
space is unacceptable.

## When NOT to use it
Don't default to heapsort for general-purpose sorting where average-case speed matters
more than worst-case guarantees — a well-tuned quicksort (or a language's built-in sort)
usually wins in practice due to cache behavior. Don't use a plain heap when you need
efficient decrease-key on arbitrary elements without extra bookkeeping — use an indexed
priority queue instead.

## Key takeaways / mental model
Swim moves a too-large element up toward the root after insertion; sink moves a too-
small root down after removal — the same two primitives, run in opposite directions,
build both the priority-queue ADT and heapsort. Heapsort's asymptotic elegance
(in-place, worst-case Theta(n log n)) doesn't translate into practical speed, because its
access pattern is cache-unfriendly compared to quicksort's mostly-sequential scans — a
reminder that asymptotic analysis and real hardware performance can diverge.

## Self-check questions
1. Explain why sink must always compare against the *larger* of a node's two children,
   and construct a small example showing what goes wrong if it compared against the
   smaller child instead.
2. Why does 1-indexing simplify the parent/child index formulas compared to 0-indexing,
   and what practical care is needed when interfacing with a 0-indexed array or language
   collection?
3. Despite heapsort's worst-case Theta(n log n) guarantee (better than quicksort's
   worst case), explain why it's typically slower in practice — what specific hardware-
   level property causes this?
4. Why does Prim's or Dijkstra's algorithm need an *indexed* priority queue rather than a
   plain heap-based one, and what operation does the indexing specifically enable?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 2.4: "Priority
  Queues."
