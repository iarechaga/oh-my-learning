---
id: ddd-evans/03
subject: ddd-evans
title: Layered architecture for model integrity
slug: layered-architecture-for-model-integrity
status: drafted
mastery:
seniority: mid
source: Domain-Driven Design (Eric Evans), Part II, Chapter 4
prerequisites: [ddd-evans/02]
created: 2026-08-10
updated: 2026-08-10
---

# Layered architecture for model integrity

## TL;DR
Layered architecture separates a system into User Interface, Application, Domain, and Infrastructure layers, each depending only on the layers below it (or on abstractions), so that domain logic (`ddd-evans/02`) stays uncontaminated by delivery mechanisms and technical plumbing.

## The idea
Isolating the domain layer is a goal; layered architecture is the concrete structural pattern that achieves it. Without an explicit layering discipline, business rules leak everywhere — into SQL queries, into UI event handlers, into serialization code — because nothing stops a developer from reaching for the nearest convenient class to add "just one more check." Each leak is small and locally reasonable, but the cumulative effect is a system where no single place holds the true, complete statement of a business rule, and every change requires hunting across the codebase to find every place a rule might be duplicated or half-implemented.

Evans proposes four conceptual layers, each with a distinct responsibility, connected by a rule of dependency direction: a layer may depend on the layers below it, but never the reverse (or, more precisely, higher layers depend on abstractions the lower layers can satisfy, which is the essence of what later became "the dependency inversion principle" applied to architecture — hexagonal/clean architecture are direct descendants of this idea).

## How it works

### The four layers
1. **User Interface (Presentation)** — shows information to the user and interprets user commands. Knows about HTML forms, JSON responses, CLI flags. Knows nothing about business rules.
2. **Application layer** — thin. Coordinates tasks and delegates work to the domain layer; it does not contain business rules itself, only orchestration ("load this order, call submit on it, save it, publish an event"). This layer is also where cross-cutting application concerns (authorization checks tied to a use case, transaction boundaries) typically live.
3. **Domain layer (Model layer)** — the heart of the system, per `ddd-evans/02`: entities, value objects, domain services, business rules, business state.
4. **Infrastructure layer** — supports the other layers: databases, message queues, filesystem, external API clients, framework plumbing. Provides implementations of interfaces the domain or application layer defines (e.g., a `PostgresOrderRepository` implementing an `OrderRepository` interface declared in the domain layer — see `ddd-evans/10`).

### Worked example: placing an order, layer by layer
- **UI**: an HTTP controller receives a POST `/orders/{id}/submit` request, extracts the order ID from the path, and calls the application layer. It has no idea what "submitting" means as a business operation.
```
@app.post("/orders/{id}/submit")
def submit_order_endpoint(id):
    submit_order_use_case.execute(id)
    return JsonResponse(status=200)
```
- **Application layer**: coordinates — fetch the aggregate, invoke the domain operation, persist, publish an event. No business rule appears here.
```
class SubmitOrderUseCase:
    def __init__(self, order_repository, event_publisher):
        self.orders = order_repository
        self.events = event_publisher

    def execute(self, order_id):
        order = self.orders.find_by_id(order_id)
        order.submit()                      # all the actual rule-checking happens inside domain code
        self.orders.save(order)
        self.events.publish(OrderSubmitted(order_id))
```
- **Domain layer**: `Order.submit()` (from `ddd-evans/02`) contains the actual rules — draft status required, minimum total, etc.
- **Infrastructure layer**: `PostgresOrderRepository` implements `find_by_id`/`save` against real tables; a `KafkaEventPublisher` implements `publish` against a real broker. Neither of these knows what "submitting an order" *means* — they just move bytes.

Notice what each layer does *not* know: the UI doesn't know about draft/submitted states, the application layer doesn't know the minimum-total rule, and the domain layer doesn't know whether persistence is Postgres or an in-memory list. That separation is the entire point — each concern changes for its own reasons (a new UI framework, a new persistence technology, a new business rule) without forcing changes in the others.

