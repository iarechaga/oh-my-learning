---
id: java-concurrency/10
subject: java-concurrency
title: Cancellation, interruption, and shutdown policies
slug: cancellation-interruption-shutdown
status: drafted
mastery:
seniority: senior
source: Java Concurrency in Practice (Goetz et al.), Chapter 7
prerequisites: [java-concurrency/08, java-concurrency/09]
created: 2026-08-10
updated: 2026-08-10
---

# Cancellation, interruption, and shutdown policies

## TL;DR
Java has no safe, forcible way to stop a thread from outside it - `Thread.stop()` is
deprecated and unsafe by design. **Interruption** is the cooperative alternative: setting
a flag that a well-written task must check (or that a blocking call throws
`InterruptedException` in response to) and honor by cleaning up and exiting. Cancellation
and shutdown are only as reliable as every task's interruption discipline - the design
challenge is making sure *every* task, and every blocking call inside it, actually
responds.

## The idea
Sometimes work needs to stop before it finishes: a user cancels a request, a timeout
expires (`java-concurrency/09`'s `Future.get(timeout, ...)`), or the application is
shutting down. Java deliberately does not provide a way to forcibly kill a thread mid-
operation - `Thread.stop()` existed once and is deprecated, because forcibly terminating
a thread at an arbitrary point can leave shared objects in a permanently inconsistent
state (e.g. a thread killed mid-way through updating two fields of an invariant,
`java-concurrency/05`, with no way to know which half completed). The alternative Java
provides instead is **cooperative cancellation via interruption**: a request, not a
command - the target thread must actively participate in stopping itself.

## How it works

### The interrupt flag: request, not command
Every `Thread` carries a boolean **interrupt status** flag.
```java
thread.interrupt();               // sets the flag (or, for a thread blocked in certain
                                    // calls, wakes it with InterruptedException instead)
boolean interrupted = thread.isInterrupted();   // reads the flag, does NOT clear it
boolean was = Thread.interrupted();              // static method: reads AND CLEARS the
                                                    // *calling* thread's own flag
```
Calling `interrupt()` does not stop anything by itself - it only sets a flag (or, if the
target thread is currently blocked in an interruptible operation, causes that operation
to throw `InterruptedException` immediately and clears the flag as it does so). What
happens next is entirely up to the target thread's own code.

### Two ways a task can be interruption-responsive
**1. Polling the flag in a loop:**
```java
public void run() {
    while (!Thread.currentThread().isInterrupted()) {
        doUnitOfWork();
    }
    // clean exit - loop noticed the flag and stopped
}
```
**2. Calling an interruptible blocking method**, which throws `InterruptedException` the
moment the thread is interrupted, instead of requiring a poll: `Thread.sleep()`,
`Object.wait()`, `BlockingQueue.put()/take()` (`java-concurrency/07`), `Future.get()`
(`java-concurrency/09`), `Lock.lockInterruptibly()` (`java-concurrency/11`), and most
blocking I/O in `java.nio` channels.
```java
public void run() {
    try {
        while (true) {
            Task t = queue.take();      // throws InterruptedException if interrupted
                                          // while blocked here
            process(t);
        }
    } catch (InterruptedException e) {
        // clean up, then let the thread exit
    }
}
```

### The cardinal rule: never swallow `InterruptedException`
```java
// WRONG - this destroys the interruption signal. The caller of this method has
// no way to know an interrupt occurred, and the thread's interrupt status is
// gone (catching InterruptedException clears the flag as part of throwing it).
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    // do nothing - "swallowing" the exception
}
```
A method that catches `InterruptedException` and does nothing with it breaks
interruption for every caller above it in the stack - the signal simply vanishes. There
are exactly two correct responses when you catch `InterruptedException` and cannot
propagate it up (e.g. inside a `Runnable.run()`, whose signature can't throw a checked
exception):

**Propagate it**, if your method signature allows:
```java
void doWork() throws InterruptedException {
    Thread.sleep(1000);   // let it propagate - don't catch it at all
}
```
**Restore the interrupt status**, if you must catch it and can't propagate (e.g. inside
`Runnable.run()`):
```java
public void run() {
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();   // restore the flag other code may check
    }
}
```
Restoring the flag means any *later* code in the call stack that polls
`isInterrupted()` (including, notably, an outer loop like the polling example above, or
a thread pool's own bookkeeping) still sees that an interrupt happened, even though this
particular method already handled `InterruptedException` itself. Silently swallowing it
is one of the most common concurrency bugs in real Java codebases, precisely because it
compiles fine, doesn't crash, and only manifests as "cancellation/shutdown mysteriously
doesn't work" much later.

### Cancellation via a custom flag - and why it's often worse than interruption
A tempting DIY alternative:
```java
private volatile boolean cancelled = false;
public void run() {
    while (!cancelled) { doUnitOfWork(); }
}
public void cancel() { cancelled = true; }
```
This works for the polling case, but it doesn't compose: if `doUnitOfWork()` calls a
blocking method (`queue.take()`, `Thread.sleep()`), setting `cancelled` won't wake it up
- the thread stays blocked regardless. Built-in interruption, by contrast, *does* wake a
thread blocked in any interruptible method. A custom cancellation flag is occasionally
appropriate as a *second*, application-level signal layered on top of (not instead of)
standard interruption - but reinventing interruption itself is almost always the wrong
move.

### `ExecutorService` shutdown: `shutdown()` vs. `shutdownNow()`
```java
pool.shutdown();       // graceful: stop accepting new tasks, let queued and
                        // running tasks finish normally
pool.shutdownNow();    // aggressive: stop accepting new tasks, attempt to stop
                        // actively executing tasks (via interrupt), and return the
                        // list of tasks that were queued but never started
boolean finished = pool.awaitTermination(30, TimeUnit.SECONDS);  // wait for either to
                                                                    // actually complete
```
`shutdown()` is the polite default: existing work finishes, new submissions after the
call throw `RejectedExecutionException`. `shutdownNow()` interrupts every actively
running task's thread (relying on those tasks being interruption-responsive to actually
stop promptly) and abandons anything still queued. **Neither call blocks** - both return
immediately; `awaitTermination` is the separate call that actually waits (with a
timeout) for the pool to finish terminating, and is almost always paired with one of the
two shutdown calls in production code, often escalating from graceful to forceful:
```java
pool.shutdown();
try {
    if (!pool.awaitTermination(30, TimeUnit.SECONDS)) {
        pool.shutdownNow();                                  // escalate: force it
        if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {
            log.error("pool did not terminate");
        }
    }
} catch (InterruptedException e) {
    pool.shutdownNow();
    Thread.currentThread().interrupt();                       // restore, per the rule above
}
```

