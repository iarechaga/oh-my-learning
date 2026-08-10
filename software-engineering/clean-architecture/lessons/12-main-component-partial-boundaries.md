---
id: clean-architecture/12
subject: clean-architecture
title: The Main Component and Partial Boundaries
slug: main-component-partial-boundaries
status: drafted
mastery:
seniority: senior
source: Clean Architecture (Robert C. Martin), Chapters 23-24
prerequisites: [clean-architecture/08, clean-architecture/09]
created: 2026-08-10
updated: 2026-08-10
---

# The Main Component and Partial Boundaries

## TL;DR
The `Main` component is the one deliberately impure, outermost place in the whole architecture where every concrete detail (which database, which framework, which specific implementations) is known and wired together — the composition root, in `clean-code/11`'s terms, elevated to a first-class architectural concept. Because full boundaries (with a real, separately-releasable component and interface on each side) are expensive, Martin also describes several cheaper "partial boundary" techniques for getting *some* of a boundary's decoupling benefit without paying its full structural cost — useful when full ceremony isn't yet justified but total coupling isn't acceptable either.

## The idea
`clean-architecture/08`'s dependency rule says every dependency points inward — but *something*, somewhere, has to actually know about and instantiate the concrete implementations (which `OrderRepository` implementation, which `PaymentGateway` implementation) and wire them together into a running system. Martin's answer is the **Main component**: a small, deliberately dependency-rule-exempt outermost component whose entire job is exactly this wiring, and nothing else — no business logic lives here, only construction and configuration.

## How it works

### Main as the composition root, elevated to an architectural concept
Directly extending `clean-code/11`'s construction/use separation to the scale of an entire application: `Main` is the *one* place allowed to `import` and instantiate every concrete class in the system — the specific database driver, the specific web framework's setup code, the specific concrete implementations of every interface the inner circles defined. Every other component in the system depends only on interfaces (per the Dependency Rule); `Main` is where those interfaces finally get matched with real implementations and everything is assembled into a runnable application.

**Worked example.**
```
# main.py — the ONE place allowed to know every concrete detail
def main():
    db_connection = connect_to_postgres(config.DATABASE_URL)   # concrete detail
    order_repository = PostgresOrderRepository(db_connection)   # concrete implementation
    payment_gateway = StripeGateway(config.STRIPE_KEY)           # concrete implementation

    place_order_use_case = PlaceOrderUseCase(
        repository=order_repository,      # wired via interfaces
        gateway=payment_gateway,
    )

    web_app = build_web_app(place_order_use_case)   # wires the Use Case into the delivery mechanism
    web_app.run()
```
Nothing about `PlaceOrderUseCase` (or `Order`, or any other inner-circle class) ever mentions Postgres or Stripe by name — those concrete choices live entirely inside `main()`, which is, deliberately, the single component in the whole system where the Dependency Rule's "no outward-facing knowledge" restriction doesn't apply, precisely because its entire purpose *is* to hold that knowledge, all in one place, so nowhere else has to.

### Why concentrating this knowledge into one place matters
This directly mirrors `pragmatic-programmer/03`'s DRY and `philosophy-of-software-design/04`'s leakage concerns, applied at the whole-application scale: if the knowledge of "which concrete database, which concrete payment gateway" were scattered across many files (each independently constructing its own dependencies), swapping any one of them would require hunting down every scattered construction site. Concentrating it into `Main` means a swap is a change to exactly one file — the practical payoff of the entire Dependency-Rule discipline, realized concretely at the point where the system actually gets assembled and run.

