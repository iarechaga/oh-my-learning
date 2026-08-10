---
id: building-microservices/01
subject: building-microservices
title: "What Microservices Are (and Are Not)"
slug: what-microservices-are
status: drafted
mastery: 
seniority: mid
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 1"
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# What Microservices Are (and Are Not)

## TL;DR
A microservice is an independently deployable service, modeled around a business domain, that owns its own data. "Micro" does not mean "small in lines of code" — it means small enough in scope that one team can own it, change it, and ship it without coordinating a release with every other service. Microservices are a deliberate trade-off: you take on real operational complexity in exchange for independent deployability, and you should only make that trade when you actually need it.

## The idea
Imagine a single application — say, an online store — built as one deployable unit: one codebase, one build, one process (or one cluster of identical processes) that contains the catalog, the cart, the checkout, the inventory, and the shipping logic. This is a **monolith**. Monoliths are not automatically bad; a huge fraction of successful software is monolithic, especially early in a product's life. But as a monolith grows, a specific pain shows up repeatedly:

- **Any team's change requires the whole thing to be rebuilt, retested, and redeployed.** If the shipping team wants to ship a one-line fix, and the checkout team is mid-way through a risky refactor, the shipping team's release is entangled with checkout's risk.
- **Scaling is all-or-nothing.** If only the catalog-search code path is CPU-heavy under load, you cannot scale just that code — you must scale the entire process, wasting resources on the parts that aren't the bottleneck.
- **The codebase becomes a shared-fate structure.** Even with good modularity *inside* the codebase (separate packages, clean interfaces), nothing stops a developer from reaching across an internal boundary at compile time, because it's all one process with no enforced boundary at runtime.

Microservices are one answer to this pain: split the system into multiple services, each of which:

1. **Is independently deployable.** You can change and release Service A without releasing Service B, on a different schedule, at a different cadence, potentially by a different team, without them needing to coordinate a joint release.
2. **Is modeled around a business domain**, not a technical layer. Not "the database layer" or "the validation layer" — but "Orders," "Inventory," "Payments" — units of business capability. (Lesson 02 goes deep on *how* to find these boundaries.)
3. **Owns its own data.** No other service reaches directly into its database. All interaction happens through the service's own published interface (an API, an event stream). This is what actually enables independent deployability — if two services share a database schema, a change to that schema can break both, and you're back to coordinated releases.

The critical thing Newman stresses, and the thing people most often get wrong: **the defining property of a microservice is independent deployability, not size.** A "small" service that shares a database table with three other services is not meaningfully a microservice — it cannot be deployed independently, because a schema change ripples across all four. Conversely, a service with 20,000 lines of code that can be built, tested, and deployed entirely on its own, without touching any other service's release, satisfies the definition even though it isn't tiny.

## How it works

### The core properties, one at a time

**1. Independent deployability.** This is the load-bearing property; everything else in the definition serves it. A service is independently deployable when you can make a change to it and ship that change into production *without* requiring a change to, or a coordinated release with, any other service. Concretely, this means:
- The service has its own versioned artifact (container image, package) and its own deployment pipeline (Lesson 09).
- Its external interface (API contract, message schema) can evolve without breaking consumers, or breaking changes are managed explicitly (Lesson 12 on consumer-driven contracts).
- No other service depends on its internal implementation details, only on its published contract.

**2. Modeled around business capability.** Newman borrows this idea from Eric Evans's Domain-Driven Design: organize services around what the business *does* (place an order, manage inventory, process a payment) rather than around technical concerns (all validation code in one service, all database access in another). A "technical layers as services" split — e.g., a `ValidationService` called by everything — tends to create a service that everyone depends on and that changes for everyone else's reasons, which destroys independent deployability. A domain-oriented split tends to keep related things that change together *inside* one service boundary, and things that change independently in separate services.

**3. Owns its data.** If two services can read or write the same underlying table, then a schema migration in that table is a de facto joint release across both services, whatever the deployment tooling looks like. Data ownership is what makes the boundary real rather than nominal. (Lesson 07 covers the mechanics and consequences of this in depth.)

### What size is not

A common beginner mistake is to treat "micro" as a literal instruction to write the smallest possible services — "a service should be under 200 lines," or "one service per REST endpoint." Newman explicitly rejects this. The right size for a service is "as small as necessary to be a single, cohesive, independently releasable unit of business capability, and no smaller than that." Splitting too aggressively creates its own costs:

- More network calls per business operation, hence more latency and more failure modes to handle (Lesson 06, Lesson 14).
- More services to build, deploy, monitor, and secure (Lessons 09, 10, 13, 16) — the fixed operational overhead per service is real and non-trivial.
- Harder-to-reason-about distributed workflows, because a single business transaction that used to be one function call is now a chain of network calls across process boundaries (Lesson 08).

So "small" is a *consequence* of good boundaries (a service that does one cohesive thing tends to be smaller than one doing five unrelated things), not the *goal* itself. Chase cohesion and independent deployability; let size fall out of that.

### Worked example: a monolithic online store

Picture a single deployable "Store" application with modules for `Catalog`, `Cart`, `Checkout`, `Inventory`, `Shipping`, all sharing one Postgres database.

Symptom: the Catalog team wants to add a new search filter. To ship it, they run the full regression suite for Cart, Checkout, Inventory, and Shipping too, because they all live in the same deployable and a bug anywhere blocks the release train. Deploys happen once every two weeks, coordinated across five teams, because nobody wants to be the team that broke the shared release.

