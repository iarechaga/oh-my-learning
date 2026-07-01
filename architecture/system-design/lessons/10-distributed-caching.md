---
id: system-design/10
subject: system-design
title: Distributed Caching
slug: distributed-caching
status: drafted
mastery:
seniority: mid
source: System Design Guide for Software Professionals (Sinha & Chopra), Chapter 6
prerequisites: [ddia/01]
created: 2026-06-30
updated: 2026-06-30
---

# Distributed Caching

## TL;DR
Distributed caching improves read latencies and database performance by storing hot data in physical memory across a cluster of servers. By intercepting reads, caches offload heavy query traffic and prevent tail-latency spikes. However, caching introduces complex challenges, including cache invalidation race conditions, eviction decisions, and thundering-herd stampedes when popular keys expire.

## The idea
Relational databases and search engines store their primary data on non-volatile disks (such as SSDs or NVMe drives). While modern disk storage is fast, accessing it still requires a system call, disk controller traversal, and physical retrieval. This process introduces latency on the order of microseconds or milliseconds.

Physical random-access memory (RAM) is orders of magnitude faster, operating on the order of nanoseconds. Storing frequently accessed data in RAM allows applications to bypass disk operations and return results immediately.

```
+--------------------------------------------------------------+
| Latency Gap Comparison                                       |
|                                                              |
| L1 Cache Read:     0.5 ns                                    |
| L2 Cache Read:     7 ns                                      |
| Main Memory (RAM): 100 ns                                    |
| SSD Disk Read:     100,000 ns (100 us)                       |
| NVMe Disk Read:    10,000 ns (10 us)                         |
| Internet Roundtrip:50,000,000 ns (50 ms)                     |
+--------------------------------------------------------------+
```

In high-traffic systems, database performance is often defined by its tail latency: the 99th percentile (p99) or 99.9th percentile (p99.9) response times (DDIA Concept 01). Under high concurrent load, disk queuing and lock contention cause p99.9 response times to spike. This behavior degrades the experience for a subset of users. 

Distributed caches protect databases by serving the vast majority of read queries from RAM, keeping p99.9 tail latencies low and predictable.

## How it works

### Caching Patterns
Caching patterns determine how data is written and read from the cache and database. Each pattern represents a distinct trade-off between latency, write complexity, and data consistency:

* **Cache-Aside (Lazy Loading)**: The application code acts as an orchestrator. When a read request arrives, the application queries the cache first. If the key exists (a cache hit), it returns the data. If it doesn't (a cache miss), the application queries the database, writes the result to the cache, and then returns the response. 
  
  Writes are made directly to the database. The application then invalidates (deletes) the key from the cache to prevent stale reads. This prevents inconsistencies but can lead to a cache miss on the next read.

* **Read-Through**: The application interacts only with the cache tier. On a cache miss, the cache provider itself fetches the data from the database and updates its own storage before returning the record to the client. This pattern keeps application code clean but requires custom database integration in the caching layer.

* **Write-Through**: The application writes only to the cache tier. The cache immediately writes the same data to the database synchronously. The write transaction is successful only when both storage engines acknowledge the write. This guarantees strong consistency but increases write latency to match the speed of the database.

* **Write-Back (Write-Behind)**: The application writes to the cache, which acknowledges the operation immediately. In the background, the cache asynchronously flushes the modifications to the database in batches. 
  
  This provides extremely high write throughput and low write latency. However, it introduces data loss risks if the cache node crashes before flushing its dirty pages to disk.

* **Write-Behind Batching**: In advanced write-back setups, the caching tier merges multiple writes to the same key into a single database write. This technique is highly effective for hot counters, like post view counts, because it replaces thousands of individual database updates with a single batched write-back operation.

* **Write-Around**: Writes bypass the cache entirely and are saved directly to the database. This pattern avoids cluttering the cache with data that may not be read immediately. However, the first read of any newly written record will always result in a slow cache miss.

```
[Caching Patterns Comparison]

+---------------+---------------+---------------+---------------------+---------------------+
| Pattern       | Read Latency  | Write Latency | Data Consistency    | Failure Complexity  |
+---------------+---------------+---------------+---------------------+---------------------+
| Cache-Aside   | Low (on hit)  | Low           | Eventual (stale risk) Application managed |
+---------------+---------------+---------------+---------------------+---------------------+
| Read-Through  | Low (on hit)  | High          | Strong              | Managed by cache    |
+---------------+---------------+---------------+---------------------+---------------------+
| Write-Through | Low           | High          | Strong              | High (double write) |
+---------------+---------------+---------------+---------------------+---------------------+
| Write-Back    | Extremely Low | Extremely Low | Weak (delay)        | Very High (loss)    |
+---------------+---------------+---------------+---------------------+---------------------+
| Write-Around  | High (first)  | Low           | Eventual            | Low                 |
+---------------+---------------+---------------+---------------------+---------------------+
```

