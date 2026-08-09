---
id: system-design-interview/09
subject: system-design-interview
title: "Design a Web Crawler"
slug: web-crawler
status: drafted
mastery: 
seniority: mid
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 9"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03, system-design-interview/04]
created: 2026-08-10
updated: 2026-08-10
---

# Design a Web Crawler

## TL;DR
A web crawler discovers and downloads pages from the web by starting from a set of
seed URLs, extracting links from each page, and recursively visiting new links, while
respecting politeness limits (don't hammer one site), avoiding infinite loops and
duplicate work, and prioritizing what to crawl next. The interview deep dive centers on
the URL frontier (the priority queue that decides crawl order and enforces
per-domain politeness) and duplicate/URL-seen detection at scale.

## The idea
Crawling sounds like a simple graph traversal (BFS/DFS over links), and at a small
scale it is. What makes it a real system design problem is scale and etiquette: the web
has trillions of pages, the crawler must not overwhelm any single site's servers, must
avoid re-crawling the same URL forever (the web graph has cycles and near-duplicate
content), must handle server errors and malicious/malformed pages gracefully, and must
decide what's worth crawling first when it can't crawl everything.

## How it works

### Step 1: Clarify requirements
- **Purpose.** Search-engine indexing (general-purpose, broad crawl) vs. a narrower use
  case (e.g., monitoring competitor prices, archiving). (Assume: general-purpose,
  HTML content only — not images/video.)
- **Scale.** Assume 1 billion pages need to be crawled per month.
- **Freshness.** Should previously-crawled pages be revisited to catch updates?
  (Assume: yes, but at a lower priority than new pages — a real crawler is a continuous
  process, not a one-shot traversal.)
- **Politeness.** Must not overwhelm any single web server. (Assume: a hard requirement
  — this shapes the whole design.)
- **Robustness.** Must handle malformed HTML, dead links, redirect loops, and
  intentionally hostile content (spider traps) without crashing or looping forever.

### Step 2: Back-of-the-envelope
1 billion pages/month: `1,000,000,000 / (30 × 100,000 seconds/day) ≈ 333 pages/sec`
average download rate. Assume average page size 500 KB (including embedded resources
counted toward the page, a generous but round estimate): storage need is
`1B × 500 KB = 500,000,000,000 KB = 500 TB/month` — clearly needs distributed storage
and object storage rather than a single disk (recall from `system-design-interview/02`
how quickly media/page storage outgrows text-only estimates). Bandwidth: `333 pages/sec
× 500 KB ≈ 166 MB/sec` average download throughput.

### Step 3: High-level design
```
[Seed URLs] --> [URL Frontier] --> [HTML Downloader] --> [Content Parser]
                     ^                                          |
                     |                                    +-----+-----+
                     |                              [Dedup check]  [Link extractor]
                     |                                    |              |
                     +---------------- new URLs ----------+              v
                                                                   [Content Storage]
```

- **URL Frontier**: a queue (really a set of queues, detailed in Step 4) holding URLs
  waiting to be crawled — the component that decides crawl order and enforces
  politeness.
- **HTML Downloader**: fetches the page content over HTTP, respecting `robots.txt`.
- **Content Parser**: validates and parses the downloaded HTML, extracts links, and
  extracts content for storage/indexing.
- **Dedup check**: has this exact URL (or this exact content) already been processed?
- **Content Storage**: durable storage (e.g., an object store) for the crawled content,
  feeding downstream indexing.

This whole pipeline is naturally parallelizable — many downloader/parser worker
instances pull from the shared frontier — and each stage can scale independently,
matching the "add workers behind a queue" pattern from `system-design-interview/03`.

### Step 4: Deep dive — the URL frontier and politeness
A single FIFO queue is not enough: it would let a crawler hammer one popular domain
(e.g., wikipedia.org) with thousands of concurrent requests the instant a page full of
Wikipedia links is parsed, which is both rude and likely to get the crawler IP-banned.

**Two-tier design (the book's approach):**
- **Priority queues (front queues)**: URLs are assigned a priority (based on factors
  like PageRank-style importance, update frequency, or freshness need) and placed into
  one of several priority queues; a selector picks from higher-priority queues more
  often, biasing crawl order toward more valuable pages first.
- **Politeness queues (back queues)**: a separate set of queues, one per host/domain,
  each with its own worker that enforces a minimum delay between requests to that host.
  A mapping table routes each URL to its host's dedicated back queue. A worker pool
  pulls one URL at a time from each back queue, respecting that queue's own rate limit
  — conceptually the same rate-limiting problem as `system-design-interview/04`, but
  keyed by hostname instead of user ID.

*Worked example:* the crawler discovers 5,000 links to wikipedia.org while parsing one
page, plus 3 links to a small personal blog. Without per-host queues, all 5,003 URLs
land in one shared queue and get fetched in roughly the order discovered — the personal
blog might wait behind 5,000 Wikipedia fetches, and Wikipedia gets hit with a burst.
With per-host back queues, the 5,000 Wikipedia URLs queue up behind Wikipedia's own
politeness worker (e.g., one request every 200ms to that host), while the blog's 3 URLs
go to a separate, empty back queue and get fetched immediately by a different worker —
both fairness across hosts and politeness per host fall out of the same mechanism.

### Step 5: Deep dive — avoiding duplicate work
Two related but distinct problems:

**URL-seen detection.** Has this exact URL already been queued or crawled? At 1
billion+ URLs, storing every seen URL as a full string and checking membership on every
new link discovered is expensive in both memory and lookup time. The standard fix is a
**Bloom filter** (a probabilistic set membership structure): it can tell you "definitely
not seen" or "possibly seen" using a small fixed-size bit array, with a tunable false
positive rate and zero false negatives. A false positive means occasionally skipping a
URL that was actually new (an acceptable loss at this scale — a small percentage of
missed pages doesn't materially harm crawl coverage) in exchange for orders-of-magnitude
less memory than storing every URL string.

*Worked example (why this matters at scale):* storing 1 billion URLs as raw strings
(~70 bytes average) needs ~70 GB. A Bloom filter targeting a 1% false-positive rate for
1 billion items needs roughly 1.2 GB — a ~98% memory reduction, the difference between
needing a single large-memory machine and needing a genuinely distributed store just
for URL-seen tracking.

**Near-duplicate content detection.** Different URLs (e.g., a page with tracking query
parameters, or mirrored content on multiple domains) can point to identical or nearly
identical content. Hash the page content (e.g., with a technique like SimHash or
MinHash, which produce similar hashes for similar content, unlike a cryptographic hash)
and compare against previously seen content hashes; skip re-processing near-duplicates.
This is a distinct problem from URL-seen detection — a URL can be "new" while its
content is a duplicate of something already crawled.

### Step 6: Deep dive — robustness and crawler traps
- **`robots.txt` compliance.** Before crawling any host, fetch and cache its
  `robots.txt` and respect its disallow rules — both an ethical/legal requirement and a
  practical one (ignoring it gets a crawler blocked).
- **Spider traps.** Some sites generate effectively infinite URLs dynamically (e.g., a
  calendar page with a "next month" link that never terminates, or session IDs embedded
  in every URL creating infinite unique-looking links to the same content). Mitigations:
  cap the maximum crawl depth per site, cap the maximum number of URLs crawled per
  domain, and detect and normalize URL patterns that vary only in ignorable parameters.
- **Malformed content and timeouts.** Downloaders must handle non-HTML content types,
  malformed HTML, extremely large pages, and unresponsive servers with strict timeouts
  — a single hung request must not block a worker indefinitely, so every fetch needs an
  explicit timeout with retry/backoff, conceptually similar to the resilience patterns
  covered in `system-design/14`.
- **DNS resolution cost.** Resolving a hostname to an IP on every single request adds
  latency and load on DNS servers at this volume; a local DNS cache (with a sensible
  TTL) avoids redundant lookups for hosts the crawler visits repeatedly.

### Step 7: Wrap-up — what would you improve given more time?
Good candidates note: distributing the frontier and workers across multiple
data centers/regions to crawl geographically closer to target servers and reduce
latency; a freshness/recrawl scheduler that revisits pages at a frequency proportional
to how often they historically change; and extensibility to non-HTML content types
(PDFs, images) if the requirements expand.

## Pros
- Naturally parallelizable pipeline — each stage (download, parse, dedup, store) scales
  independently by adding workers.
- Bloom filters make URL-seen tracking affordable at web scale, trading a small,
  tunable false-positive rate for orders-of-magnitude memory savings.
- The two-tier frontier (priority + politeness) solves both "what to crawl next" and
  "don't overwhelm one host" with a single, coherent mechanism.

## Cons
- Genuinely hard to make fully robust — the open web is adversarial (spider traps,
  malformed content, infinite URL spaces) in ways a closed internal system never is.
- Bloom filters trade correctness for memory: some new pages will be silently skipped
  (false positives), which may or may not be acceptable depending on the use case.
- Politeness and freshness pull in opposite directions (crawl slower per host vs. keep
  content fresh), and tuning that balance is an ongoing operational task, not a one-time
  design decision.

## Alternatives
- **A simple recursive crawler with a single shared queue** — fine for a small,
  narrowly-scoped crawl (e.g., a few known domains, no politeness concerns), but breaks
  down immediately at the scale and etiquette requirements this design targets.
- **Using a third-party crawling/indexing service or search API** — for most products
  that just need "search over the web," building a crawler from scratch is not worth
  it; this design is appropriate when crawling is the core product (a search engine,
  an archival service, a specialized monitoring tool).
- **Sitemap-driven crawling** — instead of discovering pages purely via link-following,
  consume sites' `sitemap.xml` files where available for more efficient, complete
  discovery of a single site's pages; often combined with link-following rather than
  replacing it, since not all sites publish sitemaps.

## When to use it
Building a search engine or any system that needs broad, ongoing discovery of web
content: SEO tools, price-monitoring services, content aggregators, academic web-graph
research.

## When NOT to use it
Don't build a general web crawler when you only need data from a small, known set of
sites with stable structure — a targeted scraper against known pages, or better, each
site's own API if available, is simpler and more respectful of their infrastructure.
Also skip the full distributed-frontier design for a one-off, small-scale crawl (a few
thousand pages) where a single-machine crawler with basic rate limiting is more than
sufficient.

## Key takeaways / mental model
Think of the crawler as two problems stacked on top of each other: a graph traversal
problem (BFS/DFS over links, needing dedup to avoid infinite loops) and a distributed
scheduling problem (deciding order and pacing across potentially millions of
independent "queues," one per host). The URL frontier is where both problems actually
live — priority queues answer "what's worth crawling," and per-host politeness queues
answer "how fast can I ethically crawl it." Everything else in the pipeline (download,
parse, dedup, store) is standard scalable-pipeline plumbing once the frontier's design
is right.

## Self-check questions
1. Why is a single shared FIFO queue insufficient once you add a politeness
   requirement, and what does the two-tier frontier design (priority + per-host back
   queues) do differently?
2. Why does the crawler need both URL-seen detection and near-duplicate content
   detection — what case does one catch that the other misses?
3. A Bloom filter says "possibly seen" for a URL that is actually new. What happens to
   that URL, and why is this an acceptable trade-off at web scale?
4. Describe a concrete spider trap scenario and one mitigation for it.
5. Why does DNS resolution caching matter specifically for a high-throughput crawler,
   more than it would for a typical low-traffic web application?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 9
- Cross-reference: `system-design-interview/04` (rate limiting) for the politeness
  mechanism's underlying pattern.
