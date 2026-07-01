---
id: microservices-patterns/12
subject: microservices-patterns
title: "Refactoring to Microservices"
slug: refactoring-to-microservices
status: drafted
mastery:
seniority: staff
source: "Microservices Patterns (Chris Richardson), Chapter 13"
prerequisites: [microservices-patterns/01, microservices-patterns/02, microservices-patterns/04]
created: 2026-07-01
updated: 2026-07-01
---

# Refactoring to Microservices

## TL;DR
Almost no team gets to build microservices from scratch; the real, high-stakes job is migrating an existing monolith *while it keeps running and shipping features*. The governing strategy is the **Strangler Fig application**: incrementally build new services *around* the monolith and route more traffic to them over time, so the monolith shrinks gradually instead of being replaced in one catastrophic "big bang" rewrite. You migrate one capability at a time (highest value / lowest risk first), glue old and new together with an **anti-corruption layer** and events, and accept that for a long period you run a **hybrid** system whose data must stay consistent across the seam. This is a staff-level concern: the hardest parts are sequencing, data synchronization, and organizational change - not the code.

## The idea
The starting truth of this lesson is the one every experienced engineer already suspects: **do not do a big-bang rewrite.** Stopping feature work to reimplement a large monolith as microservices over many months, then cutting over all at once, is enormously risky - it delivers no value until the very end, it's almost always late, requirements drift underneath it, and the cutover is a single terrifying event. History is littered with failed rewrites.

The alternative is **incremental migration**: evolve the monolith into microservices in small, safe steps, delivering value continuously and de-risking as you go. The organizing metaphor (from Martin Fowler) is the **Strangler Fig** - a vine that grows around a tree, gradually enveloping it until the original tree is gone but the shape remains. You build new microservices around the monolith and progressively route functionality to them; the monolith is "strangled" over time until little or nothing is left, and you can stop at any point with a working system.

Why even migrate? Only to escape real pain from **monolithic hell** (lesson 01): slow builds/deploys, scaling limits, difficulty adopting new tech, tangled change. Migration is justified by relieving that pain - not by fashion. And because you migrate incrementally, **each step must pay off on its own**: you pick what to extract by value and risk, not alphabetically.

The three practical pillars of a strangler migration are: (1) **stop digging** - implement *new* features as services, not more monolith; (2) **split frontend from backend** where it helps; and (3) **extract capabilities** from the monolith into services one at a time, starting where the payoff is highest. Throughout, old and new must interoperate and their data must stay consistent - which is where sagas (lesson 04), events (lesson 05), and anti-corruption layers earn their keep.

## How it works

### Strangler Fig: grow new services around the monolith
```text
   time --->
   [ MONOLITH ]      [ MONOLITH ]      [ MONO ]        [  gone  ]
                        \ svc A          \ svc A \ svc B   svc A,B,C...
   all traffic     some traffic       most traffic     all traffic
   to monolith     split via router    to services      to services
```
A routing layer (often the API Gateway, lesson 08) sits in front and directs each request either to the monolith or to the new service that now owns that capability. As you extract more, the router sends more to services and the monolith shrinks. Crucially, the system is fully working at *every* step - you're never in a non-shippable state, unlike a big-bang rewrite.

