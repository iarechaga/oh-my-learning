---
id: learning-ddd/07
subject: learning-ddd
title: "Business logic patterns: transaction script, active record, domain model"
slug: business-logic-patterns-transaction-script-active-record-domain-model
status: drafted
mastery:
seniority: mid
source: Learning Domain-Driven Design (Vlad Khononov), Part II, Chapter 5 - "Implementing Simple Business Logic" and Chapter 6 - "Tackling Complex Business Logic"
prerequisites: [learning-ddd/02, learning-ddd/06]
created: 2026-08-10
updated: 2026-08-10
---

# Business logic patterns: transaction script, active record, domain model

## TL;DR
There is no single "correct" way to structure business logic - **Transaction Script** (a simple procedural function per use case), **Active Record** (objects that bundle a bit of behavior with their own persistence), and **Domain Model** (rich objects encapsulating invariants and behavior, persistence-ignorant) sit on a rising scale of modeling investment and payoff. Picking the pattern should follow directly from a subdomain's classification (`learning-ddd/02`): simple/generic logic deserves the cheapest pattern that works; genuinely complex, core logic deserves - and needs - the Domain Model pattern.

## The idea
Business logic patterns are not a matter of taste or "best practice" applied uniformly. Each pattern trades implementation simplicity against the ability to safely express and enforce complex rules. Applying Domain Model everywhere, including trivial CRUD-shaped supporting or generic subdomains, produces unnecessary abstraction, more files, more indirection, and slower onboarding for zero benefit - the exact anti-pattern named in `learning-ddd/01`. Applying Transaction Script or Active Record to a genuinely complex core subdomain produces the opposite failure: business rules get scattered across procedural functions or leak into database-adjacent objects, invariants go unenforced because there is no single place responsible for guarding them, and the codebase accretes special-case conditionals nobody can safely change without fear of breaking an invariant they don't even know exists.

## How it works

### Transaction Script
One procedure per use case (or transaction), operating fairly directly on the underlying data. Straightforward to write and read top-to-bottom; little to no separate "domain layer."

**Worked example - SaaS: applying a discount code.**
```
function applyDiscountCode(orderId, code) {
  const order = db.orders.findById(orderId);
  const discount = db.discountCodes.findByCode(code);
  if (!discount || discount.expiresAt < now()) {
    throw new Error("Invalid or expired code");
  }
  order.total = order.total * (1 - discount.percentOff);
  db.orders.save(order);
}
```
This is entirely adequate for a supporting subdomain with one or two straightforward rules and no risk of the logic growing much more complex. It becomes a liability the moment a second use case (say, "recalculate order total when an item is removed") needs to apply the *same* discount rule and either duplicates the logic or calls back into this procedure in an awkward way - a sign the logic is outgrowing the pattern.

### Active Record
Objects mirror database rows/tables and carry a modest amount of behavior alongside their own persistence responsibility (a `save()`/`find()` method living directly on the object). A step up from Transaction Script in that related data and a bit of behavior are co-located, but the object's shape is still driven by the database schema, not by the domain's actual concepts and invariants - and the object typically knows how to persist itself, coupling domain logic to storage mechanics.

**Worked example - logistics: a Shipment Active Record.**
```
class Shipment extends ActiveRecordBase {
  static tableName = "shipments";
  markDispatched() {
    this.status = "dispatched";
    this.dispatchedAt = now();
    this.save();   // persistence is a method on the domain object itself
  }
}
```
This works well for supporting subdomains with modest behavior needs and a data shape that genuinely does mirror the database well. It starts to strain once invariants span multiple tables/records (e.g., "a shipment can only be marked dispatched if all its line items have been picked" - now `markDispatched()` needs to reach across records it doesn't naturally own, and the persistence coupling makes it awkward to test the rule without a real database).

### Domain Model
Objects are shaped entirely around business concepts and invariants, are ignorant of how they're persisted (persistence is handled separately, often via a Repository pattern), and actively enforce their own consistency rules - an object should be impossible to put into an invalid state through its public API. This is the pattern that pairs with `learning-ddd/08`'s aggregates.

**Worked example - SaaS billing: a Subscription domain model enforcing proration invariants.**
```
class Subscription {
  private status: SubscriptionStatus;
  private plan: Plan;
  private currentPeriod: BillingPeriod;

  upgradeTo(newPlan: Plan, effectiveDate: Date): ProratedCharge {
    if (this.status !== SubscriptionStatus.Active) {
      throw new CannotUpgradeInactiveSubscriptionError();
    }
    if (!this.currentPeriod.contains(effectiveDate)) {
      throw new UpgradeDateOutsideBillingPeriodError();
    }
    const charge = ProrationCalculator.calculate(
      this.plan, newPlan, effectiveDate, this.currentPeriod
    );
    this.plan = newPlan;
    return charge;   // the object never touches a database; a repository persists it separately
  }
}
```
The invariant ("can only upgrade an active subscription, only within the current billing period") lives in exactly one place, is enforced on every call path (there is no way to change `plan` except through `upgradeTo`, which always checks the invariant), and the object can be fully unit-tested with no database at all. This is the payoff that justifies Domain Model's extra structure: for a core subdomain like usage-based billing (`learning-ddd/01`'s running example), the cost of a bug in proration math is high, and the number of code paths that need to respect the invariant grows over time - exactly the conditions under which Transaction Script's scattered-procedure approach or Active Record's persistence-coupled approach would eventually let an invalid state slip through.

