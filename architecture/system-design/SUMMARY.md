# System Design - Subject Summary

A comprehensive recap of the applied system-design subject, concept by concept. This
subject takes the theory from *Designing Data-Intensive Applications* (DDIA) and uses
it to design real systems; most lessons name the DDIA concept they build on.

**Source book:** *System Design Guide for Software Professionals* - Dhirendra Sinha
and Tejas Chopra (Packt, 2024).

**Progress note:** all 20 lessons are `drafted`; none discussed yet, so mastery is
pending and no weak spots are recorded. See the table in [README.md](README.md).
Reading order is top to bottom (dependency-ordered).

## Foundations

- **[01] System design fundamentals** - high-level vs low-level design, a repeatable
  design process, functional vs non-functional requirements, and back-of-the-envelope
  estimation (QPS, storage, the latency numbers every engineer should know).
  ([lesson](lessons/01-fundamentals.md))
- **[02] Distributed-system attributes and scaling** - availability (the nines,
  SLA/SLO/SLI), reliability, durability, latency vs throughput, fault tolerance;
  vertical vs horizontal scaling and why statelessness enables horizontal scale.
  Builds on DDIA 01. ([lesson](lessons/02-distributed-system-attributes.md))
- **[03] CAP, PACELC, and consensus in practice** - under a partition you choose
  Consistency or Availability (CP vs AP systems); PACELC adds the latency-vs-consistency
  choice in normal operation; consensus (Raft/Paxos), quorums, leader election, and
  coordination via ZooKeeper/etcd. Builds on DDIA 09 and 13.
  ([lesson](lessons/03-cap-pacelc-consensus.md))
- **[04] Consistent hashing** - the hash ring plus virtual nodes so only ~K/N keys
  move when a node joins or leaves; powers distributed caches and sharded stores.
  Builds on DDIA 10. ([lesson](lessons/04-consistent-hashing.md))
- **[05] Probabilistic data structures for scale** - Bloom filters (membership, no
  false negatives), count-min sketch (frequencies), and HyperLogLog (cardinality) give
  approximate answers in tiny memory. ([lesson](lessons/05-probabilistic-data-structures.md))

## Core components

- **[06] DNS and load balancing** - DNS resolution with GeoDNS/anycast; L4 vs L7 load
  balancing, algorithms (round-robin, least-connections, IP-hash), health checks, and
  active-active vs active-passive redundancy. ([lesson](lessons/06-dns-load-balancing.md))
- **[07] API gateways and reverse proxies** - gateway responsibilities (routing, auth,
  rate limiting, request aggregation); forward vs reverse proxy; gateway vs load
  balancer vs service mesh; the BFF pattern. ([lesson](lessons/07-api-gateways-proxies.md))
- **[08] Choosing databases and storage** - SQL vs NoSQL families (key-value, document,
  wide-column, graph), choosing by access pattern, and polyglot persistence. Builds on
  DDIA 02 and 05. ([lesson](lessons/08-choosing-databases-storage.md))
- **[09] Replication and sharding in practice** - read replicas and lag; sharding
  strategies (range/hash/directory); a DynamoDB-style design with quorums and virtual
  nodes; combining replication with sharding. Builds on DDIA 07, 08, 10.
  ([lesson](lessons/09-replication-sharding-in-practice.md))
- **[10] Distributed caching** - cache-aside / read-through / write-through /
  write-back, eviction (LRU/LFU/TTL), invalidation, hot keys and the cache-stampede
  problem, Redis vs Memcached. Builds on DDIA 01. ([lesson](lessons/10-distributed-caching.md))
- **[11] Pub/sub and distributed queues** - point-to-point queues vs pub/sub;
  traditional vs log-based brokers; delivery semantics and idempotency; ordering;
  Kafka/Kinesis. Builds on DDIA 15. ([lesson](lessons/11-pubsub-distributed-queues.md))

## Cross-cutting concerns and case studies

- **[12] API design and communication** - REST vs gRPC vs GraphQL, idempotency keys,
  pagination (offset vs cursor), and versioning. Builds on DDIA 06.
  ([lesson](lessons/12-api-design-communication.md))
- **[13] Security: authentication and authorization** - authn vs authz, sessions vs
  JWT, OAuth2/OIDC, TLS/mTLS, and RBAC vs ABAC. ([lesson](lessons/13-security-auth.md))
- **[14] Rate limiting and resilience** - token bucket / leaky bucket / sliding window,
  plus timeouts, retries with backoff and jitter, circuit breakers, bulkheads, and load
  shedding. ([lesson](lessons/14-rate-limiting-resilience.md))
- **[15] Observability** - the three pillars (logs, metrics, traces), the RED and USE
  methods, SLOs and error budgets, and alerting. ([lesson](lessons/15-observability.md))
- **[16] A system-design method (URL shortener)** - a repeatable framework (clarify ->
  estimate -> API -> data model -> architecture -> scale -> bottlenecks) applied
  end-to-end to a URL shortener (key generation, caching/CDN, sharding).
  ([lesson](lessons/16-design-method-url-shortener.md))
- **[17] Case study: news feed and timelines** - fan-out on write vs read vs the hybrid
  (the celebrity problem), the follow graph, media storage with a CDN, and feed ranking.
  Builds on DDIA 01, 10, 15. ([lesson](lessons/17-case-study-news-feed.md))
- **[18] Case study: real-time collaboration** - Operational Transformation vs CRDTs for
  concurrent edits, WebSocket transport, presence, access control, and offline sync.
  Builds on DDIA 08. ([lesson](lessons/18-case-study-realtime-collaboration.md))
- **[19] Case study: video streaming** - the upload/transcoding pipeline (batch), a CDN
  with adaptive bitrate streaming, recommendations, and DRM. Builds on DDIA 14.
  ([lesson](lessons/19-case-study-video-streaming.md))
- **[20] Case study: proximity / geo service** - geospatial indexing with geohash and
  quadtrees, nearby search, and regional sharding. Builds on DDIA 10.
  ([lesson](lessons/20-case-study-proximity-service.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on concepts rated
`shaky` or `not-yet`.
