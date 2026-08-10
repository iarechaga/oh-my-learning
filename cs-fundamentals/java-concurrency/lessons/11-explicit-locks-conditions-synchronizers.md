---
id: java-concurrency/11
subject: java-concurrency
title: Explicit locks, conditions, and advanced synchronizers
slug: explicit-locks-conditions-synchronizers
status: drafted
mastery:
seniority: senior
source: Java Concurrency in Practice (Goetz et al.), Chapter 13 and Chapter 14
prerequisites: [java-concurrency/04, java-concurrency/06]
created: 2026-08-10
updated: 2026-08-10
---

# Explicit locks, conditions, and advanced synchronizers

## TL;DR
`ReentrantLock` and `Lock` give everything `synchronized` (`java-concurrency/04`) gives,
plus what it can't: `tryLock` (non-blocking attempt), timed acquisition, interruptible
acquisition, and multiple wait-conditions per lock via `Condition`. `CountDownLatch`,
`Semaphore`, `CyclicBarrier`, and `Exchanger` are higher-level, purpose-built
synchronizers built on the same underlying machinery (`AbstractQueuedSynchronizer`) for
specific coordination patterns you would otherwise hand-roll with `wait`/`notify`.

## The idea
`java-concurrency/04` covered `synchronized` - simple, always available, but rigid: you
cannot attempt a lock without committing to block indefinitely, cannot time out, cannot
interrupt a thread stuck waiting for it, and get exactly one implicit wait-condition per
lock (`Object.wait()`/`notify()`/`notifyAll()`, tied to the monitor). `java-concurrency/06`
showed why unconditional blocking acquisition is part of what makes deadlock unrecoverable
- once blocked, a thread using `synchronized` has no way out. `java.util.concurrent.locks`
exists to give you an escape hatch from exactly that rigidity, plus a set of ready-made
synchronizers for coordination patterns common enough to deserve their own class instead
of hand-rolled `wait`/`notify` logic every time.

## How it works

### `ReentrantLock`: `synchronized`'s explicit cousin
```java
private final ReentrantLock lock = new ReentrantLock();
public void doWork() {
    lock.lock();
    try {
        // critical section
    } finally {
        lock.unlock();   // MUST be in finally - unlike synchronized, nothing
    }                       // automatically releases the lock on exit
}
```
**The finally block is not optional.** `synchronized` releases its lock automatically
when the block exits, even via exception. `ReentrantLock.unlock()` is a plain method call
- if you forget the `finally`, an exception mid-critical-section leaves the lock held
forever, and every other thread waiting for it blocks permanently. This is the single
most important discipline difference from `synchronized`, and the most common bug when
migrating code to explicit locks.

**What `ReentrantLock` adds beyond `synchronized`:**
```java
if (lock.tryLock()) {                 // non-blocking attempt; returns immediately
    try { /* ... */ } finally { lock.unlock(); }
} else {
    // do something else instead of blocking - e.g. the timed-retry-with-backoff
    // fix for deadlock/livelock from java-concurrency/06
}

if (lock.tryLock(500, TimeUnit.MILLISECONDS)) {   // timed attempt
    try { /* ... */ } finally { lock.unlock(); }
} else {
    // gave up after 500ms - converts an unrecoverable deadlock risk into a
    // recoverable, retryable failure
}

lock.lockInterruptibly();             // blocks, but responds to interrupt()
                                        // (java-concurrency/10) - plain lock() does not
```
`lockInterruptibly()` matters specifically because plain `synchronized` blocking cannot be
interrupted at all - a thread stuck waiting for an intrinsic lock is stuck until it gets
the lock, full stop, even if another thread calls `interrupt()` on it. This makes
`ReentrantLock` the right choice whenever a lock-acquisition wait needs to participate in
the cancellation story from `java-concurrency/10`.

**Fairness.** `new ReentrantLock(true)` constructs a *fair* lock: threads acquire it in
roughly the order they requested it (FIFO), avoiding the starvation risk
(`java-concurrency/06`) a non-fair lock can produce under heavy contention, where a newly
arriving thread can "barge" ahead of threads that have been waiting longer. Fair locks
have measurably lower throughput under contention (more context switching, no barging
optimization) - the default is non-fair specifically because most applications value
throughput over strict ordering.

