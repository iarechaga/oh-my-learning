---
id: seven-databases/09
subject: seven-databases
title: Cross-Database Comparison and Workload-Driven Store Selection
slug: cross-database-selection
status: drafted
mastery:
seniority: senior
source: Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 9
prerequisites: [seven-databases/01, seven-databases/02, seven-databases/03, seven-databases/04, seven-databases/05, seven-databases/06, seven-databases/07, seven-databases/08]
created: 2026-08-10
updated: 2026-08-10
---

# Cross-Database Comparison and Workload-Driven Store Selection

## TL;DR
Choosing a database is a workload-fit decision, not a technology-preference decision: name your read/write ratio, consistency requirements, query shape, and scale trajectory *before* comparing products, and most of the seven systems this subject covered will eliminate themselves quickly once those four dimensions are pinned down. No database is universally "best" — each one this subject covered is the right answer to a specific, nameable set of constraints, and usually the wrong answer to most others.

## The idea
Across `seven-databases/02` through `08`, a pattern recurs: every database makes a deliberate trade — PostgreSQL trades horizontal write-scale for relational correctness and joins; HBase trades query flexibility for massive-scale sorted access; MongoDB trades cross-entity correctness for read-time convenience on aggregate objects; CouchDB trades automatic conflict resolution for offline-first multi-master replication; Neo4j trades write-shardability for traversal speed; DynamoDB trades upfront design flexibility for fully-managed, near-infinite scale; Redis trades durability-by-default for in-memory atomic speed. None of these trades is a flaw to be criticized in isolation — each is calibrated to a specific problem the book chose that database to illustrate.

The practical skill this lesson teaches is turning "which database should we use" into a small number of concrete questions about the *workload*, answering those first, and letting the answers narrow the field — rather than starting from "which database do I already know" or "which database is trending" and working backward to justify it.

## How it works

### The four dimensions that do most of the filtering

**1. Read/write ratio and throughput shape.** Is the workload read-heavy (a content site), write-heavy (event ingestion, logging), or balanced? Is traffic steady or spiky? A write-heavy, high-volume, ever-growing workload (sensor data, clickstream events) points toward HBase (`seven-databases/03`) or DynamoDB (`seven-databases/07`) — both are built around absorbing high write throughput by partitioning across many nodes. A read-heavy workload with a hot working set points toward adding Redis (`seven-databases/08`) in front of whatever system of record you already have, regardless of which one it is.

**2. Consistency needs.** Does a stale read cause real harm (financial balances, inventory that must never oversell, access-control decisions), or is brief staleness a cosmetic, tolerable blemish (view counts, "who's online," social feed ordering)? Real-harm-on-staleness workloads point toward PostgreSQL (`seven-databases/02`), HBase's per-row strong consistency (`seven-databases/03`), or Neo4j's ACID transactions (`seven-databases/06`) — all CP-leaning per the framing in `seven-databases/01`. Tolerable-staleness workloads open up CouchDB (`seven-databases/05`) and DynamoDB's default eventually-consistent mode (`seven-databases/07`), buying availability and scale in return.

**3. Query/access-pattern shape.** Are queries ad hoc and evolving (reporting, admin tools, exploratory analytics), fixed and known upfront (a handful of well-defined lookups), relationship/traversal-heavy (recommendations, fraud rings, org charts), or dominated by exact-key or range-scan access? Ad hoc and evolving points toward PostgreSQL (`seven-databases/02`) or MongoDB (`seven-databases/04`), both of which support flexible querying without redesigning the schema for every new question. Fixed and known-upfront, at scale, points toward HBase or DynamoDB, which demand that discipline but reward it with scale. Traversal-heavy points toward Neo4j (`seven-databases/06`) specifically, regardless of scale, because no other system in this tour makes multi-hop traversal cheap.

**4. Scale trajectory and operational appetite.** Will this genuinely outgrow a single well-tuned primary node, and on what timeline? Does the team have (or want) the capacity to operate a distributed cluster themselves (HBase, self-managed MongoDB/Cassandra) versus preferring a fully-managed service (DynamoDB) versus not needing distributed scale at all (PostgreSQL, a single Redis instance)? A huge fraction of real "let's use a NoSQL database for scale" decisions are made before this question is honestly answered — see `seven-databases/01`'s closing warning against reaching for scale you don't have yet.

### Worked comparison table

