---
id: microservices-patterns/02
subject: microservices-patterns
title: "Decomposition Strategies (by Capability and Subdomain)"
slug: decomposition-strategies
status: drafted
mastery:
seniority: senior
source: "Microservices Patterns (Chris Richardson), Chapter 2"
prerequisites: [microservices-patterns/01]
created: 2026-07-01
updated: 2026-07-01
---

# Decomposition Strategies (by Capability and Subdomain)

## TL;DR
The hardest and most consequential decision in a microservice architecture is *where to draw the service boundaries* - get it wrong and you build a distributed monolith that has all the pain of microservices and none of the benefit. Two disciplined strategies exist: decompose by **business capability** (what the business does) and decompose by **subdomain** (the DDD approach - carve the domain into subdomains, each becoming a bounded context and a service). Both aim at the same target: services that are loosely coupled and highly cohesive, aligned to the business rather than to technical layers, so each can change independently.

## The idea
Lesson 01 established *why* to split a monolith. This lesson is about the far harder question: *along which seams?* Boundaries are the defining architectural choice because they are expensive to move later (relocating logic and data across services is a migration, not a refactor) and because bad boundaries silently destroy the entire value proposition.

The failure mode has a name: the **distributed monolith**. If you cut the system in the wrong places, services end up tightly coupled - every business operation requires a chatty dance across many services, a single change forces coordinated redeployment of several services at once, and you cannot deploy or reason about any service in isolation. You now pay the full distributed-systems tax (network, split data, sagas) *and* still cannot deploy independently. That is strictly worse than the monolith you left.

So the goal of decomposition is precise: **loose coupling between services and high cohesion within each service.** A service should contain everything that changes together (cohesion) and depend as little as possible on the internals of others (coupling). Two strategies give you a principled way to find such boundaries instead of guessing:

1. **Decompose by business capability** - identify what the business *does* and make each capability a service.
2. **Decompose by subdomain** - use Domain-Driven Design to break the problem domain into subdomains, each becoming a bounded context, each a service.

They are complementary lenses that usually converge on similar boundaries; the book teaches both and uses them together.

## How it works

### The real objective: coupling and cohesion, aligned to the business
Before the strategies, fix the yardstick. Good boundaries maximize **cohesion** (things that change for the same reason live together) and minimize **coupling** (a service rarely needs to know or call into another to do its job). The corollary Richardson stresses: **decompose by business concern, not by technical layer.** A "presentation service," "business-logic service," and "data-access service" tier is an anti-pattern - a single feature change (add a field to orders) would ripple through all three, so they are tightly coupled and must deploy together. Slicing *vertically* by capability (an Order service that owns order UI-facing API, logic, and data) keeps a feature's change inside one service.

```text
   WRONG (horizontal layers):        RIGHT (vertical capabilities):
   +----------------------+          +--------+ +--------+ +--------+
   | Presentation service |          | Order  | |Kitchen | |Delivery|
   +----------------------+          | (api+  | | (api+  | | (api+  |
   | Business-logic svc   |          |  logic+| |  logic+| |  logic+|
   +----------------------+          |  data) | |  data) | |  data) |
   | Data-access service  |          +--------+ +--------+ +--------+
   +----------------------+          one feature change stays in ONE service
   one change ripples through all 3
```

### Strategy 1: decompose by business capability
A **business capability** is something a business does to generate value - Order Management, Restaurant Management, Delivery Management, Billing, Consumer Management. You identify capabilities by analyzing the organization's purpose, structure, and processes (they tend to be stable over time because *what* a business does changes slowly, even as *how* it does it changes constantly). Each capability - possibly with sub-capabilities - maps to a service.

