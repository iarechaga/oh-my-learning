---
id: system-design-interview/08
subject: system-design-interview
title: "Design a URL Shortener"
slug: url-shortener
status: drafted
mastery: 
seniority: junior
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 8"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03]
created: 2026-08-10
updated: 2026-08-10
---

# Design a URL Shortener

## TL;DR
A URL shortener (like bit.ly or TinyURL) maps a long URL to a short, unique alias and
redirects visitors from the alias back to the original. The whole design hinges on one
decision — how to generate the short code — and the interview walkthrough below covers
base-62 encoding of a counter as the clean solution, plus the read-heavy caching and
redirect-performance considerations that make this a good entry-level "design X"
question.

## The idea
This is often the very first "design X" problem given in interviews because its scope
is small and well-bounded, but it still touches the full framework: requirements
clarification, an API, a data model, a high-level architecture, and one genuinely
interesting deep-dive question (how do you generate a short, unique code for a
combinatorially huge space of possible long URLs?).

## How it works

### Step 1: Clarify requirements
- **Functional:** given a long URL, generate a unique short URL; given a short URL,
  redirect to the original long URL. (Assume: also support optional custom aliases and
  optional expiration.)
- **Non-functional:** high availability, low redirect latency (this is on the critical
  path of a user's click — should feel instant), and the system is heavily read-skewed
  (many more redirects than URL creations).
- **Scale.** Assume 100 million new short URLs created per month, and a 100:1
  read:write ratio (redirects vastly outnumber creations, matching typical link-sharing
  behavior).

### Step 2: Back-of-the-envelope
- Writes: `100,000,000 / (30 × 100,000 seconds/day) ≈ 33 URLs/sec average` — trivially
  low write volume (recall the method from `system-design-interview/02`: divide by
  ~100,000 seconds/day).
- Reads: at 100:1, that's ~3,300 redirects/sec average, ~6,600/sec at peak (2x
  average) — comfortably handled by caching, per Step 5 below.
- Storage: assume each record (short code, long URL, metadata) is ~500 bytes. Over 5
  years: `100M/month × 12 × 5 × 500 bytes ≈ 6,000,000,000 × 500 bytes = 3 TB` — modest,
  fits easily on a handful of database nodes, no sharding strictly required at this
  scale, though it's worth mentioning as a future step.
- Short code length: how many unique codes do we need? To cover 6 billion URLs (5-year
  total from above) with headroom, using base-62 (a-z, A-Z, 0-9 = 62 characters):
  `62^6 ≈ 56.8 billion` — a 6-character code comfortably covers the 5-year volume with
  headroom to spare; `62^7 ≈ 3.5 trillion` if you want decades of runway.

### Step 3: API design
```
POST /api/v1/urls           { long_url, custom_alias?, expiration? } -> { short_url }
GET  /{short_code}          -> HTTP 301/302 redirect to long_url
```

**301 vs. 302:** a 301 (permanent redirect) lets browsers cache the redirect, reducing
load on the service for repeat visits to the same short link — good for reducing
server load. A 302 (temporary redirect) forces the browser to hit the service every
time, which costs more but lets you track every single click (useful if the product
needs click analytics) and lets you change the mapping later. This is a genuine
product trade-off to surface explicitly rather than silently picking one.

### Step 4: Data model
A simple table is enough — no need for a relational schema with joins:

| Column | Type | Notes |
| --- | --- | --- |
| `short_code` | string (PK) | 6-7 chars, base-62 |
| `long_url` | string | the original URL |
| `created_at` | timestamp | |
| `expires_at` | timestamp, nullable | |
| `user_id` | nullable | if creation requires an account |

Given the simple key-based access pattern (fetch by `short_code`, no joins, no complex
queries) and the read-heavy, high-scale profile, a key-value store (see
`system-design-interview/06`) is a reasonable choice, though a sharded relational table
works too at this actual scale (3 TB, low write volume) — worth noting in the interview
that the "correct" database choice here is less important than demonstrating you
understand the trade-off.

### Step 5: High-level design
```
[Client] --> [LB] --> [App Servers] --> [Cache] --(miss)--> [Database]
                            |
                     (write path: generate
                      unique short_code)
```

Reads dominate (100:1), so a cache in front of the database (cache-aside, as covered in
`system-design-interview/03`) absorbs the vast majority of redirect traffic — recall
that memory access (~0.25 ms/MB) beats disk (~1 ms/MB), and every millisecond matters
on a redirect that's meant to feel instantaneous to the user.

### Step 6: Deep dive — generating the short code
This is the one genuinely interesting design decision in this problem, and where the
interview signal concentrates.

**Approach A: Hash + truncate.** Hash the long URL (e.g., MD5) and take the first 6-7
characters of the base-62-encoded hash.
- *Problem — collisions.* Two different long URLs can truncate to the same short code.
  With a 6-character space of ~56.8 billion values and, say, 6 billion URLs stored (the
  5-year estimate from Step 2), the birthday-paradox collision probability is
  non-trivial — you cannot just assume it won't happen. You need a collision-check
  step: on generation, check if the code already exists; if so, append a fixed salt (or
  retry with a different substring/offset) and re-hash. This adds a database read (and
  possibly a retry loop) on every write, which is acceptable given writes are only
  ~33/sec.
- *Benefit* — same long URL always maps to the same short code (unless you want each
  submission to get a fresh code, which is itself a requirements question to clarify:
  should re-shortening the same URL return the existing short code, or mint a new one?).

