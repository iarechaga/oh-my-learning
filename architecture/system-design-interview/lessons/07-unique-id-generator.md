---
id: system-design-interview/07
subject: system-design-interview
title: "Design a Unique ID Generator"
slug: unique-id-generator
status: drafted
mastery: 
seniority: mid
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 7"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03]
created: 2026-08-10
updated: 2026-08-10
---

# Design a Unique ID Generator

## TL;DR
Generating unique IDs across a fleet of distributed servers rules out simple
auto-increment (a single point of contention and failure). The standard interview
answer is a Twitter-Snowflake-style scheme: a 64-bit integer packed with a timestamp,
a machine/worker ID, and a per-millisecond sequence number, so every server can mint
IDs independently, roughly sortable by time, with no coordination needed per-request.

## The idea
A single relational database's auto-increment primary key is easy — but it only works
because there's exactly one writer deciding the next number. The moment you shard the
database or run multiple independent services that each need to assign IDs (e.g., a
sharded key-value store, or multiple API servers each handling writes), you need a way
to hand out IDs that are guaranteed unique *without* every server having to check in
with a central authority for every single ID (that would reintroduce the single point
of contention you were trying to eliminate by sharding).

The interview question is really asking: how do you get uniqueness, reasonable
ordering, and high throughput, all without coordination on the hot path?

## How it works

### Step 1: Clarify requirements
- **Must IDs be numeric, and must they fit a specific size?** (Assume: 64-bit integer —
  fits comfortably in a `bigint` column and is more compact/index-friendly than a
  string UUID.)
- **Do IDs need to be roughly sortable by creation time?** This matters a lot for
  systems like a news feed or chat app where "newest first" ordering by ID avoids a
  separate timestamp sort. (Assume: yes.)
- **Scale.** How many IDs per second across the whole fleet? (Assume: 10,000/sec
  system-wide, well within what a bit-packed scheme handles easily — see below.)

### Step 2: Why the obvious approaches don't work at scale
- **Single database auto-increment.** One writer, one point of failure/contention;
  doesn't scale past what a single database can handle, and breaks entirely if you
  shard the database (each shard would independently restart its own sequence,
  producing duplicate IDs across shards).
- **UUID (e.g., UUIDv4, 128-bit random).** Solves uniqueness with no coordination
  (collision probability is astronomically low), but is not time-sortable, is twice
  the size of a 64-bit integer (more index/storage overhead at scale — recall from
  `system-design-interview/02` how storage multipliers compound), and as a random
  value causes poor database index locality (new rows insert at random positions in a
  B-tree index rather than appending at the end, which is slower for many storage
  engines).
- **A central "ticket server."** A single service hands out blocks of IDs on request
  (e.g., "give me the next 1,000 IDs"). Reduces coordination frequency but reintroduces
  a single point of failure/scaling ceiling, and needs careful handling if the server
  crashes after handing out a block but before any of it is used (those IDs are
  "burned" — acceptable for most uses, since gaps in an ID sequence are usually fine,
  just not duplicates).

### Step 3: High-level design — the Snowflake approach
Pack a 64-bit integer into fields that let each server generate IDs independently:

```
 1 bit        41 bits                    10 bits        12 bits
+------+-----------------------+-------------------+---------------+
| sign | timestamp (ms since   | machine/worker ID | sequence      |
| (0)  | a custom epoch)       | (datacenter+worker)| number        |
+------+-----------------------+-------------------+---------------+
```

- **Sign bit (1 bit):** always 0, keeping the value a positive 64-bit integer (avoids
  sign-related bugs in languages/DBs that treat the top bit specially).
- **Timestamp (41 bits):** milliseconds since a custom epoch (e.g., the system's
  launch date, not the Unix epoch — this matters, see the worked example below).
  41 bits gives `2^41 ≈ 2.2 trillion` milliseconds, or about **69 years** of range from
  the chosen epoch.
- **Machine/worker ID (10 bits):** identifies which server minted this ID.
  `2^10 = 1024` possible machine IDs — enough for a large fleet, and often split into a
  datacenter ID (e.g., 5 bits) and a worker ID within that datacenter (5 bits) for
  operational clarity.
- **Sequence number (12 bits):** a per-machine, per-millisecond counter that
  increments for each ID minted within the same millisecond on the same machine, reset
  to 0 at the next millisecond. `2^12 = 4096` possible values, meaning each machine can
  mint up to 4,096 IDs per millisecond = **4.096 million IDs/second per machine**.

**Worked example — why the custom epoch matters:** if you used the Unix epoch
(1970-01-01), by the time this design ships (say, 2026), you'd already have burned
roughly 56 years of the 69-year budget just getting to today, leaving only ~13 years of
headroom. Using a custom epoch set to (say) the company's founding date or launch date
resets the clock, buying back the full ~69 years from a meaningful starting point —
this is a detail worth stating explicitly in an interview because it shows you
understand *why* the field is sized the way it is, not just that it exists.

**Worked example — generating IDs.** Suppose worker ID = 5, custom epoch = 2020-01-01
00:00:00 UTC, and the current time is 100 milliseconds after that epoch.
- First ID this millisecond: sequence = 0. ID components: `timestamp=100,
  worker=5, sequence=0`.
- A second request arrives in the same millisecond: sequence increments to 1. ID
  components: `timestamp=100, worker=5, sequence=1`.
- A third request arrives one millisecond later (timestamp=101): sequence resets to 0.
  ID components: `timestamp=101, worker=5, sequence=0`.

