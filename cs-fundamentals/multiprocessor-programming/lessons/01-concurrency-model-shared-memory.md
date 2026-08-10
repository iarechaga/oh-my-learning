---
id: multiprocessor-programming/01
subject: multiprocessor-programming
title: Concurrency model and shared-memory assumptions
slug: concurrency-model-shared-memory
status: drafted
mastery:
seniority: mid
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 1 and Chapter 4
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Concurrency model and shared-memory assumptions

## TL;DR
Multiprocessor programming assumes several independent threads run truly in parallel
(not just interleaved on one core) and communicate by reading and writing a shared
address space. Every algorithm in this subject rests on a precise model of what
"reading and writing shared memory" actually guarantees — and real hardware guarantees
far less than intuition suggests, which is why naive concurrent code breaks.

## The idea
Sequential programming has one mental model: a single stream of instructions executes
one at a time, each fully finished before the next starts. Concurrent programming breaks
that model in two ways at once. First, **true parallelism**: on a multicore or
multiprocessor machine, threads are not just time-sliced illusions of simultaneity —
they genuinely execute at the same instant on different cores, touching the same memory.
Second, **interleaving unpredictability**: even without true parallelism (e.g. a single
core switching between threads), the operating system can pause a thread at literally
any point between two machine instructions, so a "simple" operation like `counter++`
(which is really read, add one, write) can be interrupted halfway through by another
thread doing the same thing.

Before you can reason about *any* concurrent algorithm — a lock, a queue, a stack — you
need a precise answer to a deceptively hard question: when thread A writes a value and
thread B later reads it, what is B guaranteed to see? The intuitive answer ("whatever A
last wrote, obviously") is wrong on real hardware unless specific mechanisms are used.
This lesson establishes the model the rest of the subject builds on: what shared memory
means, what threads are allowed to do to it, and which assumptions are safe defaults
versus which require explicit synchronization.

## How it works

### The asynchronous shared-memory model
The book's baseline model (and the one most concurrent algorithms are proven correct
under) is **asynchronous shared memory**:
- A fixed set of **threads** (or processes — the book uses the terms loosely
  interchangeably at this level), each executing its own sequential program.
- A shared set of **memory locations** (registers/variables/objects) that any thread can
  read or write.
- **Asynchrony**: no assumption about relative speed. A thread can be paused for an
  arbitrarily long time between any two of its steps (preempted by the OS scheduler, or
  slowed by a cache miss, a page fault, or contention) and then resumed. An algorithm
  that only works if threads run at roughly the same speed is not correct in this model
  — it must work under *every* possible interleaving/timing, including the adversarial
  ones where one thread stalls for an arbitrarily long time right when it is least
  convenient.

This "assume the worst-case adversarial scheduler" stance is deliberate: if an algorithm
is proven correct under total asynchrony, it is correct on any real system, no matter how
the OS scheduler or hardware happens to behave that day. It is the concurrent-programming
analogue of proving a sorting algorithm correct for *all* inputs rather than just the
ones you tested.

### Atomic vs. non-atomic operations
The model needs a base case: some operations must be assumed indivisible, or nothing
could ever be built. The standard baseline is that a single read or a single write of one
memory word is **atomic** — it happens as one indivisible step; no thread can observe a
word half-written. Crucially, **compound operations built from atomic reads and writes
are not themselves atomic** unless something makes them so. `counter++` is read-then-write
— two atomic steps with a gap between them where another thread can interleave. This gap
is called a **race window**, and almost every concurrency bug is a race window nobody
accounted for.

