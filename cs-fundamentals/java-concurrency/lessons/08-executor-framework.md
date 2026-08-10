---
id: java-concurrency/08
subject: java-concurrency
title: Task execution with Executor framework
slug: executor-framework
status: drafted
mastery:
seniority: mid
source: Java Concurrency in Practice (Goetz et al.), Chapter 6
prerequisites: [java-concurrency/05, java-concurrency/07]
created: 2026-08-10
updated: 2026-08-10
---

# Task execution with Executor framework

## TL;DR
The `Executor` framework decouples *what* to run (a `Runnable`/`Callable` task) from
*how* and *on what thread* it runs, via a thread pool that manages its own lifecycle.
Prefer a properly configured `ExecutorService` over creating raw `Thread`s per task -
unbounded thread creation under load is one of the most common ways an otherwise-correct
concurrent application falls over in production.

## The idea
`java-concurrency/01` introduced raw `new Thread(...).start()`. That doesn't scale: each
`Thread` is an OS-level resource (megabytes of stack space, real scheduling overhead), and
"one thread per incoming request/task" under load means thread count grows unbounded with
load, eventually exhausting memory or crippling the scheduler with more runnable threads
than cores can usefully context-switch between. The `Executor` framework's core idea:
separate **task submission** (`execute(Runnable)`, decoupled from the caller) from
**task execution policy** (how many threads, what queue, what happens when overloaded) -
so the policy can be tuned, monitored, and swapped without touching the code that
submits work.

## How it works

### The `Executor` interface hierarchy
```java
public interface Executor {
    void execute(Runnable command);
}
public interface ExecutorService extends Executor {
    <T> Future<T> submit(Callable<T> task);      // java-concurrency/09
    void shutdown();                               // java-concurrency/10
    List<Runnable> shutdownNow();
    boolean awaitTermination(long timeout, TimeUnit unit) throws InterruptedException;
    // ...
}
```
`Executor` itself is minimal - just "run this somewhere, eventually." `ExecutorService`
adds task submission with results (`submit`, returning a `Future` -
`java-concurrency/09`) and lifecycle management (`shutdown` - `java-concurrency/10`).
Virtually all real usage is through `ExecutorService`.

### `Executors` factory methods - and why to be wary of most of them
```java
ExecutorService fixed    = Executors.newFixedThreadPool(10);
ExecutorService cached   = Executors.newCachedThreadPool();
ExecutorService single   = Executors.newSingleThreadExecutor();
ExecutorService scheduled = Executors.newScheduledThreadPool(4);
```
- **`newFixedThreadPool(n)`** - a fixed number of threads, backed by an *unbounded*
  `LinkedBlockingQueue`. Bounded thread count, but the task queue can grow without limit
  under sustained overload - the same unbounded-queue memory hazard from
  `java-concurrency/07`, just relocated from your own queue into the executor's internal
  one.
- **`newCachedThreadPool()`** - no fixed limit on thread count (creates a new thread for
  every task if none are idle, up to `Integer.MAX_VALUE`), reaps idle threads after 60
  seconds. Under a sudden burst of tasks, this can create an unbounded number of threads
  - the exact resource-exhaustion hazard raw `Thread` creation had, just automated.
- **`newSingleThreadExecutor()`** - exactly one worker thread, tasks run strictly in
  submission order; if the thread dies from an uncaught exception, a *replacement* thread
  is created automatically (unlike a bare single `Thread`, which just dies).
- **`newScheduledThreadPool(n)`** - supports delayed and periodic task execution
  (`schedule`, `scheduleAtFixedRate`, `scheduleWithFixedDelay`) - the modern replacement
  for the legacy `Timer` class, notably because a `Timer` uses a single thread for all
  scheduled tasks and one task throwing an uncaught exception kills that thread and
  silently cancels every other pending scheduled task; a `ScheduledThreadPoolExecutor`
  does not have this failure mode.

**The general caution**: `Executors`' convenience factories hide the exact queueing and
bounding policy behind a name, and the most common production incident from this API is
"used `newCachedThreadPool` or `newFixedThreadPool` under unexpectedly high load, ran out
of memory from unbounded threads or unbounded queued tasks." For production code, prefer
constructing `ThreadPoolExecutor` directly with an explicit bounded queue and an explicit
rejection policy (see below) so the failure mode under overload is a deliberate, visible
decision rather than a silent default.

### `ThreadPoolExecutor`: the machinery underneath every factory method
```java
new ThreadPoolExecutor(
    corePoolSize,      // threads kept alive even when idle
    maximumPoolSize,    // upper bound on threads under load
    keepAliveTime, unit, // how long excess (beyond core) idle threads live before dying
    workQueue,           // where tasks wait when all core threads are busy
    threadFactory,        // customizes thread creation (naming, priority, daemon flag)
    rejectedExecutionHandler // policy when the queue AND max threads are both full
);
```
**How a task flows through the pool**: if fewer than `corePoolSize` threads exist, start a
new one for the task even if others are idle. Otherwise, try to queue the task. If the
queue is full and fewer than `maximumPoolSize` threads exist, start an additional
("overflow") thread. If the queue is full *and* the pool is already at `maximumPoolSize`,
invoke the `RejectedExecutionHandler`.

**Rejection policies** (what happens when the pool is saturated):
- `AbortPolicy` (default) - throws `RejectedExecutionException` immediately; the caller
  must handle it.
- `CallerRunsPolicy` - runs the task on the *submitting* thread itself, which both gets
  the work done and, critically, throttles the submitter (it can't submit more until this
  one finishes) - a simple, effective backpressure mechanism.
- `DiscardPolicy` - silently drops the task. Rarely appropriate; hides overload.
- `DiscardOldestPolicy` - drops the oldest queued task to make room for the new one.

