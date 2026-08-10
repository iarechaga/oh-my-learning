---
id: clean-code/11
subject: clean-code
title: Systems and Separating Construction from Use
slug: systems
status: drafted
mastery:
seniority: senior
source: Clean Code (Robert C. Martin), Chapter 11
prerequisites: [clean-code/10]
created: 2026-08-10
updated: 2026-08-10
---

# Systems and Separating Construction from Use

## TL;DR
"How an object is built" and "how an object is used" are two different concerns that should live in different code — mixing construction logic (choosing implementations, wiring dependencies) into the same classes that use those objects couples business logic to configuration decisions that should be free to change independently. Dependency Injection and factories are the concrete mechanisms for keeping the split clean at system scale.

## The idea
Chapters up to this point mostly operate within a single function or class. This chapter zooms out to the scale of an entire application's construction — how the pieces get wired together into a running system — and argues that this wiring is itself a distinct concern from the business logic those pieces implement, and deserves its own clean separation.

The problem the chapter names directly: a class that both *uses* a collaborator (calls its methods to get real work done) and *constructs* that collaborator (decides which concrete implementation to instantiate, with which configuration) is doing two unrelated jobs at once — much like `clean-code/06`'s object/data-structure duality, and `clean-code/10`'s cohesion argument, applied specifically to the "which concrete thing do I depend on" decision. A business-logic class that internally does `payment_processor = StripeProcessor(api_key=os.environ["STRIPE_KEY"])` has bolted a configuration decision (which payment provider, with which credentials) into a class that should only care about *using* a payment processor abstractly, not about *choosing or configuring* one.

## How it works

### Why mixing construction and use is costly
- **It hardcodes a decision that should be flexible.** If the payment processor choice is buried inside the business-logic class, swapping providers (for a new market, for a fallback, for testing) means editing that business-logic class directly — even though the actual business logic (charge the customer, record the transaction) hasn't changed at all.
- **It makes the class hard to test in isolation.** A class that constructs its own real `StripeProcessor` internally can't easily be tested with a fake/mock processor, because the concrete dependency is baked in rather than supplied — directly undermining the orthogonality/testability goals from `pragmatic-programmer/04`.
- **It scatters configuration decisions across the whole codebase.** If every class that needs a database connection independently decides how to construct one, a single configuration change (connection pool size, credentials source) requires hunting down every scattered construction site instead of changing one central place.

### Dependency Injection — invert who does the constructing
The primary mechanism the chapter recommends: instead of a class constructing its own dependencies internally, the dependencies are **passed in** (via constructor, or a setter, or a framework-managed injection point) by some external code whose entire job is construction and wiring — commonly called the "main" component, composition root, or DI container.

**Worked example — before (construction and use mixed):**
```
class OrderService:
    def __init__(self):
        self.payment_processor = StripeProcessor(api_key=os.environ["STRIPE_KEY"])  # construction, buried
    def checkout(self, order):
        self.payment_processor.charge(order.total)  # use
```
**After (construction moved out, use remains):**
```
class OrderService:
    def __init__(self, payment_processor: PaymentProcessor):  # dependency injected, not constructed
        self.payment_processor = payment_processor
    def checkout(self, order):
        self.payment_processor.charge(order.total)  # use only

# somewhere else entirely — the composition root, the ONLY place that knows concrete types:
def build_order_service() -> OrderService:
    processor = StripeProcessor(api_key=os.environ["STRIPE_KEY"])
    return OrderService(payment_processor=processor)
```
Now `OrderService` only ever *uses* a `PaymentProcessor` abstraction — it has no idea Stripe exists, no idea where credentials come from, and can be tested with a fake `PaymentProcessor` trivially. All the construction knowledge (which provider, which credentials, from where) lives in exactly one place: `build_order_service` (or, in larger systems, a dedicated composition root / DI container configuration), which is the *only* code in the entire system allowed to know about concrete implementations.

