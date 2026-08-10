---
id: java-concurrency/05
subject: java-concurrency
title: Building and composing thread-safe classes
slug: composing-thread-safe-classes
status: drafted
mastery:
seniority: senior
source: Java Concurrency in Practice (Goetz et al.), Chapter 4
prerequisites: [java-concurrency/02, java-concurrency/04]
created: 2026-08-10
updated: 2026-08-10
---

# Building and composing thread-safe classes

## TL;DR
A thread-safe class isn't just "has some `synchronized` methods" - it's a class whose
documented **invariants** hold under any interleaving of concurrent calls. Designing one
means identifying the state, the invariants that must hold across that state, and the
synchronization policy that enforces them; composing thread-safe classes out of other
thread-safe classes is easy for independent state and genuinely hard the moment an
invariant spans more than one of them.

## The idea
`java-concurrency/04` showed the mechanics of `synchronized`. This lesson is about the
design question one level up: given a class with some fields, how do you decide *what*
needs a lock, *which* lock, and *how wide* the locked regions need to be - and, crucially,
what happens when you build a class out of other classes that are already thread-safe on
their own. The uncomfortable truth Goetz calls out repeatedly: thread safety does not
compose automatically. A class made of thread-safe parts is not thread-safe unless the
*combination's* invariants are also protected.

## How it works

### Step 1: identify the state
List every field. For each, ask: is it mutable? Could more than one thread reach it? If
either answer is "no" (immutable, or confined - `java-concurrency/02`), it needs no
synchronization. What remains is the state that actually needs a policy.

### Step 2: identify the invariants
An invariant is a condition that must hold whenever the object is observed from outside a
synchronized block - not necessarily every instant, but at every point another thread
could legally look. Examples: "`size == count of non-null slots`" for a bounded buffer;
"`min <= max`" for a running range tracker; "the set of `Order`s referenced by `Customer`
matches the reverse index in `OrderBook`" for a two-object relationship. **Multivariable
invariants** - ones spanning more than one field - are exactly where naive per-field
locking breaks: locking `min` and `max` separately doesn't stop a reader from observing
`min` updated but `max` not yet, violating `min <= max` mid-update.

### Step 3: pick a synchronization policy and document it
The policy states which lock guards which state. Java Concurrency in Practice's
recommendation, and the one to default to: **guard every variable that participates in
an invariant with the same lock**, and hold that lock for the *entire* duration of any
compound action that depends on the invariant. Document this - a comment stating "guarded
by `lock`" next to the field - because nothing in the language enforces it; the discipline
is entirely a human contract enforced by code review and testing, and it is the single
most common thing that silently rots as a codebase evolves.

```java
@GuardedBy("this")
private int min = Integer.MAX_VALUE;
@GuardedBy("this")
private int max = Integer.MIN_VALUE;

public synchronized void observe(int value) {
    if (value < min) min = value;
    if (value > max) max = value;
}
public synchronized int getMin() { return min; }
public synchronized int getMax() { return max; }
// A caller wanting "getMin() and getMax() together, consistently" still needs to
// synchronize externally on the same lock across both calls - see "Client-side locking" below.
```

### Monitor pattern: encapsulate state, expose no direct handles
The simplest reliable design: keep all mutable state `private`, never return a direct
reference to it, and guard every access with the object's own intrinsic lock. This is
called the **monitor pattern**. Because no external code ever gets a raw reference to the
guarded state, no one outside the class can bypass the lock - the class fully controls
its own synchronization, and callers don't need to know or care which lock is used.

```java
public class BoundedCounter {
    private final Object lock = new Object();
    @GuardedBy("lock") private int count = 0;
    private final int max;
    public BoundedCounter(int max) { this.max = max; }
    public synchronized boolean tryIncrement() {   // effectively synchronized on `this`
        if (count >= max) return false;
        count++;
        return true;
    }
}
```

### Delegating thread safety - when it's actually safe
If a class's state consists entirely of *independent*, already-thread-safe fields (no
invariant spans more than one of them), you can delegate: let each field's own
synchronization handle itself, with no additional lock in your class.

```java
public class CountingFactory {
    private final AtomicLong created = new AtomicLong();          // independent
    private final ConcurrentHashMap<String, Widget> cache =        // independent
        new ConcurrentHashMap<>();
    public Widget getOrCreate(String key) {
        return cache.computeIfAbsent(key, k -> {
            created.incrementAndGet();
            return new Widget(k);
        });
    }
}
```
This is safe *only* because `created` and `cache` have no relationship that must be kept
consistent (nobody requires `created == cache.size()`, for instance). The moment such a
relationship exists, delegation stops being sufficient - see the next section.

