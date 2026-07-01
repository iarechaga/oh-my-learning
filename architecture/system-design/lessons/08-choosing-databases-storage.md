---
id: system-design/08
subject: system-design
title: "Choosing Databases and Storage"
slug: choosing-databases-storage
status: drafted
mastery:
seniority: mid
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 5"
prerequisites: [ddia/02, ddia/05]
created: 2026-06-30
updated: 2026-06-30
---

# Choosing Databases and Storage

## TL;DR
Selecting the right storage technology is a fundamental decision that determines a system's scalability, consistency, and maintenance overhead. Different database engines make distinct architectural trade-offs between schema rigidity, read-write speeds, and query performance. Understanding these characteristics allows developers to implement polyglot persistence, aligning specific workloads with relational databases, NoSQL stores, object storage, or data warehouses.

## The idea
There is no single database that can handle all application workloads efficiently. Historically, systems relied on relational databases as a general-purpose solution for all storage needs. However, the rise of web-scale applications and high-throughput data processing exposed the limitations of this one-size-fits-all approach.

A database's design dictates how it lays out data on disk, schedules locks, and handles replication. These low-level details shape the engine's real-world characteristics. Trying to run low-latency lookups, high-volume sensor writes, and complex multi-hop graph traversals on a single relational engine inevitably creates performance bottlenecks.

To build reliable, scalable architectures, we must analyze our data's access patterns and pick specialized stores. This philosophy, known as polyglot persistence, means using multiple database technologies in a single system. Each workload uses the specific storage model that fits its query patterns, schemas, and consistency needs perfectly.

## How it works

### The Storage Landscape: SQL vs. NoSQL Families
Modern system design organizes storage solutions into several primary families, each optimized for specific data shapes and operations:

* **Relational (SQL)**: Built on Edgar Codd's relational model (DDIA concept 02). Data is stored in strict, flat tables. Relations are resolved dynamically via joins, and consistency is protected by ACID transactions. PostgreSQL and MySQL are standard choices.
* **Key-Value NoSQL**: Highly simplified engines that store and retrieve raw values (JSON, binary, strings) via unique keys. They operate in memory or use fast local indexes, providing single-digit millisecond latency. Redis and DynamoDB are prominent examples.
* **Document NoSQL**: Hierarchical, semi-structured JSON documents stored sequentially on disk. This offers great read locality because nested records are loaded in a single disk read, bypassing joins. MongoDB is a popular document database.
* **Wide-Column (Column-Family) NoSQL**: Derived from Google's Bigtable. Instead of flat rows, data is organized into dynamic, sparsely populated column families. They use Log-Structured Merge-trees (LSM-trees) for high-throughput write workloads and massive horizontal scale. Apache Cassandra is a prime example.
* **Graph NoSQL**: Treats nodes and relationships as first-class citizens. Using index-free adjacency, nodes store direct memory pointers to neighboring nodes, enabling rapid multi-hop traversal without joins. Neo4j is a standard selection.

### Relational Databases (SQL): The Standard for Transactions
Relational databases remain the gold standard for applications requiring strict transactional integrity. They organize data into rows and columns, enforcing a rigid schema before any data can be written (schema-on-write).

Under the hood, relational engines use B-Trees or B+ Trees to manage indexes. A B+ Tree organizes keys in a balanced search tree, allowing logarithmic time complexity for reads, inserts, and deletions. However, maintaining these indexes under heavy write loads causes significant random I/O overhead. This is because the engine must modify multiple pages on disk, leading to write amplification.

To achieve high read-write concurrency, relational engines implement Multi-Version Concurrency Control (MVCC). Instead of locking rows during updates, the database stores multiple versions of a record. Readers access a consistent snapshot of the data based on when their query started, while writers modify new versions. This design prevents reads from blocking writes and vice versa, which is how engines like PostgreSQL and MySQL InnoDB implement Repeatable Read and Read Committed isolation levels (referencing DDIA Chapter 7).

