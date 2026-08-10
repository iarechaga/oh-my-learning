---
id: clrs/06
subject: clrs
title: Hash tables and expected-time lookup
slug: hash-tables
status: drafted
mastery:
seniority: junior
source: Introduction to Algorithms (CLRS), Chapter 11
prerequisites: [clrs/01, clrs/05]
created: 2026-08-10
updated: 2026-08-10
---

# Hash tables and expected-time lookup

## TL;DR
A hash table maps keys to array slots via a hash function, giving expected O(1) insert,
delete, and search — dramatically faster than a linked list's O(n) search — at the cost
of no ordering guarantee and a small chance of degraded performance from collisions. The
whole design revolves around managing collisions (two keys hashing to the same slot) and
keeping the load factor low.

## The idea
A direct-address table (an array indexed literally by the key value) gives O(1) access
but only works when keys are small integers in a known, dense range — you can't allocate
an array indexed by every possible string. A hash table generalizes this: a **hash
function** h maps an arbitrary key universe down to a small range of array indices
(0..m-1), so you get array-like O(1) expected access for arbitrary key types (strings,
tuples, objects) without needing an array sized to the entire key universe. The cost:
different keys can hash to the same slot (a **collision**), and the whole design's
quality depends on handling that gracefully.

## How it works

### Collision resolution: chaining
The simplest scheme: each slot holds a linked list (`clrs/05`) of all keys that hashed
there. Insert: compute h(key), prepend to that slot's list — O(1). Search: compute
h(key), then scan that slot's list — O(1 + length of the chain). Delete: search, then
unlink — same cost as search (O(1) with a doubly linked list once found, given the
sentinel trick from `clrs/05`).

**Load factor.** Define alpha = n/m, where n is the number of keys stored and m is the
number of slots. Under **simple uniform hashing** (the idealized assumption that any key
is equally likely to hash to any of the m slots, independent of other keys), the expected
length of any chain is alpha. So a search that doesn't find the key costs Theta(1 + alpha)
expected time; a search that does find it costs Theta(1 + alpha) as well (a standard,
slightly involved averaging argument over the elements already in the table). **If m is
kept proportional to n (i.e. alpha = O(1), a constant)**, every operation is expected
Theta(1) — the entire performance story of a hash table rests on this one assumption.

### Collision resolution: open addressing
Instead of chaining out to linked lists, open addressing stores every key directly in
the table's array itself, probing through a sequence of slots on collision. A **probe
sequence** h(key, 0), h(key, 1), h(key, 2), ... tries slot h(key,0) first; on collision,
tries h(key,1), and so on, until an empty slot is found (insert) or the key is found
(search) or an empty slot is hit without finding the key (search miss). This needs
alpha <= 1 always (you cannot store more keys than slots), and deletion is trickier
(naively marking a slot "empty" would break the probe sequence for keys that probed
through it — hence a special "deleted" marker distinct from "empty," or a full rehash on
delete).

