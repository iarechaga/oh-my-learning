---
id: building-microservices/04
subject: building-microservices
title: "Splitting the Monolith (Migration Patterns)"
slug: splitting-the-monolith
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapters 2 and 3 (migration patterns)"
prerequisites: [building-microservices/01, building-microservices/02, building-microservices/03]
created: 2026-08-10
updated: 2026-08-10
---

# Splitting the Monolith (Migration Patterns)

## TL;DR
Migrate a monolith to microservices incrementally, one seam at a time, keeping the system releasable throughout — never a big-bang rewrite. The **strangler fig pattern** (intercept and gradually redirect traffic to a new service while the old code path still exists) and **branch by abstraction** (insert a seam inside the codebase, implement the new path behind it, cut over, then delete the old path) are the two core techniques; **parallel run** lets you verify the new service produces the same results as the old code before trusting it. Extract the pieces with the *least* coupling to the rest of the system first.

## The idea
Lessons 01-03 established what a good service boundary looks like. This lesson is about the much harder practical question: how do you get from an existing, live, revenue-generating monolith to a set of services with those boundaries, without a multi-month "stop the world" rewrite that risks the business?

The temptation is the **big-bang rewrite**: freeze the monolith, build the new microservices architecture in parallel over months, then cut over all at once. Newman treats this as close to an anti-pattern, for reasons that are less about elegance and more about risk:

- The old system keeps needing bug fixes and small features while the rewrite is underway, so the target keeps moving — the rewrite is chasing a moving system, not a snapshot.
- All the risk is concentrated in one enormous cutover event. If anything is wrong, you don't have a good way to roll back a fraction of it — it's often all-or-nothing.
- You get no feedback from production for months. Wrong assumptions about service boundaries (Lesson 02, Lesson 03) compound silently until the cutover, when they all surface at once.
- The business sees zero incremental value for a long time, which makes the investment hard to justify and easy to deprioritize when priorities shift.

The alternative Newman advocates throughout the book is **incremental extraction**: peel one piece off the monolith at a time, ship it, learn from it, and let that experience inform the next extraction. The system stays releasable and valuable throughout, and each extraction is a small, reversible bet rather than one enormous irreversible one.

## How it works

### The strangler fig pattern

Named after the strangler fig vine, which grows around a host tree, gradually taking over its structure until the original tree can be removed while the fig continues to stand on its own. Applied to software: you build the new service *alongside* the monolith, and gradually intercept and redirect the calls that used to go to the monolith's old code path toward the new service, until nothing calls the old path anymore — at which point you delete it.

Mechanically, this usually requires a routing layer in front of the monolith (a reverse proxy, an API gateway, or in-application routing logic) that can send a given request either to the old monolith code or to the new service, based on a rule you control (e.g., by URL path, by customer ID, by feature flag).

**Worked example: extracting `inventory-service` from a monolith.**

1. **Before:** All requests to `/inventory/*` hit the monolith's `InventoryController`, which reads/writes the shared `inventory` table directly.
2. **Step 1 — stand up the new service, dark.** Build `inventory-service` with its own database, seeded from a one-time export of the monolith's `inventory` table. It is deployed to production but receives no real traffic yet — you might send it a shadow copy of read traffic to sanity-check its responses against the monolith's (this shadowing is a form of parallel run, below).
3. **Step 2 — put a router/proxy in front of `/inventory/*`.** Initially the router forwards 100% of traffic to the monolith, unchanged. This step alone is low-risk and worth doing early, because it gives you the seam you'll use for every subsequent step.
4. **Step 3 — redirect reads first.** Reads are lower-risk than writes (no risk of data divergence from a botched write). Redirect `GET /inventory/*` to the new service. Keep writes going to the monolith, and keep the new service's database in sync via a data-sync job or by having the monolith publish stock-change events that `inventory-service` consumes (foreshadowing Lesson 07's database-per-service pattern). Monitor closely; if something's wrong, flip the router back to the monolith instantly.
5. **Step 4 — redirect writes.** Once reads have been solid in production for a reasonable bake-in period, redirect `POST/PUT /inventory/*` to the new service too. Now `inventory-service` is the sole owner of inventory data; the monolith's `InventoryController` and its access to the `inventory` table become dead code.
6. **Step 5 — delete the dead code and the old table access from the monolith.** This step is easy to skip under time pressure, but skipping it is how monoliths accumulate permanent "zombie" code paths — do this as part of the same piece of work, not as a someday cleanup.