Why it works: capabilities are cohesive by construction (everything about "delivery" belongs to Delivery) and stable (so boundaries drawn on them age well). Because they mirror what the business actually does, they also tend to align with team structure (Conway's law), which is exactly what you want for independent teams.

The output is a first-cut service-per-capability decomposition, which you then refine.

### Strategy 2: decompose by subdomain (the DDD approach)
Domain-Driven Design offers a sharper tool. You break the **problem domain** into **subdomains**, classified by strategic importance:

- **Core subdomain** - the differentiator, where you must excel (for FTGO, order-taking and delivery logistics). Invest your best design here.
- **Supporting subdomain** - necessary but not a differentiator (restaurant menu management).
- **Generic subdomain** - a solved problem you could buy/adopt (billing, notifications, auth).

Each subdomain gets its own **bounded context**: an explicit boundary within which a domain model and its **ubiquitous language** are consistent and unambiguous. This is the crucial DDD idea for microservices: the *same word means different things in different contexts*, and a bounded context makes that explicit rather than forcing one global model.

A microservice is then implemented as a bounded context (or a small set of them). Because each bounded context has its *own* model, you avoid the "one giant shared domain model" that couples everything - each service models `Order` the way *its* context needs, and they integrate through published contracts, not a shared class.

```text
Domain: Food Delivery
 +-----------------------------------------------------------+
 | Core:        Order-taking      |  Delivery logistics       |
 |              (bounded context) |  (bounded context)        |
 |-----------------------------------------------------------|
 | Supporting:  Restaurant/menu mgmt (bounded context)        |
 |-----------------------------------------------------------|
 | Generic:     Billing (bc)  |  Notification (bc)  | Auth(bc)|
 +-----------------------------------------------------------+
   each bounded context -> a service with its OWN model + language
```

### The same concept, different in each context: why bounded contexts matter
The payoff of the subdomain approach is handling the fact that a business "thing" is not one thing. In FTGO, an **Order** means different data in different contexts:

- In **Order-taking**, an Order is line items, the consumer, payment authorization, delivery address.
- In the **Kitchen** context, the relevant view is a *Ticket*: just the items to prepare and their prep status - it does not care about payment.
- In **Delivery**, the relevant view is a *Delivery*: pickup location, drop-off, courier, and timing - it does not care about menu details or price.
- In **Accounting**, it is a set of financial events.

Forcing all four into one shared `Order` class (the monolith's habit) couples all four teams to every change. Bounded contexts let each service keep the *slice* it needs (`Order`, `Ticket`, `Delivery`, `Invoice`) and integrate via events/APIs. This is the single most important reason the subdomain lens beats naive noun-hunting.

### Obstacles and guardrails
Real decomposition hits practical walls the book calls out:

- **Network latency** can make a set of boundaries impractical - if operation X requires 6 hops, you may need to merge services or move data.
- **Synchronous coupling reduces availability** - if A must synchronously call B, C, and D to answer a request, A is only as available as the *least* available of them. Prefer async messaging or replicate data to cut this (later lessons).
- **Consistency across boundaries** - a boundary that splits data needing a single ACID transaction will force a saga; sometimes the right move is to *not* split there (keep that data in one service). Boundaries and transaction requirements interact.
- **God classes** - a central class touched by everything (like `Order`) signals a place where the subdomain lens is needed to split it per-context, rather than a single service owning it all.

The rule of thumb: draw boundaries by capability/subdomain first, then *pressure-test* them against latency, availability, and consistency, and adjust.

### Worked example 1: FTGO first-cut decomposition by capability
Starting from the FTGO monolith, identify capabilities and map to services.

1. Analyze what the business does: taking orders, managing restaurants/menus, preparing food, delivering food, billing, managing consumers and couriers.
2. First-cut services: `Order Service`, `Restaurant Service`, `Kitchen Service`, `Delivery Service`, `Accounting Service`, `Consumer Service`, `Courier Service`.
3. Each owns its data and API. `Order Service` owns orders; `Kitchen Service` owns tickets; no service reads another's database.
4. Sanity check cohesion: everything about billing is in `Accounting`; everything about food prep is in `Kitchen`. A change to prep workflow touches only `Kitchen`. Good.
5. This is a *starting point*, not the final answer - the next steps refine it with the subdomain lens and the guardrails.

### Worked example 2: splitting the "Order" god class with bounded contexts
The first cut leaves a tension: several services all seem to need "the order." Applying the subdomain lens:

1. Recognize `Order` is a **god class** - a single monolithic concept the whole system leans on.
2. Instead of one `Order Service` owning a universal `Order`, define each context's own model:
   - `Order Service` (Order-taking core): `Order` = items + consumer + payment auth + address, with a state machine (PENDING -> APPROVED -> ...).
   - `Kitchen Service`: `Ticket` = items + prep status. It learns about new work via an event from Order Service, not by sharing the `Order` object.
   - `Delivery Service`: `Delivery` = pickup, dropoff, courier, ETA.
   - `Accounting Service`: financial events (charge authorized, charge captured).
3. Integration is by **domain events**: when `Order Service` approves an order, it publishes `OrderApproved`; `Kitchen` creates a `Ticket`, `Delivery` schedules a `Delivery`. No shared class, no shared table.
4. Result: a change to how the kitchen tracks prep status touches only `Kitchen Service`'s `Ticket` model - the coupling that a shared `Order` class would have imposed is gone. This is precisely what the bounded-context boundary buys.

### Worked example 3: a boundary that creates a distributed monolith, and the fix
Suppose an architect decomposes by *technical noun* instead: a `Validation Service`, a `Pricing Service`, and a `Persistence Service`, all invoked to place one order.

1. Placing an order now requires `Order UI -> Validation -> Pricing -> Persistence` synchronously in sequence - 3+ network hops for one operation.
2. Availability collapses: order placement works only if *all three* are up. If each is 99.5% available, the chain is ~98.5% - worse than a monolith.
3. Any change to the order flow (add a discount rule) spans `Pricing` and `Validation` and maybe `Persistence`, forcing a coordinated multi-service deploy - the distributed monolith.
4. The fix is to re-decompose by *capability*: a single `Order Service` owns validation, pricing, and persistence *for orders* internally (in-process, fast, one deploy), and integrates with genuinely separate capabilities (`Kitchen`, `Delivery`) via events. The chatty, fragile boundaries vanish because the cohesive logic is back inside one service.

This is the cautionary example that shows *why the strategy matters*: capability/subdomain boundaries produce independence; arbitrary or technical-layer boundaries produce a distributed monolith.

## Pros
- **Loosely coupled, highly cohesive services** when done well - a feature change stays inside one service, enabling true independent deployment.
- **Business-aligned and stable boundaries** - capabilities/subdomains change slowly, so boundaries drawn on them age better than technical or arbitrary ones.
- **Bounded contexts eliminate the shared-model coupling** - each service models a concept the way its context needs, integrating via contracts/events rather than a god class.
- **Aligns with teams (Conway's law)** - capability/subdomain boundaries tend to match team boundaries, supporting autonomy.

## Cons
- **Boundaries are hard to get right and expensive to move** - a wrong cut is a costly migration later, not a cheap refactor.
- **Requires deep domain understanding** - you cannot decompose well what you do not yet understand; premature decomposition mis-cuts.
- **Guardrail tensions** - latency, availability, and cross-boundary consistency can veto an otherwise clean boundary, forcing compromises (merged services, replicated data, sagas).
- **Risk of over-decomposition** - too many fine-grained services multiply network calls and operational load (drives the granularity trade-off from The Hard Parts).

## Alternatives
- **Decompose by business capability vs by subdomain (DDD):** the two strategies in this lesson - capability analysis is quicker and org-driven; subdomains/bounded contexts are sharper for untangling shared concepts. Usually used together.
- **Keep it a modular monolith:** enforce module boundaries (and module-owned schemas) inside one deployable; get much of the cohesion benefit while you learn the domain, and extract services later (lesson 12).
- **Decompose by technical layer (anti-pattern):** presentation/logic/data tiers - explicitly avoid; it maximizes coupling.
- **Noun- or verb-driven ad hoc splitting:** carving services around random entities or actions without capability/subdomain analysis - tends toward the distributed monolith.

## When to use it
- You are defining service boundaries for a new microservice system or planning to extract services from a monolith and need a principled method rather than guesswork.
- The domain is understood well enough to identify capabilities/subdomains (or you can invest in DDD analysis to get there).
- You want boundaries that align with teams and the business so services can evolve independently.
- You are prepared to pressure-test candidate boundaries against latency, availability, and consistency.

## When NOT to use it
- The domain is still poorly understood or rapidly changing - premature boundaries will be wrong; stay monolithic/modular until the seams are clear.
- The system is small enough that a monolith suffices - you do not need to draw service boundaries at all yet.
- A candidate boundary would split data requiring strong single-transaction consistency with no acceptable saga - reconsider the boundary rather than force it.
- You are tempted to decompose by technical layer or arbitrary nouns - that is the path to a distributed monolith; do not.

## Key takeaways / mental model
Think of decomposition like dividing a company into departments. You organize by *what people do* (Sales, Support, Fulfillment) - cohesive teams that own an outcome end to end - not by *skill layer* (a "typing department," a "phone department") that would make every task cross three departments. And you accept that "a customer" means something different to Sales, Support, and Fulfillment - each keeps the view it needs. Two rules of thumb:

1. **Cut by business capability / subdomain, vertically, never by technical layer.** The target is high cohesion + low coupling so a feature change stays in one service; capability and subdomain analysis are the two disciplined ways to find those seams, and bounded contexts kill the shared-god-class coupling.
2. **Boundaries are the expensive decision - pressure-test them.** After a capability/subdomain first cut, check latency, availability (synchronous chains erode it), and consistency (splitting transactional data forces sagas). Wrong boundaries yield a distributed monolith - all the cost of microservices, none of the independence.

## Self-check questions
1. What is a "distributed monolith," how do bad boundaries create it, and why is it worse than the monolith you started with?
2. Why is decomposing by technical layer (presentation/logic/data) an anti-pattern? Contrast it with vertical capability slices using a concrete feature change.
3. Compare decomposition by business capability with decomposition by subdomain. What does each analyze, and why are they usually used together?
4. Explain how a bounded context handles the fact that "Order" means different things in the Order-taking, Kitchen, and Delivery contexts. What coupling does this remove versus a shared `Order` class?
5. Name three guardrails (latency, availability, consistency) that can veto an otherwise clean boundary, and give an example of each forcing a change to the decomposition.
6. You are handed a proposed decomposition with `Validation Service`, `Pricing Service`, and `Persistence Service` for orders. Diagnose the problem and propose a better decomposition, justifying it in terms of coupling, cohesion, and availability.

## References
- Microservices Patterns (Chris Richardson), Chapter 2: "Decomposition strategies"
- [hard-parts/07 - Service granularity](../../hard-parts/lessons/07-service-granularity.md)
- [fundamentals/06 - Modularity fundamentals](../../fundamentals/lessons/06-modularity-fundamentals.md)
