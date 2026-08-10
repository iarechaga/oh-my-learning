---
id: algorithms-sedgewick/01
subject: algorithms-sedgewick
title: Union-find and connectivity modeling
slug: union-find-connectivity
status: drafted
mastery:
seniority: junior
source: Algorithms (Sedgewick, Wayne), Section 1.5
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Union-find and connectivity modeling

## TL;DR
Sedgewick and Wayne open their book with the union-find (dynamic connectivity) problem
specifically to teach a methodology: start with the simplest possible correct
implementation, measure it, identify the actual bottleneck, and improve it incrementally
— arriving, through three concrete versions (quick-find, quick-union, weighted
quick-union with path compression), at the same near-constant-time result CLRS proves
more abstractly (`clrs/18`).

## The idea
The dynamic connectivity problem: given a sequence of pairs of objects, and a stream of
"union" (connect these two) and "is-connected" (are these two connected, directly or
transitively?) queries, answer each query correctly and efficiently. This single problem
is used as the book's opening case study because it's simple to state, has genuinely
different implementations with dramatically different performance, and rewards a very
teachable engineering process: implement the naive thing first, benchmark it against
realistic input sizes, find where it actually breaks down, and fix specifically that.

## How it works

### Quick-find: correctness first, performance ignored
Represent the partition as an array `id[]` where `id[p]` is p's *component identifier*
(two objects are connected exactly when their `id` values are equal — the simplest
possible representation to reason about). FIND(p) is `return id[p]` — O(1), trivially.
UNION(p, q): if already connected, do nothing; otherwise, change **every** entry equal to
`id[p]` to `id[q]` — an O(n) scan of the entire array, because after the union, everyone
who used to share p's identifier must now share q's.

**Why this is unacceptably slow at scale.** A sequence of n union operations, each O(n),
is Theta(n^2) total — for even a modest n = 10^6, a billion operations, taking minutes to
hours where a better algorithm takes a fraction of a second. Sedgewick's point in walking
through this: quick-find is *correct* and *simple*, but "correct and simple" isn't
automatically "usable" — you need to actually reason about the cost of the sequence of
operations your application will perform, not just the cost of a single call.

### Quick-union: fixing UNION's cost by weakening FIND's simplicity
Represent the partition as a forest via a parent-pointer array `id[]`, where `id[p]` is
p's parent (a root is its own parent). FIND(p) walks up parent pointers to the root — no
longer O(1). UNION(p, q) sets the root of p's tree to point to the root of q's tree — a
single pointer change, O(1) (beyond the cost of the two FIND calls needed to locate the
roots first).

**Why this alone isn't enough.** Quick-union's UNION is fast, but nothing prevents trees
from growing tall and unbalanced — a pathological sequence of unions (always attaching a
larger tree under a smaller one, or a chain of unions in a bad order) can produce a tree
of height n, making FIND (and therefore UNION, which needs two FIND calls) cost O(n) in
the worst case — no asymptotic improvement over quick-find in the worst case, just a
different operation bearing the cost.

### Weighted quick-union: bounding tree height directly
Track each tree's **size** (number of nodes); on UNION, always attach the root of the
*smaller* tree under the root of the *larger* tree (this is exactly CLRS's "union by
rank," `clrs/18`, presented here size-based rather than rank-based, which Sedgewick notes
gives an equivalent height bound). This provably bounds every tree's height to
O(log n) — the same style of argument as before: attaching a smaller tree under a larger
one can increase the resulting tree's height by at most 1 compared to the larger tree's
prior height, and this can only happen a logarithmic number of times before a tree
would need to have grown enormously.

**Complexity:** FIND and UNION are both O(log n) worst case — already a dramatic
improvement over both prior versions for any sizable n, going from Theta(n^2) total cost
for a union-heavy sequence down to Theta(n log n).

### Adding path compression: the final optimization
On every FIND(p), after locating the root, make every node visited along the way point
**directly** to the root (Sedgewick's simplified variant, "path halving," makes each node
point to its *grandparent* instead, cutting path length roughly in half per FIND at
lower per-call overhead than full compression, with the same asymptotic payoff).
Combined with weighting, this achieves the same near-constant amortized performance CLRS
derives via the inverse Ackermann function (`clrs/18`) — Sedgewick's book states the
result (essentially constant amortized time per operation for any sequence realistic
applications would ever produce) without necessarily working through the full
inverse-Ackermann proof, favoring the empirical/engineering framing over the deepest
theoretical one.

