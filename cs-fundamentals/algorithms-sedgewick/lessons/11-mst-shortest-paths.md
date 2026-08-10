---
id: algorithms-sedgewick/11
subject: algorithms-sedgewick
title: Minimum spanning trees and shortest paths
slug: mst-shortest-paths
status: drafted
mastery:
seniority: mid
source: Algorithms (Sedgewick, Wayne), Sections 4.3-4.4
prerequisites: [algorithms-sedgewick/10, algorithms-sedgewick/06, clrs/14, clrs/15]
created: 2026-08-10
updated: 2026-08-10
---

# Minimum spanning trees and shortest paths

## TL;DR
Sedgewick and Wayne implement the same MST and shortest-path algorithms CLRS proves
correct (`clrs/14`, `clrs/15`), but the implementation detail that actually matters day
to day is **edge-centric vs. vertex-centric representation** and **lazy vs. eager**
priority-queue usage — the difference between a correct-but-slower textbook version and
the version you'd actually ship.

## The idea
CLRS teaches Kruskal's and Prim's algorithms for MST, and Dijkstra's and Bellman-Ford
for shortest paths, primarily to prove their correctness (the cut property, the
relaxation invariant). Sedgewick's treatment assumes you already believe the algorithms
are correct and instead asks: what data structures make them fast and simple to
implement correctly? The answer for both MST and shortest-path algorithms turns out to
be the same **weighted edge abstraction** plus an **indexed priority queue**, applied in
two structurally similar ways — which is why this book teaches them back to back as one
unit.

## How it works

### The weighted edge abstraction
Both algorithms need a graph where edges carry weights. Sedgewick introduces an `Edge`
class (undirected, for MST) and a `DirectedEdge` class (directed, for shortest paths),
each bundling two endpoint vertices (or `from`/`to` for directed) and a `double weight`.
An `EdgeWeightedGraph` or `EdgeWeightedDigraph` then stores adjacency lists of these edge
objects rather than bare vertex numbers — the same minimal-API-plus-adjacency-iteration
pattern from `algorithms-sedgewick/10`, extended so each adjacency entry now carries a
weight alongside the neighbor.

### Prim's MST: lazy vs. eager
Prim's algorithm (also in `clrs/15`) grows a tree from one vertex, at each step adding
the minimum-weight edge crossing the cut between the tree and the rest of the graph.
Sedgewick presents two implementations that differ only in priority-queue discipline:

- **Lazy Prim's**: push *every* edge crossing the cut onto a priority queue as it's
  discovered, even if a vertex already has an edge to the tree in the queue. When
  popping, check if the popped edge's non-tree endpoint is already in the tree (if so,
  it's stale — discard and pop again). Simple to implement, but the priority queue can
  hold up to O(E) entries, most of which are eventually discarded as stale.
- **Eager Prim's**: use an **indexed priority queue** (a priority queue supporting
  `decreaseKey(vertex, newWeight)`) that holds at most one entry per non-tree vertex — its
  current best known distance to the tree. When a shorter crossing edge to a vertex is
  found, `decreaseKey` updates its entry in place instead of adding a new one. This keeps
  the priority queue at O(V) entries instead of O(E), at the cost of a more complex data
  structure (a binary heap augmented with a vertex-to-heap-position index array).

Worked example: a 4-vertex graph with edges A-B(4), A-C(1), B-C(2), B-D(5), C-D(3).
Starting from A: lazy Prim's pushes A-B(4) and A-C(1); pops A-C(1) (min), adds C to tree,
pushes C-B(2) and C-D(3) *without removing the earlier A-B(4)* — the queue now holds
A-B(4), C-B(2), C-D(3). It pops C-B(2) next (correct, since 2 < 4), adds B to tree, and
when A-B(4) is eventually popped it's discarded as stale (B already in tree). Eager
Prim's instead maintains one entry per vertex: after processing C, vertex B's entry is
`decreaseKey`'d from 4 (via A) to 2 (via C) in place — no stale duplicate is ever created.

### Kruskal's MST: union-find as the engine
Kruskal's algorithm (also in `clrs/15`) sorts all edges by weight and greedily adds each
one unless it would create a cycle. Sedgewick's implementation makes explicit what CLRS
states more abstractly: "would create a cycle" is answered in O(alpha(V)) (effectively
O(1)) time using the union-find structure from `algorithms-sedgewick/01` — `find(v) ==
find(w)` means v and w are already connected, so adding edge (v, w) would close a cycle;
otherwise `union(v, w)` merges their components. This is the same union-find structure
introduced purely for connectivity queries in lesson 01, now doing the real work inside a
full MST algorithm — a concrete payoff for having built that data structure carefully.

