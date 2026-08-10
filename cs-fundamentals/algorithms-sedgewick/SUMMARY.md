# Algorithms (Sedgewick and Wayne) - Subject Summary

A practical, implementation-first recap of *Algorithms* (Robert Sedgewick, Kevin Wayne),
concept by concept.

**Progress note:** all 14 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded. This summary will gain depth
(especially on the concepts you find hard) as discussions happen - the "Focus areas"
section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
implementation basics and analysis first, then sorting/searching, then graph algorithms,
then string algorithms.

## Implementation basics and analysis

- **[algorithms-sedgewick/01] Union-find and connectivity modeling** - the case study
  showing the correct-diagnose-fix-repeat engineering methodology, from quick-find
  through weighted quick-union with path compression. ([lesson](lessons/01-union-find-connectivity.md))
- **[algorithms-sedgewick/02] Algorithm analysis and cost models** - defining a precise
  cost model (which operations count) before claiming any complexity result, and reading
  empirical doubling-ratio experiments to validate theoretical predictions.
  ([lesson](lessons/02-algorithm-analysis-cost-models.md))
- **[algorithms-sedgewick/03] Stacks, queues, and linked-list implementations** -
  resizing-array vs. linked-list trade-offs for the same abstract interface, and why
  separating interface from implementation lets client code stay unaware of the choice.
  ([lesson](lessons/03-stacks-queues-linked-lists.md))

## Sorting and priority queues

- **[algorithms-sedgewick/04] Elementary sorting (selection, insertion, shellsort)** -
  insertion sort's adaptivity on nearly-sorted data, and shellsort's h-sorting as a
  practical bridge to fully general sorts. ([lesson](lessons/04-elementary-sorting.md))
- **[algorithms-sedgewick/05] Mergesort and quicksort in practice** - engineering
  concerns (cutoff to insertion sort, median-of-three pivoting, already-sorted-skip
  optimization) that separate a textbook implementation from a production-grade one.
  ([lesson](lessons/05-mergesort-quicksort.md))
- **[algorithms-sedgewick/06] Priority queues and heapsort** - the binary heap's array
  representation and sink/swim operations, and why heapsort is rarely chosen in practice
  despite guaranteed O(n log n) with O(1) extra space.
  ([lesson](lessons/06-priority-queues-heapsort.md))

## Symbol tables and searching

- **[algorithms-sedgewick/07] Symbol tables with binary search trees** - ordered
  operations (floor, ceiling, range queries) a BST supports that a hash table
  fundamentally cannot. ([lesson](lessons/07-symbol-tables-bst.md))
- **[algorithms-sedgewick/08] Balanced search trees (red-black BSTs)** - the 2-3 tree
  model as the intuitive foundation, encoded via red links, for why red-black BSTs
  guarantee O(log n) height regardless of insertion order.
  ([lesson](lessons/08-balanced-search-trees.md))
- **[algorithms-sedgewick/09] Hash tables (separate chaining and linear probing)** -
  load-factor-driven resizing policy and the specific failure mode of deleting under
  linear probing without proper cluster re-insertion.
  ([lesson](lessons/09-hash-tables.md))

## Graph algorithms

- **[algorithms-sedgewick/10] Undirected and directed graph fundamentals** - the minimal
  `Graph`/`Digraph` API plus the "preprocess in the constructor, query cheaply
  afterward" client-class pattern used across nearly every graph algorithm in the book.
  ([lesson](lessons/10-graph-fundamentals.md))
- **[algorithms-sedgewick/11] Minimum spanning trees and shortest paths** - lazy vs.
  eager Prim's (stale priority-queue entries vs. an indexed priority queue), and the
  exact structural correspondence between eager Prim's and Dijkstra's algorithm.
  ([lesson](lessons/11-mst-shortest-paths.md))
- **[algorithms-sedgewick/12] Directed acyclic graphs and topological order** - detecting
  a directed cycle via `onStack[]` back edges, and why the reverse of DFS postorder is a
  valid topological order. ([lesson](lessons/12-dag-topological-order.md))

## String algorithms

- **[algorithms-sedgewick/13] Tries and substring search algorithms** - indexing on
  individual characters (R-way tries, TSTs) to answer prefix queries no comparison-based
  or hash-based structure can, and how KMP/Boyer-Moore/Rabin-Karp each avoid
  brute-force's wasted re-comparisons after a mismatch.
  ([lesson](lessons/13-tries-substring-search.md))
- **[algorithms-sedgewick/14] Data compression (Huffman and LZW)** - two complementary
  redundancy types - frequency skew (Huffman, via a priority-queue-built trie) and
  substring repetition (LZW, via an on-the-fly shared dictionary) - and why real
  compressors like DEFLATE combine both.
  ([lesson](lessons/14-data-compression-huffman-lzw.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
