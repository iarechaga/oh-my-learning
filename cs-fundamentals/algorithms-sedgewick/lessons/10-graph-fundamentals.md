---
id: algorithms-sedgewick/10
subject: algorithms-sedgewick
title: Undirected and directed graph fundamentals
slug: graph-fundamentals
status: drafted
mastery:
seniority: mid
source: Algorithms (Sedgewick, Wayne), Sections 4.1-4.2
prerequisites: [algorithms-sedgewick/09, clrs/13]
created: 2026-08-10
updated: 2026-08-10
---

# Undirected and directed graph fundamentals

## TL;DR
Sedgewick and Wayne build graph algorithms around a small, reusable **API design
pattern**: a `Graph` (or `Digraph`) data type exposing only vertex/edge counts and
adjacency iteration, with every higher-level algorithm (connectivity, cycle detection,
DFS/BFS-based processing) implemented as a **separate client class** that takes a graph
in its constructor and preprocesses it — a design that cleanly separates the graph
representation from the (many, varied) things you might want to compute about it.

## The idea
CLRS covers graph representations and BFS/DFS as algorithms (`clrs/13`). Sedgewick adds
a software-design layer on top: rather than writing BFS or connected-components logic as
a free function that takes a graph and returns an answer, structure each graph algorithm
as its **own class** — e.g. a `ConnectedComponents` class whose constructor runs the
necessary traversal once and stores the results, exposing simple query methods (like
`connected(v, w)` or `count()`) afterward. This "preprocess in the constructor, query
cheaply afterward" pattern recurs across nearly every graph algorithm in the book and is
worth understanding as a design pattern in its own right, not just as an implementation
detail specific to any one algorithm.

## How it works