### `Condition`: multiple wait-queues per lock
`Object.wait()`/`notify()` gives exactly one implicit condition queue per monitor.
`ReentrantLock.newCondition()` can create several, letting you signal precisely the
threads waiting for a *specific* condition instead of waking every waiter and having them
each re-check.

```java
public class BoundedBuffer<T> {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull  = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();
    private final Queue<T> items = new ArrayDeque<>();
    private final int capacity;

    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (items.size() == capacity) notFull.await();  // releases lock while waiting
            items.add(item);
            notEmpty.signal();                                    // wake ONE waiting taker
        } finally { lock.unlock(); }
    }
    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (items.isEmpty()) notEmpty.await();
            T item = items.remove();
            notFull.signal();                                     // wake ONE waiting putter
            return item;
        } finally { lock.unlock(); }
    }
}
```
This is, in essence, what `ArrayBlockingQueue` (`java-concurrency/07`) is built from
internally: two conditions on one lock, so a full-buffer signal only ever wakes threads
actually waiting for space, and an empty-buffer signal only wakes threads waiting for
data - far more efficient than a single `notifyAll()` waking every waiter (of both kinds)
to have most of them immediately re-check their condition and go back to waiting.

**Always `await()` in a `while` loop, never `if`.** A woken thread must re-check its
condition, because between being signaled and actually resuming execution and re-
acquiring the lock, another thread could have run and changed the state again (a
**spurious wakeup** is also explicitly permitted by the JVM specification - a thread can
wake from `await()`/`wait()` with no corresponding `signal()`/`notify()` at all). The
`while` loop makes the wait genuinely robust to both cases; an `if` does not.

### `CountDownLatch`: wait for N events, once
```java
CountDownLatch startGate = new CountDownLatch(1);
CountDownLatch doneGate  = new CountDownLatch(nWorkers);
for (int i = 0; i < nWorkers; i++) {
    new Thread(() -> {
        try {
            startGate.await();          // all workers wait for the same start signal
            doWork();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            doneGate.countDown();       // signal this worker is done
        }
    }).start();
}
startGate.countDown();                  // release all workers at once
doneGate.await();                       // wait for every worker to finish
```
A latch counts down from N to zero and cannot be reset - once it reaches zero, every
current and future `await()` call returns immediately, forever. This makes it perfect
for exactly two shapes: "wait for one signal to release many threads at once" (start
gate) and "wait for many threads to each finish once" (done gate) - but useless for any
recurring coordination, because it's single-use by design.

### `Semaphore`: bound concurrent access to N permits
```java
Semaphore connectionLimiter = new Semaphore(10);   // at most 10 concurrent uses
void useConnection() throws InterruptedException {
    connectionLimiter.acquire();       // blocks if all 10 permits are taken
    try {
        // use a connection
    } finally {
        connectionLimiter.release();    // MUST release, symmetric to lock's finally rule
    }
}
```
A binary semaphore (`new Semaphore(1)`) behaves like a lock but without the ownership
requirement `ReentrantLock` and `synchronized` both have (a thread other than the one that
acquired a lock cannot release it; with a `Semaphore`, any thread can call `release()`,
which is occasionally exactly what you want - e.g. one thread producing permits, a
different thread consuming them - but is also easy to misuse if you actually needed
ownership semantics).

### `CyclicBarrier`: wait for N threads, repeatedly
```java
CyclicBarrier barrier = new CyclicBarrier(4, () -> System.out.println("all 4 arrived"));
// each of 4 worker threads:
doPhaseOneWork();
barrier.await();     // blocks until all 4 have called await() for this phase
doPhaseTwoWork();
barrier.await();     // barrier resets automatically - reusable for the next phase
```
Unlike `CountDownLatch`, a `CyclicBarrier` is reusable: once all N parties arrive, it runs
an optional action and resets for the next round - suited to iterative parallel
algorithms where threads must synchronize at the end of each phase before any of them
proceeds to the next (e.g. successive rounds of a parallel simulation).

### `Exchanger`: two threads, one hand-off point
```java
Exchanger<DataBuffer> exchanger = new Exchanger<>();
// Thread A (filler)                              // Thread B (drainer)
DataBuffer full = exchanger.exchange(emptyBuffer); DataBuffer empty = exchanger.exchange(fullBuffer);
```
Both threads block at `exchange()` until the other arrives, then each receives what the
other passed in - a strict two-party, symmetric rendezvous, useful for pipeline designs
where one thread fills a buffer while another drains a previously-filled one and they
swap roles each round.