Choosing an explicit bounded queue plus `CallerRunsPolicy` (or a custom handler that
logs/counts rejections) is a common, deliberate production pattern: it converts "silent
unbounded growth" into "visible, immediate backpressure."

### Sizing the pool
For **CPU-bound tasks**, pool size close to `Runtime.getRuntime().availableProcessors()`
(or +1) is typically optimal - more threads than cores just adds context-switching
overhead with no throughput gain, since every thread is competing for the same limited
CPU time.

For **I/O-bound tasks** (waiting on network, disk, database), threads spend most of their
time blocked, not consuming CPU - a much larger pool size is appropriate, roughly
`N_threads = N_cpu * U_cpu * (1 + W/C)` where `U_cpu` is target CPU utilization (e.g. 1.0
for 100%), `W` is wait time per task, and `C` is compute time per task (Goetz's formula,
Chapter 8). In practice: measure, don't just guess, and prefer a modest pool with
monitoring over an oversized one masking a design problem (`java-concurrency/13`).

### Thread pools and thread confinement interaction
Tasks submitted to the same pool are **not** guaranteed to run on the same thread across
different submissions - `java-concurrency/02`'s `ThreadLocal` cleanup caution is directly
relevant here: a pooled worker thread is reused across many unrelated tasks, so anything
that thread-confines state via `ThreadLocal` must clear it when a task finishes, or state
leaks into the next, logically unrelated task that happens to land on the same thread.

### Worked example: a bounded, monitored executor
```java
BlockingQueue<Runnable> queue = new ArrayBlockingQueue<>(200);
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    8, 8,                                   // fixed core = max: predictable concurrency
    0L, TimeUnit.MILLISECONDS,
    queue,
    new ThreadFactoryBuilder().setNameFormat("worker-%d").build(),
    (task, executor) -> {
        metrics.increment("pool.rejected");
        throw new RejectedExecutionException("pool saturated");
    });
```
Fixed at 8 threads, a bounded 200-task queue, and an explicit rejection handler that both
records the overload and fails loudly - the operator gets a metric and the caller gets an
exception it can act on, instead of either silently queueing forever or silently spawning
unbounded threads.

## Pros
- Decouples task submission from execution policy - the policy (thread count, queueing,
  rejection) can be tuned or monitored independently of the code submitting tasks.
- Reuses threads instead of creating one per task, avoiding the real OS-level cost of
  unbounded thread creation.
- Built-in lifecycle management (`shutdown`, `awaitTermination` - `java-concurrency/10`)
  and (for `ScheduledThreadPoolExecutor`) survives individual task failures without
  losing other scheduled work, unlike legacy `Timer`.

## Cons
- The convenience `Executors` factory methods hide unbounded queueing or unbounded thread
  creation behind an innocuous-looking one-liner - a very common source of production
  memory/resource exhaustion under unexpected load.
- Picking the right pool size requires understanding whether tasks are CPU-bound or
  I/O-bound (or a mix), and getting it wrong wastes throughput either way (too few
  threads under-utilizes I/O wait time; too many adds pure overhead for CPU-bound work).
- Thread reuse means any thread-confined (`ThreadLocal`) state must be explicitly cleaned
  up per task, or it silently leaks across unrelated tasks.

## Alternatives
- **Raw `Thread` per task** - simpler to reason about for a small, fixed number of
  long-lived threads, but doesn't scale and has none of the pool's lifecycle/backpressure
  machinery - generally only appropriate for a handful of known, dedicated background
  threads, not per-request task submission.
- **Fork/Join framework (`ForkJoinPool`)** - purpose-built for recursively-decomposable
  CPU-bound work (divide-and-conquer parallelism) using work-stealing; a better fit than
  a general `ThreadPoolExecutor` when tasks spawn subtasks and wait on them.
- **Virtual threads (Project Loom, JDK 21+)** - lightweight, JVM-managed threads intended
  specifically for blocking I/O-bound workloads at very high concurrency, reducing the
  need to carefully size a pool for I/O-bound work; conceptually a different resource
  model, but task submission still goes through the same `Executor` abstraction (via
  `Executors.newVirtualThreadPerTaskExecutor()`).

## When to use it
Use an explicitly configured `ThreadPoolExecutor` (or a virtual-thread executor, on
modern JDKs, for I/O-bound work) for any workload involving submitting more than a
handful of tasks over the application's lifetime - request handling, background job
processing, parallel batch work.

## When NOT to use it
Don't reach for `Executors.newCachedThreadPool()` or `newFixedThreadPool()` as a default
in production code without understanding their unbounded-queue or unbounded-thread
behavior under overload - construct `ThreadPoolExecutor` explicitly with a bounded queue
and a considered rejection policy instead. Don't use a general-purpose executor for
recursively-decomposable parallel work - use `ForkJoinPool` for that shape of problem.

## Key takeaways / mental model
An executor separates "what work" from "how it runs" - and the "how" (pool size, queue
bound, rejection policy) is a deliberate capacity-planning decision, not a default to
accept blindly. Every `Executors.new*ThreadPool` convenience method has an unbounded
dimension (queue or thread count) somewhere; know which one before you rely on it in
production.

## Self-check questions
1. Explain the exact sequence `ThreadPoolExecutor` follows when a new task arrives: when
   does it start a new thread vs. queue the task vs. invoke the rejection handler?
2. Why is `newFixedThreadPool`'s unbounded internal queue a production risk, given that
   the thread count itself is bounded?
3. Compare `CallerRunsPolicy` and `AbortPolicy`: which one provides backpressure, and how?
4. Why do CPU-bound and I/O-bound workloads need very different pool sizing, and what
   does each additional thread actually buy you in each case?

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 6:
  "Task Execution," and Chapter 8: "Applying Thread Pools" (sizing formula).
