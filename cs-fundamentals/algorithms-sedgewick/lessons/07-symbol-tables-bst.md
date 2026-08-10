---
id: algorithms-sedgewick/07
subject: algorithms-sedgewick
title: Symbol tables with binary search trees
slug: symbol-tables-bst
status: drafted
mastery:
seniority: mid
source: Algorithms (Sedgewick, Wayne), Section 3.2
prerequisites: [algorithms-sedgewick/03]
created: 2026-08-10
updated: 2026-08-10
---

# Symbol tables with binary search trees

## TL;DR
Sedgewick and Wayne frame the **symbol table** (ordered key-value map) as an ADT first,
then show that a binary search tree (BST) implements not just get/put but a rich set of
**ordered operations** (min, max, floor, ceiling, rank, select, range queries) that
neither a hash table nor an unordered structure can support efficiently — the entire
motivation for reaching for a BST rather than a hash table, beyond raw lookup speed.

## The idea
A hash table (`clrs/06`) answers "what value is associated with this key?" in expected
O(1), but nothing more — no way to ask "what's the smallest key?" or "what keys fall
between X and Y?" without an O(n) scan. A BST maintains the ordering property (left
subtree smaller, right subtree larger) that a hash table deliberately discards, and this
lesson's focus is exactly on the rich vocabulary of **ordered symbol-table operations**
this unlocks — not just search, but a whole family of rank- and order-based queries that
recur constantly in real applications (leaderboards, range filters, nearest-value
lookups).

## How it works

