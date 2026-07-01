---
id: ddia/16
subject: ddia
title: "The Future of Data Systems"
slug: future-of-data-systems
status: drafted
mastery:
seniority: staff
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 12"
prerequisites: [ddia/13, ddia/15]
created: 2026-06-30
updated: 2026-06-30
---

# The Future of Data Systems

## TL;DR
This capstone chapter synthesizes the core principles of data engineering by exploring how to integrate specialized tools using an event log backbone. We can turn the database inside out by unbundling its storage, indexing, and caching layers into composable, stream-connected services. Achieving correctness requires end-to-end application-level guarantees, active auditing, and a deep appreciation of the ethical hazards of data collection.

## The idea
No single database can satisfy all the data storage, indexing, and analytical requirements of a modern, large-scale application. Throughout this learning path, we have examined specialized systems: relational databases for transactional integrity, caches for low latency, search indexes for full-text lookup, and column-oriented warehouses for massive analytics.

We also explored how consensus protocols guarantee consistency in [13-consistency-and-consensus.md](./13-consistency-and-consensus.md), and how stream processors manage continuous event flows in [15-stream-processing.md](./15-stream-processing.md). Understanding these disparate systems is only the first step. The true challenge lies in assembling them into a coherent, resilient architecture that remains correct in the face of inevitable failures.

The central problem of modern system design is integration. If we write to multiple independent databases directly, we risk permanent inconsistency because of network failures or application crashes.

The final chapter of Martin Kleppmann's work provides a comprehensive synthesis. It argues that by treating a complex system as an unbundled database (turning the database inside out) and using an append-only log as the system's central nervous system, we can safely and reliably keep all specialized views in perfect sync. This design philosophy enables us to scale our systems to massive proportions while maintaining clear guarantees of correctness.

## How it works
Modern systems require us to think about data integration, unbundled database architectures, and end-to-end correctness. Let's look at how these concepts fit together. By combining specialized storage engines with an append-only log, we can coordinate updates without distributed locking and build robust, high-performance distributed systems.

### Data Integration and the Evolution of Architectures
When an organization uses specialized tools (such as relational databases, full-text search indexes, and caching layers), keeping them in sync becomes a fundamental challenge. Traditional systems often try to write to multiple datastores simultaneously. This approach (the dual-write problem) is extremely fragile because network partitions or partial failures can cause the datastores to permanently diverge.

To resolve this, we can utilize a log-based stream to sequence all updates. The primary transactional database serves as the source of truth, recording updates to an append-only transaction log. A Change Data Capture (CDC) system reads this log and publishes events to a partitioned message broker like Apache Kafka. All other specialized systems (such as search indexes and caches) consume this log and update their states. Since the log forces a single, global ordering on all writes, every derived view eventually catches up in the exact same sequence, eliminating inconsistencies.

#### The Lambda Architecture and Its Critique
The Lambda Architecture was designed to combine the advantages of batch processing (DDIA/14) and stream processing (DDIA/15):
1. **The Batch Layer**: Periodically processes the entire historical dataset to compute highly accurate, immutable pre-calculated views. This layer is highly reliable but has latency of hours or days.
2. **The Speed Layer**: Processes the most recent events in real-time to compute low latency views. This layer is fast but might trade off accuracy or completeness for speed.
3. **The Serving Layer**: Queries both batch and speed views to respond to client requests, merging their results on the fly to provide a complete and up-to-date answer.

Despite its benefits, Lambda has a major drawback. Developers must implement and maintain the exact same business logic in two separate codebases (for example, MapReduce for the batch layer and Apache Storm for the speed layer). Debugging inconsistencies between the two layers is notoriously difficult.

#### Unifying Batch and Stream: The Kappa Architecture
The Kappa Architecture addresses this duplication by running a single stream processing engine (like Apache Flink or Spark Structured Streaming) over both real-time streams and historical logs. In this model, historical data is stored in a durable, replayable log-based message broker with long-term retention. To recalculate aggregates or deploy a new feature, a developer starts a new version of the stream consumer from offset zero, letting it sequentially process the historical log. Once the new consumer catches up to the live stream head, the system switches client traffic to the new materialized view and decommissions the old one, avoiding double codebase maintenance.

**Comparison of Architectural Topologies**

*Lambda Architecture Dataflow*:
```
                       ┌───► [ Speed Layer (Real-Time) ] ───► [ Real-Time Views ] ──┐
                       │                                                            ├──► [ Serving Layer ]
[ Immutable Raw Data ]─┤                                                            │
                       │                                                            │
                       └───► [ Batch Layer (Cold Path) ]  ───► [ Batch Views ] ─────┘
```