### The methodology, stated explicitly
This progression — quick-find (correct, slow) -> quick-union (fixes one bottleneck,
introduces another) -> weighted quick-union (fixes the new bottleneck with a proven
height bound) -> plus path compression (squeezes out the remaining slack) — is presented
as a *template* for algorithm engineering generally: get something correct, identify
the actual empirical or theoretical bottleneck via profiling or complexity analysis, fix
specifically that bottleneck, and repeat. Sedgewick's book returns to this pattern
repeatedly across later chapters.

## Pros
- The union-find case study teaches a transferable engineering methodology (correct,
  then diagnose the bottleneck, then fix it) in addition to the specific algorithm.
- Weighted quick-union with path compression is simple to implement (a handful of lines,
  two small arrays) yet achieves near-constant amortized performance — a striking
  ratio of simplicity to payoff.
- Directly reusable across many applications needing connectivity queries: network
  connectivity, image processing (connected-component labeling), least-common-ancestor
  queries in certain formulations, and Kruskal's MST algorithm (`clrs/15`, `clrs/18`).

## Cons
- Supports only FIND and UNION — no set enumeration, no undo/split, and no information
  about a component beyond its identity, same narrow interface as CLRS's treatment
  (`clrs/18`).
- Quick-find and unweighted quick-union, while pedagogically valuable for the
  progression, are genuinely unusable at production scale — only the final, weighted-
  plus-path-compressed version should ever actually be deployed.
- The "is-connected" query only answers yes/no about component membership — it does not
  provide the *path* connecting the two objects, which some applications also need
  (requiring BFS/DFS instead, `clrs/13`).

## Alternatives
- **BFS/DFS graph traversal** (`clrs/13`) — needed when you require the actual connecting
  path, not just a yes/no connectivity answer, or when edges can be removed (union-find
  has no efficient support for un-merging components).
- **CLRS's rank-based union-find** (`clrs/18`) — essentially the same algorithm presented
  with a more rigorous inverse-Ackermann amortized bound; the size-based and rank-based
  variants are practically interchangeable in performance.

## When to use it
Use weighted quick-union with path compression whenever you need fast, repeated
connectivity queries over a graph or partition that only grows (unions only, never
un-merging) — the standard building block for Kruskal's MST, network connectivity
monitoring, and image/percolation-style connected-component problems.

## When NOT to use it
Don't use the naive quick-find implementation in any performance-sensitive context — its
Theta(n^2) sequence cost is a real, not just theoretical, problem at realistic input
sizes. Don't reach for union-find at all if you need the actual connecting path between
two elements, or if components need to be split apart later.

## Key takeaways / mental model
The union-find case study is as much about *how to improve an algorithm* as about the
algorithm itself: identify the actual bottleneck (quick-find's O(n) union), fix it
(quick-union's O(1) union via parent pointers), notice the new bottleneck it introduces
(unbounded tree height), fix that (weighting bounds height to O(log n)), then squeeze
further (path compression flattens future lookups). Each step targets a specific,
identified cost, not a vague general "optimization."

## Self-check questions
1. Explain precisely why quick-find's UNION requires an O(n) scan, and why this makes a
   long sequence of unions Theta(n^2) overall.
2. Walk through why unweighted quick-union alone doesn't fix the worst-case problem, even
   though its UNION operation itself is O(1) — what specifically can still go wrong?
3. Why does always attaching the smaller tree under the larger one (weighting) provably
   bound tree height to O(log n)? What would go wrong if you sometimes attached the
   larger tree under the smaller one instead?
4. Describe the engineering methodology this case study demonstrates (correct -> diagnose
   -> fix -> repeat) and apply it in the abstract to a hypothetical scenario: you have a
   working but slow sorting routine — what's the first thing you'd do before trying to
   improve it?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 1.5: "Case Study:
  Union-Find."
