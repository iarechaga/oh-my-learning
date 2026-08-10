---
id: sre/13
subject: sre
title: Data Processing Reliability and Pipeline Operations
slug: data-processing-reliability
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 25-26
prerequisites: [sre/02, sre/11]
created: 2026-08-10
updated: 2026-08-10
---

# Data Processing Reliability and Pipeline Operations

## TL;DR
Batch and streaming data pipelines fail differently from request-serving services — a pipeline can be "up" (workers running, no crashes) while silently producing wrong or stale results, which no simple availability SLI would catch. Reliable pipeline operations require SLIs built specifically for correctness and freshness (not just liveness), idempotent and replayable processing so reruns are safe, and integrity checks that catch silent data corruption before it propagates downstream.

## The idea
A request-serving service's failure mode is usually loud: a request times out, returns an error, or the server crashes — something a user or a monitor notices quickly. A data pipeline's most dangerous failure mode is quiet: a job "succeeds" (exit code 0, no crash) but processes a truncated input, applies a subtly wrong transformation, or writes stale data to a downstream table — and nothing about the job's own execution signals a problem. The output looks complete; it's just wrong, or old, or missing a chunk that got silently dropped.

This is why the golden-signals framework from `sre/07` (latency, traffic, errors, saturation) is necessary but not sufficient for pipelines — none of those four signals directly measure "did the output data mean what we think it means." Data-pipeline reliability needs its own additional dimension: **correctness and freshness of the actual data produced**, verified independently of whether the job process itself reported success.

## How it works

### SLIs for pipelines: freshness and correctness, not just liveness
Building on `sre/02`'s SLI framework, a pipeline's SLIs typically include:
- **Freshness** — how stale is the most recently processed data relative to when it arrived? E.g., "99% of events are reflected in the aggregated table within 15 minutes of ingestion."
- **Completeness** — what fraction of expected input records actually got processed? E.g., "99.9% of daily active-user events from the source log are present in the daily rollup."
- **Correctness** — does the output match an independently verifiable expectation? Often checked via reconciliation against a known-good source, a checksum, or a row-count/aggregate-sum comparison, rather than by re-deriving correctness from the pipeline's own logic (which would just repeat any bug the pipeline itself has).

**Worked example.** A daily billing-aggregation pipeline processes the previous day's transaction events into per-customer totals. A completeness SLI compares the count of transaction events consumed by the pipeline against the count of events actually written to the source topic that day (from an independent source-side counter): if the source counted 4,082,113 events and the pipeline processed 4,081,940, that's `4,081,940 / 4,082,113 = 99.996%` completeness — technically very high, but if the SLO is 99.999% (allowing roughly 41 missing events/day), this run is a real SLO breach worth investigating (173 missing events, in a billing context, is real money), even though the job itself exited successfully with no errors logged.

### Idempotency: making reruns safe
A pipeline stage is idempotent if running it twice on the same input produces the same result as running it once — critically important because pipeline reliability work depends heavily on being able to safely *rerun* a failed or suspect stage without manually reasoning about what partial state it left behind. **Worked example.** A non-idempotent aggregation job that does `UPDATE customer_totals SET total = total + new_amount` will double-count if rerun after a partial failure (some rows already updated, job crashes, gets rerun from the start) — the second run adds `new_amount` again on top of the already-updated rows. An idempotent version instead computes `SET total = (recomputed_total_from_source)` or uses a write-once, keyed-by-batch-id output table that a rerun simply overwrites rather than accumulates onto — safe to rerun any number of times with the same result.

### Replayability and backfills
Because pipelines process historical data (not just live traffic), a reliable pipeline design supports replaying a specific time range from raw source data — essential both for recovering from a discovered bug (rerun the last 30 days with the fix applied) and for the routine event of upstream data arriving late. **Worked example.** A pipeline discovers on day 10 that a transformation bug has been silently mis-computing a field since day 1. Because the pipeline's design kept raw source events retained and the transformation stage is idempotent, the team can replay days 1-10 with the fixed logic and overwrite the affected output rows — a bounded, well-understood recovery. A pipeline that discarded raw inputs after processing (to save storage) or that isn't idempotent would instead require a much more fragile, bespoke manual reconciliation to fix the same bug's damage.

### Watermarks and late-arriving data
Streaming pipelines face a specific freshness challenge: events don't always arrive in the order they occurred (network delays, retried client uploads), so a pipeline must decide how long to wait for late data before considering a time window "final." A **watermark** is the pipeline's declared cutoff: "we consider all events with a timestamp before T to be complete as of now." **Worked example.** A streaming pipeline aggregating 5-minute windows sets a watermark of 2 minutes past each window's end, to absorb typical late-arrival delay. An event that arrives 3 minutes late (after the watermark has passed) is either dropped (with a corresponding drop in the completeness SLI, which should trigger investigation if the drop rate rises) or triggers a late-update/retraction of the already-emitted aggregate, depending on the pipeline's design — this tradeoff (freshness vs. completeness) is explicit and must be a deliberate design decision, not an accident of default settings.

