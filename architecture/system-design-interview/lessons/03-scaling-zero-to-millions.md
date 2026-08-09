---
id: system-design-interview/03
subject: system-design-interview
title: "Scaling from Zero to Millions of Users"
slug: scaling-zero-to-millions
status: drafted
mastery: 
seniority: mid
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 3"
prerequisites: [system-design-interview/01, system-design-interview/02]
created: 2026-08-10
updated: 2026-08-10
---

# Scaling from Zero to Millions of Users

## TL;DR
Almost every "design X" interview is really asking you to narrate the same growth
story: start with a single server running everything, then progressively separate
concerns (web tier from database, then add a load balancer, then a cache, then a CDN,
then multiple data centers, then a message queue and sharding) as each specific
bottleneck appears. Knowing this canonical sequence — and *why* each step is triggered
by a specific failure, not by fashion — lets you build up a design incrementally and
justify every component instead of presenting a finished architecture with no story
behind it.

## The idea
A common interview trap is to whiteboard the "final" 50-component architecture
immediately, with load balancers, five caching layers, sharded databases, and a message
queue, for a system that (per your own back-of-the-envelope numbers) has 10,000 users.
This signals cargo-culting, not engineering judgment — a good design is the simplest
one that satisfies the requirements, and complexity should be introduced only when a
concrete bottleneck demands it.

The antidote is to walk the growth path explicitly: what does the *simplest possible*
version of this system look like, what breaks first as load grows, what's the smallest
change that fixes that specific break, and what breaks next. This produces a design
that is also a story, which is both easier for the interviewer to follow and closer to
how real systems actually evolve.

## How it works

### Stage 0: Single server
Everything — web server, application logic, database — lives on one machine. This
easily serves a system with, per your back-of-envelope math (`system-design-interview/02`),
a few hundred to a few thousand users and low request volume. There is no cache, no
load balancer, no replication. This is the right starting point for any interview
answer — state it, then explain what breaks next.

```
[Client] --> [Single Server: web app + database]
```

### Stage 1: Separate the web tier from the database
As traffic grows, the single server's CPU/memory gets contended between serving
requests and running the database. The fix: put the application server and the
database on separate machines, so each can be scaled and tuned independently, and a
crash in one doesn't take down the other.

```
[Client] --> [Web/App Server] --> [Database Server]
```

**Choosing SQL vs. NoSQL here** depends on the access pattern established during
requirements: structured relational data with transactions and joins favors SQL
(Postgres, MySQL); loosely-structured data at very high write volume with simple
key-based access favors NoSQL (DynamoDB, Cassandra, MongoDB). See `system-design/08`
for the full trade-off table.

### Stage 2: Add a load balancer and scale the web tier horizontally
A single app server has a hard ceiling on concurrent connections and CPU. Once traffic
approaches that ceiling, add a load balancer in front of multiple, identical, stateless
app server instances. "Stateless" is the crucial word: if a server stores session data
in local memory, a request that lands on a different server on retry will lose that
session, so session state must move to a shared store (a database or distributed cache)
before you can freely add/remove app servers.

```
                    +--> [App Server 1] --+
[Client] --> [LB] --+--> [App Server 2] --+--> [Database]
                    +--> [App Server 3] --+
```

This also buys you the first layer of fault tolerance: the load balancer health-checks
each server and routes around a dead one, and you can add/remove capacity without
downtime. See `system-design/06` for load balancer algorithms and health checking.

### Stage 3: Replicate the database
The database is now the bottleneck — it's a single point of failure and a single point
of read/write contention. The standard first step is **leader-follower (master-slave)
replication**: writes go to a single leader, which asynchronously (or synchronously)
propagates changes to one or more followers/replicas; reads can be spread across
followers.

```
                                       +--> [DB Follower 1] (reads)
[App Servers] --> [DB Leader] (writes)+
                                       +--> [DB Follower 2] (reads)
```

Since most systems are read-heavy (recall the 100:1 read:write ratio example from
`system-design-interview/02`), this alone can absorb a large amount of additional
traffic by fanning reads out across replicas. It also gives you a hot standby: if the
leader dies, a follower can be promoted. The trade-off is **replication lag** — a
follower may briefly serve stale data — which is a form of eventual consistency you
must call out explicitly if the system needs strong read-your-writes guarantees (e.g.,
a user should immediately see their own comment after posting it).

