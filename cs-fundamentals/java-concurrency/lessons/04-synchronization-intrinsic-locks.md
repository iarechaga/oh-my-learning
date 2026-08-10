---
id: java-concurrency/04
subject: java-concurrency
title: Synchronization with intrinsic locks
slug: synchronization-intrinsic-locks
status: drafted
mastery:
seniority: mid
source: Java Concurrency in Practice (Goetz et al.), Chapter 2
prerequisites: [java-concurrency/01, java-concurrency/03]
created: 2026-08-10
updated: 2026-08-10
---

# Synchronization with intrinsic locks

## TL;DR
Every Java object has a built-in ("intrinsic") lock, acquired and released with the
`synchronized` keyword, that gives both **mutual exclusion** (only one thread runs the
guarded code at a time) and **visibility** (the happens-before guarantee from
`java-concurrency/03`). Using it correctly means guarding every access to a piece of
shared mutable state with the *same* lock, every time, including reads.

## The idea
`java-concurrency/01` showed why `value++` races. `java-concurrency/03` showed that
even atomic-looking single writes can be invisible to other threads without a
happens-before edge. Intrinsic locking is Java's original, built-in tool that solves
both problems at once for a block of code: while a thread holds an object's lock, no
other thread can enter a block synchronized on the *same* object, and releasing the lock
happens-before any subsequent thread's acquisition of it - so whatever the first thread
wrote inside the block is guaranteed visible to the next thread that acquires the lock.

## How it works

### The `synchronized` keyword, two forms
```java
public class Counter {
    private int value = 0;
    public synchronized void increment() { value++; }   // synchronized method:
                                                            // locks on `this`
    public synchronized int get() { return value; }       // reads need the lock too!
}
```
```java
public class Counter {
    private final Object lock = new Object();
    private int value = 0;
    public void increment() {
        synchronized (lock) { value++; }                  // synchronized block:
    }                                                        // locks on an explicit object
    public int get() {
        synchronized (lock) { return value; }
    }
}
```
A `synchronized` instance method is exactly equivalent to wrapping the whole method body
in `synchronized (this) { ... }`. A `synchronized static` method locks on the `Class`
object instead (`synchronized (Counter.class)`). Using a private, dedicated lock object
(second example) rather than `this` is generally preferable in library code: locking on
`this` exposes the lock to external code, which could accidentally (or maliciously)
synchronize on your object too, creating unexpected contention or deadlock risk you don't
control.

**Every access, not just writes.** `get()` must also be synchronized, even though it only
reads `value`. Without the happens-before edge from acquiring the same lock, a reader
thread has no visibility guarantee at all (`java-concurrency/03`) and could see a stale
cached value indefinitely, independent of the writer's own atomicity.

### Reentrancy
Intrinsic locks are **reentrant**: a thread that already holds a lock can acquire it
again (e.g. calling a synchronized method from within another synchronized method on the
same object, or a subclass's synchronized method calling `super`'s synchronized method)
without blocking on itself. The JVM tracks an acquisition count per thread-lock pair;
each `synchronized` block increments it on entry and decrements it on exit, releasing the
lock only when the count returns to zero. Without reentrancy, common patterns like a
synchronized method calling another synchronized method on the same object would
self-deadlock.

### What the lock actually guards - and the discipline this implies
A lock doesn't protect *code*, it protects *data*. "Synchronize this method" is shorthand
for "every thread must hold lock L before touching field F," and that discipline has to
be applied consistently to *every* piece of code that touches F, not just the pieces you
remember to wrap. A single un-synchronized access anywhere in the codebase (a getter that
forgot `synchronized`, a field read directly by another class) breaks the guarantee for
the *entire* class, not just that access point - because the whole safety argument rested
on "all access goes through the lock," and that's now false.

### Compound actions need one lock acquisition for the whole sequence
```java
// BUG: check-then-act is not atomic even if each step is individually synchronized
if (!map.containsKey(key)) {      // acquires lock, checks, releases lock
    map.put(key, computeValue()); // acquires lock again - another thread could have
}                                   // inserted the key in between
```
```java
// FIX: hold the lock across the entire compound operation
synchronized (lock) {
    if (!map.containsKey(key)) {
        map.put(key, computeValue());
    }
}
```
This is the check-then-act hazard from `java-concurrency/01`, and the fix illustrates the
core rule: the *scope* of the synchronized block must cover the entire invariant-
dependent sequence, not just each individual step. (In practice, prefer
`map.computeIfAbsent(key, k -> computeValue())` on a `ConcurrentHashMap` -
`java-concurrency/07` - which does this atomically without you managing a lock by hand;
this example exists to make the underlying hazard concrete.)

