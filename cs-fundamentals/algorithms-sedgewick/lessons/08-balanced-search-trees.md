---
id: algorithms-sedgewick/08
subject: algorithms-sedgewick
title: Balanced search trees (red-black BSTs)
slug: balanced-search-trees
status: drafted
mastery:
seniority: mid
source: Algorithms (Sedgewick, Wayne), Section 3.3
prerequisites: [algorithms-sedgewick/07, clrs/09]
created: 2026-08-10
updated: 2026-08-10
---

# Balanced search trees (red-black BSTs)

## TL;DR
Sedgewick and Wayne derive red-black trees from a more intuitive starting point than
CLRS's direct coloring rules: the **2-3 tree** (nodes hold one or two keys and have two or
three children), which is trivially balanced by construction, then show that a red-black
BST is exactly a clever binary-tree *encoding* of a 2-3 tree, where a "red" link
represents the internal glue holding a 2-3 node's two keys together as a small binary
subtree.

## The idea
CLRS's red-black tree (`clrs/09`) states the coloring invariants and proves they bound
height, which is rigorous but can feel like an arbitrary set of rules to memorize.
Sedgewick's approach builds the *motivation* first: a 2-3 tree, where every leaf sits at
exactly the same depth by construction (insertion always happens at a leaf, and if a leaf
node overflows to holding two keys' worth of extra content, that overflow is resolved by
splitting and pushing a key *up* to the parent — a process that provably keeps all leaves
at equal depth), is perfectly balanced with no separate "rebalancing" step needed at all.
The catch: a 2-3 tree's variable-arity nodes (some hold one key/two children, others hold
two keys/three children) are awkward to implement directly. The red-black BST is the
resolution: represent a 2-3 tree's 3-node (two keys, three children) as a small
binary-tree fragment — two BST nodes connected by a special "red" link — so the whole
structure can be implemented as an ordinary binary tree while still behaving exactly like
a 2-3 tree underneath.

## How it works

