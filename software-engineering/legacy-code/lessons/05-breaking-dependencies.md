---
id: legacy-code/05
subject: legacy-code
title: Breaking Dependencies (the Toolkit)
slug: breaking-dependencies
status: drafted
mastery:
seniority: senior
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapters 9, 25
prerequisites: [legacy-code/02, legacy-code/04]
created: 2026-08-10
updated: 2026-08-10
---

# Breaking Dependencies (the Toolkit)

## TL;DR
When no usable seam exists, you need to deliberately create one — the core toolkit for doing this safely: Extract Interface/Extract Implementer (formalize what a dependency needs to look like), Parameterize Constructor (accept a dependency instead of building it internally), and Subclass and Override (a lightweight, temporary technique for isolating one specific problematic method without a larger redesign).

## The idea
`legacy-code/02` established that seams enable substitution, and `legacy-code/04` established the two problems (sensing, separation) substitution typically solves. This lesson is the concrete "how" for the common case where **no usable seam currently exists** — you need to deliberately, carefully modify the code to create one, while still preserving its exact current behavior (this is itself a refactoring, in `refactoring/01`'s precise sense, even though it's happening specifically to enable testing rather than to improve structure for its own sake).

## How it works

### Parameterize Constructor — the most common, most direct fix
When a class constructs its own dependency internally (the exact anti-pattern `clean-code/11` and `design-patterns/05` both name), change the constructor to accept that dependency as a parameter instead, with production code passing the real implementation and tests passing a fake.

**Worked example.**
```
# Before — no seam; PaymentGateway is hardcoded
class OrderProcessor:
    def __init__(self):
        self.gateway = StripeGateway()

# After — Parameterize Constructor creates an object seam
class OrderProcessor:
    def __init__(self, gateway=None):
        self.gateway = gateway or StripeGateway()   # default preserves existing production behavior
```
Using a default value (`gateway or StripeGateway()`) is a common, low-risk technique specifically for legacy code: every *existing* caller that doesn't pass a gateway continues to get exactly the same behavior as before (`StripeGateway()`), so this change alone is behavior-preserving and safe to make immediately, verified by whatever tests already exist — and it simultaneously creates a genuine seam for any *new* test that does want to pass a fake gateway.

### Extract Interface / Extract Implementer — formalize the dependency's contract
When a dependency has a large, concrete class with many methods, but the class using it only actually needs a handful of them, extracting a narrower interface (containing just the needed methods) makes it much easier to build a minimal, focused fake implementing only what's genuinely required — rather than needing a fake that replicates the entire real class's full surface area.

**Worked example.**
```
# Extract just what OrderProcessor actually needs from the payment gateway
class PaymentGateway:              # extracted interface
    def charge(self, amount): raise NotImplementedError

class StripeGateway(PaymentGateway):   # real implementation, now conforms to the interface
    def charge(self, amount): ...      # (plus many other methods the real Stripe SDK has, not exposed here)

class FakeGateway(PaymentGateway):     # test double, trivially simple
    def __init__(self): self.charged_amounts = []
    def charge(self, amount): self.charged_amounts.append(amount)
```
This directly connects to `design-patterns/01`'s "program to an interface" principle and `clean-code/08`'s boundary-wrapping — here applied specifically as a *retrofit* technique for existing legacy code, narrowing a broad, concrete dependency down to exactly what's needed, making a faithful test double dramatically easier to build and maintain.

### Subclass and Override — a lightweight, often temporary technique
When a full interface extraction or constructor parameterization feels like more change than you want to risk right now, a lighter-weight, more surgical option: create a test-specific subclass that overrides just the one problematic method (the one making a real network call, the one reading real system time), leaving everything else about the class exactly as it is.

**Worked example.**
```
class ReportGenerator:
    def generate(self):
        timestamp = datetime.now()       # hard dependency on real system time — untestable, non-repeatable
        return f"Report generated at {timestamp}"

class TestableReportGenerator(ReportGenerator):
    def __init__(self, fixed_time):
        self.fixed_time = fixed_time
    def generate(self):
        return f"Report generated at {self.fixed_time}"   # overrides the whole method to avoid the hard dependency
```
This is deliberately a smaller, more contained intervention than fully parameterizing the constructor or extracting an interface — appropriate specifically when you need a *quick*, low-risk way to get one test in place, with the option to do a more thorough dependency-breaking refactor later once you understand the code better or have more time. Feathers is explicit that this technique, while sometimes described as a "smell" if left permanently in place, is a legitimate, pragmatic *temporary* tool for making initial progress against otherwise-intimidating legacy code.