### Eviction Policies
Because RAM is expensive and finite, caches eventually run out of space. Eviction policies define which keys are deleted to make room for new writes:

* **Least Recently Used (LRU)**: Discards the keys that haven't been accessed for the longest period of time. Under the hood, this is implemented using a hash map combined with a doubly-linked list. Every time a key is accessed, it is moved to the head of the list. Eviction removes nodes from the tail.

* **Least Frequently Used (LFU)**: Discards keys based on how rarely they are accessed. It maintains an access counter for each key. This prevents deleting keys that are occasionally accessed but highly important, though it can waste memory keeping old, high-frequency keys that are no longer active.

* **First In First Out (FIFO)**: Discards keys in the exact order they were inserted, regardless of how often or recently they were accessed. This is simple to implement but performs poorly for real-world access patterns.

* **Adaptive Replacement Cache (ARC)**: Dynamically tunes between LRU and LFU. It tracks both recent access and access frequency using two double-linked lists, providing a higher hit ratio than LRU under varied workloads.

* **Time To Live (TTL)**: Expired keys are deleted automatically. Caches clean these keys using passive eviction (deleting a key when a client attempts to read it) and active eviction (a background thread periodically scanning and purging random expired keys).

### Cache Invalidation: The Hard Problem
Keeping the cache in sync with the database is notoriously difficult due to race conditions in concurrent systems. For instance, if Server A reads a database value during a cache miss, and Server B simultaneously updates the database and deletes the cache, Server A might write its stale database value back into the cache.

To mitigate this, databases can publish changes to a queue using Change Data Capture (CDC). A worker process then consumes these change events to invalidate cache keys sequentially, avoiding dual-write race conditions.

#### Delete vs Update Controversy
In Cache-Aside, developers often debate whether to update or delete the cache key during database writes. Deleting the key is the industry standard. 

If you update the key instead of deleting it, concurrent writes can easily lead to race conditions where the cache contains stale data indefinitely. For example, if Write 1 and Write 2 happen concurrently, Write 2 might update the database last, but Write 1's cache update could arrive last, overwriting Write 2's fresher data in the cache.

### Distributing a Cache
To scale a cache horizontally, keys must be spread across multiple machines:

* **Consistent Hashing**: Keys are hashed onto a ring to determine which node owns them. This ensures that adding or removing a cache node only invalidates a small fraction of keys, preventing a massive database-hammering outage.

* **Replication**: Replicating cache nodes allows read scaling. It also provides high availability so that if a primary cache node fails, a replica can immediately handle requests. This prevents cache cold-starts where a dead node forces all traffic back to the database.

* **Cache Warm-up**: Introducing an empty, cold cache node to a high-traffic cluster can crash the database tier due to a sudden flood of cache misses. To prevent this, teams warm up new nodes by pre-loading them with historical hot keys, or by routing production traffic to them gradually using incremental canary weights.

### Hot Keys and the Cache Stampede (Thundering Herd)
A hot key is an extremely popular record (like a celebrity profile). If this key expires or is deleted, thousands of concurrent requests will result in a cache miss at the exact same millisecond. 

These requests will all query the database simultaneously. This thundering herd can saturate database connections, spike CPU usage, and crash the data tier.

```
       [Cache Stampede / Thundering Herd]
       
  Client 1 ----+
  Client 2 ----+--> [Cache Miss] ----> [Database Query] ----> Database Crashes!
  Client 3 ----+
```

Mitigation strategies include:

* **Request Coalescing (Single-Flight)**: The application tier uses locks to ensure only one thread queries the database for a specific key at a time. Other concurrent threads wait for that single thread to complete and write the result back to the cache, then read from the cache.

* **Probabilistic Early Recompute (XFetch)**: The application calculates the probability of key expiration as the TTL nears its end. If a random calculation determines the key should be recomputed early, a single background worker updates the cache value before it actually expires.

* **TTL Jitter**: Adding small, random offsets to TTL values. This prevents massive batches of keys (such as those imported during a bulk migration) from expiring at the exact same moment.

* **Local In-Memory Caching**: For extremely hot keys, application servers can store a secondary copy of the key in their own local process memory (like a local Guava or Caffeine cache) for a few seconds. This prevents the hot key from saturating even the distributed cache network interfaces.

