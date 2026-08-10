---
id: algorithm-design/09
subject: algorithm-design
title: Reductions and NP-completeness proofs
slug: reductions-np-completeness
status: drafted
mastery:
seniority: senior
source: Algorithm Design (Kleinberg & Tardos), Chapter 8
prerequisites: [algorithm-design/07, algorithm-design/08, clrs/19]
created: 2026-08-10
updated: 2026-08-10
---

# Reductions and NP-completeness proofs

## TL;DR
This lesson treats the polynomial-time reduction as a general design tool with **two
opposite uses** — transferring *tractability* (solve a new problem by reducing it to a
known-solvable one, as in `algorithm-design/08`'s max-flow reductions) and transferring
*hardness* (prove a new problem NP-complete by reducing a known-hard problem into it) —
and works through a chain of six classic reduction proofs to build fluency in constructing
the hardness direction specifically, complementing CLRS's more theorem-and-definition-first
treatment (`clrs/19`).

## The idea
`clrs/19` establishes what NP, NP-hard, and NP-complete mean and proves the concept
sound via Cook-Levin. This book's chapter 8 treats that machinery as settled and spends
its effort on the *craft* of constructing reductions — because in practice, proving a new
problem NP-complete is a hands-on construction task, not a citation. The recurring insight
this lesson emphasizes: the *same* tool (polynomial-time reduction) that lets you solve a
new problem by encoding it as a known-solvable one (bipartite matching -> max flow,
`algorithm-design/08`) also lets you prove a new problem is *hard* by encoding a
known-hard problem into it — direction of encoding is what flips "this helps me solve it"
into "this proves I probably can't."

## How it works

### The reduction chain: six classic problems
This book builds intuition through a specific, teachable chain of reductions, each
illustrating a different reduction *style*. Once you've internalized this chain, you have
a working template for constructing new reductions rather than starting from scratch each
time.

**1. 3-SAT is NP-complete** (given, via Cook-Levin, as covered in `clrs/19` — the anchor
every other reduction in the chain ultimately traces back to).

**2. 3-SAT reduces to Independent Set.** Given a 3-SAT formula with k clauses (each with 3
literals), build a graph: one vertex per literal occurrence (3k vertices total), connect
the 3 vertices within each clause to each other (forming a triangle, so at most one per
clause can be chosen in an independent set), and connect every pair of vertices
representing a variable and its negation (so a satisfying assignment can't pick both).
Claim: the formula is satisfiable if and only if this graph has an independent set of size
k. **Why:** an independent set of size k must pick exactly one vertex per clause-triangle
(no two from the same triangle are independent) and can't pick both a variable and its
negation (connected) — this directly corresponds to a consistent, satisfying literal
choice per clause. This is a **local gadget reduction**: each clause becomes a small,
reusable structural piece (a gadget) whose combinatorics mirror the logical structure
being encoded.

**3. Independent Set reduces to Vertex Cover.** As covered in `clrs/19`: a graph has an
independent set of size k if and only if it has a vertex cover of size (V - k) — the
complement relationship. This is the simplest reduction style: near-trivial, O(1) beyond
copying the graph, because the two problems are complements of each other by definition.

**4. Independent Set reduces to Clique.** A set of vertices is independent in G if and
only if it's a clique in G's complement graph (Ḡ, formed by flipping every edge/non-edge).
Build Ḡ from G in O(V^2), then an independent set of size k in G corresponds exactly to a
clique of size k in Ḡ. Another **complement-graph-style** reduction — structurally similar
to reduction 3 but operating on the *edge set* rather than the *vertex selection*.

**5. 3-SAT reduces to Graph Coloring (3-colorability).** A more intricate gadget
construction: build gadgets representing "true/false/base" triangles per variable and
clause-checking gadgets that can only be validly 3-colored if at least one literal in the
clause is satisfied by the corresponding variable-gadget's coloring. This reduction is
included specifically because it's harder to see than the others — it demonstrates that
gadget reductions can require real creative construction, not just a mechanical
complement or subset relationship.

**6. Hamiltonian Cycle and its reduction chain into Traveling Salesman.** A Hamiltonian
cycle (visiting every vertex exactly once, returning to start) existing is NP-complete
(reducible from 3-SAT via a further gadget construction covered in the book but not
detailed here); TSP (find the minimum-cost Hamiltonian cycle) is at least as hard, shown by
a **decision-version reduction**: set all given edges to cost 1 and all non-edges to cost
2 (or infinity, in variants); a Hamiltonian cycle exists in the original graph if and only
if the minimum TSP tour costs exactly n (uses only cost-1 edges). This illustrates
reducing an *optimization* problem's hardness from a *decision* problem's hardness — a
distinct reduction shape from the earlier structural gadget style.

### The reduction proof template, made explicit
Every reduction proof in this chain follows the same three-part shape (this is the
practical procedure to internalize):
1. **Construction**: describe, algorithmically and in polynomial time, how to transform
   any instance of the known-hard problem A into an instance of the new problem B.
2. **Forward direction**: if the A-instance is a "yes" instance, prove the constructed
   B-instance is also "yes" (exhibit how a solution to A maps to a solution to B).
3. **Backward direction**: if the constructed B-instance is a "yes" instance, prove the
   original A-instance must also be "yes" (the harder direction to get right — a common
   bug is a construction that's "yes implies yes" but not the converse, which would make
   B look easier than it actually is and invalidate the hardness claim).

Skipping the backward direction is the single most common error in student-constructed
reduction proofs — a reduction that only proves "A yes -> B yes" doesn't establish
B is at least as hard as A; both directions of the if-and-only-if are required.

### Reduction direction discipline
A subtlety worth stating explicitly because it's a common source of confusion: to prove B
is NP-hard, you reduce a *known-hard* problem A **into** B (construct a B-instance from an
A-instance) — not the other way around. Reducing B into a known-easy problem would prove
the *opposite* (that B is easy), which is not the goal. Getting the direction backward is
a conceptual error distinct from, but often confused with, the "reduces to" vs. "reduces
from" naming convention itself, which varies confusingly across textbooks — always anchor
on the logical content ("if I could solve X, could I now solve Y") rather than memorizing
directional phrasing.

## Pros
- A worked chain of six reductions, each illustrating a different construction style
  (complement graph, local gadget, decision-to-optimization), gives a genuine repertoire
  of reduction *patterns* to recognize and reuse, not just one memorized example.
- Fluency in constructing reductions transfers directly to recognizing when a new,
  unfamiliar problem resembles a known NP-complete one, often before attempting a full
  formal proof.
- The same reduction skill used for hardness proofs is symmetric with the tractability-
  transferring reductions in `algorithm-design/08` — one skill, two directions of use.

## Cons
- Gadget-style reductions (like 3-SAT to graph coloring) require genuine creative
  construction with no fully mechanical procedure — this is a real, non-trivial skill gap
  between "understanding what NP-completeness means" and "being able to prove a new
  problem NP-complete."
- A reduction proof with a correct construction but a missing or flawed backward-direction
  argument is a common, subtle error that produces an invalid hardness claim while looking
  complete.
- Building intuition via this specific chain (3-SAT through TSP) doesn't automatically
  transfer to constructing a reduction for a genuinely novel problem shape outside this
  chain's patterns — real fluency needs practice beyond memorizing these six proofs.

## Alternatives
- **Direct proof from Cook-Levin** — theoretically always possible (reduce straight from
  SAT/3-SAT) but usually far more work than reducing from a problem closer in structure to
  the new one (e.g. reducing from vertex cover or independent set when your new problem
  has a similar "select a subset" shape).
- **Approximation algorithms** (`algorithm-design/10`) — once NP-completeness is
  established (or strongly suspected), the practical next step rather than continuing to
  search for exact algorithms.
- **Parameterized complexity / fixed-parameter tractability** — for problems that are
  NP-complete in general but tractable when some specific parameter (not just overall
  input size) is small; a more specialized alternative to direct approximation.

## When to use it
Construct a reduction proof whenever you've designed several algorithms for a new
combinatorial problem and all have failed, especially if the problem resembles a known
NP-complete problem's shape (selection subject to pairwise constraints, satisfiability-like
structure, or tour/cycle construction) — pick the closest-shaped known-hard problem to
reduce from, rather than starting from SAT directly.

## When NOT to use it
Don't attempt a reduction proof as a first step before trying to find an efficient
algorithm at all — many problems that superficially resemble a known-hard problem have a
crucial structural difference (e.g. restricted graph classes, small parameter bounds) that
actually makes them tractable; confirm no polynomial algorithm is findable in the general
case before investing in a hardness proof. Don't submit a reduction proof missing the
backward direction — it doesn't establish what it claims to.

## Key takeaways / mental model
A polynomial-time reduction is a two-way tool: encode a new problem in terms of a
known-*solvable* one to solve it (`algorithm-design/08`), or encode a known-*hard* problem
in terms of a new one to prove the new one hard. Constructing a hardness reduction always
needs three parts — a polynomial-time construction, and both directions of the "yes
instance maps to yes instance" argument — and a repertoire of construction styles
(complement graphs, local gadgets, decision-to-optimization) transfers across problems far
better than memorizing individual proofs.

## Self-check questions
1. Walk through the 3-SAT-to-independent-set gadget construction: why does connecting the
   three literals within a clause as a triangle, and connecting every variable to its
   negation, correctly capture "at most one satisfying literal per clause, and no
   variable/negation conflict"?
2. Explain why a reduction proof that only shows "A-instance yes implies constructed
   B-instance yes" is insufficient to prove B is NP-hard — what specifically does the
   missing backward direction establish?
3. Why does proving Hamiltonian Cycle is NP-complete not automatically prove that finding
   the minimum-cost tour (TSP) is NP-hard — what additional reduction step is needed, and
   how does the cost-1/cost-2 edge assignment achieve it?
4. A colleague proposes reducing a known-easy problem into their new problem to prove the
   new problem is hard. Explain why this gets the reduction direction backward and what
   it would actually prove instead.

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 8: "NP and Computational
  Intractability."
