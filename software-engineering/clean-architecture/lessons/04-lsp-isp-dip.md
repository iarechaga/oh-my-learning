---
id: clean-architecture/04
subject: clean-architecture
title: LSP, ISP, and DIP
slug: lsp-isp-dip
status: drafted
mastery:
seniority: senior
source: Clean Architecture (Robert C. Martin), Chapters 9-11
prerequisites: [clean-architecture/03, design-patterns/02]
created: 2026-08-10
updated: 2026-08-10
---

# LSP, ISP, and DIP

## TL;DR
The Liskov Substitution Principle says a subtype must be fully substitutable for its supertype without surprising callers — violating it (even subtly) poisons polymorphism and forces callers back into type-checking, undoing OCP's benefit. The Interface Segregation Principle says don't force a client to depend on interface members it doesn't use, because that creates unnecessary coupling to unrelated changes. The Dependency Inversion Principle — the most architecturally consequential of all five SOLID principles — says depend on abstractions, never on concrete, volatile implementation details, and structure the *source code dependency* to point opposite to the flow of control when a boundary needs to be inverted.

## The idea
These three principles complete the SOLID acronym, and DIP in particular is the specific, mechanical technique that makes this entire subject's dependency rule (`clean-architecture/08`) achievable — everything else in this lesson builds toward understanding exactly how and why dependencies can (and architecturally must) be inverted.

## How it works

### LSP — substitutability, precisely, with the consequence of violating it
Liskov Substitution, formally: if `S` is a subtype of `T`, objects of type `T` should be replaceable with objects of type `S` without altering any of the desirable properties of the program that uses `T`. The famous illustrative violation: a `Square` class inheriting from `Rectangle`, where setting a `Rectangle`'s width and height independently is a documented, expected capability — but a `Square` (which must keep both dimensions equal) can't honor that expectation without breaking the invariant "a square has equal sides," or silently changing both dimensions when only one was requested, surprising any caller that reasonably expected `Rectangle`'s documented behavior.

**Why this matters architecturally, not just as an OO nitpick.** An LSP violation forces every caller that might receive either the supertype or the subtype to add a type check (`if isinstance(shape, Square): ... else: ...`) to work around the surprising behavior — which is precisely `refactoring/04`'s repeated-conditional smell, and precisely what OCP (`clean-architecture/03`) was trying to prevent by using polymorphism in the first place. **A single LSP violation anywhere in a hierarchy silently poisons OCP's benefit for every caller of that hierarchy**, because callers can no longer trust the interface's contract and must defensively check concrete types instead.

### ISP — don't force unnecessary interface dependencies
When an interface bundles together methods serving several different clients' needs, a client depending on that interface is forced to depend on (and be potentially affected by changes to) methods it never actually calls — a specific, subtler form of the coupling problem `philosophy-of-software-design/04`'s leakage concept names, here located specifically in interface design.

**Worked example.**
```
# Before — a bloated interface forces every client to depend on everything
class Worker:
    def work(self): ...
    def eat(self): ...
    def sleep(self): ...

class HumanWorker(Worker):
    def work(self): ...
    def eat(self): ...
    def sleep(self): ...

class RobotWorker(Worker):
    def work(self): ...
    def eat(self): raise NotImplementedError   # forced to implement something meaningless
    def sleep(self): raise NotImplementedError

# After — segregated interfaces; RobotWorker depends only on what it needs
class Workable:
    def work(self): ...
class Eatable:
    def eat(self): ...
class Sleepable:
    def sleep(self): ...

class RobotWorker(Workable):    # only depends on Workable, no meaningless methods to implement
    def work(self): ...
```
A caller that only ever calls `work()` should depend only on `Workable` — if `Eatable`'s interface later changes (a new method added for human workers), code depending only on `Workable` is completely unaffected, whereas code depending on the original bloated `Worker` interface would have been forced to recompile/redeploy/re-verify against a change that has nothing to do with its actual needs.

### DIP — the architecturally decisive principle
The Dependency Inversion Principle states: high-level, policy-rich modules should not depend on low-level, detail-rich modules — both should depend on abstractions. This is "inversion" in a precise, specific sense worth understanding carefully: **the direction of the *source code dependency* (which module's code mentions which other module's name) is made to point opposite to the direction of the *flow of control*** (which module actually calls which, at runtime).

