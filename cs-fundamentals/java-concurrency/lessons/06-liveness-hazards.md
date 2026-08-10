---
id: java-concurrency/06
subject: java-concurrency
title: "Liveness hazards: deadlock, starvation, livelock"
slug: liveness-hazards
status: drafted
mastery:
seniority: senior
source: Java Concurrency in Practice (Goetz et al.), Chapter 10
prerequisites: [java-concurrency/04, java-concurrency/05]
created: 2026-08-10
updated: 2026-08-10
---

# Liveness hazards: deadlock, starvation, livelock

## TL;DR
Correct locking (`java-concurrency/04`, `java-concurrency/05`) prevents *safety*
violations - wrong answers. It does nothing by itself to prevent *liveness* violations -
threads that never make progress at all. Deadlock (circular waiting), starvation
(perpetual denial of a needed resource), and livelock (threads actively running but never
progressing) are the three named ways correctly-synchronized code can still hang forever.

## The idea
A program can be perfectly safe (every invariant holds, no race ever corrupts data) and
still be useless, because two threads are stuck waiting on each other forever. Liveness
hazards are a different axis from correctness entirely: they're about *progress*, not
*consistency*. `java-concurrency/05` showed that composing thread-safe classes can
require holding multiple locks together to protect a multivariable invariant (the bank
transfer example) - and the moment you need more than one lock at once, you've opened
the door to deadlock.

## How it works

### Deadlock: circular lock-ordering
The classic case: two threads, two locks, acquired in opposite order.
```java
// Thread A                              // Thread B
synchronized (lockX) {                    synchronized (lockY) {
    synchronized (lockY) { ... }              synchronized (lockX) { ... }
}                                          }
```
1. Thread A acquires `lockX`.
2. Thread B acquires `lockY`.
3. Thread A tries to acquire `lockY` - blocks (B holds it).
4. Thread B tries to acquire `lockX` - blocks (A holds it).

Neither thread can proceed, neither will ever release what it holds, and neither will
ever get what it's waiting for. This is a genuine, permanent deadlock - the JVM has no
built-in deadlock detection or recovery for `synchronized` locks; the threads simply
hang forever (thread dump tools like `jstack` can *detect* an existing deadlock after the
fact, but nothing automatically breaks it).

**This is exactly the shape of the unfinished `Account.transferTo` example from
`java-concurrency/04` and `java-concurrency/05`**: if `transferTo` locked both accounts
(fixing the earlier atomicity bug) by always locking `this` first, then `other`, a
concurrent `other.transferTo(this, ...)` call would lock in the opposite order - the
textbook two-thread deadlock, arising from a *correct-looking* attempt to fix a different
bug.

### Lock-ordering deadlock: the general shape and the fix
Deadlock from multiple locks always comes down to: two or more threads acquiring the same
set of locks in different orders. The fix is a **consistent global lock ordering**: pick
one, universal order (e.g. always lock the account with the smaller `hashCode()`, or an
externally assigned unique ID, first) and enforce it everywhere, regardless of which
object initiated the operation.
```java
public void transferTo(Account other, long amountCents) {
    Account first  = this.id < other.id ? this : other;
    Account second = this.id < other.id ? other : this;
    synchronized (first.lock) {
        synchronized (second.lock) {
            this.balanceCents -= amountCents;
            other.balanceCents += amountCents;
        }
    }
}
```
Now every thread, regardless of which account it calls `transferTo` on, locks the
lower-ID account first - the circular wait condition (step 3/4 above) becomes structurally
impossible, because there's no pair of threads that could be waiting on each other's next
lock.

### Dynamic lock ordering and the "invoking alien method with a lock held" trap
When the lock order can't be fixed statically (e.g. no natural total order exists), a
common alternative is a global "tie-breaking" lock acquired before either object's lock,
serializing all such multi-lock operations - simple but removes concurrency between them.
A related, easy-to-miss hazard: calling into code you don't control (a listener, a
callback, an overridable method) *while holding a lock* is dangerous even with a single
lock, because you don't know what that alien code does - if it happens to call back into
your class and try to acquire the same lock your thread already holds pending some other
condition, or acquire a second lock in an order that conflicts elsewhere in the system,
you've created a deadlock risk invisible from reading your class alone. The general
guidance: avoid calling unknown/overridable code while holding a lock; if unavoidable,
keep the call outside the synchronized block (**open calls**).

### Resource ordering deadlock
Deadlock isn't limited to intrinsic locks - it can happen with any finite, blocking
resource acquired in inconsistent order: two threads each holding one connection from a
pool of two and each waiting for a second connection the other holds; two threads each
holding a permit from different `Semaphore`s and waiting on the other's. The general
principle (consistent acquisition order, or acquire-all-or-none) applies identically.