### Partial boundaries — cheaper alternatives when a full boundary isn't yet justified
`clean-architecture/09` established that full boundaries (a genuine, separately-releasable component on each side, per `clean-architecture/05`-`06`) have a real cost, and shouldn't be drawn reflexively. But sometimes you want *some* decoupling benefit without paying that full cost yet — Martin describes several intermediate techniques:
- **Skip the last step (keep one codebase, but maintain the interface split).** Define the interface and both sides' implementations, but don't actually split them into separately-versioned, separately-deployable components — everything stays in one codebase/deployment unit, but the *source-code* dependency structure (interfaces, inward-pointing dependencies) is already in place, ready to be split into real components later if and when that becomes genuinely justified, with much less rework than starting from a fully entangled structure.
- **One-dimensional boundaries (Strategy pattern, `design-patterns/09`).** Simply defining an interface and swapping implementations at a single point, without the full ceremony of a bidirectionally-protected boundary — cheaper, but offers less protection than a full boundary (a careless change on the "wrong" side can still leak coupling back through, since there's no separately-versioned component enforcing the separation).
- **Facades** (`design-patterns/07`). A Facade class can sit at a would-be boundary, providing a simplified, boundary-like interface to a set of classes that aren't actually separated into different components at all — cheaper still, but provides essentially no protection against the facade's own clients reaching past it to the concrete classes underneath if they're motivated to (nothing enforces the boundary beyond convention).

### Choosing among full boundaries, partial boundaries, and no boundary at all
Martin frames this explicitly as a spectrum of cost versus protection, to be chosen deliberately per boundary rather than applying one blanket policy everywhere: full boundaries for genuinely volatile, high-stakes dependencies where the investment is clearly justified now; partial boundaries (especially the "skip the last step" variant) for dependencies you suspect *might* need full separation later but don't have enough evidence to justify the cost yet; and no boundary at all for dependencies with no credible volatility, echoing `clean-architecture/09`'s cost/benefit test directly.

## Pros
- Main as a deliberate, well-understood exception to the Dependency Rule concentrates all concrete-detail knowledge into one place, making technology swaps a localized, single-file change.
- Partial boundaries let a team capture some of a full boundary's future-proofing benefit at a fraction of the immediate structural cost, deferring the more expensive full separation until real evidence justifies it.
- The explicit cost/protection spectrum gives a principled way to choose the right level of boundary investment per dependency, rather than a single, blanket policy applied uniformly.

## Cons
- `Main` can, if not disciplined, become a dumping ground for logic that should have lived elsewhere — its exemption from the Dependency Rule is easy to abuse as an excuse to put things there that don't actually belong.
- Partial boundaries, by design, offer less protection than full ones — a "skip the last step" boundary can still be silently violated by a careless change, since nothing enforces separate deployability the way genuine component boundaries do.
- Choosing the wrong point on the cost/protection spectrum (too cheap for a dependency that turns out to be genuinely volatile, or too expensive for one that never needed full separation) has a real correction cost either way.

## Alternatives
- **Dependency injection frameworks/containers**, instead of a hand-written `Main` — automate much of the wiring `Main` does manually, at the cost of some "magic" that can make it harder to trace exactly what's wired to what without inspecting the framework's configuration.
- **Multiple Main components for multiple entry points** (a web `Main`, a CLI `Main`, a test-harness `Main`) — a natural extension when a system genuinely has multiple delivery mechanisms, each with its own composition root wiring the same inner-circle Use Cases to different concrete outer-circle implementations.
- **No formal partial-boundary technique at all, accepting either full separation or none** — simpler to reason about, at the cost of losing the specific, deliberate middle path Martin's partial-boundary techniques provide for genuinely uncertain cases.

## When to use it
Use a dedicated `Main` component for every application's composition root, keeping it the sole place with knowledge of concrete implementations. Use partial boundaries (especially "skip the last step") for dependencies you suspect may need full separation eventually, but don't yet have enough evidence to justify the full cost.

## When NOT to use it
Don't let logic beyond pure construction/wiring accumulate inside `Main` — if `Main` starts making business decisions, that logic belongs in a Use Case, not in the composition root. Don't rely on a partial boundary's weaker protection for a dependency that's already known to be genuinely, urgently volatile — pay for the full boundary there instead.

## Key takeaways / mental model
Keep exactly one place (`Main`) that's allowed to know every concrete implementation detail, and make sure it does nothing else. For any dependency where you're unsure whether full separation is yet justified, consider a partial boundary (interfaces in place, but not yet separately deployed) as a deliberate, cheaper middle step rather than an all-or-nothing choice.

## Self-check questions
1. Using the `main()` example, explain what would need to change (and where) to swap Postgres for a different database, and confirm that change is confined to `Main`.
2. Describe a case where `Main` accumulated logic beyond pure wiring in a codebase you've seen. What problems did that cause, and how would you fix it?
3. Explain the "skip the last step" partial boundary technique, and describe a dependency in your own work where it would be an appropriate middle ground between full separation and none.
4. Why does a Facade-based partial boundary offer less protection than a full boundary? What specific kind of violation can slip through it?

## References
- Clean Architecture: A Craftsman's Guide to Software Structure and Design (Robert C. Martin), Chapter 23: "Presenters and Humble Objects" (Main component) and Chapter 24: "Partial Boundaries".