### The core BST operations, and their recursive structure
`get(key)`: compare key to the current node's key; recurse left if smaller, right if
larger, return the value if equal, or null/absent if a null link is reached.
`put(key, value)`: same recursive search, but insert a new node at the null link found,
or overwrite the value if the key already exists. Both are O(height) — which is
O(log n) for a balanced tree but O(n) worst case for an unbalanced one (identical
observation to CLRS's, `clrs/09`, motivating balanced trees).

### Ordered operations that a hash table cannot support at all
- **min/max** — follow left (or right) links from the root until reaching a null link;
  O(height).
- **floor(key)/ceiling(key)** — the largest key <= (or smallest key >=) a given key, even
  if that exact key isn't present; computed via a single recursive descent that, at each
  node, decides whether to recurse further or record the current node as a candidate
  answer, depending on the comparison — O(height).
- **rank(key)** — how many keys are strictly less than the given key; computed by
  augmenting each node with a **count** of nodes in its subtree, then using that count to
  answer rank in O(height) without an O(n) scan.
- **select(k)** — the key with rank k (the k-th smallest key overall); the mirror
  operation to rank, also O(height) using the same subtree-count augmentation.
- **range queries (keys between lo and hi)** — a modified in-order traversal that prunes
  subtrees entirely outside [lo, hi], visiting only the relevant nodes plus a bounded
  number of boundary nodes — output-sensitive: O(height + number of keys in the range),
  not O(n).

**Why this augmentation (subtree counts) is the key enabling idea.** rank and select
would otherwise require an O(n) traversal to count keys — storing a running subtree size
at each node, maintained incrementally on every insertion, is what compresses this down
to O(height). This is a specific instance of a general and reusable technique: **augment
a data structure with extra, incrementally-maintained metadata to answer a query the base
structure alone couldn't answer efficiently** — the same idea recurs in more advanced
structures like order-statistics trees and interval trees.

### Deletion: the trickiest BST operation, and Hibbard deletion's known flaw
Deleting a node with zero or one child is straightforward (splice it out, promote its
one child if any). Deleting a node with **two** children is the hard case: **Hibbard
deletion** replaces the deleted node with its **successor** (the minimum of its right
subtree — guaranteed to have no left child itself, since it's the leftmost node of that
subtree, making it simple to detach and promote). This is correct, but Sedgewick notes an
important, non-obvious practical flaw: **repeated random insertions and Hibbard
deletions asymmetrically bias the tree toward becoming left-heavy over time** (because
always promoting the *successor*, rather than alternating between successor and
predecessor, systematically shifts the tree's shape), degrading average height below
what random insertions alone would produce — a real, empirically-observed and
mathematically-characterized performance issue with an otherwise "obviously correct"
algorithm, and a good illustration of why "correct" and "well-behaved under repeated
real-world usage patterns" aren't automatically the same thing.

### Why a plain BST's average case is good, but its worst case remains a real risk
For n keys inserted in **random** order, the expected BST height is O(log n) (a
result connected to the same style of probabilistic analysis CLRS covers, `clrs/04`) —
so get/put average Theta(log n) under random insertion order. But (exactly as CLRS notes
for the motivation behind red-black trees, `clrs/09`) a sorted or adversarial insertion
order still degrades a plain BST to O(n) height — this lesson's BST is explicitly a
stepping stone toward the guaranteed-balanced structures (`algorithms-sedgewick/08`)
covered next, not a production-ready structure on its own when insertion order isn't
controlled or known to be random.

## Pros
- Supports a genuinely rich set of ordered queries (min, max, floor, ceiling, rank,
  select, range) that a hash table cannot answer efficiently at all, at the modest cost
  of O(log n) rather than O(1) for plain lookup (under random insertion order).
- The subtree-count augmentation technique used for rank/select generalizes to a wide
  class of "augment with incrementally-maintained metadata" problems well beyond this
  specific structure.
- A plain, unbalanced BST is simple to implement and reason about — a good pedagogical
  and sometimes practical stepping stone before reaching for the more complex balanced
  variants.

## Cons
- Worst-case O(n) height under adversarial or sorted insertion order — this lesson's
  plain BST offers no protection against this, unlike the balanced-tree machinery
  covered next (`algorithms-sedgewick/08`, `clrs/09`).
- Hibbard deletion's successor-only replacement strategy introduces a subtle, real
  performance degradation under repeated delete-heavy usage, even though it's
  functionally correct.
- The ordered-query capability comes at a real cost compared to a hash table's O(1)
  expected lookup — if you never need ordering, rank, or range queries, a BST is paying
  for capability you're not using.

## Alternatives
- **Hash tables** (`clrs/06`) — faster expected lookup (O(1) vs. O(log n)) when ordered
  operations are never needed.
- **Balanced BSTs** (`algorithms-sedgewick/08`, `clrs/09`) — the direct fix for a plain
  BST's worst-case height vulnerability, guaranteeing O(log n) regardless of insertion
  order.
- **Skip lists** (`multiprocessor-programming/06`) — an alternative ordered structure with
  probabilistic (not worst-case) O(log n) guarantees and simpler code, particularly
  favored in concurrent contexts.

## When to use it
Use a BST-backed symbol table (ideally the balanced variant, `algorithms-sedgewick/08`)
whenever you need ordered operations — min/max, floor/ceiling, rank/select, or range
queries — that a hash table cannot provide. Use a plain (unbalanced) BST specifically
when insertion order is known to be effectively random and worst-case guarantees aren't
required.

## When NOT to use it
Don't use a plain, unbalanced BST when insertion order might be sorted or adversarial —
its worst-case O(n) height is a real risk, not just a theoretical curiosity. Don't reach
for a BST at all (balanced or not) if you never need ordered queries — a hash table's
O(1) expected lookup is strictly better for pure key-value access.

## Key takeaways / mental model
A BST's value over a hash table is the rich family of ordered operations it supports
(min, max, floor, ceiling, rank, select, range), enabled by augmenting each node with
incrementally-maintained subtree-size metadata for rank/select specifically. A plain
BST's height is only good (O(log n)) under random insertion order — sorted or
adversarial order still degrades it to O(n), which is exactly the problem balanced BSTs
solve.

## Self-check questions
1. Explain how the subtree-count augmentation lets rank(key) run in O(height) rather than
   requiring an O(n) traversal, walking through a concrete small example.
2. Why can the successor of a node (used in Hibbard deletion) always be spliced out
   without needing to recursively handle a two-child case itself?
3. Describe the asymmetric bias Hibbard deletion introduces over repeated random
   insertions and deletions, and why "functionally correct" doesn't guarantee "good
   long-run behavior" here.
4. Give a concrete application where a range query (all keys between lo and hi) is
   needed, and explain why a hash table could not answer it efficiently regardless of its
   load factor.

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 3.2: "Binary Search
  Trees."