### Dijkstra's shortest paths: eager Prim's twin
Dijkstra's algorithm (`clrs/14`) is structurally identical to eager Prim's — same indexed
priority queue, same "settle the closest vertex, relax its edges" loop — with one
change: instead of tracking "shortest edge weight to the tree," it tracks "shortest total
distance from the source." Concretely, when vertex v is settled (removed from the
priority queue with minimum distance), for each edge v->w with weight `wt`, **relax**
means: if `distTo[v] + wt < distTo[w]`, update `distTo[w]` and `decreaseKey(w, ...)` in
the indexed priority queue. Seeing Prim's and Dijkstra's side by side, sharing the same
`IndexMinPQ` implementation, makes clear that "grow a tree by always taking the cheapest
next step" (MST) and "grow a tree by always taking the closest next vertex" (shortest
paths) are the same algorithmic skeleton solving two different optimization criteria.

### Why Dijkstra requires non-negative weights
Both this book and CLRS state the non-negative-weight requirement, but the
implementation view makes *why* concrete: once a vertex is popped from the priority queue
(settled), its `distTo[]` value is treated as final and never revisited. If a later edge
could offer a negative-weight "shortcut" to an already-settled vertex, that shortcut
would be missed entirely — the algorithm has already moved on. Bellman-Ford tolerates
negative weights precisely because it does the opposite: it relaxes *every* edge, up to
V-1 times, never treating any vertex as permanently settled until the full pass count is
exhausted.

## Pros
- The weighted-edge abstraction (`Edge`/`DirectedEdge`) cleanly extends the minimal graph
  API from lesson 10, so MST and shortest-path code reuses the same adjacency-iteration
  patterns as unweighted graph algorithms.
- Seeing lazy vs. eager Prim's side by side makes the indexed-priority-queue optimization
  concrete and motivated, rather than an abstract data-structure exercise.
- Recognizing Dijkstra's as "eager Prim's with a different relaxation rule" transfers
  understanding across both algorithms at once instead of memorizing them separately.

## Cons
- The eager implementations require an indexed priority queue (`IndexMinPQ`), a
  meaningfully more complex data structure than a plain binary heap — added
  implementation cost for a constant-factor (not asymptotic, in the comparison-based
  model) speedup over lazy Prim's.
- Kruskal's needs global edge sorting (O(E log E)) upfront, which can be wasteful if only
  a small prefix of cheap edges is ever needed to complete the tree (rare in practice, but
  a real cost on very large graphs).
- None of these implementations handle negative edge weights (Prim's and Dijkstra's are
  fundamentally reliant on non-negative weights); Bellman-Ford is required instead, at
  higher O(VE) cost.

## Alternatives
- **Bellman-Ford** (`clrs/14`) — required when edge weights can be negative; O(VE)
  instead of Dijkstra's O(E log V), and can detect negative cycles, which Dijkstra cannot
  handle at all.
- **Boruvka's algorithm** — a third classic MST algorithm (not covered in depth here)
  that grows the forest by having every component simultaneously pick its cheapest
  outgoing edge; more naturally parallelizable than Kruskal's or Prim's.
- **A\* search** — when shortest paths are needed to a single known destination (not all
  vertices) and a good heuristic distance estimate is available, A\* often explores far
  fewer vertices than Dijkstra's by directing the search toward the goal.

## When to use it
Use Prim's (eager, with an indexed priority queue) or Kruskal's for MST on graphs with
non-negative weights where you need the minimum-weight tree connecting all vertices
(network design, clustering). Use Dijkstra's for single-source shortest paths whenever
all weights are non-negative — the common case for physical distances, non-negative
costs, or hop counts.

## When NOT to use it
Don't use Dijkstra's (or eager Prim's underlying assumption) when negative edge weights
are possible — reach for Bellman-Ford instead, and check for negative cycles if the graph
allows them. Don't reach for Kruskal's global edge sort on an enormous graph where only a
small fraction of vertices need to be spanned quickly; consider Prim's, which grows
locally from a source instead of requiring a full global sort upfront.

## Key takeaways / mental model
MST and single-source shortest paths share one algorithmic skeleton — grow a tree
greedily, one vertex or edge at a time, using an indexed priority queue to always pick
the cheapest next step — differing only in what "cheapest" measures (edge weight to the
tree vs. total distance from the source). Kruskal's instead sorts all edges globally and
uses union-find to reject cycle-forming edges in near-constant time. Both MST algorithms
and Dijkstra's require non-negative weights because they treat decisions (tree
membership, settled distance) as permanent once made; negative weights break that
permanence and force the more expensive Bellman-Ford relaxation-until-convergence
approach.

## Self-check questions
1. Walk through why lazy Prim's priority queue can contain stale entries but eager
   Prim's cannot, using the worked A-B-C-D example above.
2. Explain concretely how Kruskal's algorithm uses `find`/`union` from
   `algorithms-sedgewick/01` to reject a cycle-forming edge in near-constant time.
3. Describe the exact structural correspondence between eager Prim's and Dijkstra's
   algorithm — what is identical, and what single thing differs?
4. Why does having a vertex "settled" (permanently finalized) in Dijkstra's algorithm
   break down the moment a negative edge weight is introduced?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Sections 4.3 ("Minimum
  Spanning Trees") and 4.4 ("Shortest Paths").
