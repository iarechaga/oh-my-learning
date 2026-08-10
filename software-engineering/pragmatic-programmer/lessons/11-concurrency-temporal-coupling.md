---
id: pragmatic-programmer/11
subject: pragmatic-programmer
title: Concurrency and Temporal Coupling
slug: concurrency-temporal-coupling
status: drafted
mastery:
seniority: senior
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 6
prerequisites: [pragmatic-programmer/04]
created: 2026-08-10
updated: 2026-08-10
---

# Concurrency and Temporal Coupling

## TL;DR
Temporal coupling is the hidden assumption that things happen in a specific *order* or at a specific *time* — an assumption that's invisible in sequential code and lethal once concurrency enters the picture. The fix is to design for concurrency deliberately: identify what can genuinely happen in parallel, and protect shared state with explicit, minimal-scope synchronization rather than implicit ordering.

## The idea
Sequential code has an easy, seductive property: statement order *is* the execution order, so "A happens, then B happens" is guaranteed just by writing A before B. This creates an invisible habit — relying on that ordering as if it were a *design decision* rather than an accident of writing code top-to-bottom. The moment two pieces of that "sequence" actually need to run concurrently (multiple threads, async tasks, distributed services), any hidden assumption about relative timing becomes a live bug, and because it depends on timing, it often only manifests intermittently — the worst kind of bug to diagnose (see Lesson 08).

The book's framing: **decouple time the same way you decouple everything else** (Lesson 04). Ask explicitly, for every pair of operations: "does B genuinely need A to finish first, or did I just happen to write it after A?" If the answer is "no real dependency," they're candidates to run concurrently for better throughput. If the answer is "yes, genuinely," that dependency needs to be *explicit and enforced* (a lock, a queue, an await), not left as an accident of source-code ordering.

## How it works

### Spotting temporal coupling
A concrete test: could two operations run in the opposite order, or simultaneously, without changing the result? If yes, they're temporally *independent* — safe to parallelize. If no, there's a real dependency that needs explicit enforcement once concurrency is introduced.

**Worked example.** A checkout flow: (1) charge the customer's card, (2) send a confirmation email, (3) decrement inventory.
- Is (2) genuinely dependent on (1) finishing first? Only in the sense that you don't want to email "your order is confirmed" before the charge succeeds — a real business dependency, not an accident. This needs explicit sequencing (or a guard: only enqueue the email after a successful charge event).
- Is (3) dependent on (2)? No — decrementing inventory has nothing to do with whether the email was sent. In sequential code, someone likely still wrote them in a fixed order out of habit, creating an *accidental* temporal coupling: if inventory decrement is slow or fails, it shouldn't block or be blocked by email sending, and in a concurrent redesign these two can safely run independently (e.g., as separate async tasks or queue consumers), improving throughput with zero correctness risk.

### Shared mutable state is where concurrency bugs actually live
Concurrency bugs almost never come from "running things at the same time" in the abstract — they come from **two concurrent operations touching the same mutable state without coordination**. The book's practical advice:
- **Minimize shared state.** The less mutable state two concurrent operations share, the less there is to coordinate, and the fewer ways to get it wrong. Prefer passing immutable data or using isolated, per-task state where possible.
- **Protect what must be shared, explicitly and narrowly.** When shared mutable state is unavoidable (a counter, a cache, a connection pool), guard it with the narrowest synchronization that correctly protects it — a lock scoped tightly around the actual read-modify-write, not sprayed broadly "to be safe," since overly broad locking reintroduces the very sequential bottleneck concurrency was meant to remove.

**Worked example — a classic race.** Two concurrent requests both run `balance = read_balance(); balance -= 10; write_balance(balance)` for the same account, with no lock.
```
Thread 1: read_balance() -> 100
Thread 2: read_balance() -> 100          (reads before Thread 1 writes back)
Thread 1: balance = 100 - 10 = 90; write_balance(90)
Thread 2: balance = 100 - 10 = 90; write_balance(90)   <- should be 80, not 90!
```
Both withdrawals "succeeded" from each thread's point of view, but one withdrawal was silently lost — a classic lost-update race caused entirely by unsynchronized shared mutable state, invisible in any single-threaded test and only manifesting under real concurrent load. Fix: make the read-modify-write atomic (a single `UPDATE balance = balance - 10 WHERE id = ...` at the database, or an application-level lock scoped exactly around this critical section) — narrow enough not to serialize unrelated accounts' updates, but covering the entire read-modify-write of *this* account.