### The Graph API: minimal by design
A `Graph` object supports only: `V()` (vertex count), `E()` (edge count), `addEdge(v,w)`,
and `adj(v)` (an iterable of v's neighbors) — deliberately minimal, exposing nothing
about how neighbors are stored internally (adjacency list vs. some other structure).
Every algorithm operating on the graph is written entirely in terms of these four
operations, which means the *same* algorithm code works unchanged regardless of the
underlying representation, as long as it implements this interface — a direct application
of designing to an interface rather than an implementation.

### The "constructor does the work" client pattern
A typical client class (e.g. `DepthFirstPaths`, which finds all paths from a given
source vertex) takes a `Graph` and a source vertex `s` in its constructor, immediately
runs a full DFS from `s`, and stores the results (a `marked[]` boolean array recording
reachability, and an `edgeTo[]` array recording the DFS tree's parent pointers) as
instance fields. After construction, cheap query methods (`hasPathTo(v)`,
`pathTo(v)`) simply read from these precomputed arrays — O(1) or O(path length), not
requiring a fresh traversal per query. **This pattern trades a single upfront O(V+E)
preprocessing cost for arbitrarily many cheap subsequent queries** — the right trade-off
whenever a graph is queried many times relative to how often it changes, which describes
most real applications (a road network is built once and queried millions of times for
routing).

### Undirected graph algorithms via this pattern
- **`DepthFirstSearch` / `DepthFirstPaths`** — reachability and path-finding from a
  source, via DFS (`clrs/13`), stored as `marked[]`/`edgeTo[]`.
- **`BreadthFirstPaths`** — same interface, but using BFS instead of DFS, which
  additionally guarantees the stored paths are **shortest** (fewest edges) — directly
  reusing CLRS's BFS shortest-path property (`clrs/13`) inside this client-class
  structure.
- **`CC` (connected components)** — runs DFS from every not-yet-visited vertex,
  assigning each a component ID; afterward, `connected(v, w)` is simply
  `id[v] == id[w]`, O(1), and `count()` returns the total number of components — all
  derived from one O(V+E) preprocessing pass.
- **`Cycle`** — detects whether an undirected graph has a cycle by running DFS and
  checking, for each non-tree edge encountered, whether it connects to an already-visited
  vertex that isn't the current vertex's immediate DFS-tree parent (a subtlety specific to
  undirected graphs: the edge *back* to your own parent is not a cycle, since it's the
  same edge traversed in the other direction, not a new connection).

### Directed graph algorithms: what changes
A `Digraph` has the same minimal API, but `adj(v)` now returns only *outgoing* edges from
v (an asymmetry undirected graphs don't have) — this single representational difference
cascades into meaningfully different algorithms:
- **Reachability is no longer symmetric** — u being reachable from v does not imply v is
  reachable from u, unlike the undirected case, which fundamentally changes what
  "connectivity" even means (motivating strongly-connected-components as the directed
  analogue, `algorithm-design/07`).
- **Cycle detection differs**: a directed cycle requires finding a **back edge** during
  DFS (an edge to a vertex currently on the active recursion path, not just any
  previously-visited vertex) — exactly CLRS's back-edge classification (`clrs/13`)
  applied here as the mechanism for `DirectedCycle`.
- **Topological sort** (covered in depth in `algorithms-sedgewick/12`) only makes sense
  for directed acyclic graphs and has no undirected analogue at all.
- **Transitive closure** (is there *any* directed path from v to w, for every pair v, w?)
  is a directed-graph-specific query with no natural undirected equivalent (since
  undirected reachability is already fully captured by connected components).

## Pros
- The minimal `Graph`/`Digraph` API plus "preprocess in constructor, query cheaply
  afterward" client pattern cleanly separates representation from algorithm, letting the
  same algorithm code work across different underlying graph representations.
- Structuring each algorithm as its own class with precomputed results makes repeated
  queries (common in real applications) cheap after a single upfront traversal cost,
  rather than repeating O(V+E) work per query.
- Explicitly contrasting undirected and directed graph algorithms side by side clarifies
  exactly which properties (symmetric reachability, back-edge cycle detection) depend on
  edge direction and which don't.

## Cons
- The "preprocess everything in the constructor" pattern assumes the graph doesn't change
  after construction — a dynamically changing graph (edges added/removed over time)
  requires either re-running the full preprocessing (expensive) or a fundamentally
  different incremental/dynamic algorithm design.
- Precomputing and storing full `marked[]`/`edgeTo[]` arrays costs O(V) space per client
  object, even if only a few queries are ever actually made — wasteful for a graph
  queried rarely or for only a small subset of vertices.
- The minimal API's simplicity (just `V()`, `E()`, `addEdge`, `adj`) means any algorithm
  needing additional graph properties (edge weights, for instance) requires an extended
  API (`EdgeWeightedGraph`, covered alongside MST/shortest-path algorithms) rather than
  fitting the base `Graph` type directly.

## Alternatives
- **CLRS's function-based graph algorithms** (`clrs/13`) — the same underlying algorithms
  (BFS, DFS) presented as procedures operating on a graph representation directly, without
  the object-oriented "preprocess once, query many times" client-class structuring;
  functionally equivalent, differently organized.
- **On-the-fly (no preprocessing) queries** — appropriate when a graph is queried only
  once or very rarely, where the upfront preprocessing cost of a client class isn't
  justified.
- **Dynamic/incremental graph algorithms** — needed when the graph changes frequently
  and re-running full preprocessing after every change is too expensive.

## When to use it
Use the minimal-API-plus-preprocessing-client pattern whenever a graph is built once (or
rarely modified) and queried many times — the standard situation for connectivity
checks, pathfinding, and cycle detection in most real applications (network analysis,
routing, dependency resolution).

## When NOT to use it
Don't use this pattern for a graph that changes frequently relative to how often it's
queried — the upfront preprocessing cost would be wasted or require expensive
re-computation after every change; consider a dynamic/incremental algorithm instead. Don't
conflate undirected and directed graph algorithms — reachability, cycle detection, and
connectivity all behave meaningfully differently once edges have direction.

## Key takeaways / mental model
A minimal graph API (vertex/edge counts, adjacency iteration) lets every algorithm be
written once against an interface, independent of the underlying representation.
Structuring each algorithm as a class that preprocesses in its constructor and answers
queries cheaply afterward trades one upfront traversal for many cheap subsequent
queries — the right trade-off whenever a graph is built once and queried often. Directed
edges break reachability's symmetry, which cascades into different algorithms for
connectivity, cycles, and ordering compared to the undirected case.

## Self-check questions
1. Explain the "preprocess in the constructor, query cheaply afterward" pattern using
   `BreadthFirstPaths` as an example — what's precomputed, and what does a `pathTo(v)`
   query cost after that preprocessing?
2. Why does undirected cycle detection need to specifically exclude the edge back to a
   vertex's immediate DFS parent, while directed cycle detection's back-edge check needs
   no equivalent exclusion?
3. Give a concrete example (e.g. a one-way street network) where reachability being
   asymmetric in a directed graph has a real practical consequence that wouldn't arise in
   an undirected graph.
4. Why would the "preprocess everything upfront" client-class pattern be a poor fit for a
   graph that changes (edges added/removed) on every single query?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Sections 4.1 ("Undirected
  Graphs") and 4.2 ("Directed Graphs").
