---
id: java-concurrency/02
subject: java-concurrency
title: Immutability, confinement, and thread safety basics
slug: immutability-confinement-thread-safety
status: drafted
mastery:
seniority: mid
source: Java Concurrency in Practice (Goetz et al.), Chapter 3
prerequisites: [java-concurrency/01]
created: 2026-08-10
updated: 2026-08-10
---

# Immutability, confinement, and thread safety basics

## TL;DR
The cheapest way to make code thread-safe is to never let it need synchronization in the
first place: make objects immutable (nothing to race over) or confine mutable objects to
a single thread (no one else can touch them). Only when state must be both mutable *and*
shared do you need locks (`java-concurrency/04`) - and even then, correct **publication**
of an object to other threads is a prerequisite that's easy to get wrong.

## The idea
`java-concurrency/01` established that shared mutable state is where races live. The
direct corollary: if state is not mutable, or not shared, there is no race to have. This
lesson covers the two design-level escapes from the problem before you ever reach for a
lock - **immutability** (remove the "mutable") and **thread confinement** (remove the
"shared") - plus the visibility hazard that undermines both if you're not careful about
how an object crosses from the thread that created it to the thread that uses it:
**publication**.

## How it works

### Immutability: no mutation, no race
An object is immutable if its state cannot change after construction. If no thread can
ever write to it, no interleaving of reads can ever observe a torn or inconsistent view -
immutable objects are unconditionally thread-safe, freely shareable, and require zero
synchronization to read.

An object is properly immutable in Java when:
1. All fields are `final` and set only in the constructor.
2. The object doesn't publish `this` from its constructor (no callback, no listener
   registration, no starting a thread from inside the constructor) - doing so lets another
   thread see a partially-constructed object before the constructor finishes.
3. Any mutable object referenced by a field is either itself immutable, or is never
   exposed outside the class and never mutated after construction (e.g. a private
   `List` filled once in the constructor and only exposed via an unmodifiable copy).