### Stage 4: Add a cache
Even with read replicas, hitting the database for every read is wasteful when the same
"hot" items (recall the ~90 GB "last 24 hours of tweets" example from
`system-design-interview/02`) are requested repeatedly. Add a cache (Redis/Memcached) in
front of the database, typically using the cache-aside pattern: on a read, check the
cache first; on a miss, read from the database and populate the cache; on a write,
update the database and invalidate (or update) the cache entry.

```
[App Servers] --> [Cache] --(miss)--> [Database]
```

This is often the single highest-leverage change in the whole sequence: moving a hot
read from a disk-backed database (~1 ms/MB) to memory (~0.25 ms/MB, per the reference
numbers in `system-design-interview/02`) both cuts latency and removes load from the
database, letting it handle more writes. See `system-design/10` for eviction policies,
invalidation strategies, and the cache-stampede problem.

### Stage 5: Add a CDN for static content
For any content with a large binary payload — images, video, JS/CSS bundles — serving
it from your own app servers wastes bandwidth and adds latency for geographically
distant users. A CDN caches this content at edge locations near the user.

```
[Client] --> [CDN] --(miss)--> [App/Object Storage]
[Client] --> [LB] --> [App Servers] --> [Cache] --> [Database]
```

Recall from `system-design-interview/02` that image/video storage often dwarfs text
storage by 2-3 orders of magnitude — this is exactly the content a CDN is designed to
absorb, both to cut origin load and to cut cross-continent round-trip latency (recall:
~150 ms cross-continent vs ~0.5 ms same-datacenter).

### Stage 6: Make the web/app tier stateless, and go multi-data-center
To scale the app tier further and survive a full data-center outage, run stateless app
servers (no local session/user data — anything needed across requests lives in a shared
store) across multiple data centers, with a geo-aware load balancer/DNS (e.g., GeoDNS)
routing users to their nearest healthy region.

```
                  US Region                          EU Region
[US clients] --> [LB] --> [App Servers] --> [DB]    [EU clients] --> [LB] --> [App Servers] --> [DB]
                                              \_____________ replication ______________/
```

This introduces real distributed-systems trade-offs: cross-region replication lag,
conflict resolution if both regions can accept writes, and increased operational
complexity (see `system-design/03` on CAP/PACELC for the underlying theory). Most
interview answers should introduce multi-region only after being asked about disaster
recovery/global users specifically — it is a large jump in complexity.

### Stage 7: Add a message queue to decouple and scale asynchronous work
Some work doesn't need to happen synchronously within the request-response cycle:
sending a notification, re-encoding an uploaded video, fanning out a post to followers'
feeds. Pushing this work onto a message queue (Kafka, SQS, RabbitMQ) decouples the
producer (the API server, which can respond to the user immediately) from the consumer
(a pool of workers that process the queue at their own pace), and lets you scale
producers and consumers independently.

```
[App Server] --> [Message Queue] --> [Worker Pool] --> [DB / Object Storage / Notification service]
```

This also adds resilience: if the worker pool is temporarily overwhelmed or down, work
queues up instead of being lost or blocking user-facing requests. See `system-design/11`
for delivery semantics (at-least-once vs. exactly-once) and ordering guarantees.

### Stage 8: Shard the database
Eventually a single database leader — even with read replicas and a cache absorbing
most reads — hits a **write** ceiling, or the dataset outgrows what a single node can
store affordably. At that point, shard: split the data across multiple database
instances by some key (user ID, geographic region, a hash of the primary key), so each
shard holds a fraction of the total writes and storage.

```
[App Servers] --> [Shard Router] --+--> [Shard 1: users A-H]
                                    +--> [Shard 2: users I-P]
                                    +--> [Shard 3: users Q-Z]
```

Sharding is the most invasive change in this sequence — it breaks cross-shard joins and
transactions, complicates resharding when a shard grows unevenly, and needs careful key
selection to avoid hot shards. This is why it's typically the *last* resort, only after
replication and caching have been exhausted, and it's why consistent hashing
(`system-design-interview/05`) matters: it makes adding/removing shards far less
disruptive than naive `hash(key) % N` sharding.

### Putting it together: which stage does a given interview problem need?
The point of walking this sequence is not to always reach Stage 8 — it's to stop at the
stage your back-of-the-envelope numbers justify and explain why. A 10,000-user internal
tool might legitimately stop at Stage 2 or 3. A Twitter-scale feed system, per the
300M-DAU numbers worked out in `system-design-interview/02`, clearly needs caching, a
CDN, a queue for fan-out, and eventually sharding — but you earn the right to add each
one by pointing at the specific bottleneck it fixes.