**Linear probing** (h(key,i) = (h'(key) + i) mod m) is simple and cache-friendly (probes
are sequential in memory) but suffers from **primary clustering**: once a run of occupied
slots forms, any key hashing into that run makes the run longer, which makes it *more*
likely the next key will also collide into it — a snowballing effect that degrades
performance well before alpha approaches 1.

**Double hashing** (h(key,i) = (h1(key) + i*h2(key)) mod m) uses a second hash function
to determine the probe step size, so different keys' probe sequences diverge quickly
rather than following the same linear pattern — this largely avoids primary clustering
and gives probe behavior close to the idealized uniform-hashing assumption, at the cost
of computing two hash functions per key instead of one.

### The hash function itself: what makes one "good"
A good hash function should approximate simple uniform hashing — distributing keys
roughly evenly across slots regardless of the specific key set — and be fast to compute.
The **division method** (h(key) = key mod m) is fast but sensitive to poor choices of m
(e.g. if m is a power of 2, h only depends on the key's low-order bits, which correlate
badly for certain key patterns like memory addresses always being multiples of 4);
choosing m to be a prime not too close to a power of 2 usually avoids this. The
**multiplication method** (h(key) = floor(m * ((key*A) mod 1)) for a well-chosen
constant 0 < A < 1) is less sensitive to the choice of m. **Universal hashing** goes
further: rather than fixing one hash function, pick one at random (at table-construction
time) from a carefully designed family of functions, so that no adversary who knows your
hash function's *family* — but not the specific random pick — can construct a key set
that reliably produces worst-case collisions.

### The worst case, and why it's rarely hit in practice
If every key happens to hash to the same slot, a chained hash table degrades to a single
linked list — O(n) per operation, no better than not hashing at all. This is a genuine
worst case, not just a theoretical curiosity: an adversary who knows your exact hash
function can, in principle, construct a set of n keys that all collide (this is a real
denial-of-service vector against naive hash-table implementations exposed to
untrusted input, e.g. HTTP form-parameter names). Universal hashing and per-process
random hash seeding (used by most modern language runtimes, including Python and Java's
current string hashing) exist specifically to defend against this by making the
hash function unpredictable to an external attacker.

## Pros
- Expected O(1) insert, search, and delete — the fastest possible for a general
  key-value lookup structure not exploiting extra key structure (e.g. keys known to be
  small integers, where a direct-address table or a trie could do better).
- Works for arbitrary key types (strings, tuples, custom objects) given any hash function
  satisfying the basic uniform-distribution property.
- Simple to implement (chaining, especially) and simple to reason about once the load
  factor is understood.

## Cons
- No ordering guarantee — iterating a hash table gives keys in an arbitrary,
  implementation-dependent order, unlike a balanced search tree (`clrs/09`).
- Worst-case O(n) per operation is real, not just theoretical, and can be triggered
  adversarially against a predictable hash function — a genuine security concern for
  hash tables exposed to untrusted input.
- Resizing (growing the table as n grows to keep alpha bounded) requires rehashing every
  existing key, an O(n) operation — amortized cheaply (`clrs/17`) if growth is geometric,
  but a real latency spike on the resizing operation itself.
- Open addressing's performance degrades sharply as alpha approaches 1 (probe sequences
  get long), unlike chaining which degrades gracefully (chains just get a bit longer).

## Alternatives
- **Balanced search trees** (`clrs/09`) — O(log n) per operation (worse than hash tables'
  expected O(1)) but maintain sorted order and support range queries and ordered
  traversal, which hash tables cannot do at all.
- **Direct-address tables** — O(1) worst-case (not just expected) when keys are known to
  be small, dense integers — no hashing or collisions needed at all, but inapplicable to
  general key types.
- **Tries** (`algorithms-sedgewick/13`) — for string keys specifically, a trie gives
  O(key length) lookup with no collisions at all and supports prefix queries hash tables
  cannot.

## When to use it
Use a hash table whenever you need fast average-case key-value lookup, insertion, or
deletion and don't need sorted order or range queries — the default choice for
dictionaries, sets, caches, and de-duplication in most general-purpose code.

## When NOT to use it
Don't use a hash table when you need sorted iteration, range queries (e.g. "all keys
between X and Y"), or predecessor/successor queries — use a balanced search tree
(`clrs/09`) instead. Don't rely on a naive, non-randomized hash function for keys that
come from an untrusted or adversarial source without confirming your language runtime's
hash table already defends against worst-case collision attacks (most modern ones do, but
it's worth knowing why).

## Key takeaways / mental model
A hash table trades ordering for speed: expected O(1) if the load factor is kept
constant and the hash function approximates uniform distribution. Chaining degrades
gracefully under collisions; open addressing is faster in the good case but degrades
sharply as the table fills up. The worst case (O(n)) is real and, without randomized
hashing, exploitable.

## Self-check questions
1. Explain, using the load factor alpha = n/m, why keeping alpha = O(1) is what makes a
   chained hash table's expected operations O(1), and what has to happen (a resize) if n
   grows without bound while m stays fixed.
2. Compare linear probing and double hashing: what specifically causes primary
   clustering in linear probing, and how does double hashing avoid it?
3. Why is deletion trickier in open addressing than in chaining? What breaks if you
   naively mark a deleted slot as "empty"?
4. Explain why universal hashing (choosing the hash function randomly from a family at
   runtime) defends against an adversary who knows your hashing *algorithm* but not the
   specific random choice made for this run.

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 11: "Hash
  Tables."
