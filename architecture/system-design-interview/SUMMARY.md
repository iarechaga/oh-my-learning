# System Design Interview - Subject Summary

A comprehensive recap of the interview-practice subject, concept by concept. This
subject reuses the same building blocks as the System Design subject (load balancing,
caching, sharding, queues) but organizes them around a repeatable four-step interview
method - clarify requirements, estimate scale, sketch a high-level design, then deep
dive - applied to a progression of worked case studies.

**Source book:** *System Design Interview - An Insider's Guide, Vol. 1* - Alex Xu
(ByteByteGo / independently published, 2020).

**Progress note:** all 15 lessons are `drafted`; none discussed yet, so mastery is
pending and no weak spots are recorded. See the table in [README.md](README.md).
Reading order is top to bottom (dependency-ordered): the framework and estimation
skills first, then progressively harder case studies.

## Foundations

- **[01] A framework for system design interviews** - the interview is a simulation of
  collaborating on ambiguity, not a trivia test. Four-step loop: clarify scope (~5
  min), high-level design (~10 min), deep dive (~15-20 min), wrap-up (~5 min). Failure
  modes are almost always about time budget and communication, not knowledge gaps.
  ([lesson](lessons/01-interview-framework.md))
- **[02] Back-of-the-envelope estimation** - convert a user count into QPS, storage,
  bandwidth, and memory using round numbers (100,000 seconds/day, 2x average for peak).
  The read:write ratio is the single most consequential number - it determines whether
  the bottleneck is the write path or the read path. ([lesson](lessons/02-back-of-the-envelope.md))
- **[03] Scaling from zero to millions of users** - the canonical growth sequence: one
  server -> separate app/DB -> load balancer + horizontal app tier -> DB replication ->
  cache -> CDN -> stateless multi-region -> message queue -> sharding. Each stage is
  triggered by a specific, nameable bottleneck, not fashion; stop at the stage your own
  numbers justify. ([lesson](lessons/03-scaling-zero-to-millions.md))

## Core case studies (infrastructure building blocks)

- **[04] Design a rate limiter** - token bucket (allows bursts up to capacity, steady
  refill rate) is the default algorithm; sliding window counter is the memory-cheap
  approximation of sliding window log. The hard part is making the shared counter
  correct and fast across multiple servers (atomic ops on Redis), not picking the
  algorithm. ([lesson](lessons/04-rate-limiter.md))
- **[05] Design consistent hashing** - naive `hash(key) % N` moves ~`N/(N+1)` of keys
  on every resize; a hash ring bounds this to ~`1/N`. Virtual nodes fix the ring's own
  uneven-load problem and let heterogeneous-capacity servers take a proportional share.
  Retold here fully self-contained from the interview angle; parallels
  `system-design/04`. ([lesson](lessons/05-consistent-hashing.md))
- **[06] Design a key-value store** - a Dynamo-style AP design: consistent hashing for
  partitioning, N/W/R quorum tuning for per-operation consistency/availability
  trade-offs, vector clocks to detect genuinely concurrent (vs. causally ordered)
  writes, and gossip + hinted handoff + Merkle-tree anti-entropy for failure handling.
  The senior-band deep dive is entirely about what happens when the network misbehaves.
  ([lesson](lessons/06-key-value-store.md))
- **[07] Design a unique ID generator** - Snowflake-style 64-bit IDs (sign bit +
  41-bit timestamp + 10-bit machine ID + 12-bit sequence) mint IDs with zero
  per-request coordination, roughly time-sortable. Clock rollback is the main
  operational hazard. ([lesson](lessons/07-unique-id-generator.md))

## Applied case studies (product-shaped systems)

- **[08] Design a URL shortener** - the whole design reduces to one question: how to
  generate a unique short code without collisions. Base-62-encoding a unique counter
  avoids collision-checking entirely (unlike hash-and-truncate), at the cost of losing
  "same URL -> same code" idempotency unless explicitly required. A good first practice
  problem - small but exercises the full framework. ([lesson](lessons/08-url-shortener.md))
- **[09] Design a web crawler** - a two-tier URL frontier (priority queues for crawl
  order + per-host politeness queues for rate limiting) solves both "what to crawl
  next" and "don't overwhelm one host." Bloom filters make URL-seen tracking affordable
  at web scale (~98% memory reduction vs. storing raw URL strings). Spider traps and
  malformed content require explicit robustness handling. ([lesson](lessons/09-web-crawler.md))
- **[10] Design a notification system** - decouple triggering from delivery via a
  message queue so a slow third-party push/SMS/email provider never blocks the
  triggering service. At-least-once delivery plus an idempotency-key dedup layer is the
  realistic guarantee; per-user rate limiting and per-channel worker pools round out the
  design. ([lesson](lessons/10-notification-system.md))

## Senior-band systems (heavy-tailed and stateful workloads)

- **[11] Design a news feed system** - fan-out-on-write (cheap reads, breaks on
  celebrity write amplification) vs. fan-out-on-read (cheap writes, expensive
  aggregation on every read) vs. the hybrid (push for regular accounts, pull for
  celebrities above a tunable follower threshold). The general pattern - a uniform
  strategy breaks on a heavy-tailed outlier - recurs across many designs.
  ([lesson](lessons/11-news-feed.md))
- **[12] Design a chat system** - chat is push, not poll, so WebSockets replace
  stateless HTTP, which breaks the usual "any load-balanced instance can serve any
  request" assumption. A connection registry (user -> server) becomes the load-bearing
  component for message routing, presence, and reconnect handling alike. Time-sortable
  message IDs solve ordering; idempotency keys solve at-least-once dedup.
  ([lesson](lessons/12-chat-system.md))
- **[13] Design a search autocomplete system** - precompute top-K completions per trie
  node in an offline batch job so the online serving path is a pure O(prefix-length)
  memory lookup with zero live ranking, hitting a sub-100ms budget at very high QPS.
  Freshness trades against this - a genuinely new trending query waits for the next
  rebuild unless a delta-overlay layer is added. ([lesson](lessons/13-search-autocomplete.md))
- **[14] Design YouTube (video platform)** - the hard problems are almost entirely on
  the upload/processing side: chunked, parallel, DAG-based transcoding turns a slow
  serial operation into one completing in a fraction of the video's runtime; adaptive
  bitrate streaming lets each viewer's client pick the best pre-encoded resolution
  variant for current network conditions. Storage/bandwidth needs are 4-5 orders of
  magnitude larger than any other case study in this subject. ([lesson](lessons/14-youtube.md))
- **[15] Design Google Drive** - three problems, one mechanism (content-hashed fixed-
  size blocks): block-level diffing minimizes sync bandwidth, content-addressable
  storage deduplicates identical blocks across users (a major cost lever at exabyte
  scale), and version-parent tracking detects concurrent edits, which are resolved by
  keeping both as a "conflicted copy" rather than silently auto-merging or discarding
  one. Explicitly excludes live co-editing (see `system-design/18`).
  ([lesson](lessons/15-google-drive.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on concepts rated
`shaky` or `not-yet`.