*Kappa Architecture Dataflow*:
```
[ Durable Event Log ] ───► [ Stream Processing Engine ] ───► [ Materialized Views ] ───► [ Query Path ]
```

### Unbundling the Database (Turning the Database Inside Out)
A traditional database wraps multiple components into a single, tightly-coupled system: a transaction log for durability, index structures (like B-trees) for rapid queries, cache layers for speed, and lock managers for concurrency. Unbundling means taking these internal mechanisms apart and running them as independent services across a distributed network.

We can view our entire system architecture as a single, giant, distributed database:
* The log-based message broker acts as the primary append-only write-ahead log.
* The relational databases, search indexes, and Redis caches act as different materialized views of that log, optimized for specific query patterns.
* The stream processors act as the query execution and index maintenance engine, transforming and routing data from the log to the views.

This perspective is often described as turning the database inside out. By making the log the central point of coordination, we can design applications around dataflow. Instead of services querying each other synchronously via RPC (which creates tight coupling and cascading failures), services communicate asynchronously by consuming and producing to the shared log backbone.

This dataflow-driven approach transforms how we think about system integration. By replacing synchronous request-response API calls with asynchronous stream consumption, we eliminate cascading failures and performance degradation. If a downstream search index goes offline, the rest of the application remains fully operational. The search index can simply catch up on its updates from the log once it recovers, ensuring sturdiness and reliability.

*Unbundled Database Architecture*:
```
   [ Application Client ]
             │
             │ (1) Write / HTTP POST
             ▼
   ┌──────────────────┐
   │ Primary Database │ (PostgreSQL)
   └─────────┬────────┘
             │ (2) Writes committed to WAL
             ▼
   ┌──────────────────┐
   │   CDC Connector  │ (Debezium)
   └─────────┬────────┘
             │ (3) Publishes change events sequentially
             ▼
   ┌──────────────────┐
   │ Log-Based Broker │ (Apache Kafka - Partitioned, Durable Log)
   └────┬──────────┬──┘
        │          │
        │ (4a)     │ (4b) Consumers update state asynchronously
        ▼          ▼
   ┌──────────┐ ┌──────────────────┐
   │  Cache   │ │   Search Index   │ (Elasticsearch)
   │ (Redis)  │ │ (Materialized)   │
   └──────────┘ └──────────────────┘
```

#### Read Path vs. Write Path and Materialized Views
Unbundling the database shifts our understanding of the read path and write path. When a system receives an update, it can either do the work immediately on write, or defer it until someone asks on read:
- **The Read Path**: Under a standard database query, you scan indexes and calculate aggregates at query time. This keeps writes cheap but makes reads expensive and slow for complex queries.
- **The Write Path**: Under a materialized view, you pre-calculate the query result on the write path whenever a change event is received. When a client requests the data, the system simply returns the pre-aggregated view with minimal latency.

Unbundled architectures optimize the read path by moving as much computation as possible to the write path. This model is especially helpful for offline-capable applications, where local devices maintain their own local materialized views of the log and sync updates asynchronously when network connections return.

This approach of moving computation to the write path has profound benefits for client applications. In a collaborative editor or a mobile app, local devices can store state in SQLite databases that are structured exactly like the views they render. When the user modifies data offline, the local database is updated instantly. These changes are saved as local events. Once connectivity is restored, the device uploads these events to the unbundled server log, which merges them, runs validations, and propagates the corrected state back to all other participants.

### Aiming for Correctness and Reliability
In distributed systems, failures are a constant reality. While database-level transactions (DDIA/11) offer safety guarantees within a single datastore, they cannot ensure correctness across an entire unbundled application.

#### The End-to-End Argument
The end-to-end argument states that some guarantees can only be enforced correctly with the help of the application at its endpoints. If a client attempts to execute a bank transfer, a transaction inside the database cannot prevent duplicate execution if the network fails after the database commits but before the client receives the success response. The client will naturally retry the request. To handle this correctly, the application must enforce end-to-end idempotence. By associating each transaction with a client-generated unique transaction ID, the receiving service can detect and ignore duplicate retries, ensuring that the operation runs exactly once.

#### Enforcing Uniqueness and Coordination-Avoidance
Traditional databases enforce unique constraints (like ensuring no two users register the same email) by acquiring a lock, which requires expensive distributed consensus (DDIA/13). In an unbundled, log-based system, we can enforce uniqueness without a central locking coordinator by using a single-partition log.

