---
id: algorithms-sedgewick/03
subject: algorithms-sedgewick
title: Stacks, queues, and linked-list implementations
slug: stacks-queues-linked-lists
status: drafted
mastery:
seniority: junior
source: Algorithms (Sedgewick, Wayne), Section 1.3
prerequisites: [algorithms-sedgewick/02]
created: 2026-08-10
updated: 2026-08-10
---

# Stacks, queues, and linked-list implementations

## TL;DR
Sedgewick and Wayne treat stacks and queues as **abstract data types** (ADTs) first —
defined purely by their operations and behavior, independent of implementation — then
work through both a linked-list implementation and a resizing-array implementation for
each, making the implementation trade-offs (pointer overhead vs. amortized array growth)
concrete rather than abstract.

## The idea
CLRS's elementary data structures lesson (`clrs/05`) introduces stacks, queues, and
linked lists primarily as fixed structures with known complexity. Sedgewick's treatment
adds a genuinely useful engineering layer: separate the *interface* (push/pop, enqueue/
dequeue — what the client code sees and depends on) from the *implementation*
(linked-list-backed vs. array-backed — how it's actually built), and show that either
implementation can satisfy the same interface with the same asymptotic guarantees, while
differing in real, practical trade-offs (memory overhead, cache locality, worst-case vs.
amortized cost per operation).

## How it works

### The ADT discipline: interface before implementation
Define a stack purely by its contract: `push(item)` adds an item, `pop()` removes and
returns the most recently added item, `isEmpty()` and `size()` report state — with no
commitment yet to *how* these are implemented. Client code written against this
interface works unchanged regardless of which implementation backs it. This separation
is itself a design principle worth internalizing (echoed by clean-code's boundary and
interface guidance in the software-engineering domain), not just a stepping stone to the
specific data structure.

### Linked-list implementation
A stack backed by a singly linked list: `push` prepends a new node to the front
(O(1), no traversal needed), `pop` removes and returns the front node (O(1)). A queue
needs both a `head` (for dequeue) and `tail` (for enqueue) pointer to achieve O(1) for
both ends without traversal — enqueue appends at `tail`, dequeue removes from `head`.
This matches CLRS's linked-list treatment (`clrs/05`) operation-for-operation, but
Sedgewick emphasizes the **memory overhead** explicitly: every element carries an extra
pointer (or two, for a doubly linked list), which for small elements (e.g. a single
integer) can mean the pointer overhead exceeds the actual payload's size — a genuinely
practical cost that matters at scale and is easy to overlook when only reasoning
asymptotically.

### Resizing-array implementation
A stack backed by a plain array plus a `size` counter: `push` writes to `array[size++]`
(O(1) *if* the array has room); `pop` returns `array[--size]` (O(1)). When the array is
full, **resize** (allocate a new array of double the capacity, copy every element) —
this is exactly the dynamic array amortized-analysis case CLRS works through in detail
(`clrs/17`): amortized O(1) per push despite the occasional O(n) resize, achieved
specifically because capacity **doubles** (geometric growth) rather than growing by a
fixed increment.

**The "shrink too" refinement.** Sedgewick adds a subtlety CLRS's amortized-analysis
lesson doesn't dwell on: if you only ever grow the array (never shrink it on pop), a
stack that grows very large and then shrinks back down permanently wastes the peak
memory it once needed. The fix — halve the array's capacity when usage drops to 1/4 full
(not 1/2, which would cause **thrashing**: alternating push/pop right at a 1/2 threshold
would repeatedly grow and shrink on every single operation, destroying the amortized
guarantee) — restores amortized O(1) for *both* growing and shrinking sequences,
including ones that interleave both, while keeping the array's actual size within a
constant factor of what's currently needed.

**Why the 1/4 threshold specifically, not 1/2.** After halving at 1/4-full, the array is
now 1/2 full — meaning size would need to double again (which happens only once
capacity is 100% full) or halve again (which happens only if usage drops all the way
back down to 1/4 of the *new*, halved capacity, i.e. 1/8 of the original) before another
resize is triggered — a comfortable buffer that prevents any adversarial interleaving of
pushes and pops from triggering a resize on every single call, which is exactly the
property the amortized analysis needs to hold.

### Comparing the two implementations directly
| Aspect | Linked-list | Resizing array |
| --- | --- | --- |
| Per-operation worst case | O(1), every single call | O(n) occasionally (on resize) |
| Amortized cost | O(1) | O(1) |
| Memory overhead | One+ pointer per element | None per element, but some unused
capacity |
| Cache locality | Poor (nodes scattered) | Good (contiguous array) |

This table is the practical payoff of working through both implementations: **the same
asymptotic guarantee (amortized O(1)) can come with meaningfully different real-world
behavior**, and the right choice depends on whether worst-case-per-call latency or raw
throughput/memory efficiency matters more for a given application.

## Pros
- Separating interface from implementation lets client code remain stable while the
  underlying implementation is swapped or improved — a genuinely reusable software design
  lesson beyond the specific data structures.
- Having both a linked-list and resizing-array implementation of the same ADT makes the
  amortized-vs-worst-case and memory-overhead trade-offs concrete and comparable, rather
  than each structure being taught in isolation.
- The shrink-at-1/4 refinement is a subtle but important practical detail (avoiding
  thrashing) that a purely theoretical treatment of amortized analysis can easily skip
  past.

## Cons
- A resizing-array stack has genuine per-call latency variance (the occasional O(n)
  resize) that a linked-list stack never exhibits — a real difference for latency-
  sensitive applications, even though both are amortized O(1).
- The 1/4-threshold shrinking policy adds implementation complexity beyond the simplest
  possible resizing-array stack — easy to get wrong (e.g. picking 1/2 and inadvertently
  causing thrashing) if implemented without understanding why 1/4 specifically is safe.
- A linked-list implementation's pointer overhead is a real, constant per-element memory
  cost that doesn't show up in asymptotic analysis at all — invisible to Big-O but very
  visible in actual memory usage for large collections of small elements.

## Alternatives
- **CLRS's plain linked-list treatment** (`clrs/05`) — covers the same operations without
  the resizing-array counterpart or the shrink-threshold subtlety; a good foundation but
  less complete on the array-backed trade-offs.
- **Language built-in collections** (e.g. Java's `ArrayDeque`, Python's `collections.
  deque`) — production implementations that already apply these same resizing and
  shrinking strategies; understanding this lesson explains *why* they behave the way they
  do, rather than motivating a from-scratch reimplementation.

## When to use it
Use a resizing-array implementation when average throughput and memory efficiency matter
more than worst-case-per-call latency (the common case for most application code). Use a
linked-list implementation when a hard per-call worst-case bound is required, or when
elements are large enough that pointer overhead is a rounding error.

## When NOT to use it
Don't implement a stack/queue with a fixed-increment (rather than geometric) array growth
policy — it silently degrades amortized cost to linear, defeating the entire point of a
resizing array (see `clrs/17`'s dynamic-array analysis for why). Don't skip the
shrink-threshold logic entirely if your application's usage pattern grows and shrinks
repeatedly over a long lifetime — without it, peak memory usage is never released.

## Key takeaways / mental model
An ADT's interface (push/pop, enqueue/dequeue) is implementation-independent; a
linked-list backing gives worst-case-O(1) per call at the cost of pointer overhead and
poor cache locality, while a resizing array gives amortized-O(1) with occasional latency
spikes but better memory efficiency and cache behavior. Shrinking at 1/4 (not 1/2)
capacity avoids thrashing while still reclaiming memory after a usage drop.

## Self-check questions
1. Explain why doubling (not a fixed increment) is essential for a resizing array's
   amortized O(1) push, referencing the geometric-series argument from `clrs/17`.
2. Walk through exactly why shrinking at 1/2-full (rather than 1/4-full) capacity would
   cause thrashing under an alternating push/pop sequence right at that threshold.
3. Give a concrete scenario where a linked-list stack's worst-case-O(1)-per-call guarantee
   is worth its extra memory overhead compared to a resizing array's amortized guarantee.
4. Why does separating a stack's interface from its implementation matter for client code
   that uses the stack, even if the client never directly interacts with resizing or
   pointer logic?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 1.3: "Bags, Queues,
  and Stacks."