* **Partition Key Salting**: Extremely hot keys can be duplicated across multiple partition servers. If key `hot_item` is heavily requested, we write copies to keys like `hot_item_1`, `hot_item_2`, and `hot_item_3`. Read requests are randomly routed to one of these salted variants. This distributes the massive network load across different cache nodes.

### Redis vs Memcached
The two dominant distributed caching systems have clear trade-offs in their architecture and scaling mechanisms:

* **Memcached**: A simple, highly performant, multi-threaded key-value store. It is designed purely for caching flat strings or blobs. Memcached uses a slab allocation memory management system. This system groups memory into pre-allocated slabs of specific sizes, which avoids memory fragmentation over time. Memcached excels at static caching where memory efficiency is paramount.
  
  To scale, Memcached clusters rely on client-side partitioning. Individual Memcached nodes do not communicate with each other, and there is no native clustering protocol. The client hashing library (often using consistent hashing) is entirely responsible for deciding which node receives a read or write.

* **Redis**: A single-threaded (mostly, utilizing background threads for non-blocking deletes and IO) data structure store. It natively supports hashes, lists, sets, sorted sets, and streams. Redis runs an event loop using system multiplexing (like epoll or kqueue) to handle thousands of concurrent connections efficiently on a single thread, avoiding lock contention. 
  
  Redis supports data persistence, pub/sub messaging, Lua scripting, and high availability via Redis Sentinel. For horizontal scale, Redis Cluster natively partitions the keyspace across 16,384 logical hash slots. Redis nodes communicate with each other using a gossip protocol to manage state, detect failures, and handle automatic failovers.

---

### Worked Example 1: Cache-Aside Read Miss and Write Flow
Let's trace a user profile fetch in a system using the Cache-Aside pattern.

```
Sequence Flow:

1. Client requests User Profile ID 402.
2. Application queries Redis: GET "user:402".
3. Redis returns NIL (Cache Miss).
4. Application queries Postgres: SELECT * FROM users WHERE id = 402.
5. Postgres returns user record { "id": 402, "name": "Alice" }.
6. Application writes to Redis: SET "user:402" '{ "id": 402, "name": "Alice" }' EX 3600 (TTL set to 1 hour).
7. Application returns user record to Client.
```

---

### Worked Example 2: Write-Through vs Write-Back Node Crash Analysis
Let's analyze what happens during write operations under two different caching strategies when a hardware crash occurs.

```
Scenario A: Write-Through Cache
1. Client updates user address: POST /address { "user_id": 402, "city": "Madrid" }.
2. Application sends write to Cache Node.
3. Cache Node initiates write to Database.
4. Database successfully writes to disk.
5. Database returns success to Cache Node.
6. Cache Node writes to RAM.
7. Cache Node returns success to Application.
8. Application returns success to Client.

* If Cache Node or Database crashes at Step 3:
  Write fails. Client receives 500 error. No data corruption occurs because the transaction was never committed.

Scenario B: Write-Back Cache
1. Client updates user address: POST /address { "user_id": 402, "city": "Madrid" }.
2. Application sends write to Cache Node.
3. Cache Node writes "city": "Madrid" to dirty page in RAM.
4. Cache Node immediately returns success to Application.
5. Application returns success to Client.
6. [CRASH OCCURS] Cache Node loses physical power before background thread can flush dirty page to Database.

* Impact:
  Client believes their data is safely saved because they received a 200 OK. However, the update is lost forever.
  The Database still contains the old address value. This leads to silent data loss and inconsistency.
```

---

### Worked Example 3: Mitigating Cache Stampede using Single-Flight Coalescing
Let's look at how a news website handles a viral homepage article when the cache key expires.

```
Without Single-Flight Coalescing:
1. Article key "news:top" expires at Time 12:00:00.000.
2. 5,000 concurrent user requests arrive between 12:00:00.001 and 12:00:00.020.
3. All 5,000 requests find the key missing in Redis.
4. All 5,000 threads send "SELECT * FROM articles WHERE id = 99" to MySQL.
5. Postgres connection pool is exhausted, CPU utilization spikes to 100%, and application starts returning 504 Gateway Timeouts.

With Single-Flight Coalescing:
1. Article key "news:top" expires at Time 12:00:00.000.
2. 5,000 concurrent user requests arrive.
3. Thread 1 acquires a local mutex lock for key "news:top".
4. Threads 2 through 5,000 fail to acquire the lock and block, waiting on a shared promise/future for key "news:top".
5. Thread 1 queries Postgres: SELECT * FROM articles WHERE id = 99.
6. Thread 1 writes the result back to Redis: SET "news:top" "..." EX 600.
7. Thread 1 broadcasts the article data to the waiting Threads 2 through 5,000.
8. All 5,000 threads return the article successfully. Only 1 query actually touched the database disk.
```

