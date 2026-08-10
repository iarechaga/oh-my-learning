---
id: pragmatic-programmer/10
subject: pragmatic-programmer
title: "Decoupling: The Law of Demeter and Configuration"
slug: decoupling-demeter
status: drafted
mastery:
seniority: mid
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 5
prerequisites: [pragmatic-programmer/04]
created: 2026-08-10
updated: 2026-08-10
---

# Decoupling: The Law of Demeter and Configuration

## TL;DR
The Law of Demeter says talk only to your immediate collaborators, never reach through them to grab *their* collaborators ("don't talk to strangers") — chains like `a.getB().getC().getD()` couple you to the entire structure of B and C, not just to A. Pulling volatile decisions (endpoints, thresholds, feature flags) out into configuration is the same decoupling instinct applied to values instead of object structure.

## The idea
Chapter 4's orthogonality (Lesson 04) established that hidden coupling makes systems fragile. The Law of Demeter is a concrete, checkable rule for one specific and extremely common source of hidden coupling: **method-chaining through an object's internals to reach something several hops away.**

`order.getCustomer().getAddress().getCity()` looks harmless — it's just reading data. But it silently commits the calling code to *every* structural fact along that chain: that `Order` has a `Customer`, that `Customer` has an `Address`, that `Address` has a `city`. Change any link — customers move to a "billing profile" abstraction, addresses become polymorphic (some have no `city`, only a `region`) — and this call site breaks, even though it never cared about the intermediate structure, only the final city string.

Configuration decoupling applies the identical philosophy to *values* rather than object graphs: a hardcoded API endpoint or timeout threshold couples your code to today's operational reality; pulling it into config decouples "what the code does" from "what today's specific numbers/addresses happen to be."

## How it works

### The Law of Demeter, precisely
A method of object `A` should only call methods on:
1. `A` itself,
2. objects passed as parameters to that method,
3. objects `A` creates within that method,
4. `A`'s own direct component objects (fields).

It should **not** call methods on objects *returned by* those objects — that's "talking to a stranger," a friend-of-a-friend you have no direct relationship with and whose existence is really A's private business.

**Worked example — before:**
```
class OrderProcessor:
    def apply_discount(self, order):
        city = order.getCustomer().getAddress().getCity()
        if city in PROMO_CITIES:
            order.applyDiscount(0.1)
```
`OrderProcessor` now depends on `Order` having a `Customer`, `Customer` having an `Address`, and `Address` having a `city` — three structural facts it has no real business knowing, just to answer "is this order eligible for a city promo?"

**Worked example — after (Demeter-compliant):**
```
class Order:
    def isInPromoCity(self):
        return self.customer.getAddress().getCity() in PROMO_CITIES   # Order's own business

class OrderProcessor:
    def apply_discount(self, order):
        if order.isInPromoCity():
            order.applyDiscount(0.1)
```
`OrderProcessor` now asks `Order` a direct question and gets a direct answer — it no longer needs to know that `Customer` or `Address` exist at all. `Order` still needs the same structural knowledge to answer the question, but that knowledge is now localized to the one class that should own it (`Order`, which does directly own the customer relationship), instead of scattered to every caller that ever needed to check promo eligibility. If addresses are later restructured, only `Order.isInPromoCity()` needs to change — every caller stays untouched.

### Why "just reading data" is not automatically safe
A common objection: "it's just a getter chain, it's read-only, what's the risk?" The risk isn't mutation — it's **structural coupling**. Even read-only chains commit every call site to the *shape* of the object graph. The fix isn't "don't use getters," it's: ask the object that actually owns the relevant data to answer the *question* you actually have ("is this eligible for X"), rather than fetching raw structure and computing the answer yourself at the call site.

### Configuration as decoupling from operational reality
The chapter also treats hardcoded, environment-specific, or business-decision values as a coupling problem structurally identical to Demeter violations — just decoupling *values* instead of *object relationships*. A hardcoded `PROMO_CITIES = ["Madrid", "Lisbon"]` couples the code to a marketing decision that will change; a hardcoded `TIMEOUT_MS = 3000` couples it to an infrastructure assumption that differs between dev, staging, and production.

