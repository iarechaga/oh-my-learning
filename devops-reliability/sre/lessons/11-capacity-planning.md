---
id: sre/11
subject: sre
title: Capacity Planning and Demand Forecasting
slug: capacity-planning
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 20
prerequisites: [sre/03]
created: 2026-08-10
updated: 2026-08-10
---

# Capacity Planning and Demand Forecasting

## TL;DR
Capacity planning is deliberately provisioning enough headroom, in the right places (compute, but also often the more binding constraints — network, storage I/O, or a specific downstream dependency's limits), ahead of demand growth and correlated failure scenarios, so the service can meet its SLO (`sre/03`) even during the worst realistic day, not just an average one. Under-provisioning risks SLO breaches under load; over-provisioning wastes real money — capacity planning is finding the deliberate, calculated middle.

## The idea
A service that's perfectly sized for its *average* load will fail regularly, because real traffic isn't average — it has daily and weekly cycles (peak evening hours, weekday-vs-weekend), seasonal spikes (holiday shopping, a product launch, a viral event), and correlated failure scenarios (losing an entire datacenter or region means the remaining capacity must absorb all of that region's traffic). Capacity planning is the discipline of provisioning for the demand and failure scenarios that actually matter, not for the comfortable average case.

The book frames this as a genuine cost/reliability trade-off, structurally identical to the SLO trade-off in `sre/03`: more headroom means fewer SLO breaches under load spikes, but headroom that sits idle most of the time is real, ongoing infrastructure spend that could have funded something else. Getting this trade-off right requires quantitative forecasting, not "add servers when things feel slow."

## How it works

### The headroom calculation
A basic capacity plan starts from three numbers: current peak demand, projected demand growth, and the target failure scenario to survive.

**Worked example.** A service currently peaks at 8,000 requests/second on its busiest hour of the week. Each server in the fleet can sustain 200 requests/second at the target latency SLO before saturation degrades response time. Current fleet size needed for peak: `8,000 / 200 = 40 servers`. The team wants to survive losing one of three availability zones entirely (an N+1-per-two-remaining-zones redundancy target, i.e., the two remaining zones must absorb the full peak load): if the 40 servers are spread evenly across 3 zones (about 13.3 each), losing one zone leaves ~26.7 servers, or `26.7 x 200 = 5,340 requests/second` capacity — well short of the 8,000 req/sec peak. To survive a zone loss at peak, the fleet needs total capacity such that any 2 of 3 zones alone can handle 8,000 req/sec: that means total fleet capacity must be at least `8,000 / (2/3) = 12,000 req/sec`, or `12,000 / 200 = 60 servers` (20 per zone) — 20 more servers than the naive average-load sizing, purely to survive one correlated failure scenario.

### Forecasting demand growth
Headroom for *today's* peak isn't enough if demand is growing — capacity plans need a growth projection, typically derived from historical trend plus known upcoming events (a marketing campaign, a new market launch). **Worked example.** If the service above has grown 8% quarter-over-quarter for the last four quarters, a conservative 2-quarter-ahead capacity plan multiplies the zone-loss-adjusted target by `1.08^2 ≈ 1.166`: `60 x 1.166 ≈ 70 servers` needed by two quarters from now, informing a procurement or autoscaling-limit decision made well ahead of actually needing the capacity (since server or quota procurement often has its own lead time — the book stresses that lead time itself is a capacity-planning input, not an afterthought).

### Load testing to validate assumed per-unit capacity
The "200 requests/second per server" figure in the example above isn't something to assume — it must be measured under realistic conditions, because a server's real sustainable throughput before SLO-violating latency kicks in depends on the actual request mix, cache hit rates, and downstream dependency behavior, none of which a synthetic benchmark reliably captures on its own. The book recommends periodic load testing against production-like traffic patterns specifically to keep the per-unit capacity assumption honest, because architecture changes (a new caching layer, a schema change, a new feature with a heavier query) silently shift this number over time without anyone noticing until a real peak reveals the drift.

### Non-compute bottlenecks
A common capacity-planning mistake is sizing only the most visible resource (application server count) while ignoring a less visible but equally binding constraint. **Worked example.** The 60-server fleet above might be individually well within CPU limits at 8,000 req/sec, but if each request makes 3 downstream calls to a shared database, that's 24,000 queries/second hitting the database — if the database's connection pool or I/O capacity caps out at 18,000 queries/second, the database (not the application servers) is the actual binding constraint, and no amount of adding application servers fixes the SLO violation; the capacity plan must include the database tier's own headroom calculation, load-tested independently.

### Graceful degradation as a capacity-planning tool
Not every part of a product needs full capacity to survive every failure scenario. The book recommends identifying which features can degrade gracefully (return a cached or simplified response) under extreme load, reducing the total headroom needed for a full-fidelity response everywhere. **Worked example.** The recommendations feature from `sre/03`'s worked example (already designed with a looser SLO because it can degrade to "no recommendations shown") lets the team deliberately under-provision that specific dependency relative to the core page-render path, redirecting the saved infrastructure spend toward the pricing and inventory services that can't degrade without breaking checkout entirely.

### Reviewing and updating the plan
Capacity plans decay: a plan based on last year's traffic pattern and last year's per-server throughput assumption becomes wrong as both drift. The book recommends a regular review cadence (commonly quarterly), re-running the headroom calculation with current numbers, and treating a capacity review as a standing item much like the SLO review mentioned in `sre/03`, rather than a one-time exercise done at launch and never revisited.

## Pros
- Converts "do we have enough servers?" from an anxious guess into a calculable, defensible number tied directly to the SLO and named failure scenarios.
- Explicitly accounts for correlated failures (zone/region loss) rather than only average-case sizing, which is the scenario that actually causes the worst SLO breaches when ignored.
- Surfaces non-obvious bottlenecks (a downstream database, a shared rate limit) that server-count-only planning misses.

## Cons
- Requires ongoing load testing and demand forecasting investment to keep the underlying per-unit capacity and growth assumptions accurate — a stale capacity plan can be worse than no plan, since it creates false confidence.
- Provisioning for low-probability, high-impact failure scenarios (a full zone loss) means paying for real headroom that sits mostly idle, a genuine and sometimes hard-to-justify ongoing cost.
- Forecasting demand growth is inherently uncertain; a plan built on a smooth trend line can be badly wrong when growth is actually driven by lumpy, hard-to-predict events (a viral moment, a competitor's outage driving traffic your way).

## Alternatives
- **Pure reactive autoscaling with no forward capacity plan** — scales infrastructure to current demand automatically, reducing idle-headroom cost, but is vulnerable to demand spikes that outpace scale-up speed (autoscaling has a reaction lag) and to correlated failures that reduce available capacity exactly when demand is high; usually best used *alongside* a baseline capacity plan, not as a full replacement for one.
- **Massive fixed overprovisioning ("just buy way more than we need")** — simple and robust to forecasting error, but wastes significant ongoing infrastructure spend and provides no discipline about *where* the extra capacity is actually needed (may overprovision compute while a downstream database remains the real bottleneck).
- **On-demand cloud bursting only during known peak events** — provisions extra capacity just-in-time for predictable events (e.g., a sale day), reducing idle cost relative to fixed overprovisioning, but doesn't help with unpredictable spikes or sudden correlated failures outside the planned window.

## When to use it
Do formal, quantified capacity planning for any service with a real SLO (`sre/03`) and non-trivial infrastructure cost, especially ahead of known high-demand events and as a standing quarterly review. Always test the per-unit capacity assumption against realistic traffic rather than trusting a synthetic benchmark, and check for non-compute bottlenecks explicitly.

## When NOT to use it
Don't build an elaborate capacity-planning process for a service with negligible cost, negligible traffic variance, and no meaningful SLO — reactive autoscaling with generous limits is simpler and sufficient. Also avoid capacity plans that only account for average or even peak demand without considering correlated failure scenarios (zone/region loss) if the service genuinely needs to survive one — that's the scenario formal capacity planning exists specifically to catch.

## Key takeaways / mental model
Capacity planning answers: "how much headroom, where, to survive the worst realistic combination of demand and failure — not just an average day?" Measure real per-unit capacity (don't assume it), account for correlated failures explicitly (losing a zone concentrates load on the survivors), check every tier for the actual binding constraint (not just the most visible one), and revisit the plan on a cadence, because the underlying assumptions decay.

## Self-check questions
1. A service peaks at 6,000 req/sec, each server handles 150 req/sec, spread evenly across 4 availability zones. Compute the fleet size needed to survive losing one zone entirely at peak, and compare it to the naive (no-zone-loss) sizing.
2. Explain why load testing to validate per-server throughput is necessary even if the application code hasn't changed recently. What kinds of changes could silently shift that number?
3. A team sizes its application-server fleet carefully but never checks the shared database's connection pool limit. Describe a realistic scenario where their capacity plan fails despite the application tier having plenty of headroom.
4. Why does designing a feature for graceful degradation (per `sre/03`'s recommendations-service example) reduce the total capacity-planning burden on the rest of the system?

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 20 ("Load Balancing in the Datacenter").
- See also: `sre/03` (SLOs, the target capacity planning is provisioning to meet) and `sre/14` (handling overload, for what happens when capacity planning falls short in practice).
