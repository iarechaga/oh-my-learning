---
id: multiprocessor-programming/12
subject: multiprocessor-programming
title: Memory reclamation (hazard pointers, epochs)
slug: memory-reclamation
status: drafted
mastery:
seniority: staff
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 9 (with material drawn from Michael's hazard-pointer and Fraser's epoch-based reclamation papers)
prerequisites: [multiprocessor-programming/11]
created: 2026-08-10
updated: 2026-08-10
---

# Memory reclamation (hazard pointers, epochs)

## TL;DR
A lock-free data structure that physically unlinks and frees nodes has to answer a hard
question with no lock to help it: how do you know it's safe to free a node when other
threads might still hold a pointer to it, with no way to "ask" them? Hazard pointers
(each thread publishes which nodes it's currently touching; deferred frees are checked
against that published set) and epoch-based reclamation (threads mark themselves as
"in" or "out" of an epoch; memory freed in an old epoch is only reclaimed once every
thread has left it) are the two dominant answers, trading per-operation overhead against
batch-reclamation latency.

## The idea
`multiprocessor-programming/10` introduced ABA and `multiprocessor-programming/11`
walked through Treiber's stack and the Michael-Scott queue, both of which physically
unlink nodes from a shared structure — but neither said what happens to that unlinked
node's *memory*. In a garbage-collected language, this problem mostly disappears (the GC
won't reclaim memory while any reference to it exists, even a stale one a stalled thread
holds). In a manually-memory-managed language (C, C++, unsafe Rust), or in *any* language
when you need predictable, GC-pause-free performance, freeing a node the instant it's
unlinked is a serious bug: another thread may have read a pointer to that node
**just before** the unlink and be about to dereference it — a **use-after-free**, and (as
`multiprocessor-programming/10` showed) freed memory getting reallocated for a new
purpose is exactly the mechanism that turns into an ABA hazard. Memory reclamation
schemes solve this: how do you free memory that's no longer *logically* part of the
structure, without ever freeing it while some thread might still be *physically*
dereferencing it — all without a lock to coordinate the check?

## How it works

### Why "just free it" is unsafe
Consider a thread T1 in the middle of `pop()` on a Treiber stack: it has read
`old_top = node A` and is about to read `A.next`. Meanwhile thread T2 completes a `pop()`
of A itself (A is now unlinked) and, seeing no reason to keep it around, frees A's memory
immediately. T1's next step — dereferencing `A.next` — is now a read from freed memory:
undefined behavior at best (a crash), silent corruption at worst (if the freed memory
was already reallocated for something else and now contains unrelated data that T1
misinterprets as a valid `next` pointer). No lock protects this window because the whole
point of a lock-free structure is that no thread ever waits for another — but that same
property is exactly what makes "is it safe to free this yet?" hard to answer.

### Hazard pointers
**Idea:** each thread maintains a small, publicly visible set of **hazard pointers** — a
per-thread record of "which node(s) am I *currently* about to dereference." Before
dereferencing any pointer read from shared memory, a thread first publishes that pointer
into its own hazard-pointer slot (a shared, globally readable location, one or two slots
per thread is typical). Any thread that wants to free a node must first **scan all other
threads' published hazard pointers** and confirm the node isn't listed in any of them; if
it is, freeing is deferred.

**Mechanism, step by step:**
1. A thread that wants to dereference a pointer `p` read from shared memory first writes
   `p` into its own hazard-pointer slot (making its intent visible to everyone), then
   re-validates that `p` is still the value it expects (protecting against a race where
   `p` was already freed and reused *before* the hazard pointer was published — this
   re-check-after-publish pattern is essential).
2. The thread proceeds to use `p` normally.
3. When a thread unlinks a node, instead of freeing it immediately, it adds it to a
   **local retired list** (pending frees for that thread).
4. Periodically (e.g. when the retired list reaches some threshold size), the thread
   scans *every other thread's* published hazard pointers and frees any retired node that
   does not appear in that scanned set — nodes still hazardous to someone are left in the
   retired list for the next scan.

