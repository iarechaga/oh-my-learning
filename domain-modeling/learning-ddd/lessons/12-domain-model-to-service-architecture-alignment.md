---
id: learning-ddd/12
subject: learning-ddd
title: Domain model to service architecture alignment
slug: domain-model-to-service-architecture-alignment
status: drafted
mastery:
seniority: staff
source: Learning Domain-Driven Design (Vlad Khononov), Part III, Chapter 8 - "Architectural Patterns"
prerequisites: [learning-ddd/07, learning-ddd/08, learning-ddd/11]
created: 2026-08-10
updated: 2026-08-10
---

# Domain model to service architecture alignment

## TL;DR
The architecture surrounding a domain model - Layered Architecture, Ports & Adapters (Hexagonal), CQRS, Event-Driven Architecture - should be chosen per bounded context based on that context's business-logic pattern (`learning-ddd/07`) and integration needs (`learning-ddd/11`), not adopted uniformly across an entire system. A core subdomain's rich Domain Model typically needs an architecture that actively protects it from infrastructure concerns (Ports & Adapters); a simple supporting subdomain's Transaction Script needs none of that ceremony.

## The idea
Architectural style answers a narrower question than "how do we structure the whole system": specifically, "how does the domain model relate to infrastructure - the database, the web framework, external APIs - and how much is the domain logic protected from changes in those infrastructure choices?" Khononov's throughline is the same one that has run through this whole subject: the answer should track the business-logic pattern already chosen (`learning-ddd/07`) for that specific subdomain, because a rich Domain Model has fundamentally different protection needs than a Transaction Script does, and applying the same architectural ceremony to both wastes effort on the simple side and under-protects the complex side if the mapping is inverted.

## How it works

### Layered Architecture
Code is organized into layers (presentation, application, domain, infrastructure), with dependencies flowing one direction, typically top to bottom - the domain layer sits in the middle, called by the application layer, and (in the traditional, unstrict form) can itself depend on infrastructure abstractions.