Because `timestamp` occupies the highest bits (after the sign bit), IDs are naturally
increasing over time even across machines — comparing two Snowflake IDs numerically
tells you which was minted earlier (down to millisecond resolution; within the same
millisecond, ordering across different machines is not meaningful, only ordering within
the same machine's sequence is exact).

### Step 4: Deep dive — clock skew and clock rollback
Because the scheme depends on wall-clock time, a machine's system clock going
**backwards** (e.g., due to NTP correction) is a real hazard: if the clock jumps back
after minting ID with timestamp=200, and then mints a new ID at the corrected
timestamp=195, that new ID could numerically collide with (or worse, fall behind) an ID
already minted at timestamp=195 with a different sequence — breaking both uniqueness
guarantees and the sortable-by-time property.

**Mitigation:** on ID generation, compare the current clock reading to the
last-used timestamp on that machine. If the current reading is *earlier* than the
last-used timestamp, the machine detects clock rollback and either (a) refuses to
generate IDs until the clock catches back up (safest, but causes a brief availability
gap on that machine), or (b) falls back to a small in-memory offset to keep moving
forward artificially until the real clock catches up. Production systems typically
choose (a) for a short bounded wait, since NTP corrections are normally small
(milliseconds), and treat large clock jumps as an alerting/operational event rather
than something to silently paper over.

### Step 5: Deep dive — assigning machine/worker IDs
The 10-bit machine ID must be unique per running instance, which itself needs
coordination — but only at process startup, not per-request, so it doesn't reintroduce
a hot-path bottleneck. Common approaches:
- **A coordination service (ZooKeeper/etcd).** Each worker registers and claims an
  unused ID slot on startup; releases it on graceful shutdown. Handles the "what if two
  workers grab the same ID" race correctly via the coordination service's atomic
  operations.
- **Static configuration.** In a smaller, more controlled fleet (e.g., a fixed number
  of Kubernetes StatefulSet pods with stable ordinal identities), the machine ID can be
  derived directly from the pod's stable identity (e.g., pod-3 → worker ID 3),
  avoiding a coordination service entirely.

### Step 6: Wrap-up — throughput and headroom check
Back-of-the-envelope: with 4.096M IDs/sec/machine and a system-wide requirement of only
10,000 IDs/sec (from Step 1), a single machine has enormous headroom — throughput was
never the binding constraint here; uniqueness-without-coordination was. This is worth
saying explicitly in an interview: it shows you're checking your design against the
numbers, not just building for its own sake.

## Pros
- No coordination needed on the hot path — each machine mints IDs independently once
  it has a machine ID.
- Roughly time-sortable, which many downstream systems (feeds, logs, pagination)
  benefit from directly.
- Compact (64-bit integer vs. 128-bit UUID), which matters for index size and storage
  at scale.

## Cons
- Depends on synchronized clocks; clock skew/rollback is a real operational hazard that
  needs explicit handling.
- Only sortable at millisecond granularity and only strictly ordered within a single
  machine — cross-machine ordering within the same millisecond is not guaranteed.
- Machine ID assignment/coordination, while infrequent, is still an operational
  dependency (or a constraint on deployment topology if using static IDs).

## Alternatives
- **UUID (v4, random)** — zero coordination of any kind, extremely simple, but not
  sortable and worse for index locality; fine when ordering doesn't matter and IDs are
  opaque to the application (e.g., an internal tracing ID).
- **Database ticket server (range allocation)** — simpler to reason about than bit
  packing, but reintroduces a scaling ceiling and a single point of failure at very
  high ID-issuance rates.
- **ULID / KSUID** — alternative time-sortable ID formats (128-bit, encoding
  millisecond timestamp plus randomness) that trade some of Snowflake's compactness for
  simpler generation (no machine ID coordination needed, since the random component is
  large enough to make collisions negligible without registering worker IDs).

## When to use it
Any system that shards writes across multiple database instances or app servers and
needs primary keys, message IDs, or event IDs that are unique fleet-wide and roughly
time-ordered without a central bottleneck: chat message IDs, feed post IDs, distributed
tracing/event IDs.

## When NOT to use it
If the system has a single writer (a non-sharded database), just use that database's
native auto-increment — it's simpler and Snowflake's complexity buys nothing. Also
skip it when ordering truly doesn't matter and coordination-free simplicity is the only
goal — a random UUID is simpler to implement and reason about.

## Key takeaways / mental model
Think of a Snowflake ID as three facts glued together in one number: "roughly when"
(timestamp, the high bits, dominating the sort order), "on which machine" (worker ID,
assigned once at startup, not per-request), and "which one on that machine, this
millisecond" (sequence, the only field that needs a tiny bit of local, non-distributed
coordination — an in-process counter). Nothing here requires talking to any other
machine at ID-generation time; the machine ID assignment is the only step that ever
needed coordination, and it happens rarely.

## Self-check questions
1. Why does a plain database auto-increment ID fail once you shard the database across
   multiple instances?
2. Using a custom epoch instead of the Unix epoch for the timestamp field only matters
   because of which specific bit-width constraint?
3. A machine's clock jumps backward by 50ms due to an NTP correction. What specifically
   breaks if the ID generator does nothing about it, and what's one way to guard
   against it?
4. With a 12-bit sequence field, what is the maximum IDs/sec a single machine can mint,
   and why does exceeding it within the same millisecond require waiting for the next
   millisecond rather than wrapping the sequence around?
5. Why is UUIDv4 a legitimate alternative for some systems despite not being
   time-sortable, and what workload characteristic would make you choose it over
   Snowflake-style IDs?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 7
- Twitter's Snowflake ID scheme (the original design this chapter is based on).
