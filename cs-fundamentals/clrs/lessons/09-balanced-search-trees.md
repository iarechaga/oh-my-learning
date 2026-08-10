---
id: clrs/09
subject: clrs
title: Balanced search trees (red-black trees)
slug: balanced-search-trees
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapter 13
prerequisites: [clrs/05]
created: 2026-08-10
updated: 2026-08-10
---

# Balanced search trees (red-black trees)

## TL;DR
A plain binary search tree gives O(log n) operations only if it stays balanced — an
adversarial or already-sorted insertion sequence can degrade it into a linked list
(O(n)). A red-black tree is a binary search tree augmented with a coloring rule that a
rebalancing procedure enforces on every insert/delete, guaranteeing height O(log n) no
matter the insertion order, so every operation stays O(log n) worst case.

## The idea
A binary search tree (BST) maintains the invariant: for any node, everything in its left
subtree is smaller, everything in its right subtree is larger. This supports search,
insert, and delete by walking down from the root, comparing at each node — the cost of
any of these operations is exactly the tree's height. The problem: nothing about a plain
BST prevents pathological shapes. Inserting 1, 2, 3, 4, 5 in order into a plain BST
produces a tree that's really just a linked list leaning right — height n, not log n,
so every operation degrades to O(n). A **balanced** search tree adds a structural
invariant, enforced by a rebalancing step on every modification, that mathematically
guarantees height stays O(log n) regardless of insertion order.

## How it works

### The red-black properties
A red-black tree is a BST where every node is colored red or black, satisfying:
1. Every node is red or black (trivially true, but stated for completeness).
2. The root is black.
3. Every leaf (CLRS treats NIL sentinels as leaves) is black.
4. If a node is red, both its children are black (no two reds in a row on any path — "no
   red-red violation").
5. Every path from a given node down to any of its descendant leaves contains the same
   number of black nodes (the node's **black-height**).

### Why these properties force O(log n) height
Property 5 means black nodes alone form a perfectly balanced structure (every root-to-
leaf path has the same black-node count). Property 4 means red nodes can't make any path
more than twice as long as the shortest possible path (since reds can never be adjacent,
at most every other node on a path is red). Combining these two facts, CLRS proves: a
red-black tree with n internal nodes has height at most 2*log2(n+1) — a hard mathematical
guarantee, not a probabilistic or amortized one. This is the entire point of the coloring
scheme: it's a cheap, locally-checkable invariant (each property only depends on
immediate neighbors, not the whole tree) that provably bounds global height.

### Rotations: the rebalancing primitive
A **rotation** (left-rotate or right-rotate) restructures a small, local piece of the
tree — swapping a node with one of its children while preserving the BST ordering
property — in O(1) time. Rotations are the only tool insert/delete rebalancing uses to
fix property violations; they never touch more than a constant number of pointers, which
is what keeps rebalancing cheap even though the properties are global.

### Insertion, at a high level
Insert the new node as a plain BST leaf, colored **red** (inserting red, not black,
avoids immediately violating property 5's black-height balance — a new red leaf changes
no path's black-node count). This might violate property 4 (a red node with a red
parent). Fix this with a case analysis on the new node's "uncle" (its parent's sibling):
- **Uncle is red:** recolor the parent, uncle, and grandparent (push the violation up
  the tree) and recurse on the grandparent.
- **Uncle is black (or absent):** one or two rotations plus a recoloring resolve the
  violation locally, without needing to recurse further up the tree.

Each case does O(1) work; the "uncle is red" case can repeat up the tree, but it strictly
decreases in depth, so the whole fixup is O(log n) — matching the tree's height.

### Worked example, sketched
Insert values 10, 20, 30 in increasing order into an initially empty red-black tree (the
exact sequence that breaks a plain BST into a linked list). Insert 10: becomes the black
root (property 2 forces the root to always be black after any fixup). Insert 20: as
10's right child, red — no violation (10 is black, so no red-red). Insert 30: as 20's
right child, red — now 20 (red) has a red child 30, violating property 4. 30's uncle
(10's other child, which doesn't exist / is a black NIL leaf) is black, so this triggers
a rotation case: left-rotate around 10, making 20 the new (black) root with 10 and 30 as
its red children. The tree is now perfectly balanced (height 2, not 3) despite the fully
sorted insertion order that would have degenerated a plain BST completely.

