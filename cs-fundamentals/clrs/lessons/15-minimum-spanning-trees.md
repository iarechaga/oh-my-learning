---
id: clrs/15
subject: clrs
title: Minimum spanning trees
slug: minimum-spanning-trees
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapter 23
prerequisites: [clrs/07, clrs/12, clrs/13, clrs/18]
created: 2026-08-10
updated: 2026-08-10
---

# Minimum spanning trees

## TL;DR
A minimum spanning tree (MST) connects all vertices of a weighted, undirected, connected
graph using the subset of edges with the least total weight and no cycles. Both classic
algorithms — Kruskal's (sort edges, greedily add if no cycle, using union-find) and
Prim's (greedily grow one connected tree, using a priority queue) — are greedy
(`clrs/12`), and both are provably correct via the same underlying fact: the **cut
property**.

## The idea
Given a set of locations that must all be connected (by cable, road, pipeline) at minimum
total cost, and given the cost of connecting every pair directly connectable, what's the
cheapest way to connect everything? The answer is always a *tree* (a spanning tree — a
connected sub-graph touching every vertex with no cycles), because any cycle in a
connecting sub-graph could have one of its edges removed while staying connected, saving
that edge's weight for free — so an optimal (minimum-cost) connecting sub-graph can never
contain a cycle. Among all possible spanning trees, the MST is the one with least total
edge weight. Remarkably, this problem — which looks like it might require examining
exponentially many possible spanning trees — is solvable by two different simple greedy
algorithms, both provably correct.

## How it works

### The cut property: why greedy works here
A **cut** of a graph is a partition of its vertices into two disjoint non-empty sets.
An edge **crosses** the cut if it has one endpoint in each set. The cut property states:
**for any cut, the minimum-weight edge crossing that cut is part of *some* MST** (as long
as ties are broken consistently, or the weights are distinct). This is the exchange-
argument-style fact (structurally similar to `clrs/12`'s greedy proofs) both algorithms
below rely on, directly or indirectly: if some candidate MST did *not* include that
lightest crossing edge, you could swap it in for whatever edge of the candidate MST does
cross the cut, strictly not increasing (and, with distinct weights, strictly decreasing)
the total weight — contradicting that candidate's optimality unless the lightest edge was
already included.

### Kruskal's algorithm
Sort all edges by weight, ascending. Process them in that order; add an edge to the
growing MST if and only if it does **not** create a cycle with edges already added (i.e.
its two endpoints are currently in different connected components of the tree built so
far). Stop once V-1 edges have been added (a spanning tree on V vertices always has
exactly V-1 edges).

**Why this is the cut property in action.** At the moment Kruskal's algorithm considers
edge (u,v) and finds u and v in different components, consider the cut separating u's
current component from everything else — (u,v) is (by the sorted processing order) the
lightest edge yet considered that crosses *some* cut separating already-connected pieces,
and can be shown to be a lightest crossing edge for the cut between u's component and the
rest — so the cut property licenses adding it.

**Implementation via union-find (`clrs/18`).** "Are u and v in different components?" and
"merge u and v's components" are exactly FIND and UNION — this is the canonical
motivating use case for union-find's design. With the near-constant-time union-find
operations, Kruskal's algorithm's complexity is dominated by the initial sort:
O(E log E), which (since E is at most V^2, so log E = O(log V)) is often written as
O(E log V).

### Prim's algorithm
Start with an arbitrary single vertex as a trivial one-vertex tree. Repeatedly find the
minimum-weight edge connecting the current tree to any vertex *not yet* in the tree, and
add that edge and vertex. Repeat until all vertices are included.

**Why this is also the cut property in action.** At every step, the cut is exactly (tree
vertices so far) vs. (everything else) — Prim's algorithm always adds the lightest edge
crossing precisely this specific cut, which the cut property guarantees is safe to add.

**Implementation via a min-priority queue (`clrs/07`)**, keyed by each not-yet-included
vertex's current minimum connection weight to the tree (updated via DECREASE-KEY as the
tree grows and discovers cheaper connections). With a binary heap: O((V+E) log V) — the
same complexity shape as Dijkstra's algorithm (`clrs/14`), because the two algorithms are
structurally very similar (both grow a structure one vertex at a time using a
priority-queue-driven greedy choice) despite optimizing for different objectives
(shortest paths from a fixed source, vs. minimum total connecting weight with no fixed
source relevance).

