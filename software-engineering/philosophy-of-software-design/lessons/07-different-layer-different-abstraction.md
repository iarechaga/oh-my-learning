---
id: philosophy-of-software-design/07
subject: philosophy-of-software-design
title: Different Layer, Different Abstraction
slug: different-layer-different-abstraction
status: drafted
mastery:
seniority: senior
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 7
prerequisites: [philosophy-of-software-design/04]
created: 2026-08-10
updated: 2026-08-10
---

# Different Layer, Different Abstraction

## TL;DR
Each layer in a system should represent a genuinely different level of abstraction from the layers above and below it — when adjacent layers look structurally similar (a "pass-through" layer that just forwards calls, or a "decorator" layer that adds only a trivial amount), that's a specific, named smell suggesting the layering itself may not be earning its cost.

## The idea
Layering (separating a system into levels, each building on the one below) is a foundational technique for managing complexity (echoing `architecture/fundamentals`'s treatment at the architectural scale) — but layering is only valuable when each layer actually represents something meaningfully different from its neighbors. If two adjacent layers end up looking structurally similar — same method names, same parameter shapes, one layer just calling straight through to the next with little or no added value — the *layering itself*, not just some code within it, has become the problem: you've paid the structural cost of a boundary (an interface to learn, a hop to trace through) without getting a corresponding benefit (a genuinely different, useful abstraction).

## How it works

### Pass-through methods — the most visible symptom
A **pass-through method** does nothing except call another method, forwarding the same (or nearly the same) arguments, with no meaningful transformation, decision, or added value in between. This is the clearest, most mechanically-checkable instance of the "same abstraction, different layer" problem this chapter names.

**Worked example.**
```
class OrderController:
    def create_order(self, request):
        return self.order_service.create_order(request)   # pure pass-through, adds nothing

class OrderService:
    def create_order(self, request):
        return self.order_repository.save(Order.from_request(request))
```
`OrderController.create_order` doesn't do anything an `OrderService.create_order` call couldn't do directly — it's not translating between abstraction levels (a controller layer's job, conceptually, is to translate between HTTP/transport concerns and domain concerns), it's just relaying. If this pattern repeats across *every* method on the controller, the controller layer as a whole isn't adding a genuinely different abstraction — it's a shallow module (`philosophy-of-software-design/03`) sitting on top of a deeper one, contributing interface complexity (another class to learn, another hop to trace through a debugger) without contributing corresponding value.

**Contrast — a controller method that IS earning its layer:**
```
class OrderController:
    def create_order(self, request):
        validated = self.validate_http_payload(request)      # transport-level concern, genuinely different from domain logic
        try:
            order = self.order_service.create_order(validated)
            return HttpResponse(201, order.to_json())          # translates domain result back to HTTP concern
        except OrderValidationError as e:
            return HttpResponse(400, {"error": str(e)})
```
Here, the controller genuinely operates at a different abstraction level than the service — it's handling HTTP-specific concerns (status codes, payload shape, transport-level error translation) that the domain-focused `OrderService` correctly has no business knowing about. This is a layer earning its keep, not a pass-through.