At every step, the monolith and the new service coexist and the system is fully releasable; you can pause between any two steps for weeks if priorities shift, and you can always route back to the monolith if the new service misbehaves.

### Branch by abstraction

Strangler fig works well when you can intercept traffic *externally* (at a router/proxy). Sometimes the thing you need to replace is deep *inside* the monolith's codebase — e.g., swapping out a tightly-embedded payment-processing module for a call to a new `payment-service` — where there's no natural external routing point. **Branch by abstraction** solves this from inside the code:

1. Introduce an abstraction (an interface) in front of the existing implementation, e.g. a `PaymentProcessor` interface, with the current in-process logic as one implementation (`LegacyPaymentProcessor`).
2. Change every call site in the monolith to go through the new interface instead of calling the legacy code directly. At this point, behavior is unchanged — you've only added a seam.
3. Build a second implementation (`PaymentServiceClient`) that calls the new external `payment-service` instead. Develop and test it behind a feature flag, without disturbing the live `LegacyPaymentProcessor` path.
4. Flip the flag for a subset of traffic (or all of it) to route through `PaymentServiceClient` instead. Because both implementations satisfy the same interface, this is a controlled, reversible switch, not a rewrite of every call site.
5. Once `PaymentServiceClient` is proven in production, delete `LegacyPaymentProcessor` and the abstraction can be simplified or removed.

The key advantage over a raw feature branch (in the git sense) that lives unmerged for weeks: branch by abstraction keeps the change trunk-based and continuously integrated — the abstraction and both implementations live in `main` throughout, avoiding a giant, risky, hard-to-review merge at the end. This is the same idea used in the "dark launch" and feature-flag literature more broadly.

### Parallel run

For the riskiest extractions — usually ones involving money, compliance, or hard-to-reverse actions — you often want stronger evidence than "it worked in a quick manual test" before trusting the new service with real traffic. **Parallel run** means executing *both* the old and new implementations for the same request, comparing their outputs, and only trusting (serving) the old result while you build confidence, or vice versa — silently, without the user noticing.