Scaling relational databases horizontally is notoriously difficult. While read traffic can be distributed across read replicas, write traffic must go to a single primary leader to maintain ACID transaction guarantees. Sharding across multiple database instances is possible, but it requires the application to handle complex routing and makes cross-shard joins and distributed transactions (like Two-Phase Commit) slow and brittle.

To enforce data consistency, relational databases implement different transaction isolation levels:
- **Read Uncommitted**: The lowest isolation level. It allows dirty reads where a transaction can read uncommitted changes from other transactions.
- **Read Committed**: Prevents dirty reads. It guarantees that a query only reads data that was committed before the query began.
- **Repeatable Read**: Prevents dirty reads and non-repeatable reads. If a transaction reads a row twice, it gets the exact same data both times.
- **Serializable**: The highest isolation level. It executes transactions as if they were running in a strict, single-threaded serial order, preventing phantom reads but significantly degrading write concurrency.

Relational databases traditionally utilize active-passive (single-leader) replication schemes. In this architecture, all writes must target the primary node, which replicates data asynchronously or synchronously to passive read replicas. If the primary node crashes, a failover process elects a new leader. This transition can cause brief write outages and risks data loss if replication was asynchronous, illustrating the classic CAP theorem trade-off between Consistency and Availability.

### Key-Value Stores: High-Speed Memory
Key-value stores represent the simplest data model. They map a unique key to an unstructured value, such as a string, a serialized object, or a binary blob.

To achieve sub-millisecond latencies, key-value stores like Redis hold their entire dataset in RAM. This makes them highly vulnerable to data loss if a power outage occurs. To mitigate this, they implement persistence models:

1. **RDB (Redis Database Snapshots)**: The engine takes point-in-time snapshots of the dataset and writes them to disk at regular intervals. This is fast, but any writes made between snapshots are lost during a crash.
2. **AOF (Append Only File)**: The engine logs every write operation sequentially to a file. While this provides higher durability, it increases write latency and disk space usage.

Because RAM is expensive and limited, key-value stores employ cache eviction policies like Least Recently Used (LRU) or Least Frequently Used (LFU). They also support time-to-live (TTL) configurations to automatically purge expired records.

Redis goes beyond simple strings by supporting native data structures:
- **Hashes**: Perfect for storing user profiles and session objects.
- **Lists**: Used for building simple message queues with push and pop operations.
- **Sets**: Helpful for storing unique tags or tracking online users.
- **Sorted Sets**: Maintained in sorted order using skip lists, making them excellent for leaderboard systems.

### Document Databases: Hierarchical Simplicity
Document databases are designed to store semi-structured data as self-contained JSON or BSON (Binary JSON) documents. This layout matches application-level objects perfectly, eliminating the object-relational impedance mismatch. If a user profile contains multiple phone numbers and addresses, they are nested directly inside the user document.

* **Read Locality**: Loading a user profile requires a single sequential read from disk. The engine does not need to perform multiple index lookups across join tables, providing exceptional read performance.
* **Write Amplification Cost**: If you want to update a single nested field (like changing a zip code), the database must rewrite the entire document to disk. Furthermore, large documents consume significant memory and network bandwidth during serialization and parsing.

Early document stores suffered from disk fragmentation during document growth. When an update made a document larger than its pre-allocated sector, the engine was forced to move the entire document to a new physical coordinate on disk. This relocation triggered cascade updates to every index pointing to that document, creating severe write latency spikes. Modern engines use storage layers like WiredTiger in MongoDB, which allocate space dynamically and compress data to minimize relocation costs.

To speed up queries, document databases support indexing on nested fields and array values (multikey indexes). They also feature specialized indexes, such as geospatial indexes, to locate coordinates within a specific radius. Replication is managed through replica sets with automatic leader elections based on consensus voting, providing a resilient, high-availability architecture.

### Wide-Column (Column-Family) Stores: Log-Structured Append
Wide-column databases, such as Apache Cassandra or HBase, are designed for massive horizontal scaling and high-throughput write workloads.

Instead of writing data randomly to B-Trees, wide-column engines use Log-Structured Merge-trees (LSM-trees). The write path is highly optimized:
1. An incoming write is appended sequentially to a Write-Ahead Log (WAL) on disk for durability.
2. The record is written to an in-memory sorted buffer called a Memtable.
3. Once the Memtable fills up, the engine flushes its sorted contents to disk as an immutable Sorted String Table (SSTable) file.

