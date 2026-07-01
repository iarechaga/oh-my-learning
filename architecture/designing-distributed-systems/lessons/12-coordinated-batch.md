---
id: designing-distributed-systems/12
subject: designing-distributed-systems
title: "Coordinated Batch Processing"
slug: coordinated-batch
status: drafted
mastery:
seniority: senior
source: "Designing Distributed Systems (Brendan Burns), Chapter 12 (Coordinated Batch Processing)"
prerequisites: [designing-distributed-systems/11]
created: 2026-07-01
updated: 2026-07-01
---

# Coordinated Batch Processing

## TL;DR
Event-driven pipelines (lesson 11) flow freely with no central coordinator, which is exactly why they cannot answer "is the whole batch done?" or run a step that needs *all* the data at once. Coordinated batch processing adds the missing structure: a coordinator, explicit stage boundaries, and **barriers** that hold the next stage until the previous one has fully completed - so you can do reductions (join/aggregate across the entire dataset), guarantee completion, and sequence phases that genuinely depend on one another. The classic realization is MapReduce (map -> shuffle barrier -> reduce). The cost is exactly what event-driven pipelines avoided: a coordinator to run, synchronization points that limit parallelism, and stragglers that stall an entire barrier.

## The idea
Lesson 11's event-driven batch pipelines have a deliberate gap: because stages just react to events with no coordinator, **no one knows when the whole batch is finished**, and no stage can act on the *complete* set of items at once. That is fine for streaming transformations, but many batch jobs fundamentally require both:

- **Completion:** "generate the monthly report *after every* transaction has been processed" needs a definite "all done" signal.
- **Global reduction:** "count word frequencies across *all* documents" or "compute each customer's total across *all* their orders" needs a step that sees the whole dataset (or a whole key group), not one item at a time.
- **Phase dependency:** step B cannot start until step A has *fully* finished for the entire input (not just for the item in hand) - e.g. you cannot rank results until every score is computed.

Coordinated batch processing supplies the structure to do this. It introduces a **coordinator** that knows the stages and drives the job, and **barriers** (synchronization points) that block a downstream stage until the upstream stage has completed across *all* items. Where event-driven pipelines are a free-flowing conveyor, coordinated batch is a set of phases separated by gates: everything must pass through the gate before the next phase begins.

The canonical pattern - and the reason this lesson exists - is **MapReduce**: a *map* phase transforms every input item into key/value pairs in parallel; a **shuffle/barrier** groups all values by key (and must wait for *every* mapper to finish); then a *reduce* phase aggregates each key's full group of values. The barrier between map and reduce is the whole point: reduce cannot start on a key until *all* mappers that might emit that key are done, or it would reduce an incomplete group and produce a wrong answer.

## How it works

### The coordinator and the join/barrier
Two elements distinguish coordinated batch from event-driven batch.

- **A coordinator** owns the job's structure: it knows the stages, launches the workers for each stage, tracks their completion, and only advances to the next stage when the current one is fully done. (For availability the coordinator itself is often a singleton elected via [leader election](09-ownership-election.md) - if it dies mid-job, a new one must take over and resume.)
- **A barrier (a "join" in coordination terms)** is a synchronization point: the coordinator holds the next stage until *all* tasks of the current stage report complete. This is a **fan-in on completion**, distinct from the data-fan-in (merge/join) of lesson 11 - here we wait on "everyone finished," not "match these two streams."

```text
      map phase (parallel)           BARRIER          reduce phase (parallel)
   +--------+ +--------+ +--------+   |wait for   |   +---------+ +---------+
   | map 0  | | map 1  | | map 2  |==>|ALL mappers|==>| reduce  | | reduce  |
   +--------+ +--------+ +--------+   |to finish  |   | key A   | | key B   |
      |          |          |        | + shuffle |   +---------+ +---------+
      +----------+----------+        | by key    |
        emit (key,value) pairs       +-----------+
```

