---
id: clrs/13
subject: clrs
title: Graph representations, BFS, and DFS
slug: graph-representations-bfs-dfs
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapters 22-22.3
prerequisites: [clrs/05]
created: 2026-08-10
updated: 2026-08-10
---

# Graph representations, BFS, and DFS

## TL;DR
Graphs are represented as either an adjacency list (space-efficient for sparse graphs,
fast neighbor iteration) or an adjacency matrix (fast edge-existence lookup, wasteful for
sparse graphs). Breadth-first search (BFS, using a queue) explores level by level and
finds shortest paths in unweighted graphs; depth-first search (DFS, using recursion or an
explicit stack) explores as deep as possible before backtracking and reveals structural
information (cycles, topological order, connectivity) via its edge classification and
timestamps.

## The idea
A graph — vertices connected by edges — is one of the most general data models in
computer science (representing networks, dependencies, maps, relationships, state
machines). Before any graph algorithm can run, you need a concrete way to store the
graph in memory, and that choice has real performance consequences depending on how
dense or sparse the graph is. Once represented, the two fundamental traversal strategies
— BFS (explore breadth-first, level by level) and DFS (explore depth-first, as far as
possible before backtracking) — are the building blocks nearly every other graph
algorithm (shortest paths, MSTs, topological sort, strongly connected components) is
built from.

## How it works

### Representation 1: adjacency list
An array (or map) indexed by vertex, where each entry holds a list of that vertex's
neighbors. **Space:** Theta(V + E) — proportional to the number of vertices plus edges,
which is optimal for sparse graphs (E much smaller than V^2). **Checking if edge (u,v)
exists:** O(degree(u)) — must scan u's neighbor list. **Iterating all neighbors of a
vertex:** O(degree(u)), exactly proportional to what you're iterating — no wasted work.

### Representation 2: adjacency matrix
A V x V boolean (or weighted) matrix where entry (i,j) is 1 (or the edge weight) if an
edge exists from i to j. **Space:** Theta(V^2) regardless of how many edges actually
exist — wasteful for sparse graphs, reasonable for dense ones (E close to V^2).
**Checking if edge (u,v) exists:** O(1) — direct array lookup, the matrix's key
advantage. **Iterating all neighbors of a vertex:** O(V) — must scan the entire row, even
if the vertex has very few actual neighbors, which is wasteful for sparse graphs.

**The core trade-off, stated plainly:** adjacency lists are the default choice for most
real-world graphs (social networks, road networks, dependency graphs), which are
overwhelmingly sparse (E = O(V), not O(V^2)); adjacency matrices win specifically when
the graph is dense, or when O(1) edge-existence queries are the dominant operation
(e.g. repeatedly asking "are these two specific vertices connected by a direct edge?").

### Breadth-first search (BFS)
Given a source vertex s, BFS discovers every vertex reachable from s, and — critically —
discovers them in order of increasing distance (number of edges) from s. Mechanism: start
with s in a queue (`clrs/05`), colored "discovered." Repeatedly dequeue a vertex u,
examine all its neighbors; for each undiscovered neighbor v, mark it discovered, record
its distance as (u's distance + 1) and its predecessor as u, and enqueue it. This
processes vertices in exactly the order they were discovered (FIFO), which is precisely
why it explores level by level: all distance-1 vertices are enqueued (and will be
dequeued) before any distance-2 vertex is discovered, since a distance-2 vertex can only
be discovered via a distance-1 vertex's dequeue.

**Why BFS finds shortest paths (in an unweighted graph).** Because vertices are
processed in non-decreasing order of discovery distance, the *first* time any vertex is
discovered, it's discovered via a shortest possible path — a later-discovered path to the
same vertex, coming from a vertex at distance d, can only be d+1 or more, never shorter
than an earlier discovery. This gives BFS its signature use case: shortest paths measured
in *edge count* (not weighted distance — that needs Dijkstra's algorithm, `clrs/14`).

**Complexity:** Theta(V + E) with an adjacency list — every vertex is enqueued/dequeued
once (Theta(V)), and every edge is examined exactly once or twice depending on
directedness when scanning neighbor lists (Theta(E)).

### Depth-first search (DFS)
DFS explores as far as possible along each branch before backtracking. Mechanism (usually
implemented recursively, or with an explicit stack for very deep graphs to avoid
recursion-depth limits): from the current vertex u, pick an unvisited neighbor v, recurse
into v immediately (going deeper), and only return to consider u's other neighbors once
v's entire reachable subtree has been fully explored.

**Timestamps.** DFS records two timestamps per vertex: **discovery time** (when it's
first visited) and **finish time** (when its entire subtree of unvisited-at-the-time
descendants has been fully explored and DFS is about to backtrack past it). These
timestamps have a clean **parenthesis structure**: for any two vertices u and v, their
discovery/finish intervals are either completely nested (one is a descendant of the
other in the DFS tree) or completely disjoint (neither is a descendant of the other) —
they can never partially overlap. This structural fact underlies several DFS-based
algorithms.

**Edge classification.** As DFS runs, every edge encountered falls into exactly one of
four categories: **tree edges** (edges actually used to discover a new vertex — these
form the DFS forest), **back edges** (an edge to an ancestor still being processed — the
presence of *any* back edge in a directed graph proves the graph has a cycle, which is
the standard DFS-based cycle-detection technique), **forward edges** (an edge to an
already-finished descendant, possible only in directed graphs), and **cross edges** (an
edge to a vertex in a different DFS subtree entirely, also only in directed graphs).

**Complexity:** Theta(V + E), for the same reason as BFS — every vertex is visited once,
every edge examined once (or twice, undirected).

### BFS vs. DFS: when each structural property matters
| Property | BFS | DFS |
| --- | --- | --- |
| Finds shortest path (unweighted, edge count) | Yes | No |
| Natural data structure | Queue | Stack (or recursion) |
| Reveals cycles | Possible but awkward | Natural (back edges) |
| Basis for topological sort | No | Yes (`algorithms-sedgewick/12`) |
| Memory pattern | Can need O(V) queue width (a wide "frontier") | O(depth) stack, often
much less than O(V) for a shallow, wide graph |

## Pros
- Adjacency lists give near-optimal Theta(V+E) space and traversal cost for the sparse
  graphs that dominate real-world applications.
- BFS and DFS together, at Theta(V+E) each, are the cheapest possible traversal (you
  cannot explore a graph in less than the time it takes to look at every vertex and
  edge) and form the foundation nearly every other graph algorithm builds on.
- DFS's timestamp and edge-classification machinery gives structural information (cycle
  detection, topological ordering) essentially "for free" as a byproduct of the traversal
  itself, without a separate pass.

## Cons
- Adjacency matrices waste Theta(V^2) space on sparse graphs, and neighbor iteration
  costs O(V) regardless of actual degree — a poor choice for the common sparse case.
- BFS's queue can hold up to O(V) vertices at its widest point (a graph with a very wide,
  shallow structure), which can be a real memory concern for enormous graphs even though
  the *total* work is still Theta(V+E).
