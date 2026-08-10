---
id: multiprocessor-programming/11
subject: multiprocessor-programming
title: Lock-free stacks and queues
slug: lock-free-stacks-queues
status: drafted
mastery:
seniority: senior
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 10 and Chapter 11
prerequisites: [multiprocessor-programming/10]
created: 2026-08-10
updated: 2026-08-10
---

# Lock-free stacks and queues

## TL;DR
Treiber's stack pushes/pops via a single CAS on the top pointer, with a naturally clean
linearization point but bad scalability under high contention (every operation fights
over one shared word); the elimination-backoff stack fixes this by letting pushes and
pops that would cancel out "meet" and swap directly, without ever touching the shared
top. The Michael-Scott queue uses two CAS points (enqueue links the new node, then swings
the tail; dequeue swings the head) and needs a specific two-step technique to stay
linearizable even when the tail pointer temporarily lags behind.

## The idea
`multiprocessor-programming/10` gave you the CAS-retry loop and warned about ABA.
This lesson applies both directly to the two most fundamental lock-free data structures:
stacks and queues. These aren't just illustrative exercises — Michael-Scott's queue in
particular is close to what real production concurrent queue implementations (in Java's
`ConcurrentLinkedQueue`, for instance) are based on. Understanding these two algorithms in
depth is the concrete payoff of everything built up in `multiprocessor-programming/05`
through `multiprocessor-programming/10`: linearizability, progress guarantees, and CAS
mechanics all come together here in structures you can actually reason through
completely.

## How it works

### Treiber's lock-free stack
A stack is represented as a singly linked list with a shared `top` pointer. Each node
holds a value and a `next` pointer.

```
push(v):
    node = new Node(v)
    do {
        old_top = top.get()
        node.next = old_top
    } while (!CAS(top, old_top, node))

pop():
    do {
        old_top = top.get()
        if (old_top == null) return EMPTY
        new_top = old_top.next
    } while (!CAS(top, old_top, new_top))
    return old_top.value
```

**Linearization point.** For `push`, it's the successful CAS that installs the new node
as `top` — before that instant, the push hasn't happened; after, it has, atomically.
Same for `pop`'s successful CAS. This clean, single-instruction linearization point is
exactly what `multiprocessor-programming/05` described in the abstract — here it's
concrete and easy to point at.

**Worked example.** Stack starts empty (`top = null`). Thread A calls `push(1)`: reads
`old_top = null`, sets `node.next = null`, CAS succeeds, `top` now points to node(1).
Thread B concurrently calls `push(2)`: reads `old_top` — if it reads it *before* A's CAS,
B's `old_top = null` too, and B's `node.next = null`; B's CAS will only succeed if `top`
is still `null` when B's CAS executes. If A's CAS already landed, B's CAS fails (expected
`null`, actual is node(1)), so B retries: rereads `old_top = node(1)`, sets
`node(2).next = node(1)`, CAS succeeds. Final stack, top to bottom: 2, 1 — correct LIFO
order regardless of which thread's CAS actually won the race, because each retry always
rereads the current state before recomputing.

**The scalability problem.** Every `push` and every `pop` — regardless of what value is
involved — contends on the exact same shared `top` word. Under heavy concurrent load,
this becomes the same kind of single-hot-cache-line bottleneck `multiprocessor-programming/04`
described for naive spinlocks: most CAS attempts fail and retry, wasting work and
generating cache-coherence traffic, even though a push and a completely unrelated pop
have no logical reason to conflict with each other's *correctness* — they're just both
forced through the same single point of contention.

### The ABA hazard in Treiber's stack, revisited
This is precisely the scenario worked through in `multiprocessor-programming/10`: a
`pop()` that reads `old_top` and `new_top = old_top.next`, gets preempted, and later
CASes successfully even though `old_top`'s memory was freed and reallocated in between.
Production Treiber-stack implementations require a memory reclamation scheme
(`multiprocessor-programming/12`) specifically to prevent this — it's not an academic
footnote, it's a required part of a correct implementation.

