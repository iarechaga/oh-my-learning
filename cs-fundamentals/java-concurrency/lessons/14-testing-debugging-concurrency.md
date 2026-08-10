---
id: java-concurrency/14
subject: java-concurrency
title: Testing and debugging concurrent Java programs
slug: testing-debugging-concurrency
status: drafted
mastery:
seniority: senior
source: Java Concurrency in Practice (Goetz et al.), Chapter 12
prerequisites: [java-concurrency/06, java-concurrency/10]
created: 2026-08-10
updated: 2026-08-10
---

# Testing and debugging concurrent Java programs

## TL;DR
Concurrent bugs are timing-dependent and frequently invisible under normal test load, so
"the tests pass" is weak evidence of correctness. Effective testing separates **safety**
(does it ever produce a wrong answer?) from **liveness** (does it ever hang or stall?),
deliberately increases the odds of hitting bad interleavings (more threads than cores,
randomized delays, stress duration), and leans on tools built for this - thread dumps,
`jcstress`, static analysis - rather than only ad hoc stress loops.

## The idea
`java-concurrency/01` established that a race condition can pass every test on a laptop
and fail constantly in production, because the "bad" interleaving that triggers it might
be astronomically rare under light load and common under real concurrent traffic. This
lesson is about closing that gap as much as possible: techniques that increase the
probability of exposing a genuine concurrency bug during testing, rather than discovering
it in an incident. There is no complete solution - concurrent correctness cannot be
proven by testing alone, only made more or less likely to surface - but a disciplined
approach catches far more than naive unit tests ever will.

## How it works

### Safety tests vs. liveness tests
**Safety tests** check that the program never produces a wrong result - typically
structured as: run many threads performing operations on a shared object concurrently,
then check an invariant afterward (e.g. a shared counter incremented exactly N times by N
threads should read exactly N; a concurrent set should never lose or duplicate an
element). A safety test failure is a clear, reproducible-in-principle wrong answer, even
if the exact interleaving that caused it is hard to pin down.

**Liveness tests** check that the program doesn't hang, deadlock (`java-concurrency/06`),
or fail to terminate within a bound - typically structured as: run the operation under
test with a timeout, and fail the test if the timeout is exceeded. Unlike safety-test
failures, a liveness failure often gives you nothing but "it never returned" - no stack
trace, no exception - which is why capturing a **thread dump** at the moment of the
timeout (many test frameworks and JVM tools can do this automatically) is essential for
diagnosis; without it, you know something hung but not where or why.

### Increasing the odds of exposing a race
A test with two threads on a four-core machine performing one operation each will almost
never expose a subtle interleaving bug - the window is too narrow, and there's too little
contention. Standard techniques to widen that window:
- **More threads than cores** - deliberately oversubscribing (e.g. 4x more threads than
  available cores) increases the frequency of context switches and preemption, which
  increases the odds a "bad" interleaving actually occurs during the test's runtime.
- **`Thread.yield()` or small random sleeps at suspicious points** - inserted temporarily
  (never left in production code) at exactly the point a race is suspected, to make an
  otherwise-narrow timing window far more likely to be hit. This is a targeted diagnostic
  technique for confirming a *specific* suspected race, not a general-purpose testing
  strategy.
- **Run many iterations, not once** - a single test run passing proves almost nothing;
  running the same stress test hundreds or thousands of times (or for an extended
  duration) dramatically increases the cumulative probability of hitting a rare bad
  interleaving, the same logic as running a fuzzer for longer to find a rare crash.
- **Vary the environment** - different core counts, different JVM versions/flags (e.g.
  `-Xint` to disable JIT and change timing characteristics entirely), and different
  machine load can all shift which interleavings are likely, so a bug invisible in CI on
  one machine configuration may reproduce readily on another.

### Worked example: a safety test for a thread-safe counter
```java
@Test
void concurrentIncrementsAreNotLost() throws InterruptedException {
    int nThreads = Runtime.getRuntime().availableProcessors() * 4;   // oversubscribe
    int incrementsPerThread = 100_000;
    AtomicCounter counter = new AtomicCounter();                      // java-concurrency/12
    CountDownLatch startGate = new CountDownLatch(1);                 // java-concurrency/11
    CountDownLatch doneGate  = new CountDownLatch(nThreads);

    for (int i = 0; i < nThreads; i++) {
        new Thread(() -> {
            try {
                startGate.await();       // all threads start together - maximizes contention
                for (int j = 0; j < incrementsPerThread; j++) counter.increment();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                doneGate.countDown();
            }
        }).start();
    }
    startGate.countDown();               // release all threads at (approximately) once
    assertTrue(doneGate.await(30, TimeUnit.SECONDS), "threads did not finish in time");
    assertEquals(nThreads * incrementsPerThread, counter.get());      // safety check
}
```
The `CountDownLatch` start gate is doing real work here beyond convenience: releasing all
threads at once maximizes the number of threads actually contending simultaneously,
which is exactly what widens the window for a lost-update bug (`java-concurrency/01`) to
surface. Note the test is still probabilistic, not a proof - it increases confidence, it
doesn't provide a correctness guarantee.

### Worked example: a liveness test with a timeout
```java
@Test
void acquiringBothLocksInConsistentOrderNeverDeadlocks() throws Exception {
    Account a = new Account(1, 1000), b = new Account(2, 1000);
    ExecutorService pool = Executors.newFixedThreadPool(2);
    Future<?> f1 = pool.submit(() -> a.transferTo(b, 100));
    Future<?> f2 = pool.submit(() -> b.transferTo(a, 50));
    f1.get(5, TimeUnit.SECONDS);          // throws TimeoutException if deadlocked
    f2.get(5, TimeUnit.SECONDS);
    pool.shutdown();
}
```
If `transferTo` deadlocks under the opposite-order interleaving from
`java-concurrency/06`, this test fails with a `TimeoutException` rather than hanging the
test suite forever - critical, because an un-timed liveness test that deadlocks doesn't
just fail, it can hang CI indefinitely.

