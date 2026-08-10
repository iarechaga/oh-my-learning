---
id: clrs/20
subject: clrs
title: Approximation algorithms for NP-hard problems
slug: approximation-algorithms
status: drafted
mastery:
seniority: senior
source: Introduction to Algorithms (CLRS), Chapter 35
prerequisites: [clrs/19]
created: 2026-08-10
updated: 2026-08-10
---

# Approximation algorithms for NP-hard problems

## TL;DR
When a problem is proven NP-hard (`clrs/19`), an approximation algorithm gives up exact
optimality in exchange for a polynomial-time algorithm with a **provable, worst-case
bound** on how far its answer can be from optimal — e.g. "never worse than twice the
optimal solution's cost, on any input, guaranteed." This is a fundamentally different
(and stronger) guarantee than a heuristic that merely "usually works well," because the
bound holds for every possible input, not just typical ones.

## The idea
`clrs/19` establishes that many important problems almost certainly have no efficient
exact algorithm. That doesn't mean giving up entirely — it means changing what you demand
from an algorithm. An **approximation algorithm** for a minimization problem with
**approximation ratio rho** guarantees its output is never more than rho times the true
optimal cost, for *any* input, in polynomial time (for a maximization problem, the ratio
guarantees the output is never *less* than 1/rho times optimal). The entire craft is
finding a polynomial-time algorithm and *proving* a specific, tight rho for it — not
just observing empirically that it "seems to do pretty well."

## How it works

### Worked example 1: vertex cover, a 2-approximation
Given a graph, a vertex cover is a set of vertices such that every edge has at least one
endpoint in the set; the minimum vertex cover problem (find the smallest such set) is
NP-hard. **Approximation algorithm:** repeatedly pick *any* remaining uncovered edge (u,v)
(any edge at all, no cleverness needed in the choice), add **both** endpoints u and v to
the cover, and remove every edge now covered by either of them. Repeat until no edges
remain.

**Why this guarantees a 2-approximation.** Every edge picked during the algorithm's
execution is, by construction, vertex-disjoint from every other edge picked so far (an
edge is only picked if it's still uncovered, meaning neither endpoint has been added yet)
— so the set of picked edges forms a **matching** (no two share an endpoint). Crucially,
*any* valid vertex cover — including the true optimal one — must include at least one
endpoint from *each* edge in this matching (since a matching's edges share no endpoints,
covering each one requires a genuinely distinct vertex), so the optimal cover has size at
least (number of matching edges picked). The algorithm's own cover has size exactly
*twice* the number of matching edges picked (two endpoints added per edge). Therefore:
algorithm's cover size = 2 * (matching edges) <= 2 * (optimal cover size) — a rigorous,
input-independent proof that this simple algorithm never does worse than double the true
optimum, despite using no sophisticated logic at all in picking which edge to process
next.

### Worked example 2: the traveling salesman problem (metric case), a 2-approximation via MST
Given a complete graph with distances satisfying the triangle inequality (the "metric"
TSP — a very common and realistic special case, since real physical distances always
satisfy it), find the shortest tour visiting every vertex exactly once and returning to
the start. **Approximation algorithm:** build a minimum spanning tree (`clrs/15`) of the
graph, then perform a DFS traversal of that tree, listing vertices in the order first
visited (a "preorder" walk), producing a tour (skipping any repeat visits, since DFS may
revisit a vertex's tree-parent).

**Why this guarantees a 2-approximation.** The DFS traversal of the MST, before
skipping repeats, traverses every tree edge exactly twice (once descending, once
returning) — so its total length is exactly 2 * (MST weight). The triangle inequality
guarantees that **skipping** already-visited vertices (taking a direct shortcut instead
of backtracking through them) can only *decrease*, never increase, total tour length —
so the final tour's length is at most 2 * (MST weight). Finally, any valid TSP tour,
with one edge removed, is itself a spanning tree — so the optimal tour's length is at
least the MST's weight (the MST is, by definition, the lightest possible spanning
structure). Chaining these two facts: algorithm's tour length <= 2 * MST weight <=
2 * optimal tour length — again, a rigorous, general proof, this time critically relying
on the triangle inequality (this specific approximation technique does *not* work, and
gives no guarantee at all, for general graphs where the triangle inequality can fail).

### The general recipe these examples share
Both approximation algorithms follow the same underlying strategy: find some
**efficiently computable lower bound** on the optimal solution's cost (the matching size,
for vertex cover; the MST weight, for metric TSP), then show the algorithm's own output
cost is bounded by a constant multiple of that same lower bound. This "bound the
algorithm against a computable lower bound on the unknown optimum" pattern recurs across
most classical approximation algorithms, and recognizing it is the core transferable
skill.

