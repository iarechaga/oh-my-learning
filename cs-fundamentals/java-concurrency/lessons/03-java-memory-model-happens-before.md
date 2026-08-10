---
id: java-concurrency/03
subject: java-concurrency
title: Java Memory Model and happens-before
slug: java-memory-model-happens-before
status: drafted
mastery:
seniority: senior
source: Java Concurrency in Practice (Goetz et al.), Chapter 16
prerequisites: [java-concurrency/01, java-concurrency/02]
created: 2026-08-10
updated: 2026-08-10
---

# Java Memory Model and happens-before

## TL;DR
The Java Memory Model (JMM) defines exactly when a write made by one thread is
guaranteed to be visible to a read made by another thread - and the answer is "almost
never, unless you establish a **happens-before** relationship" via synchronization,
`volatile`, thread start/join, or a handful of other specific actions. Without one of
those, the compiler, JIT, and CPU are all free to reorder and cache your code's memory
operations in ways that break intuition but are perfectly legal single-threaded
behavior.

## The idea
`java-concurrency/01` showed that races happen because operations aren't atomic.
There's a second, subtler problem the JMM exists to address: even if a write *is*
atomic, another thread has no default guarantee of ever *seeing* it, or of seeing it in
the order you wrote it. Modern CPUs cache values in per-core caches and reorder
instructions for performance; compilers reorder and eliminate operations that are
unobservable *within a single thread*. All of this is legal because a single thread can
never detect its own reordering - but a second thread watching the same memory
absolutely can, if nothing tells the JVM "this ordering matters across threads."

The JMM is the specification that draws this line precisely. It defines
**happens-before**: a partial ordering over actions in a (possibly multi-threaded)
program such that if action A happens-before action B, the effects of A (including all
its memory writes) are guaranteed visible to B. If neither A happens-before B nor B
happens-before A, the JVM is free to let them appear in any order, or for one thread to
never observe the other's write at all - not "usually observes it," but *no guarantee,
ever*, including no guarantee that a value ever propagates out of a register or a core's
local cache into main memory.

## How it works

### Why "obviously the write should be visible" is wrong
```java
class Flag {
    boolean ready = false;   // NOT volatile
    int value = 0;
}
// Thread A                       // Thread B
flag.value = 42;                  while (!flag.ready) { /* spin */ }
flag.ready = true;                System.out.println(flag.value);
```
Intuition says: A sets `value`, then `ready`; B waits for `ready`, then reads `value` -
so B should print 42. Without `volatile` or another happens-before source, **none of
this is guaranteed**:
- The compiler may reorder A's two writes (nothing in a single-threaded view of thread A
  depends on the order between them).
- Thread B may never observe `ready` becoming `true` at all - it might have cached
  `flag.ready`'s value in a register once and never re-read main memory, so the loop
  spins forever (or until an unrelated event forces a re-read).
