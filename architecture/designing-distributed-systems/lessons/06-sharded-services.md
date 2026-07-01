---
id: designing-distributed-systems/06
subject: designing-distributed-systems
title: "Sharded Services"
slug: sharded-services
status: drafted
mastery:
seniority: senior
source: "Designing Distributed Systems (Brendan Burns), Chapter 6"
prerequisites: [designing-distributed-systems/05]
created: 2026-07-01
updated: 2026-07-01
---

# Sharded Services

## TL;DR
When a service's *data* is too big or too hot to fit in one replica, you cannot just clone identical copies - you split the data into partitions called shards and give each shard to a different replica, so each replica owns a slice and only that slice. A request must now be routed to the *specific* shard that holds its data, which introduces a sharding function and a routing layer. Replication answers "handle more requests"; sharding answers "handle more *data* (or state) than one node can hold" - and real systems usually do both at once.

## The idea
A [replicated load-balanced service](05-replicated-load-balanced.md) assumes every replica is interchangeable because they are all stateless and share one backing store. That assumption collapses in two situations:

1. **The state is too big for one node.** A 10 TB in-memory cache cannot live on a machine with 64 GB of RAM, no matter how many identical copies you run - each copy would still need all 10 TB.
2. **The state is too hot for one node.** Even if it fit, the request rate against that single shared store might exceed what one store can serve.

Sharding solves both by **partitioning the data across nodes**: shard 0 holds one slice, shard 1 another, and so on. No single node holds everything, so the total capacity (memory, or throughput against distinct data) becomes the *sum* of the shards. The price is that replicas are no longer identical - each owns a specific slice - so a request for key `K` must be sent to the *one* shard that owns `K`. That routing decision is the heart of the pattern.

The canonical example in the book is a **sharded cache** placed in front of a database to protect it and cut latency. The cache is too large to replicate, so it is sharded: each cache node caches a disjoint subset of keys. A cache miss falls through to the database; a hit is served from memory.

## How it works

### The sharding function: mapping a request to a shard
The core of sharding is a deterministic function: `shard = f(shard_key) mod N` (conceptually), where `shard_key` is something stable in the request (a user ID, a cache key, a tenant ID) and `N` is the number of shards. "Deterministic" is essential: the same key must always map to the same shard, or you would store data on one shard and look for it on another.

Two families of sharding function, with very different failure behavior:

- **Modulo/hash sharding:** `shard = hash(key) mod N`. Simple and even, *but* changing `N` (adding or removing a shard) changes `hash(key) mod N` for almost every key, so nearly all data lands on the wrong shard at once - catastrophic for a cache (mass miss) and a data-mover's nightmare for a database.
- **Consistent hashing:** map both keys and shards onto a hash ring; a key belongs to the next shard clockwise. Adding or removing a shard only relocates the keys between two adjacent points - roughly `1/N` of the data - instead of almost all of it. This is why production sharded systems overwhelmingly use consistent hashing. (Full mechanics in [system-design/04 - Consistent hashing](../../system-design/lessons/04-consistent-hashing.md).)

```text
   key "user:42"
        |
        v
   +-----------+   hash(key) -> position on ring -> next node clockwise
   | shard fn  |
   +-----------+
     |   |   |
     v   v   v
  shard0 shard1 shard2   (each owns a disjoint key range)
```

### Where the routing lives
Something must apply the sharding function and send the request to the right shard. There are three common placements, and choosing one is an architecture decision:

1. **In the client / a client library:** the caller computes the shard and connects directly. Fewest hops, lowest latency, but every client must embed and agree on the sharding logic (and update in lockstep when it changes).
2. **In an ambassador** (see [the ambassador pattern](03-ambassador.md)): the app talks to `localhost`, and a co-located ambassador container computes the shard and routes. The app stays simple and shard-oblivious; the sharding logic is packaged as a reusable container. This is the book's favored composition.
3. **In a dedicated routing tier / proxy:** a standalone fleet of routers in front of the shards. Centralizes the logic but adds a network hop and its own thing to scale and operate.

### Sharding is orthogonal to replication - and you usually want both
A raw sharded service has a glaring weakness: if shard 2's node dies, the slice of data it owned is *unavailable* (for a cache, those keys now all miss; for a datastore, they are down). Sharding alone trades the single-point-of-failure of one big node for N smaller points of failure.