Because SSTables are immutable, the engine avoids random disk overwrites. This design means writes are incredibly fast and never block reads. Over time, many SSTable files accumulate on disk. To clean up duplicate keys and reclaim space, a background process called **compaction** continuously merges and re-sorts SSTables. During compaction, the engine discards deleted records, which are marked with special markers called **tombstones**.

To prevent the engine from performing expensive disk lookups across multiple SSTables for non-existent keys, wide-column databases maintain **Bloom Filters** in memory. A Bloom Filter is a fast, probabilistic data structure that can tell the engine instantly if a key is definitely not present in an SSTable, preventing useless disk reads.

In terms of replication, Cassandra uses a masterless (leaderless) distributed architecture based on DynamoDB's design. There is no single point of failure; any node can accept read or write requests. It provides tunable consistency, allowing developers to configure the number of nodes that must acknowledge a read ($R$) or a write ($W$) compared to the total replication factor ($N$). By setting $R + W > N$ (such as quorum reads and writes), the system guarantees that reads always return the latest written value, supporting strong consistency over eventual consistency on demand.

### Graph Databases: Navigating Relationships
When data is highly interconnected and relationships are as important as the entities themselves, graph databases are the best choice.

Traditional relational databases use foreign keys and join tables to link records. Querying these relationships requires performing index lookups for every join hop. As the depth of the traversal increases, performance degrades exponentially.

Graph databases like Neo4j solve this by implementing **index-free adjacency**. Each node physically stores memory pointers that point directly to its neighboring nodes. Traversing a relationship is a simple pointer-dereferencing operation, running in constant O(1) time per hop. This allows the engine to traverse millions of relationships per second, regardless of the overall size of the database.

Deploying graph databases in a distributed cluster introduces the highly complex **graph partitioning problem**. Because edges can easily cut across machine boundaries, traversing a relationship can turn a local memory access into a slow RPC network request. Consequently, most production graph databases are run on a single massive machine or use read-only replication sets, making horizontal scaling a significant technical hurdle.

### Object and Blob Storage: Flat Scale
For large, unstructured media assets like images, videos, audio, and backups, database engines are a poor choice. Storing big binary assets inside a relational table bloats the B-trees, degrading search performance and increasing storage costs.

Object storage systems (like Amazon S3, Google Cloud Storage, or MinIO) are designed to store flat, unstructured data blocks at massive scale. Objects are immutable and retrieved via HTTP-based key lookups. This separates expensive file delivery from your application database.

Historically, object storage systems used an eventual consistency model for updates and deletes. If you overwritten or deleted an object, subsequent reads could still return the old version of the file. In late 2020, Amazon S3 transitioned to a strong read-after-write consistency model for all PUT and DELETE operations. This update guarantees that once a write succeeds, any subsequent read will immediately reflect the change.

To manage storage budgets, object stores implement lifecycle policies. These policies automatically transition objects across distinct storage tiers:
- **Standard Tier**: High-availability, low-latency access for active data.
- **Warm Tier (Infrequent Access)**: Cheaper storage cost, but incurs a retrieval fee per gigabyte. Ideal for monthly backups or receipts.
- **Cold Tier (Archive/Glacier)**: Extremely cheap storage. Retrievals can take several hours, making it perfect for long-term compliance logs.

### Data Warehouses and Analytics (OLAP vs. OLTP)
Understanding the difference between Online Transactional Processing (OLTP) and Online Analytical Processing (OLAP) is critical when choosing an analytical database (DDIA concept 05):

* **OLTP (Row-Oriented)**: Designed to support user-facing applications. They handle high-volume, low-latency reads and writes of individual records (e.g. creating an order, updating a profile). These engines use row-oriented storage layouts to make individual row mutations incredibly fast.
* **OLAP (Column-Oriented)**: Designed to support data analysis, business intelligence, and reporting. They query millions of rows but only access a few columns (e.g. calculating total revenue per month). Data warehouses use column-oriented storage, grouping values of a single column together on disk. This layout minimizes disk reads, allows high compression, and accelerates aggregations. Examples include Snowflake, Google BigQuery, and Amazon Redshift.