**Worked example.** Instead of:
```
if response_time > 3000:  # hardcoded, buried in logic
    retry()
```
externalize the volatile fact:
```
if response_time > config.get("http_retry_threshold_ms"):
    retry()
```
Now changing the threshold — because production latency characteristics differ from what was true when the code was written — is a config change, deployable independently of a code release, reviewable on its own, and different per environment without a code branch.

### The line between "genuine configuration" and "over-configuring"
Not everything volatile-looking deserves to become configurable. The book's caution: configuration adds indirection and a place where things can silently be wrong (a missing or malformed config value fails differently than a hardcoded one). Reserve it for values that genuinely vary by *deployment*, *environment*, or *business decision cadence* — not for values that are actually stable implementation details dressed up as "flexibility."

## Pros
- Localizes structural knowledge to the class that actually owns a relationship, so structural changes touch one place instead of every caller.
- Makes call sites express *intent* ("is this order eligible?") rather than *mechanism* (how eligibility happens to be computed today), which reads better and survives refactoring.
- Configuration decoupling enables environment-specific and business-decision changes without code deploys, and makes those changes reviewable and auditable on their own.

## Cons
- Strict Demeter compliance can produce a proliferation of thin wrapper/delegating methods ("method bloat") if applied mechanically to every getter chain regardless of whether real coupling risk exists.
- Over-configuring turns simple, stable constants into indirection that must be looked up, documented, and can be missing or malformed at runtime — a self-inflicted failure mode a hardcoded value never had.
- Excessive configuration surfaces (dozens of environment variables and flags) create their own maintenance and cognitive burden, and combinatorial testing problems.

## Alternatives
- **Tell, Don't Ask** — a closely related principle: instead of asking an object for its state and deciding externally, tell the object what you want done and let it decide internally. Demeter is largely a structural consequence of consistently applying Tell-Don't-Ask.
- **Facade / Repository patterns** — provide a single, intentional narrow interface over a complex object graph, achieving Demeter compliance at an architectural scale rather than method-by-method.
- **Feature flag services** (LaunchDarkly, Unleash, etc.) — a more sophisticated alternative to raw config files for values that need runtime toggling, gradual rollout, or per-user targeting, rather than static per-environment configuration.

## When to use it
Apply the Law of Demeter whenever you notice a call chain reaching more than one hop past an object's direct collaborators, especially in code you expect to change or that many callers depend on. Externalize a value into configuration whenever it represents a business decision, an environment-specific fact, or something you expect to need to change without a code deploy.

## When NOT to use it
Don't mechanically eliminate every two-hop getter chain if the intermediate structure is genuinely stable and unlikely to change (e.g., reaching into a well-established, rarely-changing value object) — the wrapper-method overhead may not be worth it. Don't configure values that are actually stable implementation constants; that's indirection without a corresponding decoupling benefit.

## Key takeaways / mental model
For object structure: "ask, don't reach" — ask your direct collaborator the real question you have, don't reach through it to compute the answer yourself. For values: "if this could plausibly need to be different in another environment or after a business decision, it belongs in config, not in the code."

## Self-check questions
1. Rewrite `report.getUser().getPreferences().getTimezone()` in a Demeter-compliant way, and explain what structural change it now protects against.
2. Why is "it's just a read-only getter chain" not a valid argument against a Demeter violation?
3. Give an example of over-configuring — a value that was pulled into config unnecessarily — and explain the cost that added.
4. How does the Law of Demeter relate to the orthogonality concept from Lesson 04? Are they the same idea or different ones?

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 5: "Bend, or Break" (Decoupling and Configuration sections).
- Karl J. Lieberherr, Ian M. Holland, "Assuring Good Style for Object-Oriented Programs" (origin of the Law of Demeter).
