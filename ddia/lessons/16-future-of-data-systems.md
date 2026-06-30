---
id: ddia/16
subject: ddia
title: "The Future of Data Systems"
slug: future-of-data-systems
status: drafted
mastery:
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 12"
prerequisites: [ddia/13, ddia/15]
created: 2026-06-30
updated: 2026-06-30
---

# The Future of Data Systems

## TL;DR
This capstone chapter synthesizes the book by exploring how to integrate specialized data systems using a streaming log backbone. We can turn the database inside out by unbundling its core parts into separate, composable services connected through data streams. Correctness requires end-to-end guarantees like application-level idempotence, and we must also consider the ethical implications of data collection and automated decision-making.

## The idea
How do we build a complete, reliable, and scalable application architecture when no single tool can satisfy all our data needs? Throughout this book, we have explored individual components of data systems, ranging from low-level storage engines to replication, partition strategies, consensus protocols, and stream processors. In particular, we looked at how databases guarantee safety in [13-consistency-and-consensus.md](./13-consistency-and-consensus.md), and how event logs enable real-time processing in [15-stream-processing.md](./15-stream-processing.md).

The final chapter of Designing Data-Intensive Applications serves as a synthesis. It doesn't introduce a new isolated tool. Instead, it ties the entire book together by showing how to combine specialized systems (relational databases, caches, full-text search indexes, graph databases, and warehouses) into a unified architecture. By unbundling the traditional database and treating its internal components as independent, composable services, we can build flexible systems that keep derived state in sync.

## How it works
Modern systems require us to think about data integration, unbundled database architectures, and end-to-end correctness. Let's look at how these concepts fit together.

### Data Integration
No single database is perfect for every task. A relational database is great for transactional queries, Elasticsearch is perfect for full-text search, Redis is ideal for low latency caching, and a column-oriented data warehouse is best for analytical queries.

If we write to each of these systems directly from our application code, we face the classic dual-write problem. If the write to the database succeeds but the write to the search index fails, our data becomes permanently inconsistent.

The solution is to use a stream-based log as the backbone of our architecture. Writers send updates to a primary database that records them. An event stream or CDC system reads those changes and publishes them to a log like Apache Kafka. All other specialized systems (caches, search indexes, warehouses) consume this log and update their local state. This ensures that all derived data stays eventually consistent with the primary source of truth in a reliable, predictable order.

### Unbundling the Database (Turning the Database Inside Out)
A traditional database contains several tightly coupled components:
- A write-ahead log for durability.
- Indexing structures (like B-trees or SSTables) for fast queries.
- Cache layers for performance.
- A replication mechanism.
- A query planner and execution engine.

Unbundling the database means separating these components so they can run as independent, specialized services on different machines. We can view our entire system architecture as one giant database:
- The log-based message broker (like Kafka) acts as the write-ahead log.
- Individual databases, search engines, and caches act as different materialized views of that log, each optimizing for a specific query pattern.
- Stream processors act as the trigger and query execution engine, transforming and routing the data.

By unbundling, we can scale, deploy, and optimize each component independently.

### The Lambda Architecture
The Lambda Architecture is a popular design pattern for integrating batch and stream processing:
1. **The Batch Layer**: Reads the immutable raw data and periodically computes highly accurate, pre-calculated views (such as daily aggregates). This layer is slow but extremely reliable and correct.
2. **The Speed Layer**: Processes the most recent events in real-time to compute low latency views. This layer is fast but might trade off accuracy or completeness.
3. **The Serving Layer**: Queries both the batch and speed views to respond to user requests, merging the results to provide a complete, up-to-date picture.

#### Trade-offs of Lambda
While Lambda provides both low latency and high correctness, it has a massive drawback: developers must write and maintain the same application logic twice, once for the batch engine (like MapReduce or Spark) and once for the stream engine (like Storm or Samza).
To solve this, the **Kappa Architecture** uses a single stream processing engine (like Apache Flink) that can handle both real-time streams and historical logs. To re-run a job or recalculate aggregates, Kappa simply resets the consumer's offset and replays the historical event log from the beginning.

