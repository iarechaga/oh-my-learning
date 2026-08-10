---
id: building-microservices/15
subject: building-microservices
title: "Scaling Microservices"
slug: scaling
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 13"
prerequisites: [building-microservices/07, building-microservices/10]
created: 2026-08-10
updated: 2026-08-10
---

# Scaling Microservices

## TL;DR
There are three distinct axes to scale a system along, commonly framed as the **AKF/X-axis scale cube**: duplicate identical instances behind a load balancer (X-axis), split by function/service (Y-axis — which microservices already give you for free), and partition data (Z-axis, sharding). Autoscaling automates the X-axis based on real-time triggers (CPU, request rate, queue depth). The critical practical distinction: scaling **stateless** services is close to trivial (just add more identical instances), while scaling **stateful** services requires solving data partitioning and consistency, which is a fundamentally harder problem.

## The idea
One of microservices' selling points from Lesson 01 is independent, targeted scaling — scale the service under load without scaling the whole system. This lesson is about the actual mechanics and axes of scaling once you've got there: not just "add more instances," but a structured way to think about *which* dimension to scale along for a given bottleneck, plus the sharp distinction between scaling something that holds no state versus something that does.

The **AKF scale cube** (from Abbott and Fisher's *The Art of Scalability*, though Newman references the same three-axis framing) gives the vocabulary:

- **X-axis: horizontal duplication.** Run N identical copies of the same service behind a load balancer, each capable of handling any request. Simple conceptually — just add more instances — but only works cleanly if the service is stateless (any instance can handle any request, with no need to route a specific request to a specific instance because of state held locally).
- **Y-axis: functional/service decomposition.** Split the system by function into separate services, each independently scalable — this is exactly what decomposing a monolith into microservices already buys you (Lesson 01, Lesson 02): if `inventory-service` is under heavy load but `shipping-service` isn't, you scale `inventory-service` alone, something the Y-axis split makes possible in the first place.
- **Z-axis: data partitioning (sharding).** Split the *data* (and the requests that touch it) by some key — e.g., customer ID, geographic region — so that each partition/shard handles only a fraction of the total data and load. Each shard can be scaled somewhat independently, and no single node needs to hold or serve the entire dataset.

Microservices architecture is, in a real sense, "Y-axis scaling applied at the whole-system level" — decomposing by business capability (Lesson 02) is itself a scaling strategy, not just an organizational one. Within a single service, you then reach for X-axis (duplication) and, if the service is data-heavy, Z-axis (partitioning) to scale further.

## How it works

### X-axis: horizontal duplication and autoscaling

The simplest scaling lever: run more copies of the exact same service, with a load balancer distributing requests across them. This works cleanly when the service is **stateless** — no instance holds data or session state that only it has; any instance can equally well handle any incoming request, because all the state that matters lives in a shared, external store (a database, a cache) that every instance can reach, not in any one instance's memory.

**Autoscaling** automates this: rather than a human deciding "we need 10 more instances," the orchestration platform (Lesson 10) watches a trigger metric and adjusts the instance count automatically. Common triggers:
- **CPU utilization** — scale out when average CPU across instances crosses a threshold (e.g., 70%), scale in when it drops.
- **Request rate / requests-in-flight** — scale based on actual traffic volume rather than a proxy metric like CPU, useful when the service's CPU usage doesn't track load linearly (e.g., I/O-bound services).
- **Queue depth** — for services consuming from a message queue/event stream (Lesson 06), scale consumer instances based on how much backlog is building up, so a traffic spike that produces a growing queue triggers more consumers to drain it faster.

**Worked example.** `catalog-service` is stateless — it reads product data from a shared database and a shared cache, holding no per-instance state. During a flash sale, request rate to `catalog-service` triples. An autoscaler configured on request-rate triggers automatically increases instance count from 4 to 14 over a few minutes, the load balancer distributes the increased traffic across the new instances, and once the sale ends and traffic drops, the autoscaler scales back down to 4 — all without a human manually provisioning anything.

### Y-axis: functional decomposition (what microservices already give you)

This is the axis microservices architecture provides structurally, by definition (Lesson 01, Lesson 02): once `catalog-service`, `inventory-service`, and `shipping-service` are separate services, each can be scaled to a completely different instance count based on its own load profile, something impossible in a monolith where the whole system scales as one unit. A flash sale that spikes catalog-browsing traffic but not shipping volume lets you scale `catalog-service` to 14 instances while leaving `shipping-service` at its normal 3 — precisely the targeted-scaling benefit named as a pro in Lesson 01.

### Z-axis: data partitioning (sharding)

Sometimes X-axis duplication alone isn't enough, because the bottleneck isn't compute capacity but the volume of *data* a single database (or single service instance holding a full in-memory dataset) needs to handle. **Sharding** splits the data itself across multiple partitions by some key, so that each partition handles a fraction of the total data and the load that touches it.

**Worked example.** `inventory-service`'s database has grown to hold stock data for millions of SKUs across thousands of warehouses worldwide, and a single database instance is now the bottleneck — not CPU on the service's stateless application layer (which scales fine via X-axis), but query load and data volume on the one shared database behind it. The team shards the inventory database by warehouse region (e.g., `inventory-db-us`, `inventory-db-eu`, `inventory-db-apac`), each holding only the SKU/stock data relevant to its region. `inventory-service`'s application instances (still stateless, still scaled via X-axis) route each request to the correct regional shard based on the warehouse ID in the request. Now no single database instance needs to hold or serve the full global dataset, and each region's shard can be scaled and tuned independently.

This connects directly to `ddia/10` (Partitioning) and `system-design/04` (Consistent Hashing) — the underlying partitioning strategies (range-based, hash-based, directory-based, and consistent hashing specifically for minimizing data movement when shards change) are exactly the techniques those lessons cover in depth; this lesson's job is to place sharding correctly within the broader scaling picture, as the tool you reach for once data volume itself, not just request-handling compute, is the bottleneck.

### The critical distinction: stateless vs. stateful scaling

This is the single most important practical takeaway of the lesson. Scaling a **stateless** service is close to mechanical: spin up another identical instance, put it behind the load balancer, done — any instance can serve any request because no instance holds anything unique. Scaling a **stateful** service (one that holds data — a database, a cache, a service with in-memory session state) is a fundamentally different and harder problem, because you can't just duplicate it: two independent copies of a stateful service holding different, diverging data are not interchangeable the way two stateless instances are, and reads/writes now need to be routed *consistently* to the instance/shard/replica that actually holds the relevant, up-to-date data.

**Worked example: the contrast, concretely.** `catalog-service` (stateless, reads from a shared database) scales from 4 to 14 instances in minutes via autoscaling, with zero data-consistency concerns — every instance sees the same shared database regardless of which one handles a given request. Contrast this with naively trying to "scale" `inventory-service`'s database the same way: simply running 10 independent copies of the database, each accepting writes independently, would immediately create data divergence — one copy might show a SKU as in stock while another shows it as sold out, because writes aren't coordinated across the copies. Scaling a stateful component correctly requires either sharding (splitting the data so each copy holds a distinct, non-overlapping slice — the Z-axis approach above) or replication with a defined consistency model (read replicas, leader-based writes, and the whole apparatus covered in `ddia/07` and `ddia/08` on replication) — never naive duplication.

This is precisely why Newman (and the broader industry) pushes hard for keeping services themselves stateless wherever possible, and pushing all persistent state into well-understood, purpose-built datastores (a database, a cache, an event stream) that have their own, separately engineered scaling and consistency strategies — mixing "scale the application layer" and "scale the data layer" concerns inside one service's own process makes both problems harder to reason about and solve.

## Pros
- **X-axis (duplication + autoscaling)**: simple, fast, works well for stateless services, and can be fully automated to track real-time demand.
- **Y-axis (service decomposition)**: comes largely for free from having drawn good service boundaries (Lesson 01-03) — lets you target scaling spend exactly where the load actually is.
- **Z-axis (partitioning/sharding)**: the only real answer once data volume (not just compute) is the bottleneck, and lets a system scale well past what a single database instance could ever serve.

## Cons
- **X-axis** only works cleanly for stateless components — applying it naively to stateful components creates data divergence, as shown above.
- **Z-axis (sharding)** adds real complexity: choosing a shard key, handling cross-shard queries (which lose the simplicity of a single database's joins — echoing Lesson 07's API-composition/CQRS answers, now at the data-partition level within one service), and rebalancing when shards grow unevenly (this is exactly the problem `system-design/04`'s consistent hashing exists to minimize the cost of).
- **Autoscaling** needs careful trigger tuning — scaling too slowly under a sudden spike leaves the system overloaded during the ramp-up; scaling too aggressively on noisy metrics wastes resources and can thrash (repeatedly scaling up and down).

## Alternatives
- **Vertical scaling (bigger machines)** — increase a single instance's resources (more CPU, more RAM) rather than adding more instances. Simpler operationally (nothing to distribute or coordinate) but has a hard ceiling (the biggest machine available) and doesn't improve fault tolerance the way horizontal duplication does (one machine is still a single point of failure). Often a reasonable first step before investing in horizontal scaling infrastructure, but not a substitute for it at real scale.
- **Caching as a load-reduction strategy rather than a scaling strategy per se** — sometimes the right answer to "this service is under too much load" isn't to scale it at all, but to reduce the load it has to handle in the first place via a cache in front of it (`system-design/10`), which can be cheaper and simpler than scaling the underlying service or database further.

## When to use it
- X-axis/autoscaling: the default first lever for any stateless service under variable load.
- Y-axis: this is largely a consequence of good service decomposition (Lessons 01-03), not a separate decision — but it's worth explicitly recognizing which services need independent scaling headroom when designing boundaries.
- Z-axis/sharding: when a single datastore's data volume or query load, not application compute, is the actual bottleneck.

## When NOT to use it
- Don't reach for sharding (Z-axis) to solve a compute bottleneck in a stateless application layer — that's an X-axis problem; scale instances, don't partition data that doesn't need partitioning.
- Don't attempt to scale a stateful component by naive duplication (multiple independent writable copies with no coordination) — this doesn't "scale" it correctly, it silently introduces data divergence; use replication or sharding with an explicit consistency model instead.
- Don't over-invest in autoscaling infrastructure and tuning for a service with steady, predictable, low load — a fixed, adequately-sized instance count may be simpler and sufficient.

## Key takeaways / mental model
Three axes, three different problems: duplicate (X) for more of the same stateless work, decompose by function (Y) to target scaling spend precisely — which good service boundaries already give you — and partition data (Z) when the data itself, not just the compute, is the bottleneck. The line that matters most in practice: stateless scales by simple duplication; stateful requires solving partitioning and consistency, a genuinely harder problem that deserves purpose-built datastore techniques (replication, sharding, consistent hashing), not naive copy-and-hope.

## Self-check questions
1. Why is scaling a stateless service via horizontal duplication mechanically simple, while scaling a stateful service the same way (naive duplication) actively causes a new problem?
2. Which of the AKF scale cube's three axes does adopting microservices give you "for free," and why?
3. `inventory-service`'s application layer is CPU-bound under load, but its database is also approaching its data-volume ceiling. Which scaling axis addresses each problem, and why wouldn't the same fix work for both?
4. What autoscaling trigger would you choose for a service that consumes from an event stream and whose CPU usage doesn't correlate well with actual load, and why?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 13: "Scaling"
- Martin L. Abbott and Michael T. Fisher, *The Art of Scalability* (2nd ed., Addison-Wesley, 2015) — origin of the AKF/X-Y-Z scale cube framing.
- Related: `ddia/10` (Partitioning) and `system-design/04` (Consistent Hashing) for the deep mechanics of Z-axis sharding; `system-design/09` (Replication and Sharding in Practice) for the combined replication+sharding picture at the data layer.