### Kruskal's vs. Prim's: when each wins
Kruskal's is edge-centric (sorts all edges once, globally) and is typically preferred for
**sparse** graphs, where E is small relative to V^2, since its cost (E log E) scales with
edges. Prim's is vertex-centric (grows one connected tree, always considering edges
adjacent to the current tree) and is typically preferred for **dense** graphs, where an
adjacency-matrix-based Prim's implementation (not covered in depth here, but mentioned in
CLRS) can run in O(V^2) without needing a heap at all — beating Kruskal's E log E when E
is close to V^2.

## Pros
- Both algorithms are greedy, hence simple to implement and reason about once the cut
  property is understood, and both run efficiently (near-linear or log-linear) despite
  the naive exponential-search alternative.
- The cut property is a clean, reusable proof technique — the same style of argument
  (any optimal solution can be modified to include the locally best crossing choice
  without loss) recurs across other network-design and combinatorial-optimization
  problems.
- MSTs have direct practical applications: network design (minimum-cost wiring/cabling),
  approximation algorithms for harder problems (e.g. a 2-approximation for the metric
  traveling salesman problem is built directly on an MST), and clustering (removing the
  heaviest MST edges is a simple, effective clustering heuristic).

## Cons
- Both algorithms assume an undirected, connected graph with well-defined edge weights —
  neither directly generalizes to directed graphs (the analogous problem, minimum
  spanning arborescence, needs a different algorithm entirely).
- The MST is not necessarily unique if edge weights have ties (multiple distinct MSTs can
  exist with the same total weight) — algorithms will return *a* valid MST, not
  necessarily a canonical one, unless weights are perturbed to break ties.
- An MST minimizes *total* weight, which does not imply it minimizes the weight of any
  individual path between two vertices within the tree — for shortest point-to-point
  paths, use Dijkstra's or Bellman-Ford (`clrs/14`) instead, not the MST.

## Alternatives
- **Borůvka's algorithm** — a third classic MST algorithm (each component simultaneously
  picks its own minimum-weight outgoing edge, repeated in rounds), historically the
  first MST algorithm discovered and naturally parallelizable, though less commonly
  taught than Kruskal's or Prim's.
- **Dijkstra's algorithm** (`clrs/14`) — solves a related-looking but fundamentally
  different problem (shortest paths *from a fixed source*, not minimum total connecting
  weight) — easy to confuse with Prim's due to the structural similarity of their
  implementations, but the objective functions are different and not interchangeable.
- **Steiner tree** — a harder, NP-hard generalization of MST that allows adding extra
  ("Steiner") vertices not required to be connected, potentially reducing total weight
  further than any spanning tree over the original vertex set alone.

## When to use it
Use an MST algorithm whenever you need to connect a fixed set of vertices at minimum
total edge weight with no cycles — network design, approximate solutions to certain
NP-hard problems, and simple graph-based clustering. Prefer Kruskal's for sparse graphs,
Prim's (with an adjacency matrix, for dense graphs, or a heap otherwise) for dense ones.

## When NOT to use it
Don't reach for an MST algorithm when the actual goal is shortest point-to-point paths
(use Dijkstra's or Bellman-Ford, `clrs/14`, instead) or when the graph is directed (MST
algorithms as presented assume undirected edges).

## Key takeaways / mental model
Both Kruskal's and Prim's are greedy algorithms whose correctness rests on the same cut
property: the lightest edge crossing any cut is always safe to include in some MST.
Kruskal's applies this globally (sort all edges, add if safe, checked via union-find);
Prim's applies it locally and incrementally (always extend the current tree by its
cheapest available connection, checked via a priority queue).

## Self-check questions
1. State the cut property precisely, and explain how Kruskal's algorithm's edge-sorted
   processing order guarantees it always adds an edge that is the lightest crossing some
   valid cut.
2. Why is union-find (`clrs/18`) exactly the right data structure for Kruskal's
   "would adding this edge create a cycle?" check, rather than, say, a full graph
   traversal after each candidate edge?
3. Explain the structural similarity between Prim's algorithm and Dijkstra's algorithm
   (`clrs/14`), and precisely what different quantity each one is greedily minimizing at
   each step.
4. Give a concrete small graph with a weight tie that produces two different valid MSTs
   with the same total weight, and explain why both are correct answers.

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 23: "Minimum
  Spanning Trees."
