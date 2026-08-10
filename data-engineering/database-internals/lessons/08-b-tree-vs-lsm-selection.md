---
id: database-internals/08
subject: database-internals
title: "B-Tree vs LSM-Tree: Workload-Driven Engine Selection"
slug: b-tree-vs-lsm-selection
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part I, Chapter 4 and Chapter 7 (comparative synthesis)
prerequisites: [database-internals/03, database-internals/06, database-internals/07]
created: 2026-08-10
updated: 2026-08-10
---

# B-Tree vs LSM-Tree: Workload-Driven Engine Selection

## TL;DR
Neither B-Trees nor LSM-Trees are universally "better" — they sit at different, principled points on the RUM-conjecture trade-off (`database-internals/06`), and the right choice is determined by your actual read/write ratio, latency-predictability requirements, and update pattern (random vs. append-mostly), not by which structure is newer or more fashionable. This lesson is a decision framework, synthesizing `database-internals/03`, `database-internals/06`, and `database-internals/07` into a repeatable evaluation process for a real system.

## The idea
By this point in the subject you understand both families deeply enough to be dangerous with a strong opinion — which is exactly the risk this lesson addresses. Engineers who've just learned LSM-Trees often over-apply them ("sequential writes are always better!"), and engineers steeped in relational-database habits often default to B-Trees out of familiarity rather than fit. The actual answer requires characterizing your workload along a small number of axes and mapping that characterization onto the trade-offs each structure was built to make.

## How it works

### The decision axes
Four questions, asked in order of how strongly they usually decide the outcome:

**1. What's the read:write ratio, and how latency-sensitive are reads?**
B-Trees guarantee every key lives in exactly one place — a point lookup costs a small, predictable number of page reads (`database-internals/03`), nearly always 3-4 even at huge scale, with very little variance. LSM-Trees have read amplification that varies with how much unmerged data currently exists (`database-internals/06`, `database-internals/07`) — a read right after a burst of writes, before compaction catches up, can be meaningfully slower and less predictable than one against a freshly-compacted dataset. If your workload is read-dominated and needs tight, predictable p99 read latency (e.g. a primary OLTP system backing a live user-facing service with SLAs), that alone is often decisive toward a B-Tree.

**2. What's the write pattern: random vs. append-mostly, and how write-heavy?**
B-Trees pay in-place random-write cost on every update, including the possibility of a cascading page split (`database-internals/03`) — fine at moderate write volume, painful at very high sustained write throughput, especially with keys inserted in non-sequential order (worse locality, more scattered page touches). LSM-Trees convert essentially all writes into sequential appends (`database-internals/06`) and defer reconciliation to background compaction — this is the single biggest lever if your workload is genuinely write-dominated (telemetry ingestion, event logging, time-series) rather than read-dominated.

**3. How much does latency *variance* (not just average) matter?**
B-Trees have relatively flat, predictable per-operation latency (barring the rare cascading split). LSM-Trees have periodic latency variance from background compaction competing for disk bandwidth ("compaction stalls," `database-internals/07`) — average throughput can be excellent while tail latency occasionally spikes. Systems with hard real-time or strict SLA requirements (financial trading systems, control systems) often weight this heavily toward B-Trees even if raw average throughput would favor an LSM-Tree.

**4. What does space efficiency and hardware wear cost you?**
LSM-Trees (especially with leveled compaction, `database-internals/07`) generally achieve better long-run space efficiency and, notably, *lower total write volume to the underlying media* than B-Trees for equivalent logical write workloads on SSDs, because sequential writes reduce flash write amplification (`database-internals/01`) even before accounting for the LSM-Tree's own compaction rewrites — this is why LSM-Trees became the default choice for many SSD- and cloud-object-storage-backed systems, independent of the historical HDD-seek argument.

