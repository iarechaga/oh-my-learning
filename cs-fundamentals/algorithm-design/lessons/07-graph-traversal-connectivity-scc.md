---
id: algorithm-design/07
subject: algorithm-design
title: Graph traversal, connectivity, and strongly connected components
slug: graph-traversal-connectivity-scc
status: drafted
mastery:
seniority: mid
source: Algorithm Design (Kleinberg & Tardos), Chapter 3
prerequisites: [algorithm-design/02, clrs/13]
created: 2026-08-10
updated: 2026-08-10
---

# Graph traversal, connectivity, and strongly connected components

## TL;DR
BFS and DFS both traverse a graph in O(n+m), but the *order* they visit vertices in
carries provably different structural information: BFS discovers vertices in
distance-from-source order (giving true shortest paths in unweighted graphs), while DFS's
recursive structure classifies edges into types (tree, back, forward, cross) that directly
expose cycles, and — the highlight of this lesson — DFS finishing times are the basis for
computing **strongly connected components (SCCs)**, the directed-graph analogue of
connected components, in a second linear-time pass.

## The idea
`clrs/13` establishes BFS and DFS as the two fundamental graph traversal strategies and
proves each runs in O(n+m). This book's chapter 3 pushes further into what each
traversal's *byproducts* reveal about graph structure: BFS's layered discovery order
proves shortest paths in unweighted graphs; DFS's edge classification during traversal
(especially back edges) is what makes cycle detection and, in directed graphs, SCC
computation possible. Connectivity itself is simple in undirected graphs (two vertices are
connected if a path exists between them — a single traversal from any vertex finds its
whole component); it becomes genuinely subtler in *directed* graphs, where reachability
isn't symmetric, motivating the separate, more intricate notion of strong connectivity.

## How it works

### BFS: layered discovery and shortest paths
BFS explores a graph in layers: from source s, layer 0 = {s}, layer 1 = all neighbors of
s, layer 2 = all unvisited neighbors of layer-1 vertices, and so on, using a queue.
**Key structural fact**: layer i contains exactly the vertices whose shortest path
(fewest edges) from s has length i — this isn't incidental, it's provable by induction on
i (every vertex in layer i+1 is adjacent to some layer-i vertex by construction, so its
shortest distance is at most i+1; and it can't be less, or BFS would have discovered it in
an earlier layer). This is why BFS, not DFS, is the correct traversal for unweighted
shortest paths — DFS's discovery order carries no such distance guarantee.

### Undirected connectivity: connected components in one pass
In an undirected graph, run BFS or DFS from an arbitrary unvisited vertex; every vertex it
reaches forms one connected component. Repeat from any remaining unvisited vertex for the
next component. Total cost across all components: O(n+m), since each vertex and edge is
examined a constant number of times overall. This is the simple case — the "which vertices
can reach which" relation is inherently symmetric in undirected graphs (an edge lets you
go either way), so "connected to" is an equivalence relation and components partition the
vertex set cleanly.

### DFS: edge classification and cycle detection
DFS explores as deep as possible before backtracking, using recursion (or an explicit
stack). Every edge encountered during a DFS falls into one of four categories:
- **Tree edge**: leads to an undiscovered vertex (becomes part of the DFS tree).
- **Back edge**: leads to an ancestor still on the current recursion stack — this is
  exactly what signals a cycle (see `algorithms-sedgewick/12` for the `onStack[]`
  mechanism in directed graphs).
- **Forward edge**: leads to a already-finished descendant (directed graphs only).
- **Cross edge**: leads to a vertex in an already-fully-explored, unrelated part of the
  tree (directed graphs only; undirected DFS never produces forward or cross edges,
  because any edge to an already-visited non-ancestor vertex in an undirected graph is
  provably a back edge instead — a fact worth knowing since it simplifies undirected DFS
  reasoning).

A graph has a cycle if and only if a DFS from any vertex encounters at least one back
edge — this is the mechanism `algorithms-sedgewick/12` builds on for topological sort's
prerequisite cycle check.

### Directed reachability is not symmetric — why strong connectivity needs its own
definition
In a directed graph, u being able to reach v says nothing about whether v can reach u.
Two vertices are **strongly connected** if each can reach the other (a two-way
reachability requirement). This is again an equivalence relation (reflexive, symmetric by
definition, transitive), so it partitions the vertex set into **strongly connected
components (SCCs)** — but computing them is genuinely harder than undirected components,
because a single DFS from one vertex only finds what's *reachable from* it, not what can
*reach back to* it.

### Computing SCCs: Kosaraju's algorithm
1. Run DFS on the original graph G, recording each vertex's **finishing time** (same
   postorder concept as `algorithms-sedgewick/12`'s topological sort).
2. Compute G^T, the **transpose** graph (reverse every edge).
3. Run DFS on G^T, but process vertices **in decreasing order of finishing time** from
   step 1 (i.e., start from whichever unvisited vertex finished *last* in step 1). Each
   resulting DFS tree in this second pass is exactly one SCC.

**Why this works (intuition):** a vertex that finishes last in step 1's DFS is, roughly,
one that sits "upstream" in the SCC structure (nothing else in a later-processed SCC could
reach it without also being explored earlier). Running DFS on the *transpose* graph
starting from such a vertex can only reach vertices that were, in the original graph,
reachable *from* SCCs no earlier in finishing-time order — combined with the property that
mutual reachability is exactly what SCC membership requires, this two-pass structure
correctly isolates one SCC per DFS-tree in the second pass. (The full inductive proof is
more involved; the practical takeaway is the two-pass "DFS, transpose, DFS again by
decreasing finish time" recipe, which runs in O(n+m) total — two linear passes plus
building the transpose.)