### The "no ordering guarantee unless you enforce it" default
The book's practical rule of thumb for anything concurrent: **assume nothing about ordering, timing, or completion unless something in the system explicitly guarantees it.** Two async tasks fired "at roughly the same time" may complete in either order, may interleave arbitrarily, and may even both be mid-flight simultaneously touching shared resources — code that "usually works" because one order happens to be common in testing is not correct code, it's a bug waiting for production load patterns (higher concurrency, different network timing) to expose it.

## Pros
- Explicit synchronization around genuinely necessary dependencies produces code whose correctness doesn't depend on load-dependent timing luck.
- Removing *accidental* temporal coupling (like the email/inventory example) unlocks real parallelism and throughput gains for free.
- Naming the actual dependency explicitly (a queue, an await, a lock) documents intent for future readers far better than "this happens to work because of the order I wrote it in."

## Cons
- Correct concurrent design has a real cognitive cost — reasoning about interleavings is harder than reasoning about sequential code, and it's easy to get subtly wrong (see Lesson from `multiprocessor-programming` and `java-concurrency` in the cs-fundamentals domain for the deeper theory).
- Synchronization primitives (locks, semaphores) introduce their own risks — deadlocks, contention bottlenecks — if scoped incorrectly.
- Over-parallelizing operations that have low actual independent value (tiny units of work) can lose more to coordination overhead than it gains in throughput.

## Alternatives
- **Immutable data + message passing (actor model, CSP-style concurrency)** — avoid shared mutable state entirely by communicating through message queues between isolated units, sidestepping most lock-based hazards at the cost of a different mental model and message-ordering considerations of its own.
- **Software transactional memory / database transactions** — let the underlying system provide atomicity guarantees (e.g., a DB transaction wrapping the read-modify-write) instead of hand-rolled application-level locking, trading some performance for much lower risk of a hand-written locking bug.
- **Single-threaded event loops** (e.g., Node.js's model) — sidestep most shared-mutable-state races by design, at the cost of needing careful handling of long-running work so it doesn't block the single thread.

## When to use it
Deliberately look for temporal coupling whenever you're deciding whether two operations can run concurrently, or whenever you're introducing concurrency into previously sequential code (splitting a batch job across workers, moving from synchronous to async request handling). Always ask "what shared state does this touch, and is it protected?" before trusting any concurrent code path.

## When NOT to use it
Don't introduce concurrency into a genuinely sequential, low-volume workflow just because it's theoretically possible — the coordination complexity and bug surface it adds usually isn't worth it unless there's a real throughput or latency need driving it.

## Key takeaways / mental model
For every "A then B" you find in code that's about to become concurrent, ask: "is this a real dependency, or just the order I happened to type it in?" Real dependencies need explicit, minimal-scope enforcement (locks, queues, awaits); accidental ones are free parallelism waiting to be unlocked. And treat any shared mutable state touched by more than one concurrent path as guilty until proven protected.

## Self-check questions
1. Using the checkout example, identify one more pair of operations that might have accidental (rather than real) temporal coupling, and explain how you'd verify which it is.
2. Walk through the lost-update race step by step and explain exactly which line of interleaving causes the bug.
3. Why is "it passed all our tests" weak evidence that concurrent code is correct?
4. Give an example of over-broad locking that hurts throughput more than it needs to, and describe how you'd narrow its scope.

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 6: "Concurrency" (Breaking Temporal Coupling section).
- See also: `cs-fundamentals/java-concurrency` and `cs-fundamentals/multiprocessor-programming` for the deeper theory of thread safety and concurrent data structures.
