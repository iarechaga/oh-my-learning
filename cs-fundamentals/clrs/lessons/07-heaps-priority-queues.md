---
id: clrs/07
subject: clrs
title: Heaps and priority queues
slug: heaps-priority-queues
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapter 6
prerequisites: [clrs/01, clrs/05]
created: 2026-08-10
updated: 2026-08-10
---

# Heaps and priority queues

## TL;DR
A binary heap is an array-backed, nearly-complete binary tree satisfying the heap
property (each node is >= its children, for a max-heap), giving O(log n) insert and
O(log n) extract-max/min with O(1) peek-max/min. It is the standard implementation of a
**priority queue** — a structure that always serves the highest (or lowest) priority
element next, regardless of insertion order — and also underlies heapsort, an in-place
O(n log n) sorting algorithm.

## The idea
A queue (`clrs/05`) serves elements in insertion order; a priority queue serves elements
in *priority* order, no matter when they were inserted. Implementing a priority queue
with a sorted array gives O(1) extract-max but O(n) insert (shifting to maintain sorted
order); an unsorted array flips this (O(1) insert, O(n) extract-max to find the max). The
binary heap gets both operations down to O(log n) by maintaining only a much weaker
invariant than full sortedness — enough structure to find the max quickly, but not so
much structure that insertion is expensive.

## How it works

### The heap property and the array representation
A **max-heap** is a nearly-complete binary tree (every level full except possibly the
last, which fills left to right) where every node's value is >= both its children's
values. Crucially, this is *not* full sortedness — a node's value only needs to dominate
its own subtree, not the whole array, so there's no ordering relationship at all between
sibling subtrees. This weaker invariant is exactly what makes insertion cheap.

The tree is stored in a plain array with no pointers at all: for a node at index i
(0-indexed), its children live at indices 2i+1 and 2i+2, and its parent at
floor((i-1)/2). This works because the tree is nearly complete — there are no gaps to
represent, so array position alone encodes the tree structure.

### MAX-HEAPIFY: restoring the heap property downward
Given a node that might violate the heap property (its value might be smaller than one of
its children) but whose subtrees are already valid heaps, MAX-HEAPIFY compares the node
to its two children, and if a child is larger, swaps them and recurses into that child's
subtree (the "sift down" or "bubble down" operation). Since a nearly-complete binary tree
of n nodes has height Theta(log n), and MAX-HEAPIFY does O(1) work per level as it
descends, MAX-HEAPIFY is O(log n).

### BUILD-MAX-HEAP: turning an arbitrary array into a heap
Naively, you might call MAX-HEAPIFY on every node from the root down — but the correct
and efficient approach calls it on every node from the **last non-leaf node up to the
root** (leaves are trivially valid single-node heaps and need no work). This ordering
guarantees each call's subtrees are already valid heaps by the time it runs, satisfying
MAX-HEAPIFY's precondition. Although each call individually costs O(log n), a more
careful accounting (summing the actual costs, which are smaller for the many nodes near
the bottom and larger only for the few nodes near the top) shows BUILD-MAX-HEAP is
**Theta(n)**, not the naively-expected Theta(n log n) — a classic and important example
of a bound that looks worse than it is under a per-call worst case, but is genuinely
tighter when the whole sequence of calls is analyzed together (a preview of the
amortized-analysis mindset in `clrs/17`).

### HEAP-EXTRACT-MAX and HEAP-INSERT
**Extract-max:** swap the root (the max) with the last element in the array, shrink the
array by one (removing the old root, now at the end), then call MAX-HEAPIFY on the new
root to restore the property — O(log n) for the heapify, O(1) for everything else.

**Insert:** append the new element at the end of the array (as a new leaf), then repeatedly
compare it to its parent and swap upward ("bubble up" or "sift up") as long as it's
larger than its parent — O(log n), since the tree has height Theta(log n).

**Worked example.** Max-heap `[16, 14, 10, 8, 7, 9, 3]` (array indices 0-6). Extract-max:
swap 16 (root) with 3 (last element) -> `[3, 14, 10, 8, 7, 9]` (16 removed from the
array), then MAX-HEAPIFY(0): compare 3 to children 14 and 10, swap with 14 (larger) ->
`[14, 3, 10, 8, 7, 9]`, then MAX-HEAPIFY(1): compare 3 to children 8 and 7, swap with 8
-> `[14, 8, 10, 3, 7, 9]`, then MAX-HEAPIFY(3): node 3 (index 3) has no children (out of
bounds), done. Final heap: `[14, 8, 10, 3, 7, 9]`, and the extracted max was 16.