**Worked example - a supporting subdomain: order-history reporting.** A straightforward layered structure (a `ReportingController` in the presentation layer calling a `ReportingService` in the application layer, which queries a `ReportRepository` in the infrastructure layer) is entirely sufficient - this subdomain has no complex invariants to protect (`learning-ddd/07`'s Transaction Script fits fine), so there's no need for the stricter isolation Ports & Adapters would add.

### Ports & Adapters (Hexagonal Architecture)
A stricter discipline: the domain model defines **ports** (interfaces) for everything it needs from the outside world (persistence, external services), and infrastructure code provides **adapters** implementing those ports. Critically, dependencies point *inward* - the domain model has zero knowledge of which database, framework, or external API is actually plugged in, and can be tested completely in isolation with fake adapters standing in for real infrastructure.

**Worked example - a core subdomain: SaaS billing's Subscription domain model.**
```
// Port - defined by the domain, no infrastructure knowledge
interface SubscriptionRepository {
  findById(id: SubscriptionId): Subscription;
  save(subscription: Subscription): void;
}

// Domain logic depends only on the port, never on a concrete database
class UpgradeSubscriptionUseCase {
  constructor(private repo: SubscriptionRepository) {}
  execute(id: SubscriptionId, newPlan: Plan) {
    const sub = this.repo.findById(id);
    const charge = sub.upgradeTo(newPlan, now());   // rich Domain Model, per learning-ddd/07
    this.repo.save(sub);
    return charge;
  }
}

// Adapter - infrastructure implements the port, lives outside the domain
class PostgresSubscriptionRepository implements SubscriptionRepository {
  findById(id) { /* SQL query, ORM mapping */ }
  save(sub) { /* SQL upsert */ }
}
```
This isolation is exactly what a rich Domain Model with real invariants (`learning-ddd/08`'s `Subscription.upgradeTo()`) needs: the invariant logic can be unit-tested with an in-memory fake `SubscriptionRepository`, with zero database involved, and the team can swap Postgres for another store later by writing a new adapter, without touching a single line of domain logic. Applying this same rigor to the simple order-history reporting example above would be pure ceremony - there's no invariant-rich domain logic there worth protecting this way.

### CQRS (Command Query Responsibility Segregation)
Separates the model used to *write* (protect invariants, execute business logic - the "command" side) from the model used to *read* (denormalized, shaped for a specific query need, no invariant-protection - the "query" side). The two can even use entirely different storage technologies and be updated asynchronously relative to each other (typically via the domain events from `learning-ddd/09`, connecting directly to `learning-ddd/10`'s data-replication pattern).

**Worked example - e-commerce order management.** The write side is a rich `Order` aggregate (`learning-ddd/08`) enforcing invariants like "total must equal sum of line items," accessed only through commands (`PlaceOrder`, `CancelOrder`). The read side is a completely separate, denormalized `OrderSummaryView` table - flat, pre-joined with customer name and product titles, optimized purely for the "show a customer their order history" query - populated asynchronously by a listener reacting to `OrderPlaced` and `OrderCancelled` events. The read model doesn't enforce any invariants at all (it doesn't need to; it's derived, not authoritative) and can be denormalized as aggressively as the read pattern demands, entirely decoupled from the write side's aggregate shape.

### Event-Driven Architecture
The system's overall structure is organized around domain events (`learning-ddd/09`) flowing between components, rather than direct method or API calls - components react to events rather than being explicitly invoked. This is less a per-context internal-code-structure choice (like Layered or Ports & Adapters) and more a system-wide integration style, closely tied to `learning-ddd/11`'s event-streaming integration pattern; it shows up both *between* bounded contexts and, in an event-sourced context (`learning-ddd/09`), *within* one.

## Pros
- Ports & Adapters gives a genuinely rich Domain Model real, testable isolation from infrastructure churn - a database migration, a framework upgrade, or an external API change touches only an adapter, never the protected domain logic.
- CQRS lets read performance and write correctness be optimized completely independently, which matters enormously once a system's read and write patterns genuinely diverge (very common: reads vastly outnumber writes, and reads want denormalized, cross-aggregate views that a normalized write-side aggregate structure is deliberately not shaped to serve).
- Matching architecture to business-logic pattern (`learning-ddd/07`) avoids the two failure modes at once: heavyweight Ports & Adapters ceremony wasted on simple Transaction Scripts, and simple layered code failing to protect a genuinely complex Domain Model's invariants from infrastructure leakage.
- Event-Driven Architecture, used where the integration analysis (`learning-ddd/11`) actually calls for it, delivers real component decoupling at a system level.

## Cons
- Ports & Adapters and CQRS both add real structural overhead (more interfaces, more classes, an eventually-consistent read model to keep in sync) that is wasted effort for a subdomain whose logic is genuinely simple.
- CQRS introduces the same eventual-consistency reasoning burden as `learning-ddd/10` - the read model can be briefly stale relative to the write model, which must be an acceptable, deliberately-chosen trade-off, not an accidental surprise for users.
- Event-Driven Architecture makes end-to-end tracing and debugging harder (a request's effects are spread across multiple asynchronously-triggered reactions rather than one traceable call stack), a real operational cost that must be paid for with good observability tooling.
- Mixing architectural styles across different bounded contexts in the same system (the correct approach, per this lesson) requires engineers to understand and navigate more than one structural convention, which raises onboarding cost compared to a single uniform style - a cost worth paying deliberately, not by accident.

## Alternatives
- **One uniform architecture for the whole system** - lower onboarding and governance cost, but reproduces this subject's recurring anti-pattern (from `learning-ddd/01` onward): mismatched investment relative to actual subdomain complexity, either over-engineering the simple parts or under-protecting the complex ones.
- **Big Ball of Mud / no deliberate architecture** - the default when no explicit choice is made; works until a core subdomain's invariants start silently leaking into and being violated by infrastructure code with no protective boundary at all.
- **Clean Architecture / Onion Architecture** (Robert C. Martin and others) - closely related dependency-inversion styles to Ports & Adapters, often used interchangeably in practice; the core idea (dependencies point inward toward the domain) is the same one this lesson applies to core subdomains.

## When to use it
Choose Layered Architecture (or even simpler structures) for supporting and generic subdomains using Transaction Script or Active Record (`learning-ddd/07`). Choose Ports & Adapters for core subdomains with a rich Domain Model whose invariants genuinely need protection from infrastructure churn. Layer CQRS on top wherever a bounded context's read and write access patterns have genuinely diverged enough that one shared model no longer serves both well. Reach for Event-Driven Architecture at the integration level per `learning-ddd/11`'s relationship-driven analysis.

## When NOT to use it
Don't apply Ports & Adapters or CQRS to a subdomain whose logic is simple and stable - the added indirection has a real, ongoing cost (more files to navigate, more concepts for new engineers to learn) with no corresponding protection benefit, since there's no complex invariant or divergent read/write pattern to protect in the first place.

## Key takeaways / mental model
Architecture is a protection mechanism, sized to what needs protecting. Ask: "how much does this subdomain's domain logic (per `learning-ddd/07`) need to be isolated from infrastructure change, and how much have its read and write access patterns actually diverged?" Low on both -> simple Layered Architecture. High on either -> Ports & Adapters and/or CQRS, applied to that specific bounded context, not the whole system uniformly.

## Self-check questions
1. Take a bounded context you know. Which architectural style does it actually use, and does that match the business-logic pattern (`learning-ddd/07`) its domain logic follows? Is there a mismatch in either direction?
2. Explain concretely what "dependencies point inward" means in Ports & Adapters, and why that property is what makes a domain model unit-testable without a real database.
3. Describe a situation where a bounded context's read and write patterns have diverged enough to justify CQRS. What would the read model look like compared to the write model's aggregate shape?
4. Why does this lesson argue against picking one architectural style for an entire system, even though that would be simpler to document and onboard new engineers into?

## References
- Learning Domain-Driven Design (Vlad Khononov), Part III, Chapter 8: "Architectural Patterns".
- Clean Architecture (Robert C. Martin) - dependency-inversion and layering principles related to Ports & Adapters.
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 4, "Architecture" - see `domain-modeling/implementing-ddd`.
