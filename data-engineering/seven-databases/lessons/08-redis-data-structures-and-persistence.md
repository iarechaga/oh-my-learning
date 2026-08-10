---
id: seven-databases/08
subject: seven-databases
title: "Redis: In-Memory Data Structures, Caching Roles, and Persistence Modes"
slug: redis-data-structures-and-persistence
status: drafted
mastery:
seniority: mid
source: Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 8
prerequisites: [seven-databases/01]
created: 2026-08-10
updated: 2026-08-10
---

# Redis: In-Memory Data Structures, Caching Roles, and Persistence Modes

## TL;DR
Redis is an in-memory key-value store whose defining feature is not "it's fast because it's in memory" (true, but incomplete) but that its values are **typed data structures** — strings, lists, sets, sorted sets, hashes, streams — each with its own set of atomic, purpose-built operations, letting you push logic that would otherwise require read-modify-write round trips (and race conditions) directly into single, atomic server-side commands.

## The idea
Every database in this subject so far stores opaque blobs, rows, or documents and leaves it to the application to interpret their structure. Redis instead gives the *server* native understanding of a handful of general-purpose data structures, and exposes operations on them directly: `LPUSH` to push onto a list, `SADD` to add to a set, `ZINCRBY` to increment a member's score in a sorted set. Because these operations run inside Redis's single-threaded event loop, each one is atomic without any application-side locking — a huge simplification for the exact kind of "increment a counter," "add to a queue," "track a leaderboard" operations that are surprisingly fiddly to get race-condition-free against a general-purpose database.

The second defining trade-off is that Redis is fundamentally memory-resident: your entire (or working-set) dataset lives in RAM, which is why operations are so fast (no disk seek on the read path) and why capacity planning for Redis means "how much RAM," a very different constraint from every disk-backed database in this subject.

## How it works

### Data structures, concretely

**Strings** — the simplest type, but with atomic operations that matter: `INCR pageviews:home` atomically increments a counter with no read-modify-write race, even under massive concurrent traffic. Compare this to doing `SELECT count FROM pageviews WHERE page='home'` then `UPDATE ... SET count = count + 1` in a naively-written application against a relational database — that's a classic race condition unless wrapped in a transaction or `UPDATE ... SET count = count + 1` is used directly; Redis makes the atomic, race-free version the *only* obvious way to write it.

**Lists** — ordered collections supporting push/pop from either end in O(1): `LPUSH queue:emails job123` and `RPOP queue:emails` implement a simple work queue directly, no separate message-broker needed for lightweight cases.

**Sets** — unordered unique collections with fast membership tests and set algebra: `SADD online_users user_42` tracks who's currently online; `SINTER online_users vip_users` finds VIP users currently online in one atomic operation, without pulling both lists into the application and intersecting them there.