Nothing in the reduce phase runs until the barrier releases - that guaranteed "all-before-any" ordering is what event-driven pipelines cannot provide.

### MapReduce as the archetype, step by step
MapReduce is the coordinated-batch pattern made concrete, and understanding it teaches the whole shape.

1. **Split:** the coordinator divides the input (say a huge set of documents) into chunks, one per map task.
2. **Map (parallel):** each map task processes its chunk and emits intermediate `(key, value)` pairs. For word count, each mapper emits `(word, 1)` for every word it sees. Maps run fully in parallel, like a [work queue](10-work-queues.md).
3. **Shuffle (the barrier):** the system groups all intermediate pairs by key so that *all* values for a given key are collected together - `("distributed", [1,1,1,...])`. This requires every mapper to be finished (a straggler mapper could still emit more `("distributed", 1)` pairs), which is why shuffle is a barrier.
4. **Reduce (parallel):** each reduce task takes one key's complete group of values and aggregates it - `sum([1,1,1,...]) = 42` -> `("distributed", 42)`. Reducers run in parallel across keys, but only after the barrier.
5. **Output:** the coordinator collects reducer outputs and marks the job complete - a definite "done."

The three properties event-driven pipelines lacked all appear here: completion (step 5), global reduction per key (step 4 sees the *whole* group), and phase dependency (reduce strictly after map, enforced by the barrier).

### Why the barrier both enables correctness and limits performance
The barrier is the pattern's source of power *and* its main cost.

- **It enables correctness:** a reduction over a key is only correct once the key's group is *complete*; the barrier guarantees completeness before reduce begins.
- **It creates the straggler problem (again):** the barrier cannot release until the **slowest** task of the phase finishes. One slow mapper (a huge chunk, a slow node, a hot key) stalls the *entire* reduce phase - every reducer waits on that one mapper. This is the scatter/gather tail-latency problem (lesson 07) at batch scale: the phase's duration is set by its slowest task.
- **Mitigations mirror scatter/gather:** *speculative execution* (the coordinator launches a backup copy of a straggler task on another node and takes whichever finishes first), balanced chunking (avoid one giant chunk), and combiner functions (pre-aggregate on the map side to shrink shuffle volume, e.g. emit `("the", 500)` instead of 500 `("the", 1)` pairs).

