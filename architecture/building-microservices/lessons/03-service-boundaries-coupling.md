---
id: building-microservices/03
subject: building-microservices
title: "Defining Service Boundaries and Coupling/Cohesion"
slug: service-boundaries-coupling
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 3"
prerequisites: [building-microservices/01, building-microservices/02]
created: 2026-08-10
updated: 2026-08-10
---

# Defining Service Boundaries and Coupling/Cohesion

## TL;DR
Good service boundaries maximize **cohesion** (things that change together live together) and minimize **coupling** (a change in one service should rarely force a change in another). The specific coupling types to hunt down and eliminate across service boundaries are implementation coupling (usually via a shared database), temporal coupling (synchronous call chains), and deployment coupling (services that must be released together). Information hiding — exposing only what consumers need and hiding everything else — is the primary tool for achieving this.

## The idea
Lesson 02 covered *how* to find candidate boundaries (bounded contexts). This lesson covers the underlying quality criterion for judging whether a boundary is actually good: **high cohesion, low coupling** — a principle that predates microservices by decades (it comes from structured design in the 1970s, via Larry Constantine and Ed Yourdon) but becomes existentially important once your module boundaries are also network and deployment boundaries.

**Cohesion** is about what's *inside* a service: do the things grouped together belong together, in the sense that they tend to change for the same reasons at the same time? A service with high cohesion is one where a single business change usually requires editing code in one place.

**Coupling** is about the relationship *between* services: how much does a change in one service force a change in another? Low coupling means services can evolve independently.

Inside a monolith, poor cohesion and tight coupling are annoying — you get tangled code, ripple-effect refactors, hard-to-test modules. Across microservice boundaries, the same problems are much more expensive, because "ripple effect" now means "coordinated multi-service deployment," and "hard to test" now means "hard to test across a network with independent failure modes." Newman's core argument in this chapter: the whole *point* of splitting into services evaporates if the boundaries you drew have low cohesion and tight coupling, because you've paid the network/operational tax of Lesson 01 without getting independent deployability in return.

## How it works

### Cohesion: keep what changes together, together

A useful operational test for cohesion: "if I need to make this one business change, how many services do I need to touch?" If the answer is reliably "one," your boundaries have good cohesion. If a routine change ("add a new discount type") requires synchronized edits to `cart-service`, `order-service`, and `pricing-service`, that's a sign the discount concept is split across a seam that should not exist — the pieces that "discount logic" comprises are changing together, so DDD/bounded-context modeling (Lesson 02) would tell you they belong in the same service.

### The three coupling types to actively avoid

Newman calls out three specific, concrete forms of coupling that recur in microservice systems and quietly destroy independent deployability, even when the domain modeling looked fine on paper.

**1. Implementation coupling (usually via a shared database).** This is the most common and most damaging. If Service A and Service B both read or write the same underlying table, then:
- A schema change to that table (adding a NOT NULL column, renaming a field, changing a type) potentially breaks both services, requiring a coordinated release — the exact coupling microservices are meant to eliminate.
- Worse, one service can come to depend on an *implementation detail* of the other — e.g., Service B relies on the fact that Service A always writes `status = 'PENDING'` before `status = 'CONFIRMED'`, an internal invariant Service A never explicitly published as part of a contract and can silently break.

The fix is the data-ownership rule from Lesson 01 and detailed in Lesson 07: each service owns its data exclusively; everyone else accesses it only through the service's published API or event stream, never through direct database access. This is what Newman calls **information hiding** applied at the service level — a service publishes a stable external contract and is free to change everything behind it (its schema, its internal algorithms, its choice of datastore) without affecting anyone else, as long as the published contract holds.

**2. Temporal coupling (synchronous call chains).** If Service A must call Service B synchronously, and wait for B's response, to complete its own request, then A's availability is now bounded by B's availability, and A's latency is bounded by B's latency (this is expanded fully in Lesson 06 and Lesson 14). Chain that across several hops — A calls B calls C calls D, all synchronously — and the whole chain's uptime is roughly the *product* of each link's uptime: if each of four services is 99.9% available, the chain is only about 99.6% available, and a slow response from D at the bottom is felt all the way up at A. This is temporal coupling: the caller is coupled *in time* to the callee being up and responsive right now. It's not eliminated by microservices — if anything it's introduced by them, since the same call used to be an in-process function call with no network involved.