**Worked example.** T1 is about to dereference node A: it publishes `hazard[T1] = A`,
re-checks `top == A` (still valid), and proceeds to read `A.next`. Meanwhile T2 pops A
(unlinks it) and adds A to its retired list. Later, T2 decides to reclaim memory and
scans all threads' hazard pointers: it sees `hazard[T1] == A`, so it does **not** free A
yet, leaving it in the retired list. Once T1 finishes with A and clears its hazard
pointer (or moves it to something else), a later scan by any thread will find A no longer
hazardous to anyone, and it can finally be freed safely.

**Cost profile.** Hazard pointers add a write (publish) and a re-validation on essentially
every pointer dereference of a shared-structure node — real per-operation overhead — but
memory is reclaimed relatively promptly (as soon as no thread's hazard pointer references
it) and the technique needs only a small, bounded amount of shared metadata (a few slots
per thread), regardless of how many nodes exist.

### Epoch-based reclamation (EBR)
**Idea:** instead of tracking *which specific nodes* each thread might be touching
(hazard pointers' fine-grained approach), track a coarser signal: **which global "epoch"
each thread is currently active in.** A global epoch counter periodically advances; each
thread, whenever it's about to touch the shared structure, marks itself as "active in the
current epoch" and later marks itself inactive when done with that access. A node retired
(unlinked) during epoch E is only actually freed once every thread that could possibly
have seen it has since marked itself inactive from epoch E or earlier — meaning the
global epoch has been able to advance far enough that no live thread could still hold a
reference from that old epoch.

**Mechanism, step by step (simplified):**
1. Each thread has a local epoch counter, updated to match the global epoch when it
   begins a structure-touching operation (and typically marked "inactive"/unpinned when
   done).
2. A thread that retires (unlinks) a node tags it with the current global epoch and adds
   it to a per-epoch retired list.
3. Periodically, a thread checks whether *all* active threads' local epochs are at least
   as new as some old epoch E — if so, it's now provably safe to free everything retired
   during epoch E or earlier, because no thread could still be executing code from that
   stale epoch that might dereference those nodes.

**Cost profile.** EBR's steady-state overhead per operation is typically cheaper than
hazard pointers (marking "I'm active" is a single write per operation-batch, not a
per-dereference publish-and-revalidate), which is EBR's main appeal. Its downside: memory
reclamation is **batched and can be delayed arbitrarily** if even one thread stays
"active" for a long time (e.g. a thread that's preempted mid-operation, or simply slow) —
that one stalled thread can block reclamation of everything retired since it last became
active, a real practical risk EBR implementations must guard against (e.g. via timeouts
or forced epoch advancement heuristics).

### Comparing the two
| | Hazard pointers | Epoch-based reclamation |
| --- | --- | --- |
| Tracks | specific nodes per thread | coarse "which epoch am I in" per thread |
| Per-op overhead | higher (publish + revalidate per dereference) | lower (mark active/inactive per operation batch) |
| Reclamation promptness | prompt, node-by-node | batched, can be delayed by one slow thread |
| Vulnerable to a stalled thread? | only blocks reclamation of that specific node | can block reclamation of everything since that epoch |
| Metadata size | small, bounded (a few slots/thread) | small, bounded (one counter/thread) |

### Relationship to ABA
Both schemes are, among other things, a direct structural fix for the ABA problem's most
common real-world cause: as long as a node cannot be freed (and its memory address
recycled for an unrelated purpose) while any thread might still hold a stale reference to
it, the specific "A -> B -> A via memory reuse" scenario from
`multiprocessor-programming/10` cannot occur. Version tagging (`multiprocessor-programming/10`'s
other fix) and memory reclamation are complementary, not competing — many production
lock-free structures use both: reclamation to prevent use-after-free, tagging as defense
in depth against value-level ABA that isn't about memory reuse at all.

## Pros
- Both schemes make lock-free structures actually safe to run in manually-memory-managed
  languages, closing the use-after-free/ABA-via-reuse gap that the pseudocode in
  `multiprocessor-programming/11` glosses over.
- Bounded metadata overhead (a small number of hazard-pointer slots or one epoch counter
  per thread) regardless of the shared structure's size — scales to large structures
  fine.
- Both are largely reusable, structure-agnostic infrastructure: the same hazard-pointer
  or epoch machinery can protect many different lock-free structures in the same program.

## Cons
- Hazard pointers add real per-dereference overhead (publish + re-validate), which can be
  a meaningful cost in a hot path compared to a garbage-collected language's "just
  dereference it" simplicity.
- Epoch-based reclamation's batched, delayable reclamation means memory usage can spike
  unpredictably if any thread stalls for a long time while "active" — a genuine
  operational risk in systems with unpredictable scheduling or blocking I/O mixed into
  the same threads.
- Both schemes add non-trivial implementation complexity on top of an already-complex
  lock-free structure — a common reason teams choose a library implementation
  (`concurrent` collections in Java, `crossbeam-epoch` in Rust) rather than hand-rolling
  either scheme.

## Alternatives
- **Garbage collection** — in a GC'd language, this entire problem is handled for you: a
  node is reclaimed only once truly unreachable, including from stale references held by
  stalled threads. This is a major practical reason lock-free algorithms are notably
  easier to implement correctly in Java/Go/C# than in C/C++/unsafe Rust.
- **Reference counting** — each node carries an atomic reference count, incremented when
  a thread takes a reference and decremented when done, freed when it hits zero; simpler
  conceptually than hazard pointers or epochs, but atomic reference-count updates on
  every access add their own contention overhead, and naive reference counting doesn't
  handle certain lock-free access patterns (a thread reading a pointer without atomically
  incrementing a count first) safely without more care.
- **Never free (leak deliberately)** — acceptable only for bounded-lifetime programs or
  structures with a hard cap on total nodes ever created; not a general solution but
  occasionally the pragmatic choice for short-lived processes.

## When to use it
Use hazard pointers when reclamation promptness matters (bounded memory usage under
sustained load) and you can tolerate the per-dereference overhead. Use epoch-based
reclamation when steady-state per-operation cost matters more than reclamation latency,
and your threads reliably re-enter an "inactive" state frequently (no long stalls while
active) — this is the more common choice in high-throughput lock-free libraries today.

## When NOT to use it
Don't hand-roll either scheme for a one-off lock-free structure in a language/runtime
that already provides a well-tested implementation (Java's `java.util.concurrent`
collections, Rust's `crossbeam-epoch`/`crossbeam-skiplist`) — reuse the battle-tested
library rather than re-deriving these genuinely tricky correctness guarantees yourself.
Don't bother with either scheme at all in a garbage-collected language for structures
where GC pause characteristics are acceptable — the GC already solves this problem more
simply, and adding hazard pointers or epochs on top is redundant complexity.

## Key takeaways / mental model
Freeing a lock-free structure's unlinked node is unsafe unless you can prove no thread
still holds a stale reference to it — and there's no lock to ask. Hazard pointers answer
this with fine-grained, per-node "am I touching this right now?" publication, checked
before every free; epoch-based reclamation answers it with a coarser "which broad time
window am I active in?" signal, batching reclamation by epoch. Both are the missing piece
that makes `multiprocessor-programming/11`'s Treiber stack and Michael-Scott queue safe
to actually run in a manually-memory-managed setting, and both double as a structural
defense against the memory-reuse flavor of `multiprocessor-programming/10`'s ABA problem.

## Self-check questions
1. Explain precisely why "just free the node as soon as it's unlinked" is unsafe in a
   lock-free structure, using the Treiber-stack `pop()` scenario.
2. Walk through the hazard-pointer publish-then-revalidate sequence and explain why
   publishing alone (without the re-validation step) isn't sufficient.
3. Compare hazard pointers and epoch-based reclamation on per-operation overhead versus
   vulnerability to one stalled thread — which would you choose for a low-latency trading
   system with unpredictable OS scheduling jitter, and why?
4. Why does a garbage-collected language mostly sidestep this entire problem, and in what
   sense is that "for free" solution not available in C or unsafe Rust?

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 9: "Linked Lists: The
  Role of Locking" (node lifecycle and reclamation discussion).
- Maged M. Michael, "Hazard Pointers: Safe Memory Reclamation for Lock-Free Objects"
  (IEEE TPDS, 2004).
- Keir Fraser, "Practical Lock-Freedom" (PhD dissertation, University of Cambridge,
  2004) — origin of epoch-based reclamation.
