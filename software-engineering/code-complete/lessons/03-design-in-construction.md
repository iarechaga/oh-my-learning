---
id: code-complete/03
subject: code-complete
title: Design in Construction (Heuristics)
slug: design-in-construction
status: drafted
mastery:
seniority: mid
source: Code Complete, 2nd ed. (Steve McConnell), Chapter 5
prerequisites: [code-complete/02]
created: 2026-08-10
updated: 2026-08-10
---

# Design in Construction (Heuristics)

## TL;DR
Software design is a set of competing heuristics you apply iteratively, not a single algorithm with one correct output — you try an approach, evaluate it against criteria (coupling, cohesion, complexity), and revise, repeatedly, because the first design you think of is rarely the best one. McConnell's practical heuristics (find real-world objects, identify what varies and encapsulate it, iterate) give concrete starting points for that process.

## The idea
Unlike, say, sorting an array, software design has no single correct answer that an algorithm can compute — there are many workable designs for any nontrivial problem, differing in their trade-offs, and picking among them requires judgment guided by heuristics rather than a deterministic procedure. This chapter's core message is that design is fundamentally **iterative**: you generate a candidate design, evaluate it against known-good criteria (low coupling, high cohesion, manageable complexity — echoing `code-complete/02`), find its weaknesses, and revise — repeating this loop rather than expecting to nail the final design on the first attempt.

## How it works

### Heuristic 1: Find real-world objects
Look at the problem domain and identify the nouns that matter — the entities domain experts already talk about (a `Customer`, an `Order`, an `Invoice`). Modeling software structure around these tends to produce a design that maps naturally onto how the domain actually works, and — as a side effect — makes the code easier for domain experts (and future developers who learn the domain) to reason about, since the code's vocabulary matches the domain's vocabulary (a lighter-weight version of `domain-modeling`'s ubiquitous language).

### Heuristic 2: Identify what's likely to vary, and encapsulate it
The single most load-bearing heuristic in the chapter: for every design decision, ask "how likely is this specific thing to change, and if it does, how contained can I make that change?" — then wrap the volatile parts behind a stable interface so a future change is localized rather than scattered (directly connecting to `pragmatic-programmer/05`'s reversibility and `pragmatic-programmer/10`'s configuration decoupling).

**Worked example.** Designing a notification system: the *decision of which channel to notify through* (email today, possibly SMS or push notifications later) is highly likely to vary; the *fact that some notification needs to happen after an order ships* is comparatively stable. Encapsulate the volatile part:
```
class NotificationSender:
    def notify(self, user, message): raise NotImplementedError

class EmailNotificationSender(NotificationSender):
    def notify(self, user, message): ...

# stable part, unaffected by future channel changes:
def on_order_shipped(order):
    sender.notify(order.customer, f"Your order {order.id} has shipped")
```
When SMS support is added later, only a new `SMSNotificationSender` class is needed — the stable `on_order_shipped` logic, and every other caller, is untouched.

### Heuristic 3: Design for change with information hiding
A close cousin of Heuristic 2, applied more broadly: design classes and modules so their internal implementation details are hidden, and only a stable, minimal interface is exposed — echoing `clean-code/06` and `clean-code/11`. The chapter frames this less as a rule about class structure specifically and more as a general design attitude: assume you don't yet know everything that will change, so default toward hiding rather than exposing, unless there's a specific reason a caller needs direct access.

### Heuristic 4: Iterate — the first design is rarely the best one
McConnell explicitly frames the *first* candidate design you produce as a rough draft, not a final answer, and recommends deliberately generating and comparing a few alternative approaches to the same design problem before committing — because the first idea that comes to mind is usually influenced by whatever you happened to think of first (a familiar past solution, an available library), not necessarily the best fit for this specific problem's actual constraints. Iterating even briefly — sketching a second, structurally different candidate design and comparing the two against coupling/cohesion/complexity criteria — routinely surfaces a better option than committing to the first idea.

### Evaluating candidate designs against concrete criteria
Rather than "does this feel right," the chapter pushes toward checkable criteria when comparing design alternatives:
- **Coupling** — how much does a module depend on the internals of others? (Lower is generally better — see `pragmatic-programmer/04`.)
- **Cohesion** — do a module's parts work together toward one purpose? (Higher is generally better — see `clean-code/10`.)
- **Complexity** — how much must be held in mind to understand and safely change this design? (Lower is generally better — see `code-complete/02`.)
- **Extensibility along the axis you predicted would vary** — does the design actually make the change you anticipated (per Heuristic 2) cheap, or did the encapsulation boundary miss the real seam?

## Pros
- Treating design as iterative, criteria-evaluated, and heuristic-guided produces better outcomes than committing to a single first-pass design out of overconfidence or time pressure.
- "Identify what varies and encapsulate it" is a concrete, broadly applicable technique that directly operationalizes several more abstract principles from earlier lessons (reversibility, orthogonality, information hiding).
- Modeling around real-world domain objects produces designs that are easier for both new developers and domain experts to reason about.

## Cons
- Genuine design iteration takes real time that's easy to skip under deadline pressure, especially since the first design "seems to work" and the cost of a worse alternative is often invisible until much later.
- Predicting "what's likely to vary" is a judgment call that can be wrong — encapsulating the wrong axis of variation (or none at all) provides no benefit and adds unnecessary indirection.
- Modeling too literally around real-world objects can produce a design that mirrors the domain's incidental structure rather than its actual behavior, sometimes producing anemic, data-only classes (echoing `clean-code/06`'s object/data-structure duality) rather than a genuinely well-designed object model.

