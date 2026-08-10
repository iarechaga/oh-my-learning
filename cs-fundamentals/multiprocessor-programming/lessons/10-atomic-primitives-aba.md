---
id: multiprocessor-programming/10
subject: multiprocessor-programming
title: Atomic primitives (CAS, FAA) and ABA hazards
slug: atomic-primitives-aba
status: drafted
mastery:
seniority: senior
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 5 and Chapter 10
prerequisites: [multiprocessor-programming/09]
created: 2026-08-10
updated: 2026-08-10
---

# Atomic primitives (CAS, FAA) and ABA hazards

## TL;DR
Compare-and-swap (CAS) and fetch-and-add (FAA) are the hardware atomic instructions
nearly every lock-free algorithm is built on. CAS's core weakness is the **ABA
problem**: a location can change from A to B and back to A between a thread's read and
its CAS, and the CAS succeeds even though the underlying structure was mutated in a way
that matters — fixed by tagging values with a version counter, using hazard pointers, or
using a hardware double-word CAS.

## The idea
`multiprocessor-programming/09` established that CAS has infinite consensus number,
making it the primitive of choice for general lock-free and wait-free algorithms. This
lesson gets concrete and practical: what exactly does CAS do at the machine level, how do
you build the classic "read, compute, CAS, retry-on-failure" loop that appears throughout
`multiprocessor-programming/06` and `multiprocessor-programming/11`, and — critically —
what is the ABA problem that silently breaks a naive CAS-based algorithm even when every
individual CAS call succeeds honestly? This last question is the single most common
subtle bug in real-world lock-free code, and understanding it is what separates "I used
CAS" from "I used CAS correctly."

## How it works

### Compare-and-swap (CAS), precisely
`CAS(location, expected, new)` atomically: reads `location`'s current value; if it equals
`expected`, writes `new` to `location` and returns true (success); otherwise, leaves
`location` unchanged and returns false (failure) — all as one indivisible hardware step,
with no other thread able to observe or interleave with it. This is the building block
for the ubiquitous **CAS-retry loop**:

```
do {
    old = location.get()
    new = compute_new_value(old)
} while (!CAS(location, old, new))
```

The loop keeps retrying until it CASes successfully — i.e., until it manages to apply its
computed update starting from a value that is still current at the exact instant the CAS
executes. If another thread's CAS wins the race in between, this thread's `old` is now
stale, its CAS fails, and it loops back to re-read and recompute.

### Fetch-and-add (FAA)
`FAA(location, delta)` atomically adds `delta` to `location` and returns the *previous*
value, as one indivisible step. For simple numeric accumulation (counters, generating
unique sequence numbers), FAA is both simpler and often cheaper in hardware than a CAS-
retry loop, because it never fails/retries — it always succeeds in one step, with the
hardware itself serializing concurrent FAA calls. Note from
`multiprocessor-programming/09`: FAA has consensus number 2, strictly weaker than CAS's
infinity — FAA is the right tool for simple accumulation, but it cannot serve as the
general-purpose consensus-solving primitive that CAS can.

### The ABA problem
The CAS-retry loop's correctness silently assumes: "if `location` still equals `old` at
CAS time, nothing relevant has changed since I read it." **This assumption can be false.**
Suppose a thread reads `location == A`, computes its update, but before its CAS executes,
two *other* things happen: another thread changes `location` from A to B, and then a
third change (possibly the same or another thread) changes it back from B to A. The
original thread's CAS now sees `location == A` — matching its stale `expected` value —
and succeeds, even though the location was *not* stable the whole time; something
meaningful happened in between that the CAS's simple equality check cannot detect.

**Worked example: ABA corrupting a lock-free stack pop.** A lock-free stack
(`multiprocessor-programming/11`) implements `pop()` roughly as: read `top` (call it node
A, whose `next` pointer points to node B); CAS `top` from A to `A.next` (i.e. B),
completing the pop of A.
1. Thread 1 calls `pop()`: reads `top == A`, reads `A.next == B` (its intended new top).
2. Thread 1 is preempted right before its CAS.
3. Thread 2 runs to completion: pops A (top becomes B), pops B (top becomes some node C),
   then pushes a **freshly allocated node that happens to reuse A's memory address**
   (common with memory allocators that recycle freed memory) back onto the stack — now
   `top == A` again, but this "A" node's `next` pointer now points to C, not the original
   B.
4. Thread 1 resumes: its CAS compares `top` to its remembered `expected = A`. It matches
   (memory reuse means the address is literally the same), so the CAS succeeds — setting
   `top = B`, using Thread 1's *stale* `A.next` value from step 1.

The result: `top` is now set to `B`, a node that was already popped and may be freed,
garbage, or reused elsewhere — the stack's `top` pointer is now corrupted, pointing at
memory that isn't part of the stack's live structure at all. This is a genuine, serious
bug (potential use-after-free or silent structural corruption), and note carefully: **every
individual CAS call in this trace succeeded "honestly"** — there's no way to detect the
problem by looking at CAS's return value alone. The bug is entirely about *what happened
in between* the read and the CAS, invisible to a simple equality check.

