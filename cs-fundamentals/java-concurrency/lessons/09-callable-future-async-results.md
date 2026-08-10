---
id: java-concurrency/09
subject: java-concurrency
title: Callable, Future, and asynchronous result handling
slug: callable-future-async-results
status: drafted
mastery:
seniority: mid
source: Java Concurrency in Practice (Goetz et al.), Chapter 6
prerequisites: [java-concurrency/08]
created: 2026-08-10
updated: 2026-08-10
---

# Callable, Future, and asynchronous result handling

## TL;DR
`Callable<T>` is `Runnable` with a return value and the ability to throw checked
exceptions; submitting one to an `ExecutorService` returns a `Future<T>` - a handle to a
result that doesn't exist yet. `Future.get()` blocks until the task completes (or throws
the task's exception, wrapped) - the core primitive for "start this work now, collect its
result later," and the foundation `CompletableFuture` builds on for composing async
pipelines without blocking.

## The idea
`java-concurrency/08` covered submitting a `Runnable` to an executor - fire-and-forget,
no result, no way to know when it finished or whether it threw. Most real asynchronous
work needs a result (or at least needs to know "did this succeed, and when"). `Callable`
and `Future` are the framework's answer: `Callable<T>` is the task type that can return a
value and throw a checked exception (unlike `Runnable`, which can do neither);
`Future<T>` is a *placeholder* for that value, returned immediately on submission, whose
`get()` method is where the calling thread actually waits for the result.

## How it works

### `Callable` vs. `Runnable`
```java
public interface Runnable { void run(); }                          // no return, no checked throws
public interface Callable<V> { V call() throws Exception; }         // returns V, can throw checked
```
```java
ExecutorService pool = Executors.newFixedThreadPool(4);
Future<Integer> future = pool.submit(() -> {
    Thread.sleep(100);       // Callable can throw InterruptedException (checked) directly
    return computeAnswer();
});
```

### `Future<V>`: a handle to a not-yet-existing result
```java
public interface Future<V> {
    boolean cancel(boolean mayInterruptIfRunning);
    boolean isCancelled();
    boolean isDone();
    V get() throws InterruptedException, ExecutionException;
    V get(long timeout, TimeUnit unit)
        throws InterruptedException, ExecutionException, TimeoutException;
}
```
Calling `submit()` returns immediately - the task may not have even started yet, let
alone finished. `get()` is where you actually wait: it blocks the calling thread until the
task completes, then returns its result, or throws:
- **`ExecutionException`** - the task itself threw an exception; the original exception is
  available via `getCause()`. This wrapping is deliberate: it distinguishes "the task
  failed" from "something went wrong in `get()` itself" (e.g. `InterruptedException`
  below), and preserves the original stack trace as the cause.
- **`InterruptedException`** - the *calling* thread (the one blocked in `get()`) was
  interrupted while waiting, not the task itself (`java-concurrency/10`).
- **`CancellationException`** (an unchecked `RuntimeException`) - thrown by `get()` if the
  task was cancelled via `cancel()` before completing.
- The timed `get(timeout, unit)` overload throws `TimeoutException` if the result isn't
  ready within the given time, without cancelling the underlying task - you decide
  separately whether to call `cancel()` after a timeout.

### Worked example: fan-out, then collect
```java
ExecutorService pool = Executors.newFixedThreadPool(4);
List<Future<PriceQuote>> futures = new ArrayList<>();
for (Supplier supplier : suppliers) {
    futures.add(pool.submit(() -> fetchQuote(supplier)));   // fire all requests concurrently
}
List<PriceQuote> quotes = new ArrayList<>();
for (Future<PriceQuote> f : futures) {
    try {
        quotes.add(f.get(2, TimeUnit.SECONDS));               // collect, with a per-quote timeout
    } catch (TimeoutException e) {
        f.cancel(true);                                          // give up on the slow one
    } catch (ExecutionException e) {
        log.warn("quote fetch failed", e.getCause());
    }
}
```
This "fan out, then collect" pattern - submit N independent tasks, then loop calling
`get()` on each `Future` in submission order - is the single most common `Future` usage.
Note the loop still processes results in *submission* order, not completion order: if the
first future is slow and the second finishes instantly, this code still waits on the
first future before ever looking at the second. `ExecutorService.invokeAll()` provides a
convenience for exactly this fan-out-then-collect pattern (blocks until all complete,
returns a `List<Future<T>>` in the same order as the input tasks); for consuming results
in *completion* order instead, you'd use an `ExecutorCompletionService` or a
`CompletableFuture` combinator (see below).