Let us visualize how these two layouts store identical tabular data on disk blocks:

```
Tabular Data:
Row 1: [ID: 101, Name: "Alice", Sales: 150]
Row 2: [ID: 102, Name: "Bob",   Sales: 200]

Row-Oriented Layout (OLTP):
| Sector 1: 101, "Alice", 150 | Sector 2: 102, "Bob", 200 |

Column-Oriented Layout (OLAP):
| Sector 1 (IDs): 101, 102 | Sector 2 (Names): "Alice", "Bob" | Sector 3 (Sales): 150, 200 |
```

Because column-oriented systems store homogeneous data types sequentially, they achieve exceptional compression ratios. They compress columns using algorithms like Run-Length Encoding (RLE) or dictionary encoding, allowing the system to run aggregate queries utilizing fast, hardware-level SIMD (Single Instruction, Multiple Data) processing.

Additionally, data warehouses avoid traditional B-Trees, which are designed for row lookups. Instead, they use specialized indexing schemes:
- **Projection Indexes**: Pre-sorted projections of columns to accelerate specific sort and filter actions.
- **Bitmap Indexes**: Space-efficient bit arrays mapped to unique column values. They are incredibly powerful for low-cardinality columns like country or status, enabling the execution engine to perform rapid filters using hardware-level bitwise operations.

### Decision Table: Database Families and Best-Fit Workloads

| Store Family | Underlying Storage Structure | Scaling Model | Consistency Model | Ideal Workload | Examples |
| --- | --- | --- | --- | --- | --- |
| Relational (SQL) | Row-oriented B-Tree | Vertical scaling (Sharding required for cluster scale) | Immediate Consistency (ACID) | Financial transactions, order management, rigid relational schemas | PostgreSQL, MySQL |
| Key-Value NoSQL | Hash tables, LSM-Trees | Horizontal partitioning | Eventual or Immediate Consistency | Caching, session states, volatile shopping carts, leaderboards | Redis, Memcached |
| Document NoSQL | Hierarchical B-Tree | Horizontal partitioning | Eventual or Immediate Consistency | Content management, user profiles, flexible catalog schemas | MongoDB, Couchbase |
| Wide-Column NoSQL | Column-Family LSM-Tree | Masterless horizontal clustering | Eventual Consistency (Tunable quorum) | High-volume IoT sensor writes, log ingestion, timeline feeds | Apache Cassandra, HBase |
| Graph NoSQL | Index-free adjacency | Single-node (Complex to partition across clusters) | ACID transactions within node boundaries | Social graphs, recommendation engines, fraud detection networks | Neo4j |
| Columnar OLAP | Column-oriented blocks | Distributed MPP (Massive Parallel Processing) | Eventual Consistency | Large-scale reporting, analytics, aggregate queries | Snowflake, BigQuery |

### Worked Examples

#### Example 1: Selecting Storage for an E-Commerce Shopping Cart
A shopping cart requires extremely low latency, high write availability, and a flexible schema since items can have diverse attributes.

Let us explore the storage candidates:
1. **Relational Database**: A SQL database would require joining a `cart` table with a `cart_items` table. Every cart update forces writes across tables and index adjustments. While schema enforcement and ACID transactions are nice, the rigidity is overkill, and scaling under a massive holiday traffic spike is difficult.
2. **Key-Value Store (Redis)**: Redis is an excellent choice. By using the user ID as the key (e.g. `cart:user_773`), we can store the cart contents as a serialized JSON blob or use a Redis Hash structure. Since Redis operates in memory, cart reads and updates take less than a millisecond. To prevent stale carts from consuming RAM forever, we can set a time-to-live (TTL) of 14 days on the key.
3. **Document Database (DynamoDB)**: DynamoDB is another phenomenal fit. It offers high write throughput, predictable single-digit millisecond latency, and automatic partitioning.

