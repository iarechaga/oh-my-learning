---
id: system-design-interview/02
subject: system-design-interview
title: "Back-of-the-Envelope Estimation"
slug: back-of-the-envelope
status: drafted
mastery: 
seniority: junior
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 2"
prerequisites: [system-design-interview/01]
created: 2026-08-10
updated: 2026-08-10
---

# Back-of-the-Envelope Estimation

## TL;DR
Back-of-the-envelope estimation is the skill of turning a vague scale statement
("300 million users") into concrete numbers for queries-per-second, storage, memory,
and bandwidth, using round numbers and a handful of memorized latency/capacity facts.
It is not about precision — it is about getting within an order of magnitude fast
enough to decide "do we need a single server, a sharded database, or a CDN?" before
you've spent any real design time.

## The idea
A design choice like "should this data live in memory, on a single disk-backed
database, or sharded across 50 nodes?" is not a matter of taste — it's determined by
numbers. 1,000 users need almost nothing. 300 million active users writing a few times
a day needs careful sharding and caching. Without doing the arithmetic, a candidate (or
an engineer, on a real project) risks proposing an over-engineered system for small
scale or an under-engineered one that falls over immediately at real scale.

The skill is not being a fast mental-math wizard; it's knowing which quantities matter
(QPS, storage growth, bandwidth, memory) and having a few reference numbers memorized so
you can produce a plausible estimate in under two minutes, using round numbers
throughout so the arithmetic stays tractable.

## How it works

### The core quantities to estimate
For almost any system design problem, you want rough numbers for:
1. **Traffic** — queries per second (QPS), split into reads and writes, including peak
   vs. average.
2. **Storage** — how much data accumulates per day/year, and the total after N years.
3. **Bandwidth** — how much data moves in and out per second.
4. **Memory** — how much of the "hot" data could reasonably be cached.

### Step 1: Convert "users" into "requests"
You almost always start from a user count and a behavior assumption, then derive
traffic. Use round numbers and generous assumptions rather than looking up exact
figures — the interviewer wants to see the method, not a memorized statistic.

**Worked example — Twitter-scale tweet writes:**
- Assume 300 million monthly active users (MAU), and that ~50% are daily active users
  (DAU): 150 million DAU.
- Assume each DAU posts 2 tweets per day on average: 150M × 2 = 300 million tweets/day.
- Convert to QPS by dividing by the number of seconds in a day (round to 100,000 for
  easy math instead of 86,400):
  `300,000,000 / 100,000 = 3,000 QPS average write rate.`
- **Peak traffic is not average traffic.** A common rule of thumb is peak = 2x average
  (traffic is not evenly spread across 24 hours — it clusters around waking hours and
  events). Peak QPS ≈ 6,000.

**Worked example — read-heavy system (tweet views):**
- Reads are usually far more frequent than writes. Assume a 100:1 read:write ratio for
  a social feed (most users scroll far more than they post).
- Read QPS ≈ 3,000 × 100 = 300,000 QPS average, ~600,000 QPS at peak.

This read:write skew is the single most important number to nail down early, because it
determines whether the bottleneck is the write path (needs sharding, queueing) or the
read path (needs caching, read replicas, CDN).

### Step 2: Estimate storage
Multiply "items created per day" by "average size per item," then extrapolate to a
multi-year retention window.

**Worked example — storing tweets:**
- 300 million tweets/day (from above).
- Assume average tweet size ≈ 300 bytes of text/metadata (tweet ID, user ID, timestamp,
  text, a few flags).
- Daily storage: 300,000,000 × 300 bytes = 90,000,000,000 bytes ≈ 90 GB/day.
- Over 10 years: 90 GB × 365 × 10 ≈ 328,500 GB ≈ **328 TB** for text alone.
- Now add media. Assume 20% of tweets include an image averaging 200 KB:
  `300,000,000 × 0.20 × 200,000 bytes = 12,000,000,000,000 bytes = 12 TB/day.`
  Over 10 years that's **~43,800 TB (43.8 PB)** — two to three orders of magnitude more
  than the text data. This single calculation is why media almost always goes to a
  separate blob/object store (e.g., S3) with a CDN in front, never in the primary
  relational database.

