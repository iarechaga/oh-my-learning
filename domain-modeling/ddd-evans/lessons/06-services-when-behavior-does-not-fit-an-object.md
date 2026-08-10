---
id: ddd-evans/06
subject: ddd-evans
title: Services when behavior does not fit an object
slug: services-when-behavior-does-not-fit-an-object
status: drafted
mastery:
seniority: senior
source: Domain-Driven Design (Eric Evans), Part II, Chapter 5
prerequisites: [ddd-evans/04, ddd-evans/05]
created: 2026-08-10
updated: 2026-08-10
---

# Services when behavior does not fit an object

## TL;DR
A domain service holds a piece of significant business behavior that doesn't naturally belong as a method on any single entity or value object — typically because it operates across multiple objects, represents a domain-level process rather than a thing, or would force an awkward, unnatural dependency onto an object that shouldn't have it.

## The idea
The instinct after learning about entities and value objects is to force *every* piece of behavior onto some object — but some operations genuinely don't belong to any single thing in the domain. Consider "transfer funds from account A to account B." Is that `AccountA.transferTo(AccountB, amount)`? That's awkward: why should one account object have privileged, asymmetric authority to reach into and modify another account? The operation is really about the *relationship* and process between two accounts, not a property of either one individually.

A domain service names that behavior explicitly as a first-class domain concept, callable with the objects it needs as arguments, without pretending it's secretly a method of one particular entity. Critically, a domain service is not just "a class where you dump leftover logic" — it must still be stateless, still be named with real domain vocabulary (`FundsTransferService`, not `AccountHelper` or `AccountUtils`), and still operate purely in terms of domain concepts (entities, value objects) with no infrastructure concerns leaking in.

## How it works

### Recognizing when behavior needs a service, not an entity method
Three signals from the book suggest an operation is a service rather than an entity/value-object method:
1. **The operation is really about a relationship between multiple objects, not one object's own responsibility.**
2. **The operation would require giving one object knowledge of, or authority over, another object it doesn't conceptually own.**
3. **The operation represents a significant domain process or transformation, and forcing it onto an arbitrary object would be a distortion — it would exist there only because some class had to host the code, not because it belongs there.**

### Worked example: funds transfer
```
class FundsTransferService:
    def transfer(self, source: Account, destination: Account, amount: Money) -> None:
        if source.balance() < amount:
            raise InsufficientFundsError()
        source.withdraw(amount)
        destination.deposit(amount)
```
`Account.withdraw()` and `Account.deposit()` are legitimate entity methods — each is a rule about a *single* account's own state (it can't go negative, say). But "transfer" as a coordinated operation across two accounts, with its own failure semantics (partial transfer must never happen), doesn't belong to either account individually — it's promoted to a service. Note the service is thin: it delegates the actual state changes back to the entities' own methods rather than reaching in and mutating their internals directly, respecting encapsulation while still hosting the cross-object coordination.

### Worked example: a pricing engine that spans multiple objects
An e-commerce checkout needs to compute a final price given a `Cart`, a `Customer` (whose loyalty tier affects discounts), and a currently-active `PromotionCatalog`. None of `Cart`, `Customer`, or `Promotion` should individually own this calculation — it would force, say, `Cart` to know about loyalty tiers (a `Customer` concern) and about which promotions are currently active (a separate catalog concern), coupling three unrelated concepts into one object for no good reason.
```
class PricingService:
    def calculate_total(self, cart: Cart, customer: Customer, promotions: PromotionCatalog) -> Money:
        subtotal = cart.subtotal()
        loyalty_discount = customer.loyalty_tier().discount_rate() * subtotal
        applicable_promos = promotions.applicable_to(cart, customer)
        promo_discount = sum(p.discount_for(cart) for p in applicable_promos)
        return subtotal - loyalty_discount - promo_discount
```
This keeps `Cart`, `Customer`, and `Promotion` each focused on their own responsibilities, while `PricingService` owns the cross-cutting calculation as a first-class, testable domain concept with its own name that a domain expert would recognize ("how do we calculate the total" is a real business question with a real business answer, worth naming explicitly).