- Even if B does observe `ready == true`, there is no guarantee it sees the *write to
  `value` that happened before* it in program order on A's side - B could see `ready ==
  true` and `value == 0`.

This isn't a hypothetical edge case; it is routinely observed on real hardware with
aggressive JIT optimization, which is precisely why "it worked when I tested it" is not
evidence of correctness for code like this.

### Happens-before sources
The JMM guarantees a happens-before edge (and therefore visibility) in these specific
situations. This is the actual toolkit you have - and the entire practical content of
"thread safety" mechanisms in this subject can be understood as different ways of
establishing happens-before edges:

1. **Program order rule** - within a single thread, each action happens-before every
   subsequent action in that thread's program order. (This is why single-threaded code
   never needs to worry about any of this.)
2. **Monitor lock rule** - an unlock of a monitor (`synchronized` block/method exit)
   happens-before every subsequent lock of that *same* monitor by any thread
   (`java-concurrency/04`). This is the mechanism behind intrinsic locking's correctness:
   it's not just mutual exclusion, it's also a visibility guarantee.
3. **Volatile variable rule** - a write to a `volatile` field happens-before every
   subsequent read of that *same* field by any thread. Fixing the `Flag` example above is
   as simple as marking `ready` (or both fields, though only `ready` needs it here)
   `volatile` - once B observes `ready == true`, it's guaranteed to see everything A wrote
   *before* setting `ready`, including `value = 42`, because A's write to `value` happens-
   before A's write to `ready` (program order), and A's write to `ready` happens-before
   B's read of `ready` (volatile rule) - happens-before is transitive, so A's write to
   `value` happens-before B's read of `value`.
4. **Thread start rule** - a call to `Thread.start()` happens-before any action in the
   started thread. Anything the parent thread did before calling `start()` is visible to
   the new thread without further synchronization.
5. **Thread termination rule** - every action in a thread happens-before another thread
   successfully returns from a `Thread.join()` on it (or observes, via any means, that
   the thread has terminated).
6. **Interruption rule** - a thread calling `interrupt()` on another thread happens-before
   the interrupted thread detects the interrupt (via `InterruptedException` or polling
   `isInterrupted()`) - relevant to `java-concurrency/10`.
7. **Final field rule** - the values of an object's `final` fields, set in its
   constructor, are visible to any thread that gets a reference to the object *after*
   construction completes, provided the object was safely published (`java-concurrency/02`)
   - this is the specific rule underlying immutable objects' "no synchronization needed
   to read" guarantee.
8. **Transitivity** - if A happens-before B and B happens-before C, then A happens-before
   C. This is what lets a chain of individually-simple rules (program order + volatile
   rule, above) combine into a guarantee about two completely different fields.

### Reordering is real, not theoretical
A concrete mental model: think of each thread as potentially executing against its own
private, possibly-stale snapshot of memory, with writes trickling out to "main memory"
(and other threads' caches) on their own schedule, *unless* a happens-before edge forces
a synchronization point. `volatile` and lock acquire/release are, at the hardware level,
implemented via memory barriers/fences that flush and invalidate the relevant caches -
that's the actual mechanism beneath the JMM's abstract guarantee, though you should
reason at the happens-before level, not the cache-coherence level, because the JMM
promises the *outcome*, not a specific hardware implementation.

### Double-checked locking: a canonical JMM bug and its fix
A once-common (and broken) singleton pattern:
```java
class Broken {
    private static Broken instance;
    static Broken getInstance() {
        if (instance == null) {                 // 1st check, no lock
            synchronized (Broken.class) {
                if (instance == null) {          // 2nd check, under lock
                    instance = new Broken();     // BUG: instance can be published
                }                                 // before its constructor finishes
            }
        }
        return instance;
    }
}
```
`instance = new Broken()` is not atomic at the memory level: it can be decomposed into
(a) allocate memory, (b) run the constructor, (c) assign the reference to `instance`. The
JMM permits the compiler/CPU to make step (c) visible to another thread *before* step
(b) completes, because nothing before Java 5's JMM revision (and nothing here, still, for
a plain field) forbids that reordering. A second thread doing the unsynchronized first
check can see a non-null `instance` pointing at a partially-constructed object and return
it - the exact "unsafe publication" hazard from `java-concurrency/02`, caused here by lack
of a happens-before edge on the plain field. The fix: declare `instance` as `volatile`
(the volatile rule then forces the constructor's writes to happen-before the publishing
write, and that write happens-before any subsequent read) - or, simpler still, avoid
double-checked locking altogether via the class-initialization idiom (a `private static
final Broken instance = new Broken();` inside a lazily-loaded holder class, relying on the
JVM's own thread-safe class initialization).

## Pros
- The happens-before model gives a precise, tool-agnostic way to reason about visibility
  across any synchronization mechanism (locks, `volatile`, atomics, thread lifecycle),
  rather than needing to reason about a specific CPU's cache behavior.
- Once internalized, it explains *why* the higher-level tools in this subject
  (`synchronized`, `volatile`, `java.util.concurrent` classes) are correct, rather than
  requiring them to be memorized as opaque rules.

## Cons
- Genuinely difficult to build intuition for, because the failure mode (stale or
  reordered reads) is invisible on most development machines under light load and
  depends on JIT optimization level and CPU architecture.
- Reasoning about happens-before by hand for a large system doesn't scale; in practice
  you rely on well-tested higher-level abstractions (`java.util.concurrent`) rather than
  hand-deriving happens-before chains for custom code.

## Alternatives
- **Just always use `synchronized` or `java.util.concurrent` classes and never reason
  about happens-before directly** - a reasonable default for most application code; this
  lesson matters most when you need to understand *why* those tools work, debug a subtle
  visibility bug, or evaluate a low-level optimization (e.g. is it safe to remove this
  lock and use `volatile` instead?).
- **Sequential consistency** (the model most languages informally assume before learning
  about memory models) - the naive assumption that all threads see all memory operations
  in one single global order matching program order; the JMM explicitly does *not*
  guarantee this for unsynchronized code, which is the entire reason this lesson exists.

## When to use it
Reach for happens-before reasoning specifically when: reviewing or writing code that uses
`volatile` directly, evaluating whether a lock can safely be removed or narrowed,
debugging an intermittent, load-dependent visibility bug, or implementing a custom
synchronizer (`java-concurrency/11`) where the correctness argument rests on exactly which
actions are ordered.

## When NOT to use it
Don't hand-roll ad hoc synchronization by reasoning informally about "it should be fine,
the write happens first" - use an established happens-before source (a lock, `volatile`,
an atomic, a `java.util.concurrent` utility) rather than inventing a new one. For most
day-to-day application code, you don't need to derive happens-before chains explicitly;
you need to recognize which of `java-concurrency/04`, `java-concurrency/07`,
`java-concurrency/11`, and `java-concurrency/12`'s tools already establishes the ordering
you need.

## Key takeaways / mental model
No happens-before edge means no visibility guarantee, full stop - not "usually visible,"
not "visible after a delay," but genuinely unspecified, including possibly never. Every
synchronization primitive in Java concurrency is, underneath, a way of establishing a
happens-before edge; learning to see `synchronized`, `volatile`, thread start/join, and
atomics through that single lens unifies what would otherwise look like a pile of
unrelated rules.

## Self-check questions
1. In the `Flag` example, explain concretely (in terms of compiler/CPU behavior) two
   different ways the program could misbehave without `volatile`, beyond "it might read
   a stale value."
2. State the monitor lock rule and the volatile variable rule precisely - what exactly is
   guaranteed, and to whom?
3. Walk through, using transitivity, why marking a single field `volatile` in the `Flag`
   example is enough to make an *unrelated*, non-volatile field's write visible too.
4. Explain what specifically is broken in the double-checked locking anti-pattern, and
   why simply adding `volatile` to the singleton field fixes it.

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 16:
  "The Java Memory Model."