### The dependency-direction rule in practice
The domain layer defines the `OrderRepository` interface (an abstraction it needs), and the infrastructure layer provides the concrete implementation — this is *inversion*: infrastructure depends on an abstraction owned by the domain, not the domain depending directly on infrastructure. Without this inversion, the domain layer would need to import a database driver just to declare "I need to save orders," which would immediately violate the isolation this whole pattern exists to protect. See `ddd-evans/10` for the repository pattern in full detail.

### A layering violation, and its cost
Suppose a developer, under deadline pressure, adds a check directly in the controller: `if order.total < 10: return error(...)`. Now the "minimum order total" rule exists in *two* places — the controller and (presumably) also in the domain layer, or worse, only in the controller and nowhere in the domain layer at all. A batch import job that also submits orders won't go through the controller, so it silently bypasses the rule. This is the layering violation made concrete: any rule check outside the domain layer is a rule that can be bypassed by any code path that doesn't happen to go through that particular controller.

## Pros
- Each layer can change for its own reasons without rippling into the others — swapping a REST API for a GraphQL API touches only the UI layer; swapping Postgres for DynamoDB touches only infrastructure.
- The domain layer becomes testable in complete isolation, with no database, no HTTP server, no test containers — pure, fast unit tests.
- Makes the dependency-direction rule an explicit, checkable architectural constraint rather than an unenforced convention, which static analysis or module boundaries (see `ddd-evans/07`) can enforce.
- Onboarding is easier because "where does this logic belong" has a clear, teachable answer.

## Cons
- Adds real indirection — more interfaces, more files, more mapping between layers — that can feel like ceremony on small projects.
- Poorly enforced layering ("layering in name only," where the application layer secretly reaches into infrastructure directly) gives none of the benefit while still paying the structural cost.
- The application layer can become a dumping ground for logic that's ambiguous between "orchestration" and "business rule," requiring judgment calls that a junior team may get wrong repeatedly without review.

## Alternatives
- **Hexagonal / Ports-and-Adapters architecture** (Cockburn) — a closely related, more symmetric framing: the domain is the "hexagon" at the center, and everything else (UI, database, external services) is a "port and adapter" plugging into it; conceptually the same dependency-inversion discipline as this lesson, described from a different angle. See `implementing-ddd` for a treatment that leans on this framing directly.
- **Clean Architecture** (Robert Martin) — a further generalization with concentric rings (entities, use cases, interface adapters, frameworks); same core rule (dependencies point inward), more prescriptive about the number and naming of rings.
- **Big ball of mud / no explicit layering** — the default outcome of not applying this pattern; faster to start, but accumulates exactly the leakage problems this lesson describes as the system grows.

## When to use it
Use explicit layering on any system where the domain has real rules worth protecting and where the system is expected to survive more than one delivery mechanism, one persistence technology, or one significant refactor — which describes most production line-of-business software beyond a short-lived prototype.

## When NOT to use it
For a genuinely tiny script or a prototype meant to be thrown away, four formal layers are pure overhead; a single flat module is faster and there's no long-term cost to worry about since the code won't live long enough for the leakage problem to bite.

## Key takeaways / mental model
Ask of any piece of code: "if I deleted the database and the web framework entirely, would this code still make sense?" If yes, it belongs in the domain layer. If no, it belongs in infrastructure or UI, and it should not know anything about business rules.

## Self-check questions
1. In the order-submission example, where would you put a rule like "VIP customers can submit orders below the minimum total"? Walk through which layer it belongs in and why.
2. Why does the domain layer define the `OrderRepository` interface instead of the infrastructure layer defining it and the domain layer importing it?
3. Give an example (from a project you've worked on) of business logic that leaked into a controller or a database migration. What made it possible for that leak to happen unnoticed?
4. Is the application layer allowed to contain conditional logic at all? What's the test for whether a piece of conditional logic is "orchestration" versus "a business rule"?

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 4: "Isolating the Domain".