### Step 3: Estimate bandwidth
Bandwidth (throughput) is storage-per-day converted to a rate, for both ingress
(uploads) and egress (downloads/reads).

**Worked example:**
- Ingress for tweet writes: 90 GB/day (text) + 12 TB/day (images) ≈ 12.1 TB/day.
  Divide by ~100,000 seconds/day: ≈ 121 MB/s average ingress. At 2x peak, ~242 MB/s.
- Egress is driven by reads. If each of the 300,000 average read QPS fetches a ~300-byte
  tweet: 300,000 × 300 bytes = 90 MB/s just for text — and image egress dominates far
  more heavily than image ingress, because each image is viewed by many more people
  than it's uploaded by, which is exactly the case for a CDN (see `system-design/06`
  and `system-design/10`) to absorb.

### Step 4: Estimate cache/memory needs
Caching typically targets the "hot" fraction of data — content accessed recently or
frequently — following something like an 80/20 rule.

**Worked example:**
- Assume 20% of daily tweet reads target content posted in roughly the last 24 hours (a
  reasonable assumption for a reverse-chronological or recency-weighted feed).
- If we want to cache the last day's tweets, that's about 90 GB (text) of hot data —
  small enough to fit comfortably in a modern cache cluster's memory (a single machine
  can have hundreds of GB of RAM; a distributed cache like Redis/Memcached scales this
  further, see `system-design/10`).
- This estimate directly answers a design question: "should we cache?" Yes — 90 GB is
  cheap to keep in memory relative to serving 300,000+ reads/sec from disk.

### Step 5: Sanity-check with reference numbers
A handful of memorized numbers make the above estimates possible without a calculator
and let you sanity-check an answer that "feels wrong":

| Quantity | Rough value |
| --- | --- |
| Seconds in a day | ~100,000 (actual: 86,400 — round up for easy division) |
| 1 KB | 10^3 bytes |
| 1 MB | 10^6 bytes |
| 1 GB | 10^9 bytes |
| 1 TB | 10^12 bytes |
| Reading 1 MB sequentially from disk (SSD) | ~1 ms |
| Reading 1 MB sequentially from memory | ~0.25 ms (roughly 4x faster than SSD) |
| Round trip within same data center | ~0.5 ms |
| Round trip cross-continent (e.g., US to Europe) | ~150 ms |
| A single well-provisioned relational DB server | can handle low thousands of QPS |
| A single cache node (Redis) | can handle tens of thousands of ops/sec |

These "latency numbers every engineer should know" (a phrase from the book, tracing to
an original list by Jeff Dean) matter because they let you reason about *where* the
bottleneck will actually appear — e.g., knowing memory reads beat disk reads by roughly
4x, and a cross-continent round trip is ~300x a same-datacenter one, immediately
explains why you'd put a cache in front of a database and a CDN edge node near the
user rather than serving every request from a single origin server.

### Common pitfall: skipping the round-number simplification
A candidate who insists on 86,400 seconds/day, or exact byte counts, will burn interview
time on arithmetic instead of design. The whole point of "back of the envelope" is
approximation: 100,000 seconds/day, powers of 10 for byte units, and "2x average for
peak" as a default multiplier unless told otherwise. State your assumptions explicitly
("I'll assume peak is roughly double the average, and round a day to 100,000 seconds")
so the interviewer can correct them if the real system has a different profile (e.g., a
system with a strong daily spike, like a ticket-sale flash sale, might have peak:average
of 50:1 or more).

## Pros
- **Fast** — a full traffic/storage/bandwidth estimate takes 2-5 minutes with round
  numbers, versus getting bogged down in precise arithmetic.
