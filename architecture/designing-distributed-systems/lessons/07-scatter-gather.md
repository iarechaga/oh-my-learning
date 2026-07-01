---
id: designing-distributed-systems/07
subject: designing-distributed-systems
title: "Scatter/Gather"
slug: scatter-gather
status: drafted
mastery:
seniority: senior
source: "Designing Distributed Systems (Brendan Burns), Chapter 7 (Scatter/Gather)"
prerequisites: [designing-distributed-systems/06]
created: 2026-07-01
updated: 2026-07-01
---

# Scatter/Gather

## TL;DR
Scatter/gather is the multi-node serving pattern for parallelizing a *single* request across many leaf servers and combining their partial answers into one response. Where replication scales the number of *requests* and sharding scales the amount of *data*, scatter/gather scales the *work inside one request* by fanning it out to leaves that each process a slice in parallel, then merging their results. Its defining weakness is the straggler: because the root must wait for every leaf, the request's latency is set by the *slowest* leaf, not the average - so tail latency, not throughput, is the thing you fight.

## The idea
Some requests are too expensive for one machine to answer in acceptable time, not because of request volume but because the *computation for a single request* is huge. Searching a 100 TB document index for one query, or scoring one search across billions of items, cannot be done fast on a single node - the data to examine is enormous even for one request.

The insight: if the data is partitioned across many leaf nodes (like [sharded services](06-sharded-services.md)), a single request can be **scattered** to all leaves at once. Each leaf searches only its slice in parallel with the others, and returns a partial result. A **root** (or parent) node then **gathers** those partials and merges them into the final answer. Because the leaves work simultaneously, the wall-clock time is roughly the time for *one* leaf to search its slice - not the sum. Ten leaves searching 1/10th of the data each finish in ~1/10th the time of one node searching all of it.

So scatter/gather adds a third scaling axis to the serving patterns:

- **Replication** (lesson 05): more identical replicas -> more requests/second.
- **Sharding** (lesson 06): partition data across nodes -> hold/serve more data.
- **Scatter/gather** (this lesson): fan one request across leaves -> lower *latency* for a single expensive request by doing its work in parallel.

The pattern's beauty (parallel speedup) and its curse (tail latency) are two sides of the same coin: you get the speed of parallelism, but you also inherit a dependency on the *slowest* participant, because the answer is incomplete until the last leaf replies.

## How it works

### The topology: root and leaves
A scatter/gather service is a tree, usually one level deep.

- **Leaf nodes** each hold a shard of the data and can answer a query against *their* slice. There are `N` leaves; together they cover the whole dataset.
- **The root** (parent) receives the client request, scatters a copy to all `N` leaves, waits for their partial responses, gathers and merges them, and returns one combined result.

```text
                    client
                      |
                      v
                 +---------+
                 |  Root   |   (scatter to all, then gather+merge)
                 +---------+
              /      |       \        (request fanned out in parallel)
             v       v        v
        +------+  +------+  +------+
        |Leaf 0|  |Leaf 1|  |Leaf 2|  each searches its own shard
        +------+  +------+  +------+
             \       |       /        (partial results returned)
              \      v      /
                 merge -> final response
```

The root is typically replicated (lesson 05) for its own availability and to handle request volume; the leaves are sharded (lesson 06) to divide the data. Scatter/gather thus *composes* the two earlier patterns rather than replacing them.

### The merge step is part of the design, not an afterthought
Gathering is not always "concatenate the lists." What the root must do to combine partials depends on the query:

- **Search/ranking:** each leaf returns its top-K locally; the root merges the N lists and re-ranks to a global top-K. A leaf cannot return a global rank because it only saw its own shard.
- **Aggregation (count/sum/avg):** each leaf returns a partial aggregate; the root combines them (sum the counts; for an average, gather partial sums and counts, then divide - you cannot average the averages).
- **Existence/first-match:** the root can return as soon as *one* leaf answers positively (an optimization that escapes the straggler problem for that query type).

Designing the merge - and making sure partial results are *composable* into a correct global result - is where a lot of the pattern's subtlety lives.

### The straggler problem: latency is set by the slowest leaf
Here is the defining challenge. The root cannot return the final answer until it has heard from every leaf it needs. So the request's latency equals the latency of the **slowest** leaf, not the average. This is a tail-latency amplifier, and it gets *worse* as you add leaves.