### Ownership: only the thread's owner should interrupt it
A general design rule: only code that "owns" a thread (typically the code that created
it, e.g. an `ExecutorService` managing its own worker threads) should call `interrupt()`
on it. A library or utility method should never interrupt a thread it doesn't own (e.g.
a thread passed to it as a parameter) - interruption is a cooperative protocol, and only
the owner knows what interruption should mean for that thread's current work and how to
recover afterward.

### Uncaught exceptions in pool threads
An uncaught exception in a `Runnable` submitted via `execute()` (not `submit()`) will, by
default, propagate to the pool's `Thread.UncaughtExceptionHandler` (typically printing a
stack trace and letting the thread die - the pool creates a replacement worker thread
automatically). An uncaught exception in a task submitted via `submit()` (returning a
`Future`) is instead captured and re-thrown, wrapped in `ExecutionException`, the next
time `Future.get()` is called (`java-concurrency/09`) - it will never appear in logs or
an uncaught-exception handler unless something actually calls `get()` on that future, a
subtle and common source of silently-swallowed failures in fire-and-forget code that uses
`submit()` and never checks the returned `Future`.

## Pros
- Cooperative interruption avoids the fundamentally unsafe alternative
  (`Thread.stop()`), letting a task clean up its own invariants before exiting rather
  than being killed mid-operation.
- `ExecutorService`'s two-tier shutdown (`shutdown()` then optionally
  `shutdownNow()`) gives a clean default (finish existing work) with an escalation path
  (force it) for when graceful shutdown times out.
- Built-in interrupt support in blocking library methods (`take()`, `sleep()`,
  `Future.get()`) means well-written tasks compose correctly without custom cancellation
  flags.

## Cons
- Cancellation only works if every task, and every blocking call inside every task,
  actually honors interruption - a single un-cooperative task (one that swallows
  `InterruptedException` or loops without checking `isInterrupted()`) cannot be stopped
  by this mechanism at all.
- Swallowing `InterruptedException` is easy to write, compiles cleanly, and breaks
  cancellation silently - a very common real-world bug.
- Submitting fire-and-forget work via `submit()` and never calling `get()` on the
  returned `Future` means task exceptions vanish silently instead of surfacing anywhere.

## Alternatives
- **A custom application-level cancellation flag** - sometimes layered on top of
  interruption for finer-grained "cancel this specific unit of work" semantics beyond
  what a thread-wide interrupt flag expresses, but should not replace standard
  interruption for anything that can block.
- **Timeouts at the call site** (`Future.get(timeout, unit)`, timed `BlockingQueue`
  operations) - bound how long you wait without necessarily stopping the underlying work,
  when stopping it isn't required, only bounding your own wait is.
- **Process-level kill / container restart** - the blunt-force fallback when a task
  genuinely cannot be made interruption-responsive (e.g. calling into non-interruptible
  native code) - not a Java-level tool, but a real operational answer when nothing else
  works.

## When to use it
Design every long-running or blocking task to check `isInterrupted()` (in a polling loop)
or propagate `InterruptedException` (when calling interruptible blocking methods) from the
start - retrofitting interruption support onto a task after the fact is much harder than
building it in.

## When NOT to use it
Don't swallow `InterruptedException` silently, ever - either propagate it or restore the
flag. Don't call `interrupt()` on a thread your code doesn't own. Don't rely on
`shutdownNow()` alone to guarantee tasks actually stop promptly - it only interrupts them;
whether they respond is entirely up to how they were written.

## Key takeaways / mental model
Interruption is a request, not a command - "please stop when convenient," honored
entirely by the target thread's own cooperation. The one rule that matters most in
practice: never catch `InterruptedException` and do nothing with it - propagate it or
restore the flag, every time, everywhere.

## Self-check questions
1. Why can't Java forcibly stop a thread mid-operation, and what specifically goes wrong
   if it tried (in terms of the invariants from `java-concurrency/05`)?
2. Explain the difference between `Thread.isInterrupted()` and the static
   `Thread.interrupted()` method.
3. Walk through why a custom `volatile boolean cancelled` flag fails to stop a thread
   blocked inside `queue.take()`, while calling `interrupt()` on that thread succeeds.
4. What are the two correct responses to catching `InterruptedException` when you can't
   let it propagate, and why is "catch and do nothing" wrong in both cases?

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 7:
  "Cancellation and Shutdown."
