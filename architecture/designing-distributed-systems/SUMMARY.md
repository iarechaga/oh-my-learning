# Designing Distributed Systems - Subject Summary

A comprehensive recap of *Designing Distributed Systems* (Brendan Burns), concept by
concept.

**Progress note:** all 12 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded. This summary will gain depth
(especially on the concepts you find hard) as discussions happen - the "Focus areas"
section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered): single-node patterns first, then multi-node serving patterns, then
batch computational patterns. **Seniority baseline:** mid-senior (lessons range
mid->senior). The subject is framed around containers and orchestration (Kubernetes) as
the building blocks you compose.

## Single-node patterns

- **[designing-distributed-systems/01] Why distributed patterns (containers as building
  blocks)** (mid) - the premise: containers are the reusable, boundaried building blocks
  that let distributed systems be assembled from standard patterns rather than
  hand-built each time, the same way objects and libraries did for single-process code.
  Sets up the single-node vs multi-node pattern taxonomy.
  ([lesson](lessons/01-why-distributed-patterns.md))
- **[designing-distributed-systems/02] The sidecar pattern** (mid) - a helper container
  colocated in the same pod as the application container, extending or enhancing it
  (logging, proxying, config sync) without changing the app. The canonical single-node,
  multi-container pattern. ([lesson](lessons/02-sidecar.md))
- **[designing-distributed-systems/03] Ambassadors** (mid) - a sidecar that brokers the
  application's *outbound* connections to the outside world (sharding a client, service
  discovery, request routing), so the app talks to a simple local proxy and the
  ambassador handles the complexity. ([lesson](lessons/03-ambassador.md))
- **[designing-distributed-systems/04] Adapters** (mid) - a sidecar that adapts the
  application's *outward-facing* interface to a common standard (uniform metrics, logs,
  health checks) so heterogeneous apps present a consistent surface to the platform.
  ([lesson](lessons/04-adapter.md))

## Multi-node serving patterns

- **[designing-distributed-systems/05] Replicated load-balanced services** (mid) - run
  many identical stateless replicas behind a load balancer to scale the number of
  *requests* and provide availability; covers readiness/health checks and session
  stickiness. The baseline multi-node serving pattern.
  ([lesson](lessons/05-replicated-load-balanced.md))
- **[designing-distributed-systems/06] Sharded services** (senior) - when the *data/state*
  is too big or too hot for one replica, split it into **shards** so each replica owns a
  slice, adding a sharding function and a routing layer. Replication scales requests;
  sharding scales data - real systems do both. ([lesson](lessons/06-sharded-services.md))
- **[designing-distributed-systems/07] Scatter/gather** (senior) - parallelize a *single*
  request by fanning it out to many leaf servers that each process a slice, then merging
  their partial results. Scales the work inside one request; its defining weakness is the
  **straggler** - latency is set by the slowest leaf, so you fight tail latency.
  ([lesson](lessons/07-scatter-gather.md))
- **[designing-distributed-systems/08] Functions and event-driven processing** (mid) -
  FaaS/serverless for gluing systems together with short-lived, event-triggered
  functions; when it fits (event glue, spiky/low-traffic work) and its costs (cold
  starts, state, cost model at scale). ([lesson](lessons/08-functions-event-driven.md))
- **[designing-distributed-systems/09] Ownership election (leader election)** (senior) -
  when exactly one replica must own a responsibility (one writer/scheduler/lock holder)
  despite running several for availability. The whole difficulty is the word *exactly* -
  guaranteeing never-two-at-once across failures forces reliance on a consensus system
  rather than home-grown logic. ([lesson](lessons/09-ownership-election.md))

## Batch computational patterns

- **[designing-distributed-systems/10] Work queue systems** (mid) - the simplest batch
  pattern: a pile of independent tasks pulled by a pool of workers, scaling throughput by
  adding workers. Covers the generic container-based work-queue API and at-least-once
  delivery/idempotency. ([lesson](lessons/10-work-queues.md))
- **[designing-distributed-systems/11] Event-driven batch processing** (senior) - compose
  work-queue-style *stages* into a pipeline wired by events, using functional patterns
  (copier, filter, splitter, sharder, merge/join) with no central coordinator. Power is
  loose coupling and per-stage scaling; the difficulty is ordering, duplicates, and "did
  the whole pipeline finish?" ([lesson](lessons/11-event-driven-batch.md))
- **[designing-distributed-systems/12] Coordinated batch processing** (senior) - adds the
  structure event-driven pipelines lack: a coordinator, explicit stage boundaries, and
  **barriers** that hold the next stage until the previous fully completes - enabling
  reductions across the whole dataset and guaranteed completion. The classic realization
  is MapReduce (map -> shuffle barrier -> reduce); the cost is coordination overhead and
  barrier stragglers. ([lesson](lessons/12-coordinated-batch.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak spots
and misconceptions will be aggregated here, with extra detail on the concepts rated
`shaky` or `not-yet`. (Likely candidates for depth once discussed: the
replication-vs-sharding-vs-scatter/gather distinction (05-07), leader election's
exactly-one guarantee (09), and event-driven vs coordinated batch (11-12).)