### When delegation fails: multivariable invariants across composed objects
```java
public class NumberRange {
    // BUG: each field is individually thread-safe, but the combined invariant
    // (lower <= upper) is not - delegating to two AtomicIntegers does not
    // make the compound check-then-set atomic.
    private final AtomicInteger lower = new AtomicInteger(0);
    private final AtomicInteger upper = new AtomicInteger(0);

    public void setLower(int i) {
        if (i > upper.get()) throw new IllegalArgumentException();
        lower.set(i);     // another thread can shrink `upper` below `i` right here
    }
}
```
Two threads calling `setLower(5)` and `setUpper(3)` concurrently, each individually
passing its own check against the other field's *current* value, can both succeed and
leave `lower == 5, upper == 3` - the invariant is violated even though every individual
atomic operation was internally correct. The fix is to abandon delegation for this
invariant and guard both fields with one shared lock covering the entire check-then-set
sequence, exactly as in `java-concurrency/04`'s check-then-act discussion.

### Client-side locking and its fragility
Sometimes you need to compose an atomic operation out of two calls on an *already
thread-safe* class you don't control (e.g. "add to this `Vector` only if it isn't already
there" using a legacy synchronized collection). **Client-side locking** means the caller
acquires the *same* lock the target object uses internally, then makes both calls inside
it.
```java
List<Integer> list = Collections.synchronizedList(new ArrayList<>());
synchronized (list) {                 // must lock on the SAME object the list uses
    if (!list.contains(x)) list.add(x);
}
```
This only works if you know precisely which lock the target class uses internally (here,
`Collections.synchronizedList` documents that it's the list itself) - an implementation
detail you're now depending on. If that implementation ever changes its internal locking
strategy (as, notably, most `java.util.concurrent` classes like `ConcurrentHashMap`
explicitly do *not* document a single exposed lock, specifically to prevent client-side
locking and allow internal lock striping for scalability - `java-concurrency/07`), your
client-side lock silently stops working with no compiler error. **Class extension** (
subclassing and adding synchronized methods that call the same lock) is the more robust
alternative when the base class explicitly documents and exposes its lock for this
purpose - but few modern concurrent collections do, by design.

## Pros
- A documented synchronization policy (`@GuardedBy`, invariant comments) turns "is this
  thread-safe?" from an exercise in reading every call site into a checkable local
  property of the class.
- The monitor pattern is simple to reason about and audit: one lock, no leaked
  references, done.
- Delegation to already-thread-safe, independent fields avoids writing any new locking
  code at all when it genuinely applies.

## Cons
- Thread safety does not compose for free - assembling thread-safe parts can still yield
  a class with broken multivariable invariants, and this failure mode is easy to miss in
  review because every individual field "looks" safe.
- Client-side locking is fragile: it depends on undocumented or implementation-specific
  locking behavior in the composed class, and silently breaks if that implementation
  changes.
- A single coarse lock (the monitor pattern's simplicity) can become a scalability
  bottleneck under contention - `java-concurrency/13` covers splitting it into finer-
  grained locks when profiling shows this matters.

## Alternatives
- **Finer-grained locking / lock splitting** - once a coarse monitor lock is proven to be
  a contention bottleneck, split independent pieces of state onto separate locks (only
  safe when their invariants are truly independent - re-derive step 2 above for the
  split).
- **Immutable snapshots** - instead of composing mutable thread-safe pieces, build a new
  immutable object representing the composed state at a point in time, and swap it
  atomically via a single `volatile` or `AtomicReference` (`java-concurrency/12`) - side-
  steps multivariable invariant hazards entirely because the whole snapshot is
  constructed before ever being shared.
- **Purpose-built concurrent collections** (`java-concurrency/07`) - when the composition
  problem is "safely combine a few operations on a collection," a concurrent collection's
  atomic compound methods (`computeIfAbsent`, `putIfAbsent`) often remove the need for
  any external composition at all.

## When to use it
Apply this discipline (identify state, identify invariants, pick and document a policy)
whenever you're writing any class - not just a "concurrency utility" - that will be
shared across threads and holds more than one piece of mutable state that must stay
consistent together.

## When NOT to use it
Don't reach for client-side locking against a class whose internal lock isn't explicitly
documented and guaranteed stable - prefer redesigning around a documented atomic
operation, a coarser lock you own, or an immutable-snapshot swap instead. Don't assume
"every field here is individually a `java.util.concurrent` type" is sufficient evidence of
thread safety without checking whether any invariant spans more than one of them.

## Key takeaways / mental model
Thread safety is a property of invariants under concurrent access, not a property of
individual fields. Composing already-thread-safe pieces is safe exactly when no invariant
spans more than one piece - the moment one does, you need a shared lock (or a redesign)
covering the whole compound operation, and delegation alone will not save you.

## Self-check questions
1. Why does the `NumberRange` example remain buggy even though `AtomicInteger` is
   individually thread-safe for each field?
2. Describe the monitor pattern and explain why never leaking a reference to the guarded
   state is essential to its correctness.
3. What specifically makes client-side locking fragile, and why do many
   `java.util.concurrent` classes deliberately avoid exposing a single lock for this
   purpose?
4. Give an example (not from the lesson) of a class with two fields where delegation to
   each field's own thread safety would be sufficient, and one where it would not be -
   explain the difference in terms of invariants.

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 4:
  "Composing Objects."
