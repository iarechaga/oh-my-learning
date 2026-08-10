---
id: sre/03
subject: sre
title: "Service Level Objectives (SLOs): Target-Setting for Reliability"
slug: service-level-objectives
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 4
prerequisites: [sre/02]
created: 2026-08-10
updated: 2026-08-10
---

# Service Level Objectives (SLOs): Target-Setting for Reliability

## TL;DR
An SLO is a target value or range for an SLI over a defined time window (e.g., "99.9% of requests succeed, measured over a rolling 28 days"), chosen deliberately below 100% because perfect reliability is neither achievable nor economically justified. The SLO is the single number that later drives the error budget (`sre/04`), release policy, and alerting thresholds — choosing it wrong (too tight, too loose, or unrelated to what users actually need) undermines every mechanism downstream.

## The idea
Once you have an SLI (`sre/02`) — a real, well-defined measurement of user-visible quality — you need a target: how good does this number need to be? The naive answer, "as close to 100% as possible," is wrong for two independent reasons the book spends real effort establishing.

**First, 100% is the wrong target technically.** Every layer a request passes through — client network, DNS, load balancer, application, database, downstream dependencies — has its own non-zero failure rate. A service that depends on components that are individually 99.99% reliable cannot itself exceed the reliability of its weakest dependency chain; chasing 100% ignores basic reliability math (independent failure probabilities compound). Google's internal network, power, and hardware are not 100% reliable, so no service built on top of them can be either.