The production answer is to **replicate each shard**: every shard is itself a small replicated group (a primary plus replicas). Now:

- **Sharding** gives you data-capacity scale (sum of shards).
- **Replication within a shard** gives you availability and read scale for that slice.

```text
        Router / Ambassador
        /        |         \
  shard 0     shard 1     shard 2
  +-----+     +-----+     +-----+
  | P   |     | P   |     | P   |   P = primary
  | R R |     | R R |     | R R |   R = replica of THIS shard's data
  +-----+     +-----+     +-----+
```

This "shard across, replicate within" shape is the backbone of systems like sharded Redis, Cassandra, and most large databases. It composes the two multi-node serving patterns: lesson 05 handles "more requests," this lesson handles "more data."

### Hot shards and the rebalancing problem
Sharding assumes load spreads evenly across shards. It often does not. If one key (or key range) is far more popular than others - a celebrity user, a viral item, a giant tenant - the shard that owns it becomes a **hot shard**: overloaded while its peers idle. Mitigations:

- **Better key choice:** shard on a higher-cardinality, more uniform key so no single value dominates.
- **Split the hot shard:** with consistent hashing, add nodes/virtual-nodes around the hot range so its keys spread across more shards.
- **Replicate the hot shard harder:** give the hot slice more read replicas.
- **Cache/absorb the hot key separately:** e.g. keep the single viral item in a small dedicated cache in front.

Adding or removing shards (rebalancing) is where the choice of sharding function pays off or punishes you, as the next example shows.

### Worked example 1: why modulo sharding devastates a cache on resize
A sharded cache with `N = 4` shards, using `shard = hash(key) mod N`. It is warm: ~90% hit rate, protecting the database.

1. Steady state: key `hash=101` -> `101 mod 4 = 1` -> shard 1. Every lookup for that key hits shard 1. Fine.
2. Traffic grows; you add a 5th shard, so `N` becomes 5.
3. Now the *same* key recomputes: `101 mod 5 = 1` (unchanged here), but consider `hash=102`: was `102 mod 4 = 2`, now `102 mod 5 = 2` - and `hash=103`: was `3`, now `3`; `hash=104`: was `0`, now `4`. Work it across all keys and roughly **80% of keys map to a different shard than before.**
4. Consequence: ~80% of lookups now go to a shard that never cached that key -> mass cache miss -> a stampede of traffic falls through to the database all at once. The database, sized assuming a 90% hit rate, is suddenly hit with ~9x its normal load and may topple.

Now the same resize with **consistent hashing**: adding the 5th node only steals keys from its two ring neighbors - about `1/5` of the keyspace relocates, so ~80% of keys stay put and keep hitting. The database sees a small, survivable bump instead of a cliff. This is the concrete reason production sharding uses consistent hashing.

### Worked example 2: routing a read through an ambassador to the right shard
A service reads user profiles from a sharded datastore with 4 shards, routed by a co-located ambassador.

1. The app issues `GET profile for user:42` to `localhost:6379` (it thinks it is talking to one store).
2. The ambassador computes `shard = consistent_hash("user:42")` -> shard 3.
3. The ambassador opens/reuses a connection to shard 3's primary and forwards the read.
4. Shard 3 returns the profile; the ambassador relays it back over localhost. The app never knew there were 4 shards.
5. Later, an operator adds shard 5. Only the ambassador's ring config changes (pushed centrally). The app code is untouched - the sharding logic was packaged in the reusable ambassador container, exactly as the ambassador pattern promises.

### Worked example 3: a shard fails, with and without replication
Sharded cache, 4 shards, each owning ~25% of keys.

- **Without replication:** shard 2's node crashes. The ~25% of keys it owned now all miss and fall through to the database. That is a 25% cache-hit collapse and a large database load spike concentrated on those keys - a partial outage until a replacement warms up.
- **With replication (each shard = primary + 1 replica):** shard 2's primary crashes; its replica is promoted to primary within seconds. The slice stays available; the hit rate barely dips. The orchestrator then rebuilds a new replica for shard 2 in the background.