**Sorted sets (ZSET)** — like a set, but each member has a floating-point score, kept in sorted order. **Worked example — a real-time leaderboard.** `ZADD leaderboard 15420 "player_88"` adds or updates a player's score; `ZREVRANGE leaderboard 0 9 WITHSCORES` returns the top 10 players, sorted, in one O(log N) operation. Building this against PostgreSQL means `ORDER BY score DESC LIMIT 10` with an index — perfectly workable, but Redis's sorted set also supports `ZRANK` (a player's exact rank among millions, in O(log N)) and `ZRANGEBYSCORE` (all players within a score band) as first-class atomic operations, which is why leaderboards, priority queues, and rate limiters are canonical Redis use cases.

**Hashes** — a map of field-value pairs under one key, useful for representing an object (like a lightweight document) without JSON-serializing and deserializing it on every access: `HSET user:42 name "Dana" email "dana@example.com"`, and `HGET user:42 email` fetches just that field, not the whole object.

### Caching: the most common role, and why it's more than "a fast dictionary"
**Worked example — cache-aside pattern.** A product page needs product details that are expensive to compute (aggregated from several PostgreSQL tables). On request: check `GET product:9182` in Redis; on a cache hit, return it directly (sub-millisecond); on a miss, query PostgreSQL, then `SET product:9182 <json> EX 300` (expire in 300 seconds) before returning. This is the cache-aside pattern, and Redis's `EX`/`PX` (expiry) options make time-boxed caching a one-line concern rather than a manually-managed cleanup job. The real design work in caching isn't the Redis command — it's choosing what to cache, the expiry window (balancing staleness against database load), and the invalidation strategy for when the underlying data changes before the TTL expires (a notoriously hard problem — "there are only two hard things in computer science: cache invalidation and naming things").

### Persistence modes — Redis is not purely ephemeral
A common misconception is that Redis data disappears on restart. In reality Redis offers two persistence mechanisms, usable together: **RDB** (point-in-time snapshots written to disk on a schedule or on demand) and **AOF** (Append-Only File, logging every write operation, replayed on restart to reconstruct state, with configurable fsync frequency trading durability against write throughput). Neither makes Redis as durable as a disk-native database like PostgreSQL by default — a crash between snapshots (RDB) or before an fsync (AOF) can lose recent writes — which is exactly why Redis is usually deployed as a cache or ephemeral-data store backed by a durable system of record, rather than as the sole store for data you cannot afford to lose, even though AOF with `fsync always` can get close to that guarantee at a real latency cost.

### Beyond caching: primary-store and messaging roles
Redis's data structures are expressive enough that it's often used as more than a cache: as a lightweight message queue (via lists or the dedicated Streams type), a rate limiter (`INCR` with `EXPIRE` implementing a sliding or fixed window), a session store (hashes with TTLs), or even a primary store for data whose durability requirements are met by AOF plus replication. The distinction to keep clear: "Redis as cache" (data also lives durably elsewhere, Redis is disposable) is a fundamentally different reliability posture than "Redis as primary store" (Redis's own persistence and replication are the only copies), and conflating the two is a common production incident source — losing a "just a cache" Redis instance is a performance blip; losing a "primary store" Redis instance without proper persistence and replication is data loss.

### Scaling and consistency model
A single Redis instance is single-threaded for command execution, which is what makes its data-structure operations atomic without explicit locking, and also means CPU-bound work (a very large `SORT`, for instance) blocks all other clients momentarily. Redis Cluster shards data across multiple nodes by hashing keys into 16384 hash slots distributed across the cluster, similar in spirit to DynamoDB's partition-key hashing (`seven-databases/07`) — and, as with any sharded system, operations spanning keys on different shards (like a multi-key transaction across two different hash slots) are constrained or unavailable. Replication (primary-replica) provides read scaling and failover; Redis Sentinel or Cluster mode handles automatic failover, a deliberate AP-leaning-with-tunable-durability posture per the framing in `seven-databases/01`.

## Pros
- Purpose-built, atomic data structure operations eliminate entire classes of race conditions that would otherwise require careful locking or transactions against a general-purpose database.
- Sub-millisecond latency for in-memory operations makes it the default choice for caching, session storage, rate limiting, and real-time leaderboards.
- Versatile enough to serve caching, lightweight queuing, and pub/sub messaging roles from one system, reducing the number of moving pieces in simpler architectures.

## Cons
- Dataset size is bounded by available RAM, which is a fundamentally more expensive and more constrained resource than disk — this puts a real ceiling on how much data you can keep in Redis cost-effectively, unlike disk-backed systems in this subject.
- Default persistence modes (RDB, AOF) trade some durability for performance; treating Redis as a system of record without understanding this trade-off risks real data loss on a crash.
- Single-threaded command execution means one slow, CPU-heavy command can stall all other clients momentarily — a class of operational risk that doesn't exist the same way in databases with per-query parallelism.

## Alternatives
- **Memcached** — a simpler, purely in-memory key-value cache without Redis's rich data structures or persistence options; a reasonable choice when you genuinely only need a flat cache and want the simplest possible operational model.
- **DynamoDB with DAX (accelerator)** (`seven-databases/07`) — adds a managed in-memory caching layer in front of DynamoDB rather than operating a separate Redis fleet, appropriate when you're already committed to DynamoDB and want caching without a second system to manage.
- **PostgreSQL with an in-memory-optimized extension or careful indexing** (`seven-databases/02`) — viable when the "cache" need is really just "make this specific query fast," solvable with proper indexing rather than introducing a second data store and its cache-invalidation complexity.

## When to use it
Reach for Redis whenever you need sub-millisecond access to hot data, atomic operations on structured values (counters, queues, leaderboards, sets) without hand-rolled locking, or a lightweight caching layer in front of a slower system of record — and your working set fits comfortably (with margin) in the RAM you're willing to provision.

## When NOT to use it
Avoid using Redis as your sole system of record for data you cannot afford to lose without deliberately configuring and testing AOF durability and replication for that exact guarantee — the default mental model of "Redis as disposable cache" is safer and more common for good reason. Avoid it too when your dataset is large and cold (rarely accessed) — paying for RAM to hold data you rarely touch is a poor cost trade compared to a disk-backed store. See `seven-databases/09` for the comparison framework.

## Key takeaways / mental model
Redis's value isn't "fast key-value store" alone — it's "atomic, purpose-built operations on typed data structures, held in memory." Ask two questions before reaching for it: does this operation benefit from an atomic structure-aware command (counter, queue, leaderboard, set membership)? And is this data disposable (cache) or does it need Redis's persistence and replication actually configured for durability (primary store)? Conflating those two questions is the most common Redis production mistake.

## Self-check questions
1. Explain why `INCR` in Redis avoids a race condition that a naive "read count, add one, write count" sequence against PostgreSQL would have, and name the PostgreSQL-side fix that closes the same gap.
2. A team is using Redis purely as a cache in front of PostgreSQL, but just realized a critical feature flag is stored *only* in Redis with no backing table. Why is this a problem, and what are the two ways to fix it (in terms of the cache-vs-primary-store distinction)?
3. Given a real-time multiplayer game needing a live leaderboard of 2 million players updated thousands of times per second, walk through why a Redis sorted set is a strong fit, and name the specific commands you'd use for "show me the top 10" and "what's my rank."
4. A team wants to store their entire multi-terabyte product catalog in Redis "for speed." What would you push back on, and what alternative(s) would you propose instead?

## References
- Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 8: "Redis."
- See also: `seven-databases/01` (CAP and durability framing), `seven-databases/07` (DynamoDB's related sharding model), `database-internals/08` (engine trade-offs) for deeper background.
