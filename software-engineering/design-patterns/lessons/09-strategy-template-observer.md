---
id: design-patterns/09
subject: design-patterns
title: "Behavioral: Strategy, Template Method, Observer"
slug: strategy-template-observer
status: drafted
mastery:
seniority: mid
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 5
prerequisites: [design-patterns/02]
created: 2026-08-10
updated: 2026-08-10
---

# Behavioral: Strategy, Template Method, Observer

## TL;DR
Strategy makes an entire algorithm swappable at runtime by extracting it behind a common interface, chosen via composition. Template Method fixes the overall skeleton of an algorithm in a base class but lets subclasses override specific steps — the inheritance-based mirror image of Strategy's composition-based approach. Observer lets any number of interested objects be notified automatically when another object's state changes, decoupling the subject from needing to know who's watching.

## The idea
These three behavioral patterns address recurring problems in *how objects interact and vary their behavior* — as opposed to the structural patterns (`design-patterns/06`-`08`), which addressed how objects are *composed and related*. Strategy and Template Method solve closely related problems (swappable algorithms) via opposite mechanisms (composition vs. inheritance), making them a natural pair to contrast directly. Observer solves a different problem entirely: keeping multiple, independent, mutually-unaware objects synchronized when something they care about changes.

## How it works

### Strategy — swap an entire algorithm via composition
Extract an algorithm into its own class implementing a common interface, and have the class that needs the algorithm hold a reference to (compose) whichever concrete strategy it's configured with — directly `design-patterns/02`'s composition-over-inheritance principle, applied specifically to interchangeable algorithms.

**Worked example.**
```
class DiscountStrategy:
    def apply(self, total: float) -> float: raise NotImplementedError

class NoDiscount(DiscountStrategy):
    def apply(self, total): return total

class PercentageDiscount(DiscountStrategy):
    def __init__(self, pct): self.pct = pct
    def apply(self, total): return total * (1 - self.pct)

class Order:
    def __init__(self, discount_strategy: DiscountStrategy):
        self.discount_strategy = discount_strategy
    def total(self, subtotal):
        return self.discount_strategy.apply(subtotal)

order = Order(PercentageDiscount(0.1))     # strategy chosen and swappable at runtime
```
The discount algorithm can be swapped per-instance, at runtime, by passing a different strategy object — no subclassing of `Order` needed, and a new discount type is a new `DiscountStrategy` implementation, touching nothing else (echoing the "easy to add types" trade-off from `clean-code/06`).

### Template Method — fix the skeleton, let subclasses override the steps
Where Strategy swaps the *whole* algorithm, Template Method fixes the overall sequence of steps in a base class method, but makes individual steps abstract/overridable, so subclasses customize specific parts while the base class retains control of the overall structure and ordering.

**Worked example.**
```
class DataImporter:
    def run(self):                       # the template method — fixed sequence
        raw = self.read_source()
        parsed = self.parse(raw)
        self.validate(parsed)
        self.persist(parsed)

    def read_source(self): raise NotImplementedError
    def parse(self, raw): raise NotImplementedError
    def validate(self, parsed): pass       # optional hook, default no-op
    def persist(self, parsed): raise NotImplementedError

class CsvImporter(DataImporter):
    def read_source(self): return open("data.csv").read()
    def parse(self, raw): return parse_csv(raw)
    def persist(self, parsed): db.bulk_insert(parsed)
```
`CsvImporter` never overrides `run()` — the overall four-step sequence (read, parse, validate, persist) is fixed and enforced by the base class, guaranteeing every subclass follows the same process in the same order; subclasses only supply the format-specific pieces.

### Strategy vs. Template Method — the same underlying goal, opposite mechanisms
Both patterns let behavior vary while keeping some structure fixed, but: Template Method uses *inheritance* (the varying steps are overridden methods on a subclass, fixed at compile time, and the subclass inherits the whole enclosing structure) while Strategy uses *composition* (the varying algorithm is a separate object, swappable at runtime, with no inheritance relationship required at all). Directly connecting to `design-patterns/02`'s general guidance: Strategy is usually preferred when you want runtime flexibility or want to avoid the fragile-base-class risk; Template Method is a reasonable, simpler choice when the variation genuinely only needs to be fixed per-subclass (decided once, at class-definition time) and the fragile-base-class risk is judged acceptable for the specific, narrow "step override" being asked of subclasses.

### Observer — decouple a subject from the objects watching it
When multiple, potentially-varying objects need to be notified automatically whenever another object's state changes, Observer defines a subscription mechanism: the "subject" holds a list of registered "observers" and calls a notification method on each of them whenever relevant state changes — without the subject needing to know anything about what kind of objects its observers are or what they'll do with the notification.