### Heapsort
Build a max-heap from the input array (Theta(n)), then repeatedly extract-max and place
it at the end of the shrinking "unsorted" region — n extractions, each O(log n), for a
total of Theta(n log n), and it's **in-place** (uses the input array itself as the heap's
storage, needing only O(1) extra space, unlike mergesort's O(n) auxiliary array). Heapsort
is not, however, **stable** (equal elements can be reordered relative to each other),
because the swap-and-sift-down mechanics don't preserve original relative order.

### Priority queue operations beyond a plain heap
A full priority queue ADT also typically supports **INCREASE-KEY** (raise a specific
element's priority, then sift it up — O(log n), needed for algorithms like Dijkstra's
shortest path, `clrs/14`, which repeatedly relaxes and re-prioritizes nodes) and
sometimes **DECREASE-KEY**. Implementing these efficiently on a plain array-backed heap
requires also maintaining a map from element identity to its current array index (since
the element's position moves as the heap is modified) — a detail that matters a great
deal when implementing Dijkstra's algorithm correctly and efficiently.

## Pros
- O(log n) insert and extract-max/min, O(1) peek — good, balanced performance for
  priority-driven workloads with no need for full sortedness.
- Array-backed: no pointer overhead, excellent cache locality compared to a pointer-based
  tree structure, and BUILD-MAX-HEAP is Theta(n), cheaper than sorting the whole array.
- Heapsort gives in-place, worst-case-guaranteed Theta(n log n) sorting, unlike
  quicksort's Theta(n^2) worst case — valuable specifically where a worst-case time
  guarantee matters more than average-case speed or memory bandwidth.

## Cons
- No efficient way to search for an arbitrary element or to find anything other than the
  max (or min) — a heap answers exactly one query well and nothing else.
- Heapsort is not stable and, despite being asymptotically as good as quicksort, tends to
  have worse real-world cache behavior than a well-tuned quicksort (the sift-down
  operation jumps around the array in a pattern less cache-friendly than quicksort's
  mostly-sequential partitioning), so quicksort is often preferred in practice when
  average-case speed matters more than worst-case guarantees.
- Efficient INCREASE-KEY/DECREASE-KEY requires extra bookkeeping (an index map) beyond a
  plain array heap — easy to get subtly wrong when implementing Dijkstra's algorithm from
  scratch.

## Alternatives
- **Sorted or unsorted array/list** — simpler, but forces the O(n) cost onto either
  insertion or extraction; only reasonable for very small or rarely-modified collections.
- **Balanced search trees** (`clrs/09`) — support the same min/max extraction in
  O(log n), plus arbitrary search, predecessor/successor, and ordered traversal, at the
  cost of more implementation complexity and typically worse constant factors than an
  array-backed heap for the pure priority-queue use case.
- **Fibonacci heaps** (mentioned in CLRS, not required for typical use) — offer O(1)
  amortized insert and decrease-key, improving Dijkstra's and Prim's asymptotic
  complexity, at the cost of substantially higher implementation complexity and constant
  factors that often make them slower in practice despite better asymptotics.

## When to use it
Use a binary heap whenever you need repeated access to the current minimum or maximum of
a changing collection — task schedulers, Dijkstra's and Prim's algorithms (`clrs/14`,
`clrs/15`), event simulation queues, and top-k streaming problems.

## When NOT to use it
Don't use a heap when you need to search for arbitrary elements, maintain full sorted
order for range queries, or need stable sorting — reach for a balanced search tree
(`clrs/09`) or a stable sort (e.g. mergesort) instead.

## Key takeaways / mental model
A heap trades full sortedness for a much weaker, cheaper-to-maintain invariant ("each
node dominates its own subtree") that's just enough to answer "what's the max?" in O(1)
and update in O(log n). BUILD-MAX-HEAP's Theta(n) bound (not Theta(n log n)) comes from
most nodes being near the bottom, where sift-down work is cheap.

## Self-check questions
1. Explain why MAX-HEAPIFY requires its node's subtrees to already be valid heaps, and
   why BUILD-MAX-HEAP therefore processes nodes bottom-up rather than top-down.
2. Walk through why BUILD-MAX-HEAP is Theta(n) rather than the naively-expected
   Theta(n log n) — where does the looser bound's pessimism come from?
3. Why is heapsort not a stable sort? Construct a small example with duplicate keys where
   relative order is not preserved.
4. Why does implementing DECREASE-KEY efficiently for Dijkstra's algorithm require extra
   bookkeeping beyond a plain array-backed heap?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 6: "Heapsort."