### `AbstractQueuedSynchronizer` (AQS): what these are all built from
All of the above (`ReentrantLock`, `Semaphore`, `CountDownLatch`, and even
`ReentrantReadWriteLock`) are implemented on top of `AbstractQueuedSynchronizer`, a
framework class providing a `volatile int` state field, an internal FIFO queue of
blocked threads, and template methods (`tryAcquire`, `tryRelease`, etc.) that subclasses
override to define what "acquired" and "released" mean for their specific semantics.
You'll rarely subclass AQS directly, but recognizing it explains why all these
synchronizers share the same acquisition-blocks-and-queues, release-wakes-the-next-waiter
behavior and performance characteristics under contention.

## Pros
- `tryLock`, timed acquisition, and `lockInterruptibly()` give escape hatches from
  unconditional blocking that `synchronized` fundamentally cannot offer.
- Multiple `Condition`s per lock let you signal precisely, avoiding the "wake everyone,
  most go back to sleep" inefficiency of a single monitor's `notifyAll()`.
- Purpose-built synchronizers (`CountDownLatch`, `Semaphore`, `CyclicBarrier`,
  `Exchanger`) express common coordination patterns far more clearly and safely than
  hand-rolled `wait`/`notify` code.

## Cons
- `ReentrantLock` requires manual `unlock()` in a `finally` block - forgetting it is a
  real, easy-to-make bug that `synchronized` structurally prevents.
- More API surface and more decisions (fair vs. non-fair, which `Condition`, `tryLock`
  vs. `lock`) than `synchronized`'s single keyword - more power, more ways to misuse it.
- `CountDownLatch` and `CyclicBarrier` solve different shapes of problem and are easy to
  reach for incorrectly (a one-shot latch where you actually need repeated
  synchronization, or vice versa).

## Alternatives
- **`synchronized`** (`java-concurrency/04`) - simpler, structurally leak-proof, and
  sufficient whenever you don't need `tryLock`/timeouts/interruptibility/multiple
  conditions - the right default until you have a concrete reason to reach further.
- **`BlockingQueue`** (`java-concurrency/07`) - for producer-consumer hand-off
  specifically, a purpose-built blocking queue is usually simpler than building the same
  thing from a `Lock` and two `Condition`s, as the worked example above shows.
- **Atomic variables** (`java-concurrency/12`) - for simple state (a counter, a
  reference) where no thread ever needs to *block* waiting for a condition, lock-free
  atomics avoid locking (and its overhead) entirely.

## When to use it
Reach for `ReentrantLock` specifically when you need `tryLock`, a timeout, interruptible
acquisition, or more than one wait-condition on the same lock. Reach for
`CountDownLatch` for one-shot "wait for N events" coordination, `Semaphore` for bounding
concurrent access to a limited resource, `CyclicBarrier` for repeated phase
synchronization among a fixed set of threads, and `Exchanger` for a strict two-party
buffer swap.

## When NOT to use it
Don't default to `ReentrantLock` over `synchronized` without a concrete need for its
extra capabilities - the manual-unlock discipline is a real risk for no benefit if you
never use `tryLock`/timeouts/multiple conditions. Don't use a `CountDownLatch` where you
need repeated synchronization (use `CyclicBarrier`) or vice versa.

## Key takeaways / mental model
`ReentrantLock` trades `synchronized`'s automatic safety for explicit control - use it
when you specifically need `tryLock`, timeouts, interruptibility, or multiple conditions,
and never forget the `finally`. The purpose-built synchronizers each encode one specific
coordination shape - matching the shape of your problem to the right one (one-shot vs.
repeated, N-permits vs. two-party exchange) is most of the design work.

## Self-check questions
1. Why must `ReentrantLock.unlock()` always be called in a `finally` block, and what
   happens to other threads if it isn't?
2. Explain why `await()` on a `Condition` (or `wait()` on a monitor) must always be
   called in a `while` loop checking the condition, not an `if`.
3. Give a scenario where `CountDownLatch` is the right tool and one where
   `CyclicBarrier` is the right tool - what's the key difference in requirements between
   them?
4. What specific capability does `lockInterruptibly()` provide that plain
   `synchronized` blocking cannot, and why does that matter for the cancellation story
   in `java-concurrency/10`?

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 13:
  "Explicit Locks," and Chapter 14: "Building Custom Synchronizers."