### The 2-3 tree, first
A 2-3 tree's nodes are either **2-nodes** (one key, two children, structured like a
normal BST node) or **3-nodes** (two keys, three children — a smaller-than-both,
in-between, and larger-than-both child). **Insertion always happens at the bottom
(a leaf)**, and if inserting into a 2-node leaf, it simply becomes a 3-node leaf — no
rebalancing needed. If inserting into a **3-node leaf** (already full), it temporarily
becomes a 4-node (three keys), which is immediately split: the middle key moves up into
the parent (recursively, potentially triggering the same split-and-push-up at the parent
if it too becomes a temporary 4-node, all the way up to possibly creating a new root,
which is the *only* way a 2-3 tree's height ever increases). **Because this split-and-
push mechanism only ever changes tree height by growing the root upward — never by
extending any existing leaf's depth — every leaf remains at exactly the same depth after
any sequence of insertions**, which is the entire reason a 2-3 tree is balanced by
construction, no separate rebalancing procedure required.

### Encoding a 2-3 tree as a binary tree: red and black links
A 2-node maps directly to an ordinary binary-tree node with a normal ("black") link to
each child. A 3-node is represented as **two ordinary binary nodes connected by a red
link** (by convention, always leaning left in Sedgewick's presentation) — the red link
signals "these two nodes are really one 3-node in the underlying 2-3 tree, glued
together," while black links represent genuine 2-3-tree parent-child links. This
immediately explains CLRS's abstract coloring rules in concrete terms: **"no two red
links in a row"** (property 4) is just "a 3-node's internal glue-link doesn't chain into
another 3-node's glue-link" (since a 2-3 tree, by definition, has no node holding three
or more keys); **"equal black-height on every root-to-leaf path"** (property 5) is
exactly the 2-3 tree's "every leaf at the same depth" property, since black links are the
only links that correspond to genuine 2-3-tree depth.

### Insertion, reframed through this lens
Inserting into a red-black BST performs a standard BST insertion (attaching the new node
with a red link, since a newly inserted key starts as "glued" to whatever it landed
next to), then a sequence of local fix-ups — **rotate left** if a red link would lean
right (Sedgewick's convention keeps all red links leaning left for implementation
uniformity), **rotate right and flip colors** if two red links chain in a row (resolving
what would be an illegal 4-node), and **flip colors** if a node has both children
connected by red links (splitting a temporary 4-node exactly as the 2-3 tree's own
insertion procedure would, pushing a key up by recoloring the parent's link red). This is
the *same* fix-up logic CLRS's insertion case analysis performs (`clrs/09`), but framed
here as "restore the 2-3 tree's split-and-push-up behavior," which many learners find a
more intuitive anchor than memorizing the coloring cases directly.

### Why this reframing is pedagogically valuable, not just decorative
Understanding red-black trees via 2-3 trees means the coloring rules stop being arbitrary
constraints to memorize and become a direct, mechanical consequence of a much simpler,
more intuitive underlying structure (2-3 trees) that's obviously balanced. This is
particularly useful for reasoning about *why* a specific rotation or color flip is needed
during insertion — instead of matching a case from a table, you can ask "what would the
underlying 2-3 tree do here?" and derive the correct fix-up from first principles.

## Pros
- Motivates the coloring invariants from an intuitive, obviously-balanced-by-construction
  structure (2-3 trees), rather than presenting them as rules to memorize and separately
  prove correct.
- Provides an alternative mental model for insertion fix-up logic (split-and-push-up)
  that many find easier to reconstruct from first principles than CLRS's direct
  case-based coloring analysis.
- Same asymptotic guarantees as CLRS's red-black tree (`clrs/09`) — O(log n) worst case
  for search, insert, and delete — since it's the same underlying structure, just derived
  differently.

## Cons
- The 2-3-tree framing, while more intuitive for insertion, doesn't simplify deletion
  much — deletion from a 2-3 tree (and correspondingly from a red-black BST) remains
  genuinely intricate regardless of which mental model is used.
- Implementing a red-black BST directly as a binary structure (rather than an actual
  variable-arity 2-3 tree) still requires the same rotation and color-flip machinery as
  CLRS's version — the 2-3 tree is a mental model for *understanding why*, not a simpler
  thing to actually implement.
- Sedgewick's left-leaning convention (all red links lean left) simplifies the case
  analysis somewhat compared to CLRS's more general treatment, but this is an
  implementation choice, not a fundamentally different or more powerful data structure.

## Alternatives
- **CLRS's direct red-black tree treatment** (`clrs/09`) — the same structure, presented
  via direct coloring-invariant case analysis rather than the 2-3-tree derivation; some
  learners find this more directly applicable when reading other algorithms literature
  that assumes the coloring-rule framing.
- **B-trees** — a direct generalization of 2-3 trees to nodes with many more keys and
  children, minimizing disk/page reads; the natural next structure once 2-3 trees are
  understood, especially relevant for on-disk or database-index contexts.
- **AVL trees** — a differently-balanced BST (height-difference based, not 2-3-tree
  based) with a stricter balance guarantee, trading faster lookups for more rebalancing
  work on insert/delete.

## When to use it
Use a red-black BST (via either mental model) whenever you need guaranteed O(log n)
worst-case ordered operations — exactly the same use cases as CLRS's treatment
(`clrs/09`): ordered maps/sets, range queries, and predecessor/successor lookups where a
hash table's lack of ordering is unacceptable.

## When NOT to use it
Same guidance as CLRS's treatment: don't reach for a red-black BST when you only need
key-value lookup with no ordering requirement (a hash table's expected O(1) wins there),
and prefer a well-tested library implementation over hand-rolling one, given the real
implementation subtlety in both mental models.

## Key takeaways / mental model
A red-black BST is a binary encoding of a 2-3 tree: a red link glues together the two
binary nodes representing one 3-node. 2-3 trees are balanced by construction because
insertion only ever grows the tree at the root (via split-and-push-up), never extends an
existing leaf's depth — red-black BSTs inherit this guarantee by faithfully encoding the
same structure and behavior in binary form.

## Self-check questions
1. Explain why a 2-3 tree's height only ever increases by growing a new root, and why
   this guarantees every leaf stays at the same depth after any sequence of insertions.
2. Walk through how a red link between two binary nodes represents a single 3-node in the
   underlying 2-3 tree, and why "no two red links in a row" corresponds exactly to
   "no node holds three or more keys."
3. Using the 2-3-tree mental model, explain what should happen (conceptually, in terms of
   splitting and pushing a key up) when inserting into a full 3-node leaf, and connect
   this to the color-flip operation in the red-black BST encoding.
4. Why does the 2-3-tree framing make insertion's fix-up logic more intuitive to
   reconstruct from first principles, while not similarly simplifying deletion?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 3.3: "Balanced Search
  Trees."