### Data integrity checks as a defense layer
Beyond SLIs measured continuously, the book recommends periodic, independent integrity checks that don't rely on the pipeline's own success signal at all — e.g., a nightly reconciliation job that sums a key metric from two independently maintained systems (the pipeline's output and an audit log) and alerts if they diverge beyond a small tolerance. **Worked example.** A reconciliation check compares total revenue computed by the billing pipeline against total revenue recorded by the payment processor's own independent ledger for the same day; a divergence of more than 0.01% triggers a page, because at that point silent data corruption (not a processing crash) is the most likely explanation, and it's exactly the failure mode this lesson opened with — one that liveness monitoring alone would never catch.

## Pros
- Freshness/completeness/correctness SLIs catch the pipeline's most dangerous failure mode (silent wrongness) that liveness-only monitoring misses entirely.
- Idempotent, replayable design makes recovery from a discovered bug a bounded, well-understood operation instead of a fragile manual reconciliation project.
- Independent integrity checks (reconciliation against a second source) provide a defense layer that doesn't depend on trusting the pipeline's own self-reported success.

## Cons
- Building freshness/completeness/correctness SLIs requires an independent source of truth to compare against (an upstream counter, an external ledger) — not every pipeline has one readily available.
- Idempotent design and raw-input retention (for replayability) cost real storage and engineering effort, and retrofitting idempotency onto an existing non-idempotent pipeline can be a significant project.
- Watermark tuning is a genuine tradeoff with no universally correct answer — too short drops real late data, too long delays freshness, and different downstream consumers may want different tradeoffs from the same pipeline.

## Alternatives
- **Liveness-only monitoring (job succeeded/failed, ran on schedule)** — cheap and catches gross failures (crashes, missed schedule runs), but as this lesson argues, is blind to the most costly failure mode: a job that "succeeds" while producing wrong or incomplete output.
- **Manual, ad hoc reconciliation after an incident is suspected** — no ongoing investment required, but relies on someone noticing something looks wrong first (often much later, after the bad data has already propagated to downstream reports or decisions), rather than catching it proactively via a standing SLI.
- **Exactly-once processing guarantees at the infrastructure level** (where the underlying streaming platform supports it) — removes the need for idempotent application logic in some cases, but doesn't eliminate the need for freshness/completeness SLIs or cross-system integrity checks, since infrastructure-level exactly-once guarantees don't protect against a genuine logic bug in the transformation itself.

## When to use it
Apply freshness/completeness/correctness SLIs, idempotent design, and independent integrity checks to any pipeline whose output feeds a real business decision, a customer-facing number (billing, usage reporting), or another system's SLO. Prioritize idempotency and raw-input retention specifically for pipelines where a future bug fix requiring a backfill is a realistic scenario — which is most pipelines processing anything non-trivial.

## When NOT to use it
Don't over-invest in independent reconciliation infrastructure for a low-stakes internal analytics pipeline where an occasional small discrepancy has no real consequence — liveness monitoring plus a basic completeness check is likely sufficient. Skip strict watermark/late-data handling complexity for a pipeline where a small amount of dropped late data has genuinely no downstream impact.

## Key takeaways / mental model
A pipeline that exits successfully hasn't told you whether its output is right — only that it didn't crash. Measure freshness, completeness, and correctness directly, ideally against an independent source of truth. Design for safe reruns (idempotency) and bounded recovery (replayability from retained raw input), because the question isn't *whether* you'll discover a bug in a pipeline's logic after the fact, it's how expensive fixing the resulting bad data will be when you do.

## Self-check questions
1. A daily ETL job has run successfully (exit code 0) every day for six months, but a downstream analyst discovers the output has been silently missing about 2% of records the whole time due to a filtering bug. What kind of SLI, if it had existed, would have caught this months earlier, and why wouldn't liveness monitoring have caught it?
2. Explain, with a concrete example, why `SET total = total + new_amount` is not idempotent while `SET total = recomputed_total` is, and why this distinction matters specifically for pipeline reliability rather than request-serving reliability.
3. A streaming pipeline shortens its watermark from 5 minutes to 30 seconds to improve freshness. Predict the effect on the completeness SLI, and explain the tradeoff the team is making.
4. Why does the book recommend an integrity check that compares the pipeline's output against an *independent* second source, rather than just re-running the pipeline's own logic as a check?

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 25 ("Data Processing Pipelines") and Chapter 26 ("Data Integrity: What You Read Is What You Wrote").
- See also: `sre/02` (SLIs, extended here to freshness/completeness/correctness) and `sre/11` (capacity planning, which applies equally to pipeline throughput sizing).
