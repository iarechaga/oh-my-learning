---
id: unit-testing/08
subject: unit-testing
title: Mocking Guidelines and Interaction Testing Limits
slug: mocking-guidelines
status: drafted
mastery:
seniority: senior
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 8
prerequisites: [unit-testing/04, unit-testing/07]
created: 2026-08-10
updated: 2026-08-10
---

# Mocking Guidelines and Interaction Testing Limits

## TL;DR
Mock only true external dependencies whose interaction is part of the observable contract with the outside world (an email being sent, a payment being charged) — never mock internal collaborators that exist purely as implementation choices within your own system's boundary. When you do mock a true external dependency, verify it at most once per test and only at the point where the interaction *is* the behavior, not as a secondary check bolted onto an output assertion.

## The idea
`unit-testing/04` established that asserting on internal method calls breaks tests during safe refactors. `unit-testing/07` gave you the vocabulary (mock vs. stub vs. fake) to express the distinction precisely. This lesson answers the practical question those two leave open: **given that some mocking is legitimate, exactly where is the line, and how do you mock well once you've decided a mock is warranted?**

Khorikov's answer hinges on a single distinction: **internal communication vs. cross-application/system communication.** Internal communication is calls between objects inside your own application's boundary that could, in principle, be refactored (inlined, restructured, replaced) without any outside observer noticing. Cross-application communication is a call that crosses your system's boundary to another system — a real email provider, a payment gateway, a message queue, another microservice — where an outside party (a customer, another team's service) genuinely observes whether that call happened. Only the second category is a legitimate target for interaction-based (mock) verification.

## How it works

### The boundary test: "would an outside observer notice?"
Take an `OrderService` that, when an order is placed, (a) recalculates the total via an internal `PricingCalculator`, and (b) sends a receipt via an external `EmailGateway`.

