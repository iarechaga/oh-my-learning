---
id: legacy-code/04
subject: legacy-code
title: Sensing and Separation
slug: sensing-and-separation
status: drafted
mastery:
seniority: senior
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 5
prerequisites: [legacy-code/02]
created: 2026-08-10
updated: 2026-08-10
---

# Sensing and Separation

## TL;DR
Two distinct reasons drive most dependency-breaking in legacy code: "sensing" (you need to observe a value the code computes internally but doesn't expose, to make an assertion about it) and "separation" (you need to isolate the code under test from a dependency that's slow, unreliable, or has real side effects you don't want during a test run). Naming which problem you actually have determines which specific technique is the right fix.

## The idea
`legacy-code/02` established that seams let you substitute a dependency for testing purposes — but *why* you need to substitute something varies, and the two most common reasons call for different specific approaches. **Sensing**: the code computes or produces something internally that you need to verify, but there's no way to observe it from outside — no return value, no accessible field, the information is essentially trapped inside the method's execution. **Separation**: the code depends on something (a database, a network call, a hardware clock, a file system) that makes testing slow, unreliable, non-repeatable (violating `clean-code/09`'s F.I.R.S.T. properties), or that has real side effects you specifically don't want triggered during a test run.

## How it works

### Sensing — making the invisible visible
When a method's important effect is buried inside its execution with no way to check it from outside, you need a **sensing variable** or a way to intercept the value — often by introducing a subclass or a test-specific variant that captures the value at the point it's computed, exposing it for the test to inspect afterward.

**Worked example.**
```
class OrderProcessor:
    def process(self, order):
        total = calculate_total(order)
        self._send_confirmation(order, total)   # total is computed and used, but never exposed

    def _send_confirmation(self, order, total):
        email_service.send(order.customer, f"Total: {total}")
```
A test wanting to verify `total` was calculated correctly has no direct way to observe it — it's a purely local, internal value. A sensing approach: extract `_send_confirmation`'s call into an overridable seam, and in a test-specific subclass, override it to capture `total` into an accessible attribute instead of actually sending an email:
```
class TestableOrderProcessor(OrderProcessor):
    def __init__(self):
        self.sensed_total = None
    def _send_confirmation(self, order, total):
        self.sensed_total = total   # capture, don't actually send

processor = TestableOrderProcessor()
processor.process(order)
assert processor.sensed_total == 150.0   # now observable
```
This is a targeted, minimal, test-specific technique — the subclass exists purely to make an otherwise-invisible internal value visible for a specific test's assertion, without altering the original class's production behavior at all.

### Separation — isolating from a costly or unreliable dependency
When the problem isn't "I can't see a value," but "this code touches something I don't want touched during a test" (a real database write, a real email send, a real payment charge), the fix is a genuine object seam (`legacy-code/02`) substituting a fake, in-memory, or no-op implementation for the real dependency, specifically for the duration of the test.

**Worked example.** The same `OrderProcessor`, but now concerned about actually sending real emails during every test run:
```
class OrderProcessor:
    def __init__(self, email_service):        # object seam introduced via dependency-breaking (legacy-code/05)
        self.email_service = email_service
    def process(self, order):
        total = calculate_total(order)
        self.email_service.send(order.customer, f"Total: {total}")

# test — separation from the real email service:
fake_email_service = FakeEmailService()   # records calls, sends nothing real
processor = OrderProcessor(email_service=fake_email_service)
processor.process(order)
assert fake_email_service.sent_messages[0].total == 150.0   # separation AND sensing, combined
```
Notice this example actually solves *both* problems at once — the fake email service provides separation (no real email is sent) and, as a bonus, provides sensing too (it records what was sent, making that value observable for assertions) — a common, efficient pattern where a well-designed test double serves both purposes simultaneously.

### Distinguishing which problem you actually have — because the fix differs
A practical diagnostic: ask "is the issue that I can't *see* something the code does internally, or that I don't want the code to *actually do* something (with real side effects or real cost) during a test?" Sensing problems are often fixable with a targeted subclass or capture point, sometimes without touching the production dependency structure at all. Separation problems generally require a genuine object seam substituting the real dependency for a fake one, and often require the more involved dependency-breaking techniques from `legacy-code/05` if no such seam currently exists. Misdiagnosing which problem you have can lead to over-engineering a full dependency-injection refactor when a simple sensing subclass would have sufficed, or under-engineering a fragile sensing hack when what you actually needed was genuine separation from a costly dependency.

## Pros
- Naming sensing and separation as distinct problems clarifies which specific technique is proportionate to the actual need, avoiding both over- and under-engineering the fix.
- Sensing techniques can sometimes provide a minimal, test-only path to observability without any change to production code's structure at all.
- Separation techniques, once in place, provide the broader benefit of fast, reliable, repeatable tests (`clean-code/09`'s F.I.R.S.T. properties) beyond just solving the immediate observability problem.

## Cons
- Sensing via test-specific subclassing can become fragile if the class's internal structure changes in ways the subclass depended on — a lighter-weight but more implementation-coupled technique than a genuine seam.
- Separation generally requires more invasive changes (introducing an object seam where none exists) than sensing alone, and carries the corresponding higher cost and risk `legacy-code/05`'s dependency-breaking techniques address.
- Conflating the two problems (assuming a sensing fix will also solve a separation problem, or vice versa) can leave one need unmet — e.g., a sensing subclass that still lets the real, slow database call happen underneath it, providing observability but not actually eliminating the reliability/speed cost.

## Alternatives
- **Full dependency injection redesign upfront** — resolves both sensing and separation cleanly and permanently, at a higher upfront cost than the more targeted, minimal techniques this lesson describes for a single, specific test need — appropriate once a class is being substantially reworked anyway (see `legacy-code/11`'s fuller technique catalog).
- **Real integration tests against the actual dependency** — sidesteps needing sensing or separation techniques at all, at the cost of slower, less reliable tests, appropriate specifically for a smaller set of genuine integration-level tests complementing (not replacing) fast, isolated unit tests.
- **Test doubles/mocking frameworks** — provide both sensing (recording calls and arguments) and separation (avoiding real side effects) generically, once a genuine object seam exists for them to substitute into — the common, tooling-supported version of the manual techniques shown here.

## When to use it
Use sensing techniques when the specific problem is "I can't observe a value the code computes internally." Use separation techniques when the specific problem is "I don't want this code's real side effects (cost, unreliability, slowness) happening during a test." Diagnose which one you actually have before choosing a fix.

## When NOT to use it
Don't reach for a full separation-oriented dependency-injection redesign when a much simpler, targeted sensing subclass would answer your specific, immediate testing question. Don't rely on a fragile sensing hack when the dependency's real side effects (cost, unreliability) genuinely need to be eliminated from the test run, not just made observable.

## Key takeaways / mental model
Before reaching for any specific technique, ask: "do I need to see something the code hides, or do I need to stop something the code does?" The answer to that question — sensing or separation — determines which of this lesson's approaches (or `legacy-code/05`'s fuller toolkit) is actually proportionate to your need.

## Self-check questions
1. Using the `OrderProcessor` example, explain the difference between a pure sensing fix and a pure separation fix, and describe the combined fix that provides both.
2. Give an example from your own testing experience where you needed sensing but not separation, or vice versa.
3. Why can a fake/test double sometimes solve both sensing and separation problems simultaneously? What property of a good test double makes that possible?
4. Describe a situation where misdiagnosing sensing versus separation led to (or would lead to) an over-engineered or under-engineered fix.

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 5: "Tools".
