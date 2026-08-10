# Algorithm Design (Kleinberg and Tardos) - Subject Summary

A design-pattern-first recap of *Algorithm Design* (Jon Kleinberg, Eva Tardos), concept by
concept - focused on recognizing which paradigm a new problem calls for and proving the
resulting algorithm correct, rather than the mechanics of any single algorithm.

**Progress note:** all 12 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded. This summary will gain depth
(especially on the concepts you find hard) as discussions happen - the "Focus areas"
section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom: design
and proof foundations first, then the major paradigms (greedy, divide and conquer,
dynamic programming, network flow), then complexity boundaries and approximation.

## Design and proof foundations

- **[algorithm-design/01] Stable matching and algorithmic reasoning** - the Gale-Shapley
  algorithm as the book's opening case study in precise problem definition and
  invariant-based correctness proofs (termination via a counting argument, stability via
  proof by contradiction). ([lesson](lessons/01-stable-matching-reasoning.md))
- **[algorithm-design/02] Asymptotic analysis and recurrence solving** - the recursion
  tree method and the Master theorem as the mechanical last step for computing any
  divide-and-conquer algorithm's running time, including when the Master theorem's
  preconditions fail. ([lesson](lessons/02-asymptotic-analysis-recurrences.md))

## The major paradigms

- **[algorithm-design/03] Divide and conquer with proof of correctness** - the
  split-recurse-combine template paired with its matching strong-induction proof
  obligation, worked through closest-pair-of-points and counting-inversions.
  ([lesson](lessons/03-divide-and-conquer-correctness.md))
- **[algorithm-design/04] Greedy algorithms and exchange arguments** - three named proof
  techniques (exchange argument, "greedy stays ahead," structural graph arguments) and how
  to recognize which one a new greedy design calls for.
  ([lesson](lessons/04-greedy-exchange-arguments.md))
- **[algorithm-design/05] Dynamic programming: optimal substructure and state design** - a
  repeatable procedure for choosing DP state, illustrated by the progression from
  1D-state weighted interval scheduling to 2D-state knapsack.
  ([lesson](lessons/05-dynamic-programming-state-design.md))
- **[algorithm-design/06] Shortest paths and negative cycles** - why Dijkstra's
  correctness proof breaks under negative edge weights, and Bellman-Ford's DP-based
  alternative that also detects negative cycles via one extra relaxation round.
  ([lesson](lessons/06-shortest-paths-negative-cycles.md))
- **[algorithm-design/07] Graph traversal, connectivity, and strongly connected
  components** - BFS's layered shortest-path guarantee, DFS's edge classification, and
  Kosaraju's two-pass (DFS, transpose, DFS again) recipe for computing SCCs.
  ([lesson](lessons/07-graph-traversal-connectivity-scc.md))
- **[algorithm-design/08] Maximum flow and minimum cut** - the max-flow min-cut theorem
  and flow-network modeling as a design skill, via the bipartite matching and project
  selection reductions. ([lesson](lessons/08-maximum-flow-minimum-cut.md))

## Complexity boundaries and coping strategies

- **[algorithm-design/09] Reductions and NP-completeness proofs** - a worked chain of six
  classic reductions (3-SAT through TSP) building a repertoire of construction styles
  (complement graph, local gadget, decision-to-optimization) for proving new problems
  NP-complete. ([lesson](lessons/09-reductions-np-completeness.md))
- **[algorithm-design/10] Coping with NP-hardness: approximation algorithms** - the
  core proof pattern of bounding the unreachable true optimum via a structural or LP-
  relaxation-based lower/upper bound, worked through vertex cover and set cover.
  ([lesson](lessons/10-approximation-algorithms.md))
- **[algorithm-design/11] Coping with NP-hardness: local search and heuristic design** -
  neighborhood-structure design trade-offs, the local-optimum trap, and escape techniques
  (random restarts, simulated annealing) when no bounded approximation exists.
  ([lesson](lessons/11-local-search-heuristics.md))
- **[algorithm-design/12] Intractability in practice: modeling choices and tractable
  relaxations** - a modeling checklist (restricted input classes, fixed-parameter
  tractability, relaxed requirements) to check for exploitable structure before assuming
  the general NP-hard case applies. ([lesson](lessons/12-intractability-modeling-relaxations.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