### Starvation
Starvation is a thread being perpetually denied access to a resource it needs to make
progress, even though the resource does eventually become available to *other* threads -
unlike deadlock, the system as a whole is making progress, just never for this one
thread. Causes include: a low-priority thread starved out by a scheduler that consistently
favors higher-priority threads (a reason Java's thread-priority APIs are rarely used in
practice - they're platform-dependent and easy to misuse this way); a thread perpetually
losing the race for a non-fair lock under heavy contention from many other threads; or a
`synchronized` block that holds a lock for far longer than necessary (e.g. wrapping an I/O
call), starving out everyone else waiting on the same lock, sometimes called "starvation
due to poor responsiveness."

### Livelock
Livelock is threads that are actively running - not blocked, using CPU - but making no
real progress, typically because each is reacting to the other's attempted-and-aborted
action in a way that causes both to retry forever in lockstep.
```
Two people in a hallway, both step left to let the other pass, then both step
right at the same time, then both step left again... forever. Both are moving.
Neither is getting anywhere.
```
Concretely: two threads each hold a resource, detect potential deadlock, and both
"politely" release and retry - if both retry using the exact same policy (same delay,
same condition), they can fall into a repeating retry-collide-retry cycle indefinitely.
The fix usually involves adding **randomized backoff** before retrying, so simultaneous
retries desynchronize over a few iterations instead of staying locked in step.

### Diagnosing liveness hazards in practice
Deadlock in production typically presents as a thread (or request path) that simply never
completes, with no exception and no error logged (waiting threads don't throw). The
standard tool is a **thread dump** (`jstack <pid>`, or a JVM's built-in deadlock
detector reachable via `jconsole`/`jvisualvm`/most APM tools) - the JVM can detect a
cycle of `BLOCKED` threads each waiting on a lock the next one in the cycle holds, and
will report it explicitly as "Found one Java-level deadlock" in the dump. This detection
is diagnostic only - it does not resolve the deadlock; the process typically must be
restarted (or, if the deadlocked threads are interruptible-lock-based rather than
intrinic-lock-based, potentially interrupted - `java-concurrency/10`, `java-concurrency/11`).

## Pros
(Liveness hazards are bugs, not techniques - "pros" here means: understanding them lets
you design around them cheaply, before they cost you an incident.)
- A consistent lock-ordering discipline is nearly free to establish early in a codebase's
  life and very expensive to retrofit after many call sites have grown inconsistent
  orderings.
- Recognizing the deadlock/starvation/livelock distinction sharpens production
  diagnosis: a hung thread dump with a `BLOCKED` cycle is deadlock; a thread perpetually
  losing a lock race under heavy load is starvation; high CPU with no throughput is a
  livelock signature.

## Cons
- Lock-ordering discipline requires global knowledge of every code path that acquires
  more than one lock - easy to violate accidentally as a codebase grows, especially
  across module boundaries where the full lock graph isn't visible to any one author.
- Deadlocks caused by calling alien/overridable code while holding a lock can be
  essentially invisible in code review, since the deadlock only manifests via a
  specific external implementation you don't control.
- No amount of testing reliably proves the absence of deadlock - like races, it's a
  property of interleaving, and the "bad" interleaving may simply never occur under test
  load.

## Alternatives
- **`tryLock` with a timeout** (`java-concurrency/11`) - instead of unconditional
  blocking acquisition (which can deadlock forever), use a timed attempt and back off
  and retry (with randomization to avoid livelock) if the second lock isn't obtained in
  time - converts an unrecoverable deadlock into a recoverable, retryable failure.
- **Avoid needing multiple locks at all** - redesign around a single coarser lock (
  `java-concurrency/05`'s monitor pattern) or an immutable-snapshot swap
  (`java-concurrency/12`), removing the multi-lock ordering problem entirely at the cost
  of coarser-grained concurrency.
- **Lock-free / nonblocking algorithms** (`java-concurrency/12`) - if no thread ever
  blocks waiting for a lock, classic deadlock (circular *lock* waiting) cannot occur by
  construction, though other liveness concerns (e.g. livelock from repeated CAS failures
  under heavy contention) can still arise.

## When to use it
Apply consistent lock ordering (or, better, avoid multi-lock designs) any time a single
logical operation needs to hold more than one lock simultaneously - transfers between two
accounts, moving an item between two containers, anything spanning two independently-
lockable objects of the same type.

## When NOT to use it
Don't invent a bespoke ad hoc ordering rule per call site ("lock A before B here, but B
before A over there because it was more convenient") - inconsistency is exactly what
causes deadlock; the ordering rule must be global and total across every code path that
can acquire the relevant locks together.

## Key takeaways / mental model
Deadlock = circular waiting on locks, permanent, requires a consistent global lock
order to prevent. Starvation = one thread perpetually denied a resource others do get -
the system moves, this thread doesn't. Livelock = everyone's moving, no one's getting
anywhere - fix with randomized backoff. All three are progress bugs, orthogonal to
whether the data ends up correct.

## Self-check questions
1. Walk through the classic two-lock, two-thread deadlock step by step and explain
   exactly which condition the consistent-lock-ordering fix removes.
2. Why is "call into code you don't control while holding a lock" dangerous even in a
   single-lock design?
3. Distinguish starvation from deadlock and from livelock using the "is the system making
   any progress at all" question.
4. Why does randomized (rather than fixed) backoff help resolve livelock, and what would
   happen if both retrying threads used the exact same fixed delay?

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 10:
  "Avoiding Liveness Hazards."