### The underlying discipline: each dependency-breaking change is itself verified
Every technique in this lesson is, itself, a small code change to *production* code (not just test code) — which means it needs the same behavior-preservation verification discipline as any other refactoring (`refactoring/01`, `refactoring/03`). The specific techniques here (parameterizing with a safe default, extracting an interface the existing concrete class already satisfies) are chosen specifically because they're low-risk, easily-verified changes — but "low-risk" doesn't mean "unverified"; run whatever tests already exist immediately after each dependency-breaking change, before using the newly-created seam to add further, more targeted characterization tests (`legacy-code/03`).

## Pros
- Parameterize Constructor with a safe default is one of the lowest-risk, most broadly applicable techniques for creating a seam without disturbing any existing caller's behavior.
- Extract Interface produces a minimal, focused contract that makes building faithful, maintainable test doubles far easier than mimicking an entire large concrete class.
- Subclass and Override provides a fast, contained way to make initial progress on intimidating legacy code, without committing to a larger redesign before you're ready.

## Cons
- Parameterize Constructor with a default value, while safe, can leave a slightly awkward "optional dependency with a magic default" signature permanently in place if never cleaned up once tests are established.
- Extract Interface requires correctly identifying exactly what the dependent class actually needs — extracting an interface that's still too broad (mirroring the whole concrete class out of caution) undermines the "easy to fake" benefit.
- Subclass and Override, left in place long-term rather than as a genuinely temporary bridge, can accumulate as a permanent, awkward layer of "testing subclasses" that itself becomes confusing legacy structure — Feathers' own caution about not treating it as a final destination.

## Alternatives
- **A full, upfront redesign to dependency injection** (echoing `clean-code/11`) — cleaner and more permanent, but riskier and more time-consuming to do immediately in unfamiliar legacy code; often better attempted incrementally, once initial characterization tests (enabled by these lighter techniques) have built confidence and understanding.
- **Monkey-patching / test-framework-level substitution** — avoids modifying production code at all, at the cost of more fragile, implementation-coupled tests, and a real risk of the patch silently failing to apply if the code's internal structure changes.
- **Doing nothing and testing only at a much coarser, end-to-end level** — sidesteps needing any of these techniques, at the cost of slow, less-precise tests that don't isolate which specific unit of code is responsible for a failure.

## When to use it
Use Parameterize Constructor as your default first choice whenever a class constructs a hard-to-test dependency internally. Use Extract Interface when the dependency's full concrete surface is large relative to what's actually needed. Use Subclass and Override as a fast, temporary bridge to unblock testing progress on a specific method, with intent to revisit more thoroughly later if the class remains important.

## When NOT to use it
Don't leave a Subclass-and-Override test harness in place indefinitely without revisiting whether a more thorough, permanent fix (Parameterize Constructor, Extract Interface) is now warranted, once you have more context and confidence. Don't extract an interface mirroring an entire large concrete class "just in case" — extract only what's genuinely needed by the specific dependent code you're working on right now.

## Key takeaways / mental model
When no seam exists, ask which of these three techniques is the least invasive fix that unblocks the specific test you need right now — usually Parameterize Constructor with a safe default. Escalate to Extract Interface or a fuller redesign only once you have evidence (repeated need, growing confidence in the code) that the lighter fix isn't sufficient.

## Self-check questions
1. Walk through applying Parameterize Constructor with a safe default to a hardcoded dependency in your own code, and explain why the default preserves existing behavior.
2. Why does Extract Interface make building test doubles easier specifically when the real dependency's concrete class is large? What happens if you extract an interface that's still too broad?
3. Describe a situation where Subclass and Override would be the right first move, and explain what a more permanent fix might look like later.
4. Why must every dependency-breaking change, even a small one, be verified against existing tests immediately, per the same discipline as any other refactoring?

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 9: "I Can't Get This Class into a Test Harness" and Chapter 25: "Dependency-Breaking Techniques".
