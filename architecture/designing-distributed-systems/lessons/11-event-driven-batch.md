---
id: designing-distributed-systems/11
subject: designing-distributed-systems
title: "Event-Driven Batch Processing"
slug: event-driven-batch
status: drafted
mastery:
seniority: senior
source: "Designing Distributed Systems (Brendan Burns), Chapter 11 (Event-Driven Batch Processing)"
prerequisites: [designing-distributed-systems/10]
created: 2026-07-01
updated: 2026-07-01
---

# Event-Driven Batch Processing

## TL;DR
A single work queue (lesson 10) processes one flat pile of independent tasks; real batch pipelines need *stages* - the output of one processing step becomes the input to the next, wired together by events. Event-driven batch processing composes work-queue-style stages into a pipeline using patterns borrowed from functional programming (copier, filter, splitter, sharder, merge/join), so a stream of items flows through transformations without any central coordinator - each stage reacts to the events the previous stage emits. The power is loose coupling and independent scaling per stage; the difficulty is that multi-stage, fan-out/fan-in topologies make ordering, duplicates, and "did the whole pipeline finish?" genuinely hard to reason about.

## The idea
Lesson 10's work queue is one stage: items in, workers process them, done. But most real batch work is a **pipeline of steps**. Consider ingesting uploaded documents: extract text -> detect language -> translate non-English -> index for search -> notify the owner. That is five stages, each transforming items and passing them on. You *could* build one monster worker that does all five, but then you cannot scale the slow step independently, cannot reuse a step in another pipeline, and cannot evolve one step without redeploying everything.

Event-driven batch processing builds the pipeline instead as **independent stages connected by queues/topics**, where each stage consumes events (items) from its input, does one transformation, and *emits* events to its output - which is the next stage's input. No orchestrator tells stages what to do; each simply reacts to what arrives. This is the batch analog of the event-driven serving model (lesson 08): the wiring is events, and the coupling between stages is only the message contract on the queue between them.

Crucially, the individual transformations are a small vocabulary of reusable shapes, lifted almost directly from functional programming (map, filter, etc.). Once you know the vocabulary, you can describe any pipeline as a composition of these shapes, and each shape is itself a small, reusable, independently scalable stage (often a container or a function). This is the same "reusable building block + named patterns" thesis from lesson 01, now applied to *data flowing through stages* rather than *requests hitting services*.

## How it works

### The stage-and-queue topology
A pipeline is a directed graph of stages connected by queues/topics. Each stage is a work-queue-style consumer of its input and a producer to its output(s).

```text
 input        stage 1         stage 2         stage 3        output
 topic     +-----------+   +-----------+   +-----------+   sink
  ==> [q0] | extract   |=>[q1]| detect  |=>[q2]| translate |=> [q3] => index
           | text      |   | language  |   | (if needed)|
           +-----------+   +-----------+   +-----------+
           (each stage: consume input event, transform, emit output event)
```

Because stages communicate only through the queue between them, each stage is independently deployable and **independently scalable**: if "translate" is 10x slower than "detect language," give it 10x the workers, without touching any other stage. The queue between two stages also acts as a buffer, absorbing rate mismatches (a fast producer stage does not overwhelm a slow consumer stage - the items just wait).

### The functional vocabulary of transformations
Burns catalogs the recurring stage shapes. Naming them lets you compose pipelines the way you compose `map`/`filter`/`reduce` in code:

- **Copier (tee):** duplicates a stream so multiple downstream pipelines each get every item (e.g. send each event to both "index for search" and "archive to cold storage"). This is fan-out where *every* branch gets a copy - like pub/sub.
- **Filter:** drops items that do not match a predicate, passing only the rest downstream (e.g. only forward documents whose language != English into the "translate" stage). Reduces the volume the next stage sees.
- **Splitter:** routes items to *different* outputs based on a condition, with no item dropped and no item duplicated - each goes to exactly one branch (e.g. route `lang=es` to the Spanish pipeline, `lang=ja` to the Japanese pipeline). Contrast with copier (all branches) and filter (drop vs keep).
- **Sharder:** partitions a single stream across N identical downstream instances by a key, for parallelism while preserving per-key ordering (the [sharding](06-sharded-services.md) idea applied to a stream: all events for `doc-42` go to the same shard so they stay ordered).
- **Merge / join:** the fan-in shapes that recombine multiple streams into one - either interleaving several inputs (merge) or matching items from two streams on a key (join). This is the hard one (see below).

```text
copier:   --A--> [ --A--> branch1
                   --A--> branch2 ]      (every item to ALL branches)

filter:   --A--B--C--> [pred] --A--C-->   (B dropped)

splitter: --A(es)--B(ja)--> [ es-> pipe1
                              ja-> pipe2 ] (each item to ONE branch)
```

### Why fan-in (merge/join) is the hard part
Fan-*out* (copier, filter, splitter, sharder) is comparatively easy: one item comes in, zero-or-more go out, and each output stage is just another work queue. Fan-*in* is where event-driven batch gets genuinely senior-level:

- **Joins need state.** To join stream A with stream B on a key, a stage must *remember* items from A that have not yet seen their matching B (and vice versa). That state must live somewhere durable, and you must decide how long to wait for a match (a windowing/timeout policy) - an unmatched item cannot wait forever.
- **Ordering is not guaranteed across the graph.** Items fan out through different stages at different speeds, so two items that started in order can arrive at a downstream merge out of order. If order matters, you must re-sequence (usually via a sharder that keeps a key's items on one path, or by carrying sequence numbers).
- **Duplicates compound.** Every stage is at-least-once (lesson 10), so a duplicate produced early is duplicated again downstream; idempotency and dedup must be designed at each fan-in point, not just once.
- **"Is it done?" is unclear.** With no central coordinator and items fanning out and back in, knowing that the *whole* pipeline has finished processing a batch is not obvious - there is no single queue whose emptiness means "complete." (This is exactly the gap that *coordinated* batch processing, lesson 12, exists to fill.)

### Ordering, duplicates, and idempotency across stages
Because the pipeline is many chained at-least-once queues, the correctness rules from lesson 10 apply *at every stage*, and interact:

1. **Make every stage idempotent** and dedup on a stable item ID, so a redelivery anywhere in the graph does not double-emit downstream.
2. **Preserve order only where you must**, and do it with a sharder that pins a key's items to one ordered path - global ordering across the whole graph is generally not worth its cost.
3. **Bound waiting at joins** with windows/timeouts, and decide explicitly what to do with items that never find a match (drop, dead-letter, or emit as "unmatched").

### Worked example 1: a document-ingestion pipeline as composed shapes
Ingest uploaded documents and make them searchable in the right language.

1. **Input:** each upload emits a `DocUploaded` event onto `q0`.
2. **Extract stage** (map): consumes `q0`, pulls text from the file, emits `DocText` to `q1`. Scaled to match upload rate.
3. **Detect-language stage** (map): consumes `q1`, tags each doc with a language, emits `DocLang` to `q2`.
4. **Filter + splitter:** a *filter* passes only `lang != en` toward translation (English docs skip it, emitted straight to the index queue). A *splitter* then routes by language: `es -> q_es`, `ja -> q_ja`, each to a language-specific translate stage.
5. **Translate stages** (map, per language): each consumes its queue, translates, emits `DocTranslated` to the common `q_index`. The Japanese stage is slow, so it runs 8 workers; the Spanish stage runs 2 - independent scaling.
6. **Index stage** (map): consumes `q_index` (plus the English docs the filter sent directly), writes to the search index, emits `DocIndexed`.
7. **Copier:** `DocIndexed` is teed to both a `notify` stage (email the owner) and an `audit` stage (archive a record) - every indexed doc goes to *both*.

Every step is one named shape (map/filter/splitter/copier), independently scaled, wired only by the queue contracts. No orchestrator; the pipeline *is* the graph of stages reacting to events.

### Worked example 2: a join that needs state and a window
Enrich `ClickEvent`s with `UserProfile`s: two streams, joined on `user_id`.

1. Stream A (`clicks`) and stream B (`profile-updates`) both flow into a **join** stage keyed by `user_id`.
2. The join stage keeps a durable table of the latest known profile per `user_id`. When a click arrives, it looks up the user's profile and emits an enriched `EnrichedClick`.
3. Problem: a click for `user_99` arrives *before* that user's profile has ever been seen. The join cannot emit yet - it must *wait* for the profile. It stashes the click in state, keyed by `user_99`, with a timestamp.
4. When `user_99`'s profile arrives, the join flushes the waiting click(s), enriched. But if the profile never arrives within a **window** (say 10 minutes), the join must decide: emit the click un-enriched, drop it, or dead-letter it. That policy is a deliberate design choice - the join cannot hold unmatched items forever or its state grows without bound.
5. Duplicates: because both input streams are at-least-once, the join dedups clicks by event ID so a redelivered click does not emit twice.

This example is the crux of why merge/join is senior-level: it requires durable per-key state, an explicit windowing/timeout policy, and dedup - none of which the simple fan-out shapes need.

### Worked example 3: ordering broken by fan-out, fixed by a sharder
A pipeline processes account events; for a single account, `AccountCreated` must be processed before `AccountUpdated`.

1. Naive: events fan out to a pool of N parallel processors round-robin. `AccountCreated(acct-7)` goes to processor 2; `AccountUpdated(acct-7)` goes to processor 5. Processor 5 is faster and applies the update *before* processor 2 applies the create -> the update fails ("account does not exist") or corrupts state. Fan-out broke per-account ordering.
2. Fix with a **sharder**: shard the stream by `acct_id` so *all* events for `acct-7` land on the same downstream instance, which processes them in arrival order. Different accounts still process in parallel across shards (throughput preserved), but within an account, order is preserved.
3. This mirrors the partition-key rule from [system-design/11 - Pub/Sub and distributed queues](../../system-design/lessons/11-pubsub-distributed-queues.md): ordering is only guaranteed within a partition, so key related events to the same partition.

## Pros
- **Loose coupling and reuse:** stages communicate only through queue contracts, so each is independently deployable, replaceable, and reusable across pipelines - the building-block thesis for data flow.
- **Independent per-stage scaling:** scale only the slow stage; the buffering queue absorbs rate mismatches between fast and slow stages.
- **Composability from a small vocabulary:** copier/filter/splitter/sharder/merge/join compose into arbitrary pipelines, like functional operators.
- **Resilience per stage:** each stage inherits work-queue fault tolerance (leases, retries, DLQs); a failure in one stage does not stop the others, items just buffer.

## Cons
- **Fan-in is hard:** merge/join needs durable per-key state, windowing/timeout policies, and dedup - the genuinely difficult part of the pattern.
- **Ordering is not guaranteed across the graph:** parallel fan-out reorders items; preserving order requires sharding by key and careful design.
- **Duplicates compound across stages:** at-least-once at every hop means idempotency/dedup must be handled at each stage, not once.
- **Completion is unclear:** with no coordinator, knowing the whole pipeline finished a batch is not obvious - a gap that coordinated batch processing (lesson 12) fills.

## Alternatives
- **Single work queue (one stage):** if the work is truly one flat transformation over independent items, skip the pipeline machinery (lesson 10).
- **Coordinated batch processing:** when you need a defined start/finish, aggregation across the whole dataset, or a barrier between phases, a coordinated framework fits where free-flowing event-driven stages do not (lesson 12).
- **Batch frameworks (Spark, MapReduce):** for large multi-stage analytics with shuffles/joins over a *bounded* dataset and built-in completion semantics, a framework handles staging and fan-in for you ([ddia/14 - Batch processing](../../ddia/lessons/14-batch-processing.md)).
- **Stream processors (Kafka Streams, Flink):** for continuous, unbounded event pipelines with built-in stateful joins, windowing, and exactly-once semantics ([ddia/15 - Stream processing](../../ddia/lessons/15-stream-processing.md)).

## When to use it
- Your batch work is naturally a *pipeline* of distinct transformation steps that differ in cost and should scale independently.
- Steps can be expressed as the standard shapes (map/filter/splitter/sharder/merge) and reused across pipelines.
- You want loose coupling between steps (evolve or replace one without redeploying the rest) and buffering between rate-mismatched stages.
- Items are (mostly) independent, and where they are not, you can shard by key to preserve the ordering that matters.

## When NOT to use it
- The work is a single flat transformation - a lone work queue is simpler (no pipeline).
- You need strong global ordering or exactly-once end-to-end across a complex fan-out/fan-in graph - reach for a stream processor with those built in, or a coordinated framework.
- You need a clear "the whole batch is done" signal or cross-item aggregation - use coordinated batch processing.
- Heavy joins/aggregations over a bounded dataset are the core work - a batch framework does the staging and fan-in for you with less bespoke state management.

## Key takeaways / mental model
Think of an assembly line where each station does one operation and drops the part on a conveyor to the next station - you can add workers to a slow station without touching the others, and the conveyor buffers parts when stations run at different speeds. Splitting the line (different parts to different sub-lines) is easy; *rejoining* sub-lines and matching parts back together is where planning and buffers are needed. Two rules of thumb:

1. **Compose pipelines from the functional shapes.** copier = all branches, filter = keep/drop, splitter = exactly one branch, sharder = partition-by-key (keeps order), merge/join = fan-in. Naming the shape tells you its coupling and its difficulty.
2. **Fan-out is cheap; fan-in and ordering are the cost.** Every stage is at-least-once, so make each idempotent; preserve order only by sharding on the key that matters; and give every join a durable state store plus a window/timeout - and remember there is no built-in "batch complete" signal (that is lesson 12).

## Self-check questions
1. Why compose a batch pipeline from independent event-connected stages instead of one worker that does every step? Name three concrete benefits and the coupling that remains between stages.
2. Define copier, filter, splitter, sharder, and merge/join, and for a stream of documents give one realistic use of each. How do copier, filter, and splitter differ in how many outputs an item reaches?
3. Why is fan-in (merge/join) the hard part? Walk through what state and policies a keyed join needs and what it must do with an item that never finds a match.
4. How can parallel fan-out break per-key ordering, and how does a sharder fix it while keeping throughput? Relate this to partition keys in pub/sub.
5. Why do duplicates "compound" across a multi-stage pipeline, and what must you do at each stage to stay correct?
6. Your pipeline is extract -> classify -> (translate if non-English) -> index -> notify, where translate is 6x slower than the other stages and notify must fire exactly once per document. Describe the shapes you would use at each hop, where you would scale, and how you would guarantee "notify once" despite at-least-once stages.

## References
- Designing Distributed Systems (Brendan Burns), Chapter 11: "Event-Driven Batch Processing"
- [designing-distributed-systems/10 - Work Queue Systems](10-work-queues.md)
- [ddia/15 - Stream processing](../../ddia/lessons/15-stream-processing.md)