### Pillar 1: stop making the monolith bigger ("stop digging")
The first rule of holes: when in one, stop digging. Implement **new** functionality as a **new service**, not as more code in the monolith. The new service integrates with the monolith through an **anti-corruption layer** (ACL - a translation layer that maps between the monolith's often-messy legacy model and the new service's clean domain model, so the new service isn't "corrupted" by legacy concepts). This immediately slows the monolith's growth and gives the team practice standing up and operating services before tackling risky extractions.

### Pillar 2: split frontend from backend
Many monoliths bundle a presentation layer (web UI/API) and a backend (business logic + data). Splitting these into a separate frontend and backend gives two smaller components you can develop and deploy independently, and it exposes a clean API boundary in the backend that later extractions can hook into. It's often an early, relatively low-risk step that creates seams.

### Pillar 3: extract capabilities into services (one at a time)
The heart of migration: carve a **vertical slice** - a business capability with its logic *and its data* - out of the monolith into a service (a mini version of the decomposition work in lesson 02: identify a subdomain, define its API, split its data). Two hard sub-problems dominate:

- **Splitting the data, not just the code.** The capability's tables must move to the new service's database. But existing monolith code (and other not-yet-extracted capabilities) may still read/write that data. So during the transition you often must **keep two copies in sync** across the seam.
- **Choosing what to extract first.** Prioritize by **value vs. effort/risk**: extract capabilities that (a) relieve the most pain (e.g. the module that needs to scale independently or changes most often) and (b) are reasonably decoupled (lower risk). Avoid extracting the most tangled core last-minute; sometimes you extract an easier neighbor first to create room.

### Keeping data consistent across the seam (the real difficulty)
While a capability is half-migrated, the monolith's data and the new service's data must agree. Techniques:

- **Anti-corruption layer + API calls:** the service calls the monolith (or vice versa) through an ACL for data it doesn't own yet, translating models at the boundary.
- **Replicate via domain events / CDC:** the owner publishes events (or you tail its transaction log with change data capture) so the other side maintains a synchronized copy. This may mean **temporarily maintaining data in both places** and syncing bidirectionally until the monolith no longer needs it.
- **Sagas across the seam:** an operation that spans the monolith and a new service can no longer be one ACID transaction - it becomes a **saga** (lesson 04) with compensations, exactly as between two services. The monolith becomes "just another saga participant."

This synchronization - not the coding - is what makes migration genuinely hard and why it's a staff-level topic.

### It's an organizational change, not just technical
Microservices go hand in hand with **team structure and process** (Conway's Law: systems mirror the org that builds them). A successful migration reorganizes into small, autonomous, cross-functional teams that own services end to end, and adopts the delivery practices (CI/CD, automated testing, observability - lessons 09-11) that make many independently deployable services survivable. Migrating the architecture without migrating the organization and its practices usually fails. Leadership buy-in, incremental value delivery, and cultural change (DevOps) are first-class parts of the plan.

### Worked example 1: strangling FTGO's delivery management
FTGO wants to scale and iterate on delivery independently; it's a good first extraction (high value, fairly decoupled).

1. **Define the boundary:** identify "Delivery Management" as a subdomain - assign couriers, track deliveries - with its own data (couriers, delivery status).
2. **Stand up `Delivery Service`** with a clean API and its own database.
3. **Route via the gateway:** front FTGO with an API Gateway; send delivery-related requests to `Delivery Service`, everything else still to the monolith (Strangler routing).
4. **Sync the data:** the monolith still references orders/deliveries, so publish `DeliveryStatusChanged` events (or use CDC) so the monolith's view stays current; where the service needs order data it doesn't own yet, it calls the monolith through an **anti-corruption layer**.
5. **Shrink over time:** as delivery logic fully moves out, the monolith stops owning that capability. The system shipped features the whole time and was working at every step.

The example shows all three pillars and the data-sync reality in one slice.

### Worked example 2: a cross-seam operation becomes a saga
After extracting `Delivery Service`, "cancel an order" must cancel the order (still in the monolith) *and* cancel its delivery (new service).

1. In the old monolith this was one ACID transaction. Now it spans two databases - impossible as a single transaction.
2. It becomes a **saga** (lesson 04): monolith transitions the order to `CANCELLED` and emits `OrderCancelled`; `Delivery Service` consumes it and cancels the delivery; if delivery cancellation fails in a non-retriable way, a compensation reopens/flags the order.
3. The monolith is now **a saga participant** - to make this work you often add an outbox/events to the monolith so it can publish reliably (lesson 05).
4. Lesson: extraction doesn't just move code; it converts former local transactions across the seam into sagas with all their consistency/compensation concerns.

### Worked example 3: sequencing and "stop digging" on a new feature
FTGO plans a new "loyalty points" feature mid-migration. Where should it live?

1. **Don't add it to the monolith** ("stop digging") - that would deepen monolithic hell.
2. Implement **`Loyalty Service`** as a brand-new service from day one. It integrates with the monolith via an ACL and by subscribing to events like `OrderApproved` to award points.
3. This both delivers the new feature cleanly *and* advances the migration (one more capability outside the monolith) without a risky extraction.
4. Sequencing principle: new capabilities are free wins for the migration; extractions of existing capabilities are ordered by value and risk. Combine "stop digging" with prioritized extraction to shrink the monolith on two fronts.

## Pros
- **Low risk, continuous value** - incremental steps keep a working, shippable system throughout and deliver benefits early, unlike a big-bang rewrite that pays off (if ever) only at the end.
- **Learn and course-correct as you go** - the team builds services and operational muscle gradually and can adjust the plan with real feedback.
- **Stop anytime with a working system** - a hybrid monolith-plus-services is a valid stopping point; you migrate only as far as the value justifies.
- **Targets real pain first** - prioritizing by value/risk means the most painful constraints (scaling, change-frequency) get relieved earliest.

## Cons
- **Long-lived hybrid complexity** - for an extended period you operate both a monolith and services, with the seam's data-synchronization burden (dual writes, events/CDC, ACLs).
- **Cross-seam consistency is hard** - former local transactions become sagas with compensations and eventual consistency; the monolith must often be retrofitted to publish events reliably.
- **Anti-corruption layers add work** - translating between legacy and clean models is necessary but is extra code to build and maintain during the transition.
- **Organizational change is required and difficult** - without team restructuring (Conway's Law) and CI/CD/observability practices, the migration tends to fail regardless of technical quality.

## Alternatives
- **Big-bang rewrite (anti-pattern):** replace the monolith wholesale, then cut over once - high risk, delayed value, frequent failure; the book explicitly advises against it.
- **Keep and improve the monolith (modular monolith):** if monolithic hell isn't actually biting, invest in modularity/build speed instead of migrating - microservices aren't free (relates to fundamentals/18).
- **Extract only the painful parts, stop there:** deliberately migrate a few high-value capabilities out (e.g. the one that must scale) and keep the rest as a monolith indefinitely - a legitimate, common end state.
- **Lift-and-shift then decompose:** move the monolith to containers/cloud first for operational wins, then strangle - sequencing the operational and architectural migrations separately.

## When to use it
- An existing monolith is causing genuine **monolithic hell** (lesson 01) - slow delivery, scaling walls, tech lock-in, tangled change - and the pain justifies the cost.
- You must keep shipping features and cannot afford a feature freeze or a risky big-bang cutover.
- The organization is willing to also change team structure and adopt CI/CD, testing, and observability (lessons 09-11).
- You can identify decoupled, high-value capabilities to extract first and can build the seam (events/CDC/ACL, sagas) to keep data consistent.

## When NOT to use it
- The monolith is working fine for the team's scale and pace - migrating adds distributed-systems complexity with no payoff (premature microservices).
- The organization won't restructure teams or invest in the required delivery/operational practices - the migration will likely fail (Conway's Law working against you).
- The system is small or short-lived, where a modular monolith is simpler and sufficient.
- You're tempted by a big-bang rewrite - that's a reason to *not* proceed that way, not a use case; re-plan as incremental.

## Key takeaways / mental model
Picture renovating a house you still have to live in. You don't demolish it and camp in the yard for a year (big-bang rewrite); you renovate **room by room**, keeping the house habitable throughout, doing the highest-value rooms first, and running temporary utilities across the half-finished seam until each room is done. The strangler fig is that renovation: new structure grows around the old until the old is gone, but you never lose your home. Two rules of thumb:

1. **Migrate incrementally, never big-bang.** Grow services around the monolith (Strangler Fig): stop digging (build new features as services), split frontend from backend, and extract capabilities one at a time, ordered by value and risk - keeping a working, shippable system at every step and stopping whenever the remaining pain no longer justifies more.
2. **The hard part is the seam, not the code.** While capabilities are half-migrated, keep data consistent with anti-corruption layers, events/CDC, and sagas (the monolith becomes just another saga participant), and change the organization - small autonomous teams plus CI/CD, testing, and observability - because architecture migration without organizational migration fails.

## Self-check questions
1. Why does the book strongly advise against a big-bang rewrite, and what does the Strangler Fig strategy do instead? What property holds at every step of a strangler migration?
2. Explain the three pillars of migration ("stop digging," split frontend/backend, extract capabilities). For a brand-new feature during migration, which pillar applies and where should the feature live?
3. What is an anti-corruption layer, and why is it needed when integrating a new service with a legacy monolith?
4. When you extract a capability, why is splitting the *data* harder than splitting the *code*? Describe two techniques for keeping data consistent across the seam during the transition.
5. After extracting a service, an operation that used to be a single ACID transaction in the monolith now spans the monolith and the new service. What must it become, and what does the monolith need to be retrofitted with to participate?
6. FTGO's monolith must be decomposed but the team can't stop shipping. Propose a first capability to extract (justify by value and risk), outline the strangler steps, describe how you'd keep its data consistent with the monolith, and name the organizational changes required for success.

## References
- Microservices Patterns (Chris Richardson), Chapter 13: "Refactoring to microservices"
- [microservices-patterns/01 - Monolithic hell and the microservice architecture](01-monolithic-hell.md)
- [microservices-patterns/02 - Decomposition strategies](02-decomposition-strategies.md)
- [hard-parts/07 - Service granularity](../../hard-parts/lessons/07-service-granularity.md)
- [fundamentals/18 - SOA and microservices](../../fundamentals/lessons/18-soa-and-microservices.md)