The example shows that sharding *needs* replication to be production-grade: sharding alone converts one big failure domain into N smaller ones, but each is still a real outage for its slice.

## Pros
- **Scales state, not just requests:** total memory/throughput is the sum of the shards, so you can hold datasets no single node could.
- **Fault isolation:** a failure (or hot key) is contained to one shard's slice rather than the whole dataset.
- **Composes with replication:** "shard across, replicate within" gives both data-capacity scale and per-slice availability.
- **Targeted scaling:** you can grow only the dimension that is constrained (add shards for data, add replicas for read load).

## Cons
- **Routing complexity:** every request must be mapped to the correct shard; the sharding logic must live somewhere and stay consistent across all callers.
- **Rebalancing is hard:** adding/removing shards moves data; a naive (modulo) function relocates almost everything at once. Even consistent hashing requires careful data migration for stateful stores.
- **Hot shards / skew:** uneven key popularity overloads one shard while others idle; picking a good shard key is genuinely difficult.
- **Cross-shard operations are expensive:** anything that must touch many shards at once (a query spanning shards, a transaction across shards) loses the simplicity - and often needs scatter/gather (lesson 07) or distributed transactions.

## Alternatives
- **Replicated load-balanced service:** when the data *does* fit one shared store and you only need more request throughput - simpler, no routing (lesson 05).
- **Vertical scaling of one store:** a bigger box; works until you hit the single-machine ceiling, then stops.
- **Read replicas + caching (no sharding):** cut load on one primary with caches and read replicas before partitioning; delays sharding but does not raise the write/data ceiling.
- **Managed sharded datastores** (Cassandra, DynamoDB, Vitess, Redis Cluster): let a system implement the sharding, routing, and rebalancing for you rather than hand-building it.

## When to use it
- The dataset or working set is larger than a single node can hold (memory or disk), so identical replicas cannot each carry it all.
- Throughput against *distinct* data exceeds one store's capacity and caching/read-replicas are not enough.
- You can pick a stable, high-cardinality shard key that spreads load evenly and matches your access pattern.
- You can pair it with replication so each shard tolerates node failure.

## When NOT to use it
- The data fits comfortably in one backing store - replicate instead; sharding adds routing and rebalancing complexity for no benefit.
- Your access pattern frequently needs to touch many shards at once (cross-shard joins/transactions), which sharding makes slow and complex - rethink the data model or partition boundary first.
- You cannot find a shard key that avoids severe skew, so one shard would always be hot - fix the key or the access pattern before sharding.

## Key takeaways / mental model
Think of a library too big for one room. Replication is photocopying the *same* room many times (great when the collection is small enough to duplicate); sharding is splitting the collection across *many rooms by call number*, so to find a book you first compute which room holds it. Two rules of thumb:

1. **Sharding scales state; replication scales requests - and you almost always want both** ("shard across, replicate within"), because sharding alone just turns one big failure domain into N smaller outages.
2. **The sharding function is destiny.** Use consistent hashing, not `mod N`, so adding a shard relocates ~`1/N` of the data instead of nearly all of it - and watch for hot shards, because even a perfect function cannot fix a skewed key.

## Self-check questions
1. What two distinct problems does sharding solve that replication alone cannot, and why does the "identical interchangeable replicas" assumption break for large state?
2. Concretely, why does resizing a `hash(key) mod N` cache from 4 to 5 shards cause a mass cache miss, and how does consistent hashing avoid it? Estimate the fraction of keys relocated in each case.
3. Name the three common places the sharding/routing logic can live and give one advantage and one drawback of each. Why does the book favor the ambassador?
4. Why is a raw sharded service (no replication) not production-grade, and what does "shard across, replicate within" fix? Draw the topology.
5. What is a hot shard, what causes it, and what are three ways to mitigate it?
6. You must store 6 TB of session data with per-key lookups, tolerate any single node failing, and occasionally add capacity without a latency cliff. Sketch the sharding function, routing placement, and replication you would choose, and justify each.

## References
- Designing Distributed Systems (Brendan Burns), Chapter 6: "Sharded Services"
- [designing-distributed-systems/05 - Replicated Load-Balanced Services](05-replicated-load-balanced.md)
- [system-design/04 - Consistent hashing](../../system-design/lessons/04-consistent-hashing.md)