### Fix 1: version tagging (the ABA counter)
Pair every mutable pointer/value with a **version counter** that increments on every
modification, and CAS the *combined* (value, version) pair atomically (requiring a
double-width CAS instruction, e.g. `CAS128` on 64-bit pointers, or packing a smaller
counter into spare pointer bits). Now, even if the *value* cycles A -> B -> A, the
*version* strictly increases each time, so the combined (A, v1) the reader saw no longer
matches the current (A, v3) by the time its CAS executes — the CAS correctly fails,
forcing a retry with fresh data instead of silently succeeding on stale assumptions. This
is the classic, most direct fix, but requires hardware/language support for a wide-enough
atomic CAS to hold both the value and a counter together.

### Fix 2: hazard pointers / safe memory reclamation
A different angle: if freed memory is never actually reused (or reused only after
provably no thread can still be referencing it), the specific "A's address got recycled
for an unrelated node" scenario above cannot happen. This is exactly what
`multiprocessor-programming/12`'s memory reclamation schemes (hazard pointers, epoch-
based reclamation) provide — they don't fix ABA directly, but they eliminate the most
common real-world *cause* of ABA (premature reuse of a freed node's memory address) by
deferring reclamation until safety is proven.

### Fix 3: avoid the pattern entirely (immutable nodes, or don't recycle)
Some designs sidestep ABA by never physically reusing a memory address for a
semantically different purpose while any thread could still hold a stale reference to it
— e.g., using a garbage-collected language (the GC won't reclaim an object's memory while
any reference to it, even a "stale" one a stalled thread still holds, potentially
exists), or by simply never freeing nodes (acceptable only in specific bounded-lifetime
scenarios). This is why ABA is a much more visible, painful problem in manually-memory-
managed languages (C, C++, Rust's `unsafe` code) than in garbage-collected ones (Java, Go)
— though it is not *entirely* eliminated even under GC, since the value cycling A->B->A
can still happen for reasons unrelated to memory reuse (e.g. a counter genuinely
returning to a prior value through legitimate increments and decrements).

## Pros
- CAS-retry loops are simple to write and, combined with `multiprocessor-programming/09`'s
  universal consensus power, form the backbone of essentially all practical lock-free
  algorithms.
- FAA gives a cheaper, non-retrying alternative for the common special case of simple
  numeric accumulation, avoiding CAS-retry overhead entirely when full CAS generality
  isn't needed.
- Once understood, the ABA problem and its standard fixes (version tagging, safe memory
  reclamation) are a small, well-known, learnable checklist — not a mysterious source of
  unbounded new bugs once you know to look for it.

## Cons
- ABA is exactly the kind of bug that's invisible in ordinary testing (it requires a
  specific, narrow interleaving plus memory reuse to manifest) and can lie dormant for a
  long time before surfacing in production under real contention.
- Version-tagging fixes require wide (double-word) CAS support, which not all
  architectures/languages provide as conveniently as single-word CAS.
- CAS-retry loops can degrade under high contention (many failed retries,
  `multiprocessor-programming/04`'s contention concerns apply here too), unlike FAA which
  never needs to retry.

## Alternatives
- **Load-linked/store-conditional (LL/SC)** — some architectures provide this instead of
  CAS; it has a subtly different (and in some ways stronger) guarantee that can avoid ABA
  more directly (a store-conditional fails if *anything* wrote to the location since the
  load-linked, not just if the value differs), at the cost of being unavailable on
  CAS-only architectures.
- **Transactional memory** (`multiprocessor-programming/13`) — sidesteps hand-written
  CAS-retry loops and their ABA hazards entirely by letting the runtime detect conflicts
  at a higher level, at the cost of its own performance and implementation trade-offs.

## When to use it
Use CAS-retry loops whenever building a lock-free algorithm that needs to conditionally
update shared state based on its current value (the general case). Use FAA specifically
for simple monotonic accumulation (counters, ticket/sequence number generation) where its
non-retrying, always-succeeds property is a clean win over a full CAS loop.

## When NOT to use it
Don't write a CAS-retry loop against a pointer-based structure (linked lists, stacks,
queues) without an explicit ABA mitigation plan (version tagging or a memory reclamation
scheme from `multiprocessor-programming/12`) — assuming "the CAS succeeded, so nothing
changed" is the single most common correctness bug in lock-free pointer-based code. Don't
reach for FAA when the update logic is anything more than "add a fixed delta" — anything
conditional or dependent on the current value in a more complex way needs CAS, not FAA.

## Key takeaways / mental model
CAS's "does the current value still match what I expect?" check is only as strong as its
ability to *detect change* — and a value cycling A -> B -> A defeats a plain equality
check, which is exactly the ABA problem. The fix is always some form of "make it
impossible or detectable for the value to genuinely return to an indistinguishable A" —
either via a version counter riding along with the value, or by ensuring memory (and
therefore addresses) can't be silently recycled out from under a stalled thread
(`multiprocessor-programming/12`). Every individual CAS in an ABA-affected trace succeeds
honestly; the bug is entirely in the unnoticed history between read and CAS.

## Self-check questions
1. Walk through the stack-pop ABA example step by step and pinpoint exactly which
   assumption Thread 1's CAS silently relies on that turns out to be false.
2. Why doesn't checking the CAS's boolean return value alone ever reveal an ABA problem
   has occurred?
3. Explain how a version counter fixes ABA — specifically, what does it change about what
   the CAS is actually comparing?
4. Why is ABA a more prominent practical concern in manually-memory-managed languages
   than in garbage-collected ones, and in what narrow sense can it still occur even under
   garbage collection?

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 5: "The Relative
  Power of Primitive Synchronization Operations."
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 10: "Concurrent
  Queues and the ABA Problem."