### Static analysis and tooling
- **FindBugs/SpotBugs, Error Prone** - static analyzers with concurrency-specific checks:
  inconsistent field synchronization (a field sometimes accessed under a lock and
  sometimes not - directly detects the "one missed access breaks the guarantee"
  hazard from `java-concurrency/04`), double-checked locking without `volatile`
  (`java-concurrency/03`), and calling `Thread.run()` instead of `start()`
  (`java-concurrency/01`).
- **Thread dumps (`jstack`, or a JVM's built-in deadlock detector)** - the primary tool
  for diagnosing an already-hung process; the JVM can directly detect and report a cycle
  of `BLOCKED` threads (`java-concurrency/06`).
- **`jcstress` (Java Concurrency Stress tests)** - an OpenJDK-maintained framework
  specifically built to expose JMM-level (`java-concurrency/03`) visibility and ordering
  bugs by running huge numbers of iterations of a small test across many threads and
  cross-checking observed outcomes against what the JMM permits - the right tool when you
  need to verify a subtle happens-before argument empirically, beyond what an ordinary
  unit test can practically probe.
- **Race detectors (e.g. ThreadSanitizer-style tools, less mature in the JVM ecosystem
  than for C/C++)** - instrument memory accesses to detect unsynchronized concurrent
  access directly, rather than relying on the bug actually manifesting as a wrong answer.

### Code review heuristics specific to concurrency
Because tests can't reliably prove concurrent correctness, review discipline matters
disproportionately for concurrent code: check that every piece of shared mutable state
has a documented synchronization policy (`@GuardedBy`, `java-concurrency/05`), that every
compound action (check-then-act) holds its lock across the whole sequence, that
`InterruptedException` is never silently swallowed (`java-concurrency/10`), and that any
multi-lock code path follows a consistent, documented lock ordering
(`java-concurrency/06`). These are exactly the properties automated tests are worst at
catching and human review is comparatively good at catching, because they're structural
properties of the code, not behaviors that need a specific unlucky interleaving to
manifest.

## Pros
- Deliberately widening the interleaving window (oversubscription, repeated runs, varied
  environments) catches real bugs that naive single-pass tests miss entirely.
- Separating safety and liveness testing gives each failure mode a clear, actionable
  signal instead of one ambiguous "the test hung or was wrong somehow."
- Purpose-built tools (`jcstress`, static analyzers, thread dumps) target exactly the
  failure modes ad hoc testing is worst at catching.

## Cons
- No amount of testing proves the absence of a race condition - only increases
  confidence; the theoretical guarantee still has to come from correct design and review
  (`java-concurrency/04`, `java-concurrency/05`).
- Stress tests are inherently slower and flakier than unit tests, complicating CI
  pipelines (a test that occasionally fails due to a real bug looks identical to one that
  occasionally fails due to environmental flakiness, until investigated).
- Techniques like inserted `Thread.yield()`/sleep calls are diagnostic tools for
  confirming a specific suspected race, not something to leave in production code or
  even in the permanent test suite.

## Alternatives
- **Formal verification / model checking** - for the highest-stakes concurrent
  algorithms (e.g. a new lock-free data structure), tools that exhaustively check all
  possible interleavings of a bounded model exist (e.g. TLA+) and give actual proofs
  rather than probabilistic confidence - far more expensive to apply than testing, and
  reserved for genuinely critical, hard-to-get-right algorithms.
- **Design for testability from the start** - favoring higher-level, well-tested
  abstractions (`java.util.concurrent` collections and synchronizers) over hand-rolled
  concurrency reduces how much custom concurrent logic needs this level of scrutiny in
  the first place - the best "testing strategy" is often writing less bespoke concurrent
  code.

## When to use it
Apply stress/safety/liveness testing to any hand-written concurrent class (a custom
synchronizer, a hand-rolled thread-safe collection, anything from `java-concurrency/05`
or `java-concurrency/11`) before trusting it in production, and use thread dumps as the
first diagnostic step whenever a production issue looks like a hang rather than a crash
or wrong answer.

## When NOT to use it
Don't treat a single passing stress-test run as proof of correctness - always run
multiple iterations and vary conditions. Don't leave diagnostic `Thread.yield()`/sleep
insertions in shipped code - they're a temporary tool for confirming a hypothesis, not a
fix. Don't skip design-level review (lock discipline, consistent ordering) on the
assumption that tests will catch what review would have caught more reliably and more
cheaply.

## Key takeaways / mental model
Concurrency bugs hide in narrow timing windows - testing strategy is fundamentally about
widening those windows (more threads, more iterations, varied environments) to make the
bad interleaving likely enough to actually occur during a test run, plus using tools
built to detect specific failure classes (deadlock via thread dumps, JMM violations via
`jcstress`) rather than relying on generic assertions alone. None of this replaces
correct design and disciplined review - it supplements it.

## Self-check questions
1. Why is a concurrent unit test that runs once, with two threads on an eight-core
   machine, weak evidence of correctness compared to the same test run 1,000 times with
   32 threads?
2. Explain the difference between a safety test and a liveness test, and what each looks
   like when it fails.
3. Why is a thread dump essential for diagnosing a liveness test failure, compared to a
   safety test failure?
4. Name two things a static analyzer can catch about concurrent code that a typical unit
   test cannot, and explain why.

## References
- Java Concurrency in Practice (Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea), Chapter 12:
  "Testing Concurrent Programs."
- OpenJDK `jcstress` project documentation, for empirical JMM-level testing beyond what
  the book covers.