**Worked example: the lost update.** Two threads run `counter++` concurrently, starting
from `counter = 5`.
1. Thread A reads `counter` -> gets 5.
2. Thread B reads `counter` -> gets 5 (A hasn't written yet).
3. Thread A computes 5 + 1 = 6, writes `counter = 6`.
4. Thread B computes 5 + 1 = 6, writes `counter = 6`.

Final value: 6. Correct answer after two increments: 7. One update was silently lost
because both threads read the same stale value before either wrote back. This is the
canonical motivating example for everything in `multiprocessor-programming/02` onward:
mutual exclusion exists precisely to prevent this interleaving from being possible.

### Shared objects and the interface abstraction
Rather than reasoning about raw memory words, the book treats shared data as **shared
objects** exposing a set of methods (e.g. a counter with `increment()`/`get()`, a queue
with `enqueue()`/`dequeue()`). This is the same interface-hides-implementation idea as
any abstract data type, but with a concurrency twist: a shared object's implementation
must define what happens when multiple threads call its methods **at the same time**, not
just what each method does in isolation. Two different implementations of the same
interface (say, a lock-based queue vs. a lock-free queue, `multiprocessor-programming/11`)
can have wildly different concurrent behavior, performance, and progress guarantees while
satisfying the same sequential contract.

### What the model does NOT assume (and why that matters)
- **No assumption of fairness beyond "eventually runs."** A thread that is ready to run
  is guaranteed to run *eventually* (this weak fairness assumption is needed or nothing
  could ever be proven to terminate), but there is no bound on *how long* "eventually"
  takes. An algorithm cannot assume a starved thread will get scheduled soon — only that
  it will not be excluded forever.
- **No assumption about relative thread speed.** As above — a "fast" thread and a "slow"
  thread are both valid schedules the algorithm must handle.
- **No assumption that operations on *different* words are ordered the way you'd expect**
  once you leave the idealized model and hit real hardware and compilers — this is
  exactly the gap that the Java Memory Model (or C++'s memory model) exists to close by
  making specific guarantees explicit. This lesson's model is the "abstract machine";
  real languages/hardware require you to opt into the guarantees (via `volatile`, atomics,
  memory fences) that this abstract model assumes for free.

### Why "shared-memory" as opposed to "message-passing"
The alternative to shared-memory concurrency is **message-passing** (processes with
private memory, communicating only by sending messages — the model behind actor systems
and distributed systems). Shared-memory concurrency is harder to reason about precisely
because any thread can touch any shared location at any time with no visible "message" as
a synchronization point — but it is also the model that every multicore CPU actually
implements at the hardware level (all cores can address the same RAM), so understanding
it deeply pays off even if you mostly write higher-level concurrent code.

## Pros
- Gives a precise, adversary-proof foundation: an algorithm proven correct in this model
  is correct under any real scheduler, not just the ones you happened to test against.
- Matches how real multicore hardware actually works (a single shared address space
  visible to all cores), so the model transfers directly to real systems programming.
- The atomic-read/atomic-write baseline is minimal and uncontroversial — nearly every
  real architecture provides at least this much, so algorithms built on it are broadly
  portable.

## Cons
- Reasoning under full asynchrony (worst-case adversarial interleaving) is genuinely
  hard for humans — our intuition defaults to "things mostly happen in the order I wrote
  them," which is exactly the assumption this model forbids.
- The model is an idealization; real hardware and compilers can reorder operations on
  *different* memory locations in ways this abstract model glosses over (that gap is
  filled by a memory model, e.g. the Java Memory Model, which real code must respect).
- "Assume the worst-case scheduler" leads to conservative, sometimes more complex
  algorithms than would be needed if you could assume, say, bounded thread-speed
  differences — but relaxing that assumption sacrifices the portability guarantee.

## Alternatives
- **Message-passing / actor model** — processes have private memory and communicate only
  via explicit messages; avoids shared-memory races entirely but introduces its own
  complexity (message ordering, delivery guarantees) and is a different subject area
  (distributed systems) rather than an alternative *within* this one.
- **Sequential consistency as a simpler mental model** — assuming all threads observe
  memory operations in one single global order matching program order is easier to reason
  about than full asynchrony with reordering, but real hardware doesn't provide it for
  free (see `multiprocessor-programming/05` for the closely related idea of
  linearizability, which is the *per-object* analogue used to define correctness for
  shared data structures).

## When to use it
Use this model whenever you are implementing or reasoning about a shared data structure
or synchronization primitive that must work correctly regardless of the OS scheduler, core
count, or relative thread speeds — which is to say, any time you write concurrent code
meant to be genuinely robust rather than "seems to work in my testing."

## When NOT to use it
If you are working entirely within a single-threaded event loop (e.g. classic Node.js
callback code, or a UI thread with no worker threads) there is no real concurrency to
model — this whole framework is unnecessary overhead for reasoning about code that never
actually interleaves. Similarly, if your system is message-passing only (no shared
memory across the boundary you're reasoning about, e.g. separate processes communicating
via sockets with no shared segment), this shared-memory model doesn't apply; reach for a
distributed-systems correctness model instead.

## Key takeaways / mental model
Concurrent correctness must hold under *every* possible interleaving/timing a fully
asynchronous, adversarial scheduler could produce — never assume threads run at similar
speeds or in a "reasonable" order. Single reads/writes of a word are the atomic baseline;
anything built from more than one such step (like `counter++`) has a race window unless
you add explicit synchronization. This lesson is the foundation every later lesson in
this subject builds on: mutual exclusion (`multiprocessor-programming/02`), correctness
criteria (`multiprocessor-programming/05`), and progress guarantees
(`multiprocessor-programming/07`) are all different answers to "how do we tame this
asynchronous shared-memory model safely?"

## Self-check questions
1. Why does the model assume a fully asynchronous, worst-case scheduler rather than a
   "reasonable" one where threads run at roughly similar speeds?
2. Walk through the lost-update race on `counter++` step by step, and explain exactly
   which atomic reads/writes interleave to produce the wrong final answer.
3. What is the minimal atomicity assumption this model relies on, and why would nothing
   be provable without at least that much?
4. Why is shared-memory concurrency generally considered harder to reason about than
   message-passing concurrency, even though it more directly matches real multicore
   hardware?

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 1: "Introduction."
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 4: "Foundations of
  Shared Memory."