Suppose each leaf usually responds in 10 ms, but 1% of the time a leaf takes 1,000 ms (a GC pause, a slow disk, a hot shard). With **1 leaf**, 99% of requests are fast. With **100 leaves**, the chance that *at least one* of the 100 is slow on a given request is `1 - 0.99^100 ~= 63%`. So ~63% of requests wait ~1,000 ms - even though any individual leaf is fast 99% of the time. Fan-out multiplies the odds of hitting a straggler.

```text
P(a request is slow) = 1 - (P one leaf is fast)^(number of leaves)
  1 leaf,   1% slow each: 1 - 0.99^1   =  1%
  10 leaves:              1 - 0.99^10  = ~9.6%
  100 leaves:             1 - 0.99^100 = ~63%
```

This is why scatter/gather is a *senior* topic: the naive version works in a demo and then falls over on tail latency in production. Mitigations are mandatory, not optional:

1. **Hedged requests / backup requests:** if a leaf has not replied within, say, the 95th-percentile latency, send the same sub-query to a *replica* of that leaf's shard and take whichever returns first. This caps the tail at roughly the second-fastest of two tries.
2. **Partial results with a deadline:** the root sets a timeout; if a few leaves miss it, return the answer computed from the leaves that *did* reply, flagged as "partial." For search, missing one shard slightly degrades results but keeps latency bounded - usually a good trade.
3. **Reduce fan-out:** fewer, larger leaves mean fewer chances to hit a straggler (at the cost of more work per leaf). There is an optimum, not "more leaves is always better."
4. **Tail-tolerant leaf design:** keep leaf shards evenly sized (avoid hot shards), and keep per-leaf work predictable.

### The fan-out cost: work is amplified too
Every leaf does work for *every* request that touches it. A single client request becomes `N` leaf requests. If the root fans out to 100 leaves, one query is 100 units of backend work. This is fine when the parallel *latency* win is worth the *total-work* cost, but it means scatter/gather does not improve - and can worsen - overall throughput/efficiency. You are spending more total CPU to make one request *faster*, which is the right trade for latency-critical queries and the wrong trade for cheap ones.

### Worked example 1: parallel search with local-then-global top-K
A search service indexes 100 million documents across 10 leaf shards (10M docs each). A user searches "distributed systems patterns," wants the top 10 results.

1. The root receives the query and scatters it to all 10 leaves simultaneously.
2. Each leaf searches its own 10M-document shard and returns *its* local top 10 (with relevance scores). Ten leaves work in parallel, so this takes ~the time for one leaf to search 10M docs, not 100M.
3. The root now has 10 lists of 10 = 100 candidate results. It merges them by score and takes the global top 10.
4. Why local top-10 and not top-1? A globally-best result could be the 7th-best on its own shard, so each leaf must return enough candidates (>= the global K) for the merge to be correct. Returning only each leaf's #1 would miss results.
5. Result: a search over 100M docs answered in roughly the latency of a 10M-doc search, at the cost of 10x the total search work.

### Worked example 2: the straggler bites, and a hedge saves the tail
Same 10-leaf search. Each leaf normally replies in 20 ms; occasionally one stalls for 400 ms (a GC pause). Each shard has a replica (shard replicated per lesson 06).

- **Without hedging:** on a request where leaf 6 stalls, the root has 9 answers at 20 ms but must wait for leaf 6 -> the user waits ~400 ms. With 10 leaves and a 2% stall rate each, `1 - 0.98^10 ~= 18%` of requests suffer this. Nearly one in five searches is slow.
- **With hedging:** the root notes leaf 6 has not answered by 40 ms (well past the 20 ms norm) and sends the same sub-query to leaf 6's *replica*. The replica answers in 20 ms. The root uses whichever of the two returns first -> the request finishes in ~60 ms instead of 400 ms. The tail collapses from 400 ms toward ~60 ms, at the cost of a little extra work on hedged sub-queries only.

### Worked example 3: partial results under a deadline
A monitoring dashboard scatters a "count errors in the last hour" query across 50 leaf shards; the UI needs an answer within 100 ms.

1. Root scatters to all 50 leaves; each returns a partial count.
2. At the 100 ms deadline, 48 leaves have replied; leaves 12 and 37 are slow (one has a hot shard).
3. Rather than block the whole dashboard on 2 stragglers, the root sums the 48 partial counts and returns the total **flagged as ~96% complete** (48/50 shards), with the count of missing shards.
4. For a monitoring number, "12,340 errors (based on 48 of 50 shards)" delivered in 100 ms is far more useful than an exact number delivered in 400 ms. The pattern trades a sliver of accuracy for a hard latency bound - a deliberate, senior-level call about which the merge logic and the product both must agree.

