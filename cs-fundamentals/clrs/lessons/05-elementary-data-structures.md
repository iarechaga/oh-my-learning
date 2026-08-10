---
id: clrs/05
subject: clrs
title: Elementary data structures (stacks, queues, linked lists)
slug: elementary-data-structures
status: drafted
mastery:
seniority: junior
source: Introduction to Algorithms (CLRS), Chapter 10
prerequisites: [clrs/01]
created: 2026-08-10
updated: 2026-08-10
---

# Elementary data structures (stacks, queues, linked lists)

## TL;DR
Stacks, queues, and linked lists are the basic building blocks for organizing dynamic
collections of data with cheap insertion and removal. Each fixes a specific access
pattern (last-in-first-out for stacks, first-in-first-out for queues, arbitrary-position
insert/delete for linked lists) in exchange for giving up something else — usually
random access.

## The idea
An array gives O(1) random access but O(n) insertion/deletion in the middle (everything
after the insertion point must shift). Many algorithms don't need random access at all —
they only ever need to add or remove from one or two specific ends, or need to insert or
delete at arbitrary positions without needing to know an item's position by index. These
elementary structures specialize for exactly those access patterns, and the specialization
buys real efficiency: O(1) operations at the ends, and O(1) insertion/deletion in linked
lists once you already have a reference to the node (not searching for it).

## How it works

### Stacks: last-in-first-out (LIFO)
A stack supports two operations: **PUSH** (add to the top) and **POP** (remove from the
top) — both O(1). Think of a stack of plates: you can only add or remove from the top.
Implemented on an array, PUSH is `array[++top] = x` and POP is `return array[top--]` —
both constant time, no shifting needed, because insertion/removal only ever happens at
one fixed end.

**Worked example — balanced parentheses checking:** scan a string; on `(` push it; on
`)` pop and check a matching `(` was popped (if the stack is empty, the string is
unbalanced). At the end, the stack must be empty. This is the canonical use case for a
stack: matching nested structure, where the most recently opened thing must be the first
one closed.

### Queues: first-in-first-out (FIFO)
A queue supports **ENQUEUE** (add to the tail) and **DEQUEUE** (remove from the head) —
both O(1) with the right implementation. Think of a line at a store: the first person to
join is the first person served. A naive array implementation with a fixed head at index
0 would need to shift every element left on dequeue (O(n)); the standard fix is a
**circular buffer**: maintain `head` and `tail` indices that wrap around the array's end
using modular arithmetic, so both enqueue and dequeue are O(1) without any shifting.

**Worked example — breadth-first search (`clrs/13`)** uses a queue specifically because
it must process nodes in the order they were *discovered* (FIFO) to guarantee it explores
level by level, which is what makes BFS find shortest paths in an unweighted graph.

### Linked lists: arbitrary insertion/deletion via pointers
A linked list is a sequence of nodes, each holding a value and a pointer to the next node
(and, in a **doubly linked list**, also a pointer to the previous node). Unlike an array,
elements are not contiguous in memory — a node can live anywhere, and the pointers alone
define the sequence's order. This means insertion or deletion at a *known* position
(i.e. you already hold a pointer to the relevant node) is O(1): just relink a constant
number of pointers, no shifting. The cost you pay: finding the k-th element, or searching
for a value, requires O(n) traversal — there is no random access, because there's no
formula mapping an index to a memory address the way there is for an array.

**Worked example — inserting into a doubly linked list.** To insert node `y` after node
`x`: set `y.next = x.next`, `y.prev = x`, `x.next.prev = y` (if `x.next` exists), then
`x.next = y`. Four pointer assignments, O(1), regardless of how large the list is or
where `x` sits within it — contrast with an array insertion at the same logical position,
which is O(n) due to shifting every subsequent element.

**Sentinels.** CLRS introduces the sentinel (a dummy node, often called `nil`, that never
holds real data) to eliminate special-casing the empty-list and boundary conditions in
insert/delete code — the sentinel's `next` and `prev` pointers always point somewhere
valid, so insert/delete code never needs an `if (list is empty)` branch. This is a small
implementation trick, but it meaningfully simplifies and de-bugs pointer manipulation
code, which is notoriously easy to get subtly wrong (off-by-one in relinking is a classic
bug source).