### Worked example 1 — a user-facing OLTP order-management system
Characterize the workload: reads (order lookups by ID, customer order history queries) vastly outnumber writes (new orders, status updates); reads need consistent low latency because a customer is waiting on a page load; writes, while important, are a small fraction of total traffic and not extreme in volume. Applying the axes: read:write ratio strongly favors B-Tree (axis 1 decisive); write pattern isn't punishing (moderate volume, not append-only firehose, axis 2 doesn't override); latency predictability matters a lot for a live customer-facing system (axis 3 reinforces B-Tree). **Verdict: B-Tree-based engine (e.g. PostgreSQL/MySQL's InnoDB) is the clear fit** — this is, unsurprisingly, exactly the profile most relational OLTP databases target by default.

### Worked example 2 — a telemetry/metrics ingestion pipeline
Characterize the workload: extremely high write volume (millions of metric points per second, effectively append-only — nearly nothing gets updated once written), reads are comparatively rare and often aggregate-oriented (scan a time range, compute a rollup) rather than latency-critical single-key point lookups, and the system runs on cost-sensitive commodity or cloud storage where space efficiency and write endurance matter. Applying the axes: write pattern is the dominant signal (axis 2, overwhelming write volume, append-mostly) strongly favoring LSM-Tree; read latency predictability (axis 3) is a lesser concern here since aggregate/scan reads tolerate more variance than a synchronous customer-facing point lookup would; space/wear efficiency (axis 4) further reinforces LSM-Tree on SSD-backed infrastructure. **Verdict: LSM-Tree-based engine (e.g. Cassandra, a time-series database like InfluxDB/TimescaleDB's LSM-backed layers, or a raw RocksDB-based store) is the clear fit.**

### Worked example 3 — a genuinely mixed, ambiguous case
A social-media-style application: writes are frequent (posts, likes, comments) but not extreme; reads are also frequent (feed loads) and latency-sensitive, but the workload also has hot, frequently-updated counters (like counts) that see intense localized write churn. This case doesn't resolve cleanly to either extreme — and that's realistic; many production systems land here. The typical real-world answer is **not** "pick one engine for everything" but rather **workload segmentation**: use a B-Tree-backed store for the latency-sensitive, read-heavy, moderately-written entities (post content, user profiles), and an LSM-Tree-backed store (or a specialized counter/cache layer) for the intensely write-churny, less latency-critical aggregates (like counters, engagement metrics) — accepting the operational cost of running two storage systems in exchange for each workload getting an engine matched to its actual shape, rather than forcing one engine to compromise across a workload that's genuinely bimodal.

### A practical checklist to run before choosing
1. Measure (don't guess) your actual read:write ratio and write pattern (random-key vs. append-mostly/monotonic-key).
2. Determine whether your SLA cares about tail latency variance specifically, or just average throughput.
3. Estimate total write volume and whether it's likely to saturate a B-Tree's random-write capacity on your actual hardware.
4. If the workload is genuinely bimodal (like worked example 3), seriously consider segmenting by entity type rather than forcing a single engine choice.
5. Revisit the decision as the workload evolves — a system that starts read-dominated can become write-dominated as usage patterns shift (e.g. a product pivot toward high-frequency event tracking), and the original engine choice may no longer fit.

## Pros
- Framing the decision as workload axes (rather than "which technology is trendier") produces decisions that are defensible and revisitable as the workload's actual shape becomes known or changes.
- Recognizing bimodal workloads early (worked example 3) avoids the trap of forcing one engine to serve two genuinely different access patterns poorly.

## Cons
- Real workloads are often not cleanly characterized in advance — you may need to prototype against both engine families or migrate later once real traffic patterns are observed, which is itself costly.
- Segmenting storage by workload type (multiple engines) trades a cleaner architecture for operational complexity (more systems to run, monitor, and keep consistent).

## Alternatives
- **Hybrid/tunable engines** (e.g. RocksDB's configurable compaction, or engines offering both B-Tree and LSM-Tree storage modes for different tables/collections within one system) — let you make this trade-off per-table rather than per-database, reducing (but not eliminating) the need for a system-wide binary choice.
- **Fractal Trees / Bε-trees** — a genuine structural middle ground (mentioned in `database-internals/03` and `database-internals/06`) for workloads that don't cleanly favor either extreme.

## When to use it
Run this decision framework any time you're choosing (or reconsidering) a primary storage engine for a new service, or diagnosing why an existing engine choice is straining under a workload that has evolved since the original decision was made.

## When NOT to use it
Don't re-litigate this decision reflexively for every new table/feature within an already-well-fitted system — if your database already matches your dominant workload shape well, adding one moderately-written new table rarely justifies re-evaluating the whole engine choice; reserve full re-evaluation for genuine workload shifts or new services.

## Key takeaways / mental model
Ask, in order: "is this read-dominated with latency SLAs, or write-dominated and append-heavy?" then "does tail-latency variance matter as much as average throughput?" then "is this actually one workload, or two disguised as one?" A B-Tree is a filing cabinet optimized for fast, predictable retrieval; an LSM-Tree is an inbox-then-archive system optimized for fast, cheap intake. Neither is "the modern one" or "the legacy one" — they're different tools built for genuinely different jobs, and most real systems have components that want each.

## Self-check questions
1. Using the four decision axes, walk through why a high-frequency trading order book (extremely latency-sensitive reads, moderate writes) would favor a B-Tree even though its write volume might be nontrivial.
2. Explain why "LSM-Trees have better average write throughput" and "LSM-Trees have worse tail-latency predictability" are both true simultaneously, and why a system might care much more about one than the other depending on its SLA shape.
3. Design worked example 3 (the social app) differently: propose a concrete segmentation of which entities go to a B-Tree-backed store vs. an LSM-Tree-backed store, and justify each choice using the four axes.
4. A system was originally read-heavy (favoring a B-Tree engine) but a product pivot has made it write-dominated (high-frequency event tracking). What signals in production metrics would tell you it's time to revisit the original engine choice, and what would the migration risk/cost trade-off look like?

## References
- Database Internals (Alex Petrov), Part I, Chapter 4 and Chapter 7 (synthesized comparison of B-Tree and LSM-Tree families).
- See also: `database-internals/03`, `database-internals/06`, `database-internals/07` for the underlying mechanics this decision framework draws on, and `ddia/04` for the DDIA-level version of this same comparison.