An exact document representation for a cart in MongoDB or DynamoDB might look like this:
```json
{
  "_id": "cart_user_992",
  "userId": "user_992",
  "updatedAt": "2026-06-30T10:00:00Z",
  "items": [
    {
      "productId": "prod_118",
      "quantity": 2,
      "price": 49.99,
      "name": "Mechanical Keyboard"
    },
    {
      "productId": "prod_224",
      "quantity": 1,
      "price": 19.99,
      "name": "Ergonomic Mouse"
    }
  ]
}
```

*Decision*: For volatile, active carts, pick Redis for raw speed. For persistent carts that must survive cache evictions and scale horizontally without RAM limits, pick Amazon DynamoDB or MongoDB.

#### Example 2: Selecting Storage for a Social Network Graph
A social network needs to track millions of users and their relationships (friends, followers, blocks). A core query is: "Find mutual friends between User A and User B," or "Recommend friends-of-friends."

Let us explore the storage candidates:
1. **Relational Database**: In a relational model, relationships are stored in a many-to-many join table `friendships(user_id, friend_id)`. Finding friends-of-friends requires joining this table with itself. When traversing three or four degrees of separation, the query requires multiple recursive joins, causing the database to perform extensive index lookups and thrash the CPU.
2. **Graph Database (Neo4j)**: Neo4j is designed specifically for this. It uses index-free adjacency. When we query a node, the engine immediately reads the direct pointers to neighboring nodes. Traversal operations run in time proportional to the size of the subgraph being searched, not the total size of the database.

Using Cypher, Neo4j's query language, finding mutual friends between Alice and Bob is incredibly simple:
```cypher
MATCH (alice:User {name: "Alice"})-[:FRIEND]-(mutual)-[:FRIEND]-(bob:User {name: "Bob"})
RETURN mutual.name
```
The database engine executes this by locating the Alice node via index, then traversing direct memory pointers to friends, checking if Bob is at the end of any shared pointers. This avoids costly tables-scans and index intersections.

*Decision*: Pick a graph database like Neo4j to store and query the highly interconnected network structure, while storing basic user profile information in a document or relational database.

#### Example 3: Selecting Storage for an Analytics and Reporting System
An enterprise wants to generate monthly reports on user activity, calculating metrics like average order value, daily active users, and total sales across millions of rows.

Let us explore the storage candidates:
1. **Relational OLTP (PostgreSQL)**: PostgreSQL stores data in rows. To calculate total sales, the engine must load every single row of the transaction table into memory, parse the row, extract the `amount` column, and sum them. This performs massive, wasted disk reads of columns (like user IDs, product IDs, addresses, and shipping details) that are completely irrelevant to the aggregation, leading to high disk I/O bottlenecks.
2. **Column-Oriented Data Warehouse (Snowflake)**: Columnar warehouses group data by column. On disk, all values for the `amount` column are stored sequentially. To run the sum aggregation, the engine only reads the blocks for the `amount` column from disk. The read operation is extremely fast and can be heavily optimized because sequential column values of the same data type compress beautifully (connecting back to DDIA concept 05).

Consider a simple analytical SQL query:
```sql
SELECT EXTRACT(MONTH FROM created_at) as sales_month, SUM(amount)
FROM transactions
GROUP BY sales_month
```
On a row-oriented relational engine with 10 million transactions (averaging 500 bytes per row), the database must read approximately 5 gigabytes of raw data from disk. On a column-oriented system, where each column is stored sequentially and compressed, the engine only reads the `created_at` (8 bytes) and `amount` (8 bytes) columns. After compression, the total read volume is reduced to less than 100 megabytes, cutting disk I/O by over 98%.

*Decision*: Pick a columnar data warehouse like Snowflake or Google BigQuery. Extract, transform, and load (ETL) transactional data from your production OLTP relational database into the data warehouse on a regular schedule to run analytical queries without impacting the user-facing application.