### Worked example - healthcare: choosing per subdomain, not uniformly
A hospital scheduling system has both a simple "provider marks themselves unavailable for a day" feature (Transaction Script is entirely adequate - it's a single, low-risk update with essentially no invariants to protect) and a complex "resolve conflicting resource bookings across rooms, equipment, and specialists" feature (Domain Model is warranted - the invariants are numerous, cross-cutting, and a violated invariant here means a double-booked operating room, a genuinely costly failure). A well-run system uses different patterns for different subdomains within the same codebase, deliberately, rather than picking one pattern and applying it everywhere.

## Pros
- **Transaction Script**: fastest to write, easiest for a new engineer to read top-to-bottom with no indirection to trace through; ideal for genuinely simple, low-risk logic.
- **Active Record**: co-locates data and a modest amount of behavior, reducing the "anemic object, logic scattered in services" problem for moderately complex supporting subdomains, with less ceremony than a full Domain Model plus Repository setup.
- **Domain Model**: the only pattern of the three that reliably protects invariants that span multiple fields or multiple related objects; makes illegal states genuinely unrepresentable through the object's own API; testable in complete isolation from infrastructure.

## Cons
- **Transaction Script**: duplicates logic across procedures as rules multiply or need reuse; no natural home for cross-cutting invariants, so they get re-checked (or forgotten) inconsistently across every procedure that touches the same data.
- **Active Record**: couples domain logic to persistence mechanics, making unit testing without a database awkward; struggles once an invariant spans more than the one record/table the object mirrors; the object's shape is dictated by storage convenience rather than by the domain's actual concepts, which can produce a class that's neither a clean domain model nor a simple data holder.
- **Domain Model**: the most expensive to build (more classes, an explicit repository layer, more upfront design conversation with domain experts); overkill - genuinely wasted effort per `learning-ddd/01` - for a subdomain whose logic will never grow complex enough to need it.

## Alternatives
- **Event-Sourced Domain Model** - a variant of Domain Model where state is derived from a persisted sequence of domain events (`learning-ddd/09`) rather than stored as current-state snapshots; adds full historical auditability and temporal query power at the cost of materially higher implementation and operational complexity - reach for it when the business genuinely needs to answer "what was the state at any point in time" or "why did this change," not by default.
- **Table Module** (from Martin Fowler's *Patterns of Enterprise Application Architecture*) - one class per database table (rather than per row, as in Active Record) handling all rows' logic together; a middle-ground pattern less commonly needed once Transaction Script, Active Record, and Domain Model are well understood, but worth knowing as a fourth point on the same spectrum.
- **CQRS-driven logic separation** (`learning-ddd/12`) - rather than one pattern per subdomain, separate the write-side model (which might be a rich Domain Model protecting invariants) from the read-side model (which is typically simple, denormalized, and closer to Transaction Script in spirit) - a complementary axis to this lesson's choice, not a replacement for it.

## When to use it
Match the pattern to the subdomain classification from `learning-ddd/02`: Transaction Script for generic subdomains and the simplest supporting subdomains; Active Record for supporting subdomains with moderate, mostly-local behavior; Domain Model for core subdomains and any supporting subdomain whose invariants are genuinely complex or cross-cutting enough that scattered enforcement would be dangerous.

## When NOT to use it
Don't reach for Domain Model as a default "best practice" for a subdomain that is simple and stays simple - the extra abstraction (repositories, rich objects, explicit invariant methods) adds real cognitive and maintenance overhead with no corresponding payoff there, and it will make the codebase harder, not easier, for new engineers to navigate. Equally, don't force-fit Transaction Script onto logic that has already grown several interacting rules and duplicated checks across procedures - that's the signal it's time to graduate to Domain Model, ideally *before* an invariant violation reaches production, not after.

## Key takeaways / mental model
Ask two questions before picking a pattern for a piece of logic: **(1)** How many invariants does this need to protect, and do they span more than one field or one record? **(2)** How much does an invariant violation here actually cost the business (per `learning-ddd/01`'s core/supporting/generic lens)? Low answers to both -> Transaction Script. Moderate, mostly-local behavior -> Active Record. High stakes and/or cross-cutting invariants -> Domain Model, which then sets up the aggregate design work in `learning-ddd/08`.

## Self-check questions
1. Take a piece of business logic you've implemented recently. Which of the three patterns did it actually use? Was that the right choice given the subdomain's complexity and stakes, or was it over- or under-built?
2. Explain concretely why Active Record's coupling of behavior to persistence makes cross-record invariants harder to enforce than in a Domain Model with a separate repository.
3. Describe a piece of logic that started as a reasonable Transaction Script and later needed to graduate to a Domain Model. What symptom in the code would signal that moment?
4. Why does this lesson insist the pattern choice should differ *within* a single codebase, subdomain by subdomain, rather than being picked once for the whole system?

## References
- Learning Domain-Driven Design (Vlad Khononov), Part II, Chapter 5: "Implementing Simple Business Logic" and Chapter 6: "Tackling Complex Business Logic".
- Patterns of Enterprise Application Architecture (Martin Fowler) - original Transaction Script, Active Record, and Domain Model pattern definitions.