### Elimination-backoff stack: turning contention into cooperation
The insight behind the **elimination-backoff stack**: under high contention, a `push` and
a concurrent `pop` are, in a sense, "made for each other" — if they could pair up
directly, the pop could simply take the value the push was about to add, without either
one ever touching the shared `top` at all, and the net effect on the stack's abstract
state is *as if* neither operation happened (push then immediately pop of the same value
leaves the stack unchanged) — which is a perfectly valid linearization.

**Mechanism.** Add a small auxiliary **elimination array** of "exchange slots." When a
thread's CAS on the main `top` fails (signaling contention), instead of immediately
retrying the CAS, it posts its operation (push with its value, or pop) to a randomly
chosen slot in the elimination array and waits briefly. If another thread posts a
complementary operation to the same slot within a short window, the two threads exchange
the value directly (pop reads the value the push posted) and both return immediately,
having "elided" the shared stack entirely for this operation. If no match happens within
the window, the thread falls back to retrying the normal Treiber CAS loop.

This is a direct application of the backoff idea from `multiprocessor-programming/04`
(don't hammer the same contended location; back off and try something less contended),
specialized cleverly for stacks: instead of *waiting* during backoff, threads use the
backoff window productively to look for a direct pairing. Under high contention this can
dramatically outperform plain Treiber, since many operations complete without ever
touching the shared `top` at all; under low contention, elimination rarely triggers and
the algorithm behaves like plain Treiber with a small constant overhead for checking the
elimination array.

### Michael-Scott lock-free queue
A queue needs both `head` (for dequeue) and `tail` (for enqueue) pointers, plus a subtlety
neither pointer alone can solve: a naive single-CAS-per-pointer design has a race where a
new node is linked into the list but the `tail` pointer hasn't yet been updated to point
to it, and a concurrent enqueue reading a stale `tail` would corrupt the list. The
**Michael-Scott (M&S) queue** solves this with a dummy/sentinel head node and a careful
two-step enqueue.

```
enqueue(v):
    node = new Node(v)
    loop:
        last = tail.get()
        next = last.next.get()
        if (last == tail.get()):       // tail hasn't moved since we read it
            if (next == null):          // last really is the last node
                if (CAS(last.next, null, node)):   // step 1: link the new node
                    CAS(tail, last, node)           // step 2: try to swing tail (may fail, OK)
                    return
            else:
                CAS(tail, last, next)   // tail was lagging; help move it forward, then retry

dequeue():
    loop:
        first = head.get()
        last = tail.get()
        next = first.next.get()
        if (first == head.get()):
            if (first == last):         // queue looks empty or tail is lagging
                if (next == null): return EMPTY
                CAS(tail, last, next)   // help move tail forward, then retry
            else:
                value = next.value
                if (CAS(head, first, next)): return value
```

**Why two CAS steps for enqueue.** Step 1 (linking the new node onto `last.next`) is the
*true* linearization point of enqueue — the moment the new node becomes reachable from
the list. Step 2 (swinging `tail` to point at the new node) is purely a **performance
optimization**, not required for correctness of the immediate operation: even if step 2
is delayed or fails (the enqueuing thread gets preempted right after step 1), the queue's
structure is still fully correct and traversable — `tail` is just temporarily "lagging"
one node behind reality. This is why every other thread's enqueue/dequeue includes a
"tail is lagging, help move it forward" step (the `CAS(tail, last, next)` calls) — any
thread that notices a lagging tail **helps** advance it before proceeding with its own
operation, a lightweight version of the "helping" pattern from
`multiprocessor-programming/08`'s universal constructions. This guarantees the queue
stays lock-free: even if the original enqueuing thread that linked the node is
permanently stalled, some other thread will notice and finish swinging `tail` for it.

**Worked example: lagging tail.** Queue has sentinel -> A (head at sentinel, tail at A).
Thread 1 enqueues B: reads `last = A`, `next = A.next = null`, CASes `A.next` from null
to B (step 1 succeeds — B is now reachable: sentinel -> A -> B). Thread 1 is preempted
before step 2 (`tail` is still pointing at A, not B — lagging by one node). Thread 2
concurrently tries to enqueue C: reads `last = tail.get() = A`, reads
`next = A.next.get() = B` (not null!) — this tells Thread 2 that `tail` is stale (A is
not actually the last node; B is). Instead of trying to link after A (which would be
wrong), Thread 2 executes the "help" branch: `CAS(tail, A, B)`, advancing `tail` to the
correct current last node, then loops back and retries its own enqueue from scratch —
now correctly linking C after B. The queue stays perfectly correct and linearizable
throughout, even though Thread 1 never got to run its own step 2.

## Pros
- Treiber's stack is small and easy to fully understand and prove correct — an excellent
  teaching example for the CAS-retry pattern and linearization points in a real structure.
- Elimination-backoff dramatically improves scalability under contention by turning
  colliding operations into direct, shared-top-free exchanges instead of wasted retries.
- Michael-Scott's queue is genuinely production-grade — the "help advance a lagging tail"
  pattern is a clean, teachable instance of lock-free helping that guarantees system-wide
  progress even if one thread stalls mid-operation.

## Cons
- Plain Treiber's stack scales poorly under contention — the single shared `top` is a hot
  spot exactly like a naive spinlock's shared word (`multiprocessor-programming/04`).
- Elimination-backoff adds real implementation complexity (the auxiliary exchange array,
  tuning the wait window) for a benefit that only materializes under genuinely high
  contention; at low contention it's pure overhead.
- Both structures require careful memory reclamation (`multiprocessor-programming/12`) to
  avoid ABA and use-after-free — none of the pseudocode above is safe to run as-is in a
  manually-memory-managed language without that additional layer.

## Alternatives
- **Lock-based stack/queue** (`multiprocessor-programming/06`'s techniques adapted, or
  simple coarse-grained locking) — much simpler to implement correctly, and often
  competitive in performance at low-to-moderate contention; the lock-free versions only
  clearly win when contention and progress-guarantee requirements are both high.
- **Bounded ring-buffer queues** — for fixed-capacity queues, a ring buffer with atomic
  head/tail indices can be simpler and faster than a linked-list-based M&S queue, at the
  cost of a fixed maximum capacity.

## When to use it
Use Treiber's stack (or a library implementation of it) for a simple lock-free LIFO
structure under low-to-moderate contention. Reach for elimination-backoff specifically
when profiling shows the plain Treiber stack is contention-bound with roughly balanced
push/pop traffic (elimination only helps when pushes and pops can actually pair up).
Use the Michael-Scott queue (or a library based on it) whenever you need a general-
purpose, unbounded, lock-free FIFO queue with strong progress guarantees.

## When NOT to use it
Don't reach for elimination-backoff's added complexity when contention is low or when
your workload is push-heavy or pop-heavy with little balance between the two (elimination
can't help if there's rarely a complementary operation to pair with). Don't use an
unbounded linked-list queue (M&S) when a fixed maximum size is acceptable and predictable
low latency matters more than unbounded capacity — a bounded ring buffer is usually
simpler and faster in that case.

## Key takeaways / mental model
Treiber's stack is "read top, compute, CAS top" — simple, correct, but contention-bound
on one shared word; elimination-backoff relieves that contention by letting opposite
operations cancel out directly instead of fighting over the shared pointer. Michael-Scott's
queue separates the *true* linearization point (linking a node) from a *performance-only*
step (swinging tail), and relies on every other thread helping advance a lagging tail —
this is what keeps it lock-free even if the original enqueuer stalls. Both structures are
concrete proof that the abstract ideas from `multiprocessor-programming/05` through
`multiprocessor-programming/10` (linearization points, progress guarantees, CAS
mechanics, ABA) compose into real, usable, provably-correct data structures.

## Self-check questions
1. Identify the exact linearization point of Treiber's `push` and `pop`, and explain why
   it is a single CAS instruction in each case.
2. Explain how elimination-backoff can let a push and a pop both "succeed" without either
   one ever touching the shared `top` pointer, and why this is still a valid
   linearization of the stack.
3. Walk through the Michael-Scott enqueue's two-step design: why is swinging `tail` a
   performance optimization rather than a correctness requirement, and what mechanism
   ensures it eventually happens even if the original enqueuing thread stalls forever?
4. Why do both Treiber's stack and the Michael-Scott queue require a memory reclamation
   strategy in a manually-memory-managed language, even though the pseudocode itself
   never explicitly frees anything?

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 10: "Concurrent
  Queues and the ABA Problem."
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 11: "Concurrent
  Stacks and Elimination."
