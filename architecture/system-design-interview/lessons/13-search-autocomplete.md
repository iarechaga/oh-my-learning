---
id: system-design-interview/13
subject: system-design-interview
title: "Design a Search Autocomplete System"
slug: search-autocomplete
status: drafted
mastery: 
seniority: senior
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 13"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03]
created: 2026-08-10
updated: 2026-08-10
---

# Design a Search Autocomplete System

## TL;DR
An autocomplete (type-ahead) system suggests the most likely completions for a search
query as the user types, and must respond within tens of milliseconds per keystroke.
The standard design precomputes the top-K completions for every prefix using a trie
(or an equivalent index) built from historical query frequency data, refreshed
periodically offline rather than updated live on every search — because live updates
at the per-keystroke latency budget this system operates under are neither necessary
nor affordable.

## The idea
Autocomplete looks like a simple "prefix match" problem, but the interesting
constraints are speed (a suggestion must render before the user's next keystroke, so
the budget is on the order of 100ms end-to-end including network) and data freshness
at scale (trending queries should surface reasonably quickly, but recomputing rankings
on every single keystroke across every user is unnecessary and wasteful). The design
splits into two very different subsystems: an offline pipeline that builds the ranked
suggestion data, and an online serving path that answers queries against it with
minimal latency.

## How it works

### Step 1: Clarify requirements
- **Scope.** Suggest the top 5 completions for a given prefix, ranked by historical
  popularity. (Assume: no personalization for the core design — mention it as an
  extension.)
- **Latency.** Must respond within ~100ms per keystroke, including network round trip.
- **Data freshness.** Suggestions should reflect real usage patterns, updated
  periodically (e.g., hourly/daily), not necessarily in real time. (Assume: this
  trade-off is acceptable — worth confirming explicitly, since "real-time trending"
  is a materially harder variant of this problem.)
- **Scale.** Assume 10 billion searches/day across a large, diverse query vocabulary.

### Step 2: Back-of-the-envelope
`10,000,000,000 / 100,000 seconds/day = 100,000 QPS average` search-triggering
keystrokes (assuming a suggestion request fires on most keystrokes, not just full
query submission — this is a meaningfully higher request rate than "searches
submitted," since a single typed query might trigger 5-10 autocomplete requests, one
per keystroke, before the user finishes typing or picks a suggestion). At ~200,000 QPS
peak, this system must serve requests almost entirely from memory — no request in this
path can afford a disk-backed database round trip within the ~100ms budget once network
and rendering time are subtracted (recall from `system-design-interview/02`: memory
access ~0.25ms/MB vs. disk ~1ms/MB — at this QPS and latency budget, disk access per
request is a non-starter for the hot path).

### Step 3: High-level design — two pipelines
```
Offline (batch):
[Query Logs] --> [Aggregation Job] --> [Build Trie / Top-K per prefix] --> [Trie Store / Snapshot]

Online (serving):
[Client keystroke] --> [LB] --> [Autocomplete Servers] --(load trie into memory)--> [Cache] --> [response]
```

The **offline pipeline** periodically (e.g., daily) processes historical search-query
logs, counts query frequency, and builds a data structure that maps every prefix to its
top-K most frequent completions. The **online serving path** simply looks up the
current prefix against this precomputed structure, entirely in memory, and returns the
top-K — no ranking computation happens on the request path at all, which is what makes
sub-100ms responses achievable at 200,000 QPS.

### Step 4: Deep dive — the trie and precomputing top-K per node
A trie (prefix tree) naturally represents "all queries sharing this prefix" as the
subtree rooted at the node for that prefix. The naive version stores raw query
frequency at each leaf and, on a request, would need to traverse the entire subtree
under the user's typed prefix to find the top-K most frequent completions — too slow
to do per-request at this QPS.

**The fix: precompute and cache the top-K at every node, not just leaves.** During the
offline build, for every trie node (i.e., every possible prefix), store the top-K
completions (by frequency) reachable from that node, computed once during the batch
job. At serving time, a request for prefix "sys" is a single trie traversal down to the
"sys" node (O(length of prefix), not O(size of subtree)), followed by reading its
precomputed top-K list directly — no subtree walk needed at request time.

