---
id: system-design-interview/11
subject: system-design-interview
title: "Design a News Feed System"
slug: news-feed
status: drafted
mastery: 
seniority: senior
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 11"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03, system-design-interview/07]
created: 2026-08-10
updated: 2026-08-10
---

# Design a News Feed System

## TL;DR
A news feed shows each user a personalized, roughly-chronological stream of posts from
the people/pages they follow. The core interview tension is fan-out-on-write
(precompute each follower's feed when a post is made) vs. fan-out-on-read (compute the
feed at read time by merging the followed accounts' recent posts), and the deep dive is
almost always about how to handle celebrity accounts with tens of millions of
followers, which break the naive version of either approach on its own.

## The idea
There are two fundamentally different places to do the expensive work of "assembling
who-posted-what for this specific user": at write time (when a post is created) or at
read time (when a user opens their feed). Which is cheaper depends entirely on the
read:write ratio and the shape of the follow graph — and real social products have a
follow graph so skewed (most accounts have few followers, a handful have tens of
millions) that neither pure approach works uniformly, which is exactly what makes this
a strong deep-dive interview question.

## How it works

### Step 1: Clarify requirements
- **Feed composition.** Purely reverse-chronological from followed accounts, or
  ranked/algorithmic? (Assume: reverse-chronological for simplicity — ranking is a
  large topic of its own and worth explicitly scoping out unless the interviewer wants
  it.)
- **Scale.** Assume 300 million DAU, average 200 followees per user, with a small
  number of celebrity accounts having 30+ million followers.
- **Content types.** Text and images. (Assume, per `system-design-interview/01`'s
  scoping example.)
- **Freshness expectations.** A new post should appear in followers' feeds within
  seconds, not be instant to the millisecond.

### Step 2: Back-of-the-envelope
- Posts: assume 150M DAU each post 2x/day → 300M posts/day → ~3,000 QPS average write
  rate (same math as `system-design-interview/02`'s tweet example).
- Feed reads: assume each DAU checks their feed 10x/day → 1.5 billion feed reads/day →
  ~15,000 QPS average, ~30,000 QPS at peak — a roughly 5:1 read:write ratio at the
  feed-view level (lower than a pure "view a single post" ratio, because loading a feed
  is itself already an aggregation of many posts).
- Fan-out cost if done naively on every write: average 200 followers × 300M posts/day =
  60 billion feed-insert operations/day just for average accounts — before even
  considering celebrities. This number is the whole reason the design needs to be
  smarter than "always fan out on write."

### Step 3: High-level design
```
Write path:
[User posts] --> [API Server] --> [Post Store] --> [Fan-out Service] --> [Feed Cache: per-user feed list]

Read path:
[User opens feed] --> [API Server] --> [Feed Cache] --(merge if needed)--> [Post Store (hydrate content)]
```

- **Post Store**: durable storage for the post content itself (text, image references),
  keyed by post ID (a Snowflake-style unique ID, `system-design-interview/07`, gives
  natural chronological ordering for free).
- **Feed Cache**: for each user, a precomputed, ordered list of post IDs representing
  their feed — this is what fan-out-on-write populates.
- **Fan-out Service**: on a new post, determines who should receive it and updates
  their feed caches (asynchronously, via a message queue, matching the decoupling
  pattern from `system-design-interview/03`).

### Step 4: Deep dive — fan-out-on-write (push model)
When a user posts, immediately push the new post ID onto every follower's precomputed
feed list (typically capped to the most recent N, e.g., 1,000 post IDs per user, stored
in a fast store like Redis).

*Worked example:* User A has 200 followers and posts. The fan-out service enqueues a
job that, for each of the 200 followers, prepends the new post ID to their cached feed
list (`LPUSH` in Redis terms) and trims the list to the most recent 1,000 entries.
When any of those 200 followers opens their feed, it's already assembled — read the
cached list, then batch-fetch the actual post content from the Post Store for
hydration. This makes reads extremely fast (a cache lookup, not an expensive
aggregation query).

**Why this breaks for celebrities.** A celebrity account with 30 million followers
posting once means 30 million feed-cache updates for a single post — at even a modest
rate of celebrity posting, this is a massive, bursty write amplification (recall the
"60 billion feed-inserts/day for average accounts" number from Step 2 — a single
celebrity post alone can rival that in one event). Worse, if a celebrity posts multiple
times in quick succession, the fan-out queue backs up, and *fresh* posts from average
users get delayed behind the celebrity fan-out backlog, degrading freshness
system-wide, not just for the celebrity's own followers.

### Step 5: Deep dive — fan-out-on-read (pull model)
Instead of precomputing, do nothing at write time beyond storing the post. At read
time, fetch the list of accounts the user follows, then fetch each of their most recent
posts, merge them by timestamp, and return the top N.

*Worked example:* User B follows 200 accounts. When B opens their feed, the read path
queries "most recent posts" for each of the 200 followees (or a smarter batched query
against an index), merges the results, sorts by time, and returns the top 20. This
scales fine on the write side (a celebrity posting costs exactly one write, regardless
of follower count) but makes every single feed read expensive — an aggregation across
up to hundreds of accounts, every time, even if the user checks their feed 10 times in
a row with no new posts in between.

**Why this is bad on its own:** given the read:write ratio worked out in Step 2 (feed
reads happen far more often, in aggregate, than posts are made), pushing all the
aggregation cost onto every read means paying the most expensive operation on the more
frequent path — the opposite of where you want expensive work to live.

### Step 6: Deep dive — the hybrid approach (the standard answer)
Combine both: fan-out-on-write for the vast majority of accounts (which have modest
follower counts, so the write amplification is cheap), and fan-out-on-read specifically
for celebrity accounts (so a celebrity's single post is a single write, not millions).

*Worked example — assembling User C's feed under the hybrid model:* User C follows 195
regular accounts and 5 celebrity accounts.
1. Read C's precomputed feed cache — already contains recent posts from the 195
   regular accounts (populated via fan-out-on-write as those accounts posted).
2. Separately, fetch the most recent posts from each of the 5 celebrity accounts C
   follows (fan-out-on-read, done only for celebrities, and only at read time for the
   handful of users actively viewing their feed right now, not for all 30 million
   followers).
3. Merge the precomputed cache results with the freshly-fetched celebrity posts by
   timestamp, return the top N.

This means: a celebrity's post triggers zero fan-out writes (cheap for the write path,
regardless of follower count), and a regular user's feed read pays a small, bounded
extra cost (a handful of extra lookups, one per followed celebrity — not per follower)
rather than the full aggregation-over-200-accounts cost of pure fan-out-on-read.

**Where's the threshold?** A follower-count cutoff (e.g., accounts above 1 million
followers use pull, everyone else uses push) is a tunable parameter, not a fixed
constant — worth stating explicitly as a design knob you'd tune based on real
production data (fan-out queue depth, feed staleness metrics) rather than a number you'd
hardcode blindly.

### Step 7: Deep dive — feed cache storage and invalidation
The per-user feed cache (a list of recent post IDs) is typically kept in an in-memory
store like Redis, bounded to a fixed length (e.g., 1,000 entries) to keep memory usage
predictable — recall from `system-design-interview/02`'s method, `300M users × 1,000
post IDs × ~8 bytes/ID ≈ 2.4 TB`, sized comfortably for a distributed cache cluster but
large enough to justify sharding the cache itself by user ID.

When a followed user is unfollowed, or a post is deleted, the cached feed entries need
invalidation — typically handled lazily (filter out unfollowed/deleted content at read
time when hydrating from the Post Store, rather than eagerly scrubbing every affected
cached feed list, which would be its own expensive fan-out operation).

### Step 8: Wrap-up — trade-offs to state explicitly
Summarize the core trade-off for the interviewer: fan-out-on-write optimizes reads at
the cost of write amplification; fan-out-on-read optimizes writes at the cost of read
latency; the hybrid approach applies each where it's cheap and avoids each where it's
expensive, using follower count as the signal for which regime an account falls into.
This mirrors a very common system design pattern beyond feeds specifically: whenever
one side of a read/write imbalance has a long-tail outlier (here, celebrity follower
counts), a uniform strategy across all cases tends to break on the outlier, and a
hybrid, threshold-based strategy is the fix.

## Pros
- The hybrid approach gets fast reads for the common case (regular accounts, most
  users' feeds) without paying celebrity-scale write amplification.
- Fan-out via a queue (`system-design-interview/03`'s decoupling pattern) means a
  temporary fan-out backlog degrades freshness gracefully rather than failing writes.
- Feed caches make the hot read path (opening the app) fast, which is the
  highest-frequency user action in a social product.

## Cons
- Meaningfully more complex than either pure approach — two code paths, a tunable
  threshold, and a merge step at read time for celebrity-following users.
- Feed cache invalidation on unfollow/delete is inherently a bit lossy if handled
  lazily (a deleted post might briefly still appear until filtered at hydration).
- Precomputed feeds bounded to a fixed length (e.g., 1,000 posts) can miss older
  content if a user hasn't opened the app in a long time and needs to "catch up"
  further back than the cache retains.

## Alternatives
- **Pure fan-out-on-write** — simplest, fastest reads, but breaks down exactly at
  celebrity-scale follower counts, as shown in Step 4; acceptable only for products
  with a follow graph that has no extreme outliers (e.g., a small internal team feed).
- **Pure fan-out-on-read** — simplest on the write side, but pushes aggregation cost
  onto the far more frequent read path; acceptable for products with very low read
  volume relative to writes, or very small follow counts per user.
- **Ranked/algorithmic feed instead of reverse-chronological** — a separate axis of
  complexity (scoring and ranking posts by predicted engagement rather than pure
  recency), often layered on top of either fan-out strategy rather than replacing it;
  worth mentioning as a follow-on if the interviewer wants to go further.

## When to use it
Any social product with a follow/subscribe graph and a personalized activity stream:
social networks, professional networks, blogging platforms with a "following" feature.
The hybrid pattern specifically is warranted whenever the follow-graph's degree
distribution is heavy-tailed (a small number of accounts with vastly more followers
than the median).

## When NOT to use it
For a product where every user follows a small, roughly-uniform number of other users
with no outliers (e.g., a team collaboration tool where "following" means "same team,"
capped at dozens of members), pure fan-out-on-write is simpler and sufficient — the
hybrid model's extra complexity buys nothing without a heavy-tailed follow graph to
protect against.

## Key takeaways / mental model
Picture two dials you can turn: "how much work happens when someone posts" and "how
much work happens when someone reads their feed." Fan-out-on-write cranks the first
dial up and the second down; fan-out-on-read does the reverse. Celebrities are the
account type where cranking the write-time dial up is catastrophic (millions of
fan-out writes per post), so the hybrid design turns the write-time dial down
specifically for them and accepts a small, bounded increase in read-time cost instead
— a classic "handle the common case one way, handle the outlier a different way"
pattern.

## Self-check questions
1. Why does fan-out-on-write's cost scale with a poster's *follower count*, while
   fan-out-on-read's cost scales with a reader's *followee count* — and why does that
   distinction matter for celebrity accounts specifically?
2. Walk through what happens to feed freshness for regular users if a celebrity with 30
   million followers posts three times in one minute, under a pure fan-out-on-write
   design.
3. In the hybrid model, why is the follower-count threshold a tunable parameter rather
   than a fixed constant, and what production signal would you use to tune it?
4. A user unfollows someone whose posts are already sitting in their precomputed feed
   cache. Why is lazy filtering at read time a reasonable choice here instead of
   eagerly scrubbing the cache?
5. If this system needed to support algorithmic (non-chronological) ranking instead of
   pure recency, which part of the design from this lesson would need to change, and
   which parts would stay the same?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 11
- Cross-reference: `system-design/17` (case study: news feed and timelines) covers the
  same fan-out trade-off from the general system-design angle.