### Designing for Correctness and End-to-End Idempotence
In distributed systems, failures are inevitable. To ensure correctness, we cannot rely solely on database-level transactions, because they don't cover the entire path of an operation. If an application successfully inserts a row into a database but crashes before sending a success response to the client, the client will retry the request, leading to duplicate execution.

True correctness requires end-to-end guarantees. We can achieve this by making operations idempotent at the application level. Every client request should include a unique identifier (like a UUID). The receiving service stores this ID and uses it to detect and ignore duplicate retries, ensuring that the operation runs exactly once, even if network failures cause multiple retries.

### Ethics of Data
Technological capability doesn't exist in a vacuum. As engineers building massive data systems, we must recognize that the choices we make have real-world impacts. Collecting every action a user takes, storing it forever in immutable logs, and running automated machine learning algorithms over it can lead to severe privacy violations, discrimination, and algorithmic bias. Data systems should be designed with privacy-by-design principles, active consent, and transparent automated decision-making.

## Pros
- **Optimal Tooling**: Integrating specialized systems allows each database, search index, or cache to do what it does best without compromise.
- **Improved Reliability**: Unbundling separates read and write paths, preventing heavy query loads from impacting transactional write performance.
- **Consistent Derived State**: A log-based CDC architecture guarantees that secondary stores are updated in a predictable, sequential order.
- **Flexibility**: We can easily add a new type of index or database to our system by starting a new consumer from the beginning of the log.

## Cons
- **Extreme Operational Complexity**: Running multiple specialized databases alongside messaging logs and stream processors is highly demanding.
- **Eventually Consistent Views**: Derived data stores are always slightly behind the primary log, leading to potential lag that applications must tolerate.
- **Lack of Universal Transactions**: Coordinating transactions across unbundled, heterogeneous systems is nearly impossible without costly coordination.
- **Logic Duplication in Lambda**: The lambda architecture requires maintaining two separate codebases for the same business logic.

## Alternatives
- **Single Monolithic Database**: Using a single relational database (like PostgreSQL) for OLTP, full-text search (using gin indexes), and basic analytical queries. This is much simpler to operate and provides strong consistency, but it fails to scale when dataset sizes or query complexities grow extremely large.
- **Dual-Writing from Application Code**: Manually writing to both the database and the search index from the application. This avoids setting up event streams and CDC, but it leads to permanent inconsistencies when network or process failures occur during writes.
- **Distributed Transactions (2PC)**: Using a protocol like two-phase commit to write to multiple systems transactionally. This provides strong consistency across systems, but it introduces a severe performance bottleneck and creates a single point of failure.

## When to use it
Unbundled and integrated data architectures are the correct choice when:
- You have highly diverse query patterns that cannot be served efficiently by a single database (for example, needing high volume transactions, fast full-text search, and complex graph traversal simultaneously).
- Your application operates at massive scale, where write throughput and read performance must be scaled independently.
- You are building real-time data pipelines where downstream systems must stay continuously updated with minimal lag.

## When NOT to use it
Do not use this complex unbundled approach when:
- Your application can be served comfortably by a single SQL database. Postgres or MySQL can handle transactions, basic full-text search, and analytical reporting for the vast majority of applications, with much lower operational cost.
- Your team is small and cannot afford the operational overhead of managing Kafka clusters, CDC connectors, and multiple databases.
- Strong, immediate consistency across all read views is a strict requirement for your business logic.

## Key takeaways / mental model
Think of unbundling a database as taking a classic mechanical watch apart, laying its gears and springs out on a table, and connecting them with elastic bands. Instead of a single, closed metal case (the monolithic database) containing everything, you can see and scale each individual part (the log, the indexes, the query engine) on its own. The elastic bands (event streams) ensure that when one gear turns, the others rotate in response, keeping the entire system in perfect harmony.

## Self-check questions
1. What is the "dual-write" problem, and how does a log-based CDC architecture solve it?
2. What does the phrase "turning the database inside out" mean in the context of unbundling?
3. What are the primary trade-offs of the Lambda Architecture, and how does the Kappa Architecture attempt to address them?
4. Why are database-level transactions insufficient for guaranteeing end-to-end correctness in a web application?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 12