| System | CAP lean | Query shape it's built for | Native write-scaling | Operational model |
| --- | --- | --- | --- | --- |
| PostgreSQL (`02`) | CP | Ad hoc, relational, joins | Vertical + manual sharding | Self-managed or managed service |
| HBase (`03`) | CP (per-row) | Exact key / sorted range scan | Native (regions) | Self-managed Hadoop cluster |
| MongoDB (`04`) | CP (tunable) | Ad hoc, aggregate-document | Native sharding | Self-managed or managed (Atlas) |
| CouchDB (`05`) | AP | Map/reduce views, offline sync | Multi-master replication | Self-managed or embedded (mobile) |
| Neo4j (`06`) | CP | Multi-hop traversal | Read replicas only | Self-managed or managed (Aura) |
| DynamoDB (`07`) | AP (tunable) | Exact key / sort-key range | Native (fully managed) | Fully managed only |
| Redis (`08`) | AP (tunable durability) | Atomic structure ops, cache | Native (Cluster mode) | Self-managed or managed |

### Worked scenario walkthroughs

**Scenario A — B2B SaaS invoicing platform.** Financial data, moderate scale (thousands of customers, not billions of rows), needs joins (invoices, line items, payments, customers all relate), correctness matters a great deal (a wrong balance is a real incident). Read/write ratio: balanced, no extreme spikes. **Answer: PostgreSQL (`02`)** — nothing about this workload's scale exceeds what vertical scaling plus replicas comfortably handles, and the relational guarantees are exactly what a financial domain needs. Reaching for DynamoDB here would trade away joins and ad hoc reporting for scale headroom this workload will likely never use.

**Scenario B — IoT fleet telemetry, millions of devices reporting every few seconds.** Write-heavy, extremely high volume, queries are almost entirely "readings for device X in time range Y," consistency needs are moderate (a few seconds of staleness on a dashboard is fine), team has strong ops capacity and wants full infrastructure control. **Answer: HBase (`03`)** — the access pattern (device ID + time-range scan) maps directly onto a well-designed row key, the write volume needs native horizontal scaling, and the team's ops capacity makes self-managing the cluster a reasonable trade for avoiding vendor lock-in and per-request cloud costs at that volume. If the team instead strongly preferred zero ops burden, **DynamoDB (`07`)** with `deviceId` as partition key and timestamp as sort key would be the equally-valid managed alternative — the deciding factor here is genuinely the ops-appetite dimension, not a technical difference in fit.

**Scenario C — Social recommendation engine ("people you may know," fraud-ring detection).** Read-heavy, relationship-traversal-dominated queries at variable depth, moderate data volume, consistency needs are moderate. **Answer: Neo4j (`06`)** — this is the canonical shape Neo4j is built for; no relational or document approach handles variable-depth traversal at comparable speed or query clarity, and the data volume here doesn't push against Neo4j's single-primary write-scaling ceiling.

**Scenario D — Mobile field-data-collection app, intermittent connectivity, multiple inspectors editing overlapping records.** Offline-first is a hard requirement, not an edge case; conflicting concurrent edits are expected and must be handled explicitly; moderate scale. **Answer: CouchDB (`05`)** — this is the one scenario in this tour where CouchDB's specific multi-master, explicit-conflict design is a genuine requirement rather than an interesting alternative; MongoDB's single-primary model would need bespoke conflict handling bolted on to achieve what CouchDB provides natively.

**Scenario E — E-commerce product catalog with rapidly-evolving, category-specific attributes, moderate scale, occasional ad hoc admin queries.** Schema genuinely varies by category (books vs. shirts vs. electronics), read-heavy on "fetch one product, whole," moderate write volume. **Answer: MongoDB (`04`)**, with a strong caching layer in **Redis (`08`)** in front of the hottest product pages — this combination is extremely common precisely because it separates two concerns (flexible document storage, and hot-path read speed) that different systems in this tour each do well.

### Combining systems is normal, not a compromise
Nearly every real production architecture in this space uses more than one database from this tour simultaneously — a relational system of record (PostgreSQL) plus a cache (Redis) plus perhaps a search index or graph layer for one specific feature is a completely ordinary architecture, not a sign of indecision. The skill this lesson teaches is not "pick one winner" but "assign each distinct access pattern in your system to the store best suited for it," which is exactly the same reasoning `seven-databases/01` introduced as "name the actual requirement, then choose," applied now across a whole system rather than one query.