### Multi-stage coordinated jobs and DAGs
Real jobs are often more than one map+reduce. Frameworks generalize to a **DAG (directed acyclic graph) of stages**, each separated by barriers, where a stage may depend on several upstream stages completing. The coordinator schedules stages in dependency order, launching a stage only when all its prerequisites have passed their barriers. (Spark's stage graph and workflow schedulers like Airflow are this idea; the coordinator turns a dependency graph into a sequence of barrier-gated phases.)

```text
   stage A --\
              >-- [barrier] --> stage C --\
   stage B --/                             >-- [barrier] --> stage D (output)
                              stage C2 ----/
   (C runs only after A and B finish; D runs only after C and C2 finish)
```

### Failure handling and idempotent, re-runnable tasks
Because tasks run on many nodes, some will fail. Coordinated frameworks handle this by making tasks **idempotent and re-runnable**: if a map or reduce task dies, the coordinator simply re-launches it, and because tasks write their output deterministically (to a task-specific location that is only "committed" on success), a re-run produces the same result without double-counting. This is the same at-least-once + idempotency discipline as work queues (lesson 10), now under a coordinator that decides *what* to retry and tracks the barrier so a retried task still gates the next phase correctly. The coordinator's own durability matters too: it must checkpoint job progress so that if it (or its elected leader) restarts, it resumes from the last completed stage rather than redoing the whole job.

### Worked example 1: word count over 100 GB of text (MapReduce end to end)
Count how many times each word appears across 100 GB of documents.

1. **Split:** the coordinator cuts the input into 800 chunks of ~128 MB, one per map task.
2. **Map:** 800 map tasks run (across, say, 100 nodes, 8 at a time). Each emits `(word, 1)` per word. A *combiner* pre-sums within each map output, so a chunk with 300 "the"s emits `("the", 300)` once instead of 300 pairs - shrinking shuffle data massively.
3. **Barrier/shuffle:** the system waits for all 800 mappers, then groups by word so every partial count for "distributed" lands at one reducer: `("distributed", [12, 7, 20, ...])`.
4. **Reduce:** reduce tasks (one group of keys each) sum each word's list: `("distributed", 39)`, `("the", 41022)`, etc. They run only after the barrier.
5. **Output + completion:** the coordinator gathers reducer files and declares the job done - a definite signal that "the count over *all* 100 GB" is complete and correct.

Why coordination was required: you cannot emit a word's final count until *every* chunk that might contain it has been mapped - the barrier guarantees exactly that.

### Worked example 2: a straggler stalls the barrier, fixed by speculative execution
Same job; 799 of 800 map tasks finish in ~30 s, but map task 512 landed on a node with a failing disk and is crawling at 5x slower (~150 s).

1. Without mitigation: the shuffle barrier cannot release until task 512 finishes, so all reducers sit idle for ~120 extra seconds. The whole job's map phase is paced by its single slowest task - the batch straggler problem.
2. With **speculative execution**: at ~60 s the coordinator notices task 512 is far behind its peers and launches a *duplicate* of task 512 on a healthy node. The duplicate finishes in ~30 s. The coordinator takes whichever copy completes first (the healthy one), discards the slow one's output, and releases the barrier at ~90 s instead of ~150 s.
3. This is deliberately the same remedy as hedged requests in scatter/gather (lesson 07): run a backup of the laggard and take the winner. Coordinated batch inherits scatter/gather's tail problem at the barrier and borrows its fix.

### Worked example 3: why an event-driven pipeline could not do this
Suppose you tried the word count as a free-flowing event-driven pipeline (lesson 11): a `count` stage keeps a running per-word tally as document events stream through.

1. At any instant, the `count` stage's tallies are *partial* - more documents may still be flowing in. If you read "distributed = 25" now, you cannot tell whether that is final or whether 10 more documents are in flight.
2. There is no barrier and no coordinator, so there is no moment that means "every document has been counted" - the pipeline never says "done."
3. If a downstream stage needs the *final* counts (e.g. "rank the top 100 words"), it has nothing correct to consume - ranking a partial tally gives a wrong top-100.
4. Coordinated batch fixes precisely this: the map/shuffle/reduce barrier defines "all input consumed," so the reduce output is *final*, and the coordinator's completion signal lets the ranking stage start on correct data.

The example pins down when to reach for coordination over event-driven flow: whenever a step needs the *complete* dataset or you need a trustworthy "finished."

## Pros
- **Completion guarantee:** the coordinator + barriers give a definite "the whole batch is done" signal that free-flowing pipelines cannot.
- **Correct global reductions:** barriers ensure a reduce/aggregate sees a key's *complete* group, so results over the whole dataset are correct, not partial.
- **Phase sequencing:** stages that genuinely depend on prior stages finishing (rank-after-score) are enforced by barriers and dependency-ordered DAGs.
- **Robust failure recovery:** idempotent, re-runnable tasks plus a checkpointing coordinator let the job survive worker (and coordinator) failures without redoing everything.

## Cons
- **A coordinator to run and make reliable:** you need the coordinator (often a leader-elected singleton with checkpointing) - operational weight the event-driven model avoided.
- **Barriers limit parallelism and add latency:** the next phase waits for the slowest task of the current one, so stragglers stall the whole job (the batch tail-latency problem).
- **Less flexible / higher latency than streaming:** coordinated jobs are "run to completion" over a bounded input, unsuited to continuous, low-latency processing.
- **Shuffle can be expensive:** grouping all data by key across the cluster moves a lot of data over the network unless combiners/pre-aggregation shrink it.

## Alternatives
- **Event-driven batch pipeline:** when you need free-flowing per-item transformations with independent scaling and *don't* need global reduction or a completion barrier (lesson 11).
- **Single work queue:** for one flat pass of independent items with no cross-item aggregation and no ordering between phases (lesson 10).
- **Stream processing:** for unbounded, continuous input where you want windowed aggregates and low latency rather than a run-to-completion batch ([ddia/15 - Stream processing](../../ddia/lessons/15-stream-processing.md)).
- **Managed batch frameworks (MapReduce/Hadoop, Spark) and workflow schedulers (Airflow):** implement the coordinator, barriers, shuffle, speculative execution, and DAG scheduling for you rather than hand-building them ([ddia/14 - Batch processing](../../ddia/lessons/14-batch-processing.md)).

## When to use it
- A step must operate on the *complete* dataset or a whole key group (aggregation, sorting, ranking, deduplication across everything).
- You need a definite "the whole batch finished" signal to trigger downstream work.
- Stages have real dependencies (B strictly after A completes for all items), expressible as a barrier-gated DAG.
- The input is bounded and run-to-completion latency is acceptable (minutes/hours), not continuous streaming.

## When NOT to use it
- Per-item transformations that need neither global reduction nor a completion barrier - use an event-driven pipeline or a work queue; a coordinator is overhead.
- Continuous, unbounded, low-latency processing - use a stream processor; coordinated batch is run-to-completion by design.
- Jobs where a single straggler-induced barrier stall is unacceptable and cannot be mitigated - reconsider partitioning or use incremental/streaming aggregation.
- Trivial data volumes where a single process could aggregate everything in memory - the coordination machinery is unjustified.

## Key takeaways / mental model
Think of grading a national exam. In the *map* phase, thousands of graders each score their own stack of papers in parallel. Before you can compute national averages, you must **wait for every grader to finish** (the barrier) and sort all scores by region (shuffle). Only then, in the *reduce* phase, can each region's total be computed correctly - and only when all regions are tallied is the report "done." Two rules of thumb:

1. **Barriers buy correctness and completion at the price of the straggler.** A reduction is only correct on a *complete* group, so the barrier waits for all - which means the slowest task paces the phase; fight it with speculative execution, balanced chunks, and combiners.
2. **Reach for coordination exactly when free-flowing pipelines fail you:** when a step needs the whole dataset, when phases strictly depend on each other, or when you need a trustworthy "the batch is finished." Otherwise prefer the lighter event-driven or work-queue patterns.

## Self-check questions
1. What two capabilities do event-driven pipelines lack that coordinated batch processing provides, and why does the lack of a coordinator cause them?
2. Walk through MapReduce end to end for word count. Why is the shuffle a *barrier*, and what would go wrong if reduce started before all mappers finished?
3. Explain how the barrier both guarantees correctness and creates the straggler problem. How does speculative execution mitigate it, and which serving pattern uses the same trick?
4. Distinguish the "completion barrier" (coordination fan-in) of this lesson from the "merge/join" (data fan-in) of lesson 11. What is each waiting on?
5. What does a combiner do, and why does it matter for shuffle cost? Give the word-count example with and without a combiner.
6. You must compute each customer's lifetime total across all historical orders, then email the top 100 customers - and it must be correct and clearly finished. Explain why an event-driven pipeline is insufficient and sketch the coordinated job (phases, barrier, what runs in parallel, how you handle a straggler and a failed task).

## References
- Designing Distributed Systems (Brendan Burns), Chapter 12: "Coordinated Batch Processing"
- [designing-distributed-systems/11 - Event-Driven Batch Processing](11-event-driven-batch.md)
- [ddia/14 - Batch processing](../../ddia/lessons/14-batch-processing.md)
