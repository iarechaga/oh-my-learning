---
id: algorithms-sedgewick/09
subject: algorithms-sedgewick
title: Hash tables (separate chaining and linear probing)
slug: hash-tables
status: drafted
mastery:
seniority: junior
source: Algorithms (Sedgewick, Wayne), Section 3.4
prerequisites: [algorithms-sedgewick/07, clrs/06]
created: 2026-08-10
updated: 2026-08-10
---

# Hash tables (separate chaining and linear probing)

## TL;DR
Sedgewick and Wayne cover the same two collision-resolution schemes as CLRS (`clrs/06`)
— separate chaining and linear probing — with extra attention to the practical
engineering of Java's/most languages' hashCode contract, resizing policy tied
symmetrically to load factor (both growing and shrinking), and a concrete, worked
comparison of when chaining's degrade-gracefully behavior beats linear probing's
better-when-uncrowded cache locality.

## The idea
CLRS's treatment (`clrs/06`) establishes the theory: expected O(1) operations under
simple uniform hashing and a bounded load factor. Sedgewick's treatment is more directly
tied to implementing a hash table in a real language with a real `hashCode`/`equals`
(or `__hash__`/`__eq__`) contract, and pays specific attention to two engineering details
that matter in practice: how resizing policy should be **symmetric** (shrink as well as
grow, avoiding the same kind of thrashing risk covered in
`algorithms-sedgewick/03`'s resizing-array stack) and how a poorly distributed
`hashCode` — even one that's technically deterministic and correct — can silently degrade
real-world performance despite a theoretically sound algorithm underneath.

## How it works

### The hashCode/equals contract
Any hash table implementation built on a general-purpose hash function relies on a
contract between the hash function and equality: **if two keys are equal, they must
produce the same hash code** (violating this breaks correctness outright — a key could
be inserted and then become unfindable) — but the reverse is not required (two unequal
keys *may* share a hash code; that's simply a collision, handled by the collision-
resolution scheme, not a correctness bug). A poor hash function that violates the "equal
keys, same hash" direction is a genuine correctness bug, not just a performance issue,
and this is a real, easy-to-introduce mistake when implementing a custom key type's hash
function alongside a custom equality method without keeping them consistent.

### Separate chaining, revisited with resizing
Each of M array slots holds a linked list (or, in some modern implementations for very
large chains, a small balanced tree, as Java's `HashMap` does past a size threshold) of
all keys hashing there. **Resizing policy:** when the average chain length grows too
long (Sedgewick suggests doubling M when the average number of keys per chain exceeds a
small constant, e.g. 8-10), double the table size and rehash every key into the new,
larger table — an O(n) operation, amortized (`clrs/17`) to O(1) per insertion across a
long sequence, exactly analogous to a dynamic array's amortized push cost
(`algorithms-sedgewick/03`).

### Linear probing, revisited with symmetric resize
Insert by probing sequentially from the hashed slot until an empty slot is found; search
similarly, stopping either at the key or at the first empty slot encountered (an empty
slot proves the key isn't present, since insertion would have stopped there). **Load
factor must be kept meaningfully below 1** (Sedgewick recommends resizing to keep it
around 1/2, not letting it approach 1, since linear probing's performance — average
probe length ~ (1 + 1/(1-alpha))/2 for successful search — degrades sharply, not
gracefully, as alpha approaches 1, unlike chaining). **Symmetric resizing** (doubling
when load factor gets too high, *and* halving when it drops too low after deletions)
mirrors exactly the resizing-array stack's shrink-at-1/4-not-1/2 policy
(`algorithms-sedgewick/03`) to avoid thrashing, applied here to hash-table capacity
instead of a stack's array capacity.

**Deletion under linear probing, the subtlety.** Naively marking a deleted slot "empty"
breaks future searches that probed *through* that slot to reach their actual target
(since an empty slot is treated as "definitely not present, stop searching") — Sedgewick's
fix is to, upon deletion, **remove the key and then re-insert every key in the same
cluster** (the contiguous run of occupied slots from the deleted slot's original hash
position onward) to restore correct probe-ability, rather than using a separate "deleted"
tombstone marker (an alternative CLRS mentions but Sedgewick treats as adding complexity
for arguably limited practical benefit at typical table sizes).

### Chaining vs. linear probing: a concrete practical comparison
| Property | Separate chaining | Linear probing |
| --- | --- | --- |
| Degrades under high load factor | Gracefully (chains get longer) | Sharply (probe
sequences get very long as alpha -> 1) |
| Memory overhead | One pointer per key (linked list nodes) | None per key, but must keep
some slots empty (alpha < 1) |
| Cache locality | Worse (chain nodes scattered) | Better (probes are sequential array
accesses) |
| Deletion | Simple (unlink from chain) | Requires cluster re-insertion or tombstones |

**The practical takeaway.** Linear probing's better cache locality can make it
meaningfully faster in practice when the load factor is kept comfortably low (its whole
performance story requires this discipline) — but chaining's graceful degradation makes
it more forgiving of a load factor that grows larger than planned, a real engineering
consideration when table size is hard to predict in advance or under adversarial growth.

## Pros
- Both schemes achieve expected O(1) operations under a well-distributed hash function
  and controlled load factor — matching CLRS's asymptotic result (`clrs/06`) while adding
  concrete implementation guidance.
- Symmetric resizing (grow and shrink, both amortized safely) prevents both unbounded
  memory growth from a temporary usage spike and thrashing from operations near a resize
  threshold — the same principled policy as the resizing-array stack
  (`algorithms-sedgewick/03`).
- Understanding the hashCode/equals contract explicitly prevents a specific, real, and
  easy-to-introduce class of correctness bug (custom key types with inconsistent hash and
  equality logic).

## Cons
- Linear probing's sharp performance degradation near load factor 1 makes it less
  forgiving than chaining if load factor isn't actively managed — a real operational risk
  if resizing policy is misconfigured or skipped.
- Chaining's per-key pointer overhead is a genuine memory cost, especially for hash
  tables storing many small keys.
- Linear probing's cluster-based deletion (re-inserting an entire cluster) is more
  complex to implement correctly than chaining's simple unlink, and is a common source of
  subtle bugs in from-scratch implementations.

## Alternatives
- **CLRS's chaining and open-addressing treatment** (`clrs/06`) — covers the same two
  schemes with additional open-addressing variants (double hashing) and the formal
  uniform-hashing analysis; complementary to this lesson's more implementation-focused
  view.
- **Cuckoo hashing** (not covered in either book's core treatment) — an alternative open-
  addressing scheme guaranteeing O(1) worst-case (not just expected) lookup, at the cost
  of more complex, occasionally-rehashing insertion.
- **Balanced search trees** (`algorithms-sedgewick/08`, `clrs/09`) — when ordered
  operations, not just key-value lookup, are needed.

## When to use it
Use separate chaining when load factor might grow unpredictably or deletion is frequent
(simpler, more forgiving under those conditions). Use linear probing when load factor is
actively managed and kept low, and cache-locality-driven speed is a priority (common in
performance-critical, memory-conscious implementations).

## When NOT to use it
Don't use linear probing without actively managing (and resizing to control) the load
factor — its performance cliff near alpha=1 is a real risk, not a theoretical edge case.
Don't implement a custom key type's hash function without also ensuring it's consistent
with that type's equality method — this is a correctness bug, not merely a performance
concern.

## Key takeaways / mental model
Both schemes deliver expected O(1) under a bounded load factor and well-distributed
hashing; chaining degrades gracefully and linear probing degrades sharply as load factor
rises, which should directly inform resizing policy. Symmetric grow-and-shrink resizing
(mirroring the dynamic array's amortized-analysis lesson) keeps a hash table's real-world
memory and performance behavior sound across its full usage lifecycle, not just during
growth.

## Self-check questions
1. Explain the hashCode/equals contract's asymmetric requirement (equal keys must share a
   hash code, but not vice versa) and why violating just the first direction is a
   correctness bug, not merely a performance issue.
2. Why does linear probing's average probe length grow sharply (not gracefully) as load
   factor approaches 1, while chaining's average chain length grows only linearly with
   load factor?
3. Walk through why naively marking a deleted slot "empty" under linear probing can break
   a subsequent search for an unrelated key, and how cluster re-insertion fixes this.
4. Why should a hash table's resizing policy be symmetric (shrink as well as grow), and
   what specific failure mode (referencing `algorithms-sedgewick/03`'s stack example)
   does a naive threshold choice risk?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 3.4: "Hash Tables."