### Approximation schemes: when you can get arbitrarily close
For some problems (the **knapsack** problem, notably), a stronger result is achievable: a
**polynomial-time approximation scheme (PTAS)** — for any desired error tolerance epsilon
> 0, a polynomial-time (in the input size, though possibly exponential in 1/epsilon)
algorithm achieving within (1 + epsilon) of optimal. This lets you trade running time for
approximation quality on a sliding scale, rather than being stuck with one fixed ratio.
Not every NP-hard problem admits a PTAS — some (under standard complexity assumptions)
have a fixed best-possible approximation ratio and provably cannot be approximated
arbitrarily closely in polynomial time (a further, "hardness of approximation" layer of
theory beyond this lesson's scope).

## Pros
- Gives a polynomial-time algorithm with a *provable*, input-independent worst-case
  quality guarantee for problems where an exact efficient algorithm almost certainly
  doesn't exist — a rigorous middle ground between "give up" and "search forever for an
  impossible exact algorithm."
- Approximation algorithms are often remarkably simple (the vertex-cover algorithm above
  needs no sophisticated logic at all) — the sophistication lives entirely in the *proof*
  of the ratio, not necessarily in the algorithm's mechanics.
- The "bound against a computable lower bound" technique transfers across many different
  NP-hard problems, making it a genuinely reusable design pattern once internalized.

## Cons
- A guaranteed approximation ratio (e.g. "never worse than 2x optimal") can still be a
  poor result for a specific application that needs a result close to optimal — the
  bound is a worst-case guarantee, not a promise of good typical-case behavior (though in
  practice, many approximation algorithms do noticeably better than their proven worst
  case on typical instances).
- Not every NP-hard problem admits a good (small-ratio, or any-ratio) approximation
  algorithm at all — some are provably hard to approximate within any constant factor
  (again, a further theoretical layer), forcing a fallback to heuristics with no
  guarantee whatsoever.
- Constructing and proving a tight approximation ratio requires real mathematical care —
  significantly more design and proof effort than writing an unproven heuristic, even
  though the heuristic might perform similarly well in practice without any guarantee at
  all.

## Alternatives
- **Exact exponential-time algorithms** — for genuinely small instances, brute force or
  branch-and-bound can still find the true optimum, sidestepping approximation entirely
  when input size permits.
- **Unproven heuristics / local search** (`algorithm-design/11`) — often perform very
  well in practice on realistic instance distributions, but offer no worst-case
  guarantee at all, unlike a proven approximation algorithm — a real trade-off between
  "provably bounded, possibly conservative" and "no guarantee, possibly excellent in
  practice."
- **Exploiting problem-specific structure** — some NP-hard problems become tractable
  (exactly, not just approximately) when restricted to special input classes (planar
  graphs, bounded treewidth, interval structures), which can be more valuable than a
  general-purpose approximation algorithm if your instances happen to have that
  structure.

## When to use it
Use a proven approximation algorithm whenever you're facing an NP-hard optimization
problem in a context where you need a genuine, input-independent worst-case quality
guarantee in polynomial time — vertex cover, facility location, and metric TSP style
problems in network design, scheduling, and logistics are classic real-world fits.

## When NOT to use it
Don't reach for an unproven heuristic and call it an "approximation algorithm" without an
actual ratio proof — the value of the approximation-algorithm framing specifically comes
from the guarantee, not just from being a fast, reasonable-seeming method. Don't apply an
approximation technique that relies on a specific structural assumption (like metric
TSP's triangle inequality) to an instance that doesn't satisfy that assumption — the
proof (and therefore the guarantee) simply doesn't transfer.

## Key takeaways / mental model
An approximation algorithm's value lives in its proof, not just its mechanics: find a
cheap, computable lower bound on the true (unknown, hard-to-compute) optimum, then show
the algorithm's output is bounded by a constant multiple of that lower bound. This
pattern — matching size bounding vertex cover, MST weight bounding metric TSP — is the
transferable skill, more than either specific algorithm.

## Self-check questions
1. Walk through why the set of edges picked by the vertex-cover approximation algorithm
   forms a matching, and why that matching's size is a valid lower bound on the true
   optimal cover's size.
2. Explain precisely where the triangle inequality is used in the metric-TSP
   approximation's proof, and why the algorithm would give no guarantee at all on a graph
   that violates it.
3. What's the practical difference between a fixed-ratio approximation algorithm (e.g.
   always 2x optimal) and a PTAS (achieves within (1+epsilon) of optimal for any chosen
   epsilon)? What do you give up to get the PTAS's flexibility?
4. A colleague proposes a fast heuristic for an NP-hard problem that "does really well in
   practice" but has no proven ratio. How would you describe the practical trade-off
   between adopting their heuristic and using a proven, worse-in-the-worst-case
   approximation algorithm instead?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 35:
  "Approximation Algorithms."