### `cancel()` and interrupt interaction
`future.cancel(true)` attempts to cancel a running task by interrupting its thread (if
`true` is passed and the task hasn't started or is already running); `cancel(false)`
only prevents the task from starting if it hasn't yet, and has no effect on an
already-running task. This only works cleanly if the task itself is **interruption-
responsive** (checks `Thread.interrupted()` periodically, or calls a blocking method that
throws `InterruptedException` and doesn't swallow it) - `java-concurrency/10` covers this
in depth; a `Callable` that ignores interruption cannot actually be stopped by `cancel()`.

### `CompletableFuture`: composing async work without blocking
Plain `Future.get()` has a real limitation: there's no way to say "when this completes,
then do X" without a thread sitting blocked in `get()`. `CompletableFuture<T>` (Java 8+)
implements `Future<T>` but adds a rich set of composition methods that register
continuations instead of blocking:
```java
CompletableFuture<PriceQuote> quote =
    CompletableFuture.supplyAsync(() -> fetchQuote(supplierA), pool)
        .thenApply(q -> applyDiscount(q))          // transform the result, once available
        .exceptionally(ex -> PriceQuote.fallback()); // recover from a failure

CompletableFuture<PriceQuote> best =
    quote.thenCombine(
        CompletableFuture.supplyAsync(() -> fetchQuote(supplierB), pool),
        (a, b) -> a.price() < b.price() ? a : b);    // combine two independent async results

PriceQuote result = best.get();   // still blocks, but only at the one point you actually need it
```
Key methods: `thenApply` (transform a successful result), `thenCompose` (chain another
async operation, flattening nested futures - the async analogue of `flatMap`),
`thenCombine` (join two independent futures), `exceptionally`/`handle` (recover from
failure), and `allOf`/`anyOf` (wait for a collection of futures together). This lets you
build a pipeline of dependent async steps where no thread blocks until the very end (or
never, if you register a final callback instead of calling `get()`) - a substantially
better fit for I/O-heavy pipelines with several dependent async calls than manually
chaining `submit()`/`get()` calls.

### Completion order vs. submission order
When you need results as they arrive rather than in submission order,
`ExecutorCompletionService` wraps an executor and exposes a `take()`/`poll()` queue of
completed futures in *completion* order:
```java
CompletionService<PriceQuote> ecs = new ExecutorCompletionService<>(pool);
for (Supplier s : suppliers) ecs.submit(() -> fetchQuote(s));
for (int i = 0; i < suppliers.size(); i++) {
    Future<PriceQuote> done = ecs.take();   // returns whichever finished first, blocks if none ready
    process(done.get());
}
```
This is the right tool specifically when you want to act on the *fastest* results first
(e.g. show the first successful price quote to a user, cancel the rest) rather than
processing strictly in the order tasks were submitted.

## Pros
- `Future` decouples "start the work" from "wait for the result," letting a caller fan
  out multiple tasks concurrently and collect results later instead of serially blocking
  on each one.
- `CompletableFuture` composes async pipelines declaratively, without a thread blocked in
  `get()` at every intermediate step.
- Checked-exception support in `Callable` (unlike `Runnable`) lets tasks propagate
  failures naturally instead of needing ad hoc wrapping.

## Cons
- `Future.get()` without a timeout blocks indefinitely if the task never completes and is
  never interrupted - always prefer the timed overload in code that must stay responsive.
- `cancel()` only works if the task cooperates with interruption
  (`java-concurrency/10`) - it cannot forcibly stop a task that ignores
  `InterruptedException` or never checks its interrupt status.
- `CompletableFuture`'s composition API is powerful but has a real learning curve, and
  misusing `get()`/`join()` inside a callback chain (blocking inside an async stage) can
  silently reintroduce the exact blocking you were trying to avoid, or exhaust a shared
  thread pool.
- Iterating a `List<Future<T>>` in submission order (rather than completion order) can
  waste time waiting on a slow task while faster results sit ready but unprocessed.

## Alternatives
- **`invokeAll`/`invokeAny`** (`ExecutorService` methods) - convenience methods for
  "submit all these, wait for all" or "submit all these, return the first successful
  one" without manually managing a `List<Future<T>>`.
- **`ExecutorCompletionService`** - when you need completion order rather than submission
  order.
- **Reactive streams (Project Reactor, RxJava)** - for pipelines with backpressure,
  multiple emitted values over time (not just a single eventual result), or complex
  operator chains; `CompletableFuture` models exactly one eventual value, not a stream.

## When to use it
Use `Callable`/`Future` (via `submit()`) whenever a task needs to return a result or
report a failure the caller must observe. Use `CompletableFuture` specifically when you
need to compose multiple dependent or independent async steps without blocking at each
one, or need built-in failure recovery (`exceptionally`/`handle`).

## When NOT to use it
Don't call `future.get()` with no timeout in a request-handling path that must stay
responsive under a slow or hung dependency - always bound the wait. Don't build a large
`CompletableFuture` chain and then immediately call `.get()`/`.join()` on it inline
without a good reason - if you're going to block right away anyway, a simpler
`submit()`/`get()` or `invokeAll()` is often clearer.

## Key takeaways / mental model
`Callable` + `Future` is "start now, collect later" - submission is non-blocking,
`get()` is where waiting actually happens, and exceptions come back wrapped in
`ExecutionException` so failure is a first-class, catchable outcome rather than a crash.
`CompletableFuture` extends this into composable pipelines where continuations replace
blocking waits at every intermediate step.

## Self-check questions
1. What is the difference between the exception a `Future.get()` throws when the task
   itself failed versus when the calling thread was interrupted while waiting?
2. Why does `future.cancel(true)` not guarantee the underlying task actually stops, and
   what has to be true of the task for cancellation to work?
3. Walk through why processing a `List<Future<T>>` in submission order can waste time
   compared to using an `ExecutorCompletionService`.
4. Explain what `thenCompose` does differently from `thenApply`, and why that distinction
   matters when chaining two async operations together.

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 6:
  "Task Execution."
- `java.util.concurrent.CompletableFuture` Javadoc (JDK 8+) for the composition API,
  which postdates the book.