*Worked example:* suppose historical query counts include: "system design" (50,000),
"system design interview" (30,000), "systematic review" (8,000), "systems thinking"
(5,000). Building the trie: the node for prefix "sys" would store, precomputed,
`top-3 = ["system design" (50k), "system design interview" (30k), "systematic review"
(8k)]` — "systems thinking" (5k) doesn't make the top-3 for this prefix and is
discarded from that node's cached list (though it remains in the full dataset and could
surface at a more specific prefix like "syste" or "systems" where fewer competitors
exist above it).
- User types "s" → look up node "s" → return its precomputed top-K.
- User types "sy" → look up node "sy" → return its precomputed top-K.
- User types "sys" → look up node "sys" → return the `top-3` list from above directly.

Each keystroke is an independent O(1)-ish lookup (after an O(prefix length) trie
descent) against precomputed data — no ranking or aggregation work happens live.

### Step 5: Deep dive — building the trie at scale (the offline job)
With billions of daily searches and a large vocabulary, building this structure is a
genuine batch-processing problem, not a small script:
1. **Aggregate query frequency** from search logs (typically via a distributed batch
   job, e.g., MapReduce/Spark-style aggregation): group by exact query string, count
   occurrences over the aggregation window (e.g., the last 7 or 30 days, often
   weighted so more recent activity counts more, to let trending queries rise and stale
   ones fade).
2. **Insert each (query, frequency) pair into the trie**, and at each node along the
   insertion path, update that node's top-K list if the new query's frequency
   qualifies.
3. **Persist the resulting trie as an immutable snapshot** (e.g., serialized to a
   compact binary format) and distribute it to the online serving fleet.

Because this runs periodically (not on every write), it sidesteps the need for the trie
to support fast concurrent updates under heavy read load — the online serving fleet
only ever reads from an immutable snapshot, which is far simpler and faster than a
trie that must handle live inserts and reads simultaneously.

### Step 6: Deep dive — serving the trie in production
The full trie, at web-search scale, is too large to serve from a single machine's
memory (a large vocabulary with per-node top-K lists is substantial, though far smaller
than the raw query log data it was built from, since only top-K per node is retained,
not the full frequency table).

**Sharding the trie.** Partition it — e.g., by first character or first few characters
of the prefix (all queries starting with "a" go to shard 1, "b" to shard 2, etc.) —
across multiple serving nodes, each holding its shard entirely in memory. A router in
front determines which shard(s) to query based on the user's typed prefix. Uneven
distribution (far more queries start with common letters than rare ones) is a real
concern, addressed similarly to hot-shard problems elsewhere (see the consistent
hashing lesson, `system-design-interview/05`, for the general shape of this problem,
though here the partitioning key is semantic — prefix — rather than a hash).

**A cache in front of the trie servers** absorbs the most repeated prefixes (a small
number of very common prefixes — "a", "th", "how" — likely account for a
disproportionate share of traffic), further reducing load on the trie-serving tier
itself, following the same cache-aside principle used throughout this subject
(`system-design-interview/03`).

**Client-side debouncing.** Not every keystroke needs to trigger a network request —
clients typically wait a short delay (e.g., 50-100ms) after the last keystroke before
firing the autocomplete request, cutting the effective request volume substantially
for fast typists without materially hurting perceived responsiveness.