**Second, and more importantly, 100% is the wrong target economically.** Users can't perceive a difference between 99.99% and 99.999% reliability in most applications — a mobile app already flaky on cellular networks masks the difference entirely. But the *engineering cost* to go from 99.9% to 99.99% to 99.999% grows roughly exponentially (each additional "nine" typically requires redundant infrastructure, more sophisticated failover, more testing, more operational rigor). Google's summary framing: **the appropriate SLO is the one where cost of additional reliability starts to exceed the marginal benefit to users** — not zero risk, but the *right amount* of risk, deliberately chosen. This is the substance of "embracing risk" (this book's Chapter 3): unreliability up to the SLO is an accepted, budgeted cost of doing business, not a failure.

## How it works

### Choosing the SLI to attach the SLO to
Reuse the SLI definitions from `sre/02` (availability, latency, throughput, freshness) and pick the ones that matter for this specific service's users. A payments API cares deeply about availability and correctness; a video-streaming CDN cares more about latency and throughput; a nightly analytics pipeline cares about freshness and completeness, not sub-second latency at all. Don't set SLOs on SLIs users don't experience — an SLO on "CPU utilization under 80%" is not a valid SLO, because CPU utilization is not user-visible behavior.

### Setting the target number
**Worked example — a checkout API.** Suppose historical data shows the service has been running at roughly 99.95% success over the last year, and user research/support-ticket volume shows no meaningful user complaints correlate with that level. The team sets:

```
SLO: 99.9% of checkout requests succeed, measured over a rolling 28-day window.
```

Why 99.9% and not the observed 99.95%? Deliberately leaving headroom below the observed historical performance is common practice — it keeps the SLO achievable even on a bad week, and it reserves some of the "budget" (see `sre/04`) for planned risk: migrations, load tests, chaos experiments, or simply normal variance. Setting the SLO exactly at (or above) current performance leaves zero room for anything to ever go slightly wrong, which in practice means the team either constantly misses the SLO (which erodes its credibility as a target) or freezes all risk-taking to protect an unrealistically tight number.

### Latency SLOs: target + percentile, together
A latency SLO needs two numbers, not one: a threshold and a percentile. For example:

```
SLO: 99% of read requests complete in under 300ms, measured over a rolling 28 days.
```

This says nothing about the slowest 1% of requests — which is intentional. A well-designed latency SLO usually pairs a "typical case" bound (e.g., p50 or p95 with a tight threshold) with a "worst case" bound (e.g., p99.9 with a looser threshold), because a system can satisfy a p95 target while still having a badly broken tail that a single-percentile SLO would hide. **Worked example.** A search API sets two latency SLOs: "95% of queries return in <200ms" AND "99.9% of queries return in <2s." The first captures the typical experience; the second acts as a backstop against timeouts and cascading retries (`sre/14`) that a p95-only SLO would never catch, since only 1 in 1,000 requests needs to blow past 2 seconds to violate the second SLO even while the first is comfortably met.

### User-journey vs. component SLOs
A large system is made of many services calling each other. The book distinguishes:
- **User journey SLOs** — measured at the boundary the end user experiences (e.g., "page load completes"), aggregating across every internal call that journey depends on.
- **Component SLOs** — measured for one internal service in isolation (e.g., the recommendations microservice's own success rate), used so each team can be held accountable for its own slice.

**Worked example.** A product page depends on three internal services: pricing (99.95% SLO), inventory (99.9% SLO), and recommendations (99.5% SLO, since a failed recommendation degrades gracefully to "no recommendations shown" rather than failing the page). If pricing and inventory are both required for the page to render, and their failures are independent, the *best case* user-journey availability from just those two dependencies is roughly 0.9995 x 0.999 = 99.85% — already below either individual component's SLO. This is why user-journey SLOs are usually looser than the tightest component SLO in the chain, and why teams building on top of several dependencies must do this multiplication explicitly rather than assuming their own SLO alone determines the user's experience.

### Negotiating SLOs with stakeholders
SLOs are not chosen unilaterally by SRE or by engineering. The book frames them as a negotiation between: the product/business (what reliability does the product actually need to compete or retain users), engineering (what's realistic given the architecture and dependencies), and SRE (what's operationally sustainable given the team's toil budget, `sre/05`). A common anti-pattern is a business stakeholder demanding "99.999%" without understanding the cost — the SRE/engineering role is to translate that demand into a concrete cost estimate (redundant infrastructure, multi-region failover, additional headcount) so the business can make an informed trade-off, rather than accepting an aspirational number that nobody actually resources.

### Internal vs. external (contractual) SLOs
Internal SLOs (used for engineering decisions, error budgets, alerting) are usually set tighter than any externally published SLA, precisely so that an internal SLO breach gives the team time to react *before* a customer-facing contractual SLA is at risk. **Worked example.** A service might have an external SLA of 99.9% (with financial penalties for breach) but an internal SLO of 99.95% — the extra 0.05% of margin is the team's early-warning buffer.

## Pros
- Converts a vague goal ("be reliable") into a specific, falsifiable target that can drive concrete engineering and release decisions.
- Makes the reliability-vs-velocity tradeoff explicit and negotiable between stakeholders instead of an unstated assumption.
- Prevents both over-investment (chasing unnecessary nines) and under-investment (no target at all, reliability drifts down unnoticed).

## Cons
- Choosing the wrong target is easy and costly: too tight wastes engineering effort and freezes releases unnecessarily; too loose lets real user pain go unaddressed.
- Requires good historical SLI data and some understanding of user tolerance to set credibly — a brand-new service often has neither, forcing an initial guess that must be revisited.
- Multiple dependent services' SLOs must be reasoned about together (the multiplication problem above); teams that set SLOs in isolation without accounting for their dependency chain routinely produce user-journey reliability worse than any individual SLO suggests.

## Alternatives
- **No formal SLO, informal "keep it up" culture** — simpler to start, but leaves the reliability-vs-velocity tradeoff unexamined and un-negotiated; tends to default to whichever pressure (features or stability) has more organizational power at a given time. See `sre/01`.
- **Contractual SLA only, no internal SLO** — treats reliability purely as a legal/financial commitment with penalty clauses; misses the internal early-warning function an SLO gives engineering before a customer-facing breach occurs.
- **100%-uptime aspiration ("five nines everywhere")** — appealing rhetorically, but as this lesson argues, economically and technically unjustifiable for most services; usually a sign the SLO-setting conversation hasn't happened yet.

## When to use it
Set an SLO for any service with real users depending on it, especially once it's important enough to be on an on-call rotation (`sre/08`) or to warrant a release-governance conversation (`sre/12`). Revisit SLOs periodically (the book suggests reviewing quarterly or after major architecture changes) as the service, its dependencies, and user expectations evolve.

## When NOT to use it
Don't formalize an SLO for a prototype or pre-product-market-fit service where the architecture and usage pattern are still changing weekly — the target will be obsolete before it's useful, and the negotiation overhead isn't worth it yet. Also avoid setting an SLO you have no intention of enforcing (i.e., no error budget consequence when missed, see `sre/04`) — an unenforced SLO is worse than no SLO, because it creates false confidence that reliability is being managed.

## Key takeaways / mental model
An SLO answers: "how unreliable are we willing to be, on purpose, and over what window?" It is always less than 100%, deliberately, because the cost of the next nine grows faster than its benefit to users. Every SLO needs three things named explicitly: the SLI it's measured on, the numeric target, and the time window — and every user-journey SLO must account for the multiplicative effect of its dependencies' own SLOs.

## Self-check questions
1. A stakeholder asks for a "99.999% uptime" SLO for a new internal admin tool with 20 daily users. Using this lesson's reasoning about cost vs. user-perceptible benefit, how would you push back, and what would you propose instead?
2. A user-facing page depends on two backend services with SLOs of 99.9% and 99.8% respectively, called serially and independently. Compute the best-case user-journey availability and explain why the page's own SLO should not simply copy the tighter of the two component SLOs.
3. Why does the book recommend setting a latency SLO's target below what the service currently, historically achieves, rather than at or above it?
4. Explain the practical difference between an internal SLO of 99.95% and an external contractual SLA of 99.9% for the same service, and why a team would deliberately want a gap between them.

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 4 ("Service Level Objectives") and Chapter 3 ("Embracing Risk").
- See also: `sre/04` (error budgets, the mechanism SLOs feed) and `sre/12` (release engineering, which consumes error budget status).