### Comparing all three against the array
| Structure | Access by index | Insert/delete at known position | Insert/delete at
one end |
| --- | --- | --- | --- |
| Array | O(1) | O(n) (shifting) | O(1) amortized at end (`clrs/17`'s dynamic array) |
| Stack (array-backed) | N/A (only top) | N/A | O(1) at top |
| Queue (circular buffer) | N/A (only head/tail) | N/A | O(1) at both ends |
| Doubly linked list | O(n) (traversal) | O(1) (given the node pointer) | O(1) at both ends |

## Pros
- Stacks and queues give O(1) operations for exactly the access pattern (LIFO/FIFO) that
  a huge number of algorithms actually need (recursion/backtracking for stacks;
  level-order traversal, scheduling, buffering for queues).
- Linked lists give O(1) insert/delete at a known position with no shifting cost,
  regardless of list size or position — valuable when insertions/deletions are frequent
  and positions are usually already known (e.g. maintaining a free list, an LRU cache's
  usage order).
- All three are simple enough to implement correctly and reason about precisely, and
  serve as building blocks for more advanced structures (e.g. a hash table's chaining
  uses linked lists; a heap-based priority queue is unrelated to but named similarly to
  a queue).

## Cons
- Linked lists have no random access (O(n) to reach the k-th element) and worse cache
  locality than arrays (nodes are scattered in memory, so traversal causes more cache
  misses per element visited) — for pure sequential scanning of known-size data, a
  contiguous array is usually faster in practice despite the same asymptotic complexity.
- Every linked-list node carries pointer overhead (one or two extra words per element) —
  for small elements this can dominate the actual payload's memory footprint.
- A basic stack or queue doesn't support arbitrary-position access or search at all; if
  your access pattern isn't strictly LIFO or FIFO, you need a different structure.

## Alternatives
- **Dynamic arrays** (amortized analysis, `clrs/17`) — for a "queue" or "stack" workload
  that also occasionally needs random access or better cache locality, a growable array
  (like a Python list, Java ArrayList, or C++ vector) is often preferable to a linked
  list, trading O(n) worst-case (but O(1) amortized) growth for contiguous storage.
- **Deques (double-ended queues)** — support O(1) insert/remove at *both* ends, a
  generalization of stack and queue in one structure; implemented via a circular buffer
  or a doubly linked list.
- **Heaps / priority queues** (`clrs/07`) — for access patterns based on priority rather
  than insertion order (always remove the *smallest* or *largest*, not the *oldest* or
  *newest*).

## When to use it
Use a stack whenever the access pattern is inherently LIFO (recursion, undo history,
expression parsing, DFS via an explicit stack). Use a queue whenever it's inherently FIFO
(BFS, task scheduling, producer-consumer buffering). Use a linked list when insertions
and deletions at known, arbitrary positions dominate and you don't need random access
(implementing other structures' internals, maintaining an ordered set with frequent
splicing).

## When NOT to use it
Don't use a plain singly linked list when you need random access or frequent full scans
with cache-sensitive performance — a dynamic array will usually outperform it in
practice despite equal or better asymptotic complexity, due to memory locality. Don't use
a stack or queue where the required access pattern is priority-based rather than
order-based — that calls for a heap (`clrs/07`) instead.

## Key takeaways / mental model
Match the structure to the access pattern, not the other way around: LIFO -> stack, FIFO
-> queue, "I already have a pointer to where I need to insert/delete" -> linked list,
"I need to jump straight to element k" -> array. Sentinels remove special-casing from
linked-list code, at the cost of one extra dummy node.

## Self-check questions
1. Why is dequeue O(1) on a circular-buffer-backed queue but O(n) on a naive
   fixed-head array-backed queue? Trace through what has to move in each case.
2. Explain why a doubly linked list's insert/delete is O(1) "given a pointer to the
   node" but O(n) "given only a value to search for." What's the difference being
   measured in each case?
3. Describe a scenario (e.g. an LRU cache) where a doubly linked list's O(1)
   arbitrary-position removal is essential, and explain why an array wouldn't work as
   well there.
4. Why does CLRS introduce sentinel nodes for linked lists, and what specific class of
   bug do they eliminate?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 10: "Elementary
  Data Structures."