## Pros
- **Gives every design decision a justification** — "we add a cache because reads
  outnumber writes 100:1 and hot data is small enough to fit in memory" is a much
  stronger interview answer than presenting a cache with no rationale.
- **Matches how real systems actually evolve** — very few production systems are born
  sharded and multi-region; they grow into it as specific bottlenecks appear, so this
  narrative also reflects genuine operational experience.
- **Naturally paces the interview** — each stage is a natural checkpoint to pause and
  ask the interviewer "should we go further, or focus here?"

## Cons
- **Can read as formulaic if recited without adapting** — not every system needs every
  stage in this exact order (a write-heavy analytics ingestion system might need
  sharding long before it needs a CDN); use it as a checklist of *candidate* next
  bottlenecks, not a fixed script.
- **Risks spending too much time on early, "easy" stages** (load balancer, replication)
  that the interviewer already assumes you know, at the expense of the actually
  differentiating deep dive.
- **Doesn't cover data-model or algorithmic depth** — this sequence is about
  infrastructure scaling; the hard, differentiating parts of many designs (e.g., feed
  ranking, ID generation, consistent hashing) need their own deep dive beyond "add more
  infrastructure."

## Alternatives
- **Cloud-native/serverless scaling** — instead of manually reasoning through each
  stage, rely on auto-scaling managed services (e.g., a serverless function platform,
  a managed database with built-in read replicas and auto-sharding). This trades
  control and cost-predictability for operational simplicity, and is worth mentioning
  as a real-world option, but interviewers generally still want you to demonstrate you
  understand *what* is being scaled and why, not just "and then it auto-scales."
- **Vertical scaling only** — buying a bigger single machine instead of adding more
  machines. Simpler operationally, and legitimate for genuinely small/medium scale, but
  it has a hard ceiling (there is a biggest machine you can buy) and no fault tolerance
  (one machine, one failure domain).
- **Starting distributed from day one** (microservices, sharded DB, multi-region) for a
  greenfield product with unknown/low initial traffic — trades a large amount of
  complexity for headroom you may never need; usually the wrong call unless you have
  strong evidence of imminent hyper-growth.

## When to use it
Use this sequence as your mental checklist any time you're designing the high-level
architecture for a system whose scale is genuinely large (per your back-of-the-envelope
numbers). It's also the right way to answer "how would this design change if traffic
grew 100x?" — walk forward from wherever your current design sits in this sequence.

## When NOT to use it
Don't apply it to systems whose bottleneck isn't infrastructure scale at all — e.g., a
concurrency/correctness problem (design a distributed lock), a pure algorithm/data
structure problem (design an autocomplete trie), or a problem explicitly scoped to a
single, small deployment. Also don't march through every stage regardless of your
actual numbers — if your back-of-the-envelope math shows a few thousand QPS that a
single well-provisioned database with a couple of read replicas can absorb, proposing
full geo-sharding across five regions is over-engineering, and a good interviewer will
push back on it.

## Key takeaways / mental model
Picture a single line that gets progressively cut into parallel lanes, each cut
triggered by a specific, nameable bottleneck: one server splits into app+DB (resource
contention) → app tier gets a load balancer and horizontal replicas (CPU/connection
ceiling) → DB gets replicas (read contention) → a cache absorbs hot reads (latency +
DB load) → a CDN absorbs static/media bandwidth (cross-region latency + bandwidth) →
the app tier goes stateless and multi-region (data-center-level fault tolerance) → a
queue decouples slow async work (blocking the request path) → the DB gets sharded
(write/storage ceiling). Each arrow has a *reason*; reciting the stages without the
reasons is a worse interview answer than stopping two stages earlier with clear
justification.

## Self-check questions
1. Why does adding a load balancer require making the app tier stateless, and what
   breaks if you skip that step?
2. A system has a 100:1 read:write ratio and its hot dataset fits in a few hundred GB.
   Which two stages from this sequence would you prioritize before considering
   sharding, and why?
3. What specific problem does database sharding solve that read replicas and caching
   cannot?
4. Why is a message queue introduced specifically for work like fan-out or video
   transcoding, rather than for, say, a simple login request?
5. An interviewer asks, "what if this needs to survive an entire AWS region going
   down?" Which stage of this sequence answers that, and what new problem does it
   introduce that a single-region design didn't have?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 3