### Deletion
Deletion is more involved than insertion (CLRS spends more case analysis on it) because
removing a black node can violate property 5 (black-height) for every path through the
removed node's position, and the fix-up has more distinct cases (based on the "sibling"
node's color and its children's colors) — but the guarantee is the same: O(log n) fixup
via a constant number of rotations plus recoloring per level.

### The complete operation-cost picture
Because search only ever needs the BST ordering property (not the coloring at all),
search is a plain BST search, cost = height = O(log n) guaranteed by the red-black
invariant. Insert and delete are O(log n) for the plain BST operation plus O(log n)
(actually O(1) amortized rotations, though O(log n) recoloring in the worst case) for the
rebalancing fixup — net O(log n) worst case for every operation.

## Pros
- Worst-case O(log n) for search, insert, and delete, guaranteed regardless of insertion
  order — no adversarial or already-sorted sequence can degrade it, unlike a plain BST.
- Supports everything a plain BST supports beyond a hash table: sorted (in-order)
  traversal, range queries, predecessor/successor, min/max in O(log n) — none of which a
  hash table (`clrs/06`) can do.
- The underlying idea (a cheap, local, provably-sufficient invariant maintained via O(1)
  rotations) generalizes: B-trees, AVL trees, and 2-3-4 trees all follow the same
  "local invariant forces global balance" pattern with different specific rules.

## Cons
- Real implementation complexity: the insert/delete fixup case analysis is genuinely
  intricate and easy to get subtly wrong from scratch — most engineers use a library
  implementation rather than writing one, unlike, say, a binary heap.
- Constant factors are noticeably worse than a hash table's expected O(1) for pure
  key-value lookup with no ordering need — don't pay for a red-black tree's guarantees if
  you never use sorted order or range queries.
- Pointer-based (unlike an array-backed heap), so worse cache locality than contiguous
  structures for equivalent-sized data.

## Alternatives
- **Hash tables** (`clrs/06`) — expected O(1) instead of guaranteed O(log n), but no
  ordering support at all; the right choice when you never need sorted traversal or
  range queries.
- **AVL trees** — a different balanced-BST scheme (balance by height difference, not
  color) with a stricter balance invariant, giving slightly faster lookups but more
  expensive rebalancing on insert/delete than red-black trees — a classic lookup-heavy
  vs. modification-heavy trade-off.
- **B-trees** — generalize the same "local invariant, O(log n) height" idea to nodes with
  many children rather than two, minimizing disk/page reads for on-disk or
  cache-unfriendly-memory-hierarchy storage (the standard choice for database indexes).
- **Skip lists** (`multiprocessor-programming/06`) — a probabilistic alternative giving
  expected O(log n) operations with simpler code (no rotation case analysis) at the cost
  of a probabilistic rather than a worst-case guarantee.

## When to use it
Use a red-black tree (or rely on your language's built-in ordered map/set, almost always
backed by one) whenever you need guaranteed O(log n) worst-case operations *and* sorted
order, range queries, or predecessor/successor queries — e.g. an interval scheduling
structure, an ordered index, or any scenario where a hash table's lack of ordering is a
dealbreaker.

## When NOT to use it
Don't reach for (or hand-implement) a red-black tree when you only need key-value lookup
with no ordering requirement — a hash table's expected O(1) and much simpler
implementation win there. Don't hand-roll one at all in production code if a
well-tested standard-library ordered map/set is available — the fixup logic's
subtlety makes a from-scratch implementation a real correctness risk.

## Key takeaways / mental model
A red-black tree buys O(log n) worst-case guarantees by enforcing a cheap, local,
constant-time-checkable coloring invariant (no red-red, equal black-height on every
path) that provably bounds height to O(log n) — restored after every insert/delete via a
bounded number of O(1) rotations plus recoloring. The mechanism (local invariant, O(1)
repair, global balance) is the same pattern reused across AVL trees, B-trees, and 2-3-4
trees.

## Self-check questions
1. Explain why inserting a new node as red (not black) avoids immediately violating
   property 5 (equal black-height on every path), and why coloring it black instead
   would have been the wrong default.
2. Walk through why properties 4 and 5 together mathematically force height
   O(log n) — what would go wrong (which bound would fail) if you dropped property 4
   alone and kept only property 5?
3. Compare a red-black tree to a hash table for a use case requiring "give me all keys
   between X and Y in sorted order" — why can't a hash table answer this efficiently at
   all, regardless of load factor?
4. Why might an AVL tree be preferable to a red-black tree for a read-heavy, write-rare
   workload, and vice versa for a write-heavy workload?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 13: "Red-Black
  Trees."