**Worked example.**
```
class StockPrice:
    def __init__(self):
        self.observers = []
        self._price = 0
    def subscribe(self, observer): self.observers.append(observer)
    def set_price(self, new_price):
        self._price = new_price
        for observer in self.observers:
            observer.on_price_changed(new_price)     # subject never knows WHAT observers do

class PriceDisplay:
    def on_price_changed(self, price): print(f"Display updated: {price}")

class PriceLogger:
    def on_price_changed(self, price): log(f"Price changed to {price}")

stock = StockPrice()
stock.subscribe(PriceDisplay())
stock.subscribe(PriceLogger())
stock.set_price(105.50)   # both observers notified automatically, StockPrice never named either class
```
`StockPrice` has zero compile-time knowledge of `PriceDisplay` or `PriceLogger` — new observer types can be added (an alerting system, an analytics tracker) without ever modifying `StockPrice` itself, a direct instance of the Open/Closed Principle (see `software-engineering/clean-architecture`) and the basis for most reactive/event-driven UI frameworks and pub/sub messaging systems (see `architecture/system-design`).

### A caution with Observer: notification order and cascading updates
Because observers are notified in some (often insertion) order with no inherent guarantee about independence between them, a naive Observer implementation can produce subtle bugs if one observer's reaction to a notification triggers a further state change that re-notifies observers already partway through handling the original notification — an implicit temporal-coupling hazard (`pragmatic-programmer/11`) hiding inside a pattern that looks fully decoupled on the surface.

## Pros
- Strategy provides genuine runtime flexibility and avoids inheritance's fragile-base-class risk (`design-patterns/02`) for swappable algorithms.
- Template Method guarantees a fixed, correct overall process while still allowing meaningful per-subclass customization, useful when process integrity matters more than runtime flexibility.
- Observer decouples a subject entirely from the specific types of objects reacting to its changes, enabling extensible, event-driven designs without modifying the subject.

## Cons
- Strategy requires defining an interface and at least one concrete implementation even for a single, rarely-varying algorithm — overhead disproportionate to genuinely fixed, never-varying logic.
- Template Method still carries inheritance's coupling risk (a subclass depends on the base class's exact step-calling sequence and hook semantics) even though it's more constrained than open-ended inheritance.
- Observer's implicit, potentially-ordered notification chain can produce hard-to-trace cascading update bugs, and a subject with many observers can suffer subtle performance or ordering surprises that aren't visible just from reading the subject's own code.

## Alternatives
- **Plain conditional dispatch (if/elif on a type or flag)** instead of Strategy — simpler for a small, stable, rarely-changing set of algorithm variants where the flexibility Strategy offers isn't actually needed.
- **Higher-order functions / passing a function directly**, instead of a full Strategy class hierarchy — in languages with first-class functions, often a lighter-weight way to achieve the same swappable-behavior goal with less structural ceremony.
- **Event buses / message queues** instead of direct Observer subscription lists — for larger, more decoupled or distributed systems, an event bus (see `architecture/system-design`) generalizes Observer's idea across process/service boundaries, at the cost of additional infrastructure.

## When to use it
Use Strategy when an algorithm genuinely needs to vary at runtime or across instances. Use Template Method when a process's overall structure must be enforced consistently while still allowing well-defined customization points. Use Observer whenever multiple, potentially-changing sets of interested parties need to react to another object's state changes without that object needing to know who they are.

## When NOT to use it
Don't introduce Strategy for an algorithm that has never varied and shows no real sign of needing to — a direct implementation is simpler (echoing `clean-code/12`'s speculative-generality caution). Don't reach for Template Method if the variation actually needs runtime flexibility, not just per-subclass fixed customization — that's Strategy's job instead. Don't use Observer if there's really only ever one interested party with a stable, direct relationship to the subject — a plain, direct method call is simpler and easier to trace than a subscription mechanism with only one subscriber.

## Key takeaways / mental model
Ask: "does the behavior need to vary at runtime, per instance (Strategy), or is a fixed sequence with subclass-customizable steps enough (Template Method)?" And separately: "do I have multiple, decoupled, possibly-changing parties that need to react to a state change without the source needing to know who they are (Observer)?"

## Self-check questions
1. Rewrite the `DiscountStrategy` example as a Template Method instead, and explain what flexibility is lost in the conversion.
2. Using the `StockPrice` example, explain how a new observer type could be added without modifying `StockPrice`, and why that matters for the Open/Closed Principle.
3. Describe a cascading-update bug that could arise from Observer's notification mechanism, and how you'd prevent it.
4. Give an example from your own code where a simple conditional or direct function call would be preferable to introducing Strategy.

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 5: "Behavioral Patterns" (Strategy, Template Method, Observer sections).