## Alternatives
- **Design patterns as pre-evaluated heuristic solutions** (see `software-engineering/design-patterns`) — a catalog of already-iterated, named design responses to recurring problems, letting you skip some of the from-scratch iteration this chapter describes by recognizing "this is a Strategy pattern situation" directly.
- **Test-driven design** — let the shape of tests you'd want to write drive the design iteratively, rather than reasoning about coupling/cohesion abstractly first — a more concrete, execution-grounded route to a similar destination.
- **Formal architectural decision records (ADRs)** (see `architecture/fundamentals`) — for larger-scale design decisions than this chapter's routine/class-level focus, formally documenting the alternatives considered and why one was chosen, rather than iterating informally in your head or on a whiteboard.

## When to use it
Apply "identify what's likely to vary and encapsulate it" as a standing question for every nontrivial design decision. Deliberately sketch at least a second candidate design for any design decision significant enough that getting it wrong would be costly to change later.

## When NOT to use it
Don't iterate extensively on trivial, low-consequence design decisions where the first reasonable approach is clearly adequate — that's wasted design effort disproportionate to the stakes (echoing `code-complete/01`'s doghouse-vs-skyscraper scaling principle). Don't encapsulate a "what varies" axis you're only speculating might matter with no real evidence — that risks the speculative-generality smell from `clean-code/12`.

## Key takeaways / mental model
For any design decision, ask two questions in sequence: "what part of this is most likely to change later, and have I hidden it behind a stable boundary?" and "is this actually the best design I could produce, or just the first one I thought of?" Both questions cost little to ask and routinely improve the outcome.

## Self-check questions
1. Using the notification-sender example, identify a different system you've worked on where "what's likely to vary" was correctly (or incorrectly) identified and encapsulated.
2. Why does McConnell recommend generating more than one candidate design before committing, even briefly?
3. Explain how "coupling, cohesion, complexity" as evaluation criteria connect back to `code-complete/02`'s cognitive-load argument.
4. Give an example of modeling too literally around a real-world object, producing a design that's easy to understand but awkward to actually use.

## References
- Code Complete, 2nd ed. (Steve McConnell), Chapter 5: "Design in Construction".