Worked example: extracting a `pricing-service` that computes order totals including tax and discounts, previously computed inline in the monolith's checkout code. For each real checkout, you run both the monolith's existing pricing logic and the new `pricing-service`'s logic, log both results, and continue to serve the monolith's number to the customer. An automated comparison job flags any divergence between the two for investigation. Only once divergences have dropped to zero (or to an accepted, understood residual, e.g. floating-point rounding differences you've reconciled) do you flip to serving the new service's result. This catches subtle bugs — an edge case in tax calculation for a specific state, say — before they ever reach a real customer, at the cost of running both code paths (extra compute, extra complexity) for the duration of the verification period.

### Choosing extraction order: pull the loosest threads first

A recurring question when facing a large monolith: which piece to extract *first*? Newman's guidance, consistent with the coupling analysis from Lesson 03: **extract the parts with the least coupling to the rest of the system first.** Concretely://
- Prefer modules that are already relatively self-contained internally (high cohesion) and have few, well-defined interaction points with the rest of the code (low coupling) — these are the cheapest to cut cleanly and the least likely to surface hidden dependencies mid-extraction.
- Prefer modules whose data is not deeply entangled with other modules' data (no complex joins across their tables) — this avoids the hardest part of Lesson 07's database-splitting problem up front.
- Consider extracting a module that's a source of pain right now (a hotspot for bugs, or a part under disproportionate scaling pressure) — even modest coupling, the extraction pays for itself quickly in reduced risk or freed-up scaling.
- Deliberately avoid starting with the most tangled, most central part of the domain (often something like "Order" or "Customer" in an e-commerce system) — that's exactly the piece with the most hidden coupling, and a failed first extraction there can sour the whole migration effort's credibility. Build extraction experience and tooling on easier pieces first, then tackle the hard core once the team has a proven playbook.

## Pros
- **Keeps the system releasable and valuable throughout the migration** — no long freeze, no single high-stakes cutover.
- **Each step is small and reversible** — a bad extraction can be rolled back by flipping a router or a feature flag, not by reverting a multi-month rewrite.
- **Generates real production feedback early**, which corrects wrong assumptions about boundaries (Lesson 02, Lesson 03) before they compound.
- **Builds organizational muscle and tooling incrementally** — the second and third extractions get faster because the team has learned from the first.

## Cons
- **Slower to reach a "fully microservices" end state** than a big-bang rewrite would be *if* the big-bang rewrite actually worked — incremental migration is a marathon, and sustaining momentum and buy-in across many small steps is a real organizational challenge.
- **Temporary complexity during migration** — running strangler-fig routing logic, dual-write/dual-read sync jobs, and parallel-run comparison infrastructure is itself extra code that must eventually be torn down; skipping the teardown step leaves permanent cruft.
- **Requires careful handling of data during the transition** (Step 3/4 above) — keeping two data stores in sync during a phased cutover is genuinely tricky and is often the hardest part of any single extraction.

## Alternatives
- **Big-bang rewrite** — build the whole new system in parallel and cut over once. Occasionally justified for a small system with low risk tolerance for prolonged migration overhead, but Newman treats it as the default anti-pattern for anything of meaningful size, for the reasons above.
- **Greenfield-only microservices** — for genuinely new products with no existing monolith, none of this migration machinery is needed; you can design service boundaries from the start using Lesson 02's approach. This lesson's techniques apply specifically to systems that already exist.

## When to use it
- Any migration of an existing, live monolithic system to microservices — the strangler fig plus branch-by-abstraction combination is the default toolkit.
- Especially valuable when the system cannot tolerate downtime or a long feature freeze during migration (which is most production systems).
- Parallel run specifically for high-risk extractions involving money, compliance, or hard-to-reverse business actions.

## When NOT to use it
- A small, low-traffic, low-risk system where a clean rewrite is genuinely faster and the cost of being wrong is low — the overhead of strangler-fig routing infrastructure may not be worth it.
- When the domain model itself is still actively churning (see Lesson 01/02) — extracting services around boundaries you don't trust yet just locks in bad boundaries faster; better to stabilize the domain understanding first, even if that means staying monolithic a while longer.

## Key takeaways / mental model
Never bet the whole migration on one cutover. Think "strangler fig, not surgery": grow the new service alongside the old code, redirect traffic to it a slice at a time (reads before writes, low-risk before high-risk), verify with parallel runs where the stakes are high, and only delete the old path once nothing depends on it anymore. Pull the loosest threads first — extract the least-coupled, least-central pieces before tackling the tangled core, so the team builds a proven playbook on low-risk extractions before it needs one for the hard ones.

## Self-check questions
1. Why does Newman treat the big-bang rewrite as close to an anti-pattern, even when the target architecture is well understood in advance?
2. Walk through the five-step strangler fig extraction of `inventory-service` above. At which step is the system most exposed to risk, and what makes that step reversible?
3. What problem does branch by abstraction solve that a purely external strangler-fig router cannot, and what is the mechanism it uses instead?
4. You must extract five modules from a monolith. How would you decide which one to extract first, and why is starting with the most central, most tangled module (e.g. "Order") usually the wrong choice?
5. When would you reach for a parallel run instead of just extracting and monitoring in production? What does it catch that monitoring alone would not?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 2 ("The Evolutionary Architect") and Chapter 3 migration guidance; Newman's earlier book *Monolith to Microservices* (O'Reilly, 2019) covers this material in much greater depth and is the direct source for the strangler fig, branch-by-abstraction, and parallel-run patterns as applied to microservices migrations.
- Martin Fowler, "StranglerFigApplication" (martinfowler.com) — origin reference for the pattern name and mechanics.