### Step 7: Deep dive — freshness and the trending-query problem
Because the trie is an immutable, periodically-rebuilt snapshot, a genuinely new
trending query (e.g., breaking news) won't appear in suggestions until the next
rebuild cycle. Mitigations:
- **Shorten the rebuild interval** for at least a "delta" layer (e.g., rebuild the full
  trie daily, but maintain a small, fast-refreshing overlay of very recent high-velocity
  queries that gets merged with the main trie's results at serving time) — this is
  explicitly a scope extension beyond the core design from Step 1, worth raising if the
  interviewer pushes on real-time trending.
- **Weight recent activity more heavily** in the frequency aggregation itself (Step 5),
  so the *next* rebuild reflects trends quickly even without a separate real-time path.

### Step 8: Wrap-up — what to mention if pushed further
Spelling correction/fuzzy matching (tolerating typos), personalization (weighting a
given user's own search history), and multi-language support (each with its own
tokenization concerns) are all natural extensions, worth naming explicitly as
out-of-scope-for-now rather than silently ignored, per the framework's Step 1 scoping
discipline (`system-design-interview/01`).

## Pros
- Precomputing top-K per trie node turns each keystroke into a fast, O(prefix length)
  lookup with zero live ranking computation — essential to hitting the sub-100ms
  budget at very high QPS.
- Separating the offline build from the online serving path means the read-heavy,
  latency-critical serving fleet never has to handle concurrent writes, dramatically
  simplifying it.
- Sharding by prefix keeps each shard's working set small enough to serve entirely from
  memory.

## Cons
- Freshness lag — a genuinely new trending query won't surface until the next rebuild,
  which is a real product trade-off, not a free simplification.
- Prefix-based sharding can be unevenly loaded (common prefixes get disproportionate
  traffic) and needs its own load-balancing care.
- The precomputed top-K per node doesn't personalize or adapt to an individual user's
  intent — a real limitation without the personalization extension.

## Alternatives
- **Query the full search index directly for every autocomplete request** (no separate
  trie/precomputation) — simpler to build and always fresh, but far too slow at this
  QPS/latency budget; reasonable only for low-traffic or non-latency-critical
  autocomplete use cases.
- **A dedicated search engine's built-in suggest feature** (e.g., Elasticsearch's
  completion suggester) — offloads the trie-building and serving complexity to an
  existing, well-optimized system; a very reasonable real-world choice, worth
  mentioning as "I'd likely use an existing solution here in practice, but here's how
  it works under the hood" if the interviewer wants the mechanism explained anyway.
- **Real-time streaming aggregation** (update rankings continuously as new queries
  arrive, e.g., via a stream processor) instead of periodic batch rebuilds — solves the
  freshness lag directly, at the cost of materially higher system complexity; the right
  choice only if freshness is a hard, explicit requirement (Step 1's clarification).

## When to use it
Any search or command interface needing fast, popularity-ranked suggestions as the
user types: web search boxes, e-commerce product search, IDE command palettes,
address/form autofill.

## When NOT to use it
Skip the full precomputed-trie-plus-sharding architecture for a low-traffic internal
tool or a small, bounded vocabulary (e.g., autocomplete over a company's ~500 internal
document titles) — a simple in-memory prefix search over the small dataset, rebuilt on
every deploy or even computed live, is more than fast enough and far simpler to build
and operate.

## Key takeaways / mental model
The whole design is an application of one idea: move all the expensive work
(aggregating and ranking) to an offline batch process that runs occasionally, so the
online path only ever does the cheapest possible operation (a prefix lookup against
precomputed, in-memory data) on the hot, latency-critical, high-QPS path. Whenever a
system has a very tight per-request latency budget and a workload that tolerates
some staleness, this offline-build/online-serve split is the general pattern to reach
for — it shows up again in other read-heavy, latency-sensitive designs beyond
autocomplete specifically.

## Self-check questions
1. Why is a naive "walk the trie subtree under the user's prefix at request time"
   approach too slow at this system's scale, and what does precomputing top-K per node
   change about the request-time cost?
2. Walk through why separating the offline trie-build pipeline from the online serving
   path lets the serving fleet avoid handling concurrent writes.
3. Given 10 billion searches/day and ~5-10 keystroke-triggered requests per completed
   search, why does the effective QPS this system serves differ so much from "searches
   submitted per day," and why does that distinction matter for capacity planning?
4. Why does prefix-based trie sharding risk uneven load across shards, and what's one
   way to address it?
5. A stakeholder asks why a breaking-news query isn't showing up in autocomplete
   suggestions yet, an hour after it started trending. What part of this design
   explains that, and what would you change to fix it?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 13