### Decorators that add too little
A related symptom: a class that wraps another (structurally resembling the Decorator pattern, `design-patterns/07`) but adds only a trivial amount of behavior on top — logging a single line, or forwarding with one minor parameter tweak — without genuinely representing a different concern. Ousterhout's caution here isn't that decoration is bad (it's a legitimate, named pattern for good reason) — it's that a decorator layer should still earn its interface cost by adding *meaningful* behavior, not just exist because "we might want to add something here eventually" (echoing `pragmatic-programmer/05`'s speculative-abstraction caution, applied here specifically to layering).

### The fix: either eliminate the layer, or genuinely differentiate it
Once a pass-through or trivial-decorator layer is identified, the chapter's suggested responses are direct:
1. **Eliminate the redundant layer** — if a layer genuinely adds nothing, callers should talk directly to the layer beneath it, removing the extra hop entirely.
2. **Merge the two layers** — if the reason for separation was historical or aspirational rather than a genuine present abstraction difference, combining them into one class/module (at the appropriate depth, per `philosophy-of-software-design/03`) may be the more honest design.
3. **Genuinely differentiate the layer's responsibility** — if there's a real reason the layer should exist (e.g., the controller example above), make sure it's actually doing that differentiated work consistently, not just in some methods while others remain pure pass-throughs.

### Why this matters beyond aesthetics
A system riddled with pass-through layers directly produces `philosophy-of-software-design/01`'s cognitive-load symptom in a specific, avoidable way: a developer trying to trace how a request is actually handled must step through several layers that each add no real information, multiplying the number of files/methods they must open and mentally track for zero corresponding insight — pure overhead, imposed on every single future reader trying to understand the flow, in exchange for no genuine abstraction benefit at all.

## Pros
- Naming "pass-through methods" as a specific, checkable symptom makes an otherwise-vague "this layering feels unnecessary" complaint concrete and actionable.
- Eliminating or merging redundant layers directly reduces the number of hops a reader must trace to understand a flow, with no loss of genuine abstraction value.
- Encourages deliberate justification for every layer boundary, rather than layering by default or by habit (e.g., always having a separate "controller," "service," and "repository" layer regardless of whether each genuinely differs in abstraction).

## Cons
- Some layering exists for reasons beyond pure abstraction difference within a single codebase — e.g., enforcing architectural boundaries for testability or for future extensibility (a controller/service split can matter even with some pass-through methods, if it keeps HTTP concerns swappable independent of domain logic) — collapsing such layers purely because some methods currently pass through can sacrifice a real, if not code-visible, architectural benefit.
- Distinguishing "a pass-through that should be eliminated" from "a layer that's *mostly* doing genuine work, with a few incidentally simple methods" requires judgment; not every simple-looking method in a layered architecture is a smell.
- Merging layers to eliminate pass-throughs can reduce flexibility to later swap one layer's implementation independently (echoing `clean-code/11`'s construction/use separation) if done without considering that trade-off.

## Alternatives
- **Uniform layering conventions regardless of per-method abstraction difference** (e.g., always maintaining a controller/service/repository split as an architectural standard) — trades some of this chapter's efficiency argument for consistency and architectural predictability across a large codebase or team, a reasonable trade-off in some organizational contexts.
- **Vertical slice architecture** — organizes code by feature rather than by horizontal layer, sidestepping the pass-through-layer problem by not imposing uniform layers across unrelated features in the first place.
- **Explicit architectural boundary enforcement via testing/linting** (e.g., dependency-direction checks) — retains a layer's *structural* separation for architectural reasons even where individual methods look like pass-throughs, treating the boundary's value as independent of any single method's local simplicity.

## When to use it
Scrutinize any class/layer where a substantial fraction of its methods are pure pass-throughs — ask whether the layer as a whole is earning its interface cost, and either eliminate/merge it or ensure it's genuinely doing differentiated work throughout, not just in some methods.

## When NOT to use it
Don't eliminate a layer purely because some (not most) of its methods happen to be simple pass-throughs, if the layer's overall boundary still serves a genuine architectural purpose (independent testability, independent evolution, enforced separation of concerns) beyond what any single method's complexity suggests.

## Key takeaways / mental model
When tracing how a request or operation flows through your system, count the layers that add zero transformation or decision-making value along the way. Each one is pure overhead for every future reader — either give it real work to do, or remove it.

## Self-check questions
1. Using the `OrderController` example, explain the specific difference between the pass-through version and the version that genuinely earns its layer.
2. Describe a layer from your own codebase where most methods are pass-throughs. What would eliminating or merging it change, and what (if anything) would be lost?
3. Why might a controller/service split still be worth keeping even if some individual methods are pass-throughs? What's the counterargument to eliminating the layer in that case?
4. How does this chapter's pass-through smell relate to `philosophy-of-software-design/03`'s deep-module criterion?

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 7: "Different Layer, Different Abstraction".