**Worked example.** Without DIP, a `PaymentService` (high-level policy: "process a payment, apply business rules") directly calls a concrete `StripeGateway` (low-level detail: a specific vendor's API) — the *source code* dependency and the *runtime control flow* point the same direction (policy depends on, and calls, the detail). With DIP applied:
```
class PaymentGateway:                          # abstraction, OWNED by the high-level policy layer
    def charge(self, amount): raise NotImplementedError

class PaymentService:                          # high-level policy
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
    def process_payment(self, order):
        self.gateway.charge(order.total)        # control flow still goes policy -> detail

class StripeGateway(PaymentGateway):            # low-level detail, now DEPENDS ON (implements) the policy's interface
    def charge(self, amount): ...
```
At runtime, control still flows `PaymentService -> StripeGateway.charge()`, exactly as before — but the *source code* dependency has inverted: `StripeGateway` now depends on (imports, implements) `PaymentGateway`, which is defined and owned by the high-level policy layer, not the other way around. `PaymentService` no longer mentions `StripeGateway` anywhere in its own source — it's completely decoupled from which specific vendor is used, and that decoupling is precisely what makes the vendor swappable, testable with a fake (`legacy-code/05`), and — critically for this subject's later lessons — is the exact mechanism that lets business policy stay "closed" (OCP) against changes to low-level details.

### Why the abstraction should be owned by the high-level side
A specific, easy-to-miss detail: the `PaymentGateway` interface in the example is conceptually *defined by and belongs to* `PaymentService`'s layer (the policy that needs a payment capability), not to the Stripe integration's layer — this ownership direction is what makes the dependency genuinely inverted. If the interface were instead defined in the low-level detail's package, and the high-level policy merely happened to use it, the *conceptual* ownership (and the packaging/component structure covered in `clean-architecture/05`-`06`) wouldn't actually reflect a true inversion, even if the code technically compiles the same way.

## Pros
- LSP violations are specifically diagnosable (does a caller need to type-check to use this subtype safely?) and directly protect OCP's polymorphism-based extensibility from being silently undermined.
- ISP reduces unnecessary coupling to interface members a client never uses, directly limiting the blast radius of changes to unrelated interface members.
- DIP is the concrete, mechanical technique that makes an entire system's business policy independent of frameworks, databases, and UI details — the foundation the rest of this subject's architecture builds on.

## Cons
- Detecting subtle LSP violations (versus more obvious ones like the `Square`/`Rectangle` example) requires careful attention to a supertype's full, sometimes-implicit behavioral contract, not just its method signatures.
- ISP, applied too granularly, can produce an excessive proliferation of tiny, single-method interfaces that add navigational overhead disproportionate to the actual coupling risk being managed.
- DIP's abstraction layer has a real cost (an interface to define, maintain, and understand) — applying it to every dependency regardless of genuine volatility (echoing `philosophy-of-software-design/05`'s "somewhat general, not speculative" guidance) produces unnecessary architectural ceremony.

## Alternatives
- **Composition over inheritance** (`design-patterns/02`) — a closely related principle that, applied consistently, prevents many LSP violations from arising in the first place, since composition doesn't force a false is-a relationship the way an ill-fitting inheritance hierarchy can.
- **Duck typing / structural typing** — in dynamically-typed or structurally-typed languages, ISP's segregation goal is sometimes achieved implicitly (a client only calls the methods it needs, with no formal interface declaration required at all) rather than through explicit interface definitions.
- **Service locator pattern** — a weaker, less explicit alternative to DIP's constructor-injected abstraction, achieving some decoupling from concrete types but hiding the dependency (echoing `pragmatic-programmer/10`'s and `clean-code/11`'s critique of hidden dependencies) rather than making it visible and inverted.

## When to use it
Apply LSP's substitutability test to any inheritance relationship before relying on polymorphism to satisfy OCP. Apply ISP when a client depends on an interface but uses only a fraction of its methods, especially if the unused portion is volatile. Apply DIP specifically at architectural boundaries between business policy and volatile technical details (databases, frameworks, external services, UI).

## When NOT to use it
Don't force LSP compliance onto a relationship that isn't genuinely is-a in the first place — that's a signal to use composition (`design-patterns/02`) instead of inheritance, not to contort the inheritance to technically satisfy LSP. Don't apply ISP so granularly that every interface has exactly one method regardless of whether clients' actual usage patterns justify the split. Don't apply DIP to a dependency that's genuinely stable and unlikely to ever need swapping — the abstraction layer's cost isn't justified there.

## Key takeaways / mental model
LSP: "can every caller treat this subtype exactly like its supertype, with zero surprises?" ISP: "does this client actually use everything this interface forces it to depend on?" DIP: "does my high-level policy's source code mention any low-level, volatile detail by name — and if so, can I invert that by having the detail implement an interface my policy owns instead?"

## Self-check questions
1. Using the `Square`/`Rectangle` example, explain precisely how an LSP violation forces callers back into type-checking, undoing OCP's benefit.
2. Rewrite the bloated `Worker` interface example using ISP, and explain what change to `Eatable` no longer affects `RobotWorker`.
3. Walk through the `PaymentService`/`StripeGateway` example, and explain precisely what "inverted" means here — which direction does the source-code dependency point, versus the runtime control flow?
4. Why does it matter, architecturally, which side (high-level or low-level) conceptually owns the abstraction interface in a DIP-satisfying design?

## References
- Clean Architecture: A Craftsman's Guide to Software Structure and Design (Robert C. Martin), Chapter 9: "LSP: The Liskov Substitution Principle," Chapter 10: "ISP: The Interface Segregation Principle," Chapter 11: "DIP: The Dependency Inversion Principle".