## Pros
* **Extremely low read latency**: Serving reads directly from RAM reduces response times to single-digit milliseconds or microseconds.
* **Database offloading**: Caching reduces the processing load on database instances, allowing teams to use smaller database servers.
* **Highly predictable tail latency**: By avoiding disk operations and lock contention, caches keep p99 and p99.9 latency spikes to a minimum.
* **Scalable read performance**: Adding cache replicas allows applications to scale read throughput horizontally to handle millions of queries per second.
* **Session and state management**: Caches provide a fast, centralized store for transient data like user login sessions and rate-limiting counters.

## Cons
* **Cache invalidation complexity**: Ensuring data in the cache is synchronized with the primary database requires complex application logic and introduces race conditions.
* **Memory cost**: RAM is significantly more expensive per gigabyte than SSD storage, making large caches costly to run.
* **Data consistency risks**: Relying on eventual consistency models can lead to applications serving outdated or stale data to users.
* **Cold-start vulnerability**: If a caching cluster restarts, the empty cache will forward all incoming queries to the database, potentially crashing it.
* **Increased system surface area**: Adding an additional caching tier increases infrastructure complexity, monitoring requirements, and network points of failure.

## Alternatives
* **Materialized views**: Many relational databases pre-compute and store complex query results on disk. Choose this when data changes slowly and you need SQL compliance.
* **In-memory databases**: Running databases like Redis as the primary data store rather than a cache. Choose this when you can tolerate memory-limit constraints but want maximum speed.
* **Database read replicas**: Scaling reads by replicating your primary database. Choose this when query logic is complex and caching raw key-value pairs is impractical.

## When to use it
* **Read-heavy workloads**: Use caching when your application has a high read-to-write ratio (such as 100:1), allowing the cache to handle the vast majority of traffic.
* **Slow database queries**: Cache the results of complex SQL joins, aggregations, or search operations that take hundreds of milliseconds to compute.
* **Transient session storage**: Store user sessions, shopping carts, or authentication tokens that require fast access but do not need long-term database durability.
* **Rate-limiting counters**: Store API usage counters that require low latency increments and automatically expire after a specific time window.

## When NOT to use it
* **Write-heavy workloads**: Avoid caching if your application is write-heavy (such as a logging or telemetry system). Writing to a cache and immediately syncing to disk adds overhead with no read benefit.
* **Highly dynamic data**: Don't cache records that change constantly (such as real-time stock prices). The overhead of constantly invalidating and rewriting keys will negate any performance gains.
* **Strict transactional consistency**: Do not use a cache for financial ledger transactions or inventory balances where stale data can lead to double-spending or over-selling.
* **Massive, cold datasets**: If your dataset is huge but rarely accessed (such as historical archives), storing it in an expensive RAM-based cache is an inefficient use of resources.

## Key takeaways / mental model
Think of a distributed cache as a desk drawer in an office. The primary database is the archive filing cabinet in the basement. Going to the basement takes minutes (millisecond disk reads). Keeping files you are actively working on in your desk drawer takes seconds (nanosecond RAM reads). 

However, you must clean your desk when files change, or you will work with outdated information (cache invalidation). If you throw away a popular file, everyone in the office might run to the basement at once, jamming the elevator (cache stampede).

## Self-check questions
1. How does the XFetch algorithm mathematically calculate whether a key should be recomputed early, and what parameters determine this probability?
2. Explain how a race condition can occur when two application servers simultaneously try to update a database and invalidate a Cache-Aside key.
3. Why does the Write-Back caching pattern provide the lowest possible write latency, and what are the specific data loss risks associated with it?
4. In Redis, how does the memory footprint and CPU behavior of active eviction differ from passive eviction for expiring keys?
5. Under what scenarios would you choose Memcached over Redis, and why does Memcached handle multi-threaded workloads more efficiently?
6. Imagine a consistent hashing ring with 3 cache nodes. If Node B crashes, what percentage of the keys on the ring are invalidated, and how do virtual nodes mitigate this?
7. How does Memcached's slab allocation memory model prevent memory fragmentation, and what is the potential downside of this model (slab calcification)?
8. What is the difference between ARC (Adaptive Replacement Cache) and standard LRU, and why is ARC considered scan-resistant?

## References
- System Design Guide for Software Professionals (Sinha & Chopra), Chapter 6
- Designing Data-Intensive Applications (Kleppmann), Chapter 1 (Percentiles and Tail Latency)
- Redis Documentation on Clustering, Eviction Policies, and Event Loop Mechanics
- Memcached Architecture and Slab Allocation System Design Papers
