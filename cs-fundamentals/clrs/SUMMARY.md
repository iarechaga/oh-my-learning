# Introduction to Algorithms (CLRS) - Subject Summary

A comprehensive recap of *Introduction to Algorithms* (Cormen, Leiserson, Rivest, Stein),
concept by concept.

**Progress note:** all 20 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded. This summary will gain depth
(especially on the concepts you find hard) as discussions happen - the "Focus areas"
section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
analysis foundations, then elementary data structures, then core algorithm families
(sorting, DP, greedy), then graph algorithms, then advanced correctness/complexity
topics.

## Analysis foundations

- **[clrs/01] Asymptotic growth and Big-O/Theta/Omega** - O is "at most," Omega is "at
  least," Theta is "exactly, up to constants"; drop lower-order terms and constant
  factors to compare algorithms by scaling behavior. ([lesson](lessons/01-asymptotic-growth.md))
- **[clrs/02] Recurrences and the Master method** - solve T(n) = aT(n/b) + f(n) by
  comparing f(n) to n^(log_b(a)); recursion trees build the intuition the Master method
  automates. ([lesson](lessons/02-recurrences-master-method.md))
- **[clrs/03] Divide and conquer as a design paradigm** - split into independent
  same-kind subproblems, solve recursively, combine; the induced recurrence's parameters
  (a, b, f(n)) are design choices with direct asymptotic consequences (Strassen's
  algorithm as the clearest case). ([lesson](lessons/03-divide-and-conquer.md))
- **[clrs/04] Probabilistic analysis and randomized algorithms** - indicator random
  variables plus linearity of expectation compute expected costs even under dependent
  events; randomized algorithms supply their own randomness so the guarantee holds for
  every input, not just "average" ones. ([lesson](lessons/04-probabilistic-analysis-randomization.md))

## Elementary data structures

- **[clrs/05] Elementary data structures (stacks, queues, linked lists)** - match the
  structure to the access pattern: LIFO -> stack, FIFO -> queue, known-position
  insert/delete -> linked list. ([lesson](lessons/05-elementary-data-structures.md))
- **[clrs/06] Hash tables and expected-time lookup** - expected O(1) via chaining or open
  addressing, contingent on a bounded load factor and a hash function approximating
  uniform distribution; the worst case is real and exploitable without randomized
  hashing. ([lesson](lessons/06-hash-tables.md))
- **[clrs/07] Heaps and priority queues** - a weaker invariant than full sortedness
  (each node dominates its own subtree) gives O(log n) insert/extract-max and O(1) peek;
  BUILD-MAX-HEAP is Theta(n), not Theta(n log n). ([lesson](lessons/07-heaps-priority-queues.md))
- **[clrs/09] Balanced search trees (red-black trees)** - a cheap, local coloring
  invariant (no red-red, equal black-height) provably bounds height to O(log n)
  regardless of insertion order, restored via O(1) rotations. ([lesson](lessons/09-balanced-search-trees.md))
- **[clrs/18] Disjoint sets and union-find analysis** - union by rank plus path
  compression together give amortized O(inverse-Ackermann(n)) per operation - for all
  practical purposes O(1). ([lesson](lessons/18-disjoint-sets-union-find.md))

## Sorting and selection

- **[clrs/08] Quicksort and randomized partitioning** - any constant-fraction partition
  split gives Theta(n log n); randomizing the pivot converts input-dependent Theta(n^2)
  into vanishingly-unlikely-regardless-of-input. ([lesson](lessons/08-quicksort-randomized.md))
- **[clrs/10] Order statistics and selection in linear time** - quickselect prunes one
  recursive branch entirely, turning quicksort's Theta(n log n) into Theta(n);
  median-of-medians achieves the same worst-case Theta(n) deterministically.
  ([lesson](lessons/10-order-statistics-selection.md))

## Algorithm design paradigms

- **[clrs/11] Dynamic programming fundamentals** - solve each distinct overlapping
  subproblem once (memoization or tabulation) instead of recomputing it; complexity =
  (distinct subproblems) x (work per subproblem). ([lesson](lessons/11-dynamic-programming-fundamentals.md))
- **[clrs/12] Greedy algorithms and exchange arguments** - a locally optimal, never-
  revisited choice is only valid once proven via an exchange argument; 0/1 knapsack is
  the canonical case where a plausible greedy rule provably fails.
  ([lesson](lessons/12-greedy-algorithms.md))

## Graph algorithms

- **[clrs/13] Graph representations, BFS, and DFS** - adjacency list (sparse, iteration)
  vs. matrix (dense, O(1) lookup); BFS's FIFO order finds shortest unweighted paths, DFS's
  timestamps reveal cycles and structure. ([lesson](lessons/13-graph-representations-bfs-dfs.md))
- **[clrs/14] Shortest-path algorithms** - Dijkstra's greedy finalize-the-closest order
  needs non-negative weights; Bellman-Ford's brute-force relaxation tolerates negative
  weights and detects negative cycles, at O(VE) cost. ([lesson](lessons/14-shortest-path-algorithms.md))
- **[clrs/15] Minimum spanning trees** - Kruskal's (edge-sorted, union-find) and Prim's
  (vertex-grown, priority queue) are both greedy, both correct via the same cut property.
  ([lesson](lessons/15-minimum-spanning-trees.md))
- **[clrs/16] Maximum flow and the max-flow min-cut theorem** - Ford-Fulkerson pushes flow
  along residual-graph augmenting paths (backward edges let it undo earlier choices);
  max-flow min-cut proves optimality by exhibiting a matching bottleneck cut.
  ([lesson](lessons/16-maximum-flow-min-cut.md))

## Amortized analysis and computational complexity

- **[clrs/17] Amortized analysis techniques** - aggregate, accounting, and potential
  methods bound average cost per operation over a worst-case sequence; geometric (not
  linear) dynamic-array growth is what makes push amortized O(1).
  ([lesson](lessons/17-amortized-analysis.md))
- **[clrs/19] NP-completeness and polynomial-time reductions** - P vs. NP vs.
  NP-complete; polynomial-time reductions from a known NP-complete problem (all
  ultimately anchored to SAT via Cook-Levin) prove new problems equally hard.
  ([lesson](lessons/19-np-completeness-reductions.md))
- **[clrs/20] Approximation algorithms for NP-hard problems** - bound the algorithm's
  output against a cheaply computable lower bound on the unknown optimum (a matching for
  vertex cover, an MST for metric TSP) to prove a worst-case approximation ratio.
  ([lesson](lessons/20-approximation-algorithms.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