### Factories — when construction logic itself needs to be dynamic
Sometimes the *use* side genuinely needs to decide, at runtime, which concrete type to construct (e.g., "construct a `PdfExporter` or `CsvExporter` depending on a user's chosen format") — plain, static dependency injection at startup can't express a decision that depends on runtime data. The book's answer: push that decision into a dedicated **factory** — a small object/function whose *only* job is to construct the right concrete type given some input, still kept separate from the business logic that then *uses* whatever the factory returns.
```
class ExporterFactory:
    def create(self, format: str) -> Exporter:
        if format == "pdf": return PdfExporter()
        if format == "csv": return CsvExporter()
        raise ValueError(f"unknown format: {format}")

class ReportService:
    def __init__(self, exporter_factory: ExporterFactory):
        self.exporter_factory = exporter_factory
    def export(self, report, format):
        exporter = self.exporter_factory.create(format)  # construction, isolated to the factory
        return exporter.export(report)                    # use
```
`ReportService` still never directly names `PdfExporter` or `CsvExporter` — the runtime decision is isolated inside `ExporterFactory`, a class whose entire, single responsibility (echoing `clean-code/10`) is exactly this decision, and nothing else.

### Cross-cutting concerns and the promise of separating construction from use at scale
At the scale of a whole system, this separation pays off further when combined with techniques like Aspect-Oriented Programming or decorator-based middleware for cross-cutting concerns (logging, transactions, security checks) — because business-logic classes that never construct their own dependencies also don't need to manually weave in logging/transaction code themselves; a composition root or framework can wrap dependencies with cross-cutting behavior *outside* the business logic entirely, keeping it focused purely on domain rules.

## Pros
- Business logic classes become trivially testable with fakes/mocks, since dependencies are supplied rather than self-constructed.
- All knowledge of concrete implementations and configuration concentrates in one place (a composition root), making system-wide changes (swap a provider, change credentials source) a small, localized edit.
- Cleanly separates "what the system does" from "how the system is wired," letting each evolve independently — the same business logic can be wired differently for tests, local dev, and production.

## Cons
- Introduces indirection (interfaces, injected dependencies, factories, possibly a DI framework) that adds real cognitive overhead for a reader unfamiliar with the pattern, especially in smaller systems where the flexibility may never be exercised.
- DI containers/frameworks, if overused, can make it hard to trace at a glance which concrete implementation actually gets wired in for a given class — "magic" wiring resolved by a framework config rather than visible in the code.
- Factories that grow to handle many cases can themselves become a maintenance burden if not kept simple and single-purpose.

## Alternatives
- **Service locator pattern** — objects pull their dependencies from a global registry at the point of use, rather than having them pushed in via constructor — achieves some decoupling from concrete types but hides the dependency (a class doesn't visibly declare what it needs in its constructor signature), which the book and most modern practice consider inferior to explicit DI for that reason.
- **Manual wiring without a framework ("poor man's DI")** — plain composition-root functions like the example above, with no DI container/framework — simpler to trace and reason about at small-to-medium scale, at the cost of more manual wiring code as the system grows.
- **Singletons / global static instances** — the most tightly-coupled alternative, where a class directly reaches for a globally-accessible single instance rather than having one injected — reintroduces the exact hidden-coupling and untestability problems this chapter is trying to eliminate.

## When to use it
Apply construction/use separation to any class with a dependency that could plausibly need to vary (across environments, across tests, across future implementation swaps) — which, in practice, includes most collaborators that represent an external system, a policy decision, or anything you'd want to fake in a test.

## When NOT to use it
Don't inject or factory-ize a dependency that will never plausibly vary and costs nothing to construct directly (e.g., a simple, stateless value object with no external dependencies of its own) — that's indirection without a corresponding flexibility or testability benefit. Don't reach for a full DI framework for a small system where a few plain composition-root functions would be equally clear and far simpler to trace.

## Key takeaways / mental model
Ask, of every class: "does this class decide *which* concrete implementation to use, or does it just *use* whatever it's given?" If it's deciding, that decision belongs in a dedicated construction point (a composition root or a factory) — not mixed into the same class that then uses the result, because those are two different concerns with two different reasons to change.

## Self-check questions
1. Find a class in code you've worked on that constructs its own dependency internally. Rewrite it to receive that dependency via constructor injection instead, and identify where the construction logic should move to.
2. Explain the difference between plain dependency injection and a factory, and give an example of a decision that genuinely requires a factory rather than static injection.
3. Why is the service locator pattern considered inferior to constructor injection, even though both avoid hardcoding concrete types inside business logic?
4. Describe a situation where introducing DI/factories would be over-engineering for a given piece of code, and explain why.

## References
- Clean Code: A Handbook of Agile Software Craftsmanship (Robert C. Martin), Chapter 11: "Systems".
- See also: `software-engineering/clean-architecture` for how this separation scales into a full dependency-rule-based architecture.