**3. Deployment coupling.** Two services are deployment-coupled if, in practice, you cannot release one without also releasing the other — even if nothing in the tooling formally requires it. This happens subtly: a shared client library that both services must upgrade in lockstep to avoid a serialization mismatch; an API change that isn't backward-compatible, forcing consumer and provider to deploy in the same maintenance window; a shared staging environment where testing one service's change requires the other to also be at a specific version. Deployment coupling is the symptom that tells you independent deployability (Lesson 01's core promise) has quietly failed, even though the services are technically two separate deployables.

### Information hiding as the unifying tool

Newman frames information hiding (a term from David Parnas's classic 1972 module-design work) as the single most important discipline for avoiding all three coupling types above. The rule: a service should expose the smallest possible interface needed by its consumers, and hide everything else — internal data structures, internal algorithms, internal database schema, internal sequencing of steps. Consumers depend only on the published contract, so the service is free to change anything hidden behind that contract without breaking anyone.

Concretely, this means:
- Publish an explicit API contract (REST resource, gRPC schema, event schema) — never let consumers infer behavior from internal implementation details.
- Never grant direct database access to another service.
- Treat every field and endpoint you expose as a promise you now have to keep (or version deliberately — Lesson 12 covers how consumer-driven contracts catch violations of this promise in CI).

### Worked example: a poorly-bounded "Order" split

Suppose a team splits Order into two services for reasons that seemed reasonable at the time: `order-write-service` (handles placing/modifying orders) and `order-read-service` (handles querying order history), each independently deployed. On the surface this looks like a legitimate CQRS-style split (see Lesson 07 for API composition/CQRS-lite as an answer to cross-service queries). But suppose the team implemented it by having both services read and write the *same* `orders` table directly, for speed of initial delivery.

Now: `order-write-service` decides it needs to rename the `total_cents` column to `total_amount_cents` for clarity. This silently breaks `order-read-service`, which has no idea the schema changed underneath it — implementation coupling via shared database. The two "independent" services must now release together whenever either team touches the schema — deployment coupling, in practice, despite being nominally two separate deployables. And if `order-read-service` calls `order-write-service` synchronously on every read to double-check the latest write landed (a mitigation someone bolts on after a consistency bug), that's temporal coupling layered on top.

The fix, following the principles above: `order-write-service` owns the `orders` table exclusively. It publishes an `OrderPlaced`/`OrderUpdated` event stream (Lesson 06) that `order-read-service` consumes to build its own read-optimized copy of the data, in its own schema, which it owns. Now `order-write-service` can rename any internal column freely — the event schema is the only published contract, and it's versioned deliberately. The two services are cohesive internally and loosely coupled to each other.

### Loose coupling doesn't mean zero coupling

A caution Newman makes explicit: some coupling between services is inevitable and even healthy — a service that calls nothing and is called by nothing is probably not doing anything useful. The goal isn't to eliminate coupling; it's to make the coupling that remains **explicit, minimal, and stable** — coupling through a well-defined, versioned contract, not through shared implementation details, synchronous chains you can avoid, or accidental release-train entanglement.

## Pros
- **Cohesive services minimize the blast radius of change** — most feature work stays inside one service.
- **Loose coupling preserves independent deployability** — the entire reason to take on microservices in the first place (Lesson 01).
- **Information hiding gives each team real autonomy** to change internals (schema, algorithms, even datastore) without cross-team negotiation.

## Cons
- **Requires ongoing discipline, not a one-time decision** — coupling creeps back in via shortcuts (shared DB "just for this one query," a synchronous call added "just for now") unless actively resisted.
- **Diagnosing coupling after the fact is hard** — deployment coupling especially is often invisible until a release actually fails or gets blocked, because nothing in the tooling flags it directly.
- **Fixing tight coupling after the fact usually requires real migration work** (moving off a shared database, replacing a sync call with an event) — see Lesson 04 for the incremental techniques.

## Alternatives
- **Accept tighter coupling deliberately, as a conscious trade-off** — e.g., two services that are always deployed together and always will be might genuinely be better modeled as one service (or one deployable with two processes); forcing an artificial split just to look more "microservice-y" adds cost for no benefit. Newman is explicit that a boundary should be drawn to serve independent deployability where it's actually needed, not everywhere by default.
- **Shared library for genuinely stable, rarely-changing logic** (e.g., a currency-formatting utility) — lower-risk than a shared database, but still creates a form of coupling (all consumers must eventually upgrade); keep such libraries small, stable, and free of business logic that changes often.

## When to use it
- Whenever you are evaluating whether an existing or proposed service boundary is healthy — use the cohesion test ("how many services does this one business change touch?") and check for the three coupling types.
- Before adding a "quick" cross-service database read or a "just this once" synchronous dependency — both are exactly the shortcuts that quietly reintroduce coupling.

## When NOT to use it
- Don't chase zero coupling as a goal in itself — some explicit, contract-based coupling is healthy and unavoidable; over-decomposing to avoid all coupling just multiplies network hops and operational overhead (Lesson 01's cons) without a corresponding benefit.
- Don't retrofit strict boundary discipline onto a prototype or throwaway system where the domain and boundaries are still being discovered — that's a case for staying in a modular monolith a while longer (Lesson 01, Lesson 04).

## Key takeaways / mental model
High cohesion, low coupling — the same principle from structured design, now applied at the service level where violations are far more expensive. Ask two questions of every boundary: "does one business change usually touch just this one service?" (cohesion) and "if I change this service's internals, does anything else break?" (coupling). Watch specifically for the shared database, the synchronous call chain, and the release-train entanglement — the three coupling types that quietly undo independent deployability. Information hiding — publish a narrow contract, hide everything else — is the main tool for keeping coupling low.

## Self-check questions
1. Two services share a Postgres database and one renames a column, breaking the other. Which of the three coupling types is this, and what is the standard fix?
2. A chain of four synchronously-called services is each individually 99.9% available. Roughly what is the chain's overall availability, and what coupling type is responsible for that multiplication effect?
3. What does "deployment coupling" mean, and why can two services be deployment-coupled in practice even if their pipelines are technically independent?
4. Give an example of coupling between two services that is healthy and should not be eliminated. What makes it different from the coupling types this lesson says to avoid?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 3: "How to Model Microservices"
- David Parnas, "On the Criteria to Be Used in Decomposing Systems into Modules" (1972) — origin of information hiding, cited by Newman as the foundation for service-level boundary design.