## Pros
- **Maximized query performance**: Aligning storage engines with query shapes ensures low-latency reads and writes.
- **Enhanced data durability and safety**: Using ACID-compliant relational databases for transactional data minimizes corruption and inconsistency.
- **Seamless horizontal scaling**: Selecting NoSQL stores (like Cassandra or DynamoDB) allows systems to scale writes and storage capacity across clusters of commodity hardware.
- **Optimized storage costs**: Moving large media assets to object storage and analytical datasets to compressed columnar warehouses keeps expensive database storage lightweight.

## Cons
- **Increased operational complexity**: Managing multiple database families in a single architecture multiplies maintenance, backup, and monitoring overhead.
- **Complex data synchronization**: Polyglot persistence requires building ETL or change data capture (CDC) pipelines to synchronize data across stores, introducing latency.
- **Loss of global transactional integrity**: Distributing data across NoSQL and SQL databases makes cross-system transactions extremely difficult, forcing reliance on eventual consistency.
- **Fragmented developer expertise**: Engineering teams must learn and maintain deep knowledge of distinct query languages, storage engine details, and tuning parameters for multiple platforms.

## Alternatives
- **Universal Relational Engine with Multi-Model Support**: Using PostgreSQL with JSONB columns (for document storage), TimescaleDB extension (for time-series data), and pgvector (for vector search). This keeps the infrastructure simple and consolidated under one engine but can hit scaling bottlenecks under massive volume.
- **NewSQL Distributed Databases**: Systems like Spanner, CockroachDB, or TiDB that offer horizontal scalability of NoSQL databases while maintaining full ACID transactional support and SQL interfaces. This simplifies scaling but comes with higher infrastructure costs and operational maturity requirements.
- **Single massive document database**: Using MongoDB or DynamoDB for the entire system, emulating transactions and relations in application-layer code. This reduces infrastructure complexity but results in slow, complex join logic and poor analytical query performance.

## When to use it
- **Large-scale web architectures**: When individual features (carts, feeds, searches, graphs, audits) experience high traffic and have wildly different storage and schema needs.
- **Microservice ecosystems**: When independent services own their respective data stores, allowing teams to pick the best-fit database for their specific microservice boundary.
- **Read-heavy systems with complex analytics**: When your application must serve rapid user writes while simultaneously running heavy, long-running intelligence reports.

## When NOT to use it
- **Simple startup or MVP projects**: If your user base is small and requirements are fluid, a single relational database (like PostgreSQL) is the best choice. It handles relations, documents, and search well enough until you reach scale.
- **Strict, highly regulated financial applications**: In systems where every transaction must be tightly coordinated and consistency is legally required, distributed polyglot persistence introduces unnecessary risk. Maintain a centralized SQL database.
- **Teams with limited operations bandwidth**: If you do not have dedicated platform engineers or database administrators, managing five distinct databases will distract your developers and lead to outages.

## Key takeaways / mental model
Think of databases like tools in a master carpenter's workshop. A relational database is a high-precision chisel, perfect for fine, detailed cuts. NoSQL stores are heavy power saws and sanders, designed to cut and smooth massive amounts of wood quickly. Object storage is the lumber yard, storing raw materials until needed.

Attempting to build an entire house using only a chisel is slow and painful; trying to carve delicate joints with a power saw is disastrous. Choose the tool that matches the immediate task.

## Self-check questions
1. Contrast the storage engine design of a relational B-tree database with an LSM-tree based wide-column store. How do these differences impact write performance?
2. Under what circumstances does the read locality of a document database become a liability rather than a performance benefit?
3. Explain why storing high-resolution product images in a relational database degrades query performance, and describe the alternative storage architecture.
4. How does a column-oriented database accelerate aggregations over millions of rows, and why is this layout unsuitable for OLTP applications?
5. Imagine a system where a user places an order. Describe a polyglot persistence architecture showing which parts of this event go to which storage systems.
6. What is eventual consistency, and how does selecting a horizontally scalable NoSQL database affect your application's transaction logic?
7. Explain the differences between active-passive single-leader replication (SQL) and masterless leaderless replication (Cassandra) under a network partition.

## References
- Sinha, D. & Chopra, T. (2024). *System Design Guide for Software Professionals*, Chapter 5. Packt Publishing.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly Media.