Because a single log partition sequences all incoming creation requests sequentially, we can avoid distributed locking. A stream consumer reads this partition sequentially. It keeps a local index of all registered usernames. If it processes a username creation event and finds the username is not in its index, it registers the user. In the event that the username is already registered, the consumer rejects the update. This approach (coordination-avoidance) enables massive write throughput by removing synchronous locking bottlenecks from the write path.

#### Timeliness vs. Integrity
We must distinguish between two different aspects of correctness in unbundled architectures:
* **Timeliness**: How quickly updates are propagated to derived views. Lagging derived views violate timeliness but do not violate safety.
* **Integrity**: The absolute prevention of state corruption or inconsistent data (such as money disappearing from a bank account).

In unbundled dataflows, timeliness is eventually consistent. A search index might be a few seconds behind the primary database, but this lag is usually acceptable to users. Integrity, however, must be maintained absolutely. By using immutable logs and idempotent consumers, we can guarantee integrity even when timeliness is delayed by network lag or consumer crashes.

### Tying It Together: Batch, Stream, and Consensus
This final synthesis allows us to tie together the three major pillars of modern distributed data systems:
1. **Consistency and Consensus (DDIA/13)**: Consensus protocols provide strong guarantees (like serializable transactions) but require high coordination overhead. This coordination creates a major performance bottleneck under high write volume.
2. **Batch Processing (DDIA/14)**: Batch systems (like MapReduce) offer massive throughput and high correctness for historical data. However, they sacrifice real-time timeliness, acting as slow-moving offline engines.
3. **Stream Processing (DDIA/15)**: Stream processors (like Flink) provide sub-second timeliness on unbounded data but must manage state and late-arriving events with watermarks and checkpointing.

By unbundling the database, we can integrate these pillars. Instead of running synchronous distributed transactions (which rely on locking and consensus), we can use a partitioned, log-based broker (like Kafka) as our transaction sequencer. This broker acts as a coordination-free consensus engine. It sequences all updates in a fixed order, ensuring that downstream systems process writes consistently.

Downstream systems then use both stream and batch processing to process this log. The stream processor maintains low latency, real-time views (the speed path) for immediate needs. Meanwhile, the batch system runs periodically over the raw logs (the batch path) to audit the system, find inconsistencies, and correct derived datastores. This elegant division of labor allows us to achieve high write throughput, low read latency, eventual consistency, and absolute integrity, all without the high cost of synchronous, distributed consensus.

### Trust but Verify: Auditing and Data Integrity
Even with elegant protocols, software bugs or hardware deterioration can corrupt data silent-style over time. True correctness requires auditing. We should periodically run batch jobs (such as Hadoop or Spark jobs) that compare the raw, immutable event log with the current state of our databases and search indexes. If a discrepancy is found, we can use the event log as the source of truth to automatically repair the corrupt views. This auditing practice provides a critical safety valve, ensuring that eventual consistency does not become permanent inconsistency.

To make auditing even more robust, we can use cryptographic techniques like hash-chaining or Merkle trees. By appending a hash of the previous log record to each new event, the log becomes tamper-evident. If an attacker or a disk failure attempts to alter an old event, the hashes will no longer match, which immediately alerts the auditing system. This cryptographic auditability ensures that the event log remains a trustworthy, permanent record of historical facts, establishing a foundation of absolute data integrity across all unbundled systems.

### Ethics and the Hazards of Data Collection
Building data-intensive systems is not purely a technical challenge. It carries profound social responsibilities. As engineers, we must recognize that data is a hazard, not just an asset. Storing massive, immutable logs of user behaviors can lead to systemic violations of privacy, surveillance abuses, and algorithmic bias. For instance, predictive analytics models trained on historical data often reinforce human biases, creating automated feedback loops that discriminate against marginalized groups. Data systems should be designed from the ground up with strict retention limits, pseudonymization, active consent mechanisms, and clear audit trails to protect individuals from automated harm.

Self-reinforcing feedback loops occur when predictive algorithms make automated decisions based on historical data, and those very decisions generate new data that confirms the algorithm's bias. For example, if a predictive policing algorithm disproportionately routes officers to a specific neighborhood based on historical arrest records, the officers will make more arrests in that neighborhood, which then feed back into the algorithm to justify routing even more officers there. To break these loops, we must practice data minimization. Storing only the bare minimum of user data required for a specific task, deleting logs as soon as they are processed, and actively monitoring algorithms for systemic drift are critical engineering responsibilities.

### Worked Examples with Numbers

