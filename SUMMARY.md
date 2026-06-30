# Oh My Learning - Cross-Domain Summary

A top-level view of every domain and subject, its coverage, and overall mastery.
Regenerated as lessons are added and after every discussion.

## Architecture

The domain covering how to design software systems - theory and applied practice.

### 1. DDIA - Designing Data-Intensive Applications

The theoretical foundation of the track.

- **Status:** 16/16 lessons authored (all `drafted`); not yet discussed, mastery pending.
- **Covers:** reliability, scalability and maintainability; data models and query languages; storage engines (OLTP/OLAP, column storage); encoding and schema evolution; replication; partitioning; transactions; distributed-systems failure modes; consistency and consensus; batch and stream processing.
- **Read:** [progress table](architecture/ddia/README.md) and [concept-by-concept recap](architecture/ddia/SUMMARY.md).

### 2. System Design - System Design Guide for Software Professionals

The applied layer of the track: takes DDIA theory and uses it to design real systems. Most lessons cross-link to the DDIA concept they build on.

- **Status:** 20/20 lessons authored (all `drafted`); not yet discussed, mastery pending.
- **Covers:** distributed-system attributes; CAP/PACELC and consensus; consistent hashing; DNS and load balancing; API gateways and proxies; databases, storage and sharding; distributed caching; pub/sub and queues; API design and communication; security and auth; rate limiting and resilience; observability; a repeatable design method; and case studies (URL shortener, news feed, real-time collaboration, video streaming, proximity service).
- **Read:** [progress table](architecture/system-design/README.md) and [concept-by-concept recap](architecture/system-design/SUMMARY.md).

### 3. The Hard Parts - Software Architecture: The Hard Parts

The trade-off layer of the track: how to pull a monolith apart and put it back together, reasoning about everything as explicit trade-offs. Cross-links to DDIA and System Design.

- **Status:** 17/17 lessons authored (all `drafted`); not yet discussed, mastery pending.
- **Covers:** trade-offs and "no best practices"; static and dynamic coupling and the architecture quantum; architectural modularity and decomposition; component-based decomposition patterns; service and data granularity; reuse patterns; data ownership; distributed transactions and eventual consistency; distributed data access; orchestration vs choreography; the eight transactional saga patterns; strict vs loose contracts; and analytical data (warehouse, lake, mesh).
- **Read:** [progress table](architecture/hard-parts/README.md) and [concept-by-concept recap](architecture/hard-parts/SUMMARY.md).

### 4. Fundamentals of Software Architecture

- **Status:** planned, not started.
- **Focus:** consolidating architectural concepts and vocabulary.

## Other domains

None yet. Future domains such as `clean-code` and `engineering-practices` will appear
here beside `architecture/` as the library grows.

## Focus areas (aggregated weak spots)

None yet - discussions have not started. As discussions happen across subjects, the
open weak spots (especially concepts rated `shaky` or `not-yet`) will be collected
here so it is clear what to revisit.