- Naive recursive DFS on a very deep, narrow graph (e.g. a long chain) can hit the call
  stack's recursion-depth limit — production implementations of DFS on graphs of unknown
  or potentially large depth often use an explicit stack instead of language-level
  recursion.

## Alternatives
- **Iterative deepening DFS** — bounds DFS's depth and increases the bound iteratively,
  combining DFS's low memory footprint with BFS's shortest-path guarantee, at the cost of
  revisiting shallow parts of the graph multiple times; more common in AI search contexts
  than general graph algorithms.
- **Bidirectional BFS** — runs BFS simultaneously from both the source and target,
  meeting in the middle; can dramatically reduce the explored frontier size for
  shortest-path queries between two specific known vertices, at the cost of more complex
  bookkeeping.
- **Union-find** (`clrs/18`) — for pure connectivity queries ("are u and v in the same
  component?") without needing full path or distance information, union-find can answer
  faster than a full traversal, especially under incremental edge additions.

## When to use it
Use an adjacency list by default for any graph that isn't known to be dense. Use BFS
whenever you need shortest paths by edge count, or need to process a graph level by
level (e.g. finding all nodes within k hops). Use DFS whenever you need structural
information (cycle detection, topological order, connected/strongly connected
components) or when memory (not shortest paths) is the binding constraint.

## When NOT to use it
Don't use an adjacency matrix for large sparse graphs (social networks, road networks) —
the Theta(V^2) space cost becomes prohibitive well before V reaches even modest sizes.
Don't use plain BFS or DFS when edges have weights and you need shortest *weighted*
distance, not just fewest edges — that requires Dijkstra's or Bellman-Ford (`clrs/14`)
instead.

## Key takeaways / mental model
Adjacency list vs. matrix is a sparse-vs-dense, iteration-vs-lookup trade-off. BFS's
queue (FIFO) naturally processes vertices in non-decreasing distance order, which is
exactly why it finds shortest unweighted paths; DFS's stack-like (LIFO) behavior
naturally produces the nested discovery/finish timestamp structure that reveals cycles
and orderings. Both are Theta(V+E) — the theoretical floor for any algorithm that must
look at every vertex and edge at least once.

## Self-check questions
1. Explain precisely why BFS guarantees the *first* discovery of any vertex is via a
   shortest path, using the FIFO property of its queue.
2. Why does a back edge in a directed graph's DFS prove the graph has a cycle, while a
   forward or cross edge does not?
3. For a graph with V=1,000,000 vertices and E=2,000,000 edges, compare the memory cost
   of an adjacency list vs. an adjacency matrix representation, and explain why the
   matrix would be impractical here.
4. Give an example where DFS's O(depth) memory usage is a meaningful advantage over BFS's
   potential O(V) queue width, and one where the reverse is true.

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 22:
  "Elementary Graph Algorithms," sections 22.1-22.3.