- **Drives concrete design decisions** — "do we need sharding," "do we need a CDN," "do
  we need a cache" all fall directly out of these numbers instead of being guessed.
- **Transfers directly to real engineering** — capacity planning, choosing instance
  sizes, and setting SLOs all use the same technique.

## Cons
- **Easy to get an assumption wrong and compound the error** — e.g., assuming a 1:1
  read:write ratio when it's actually 100:1 changes every downstream number by two
  orders of magnitude. Always state assumptions aloud so they can be checked.
- **Order-of-magnitude only** — not a substitute for real load testing or production
  metrics; it tells you whether to worry, not the exact instance count you'll need.
- **Can be over-invested in** — spending 15 minutes perfecting an estimate instead of
  moving to the design itself defeats the purpose (see `system-design-interview/01`'s
  time budget).

## Alternatives
- **Skipping estimation and designing "for scale" by default** — always assuming you
  need sharding, multi-region replication, and a message queue regardless of actual
  numbers. This is a real interview red flag: it signals pattern-matching rather than
  reasoning, and a good interviewer will ask "why do you need that at this scale?" and
  expose the gap.
- **Asking the interviewer for exact numbers instead of estimating** — sometimes
  reasonable for one or two key facts (e.g., "is this closer to Twitter-scale or a
  niche 10k-user app?"), but repeatedly asking for numbers you could reasonably assume
  yourself wastes the interviewer's patience and doesn't demonstrate the estimation
  skill being tested.
- **Precise capacity planning tools/spreadsheets** — the real-world equivalent (e.g., a
  formal capacity model with measured p99s and load-test data) is more accurate but far
  too slow for a live interview; back-of-envelope is the appropriate fidelity for a
  45-minute conversation.

## When to use it
Use it early in every system design interview, right after scoping (Step 1 of the
framework in `system-design-interview/01`), to decide the shape of the system before
you commit to specific components. Use it again mid-interview whenever a design
decision hinges on scale ("would a single Postgres instance handle this, or do we need
to shard?").

## When NOT to use it
Don't reach for elaborate estimation when the interviewer has explicitly said scale
doesn't matter for this question (e.g., "assume infinite scale, focus on the
algorithm"), or when the problem is inherently about correctness/logic rather than
capacity (e.g., "design the state machine for a traffic light controller"). Also avoid
spending disproportionate time chasing precision the conversation doesn't need — two
minutes of estimation that produces "we're in the low thousands of QPS, reads dominate
writes 100:1" is more valuable than ten minutes that produces a more "precise" number
with no time left to design around it.

## Key takeaways / mental model
Think of back-of-the-envelope estimation as a compass, not a map: it tells you which
direction to walk (cache vs. no cache, shard vs. single node, CDN vs. direct serving),
not the exact coordinates. The workflow is always the same shape: users → behavior
assumption → requests/day → QPS (divide by ~100,000) → peak QPS (×2) → storage
(items/day × size, extrapolated over years) → bandwidth (storage/day as a rate) →
memory (hot fraction of storage). Memorize a handful of latency/throughput reference
numbers so you can sanity-check results instead of deriving everything from scratch.

## Self-check questions
1. Given 500 million MAU, 40% DAU, and 5 photo uploads/day per DAU averaging 2 MB each,
   estimate the average write QPS, peak write QPS (assume 2x), and storage growth per
   day. Round aggressively.
2. Why does the read:write ratio matter more, in terms of design impact, than getting
   the exact average tweet size correct?
3. A system stores 50 GB of "hot" data accessed in the last 24 hours. Would you put
   this behind a cache? Why does the answer depend on typical single-node memory
   capacity?
4. You calculate 900,000 QPS at peak for reads. A single database server tops out
   around a few thousand QPS. What does this gap tell you about the design, before
   you've drawn anything?
5. Why is "round to 100,000 seconds/day" a defensible simplification in an interview,
   and when would a real production capacity plan need the exact 86,400?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 2