### Domain services versus application services versus infrastructure services
This is the single most common confusion when learning this pattern. There are three different kinds of "service" in a layered system (`ddd-evans/03`), and only one of them is what this lesson is about:
- **Domain service**: pure business logic spanning multiple domain objects, living in the domain layer, with zero infrastructure dependencies (`FundsTransferService`, `PricingService` above).
- **Application service**: orchestration in the application layer — fetches objects via repositories, calls domain methods/services, manages transactions, publishes events. Contains no business *rules* itself, only sequencing (see `ddd-evans/02`'s `SubmitOrderUseCase` example).
- **Infrastructure service**: technical capability with no business meaning — an email-sending service, a PDF-rendering service, a payment-gateway client. Lives in the infrastructure layer.

Conflating these — especially building a bloated "OrderService" that mixes real business rules with database calls and email-sending — is one of the most common and costly mistakes teams make; it recreates the anemic-model-plus-service-dumping-ground anti-pattern warned about in `ddd-evans/02`, just with a more official-sounding name.

### Keep services thin and push behavior into entities/values when possible
A domain service should be a last resort, not a default. Before reaching for a service, ask whether the operation actually belongs on one of the participating objects — `Account.withdraw()` is correctly on `Account`, not pulled out into a service, because it's genuinely about one account's own state and rules. Overusing services turns entities and value objects into anemic data bags (violating `ddd-evans/02`'s core goal) while all the real logic accumulates in a growing pile of stateless service classes — which is exactly the anti-pattern this whole building-block chapter of the book is trying to prevent.

## Pros
- Gives cross-object domain processes an honest, explicit, nameable home instead of forcing them awkwardly onto one arbitrarily-chosen participant.
- Keeps entities and value objects focused and free of unnatural cross-object dependencies.
- Domain services are easy to test in isolation — pure functions of their (domain object) arguments, no hidden state.

## Cons
- Overused, services become a dumping ground that hollows out entities into anemic data holders — the single most common misapplication of this pattern in real codebases.
- The line between "this belongs on the entity" and "this needs a service" requires real judgment and is a frequent source of disagreement/bikeshedding on teams.
- Confusing domain services with application or infrastructure services (all sharing the word "service") leads to bloated classes that mix business rules with orchestration and technical plumbing, defeating layering (`ddd-evans/03`) entirely.

## Alternatives
- **Entity/value-object methods** — always the preferred default when the behavior genuinely belongs to one object's own responsibility; reach for a service only when it doesn't.
- **Domain events plus reactive handlers** — for cross-object processes that don't need to happen synchronously/transactionally, model the interaction as an event (`OrderPlaced`) with independent handlers reacting to it, rather than a service directly coordinating both sides; this decouples the objects further at the cost of eventual (not immediate) consistency.
- **Double dispatch / visitor patterns** — a more object-oriented way to handle some "operation spanning two types" scenarios without a separate service class, more common in statically-typed OO languages with strong type systems; adds its own complexity and is less commonly reached for in practice than a straightforward service.

## When to use it
Reach for a domain service when an operation genuinely spans multiple domain objects, represents a real business process with its own name, and would force an unnatural ownership relationship if pinned onto any single participant.

## When NOT to use it
Don't create a service just because a method needs "somewhere to live" — check first whether it's really a single object's own responsibility (then it's an entity or value-object method), and don't let "service" become a synonym for "miscellaneous business logic dumping ground," which recreates the anemic-model problem `ddd-evans/02` warns against.

## Key takeaways / mental model
Ask "whose responsibility is this, really?" If the honest answer is "it's not really about any one of these objects individually, it's about the process connecting them," that's a domain service. If the honest answer is "well, I guess I could put it on any of them," that's usually a sign it actually belongs on one specific object and you just haven't identified which.

## Self-check questions
1. Why shouldn't `transfer()` live as a method on `Account` (e.g., `sourceAccount.transferTo(destAccount, amount)`)? What ownership problem does that create?
2. Distinguish a domain service from an application service using the `PricingService` and `SubmitOrderUseCase` examples. What's in each, and what's deliberately excluded from each?
3. Describe the anemic-domain-model failure mode this pattern can accidentally cause. What's the warning sign that a codebase has fallen into it?
4. Take a cross-object operation from a domain you know well and decide: does it belong on one of the objects, or does it need a service? Justify the call.

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 5: "A Model Expressed in Software" (Services section).