### Worked example: a thread-safe bank account
```java
public class Account {
    private final Object lock = new Object();
    private long balanceCents;

    public Account(long initialCents) { this.balanceCents = initialCents; }

    public void transferTo(Account other, long amountCents) {
        // BUG risk: locking two different objects separately, one at a time,
        // does not make the transfer atomic as a whole - another thread could
        // observe an intermediate state where money has left this account but
        // not yet arrived, or (worse) this ordering can deadlock, see java-concurrency/06.
        synchronized (this.lock) { this.balanceCents -= amountCents; }
        synchronized (other.lock) { other.balanceCents += amountCents; }
    }
}
```
This compiles and "looks" synchronized, but it's still broken: a thread reading either
account's balance between the two `synchronized` blocks can observe money that has
vanished from one account and not yet appeared in the other. Fixing this properly needs
either a single object-level lock ordering discipline (`java-concurrency/06`) or a
higher-level design (e.g. routing all transfers through one serializing component) -
the point of this example is that "I used `synchronized`" is not, by itself, evidence of
correctness; you have to reason about what invariant needs to hold atomically and whether
your lock scope actually covers it.

### Cost of intrinsic locks
Uncontended `synchronized` in modern JVMs is cheap (biased/thin locking optimizations
make the common single-thread-repeatedly-locking case very fast). Under real contention -
many threads actually blocking on the same lock - every waiting thread pays context-
switch and scheduling cost, and throughput drops as contention rises; `java-concurrency/13`
covers this in depth.

## Pros
- Built into the language, always available, no import needed.
- Gives mutual exclusion and visibility together in one mechanism - you don't need to
  separately reason about a happens-before edge, `synchronized` provides one as a
  side effect of correct lock discipline.
- Reentrant, so composing synchronized methods (including via inheritance) doesn't
  self-deadlock.

## Cons
- No way to attempt a lock without blocking, no timeout, no interruptible wait, and no
  way to check "is this locked" - `java-concurrency/11`'s `ReentrantLock` and friends
  exist specifically to fill these gaps.
- No fairness guarantee (a thread that's been waiting a long time is not guaranteed to
  get the lock before a thread that just arrived) - relevant to starvation,
  `java-concurrency/06`.
- Easy to under-scope (leaving a gap where an unsynchronized access slips through) or
  over-scope (holding the lock across expensive work, e.g. I/O, needlessly serializing
  unrelated work and hurting scalability - `java-concurrency/13`).
- Locking on a publicly reachable object (`this`, a shared `Class` object) exposes your
  lock to code you don't control, which can accidentally increase contention or
  contribute to deadlock.

## Alternatives
- **`ReentrantLock` and explicit locks** (`java-concurrency/11`) - when you need
  `tryLock`, timeouts, interruptible acquisition, multiple wait conditions, or
  non-block-structured locking.
- **Atomic variables** (`java-concurrency/12`) - for a single field, compare-and-swap
  based atomics often avoid locking entirely, with better scalability under contention.
- **Immutability or confinement** (`java-concurrency/02`) - the cheapest fix is to not
  need a lock at all.
- **Concurrent collections** (`java-concurrency/07`) - purpose-built thread-safe
  collections handle their own internal locking (often more granular and efficient than
  a single external lock around a plain collection) and expose atomic compound
  operations like `computeIfAbsent`.

## When to use it
Use `synchronized` as the default tool for protecting a small, well-defined piece of
mutable state shared across threads, especially when you don't need the advanced features
of explicit locks - it's simpler to write correctly and to review than manual
lock/unlock pairs.

## When NOT to use it
Don't use `synchronized` around long-running or blocking operations (network calls, disk
I/O, waiting on another lock) - you'll serialize unrelated work and create contention
far beyond what's necessary; narrow the guarded section to just the state mutation. Don't
use it when you need `tryLock`/timeouts/interruptibility - use `java-concurrency/11`
instead. Don't use it as a substitute for actually identifying which invariant needs
protecting - see the bank account example above.

## Key takeaways / mental model
A lock protects an invariant across *every* access to the data it guards, not just the
one call site you're currently editing - one missed synchronized access anywhere breaks
the guarantee everywhere. Scope the lock to cover the entire compound operation that must
appear atomic, no more (cost) and no less (correctness).

## Self-check questions
1. Why must a getter method that only reads shared state still be synchronized, given
   that a single field read is already atomic at the bytecode level?
2. Explain reentrancy: why is it necessary for a synchronized method to be able to call
   another synchronized method on the same object without deadlocking?
3. In the `Account.transferTo` example, why does synchronizing each individual
   balance update separately fail to make the transfer atomic as a whole? What would you
   need to change to fix it (in general terms - full fix is in `java-concurrency/06`)?
4. Why is locking on a private, dedicated lock object generally preferable to locking on
   `this` in library code?

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 2:
  "Thread Safety."