```java
public final class Point {
    private final int x, y;
    public Point(int x, int y) { this.x = x; this.y = y; }
    public int getX() { return x; }
    public int getY() { return y; }
    // No setters. Every "change" to a Point creates a new Point.
    public Point translated(int dx, int dy) { return new Point(x + dx, y + dy); }
}
```
Note the pattern in `translated`: instead of mutating `this`, it returns a new instance.
This is the standard immutable-object idiom (also seen in `String`, `BigDecimal`, and
Java's record types) - "changing" state means producing a new value, never editing the
old one in place.

**Why `final` fields matter beyond documentation.** The Java Memory Model
(`java-concurrency/03`) gives `final` fields a special guarantee: once a constructor
finishes and the reference to the object is safely published (see below), every thread
that sees the reference is guaranteed to see the correctly initialized values of its
`final` fields - no synchronization required to read them. Non-`final` fields get no such
guarantee, which is exactly why immutability in Java specifically means `final` fields,
not just "a class with no setters" (a class could have no setters but still mutate a
non-`final` field internally, or simply omit `final` and lose the visibility guarantee).

### Thread confinement: no sharing, no race
If mutable state is only ever touched by one thread, it needs no synchronization either -
there is no second thread to race against. Three flavors:

- **Ad hoc confinement** - a convention, enforced by discipline and code review, that a
  given object is only touched by one thread (e.g. a `SimpleDateFormat` instance kept as
  a local variable, never shared). Fragile - nothing in the type system stops a future
  change from leaking it to a second thread.
- **Stack confinement** - the object exists only as a local variable and never escapes
  the method (never stored in a field, never passed to something that might retain a
  reference and hand it to another thread). Since local variables live on the calling
  thread's private stack, this is automatically safe.
- **`ThreadLocal`** - Java's built-in tool for confinement when each thread genuinely
  needs its own independent copy of a value across multiple method calls (e.g. a
  per-thread `SimpleDateFormat`, a per-request transaction context in a thread-per-request
  server). `ThreadLocal<T>` stores a separate value per thread internally; `get()`/`set()`
  always operate on the calling thread's own slot.

```java
private static final ThreadLocal<SimpleDateFormat> DATE_FORMAT =
    ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd"));

String format(Date d) { return DATE_FORMAT.get().format(d); } // safe: each thread's own instance
```
`SimpleDateFormat` is famously not thread-safe internally (it mutates internal `Calendar`
state during formatting); sharing one instance across threads is a real, commonly-hit bug.
`ThreadLocal` sidesteps the whole problem by never sharing the instance in the first
place - each thread gets its own, lazily created by the initializer on first `get()`.

**Confinement caveat in pooled-thread environments.** In a thread pool
(`java-concurrency/08`), threads are reused across many tasks. A `ThreadLocal` value set
by one task and not cleared will leak into the *next* task that happens to run on that
same pooled thread - a subtle correctness and memory-leak hazard. Frameworks that use
`ThreadLocal` for per-request context (e.g. security context, MDC logging context) must
explicitly clear it when the task finishes.

### Publication and escape
**Publication** is making an object reachable from outside the scope that created it -
returning it, storing it in a public field, passing it to another method that might
retain it, or registering it as a listener/callback. An object has **escaped** when it's
been published somewhere it shouldn't have been - most dangerously, before its
constructor has finished.

**Unsafe publication example:**
```java
public class Holder {
    public static Holder instance;      // published via a static field
    private int value;
    public Holder(int value) {
        this.value = value;
        instance = this;                 // "this" escapes before the constructor returns
    }
}
```
Another thread reading `Holder.instance` concurrently with construction can observe a
`Holder` object whose `value` field has not yet been assigned - a partially-constructed
object, sometimes literally impossible for `value` to have a legal value in, because there
was no synchronization ordering the write to `value` before the write to `instance`. This
exact failure mode is why "publish `this` from the constructor" (starting a thread,
registering a listener, assigning to a static field) is a standing rule to avoid, not a
style nitpick.

**Safe publication idioms** (guaranteed by the JVM specification to make an object's
state visible correctly to any thread that obtains the reference):
1. Initializing an object reference from a `static` initializer (run once by the JVM
   under an implicit lock, before any thread can observe it).
2. Storing the reference into a `volatile` field or an `AtomicReference`.
3. Storing the reference into a `final` field of a properly constructed object (the
   `final`-field guarantee mentioned above).
4. Storing the reference into a field that's properly guarded by a lock, consistently
   used by both the publishing and consuming thread (`java-concurrency/04`).
5. Putting it into an already-thread-safe collection (e.g. `ConcurrentHashMap`,
   `BlockingQueue` - `java-concurrency/07`), whose internal synchronization does the
   ordering for you.

### Worked example: fixing the Holder class
```java
public class Holder {
    private static volatile Holder instance;
    private final int value;
    private Holder(int value) { this.value = value; }
    public static Holder create(int value) {
        Holder h = new Holder(value);   // constructor fully completes first
        instance = h;                    // then published via volatile - safe publication
        return h;
    }
    public static Holder getInstance() { return instance; }
}
```
Now `value` is `final` (gets the constructor-completion guarantee) and `instance` is
`volatile` (any thread reading it after it's non-null is guaranteed to see the fully
constructed object, because a `volatile` write happens-before a subsequent `volatile`
read of the same field - see `java-concurrency/03`).

## Pros
- Zero synchronization overhead and zero risk of races for anything immutable or
  properly confined - the strongest and cheapest correctness guarantee available.
- Immutable objects are trivially shareable, cacheable, and safe to use as hash keys or
  in concurrent collections without defensive copying.
- Design-level discipline (immutability, confinement) scales better than lock discipline:
  there's no lock-ordering to get wrong, no forgotten unlock, no possibility of deadlock.

## Cons
- Not every problem fits an immutable or confined model - genuinely shared, genuinely
  mutable state (a live connection pool, a running counter) still needs real
  synchronization.
- Immutability can mean more object allocation (each "change" is a new object), a real
  cost under high-churn workloads, though usually far smaller than lock contention costs.
- `ThreadLocal` in a pooled-thread environment requires explicit cleanup discipline or it
  leaks state (and memory) across unrelated tasks.
- Unsafe publication bugs are invisible in single-threaded testing and depend on exact
  JIT/CPU reordering behavior, making them some of the hardest concurrency bugs to
  reproduce and diagnose.

## Alternatives
- **Explicit locking** (`java-concurrency/04`) - when state must be both mutable and
  shared and neither immutability nor confinement applies, use intrinsic locks or
  explicit locks (`java-concurrency/11`) to serialize access.
- **Atomic variables** (`java-concurrency/12`) - for a single shared mutable field (a
  counter, a reference), often replaces a full lock with a lighter-weight
  compare-and-swap based approach.
- **Concurrent collections** (`java-concurrency/07`) - when the shared mutable state is a
  collection, a purpose-built thread-safe collection is usually simpler and faster than
  hand-rolled locking around a plain `HashMap` or `ArrayList`.

## When to use it
Default to immutability for any value object (DTOs, coordinates, configuration snapshots,
money amounts). Default to confinement (a local variable, or `ThreadLocal` when a
per-thread value must persist across calls) for any mutable helper object that doesn't
need to be shared. Reach for real synchronization only for the state that's left over
after applying both.

## When NOT to use it
Don't force immutability onto state that's inherently mutable and shared by design (a
live cache, an in-flight counter of active connections) - you'll end up building an
awkward copy-and-replace scheme that's really just a worse version of proper
synchronization. Don't rely on ad hoc confinement ("we just never share this, I promise")
for anything long-lived or touched by more than one contributor - it has no compiler or
runtime enforcement and silently breaks the moment someone hands the object to a new
thread.

## Key takeaways / mental model
Before reaching for a lock, ask: can this be immutable? Can it be confined to one thread?
Only genuinely shared, genuinely mutable state needs synchronization. And whenever an
object crosses a thread boundary, ask specifically how it was published - an unsafely
published object can appear partially constructed to the receiving thread even if its
constructor "already finished" from the publisher's point of view.

## Self-check questions
1. Why does Java's `final` field guarantee specifically require the object to be
   "properly constructed" (not publishing `this` early) to hold?
2. Give an example of ad hoc confinement, stack confinement, and `ThreadLocal`
   confinement, and explain what could break each one if a future change violated its
   assumption.
3. Walk through why the unsafe `Holder` example can let another thread observe
   `value == 0` (or garbage) even though the constructor "already ran" from the
   publishing thread's perspective.
4. Name three safe publication idioms from this lesson and explain, for one of them,
   what specific JVM guarantee makes it safe.

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 3:
  "Sharing Objects."