- `PricingCalculator` — purely internal. If you refactor how pricing is calculated (a different algorithm, a different internal class structure), no one outside the system notices or cares, as long as the *resulting total* is still correct. **Do not mock this and verify it was called** — assert on the resulting total instead (as in `unit-testing/04`).
- `EmailGateway` — crosses the system boundary to a real email provider. Whether or not this call happens is something a real customer experiences directly (they get an email or they don't). **This is a legitimate mock target.**

```
test "placing an order sends a receipt email to the customer":
    emailGatewayMock = mock(EmailGateway)
    stubPricing = new StubPricingCalculator(returns: 180)
    service = new OrderService(pricing: stubPricing, email: emailGatewayMock)
    service.placeOrder(customerEmail: "a@b.com", subtotal: 200)
    verify(emailGatewayMock.send(to: "a@b.com", subject: contains("Receipt"))).wasCalledOnce()
```
Notice `PricingCalculator` here is a *stub* (feeding data in), not a mock (verified for interaction) — consistent with `unit-testing/07`'s "least powerful double" guidance. Only `EmailGateway`, the true cross-boundary dependency, gets the mock treatment.

### Guideline: verify the interaction only where the interaction IS the behavior
Even for a legitimate external-dependency mock, resist the temptation to verify every incidental detail of the call. Compare:
```
# Over-specified — brittle even for a legitimate mock target
verify(emailGatewayMock.send(
    to: "a@b.com",
    subject: "Your Receipt",
    body: "Thank you for your order of $180.00, placed on 2026-08-10 at 14:32:07...",
    headers: {"X-Retry-Count": "0"}
)).wasCalledOnce()

# Right-sized — verifies what actually matters to the requirement
verify(emailGatewayMock.send(to: "a@b.com", subject: contains("Receipt"))).wasCalledOnce()
```
The first version couples the test to incidental formatting details (exact timestamp string, an internal retry header) that have nothing to do with the requirement "a receipt gets sent" — any change to email copy or an unrelated header now breaks this test. The second version verifies exactly the contractually meaningful part: a receipt-like email goes to the right address. This is the interaction-testing analogue of `unit-testing/04`'s output-testing discipline: assert on what the requirement actually promises, nothing more.

### Guideline: one mocked interaction per test, and don't mix too many mocks
A test verifying five different mocked interactions in one go is hard to read and hard to diagnose on failure (which of the five broke, and why?). Prefer one test per distinct external effect being verified. Similarly, a test that needs to mock four or five different collaborators to even run is often a design smell — Khorikov calls this out directly: **it's frequently a signal that the class under test has too many responsibilities** (a violation of single responsibility) rather than a signal that you need a more powerful mocking framework. The fix is usually to split the class, not to write a more elaborate test.

### Worked example: refactoring away from over-mocking
Before (five mocked collaborators, brittle, hard to read):
```
test "processing a subscription renewal":
    billingMock = mock(BillingGateway)
    emailMock = mock(EmailGateway)
    inventoryMock = mock(InventoryService)     # unrelated to subscriptions!
    auditLogMock = mock(AuditLogger)
    metricsMock = mock(MetricsClient)
    service = new SubscriptionService(billingMock, emailMock, inventoryMock, auditLogMock, metricsMock)
    service.renew(subscriptionId: 42)
    verify(billingMock.charge(42, 9.99)).wasCalledOnce()
    verify(emailMock.send(...)).wasCalledOnce()
    verify(auditLogMock.record(...)).wasCalledOnce()
    verify(metricsMock.increment("renewals")).wasCalledOnce()
```
The presence of `inventoryMock` (unrelated to billing) and the sheer count of verified interactions both signal `SubscriptionService` is doing too much. A cleaner design separates the true external-effect concerns (billing, email — worth their own focused tests) from cross-cutting concerns like audit logging and metrics (often better handled via a decorator, middleware, or event-driven side effect that doesn't need to be verified inline with the core business flow at all). After that split, each remaining test verifies at most one or two mocked interactions, each clearly tied to one requirement.

## Pros
- Confines interaction testing to the one place it's actually load-bearing (true external effects), which keeps most of the suite resistant to refactoring per `unit-testing/04`.
- Right-sized verification (only the contractually meaningful parts of a call) reduces false failures from unrelated formatting/detail changes.
- The "too many mocks needed" smell doubles as a free design-quality signal, nudging toward better-factored classes.

## Cons
- Requires judgment to classify a given collaborator as "internal" vs. "true external dependency" — the line is not always obvious, especially with internal services that feel external (e.g., another team's microservice reached via an in-process call in a monolith).
- Even well-scoped mocks of external dependencies don't verify that the *real* dependency behaves as assumed — the risk that a fake or mock's assumed contract drifts from reality (raised in `unit-testing/07`) still applies.
- Teams accustomed to mocking everything by default find this discipline to be a genuine behavior change, not just a small tweak.

## Alternatives
- **Mock everything, verify every interaction (classic London-school maximalism)** — treated in depth in `unit-testing/09`; internally consistent as a philosophy but requires much stricter discipline than this lesson recommends to avoid brittleness, and Khorikov argues it more often produces the over-mocking failure mode than avoids it.
- **Verify external effects via integration tests instead of mocks** — replace the mocked `EmailGateway` verification with an actual integration test against a sandboxed email provider (`unit-testing/10`); more realistic, much slower, appropriate in smaller numbers as a complement, not a replacement, for the unit-level mock test.
- **Outbox/event pattern** — instead of the service directly calling `EmailGateway`, it records an "OrderPlaced" event/outbox row; a separate process later delivers the email. This removes the need to mock the email call at all in the core `placeOrder` test, pushing the external-effect verification to a separate, smaller component (echoes the Humble Object split in `unit-testing/05`).

## When to use it
Reach for a mock exactly when: (1) the collaborator is a genuine external dependency crossing your system's boundary, and (2) whether that call happens is itself part of the requirement you're testing. Keep the verified details limited to what the requirement actually specifies.

## When NOT to use it
Don't mock internal collaborators just because "mocking makes the test faster/more isolated" — use a stub or fake for internal collaborators that supply data, and prefer real objects wherever they're fast and deterministic (per `unit-testing/06`). If a test needs many mocks to run at all, treat that as a design smell to fix, not a testing problem to work around with a bigger mock setup.

## Key takeaways / mental model
Before mocking anything, ask: "does this call cross my system's boundary to somewhere an outside observer would notice?" If yes, mock it — narrowly, verifying only the contractually meaningful details. If no, it's internal implementation — use a stub, a fake, or a real object, and never verify the call itself.

## Self-check questions
1. A `NotificationService` calls both an internal `TemplateRenderer` (formats the message text) and an external `SmsGateway` (actually sends the SMS). Which one is a legitimate mock target, and what specifically would you verify on it?
2. A test needs to construct mocks for six different collaborators before it can even run. What does this lesson say that fact is telling you, and what would you investigate first?
3. Explain why verifying the exact email body text (down to the timestamp) in a receipt-sending test is worse than verifying just the recipient and a `contains("Receipt")` subject match, even though both are technically "verifying the mocked interaction."

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 8: "Why Do We Need Mocks?"