Let's examine three detailed scenarios that demonstrate how unbundled database concepts work in practice.

#### Example 1: Coordination-Free Uniqueness Enforcement
Suppose we are building a registration service where usernames must be unique. Instead of using a distributed lock, we use a single-partition Kafka topic named `username-registrations` to sequence all requests.

Let's trace how concurrent registration requests for the username "alice" are resolved:
1. At processing time `12:00:01`, User A submits a registration request for "alice". This request lands on the Kafka partition at offset `1200`.
2. At processing time `12:00:02`, User B submits an identical registration request for "alice". This request lands on the same Kafka partition at offset `1201`.
3. The username consumer reads the log sequentially. It maintains an internal, in-memory hash set of registered usernames, which currently does not contain "alice".
4. When the consumer processes offset `1200`, it checks its hash set. Since "alice" is free, it adds "alice" to its local state and writes a success record `(User_A, "alice")` to its materialized registration database.
5. When the consumer processes offset `1201`, it checks its hash set again. Because offset `1200` was already processed, the consumer finds that "alice" is already registered. It immediately rejects User B's request and writes a failure record `(User_B, "alice", REJECTED)` to the database.

Both requests were evaluated without any distributed locking or database coordination on the write path. This coordination-free mechanism scales writes extremely well because the single Kafka partition enforces the global ordering of the requests.

#### Example 2: Read Path vs. Write Path Optimization
Let's look at an analytical dashboard for an e-commerce platform that must display total revenue. We receive 10,000 purchase events per day, and the dashboard is queried 1,000 times per second.

Let's compare the computational costs under two designs:

**Design A: Query-Time Aggregation (Read-Path Optimization)**
* **On write**: Each incoming purchase event is simply inserted as a row into a database. Write cost is negligible.
* **On read**: Every dashboard query executes: `SELECT SUM(amount) FROM purchases`. To answer this, the database must scan all 10,000 rows.
* **Total Cost**:
  - Daily write cost: 10,000 inserts.
  - Daily read cost: `1,000 queries/sec * 86,400 seconds/day * 10,000 rows scanned = 864,000,000,000 rows scanned`.
  - This design places a massive load on the database read path, resulting in slow query responses and high hardware costs as the dataset grows.

**Design B: Materialized Aggregation (Write-Path Optimization)**
* **On write**: When a purchase event occurs, a stream processor consumes the event and immediately updates a single row in a `daily_revenue` table: `UPDATE daily_revenue SET total = total + event.amount WHERE date = event.date`.
* **On read**: Every dashboard query executes: `SELECT total FROM daily_revenue WHERE date = current_date`. This is a single, O(1) index lookup.
* **Total Cost**:
  - Daily write cost: 10,000 updates to a single row.
  - Daily read cost: `1,000 queries/sec * 86,400 seconds/day * 1 row scanned = 86,400,000 rows scanned`.
  - This design reduces the daily computational burden by a factor of 10,000. Shifting the work from the read path to the write path enables sub-millisecond query responses and prevents database overloading.

#### Example 3: End-to-End Idempotence with Client-Side Request IDs
Suppose a client wants to transfer $100 from Account X to Account Y. Let's trace how end-to-end idempotence protects against duplicate transfers in a network failure scenario.

**The Scenario**:
1. The client generates a unique Request ID `req_888_999` and makes an HTTP POST request: `/transfer?id=req_888_999&from=X&to=Y&amount=100`.
2. The server receives the request. It initiates a transaction in Postgres.
3. As part of this transaction, the server first checks if the Request ID `req_888_999` exists in a `processed_requests` table. It finds no record, meaning this is a new request.
4. The server deducts $100 from Account X, adds $100 to Account Y, and inserts a row `(req_888_999, SUCCESS, response_payload)` into the `processed_requests` table.
5. The transaction commits successfully in Postgres.
6. Before the server can send the HTTP 200 success response back to the client, a router crashes, breaking the network connection. The client sees a timeout error.
7. Following standard retry policies, the client automatically resends the identical request: `/transfer?id=req_888_999&from=X&to=Y&amount=100`.
8. The server receives the retried request and starts a new Postgres transaction.
9. This time, the server checks the `processed_requests` table and finds that `req_888_999` already has a success status.
10. Instead of executing the transfer again (which would deduct an extra $100), the server immediately returns the cached response from the table.

Even though the network failed and a retry occurred, the client was charged exactly $100. This correctness could not be achieved by database-level transactions alone. It required the cooperation of the client (generating the ID) and the application (tracking the ID), representing the classic end-to-end correctness model.