**Approach B: Base-62 encode a unique counter (the book's recommended default).** Use a
globally unique, monotonically increasing ID — generated via the unique ID generator
pattern from `system-design-interview/07`, or a simple auto-increment if a single
database is sufficient at this scale — and base-62-encode it directly into the short
code.

*Worked example:* counter value `125,412,584`.
- Repeatedly divide by 62 and map the remainder to a base-62 character
  (`0-9`→0-9, `A-Z`→10-35, `a-z`→36-61):
  `125,412,584 = 2,022,783 × 62 + 38` → last char = base62[38] = `'c'`
  `2,022,783 = 32,625 × 62 + 33` → next char = base62[33] = `'X'`
  `32,625 = 526 × 62 + 13` → next char = base62[13] = `'D'`
  `526 = 8 × 62 + 30` → next char = base62[30] = `'U'`
  `8 = 0 × 62 + 8` → next char = base62[8] = `'8'`
  Reading remainders in reverse order: `8UDXc`.
- No collision check needed by construction — each counter value is unique, so each
  encoded short code is unique. This is a meaningful simplification over Approach A:
  no retry loop, no collision-probability math to defend.

**Why the book prefers Approach B:** it trades "same URL always gets the same short
code" (a nice-to-have, not a requirement unless explicitly asked for) for a simpler,
collision-free generation path with no extra database read on the write path. If the
requirement *does* include deduplication (re-shortening the same URL returns the same
code), add a secondary lookup (long_url → short_code) as a separate index/cache, which
is an explicit extra cost worth calling out rather than silently bolting on.

### Step 7: Deep dive — the unique counter at scale
Approach B needs a source of unique, non-repeating counter values across potentially
many app servers. Options, cheapest to most complex:
- **Single database auto-increment**, fine at 33 writes/sec — far below what a single
  database can handle.
- **Pre-allocated ID ranges**: each app server checks out a block of, say, 1,000 IDs
  from a central counter at once, then hands them out locally without a database
  round-trip per request — reduces database load further, at the cost of some IDs being
  "wasted" if a server crashes mid-block (acceptable, since gaps are harmless here).
- **Snowflake-style distributed ID generation** (`system-design-interview/07`) if the
  system later shards its database and needs coordination-free ID minting across many
  writers.

### Step 8: Wrap-up
Mention: rate limiting URL creation to prevent abuse (`system-design-interview/04`),
handling expired links (a background job or lazy check-on-read that deletes/ignores
expired entries), and analytics (if click tracking is wanted, a message queue can
capture each redirect event asynchronously without slowing down the redirect itself).

## Pros
- Small, well-scoped problem that still exercises the full framework end-to-end —
  useful both as an interview warm-up and as a genuinely useful piece of
  infrastructure.
- The counter+base-62 approach avoids collision handling entirely, simplifying the
  write path.
- Naturally read-heavy, which makes the caching story clean and the design's
  bottleneck obvious.

## Cons
- The counter approach requires a coordinated unique-ID source, which is minor
  extra infrastructure for what looks like a simple problem.
- Short codes generated sequentially from a counter are guessable/enumerable (an
  attacker can iterate through codes) unless deliberately randomized or access-controlled
  — a real security consideration worth mentioning.
- Custom aliases (a common real product feature) reintroduce collision-checking even
  if the default path avoids it.

## Alternatives
- **Hash + truncate with collision retry (Approach A above)** — gives idempotent
  mapping (same URL → same code) at the cost of collision handling complexity.
- **Random string generation with existence check** — generate a random 6-7 character
  string, check if it's taken, retry on collision. Simple to reason about but adds an
  unpredictable number of database round-trips per write as the namespace fills up.
- **Third-party/managed short-link services** — for many real products, not worth
  building in-house at all; use an existing provider unless short-link generation is a
  core product differentiator.

## When to use it
Any product needing shareable short links: social media post links, SMS/marketing
campaigns, QR codes. Also a strong first practice problem for someone new to system
design interviews, since it's small enough to fully complete in 45 minutes while still
covering the whole framework.

## When NOT to use it
Don't over-engineer this for a use case that doesn't need dynamic short-link creation
at scale — a small internal tool with a few hundred links doesn't need a distributed ID
generator or a cache tier; a single database table is enough (know your own numbers,
per `system-design-interview/02`, before adding infrastructure).

## Key takeaways / mental model
The entire design collapses to one central question: how do you turn "an arbitrarily
large space of long URLs" into "a small, unique, dense short code" without collisions
and without a bottleneck on the write path? Base-62-encoding a unique counter answers
that cleanly — uniqueness is guaranteed by construction (the counter never repeats),
and the encoding is just a change of base, not a hash, so there's nothing to collide.
Everything else in the design (caching, redirect codes, rate limiting) is standard
read-heavy-system plumbing you'd reach for regardless of the specific product.

## Self-check questions
1. Why does base-62-encoding a unique counter avoid the collision-checking problem that
   hashing the long URL and truncating does not?
2. Walk through base-62-encoding the counter value `238,328` by hand (divide-and-
   remainder method) to produce its short code.
3. What's the functional difference between a 301 and a 302 redirect for this system,
   and why might a product team prefer one over the other?
4. Given 100M new URLs/month and a desired 5-year runway, why is a 6-character base-62
   code (62^6 ≈ 56.8 billion combinations) sufficient, and when would you need 7
   characters instead?
5. If a requirement changes to "re-shortening the same long URL must always return the
   same short code," what does that add to the design from Step 6 onward?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 8
