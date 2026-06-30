# System Design (applying DDIA in practice)

The applied layer of the track: take the theory from *Designing Data-Intensive
Applications* and use it to design real, scalable, reliable systems - load balancing,
caching, sharding, queues, APIs, security, observability, and full end-to-end case
studies. Most lessons cross-link back to the DDIA concept they build on.

**Source book:** *System Design Guide for Software Professionals* - Dhirendra Sinha
and Tejas Chopra (Packt, 2024).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`system-design/<NN>`* (e.g. *"discuss `system-design/09`"*). Ordered by dependency:
foundations first, then core components, then cross-cutting concerns and case studies.

## Concepts

| ID  | Concept | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | System design fundamentals | drafted | — | — | [lesson](lessons/01-fundamentals.md) | — |
| 02  | Distributed-system attributes and scaling | drafted | — | — | [lesson](lessons/02-distributed-system-attributes.md) | — |
| 03  | CAP, PACELC, and consensus in practice | drafted | — | — | [lesson](lessons/03-cap-pacelc-consensus.md) | — |
| 04  | Consistent hashing | drafted | — | — | [lesson](lessons/04-consistent-hashing.md) | — |
| 05  | Probabilistic data structures for scale | drafted | — | — | [lesson](lessons/05-probabilistic-data-structures.md) | — |
| 06  | DNS and load balancing | drafted | — | — | [lesson](lessons/06-dns-load-balancing.md) | — |
| 07  | API gateways and reverse proxies | drafted | — | — | [lesson](lessons/07-api-gateways-proxies.md) | — |
| 08  | Choosing databases and storage | drafted | — | — | [lesson](lessons/08-choosing-databases-storage.md) | — |
| 09  | Replication and sharding in practice | drafted | — | — | [lesson](lessons/09-replication-sharding-in-practice.md) | — |
| 10  | Distributed caching | drafted | — | — | [lesson](lessons/10-distributed-caching.md) | — |
| 11  | Pub/sub and distributed queues | drafted | — | — | [lesson](lessons/11-pubsub-distributed-queues.md) | — |
| 12  | API design and communication | drafted | — | — | [lesson](lessons/12-api-design-communication.md) | — |
| 13  | Security: authentication and authorization | drafted | — | — | [lesson](lessons/13-security-auth.md) | — |
| 14  | Rate limiting and resilience | drafted | — | — | [lesson](lessons/14-rate-limiting-resilience.md) | — |
| 15  | Observability: logging, metrics, tracing | drafted | — | — | [lesson](lessons/15-observability.md) | — |
| 16  | A system-design method (URL shortener) | drafted | — | — | [lesson](lessons/16-design-method-url-shortener.md) | — |
| 17  | Case study: news feed and timelines | drafted | — | — | [lesson](lessons/17-case-study-news-feed.md) | — |
| 18  | Case study: real-time collaboration | drafted | — | — | [lesson](lessons/18-case-study-realtime-collaboration.md) | — |
| 19  | Case study: video streaming | drafted | — | — | [lesson](lessons/19-case-study-video-streaming.md) | — |
| 20  | Case study: proximity / geo service | drafted | — | — | [lesson](lessons/20-case-study-proximity-service.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**DDIA prerequisites** are listed per lesson in its front matter as cross-subject IDs
(e.g. `ddia/07`); each lesson also names the DDIA concept it builds on in prose.