## Pros
- **Optimal Tool Selection**: Integrating specialized databases allows each index, search engine, or cache to do what it does best.
- **Improved Performance and Scaling**: Unbundling separates the read path from the write path, preventing heavy query loads from impacting writes.
- **Reliable Derived Views**: Using log-based CDC ensures that secondary stores are updated sequentially and reliably.
- **Architectural Flexibility**: Adding a new database or full-text index is simple because we can replay the log from any offset.
- **Resilience Against Slow Reads**: Heavy read queries on specialized views cannot exhaust database connection pools or degrade write transaction throughput.

## Cons
- **Substantial Operational Complexity**: Managing multiple distributed databases, CDC connectors, and log brokers requires significant team overhead.
- **Eventually Consistent Lag**: Derived views are inherently slightly behind the primary log, meaning application reads must tolerate eventual consistency.
- **Lack of Distributed Transactions**: Coordinating atomic transactions across different, unbundled datastores is hard and requires costly coordination.
- **Logic Duplication in Lambda**: The Lambda Architecture requires maintaining identical processing logic in two separate codebases.
- **Loss of Ad-hoc Query Capabilities**: Log-based systems make it harder to run spontaneous, arbitrary queries on raw logs without first constructing a materialized view.

## Alternatives
- **Single Monolithic Relational Database**: Uses a single SQL database (like Postgres) to handle transactions, full-text search, and reporting. It differs by keeping all data in one place with immediate consistency. Choose this option for standard, low-to-medium traffic applications to avoid operational complexity.
- **Dual-Writing Application Code**: Writes updates directly to multiple datastores inside the application code. It differs by failing to guarantee ordering or failure recovery. Choose this method only for simple, non-critical systems where eventual consistency lag and occasional mismatches are acceptable.
- **Distributed Two-Phase Commit (2PC)**: Coordinates atomic transactions across separate systems. It differs by creating a severe performance bottleneck and a single point of failure. Choose this approach only when strict transaction guarantees are required across heterogeneous databases and throughput is not a concern.

## When to use it
Reach for unbundled, log-based architectures when:
* Your application runs at a massive scale where read performance and write throughput must be scaled independently.
* You have highly diverse query patterns that cannot be served efficiently by any single database (such as needing transactional SQL, full-text search, and graph traversal simultaneously).
* Downstream data pipelines, caches, and analytical warehouses must stay in sync with primary transactional databases in near-real-time.

## When NOT to use it
Avoid unbundling and integrated stream setups when:
* Your entire application can be easily served by a single SQL database. Reach for a standard Postgres or MySQL database with synchronous API calls to minimize infrastructure cost and development effort.
* Strict, immediate, and globally consistent reads are required across all views of the application state. Reach for a single database with standard ACID transaction isolations instead.
* Your development team is small and lacks the operational expertise to monitor and maintain Kafka clusters, CDC connectors, and multiple database systems. Reach for a managed, single-database cloud solution instead.

## Key takeaways / mental model
Think of an unbundled database as a high-end mechanical watch that has been disassembled on a workspace table, with its gears and springs connected by elastic bands. Instead of a single, closed watch face (the monolithic database) hiding all its parts, you can see and scale each component (the write-ahead log, the indexes, the query engine) on its own. The elastic bands (the change streams) ensure that when one gear rotates, the others spin in response, keeping the entire mechanism in perfect sync.

## Self-check questions
1. What does it mean to "turn the database inside out," and how does unbundling differ from a monolithic database architecture?
2. Compare the Lambda and Kappa architectures. Why does Kappa simplify code maintenance for developers?
3. What is the dual-write problem? Why is dual-writing directly from application code a dangerous anti-pattern?
4. Explain how the end-to-end argument applies to enforcing idempotence in bank transfers. Why are database-level transactions alone insufficient?
5. How can a single-partition event log enforce unique username registration without acquiring a distributed database lock?
6. Imagine a system where timeliness of derived cache views is low (lag is 10 seconds), but integrity is high. Is this system acceptable for an e-commerce stock dashboard? Why or why not?
7. Discuss the ethical hazards of automated predictive analytics models trained on historical user logs. How can a software engineer mitigate the risk of algorithmic feedback loops?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 12
- Out of the Tar Pit (Ben Moseley and Peter Marks)
- End-to-End Arguments in System Design (J.H. Saltzer, D.P. Reed, and D.D. Clark)
- The Log: What every software engineer should know about real-time data's unifying abstraction (Jay Kreps)