## Pros
- **Latency scaling for a single request:** parallelizes one expensive query across leaves, so wall-clock time approaches "one leaf's slice" instead of "the whole dataset."
- **Handles datasets no single node could query in time:** search/analytics over huge corpora become feasible per-request.
- **Composes with replication and sharding:** roots replicate for availability, leaves shard for data - the three serving patterns stack.
- **Tunable accuracy/latency trade:** deadlines + partial results let you bound latency by relaxing completeness when appropriate.

## Cons
- **Tail latency dominated by the slowest leaf:** fan-out multiplies the probability of hitting a straggler, so p99 latency degrades as leaves increase - the central difficulty.
- **Work amplification:** one request becomes N leaf requests; total backend work (and cost) grows with fan-out, hurting efficiency/throughput.
- **Merge complexity:** partial results must be *composable* into a correct global answer (global top-K, partial aggregates), which is query-specific and easy to get subtly wrong.
- **Operational fragility:** requires hedging, deadlines, and even shard sizing to stay fast; the naive implementation looks fine until production tail latency exposes it.

## Alternatives
- **Sharded service with client-side routing (no fan-out):** if a request only needs *one* shard's data (a point lookup by key), route to that single shard instead of scattering - no straggler problem (lesson 06).
- **Precomputation / materialized results:** compute expensive aggregates ahead of time (batch or streaming) and serve them with a cheap lookup, avoiding per-request fan-out entirely (see [ddia/14 - Batch processing](../../ddia/lessons/14-batch-processing.md)).
- **Approximate/probabilistic answers:** use sketches (HyperLogLog, top-K sketches) to answer "how many"/"most frequent" from a single node without querying every shard.
- **Vertical scaling of one leaf:** for moderate data, a single bigger machine avoids fan-out and its tail-latency amplification - until the data outgrows one node.

## When to use it
- A *single* request requires processing more data than one node can handle within the latency budget, and that data is (or can be) partitioned across leaves.
- The work parallelizes cleanly and the partial results are composable into a correct global answer (search, ranking, aggregation).
- Low per-request latency matters enough to justify spending extra total work (fan-out) to get it.
- You can afford the mitigations (shard replicas for hedging, deadline/partial-result logic).

## When NOT to use it
- The request needs data from only one shard - route directly to it; scattering to all leaves wastes work and imports the straggler problem for nothing.
- You cannot tolerate the tail-latency amplification and cannot deploy hedging/deadlines - a large fan-out will make p99 unacceptable.
- The answer can be precomputed or approximated cheaply - do that instead of fanning out on every request.
- Throughput/cost efficiency matters more than single-request latency - fan-out's work amplification is the wrong trade.

## Key takeaways / mental model
Picture asking a question to a room of 100 researchers, each of whom has read a different tenth of the library, and you cannot leave until *every* one has answered. You get the speed of 100 people reading in parallel - but the meeting ends only when the *slowest* person finishes, and with 100 people the odds that *someone* is slow are high. Two rules of thumb:

1. **Scatter/gather scales single-request latency, not throughput - and its enemy is the tail.** Latency tracks the slowest leaf, and fan-out multiplies the chance of a straggler (`1 - fast^N`), so hedged requests, deadlines with partial results, and bounded fan-out are mandatory, not optional.
2. **The merge defines correctness.** Leaves see only their slice, so they must return enough (local top-K, partial sums) for the root to compute a correct *global* answer - "average the averages" and "top-1 per shard" are classic bugs.

## Self-check questions
1. How does scatter/gather differ from replication and from sharding in *what* it scales? Why does it "compose" the other two rather than replace them?
2. Derive why a service that fans out to 100 leaves, each fast 99% of the time, is slow ~63% of the time. What does this tell you about tail latency vs. fan-out?
3. Explain three straggler mitigations (hedged requests, deadline + partial results, reduced fan-out) and the specific cost each one pays.
4. In the parallel-search example, why must each leaf return its local top-K rather than just its single best result? What breaks if K is too small?
5. What does "the merge step defines correctness" mean? Give an aggregation example where naively combining partial results yields the wrong answer, and the correct composition.
6. You must answer "count of distinct users in the last hour" with a 50 ms budget over 200 shards. Would you use scatter/gather, and if not, what would you use instead? Justify the trade-off.

## References
- Designing Distributed Systems (Brendan Burns), Chapter 7: "Scatter/Gather"
- [designing-distributed-systems/06 - Sharded Services](06-sharded-services.md)
- [ddia/14 - Batch processing](../../ddia/lessons/14-batch-processing.md)