## Pros
- A workload-first framework prevents both common failure modes: over-engineering (reaching for DynamoDB's scale discipline when PostgreSQL would do fine) and under-engineering (forcing a graph-shaped or offline-sync-shaped problem into a relational or single-primary document model).
- Naming the four dimensions explicitly (read/write ratio, consistency needs, query shape, scale/ops trajectory) turns a vague "which database is best" debate into a concrete, checkable decision.
- Recognizing that combining systems is normal encourages assigning each access pattern to its best-fit store, rather than searching for one database to serve a whole application's diverse needs.

## Cons
- Every additional data store in an architecture adds real operational cost (another system to monitor, back up, secure, and keep a team skilled in) — the framework can be misused to justify unnecessary polyglot-persistence sprawl if the "is this pattern different enough to warrant a new store" bar isn't kept honest.
- Workloads change over time; a decision that was correct at launch (PostgreSQL for a small SaaS) may need revisiting as scale or query shape genuinely shifts — this framework is a decision aid at a point in time, not a permanent verdict.
- The four-dimension framework simplifies real decisions that also involve team familiarity, hiring market, existing infrastructure investment, and vendor/cost constraints — technical fit is necessary but not sufficient for a real-world choice.

## Alternatives
- **Default to the team's existing, familiar stack** — often the pragmatically correct choice for small or early-stage systems where the workload doesn't yet clearly demand a specialized store; optimizing for team velocity over theoretical best-fit is a legitimate trade-off this lesson's framework should be weighed against, not blind to.
- **Benchmark-driven selection** — running representative load tests against 2-3 finalist candidates before committing; more rigorous than the qualitative framework here, appropriate when the decision is high-stakes and the workload's shape is well-understood enough to benchmark meaningfully.
- **Multi-model databases** (e.g., PostgreSQL with JSONB and extensions, or genuinely multi-model systems) — reduce the number of distinct stores needed by covering several access patterns adequately (if not optimally) in one system, trading peak fitness-per-pattern for reduced operational surface area.

## When to use it
Apply this framework at the start of any new system's storage design, and revisit it whenever a system's actual (not hypothetical) read/write ratio, consistency needs, query shape, or scale genuinely changes — a new feature that introduces a graph-shaped or offline-sync-shaped access pattern is a legitimate trigger to add a second, purpose-fit store rather than stretching the existing one to cover it poorly.

## When NOT to use it
Don't run this full framework for genuinely small, low-stakes systems where "use what the team already knows and can operate well" is clearly the dominant factor — the analysis has a cost too, and applying it exhaustively to a weekend project or an internal tool with ten users is its own kind of over-engineering. Don't use it to justify adding a store "because it's technically the best fit" if the operational cost of running it isn't honestly accounted for.

## Key takeaways / mental model
Before naming a database, name the workload: read/write ratio, consistency needs, query shape, and scale/ops trajectory. Most of the time, three or four of those dimensions alone eliminate all but one or two of the seven systems in this tour — and it is completely normal for a real system to end up using several of them together, each covering the access pattern it's actually best at, rather than searching for one database to rule the whole application.

## Self-check questions
1. A team is building a multiplayer game needing (a) a persistent player-profile and inventory system, (b) a real-time leaderboard, and (c) a friend/social graph with "mutual friends" queries. Assign each of the three needs to the database from this tour best suited to it, and justify each choice using the four-dimension framework.
2. Explain why "combining multiple databases" is described in this lesson as normal rather than a compromise, and name one real operational cost that combining stores introduces which a single-store architecture avoids.
3. A startup's founding engineer wants to use DynamoDB for everything "because it'll scale forever, so we'll never have to migrate." Using this lesson's framework, what questions would you ask to pressure-test that reasoning, and what's the risk in the decision as stated?
4. Revisit Scenario E (the e-commerce catalog). Six months later, the team adds a "customers who bought X also bought Y" recommendation feature requiring multi-hop traversal over purchase history. Does this change your original MongoDB + Redis recommendation? What, if anything, would you add, and why?

## References
- Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 9: "Wrapping Up" (and synthesis across all preceding chapters).
- See also: `seven-databases/01` through `08` for the per-database detail this synthesis draws on; `ddia/02` (data models), `ddia/10` (partitioning), and `database-internals/08` (engine trade-offs) for deeper cross-cutting background.