A microservices decomposition (candidate boundaries, driven by business capability — see Lesson 02 for the method): `catalog-service`, `cart-service`, `checkout-service`, `inventory-service`, `shipping-service`, each with its own database, its own repo (or its own clearly bounded directory with its own pipeline), and its own deployment cadence. Now:
- The Catalog team ships the search filter the moment it's ready, without waiting on the other four teams.
- Inventory, which experiences huge read load during flash sales, can be scaled to 20 instances while Shipping stays at 2 — impossible when they were one process.
- A bug in Shipping's code cannot corrupt Catalog's data, because Shipping cannot touch Catalog's database at all.

But note the new costs: Checkout now calls Inventory and Cart over the network to build an order, which used to be in-process function calls (Lesson 05, Lesson 06); a checkout that used to be a single database transaction is now a workflow across three services with independent failure and consistency (Lesson 08); and there are now five pipelines, five sets of dashboards, and five services' worth of on-call surface to build (Lessons 09, 10, 13) instead of one.

### The trade-off is the point

Newman's stance, repeated throughout the book, is: **microservices are not free, and you should not adopt them by default.** The independent deployability they buy you is valuable specifically when:
- Multiple teams need to ship independently without blocking each other.
- Different parts of the system have genuinely different scaling profiles.
- Parts of the system have different technology needs or different rates of change.

If none of those pressures exist — a small team, a system with a single natural release cadence, uniform load — a monolith (ideally a *modular* monolith, with clean internal boundaries that could later be extracted) is very often the right call, and adopting microservices prematurely just adds the operational tax described above without buying the benefit.

## Pros
- **Independent deployability** — teams ship on their own schedule without coordinating a joint release.
- **Independent, targeted scaling** — scale only the service under load, not the whole system.
- **Fault and blast-radius isolation** — a bug or crash in one service does not directly corrupt another service's process or data (though it can still cause cascading failures over the network — see Lesson 14).
- **Technology heterogeneity** — each service can pick the language/datastore best suited to its problem (a real option, but Newman cautions against over-using it — more languages means more operational surface).
- **Team autonomy and ownership** — a team can own a service end-to-end, from code to production (this connects directly to Lesson 17, Conway's Law).

## Cons
- **Distributed systems complexity** — network calls fail in ways function calls don't (partial failure, latency, timeouts); this is the single biggest cost and it never fully goes away (Lesson 06, Lesson 14).
- **Operational overhead per service** — every service needs its own pipeline, monitoring, logging, and on-call story; N services means roughly N times the fixed operational cost (Lessons 09, 10, 13).
- **Data consistency gets harder** — no more single-database ACID transactions across the whole workflow; you now reach for sagas and eventual consistency (Lesson 07, Lesson 08).
- **Harder end-to-end reasoning and testing** — a single user request may now touch many services, making it harder to trace, test, and debug (Lesson 11, Lesson 13).
- **Premature decomposition is expensive to undo** — wrong service boundaries chosen early are genuinely painful to redraw later, more so than restructuring modules inside a monolith.

## Alternatives
- **Monolith (single deployable unit)** — everything ships together. Right default for small teams, early-stage products, or systems without differentiated scaling/team needs. Much lower operational overhead; the cost is coordinated releases and all-or-nothing scaling.
- **Modular monolith** — one deployable unit, but with strong internal module boundaries (enforced via package structure, internal APIs, and discipline) that make each module a *candidate* microservice later. Newman recommends this as a common starting point: get the boundaries right in-process first, where mistakes are cheap to fix, before paying the network cost of splitting them out.
- **Macroservices / a small number of coarser services** — a middle ground: split along the biggest, clearest seams (e.g., 3-4 services) without decomposing all the way to fine-grained business capabilities. Reduces network chatter and operational count versus "full" microservices, at the cost of somewhat less team autonomy.

## When to use it
- Multiple teams need to release independently and are currently blocked on each other by a shared deployable.
- Different parts of the system have clearly different scaling, availability, or compliance requirements that are hard to satisfy in one process.
- The organization is large enough to absorb the fixed per-service operational cost (tooling, on-call, pipelines) without it dominating engineering time.
- You have (or are willing to build) the operational maturity — CI/CD, monitoring, on-call practices — that microservices assume as a baseline (Newman is explicit that this maturity should generally come *before* the migration, not after).

## When NOT to use it
- A small team (a handful of engineers) with one release cadence and no differentiated scaling needs — the coordination problem microservices solve doesn't exist yet, so you'd be paying the distributed-systems tax for nothing.
- Early-stage products where the domain model is still churning — service boundaries drawn around a not-yet-understood domain are likely to be wrong, and wrong boundaries are expensive to fix once services are split (Lesson 03).
- Teams without basic CI/CD, monitoring, and automated deployment maturity — microservices amplify the cost of not having these, rather than being a reason to finally get them.
- When the actual goal is just "better internal code organization" — a modular monolith gets you that without the network and operational costs.

## Key takeaways / mental model
Microservices are defined by **independent deployability**, not by size. The mental model: a microservice is a business capability wrapped in a deployment boundary you can cross alone. Everything else — small size, one team per service, polyglot tech — is a common *consequence* of good boundaries, not the definition itself. Treat the decision to adopt microservices as an explicit trade: real complexity now, in exchange for independent deployability and scaling later — and only make that trade when you're actually blocked by the monolith's coordination costs.

## Self-check questions
1. Two services share a single database table and neither can change its schema without coordinating with the other. Are they microservices by Newman's definition? Why or why not?
2. A team splits a monolith into 40 tiny services, each under 100 lines, but every business transaction now requires calls across 8 of them. What did they optimize for, and what did they likely sacrifice?
3. Give two concrete organizational or technical signals that would tell you a system is ready to benefit from splitting into microservices, and two signals that say "not yet."
4. Why does Newman recommend that CI/CD and monitoring maturity generally come *before* a microservices migration rather than after?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 1: "What Are Microservices?"