**Worked example.** Directed graph: A->B, B->C, C->A (a 3-cycle: A,B,C form one SCC),
plus C->D, D->E, E->D (D,E form a second SCC), so overall SCCs are {A,B,C} and {D,E}.
Step 1 DFS from A: visit A, B, C (C->A already visited, skip; C->D), D, E (E->D already
visited, skip), E finishes first, D finishes, C finishes, B finishes, A finishes.
Finishing order (increasing): E, D, C, B, A. Step 2: transpose G^T has edges B->A, C->B,
A->C, D->C, E->D, D->E. Process in decreasing finish-time order: A first (last finished in
step 1). DFS from A in G^T: A->C->B->A (all reachable, all already-visited eventually) —
this DFS tree covers {A, B, C}, exactly one SCC. Continue to next unvisited vertex in
decreasing finish order: D. DFS from D in G^T: D->C (already visited, skip), D->E->D
(already visited) — this tree covers {D, E}, the second SCC. Matches the expected {A,B,C}
and {D,E}.

### Condensing SCCs into a DAG
Once SCCs are identified, contracting each SCC into a single "super-vertex" always
produces a genuine DAG (no cycles possible between SCCs — if two SCCs had a cycle between
them they'd actually be the same SCC by definition). This is exactly the technique
`algorithms-sedgewick/12` references for topologically ordering a graph that might have
cycles: condense to SCCs first, then topologically sort the resulting DAG.

## Pros
- Both traversals run in O(n+m), and SCC computation adds only a constant factor (two
  full traversals plus a transpose) — genuinely efficient for graphs of any practical size.
- SCC decomposition reveals real structural information used directly in practice:
  detecting circular dependencies (build systems, package managers), finding mutually
  reachable clusters in web graphs or social networks, and simplifying a cyclic graph into
  a DAG for further processing (topological sort, DP over the condensation).
- The edge-classification framework (tree/back/forward/cross) generalizes cleanly and is
  the same conceptual tool used for cycle detection, SCC computation, and (in
  `algorithms-sedgewick/12`) topological sort.

## Cons
- Kosaraju's algorithm requires building the transpose graph explicitly (or maintaining
  reverse adjacency lists), an extra O(n+m) space/time cost some implementations try to
  avoid via alternative single-pass algorithms (Tarjan's SCC algorithm) at the cost of more
  intricate bookkeeping (a low-link array).
- SCC computation is meaningful only for directed graphs; applying it (or reasoning about
  it) on an undirected graph is a category error — undirected connectivity is already the
  simpler, single-pass notion.
- The "why it works" proof for Kosaraju's algorithm is genuinely non-obvious (unlike
  undirected connected components' simple single-traversal argument) — treating the
  two-pass recipe as "just works" without understanding the finishing-time argument leaves
  a gap in the same proof-first discipline this subject otherwise insists on.

## Alternatives
- **Tarjan's SCC algorithm** — computes SCCs in a single DFS pass using a low-link value
  per vertex, avoiding the need to build a transpose graph; more space-efficient but the
  low-link invariant is more intricate to implement correctly than Kosaraju's two-pass
  recipe.
- **Union-find** (`algorithms-sedgewick/01`) — the right tool for *undirected* connected
  components when queries are interleaved with edge insertions (incremental connectivity),
  rather than a one-shot traversal.
- **Path-based (Gabow's) SCC algorithm** — another single-pass alternative to Kosaraju's,
  using two auxiliary stacks instead of low-link values.

## When to use it
Use plain BFS/DFS traversal for undirected connectivity or unweighted shortest paths. Use
SCC computation (Kosaraju's or an alternative) whenever you need to find mutually-reachable
clusters in a directed graph — detecting circular dependencies, condensing a cyclic graph
into a DAG before further processing, or analyzing directed-graph structure like web link
graphs or state machines.

## When NOT to use it
Don't use SCC machinery on an undirected graph — undirected connected components are
strictly simpler (a single traversal per component, no transpose, no finishing-time
bookkeeping) and SCC's added complexity buys nothing there. Don't use BFS when you need
DFS's edge-classification information (cycle detection, SCCs, topological order) — BFS's
layered structure doesn't expose the same back-edge information DFS does. See
`algorithms-sedgewick/12` for the directed-acyclic-graph-specific follow-on: once you have
a genuine DAG (either because the graph was acyclic to begin with, or because you
condensed SCCs into a DAG here), topological sort via reverse DFS postorder is the next
step.

## Key takeaways / mental model
BFS's layered order gives unweighted shortest paths; DFS's recursive structure and edge
classification (especially back edges) expose cycles and, via the two-pass
DFS-then-transpose-DFS recipe (Kosaraju's algorithm), strongly connected components in
directed graphs. Undirected connectivity is simple (one traversal per component);
directed strong connectivity is genuinely harder because reachability isn't symmetric, and
needs the two-pass structure specifically because a single DFS only sees "reachable from,"
never "can reach back to."

## Self-check questions
1. Explain why BFS, not DFS, is the correct choice for computing shortest paths in an
   unweighted graph — what invariant does BFS's layer structure guarantee that DFS's
   discovery order does not?
2. Why does an undirected graph's DFS never produce forward or cross edges, only tree and
   back edges? (Hint: think about what a "forward" or "cross" edge would imply about an
   edge you've already traversed in the other direction.)
3. Walk through, in your own words, why processing vertices in decreasing finishing-time
   order (from the first DFS pass) on the transpose graph correctly isolates one SCC per
   resulting DFS tree.
4. A colleague has a directed graph representing microservice call dependencies and wants
   to detect "circular dependency" issues. Explain how SCC computation answers this, and
   what condensing SCCs into a DAG would let them do next.

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 3: "Graphs."
