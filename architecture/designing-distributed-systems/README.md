# Designing Distributed Systems

The reusable-patterns layer for distributed systems built on containers and
orchestration: the repeatable building blocks (single-node and multi-node patterns)
you compose to build reliable distributed applications, plus the batch-processing
patterns. Practical and pattern-oriented, framed around containers/Kubernetes.
Cross-links to DDIA (replication, partitioning, batch) and System Design.

**Source book:** *Designing Distributed Systems* - Brendan Burns (O'Reilly, 2018;
patterns for containerized/orchestrated systems).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`designing-distributed-systems/<NN>`* (e.g. *"discuss `designing-distributed-systems/03`"*).
Ordered by dependency: single-node patterns first, then multi-node serving patterns,
then batch computational patterns.

**Seniority baseline:** mid-senior (lessons range mid->senior).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Why distributed patterns (containers as building blocks) | mid | drafted | — | — | [lesson](lessons/01-why-distributed-patterns.md) | — |
| 02  | The sidecar pattern | mid | drafted | — | — | [lesson](lessons/02-sidecar.md) | — |
| 03  | Ambassadors | mid | drafted | — | — | [lesson](lessons/03-ambassador.md) | — |
| 04  | Adapters | mid | drafted | — | — | [lesson](lessons/04-adapter.md) | — |
| 05  | Replicated load-balanced services | mid | drafted | — | — | [lesson](lessons/05-replicated-load-balanced.md) | — |
| 06  | Sharded services | senior | drafted | — | — | [lesson](lessons/06-sharded-services.md) | — |
| 07  | Scatter/gather | senior | drafted | — | — | [lesson](lessons/07-scatter-gather.md) | — |
| 08  | Functions and event-driven processing | mid | drafted | — | — | [lesson](lessons/08-functions-event-driven.md) | — |
| 09  | Ownership election (leader election) | senior | drafted | — | — | [lesson](lessons/09-ownership-election.md) | — |
| 10  | Work queue systems | mid | drafted | — | — | [lesson](lessons/10-work-queues.md) | — |
| 11  | Event-driven batch processing | senior | drafted | — | — | [lesson](lessons/11-event-driven-batch.md) | — |
| 12  | Coordinated batch processing | senior | drafted | — | — | [lesson](lessons/12-coordinated-batch.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** (e.g. `ddia/10`, `system-design/06`) are listed per
lesson in its front matter and named in prose.
