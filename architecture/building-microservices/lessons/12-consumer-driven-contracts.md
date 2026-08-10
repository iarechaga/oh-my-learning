---
id: building-microservices/12
subject: building-microservices
title: "Consumer-Driven Contracts"
slug: consumer-driven-contracts
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 10"
prerequisites: [building-microservices/11]
created: 2026-08-10
updated: 2026-08-10
---

# Consumer-Driven Contracts

## TL;DR
In consumer-driven contract (CDC) testing, each **consumer** of a service writes down the exact expectations it has of that service's API (the specific fields and behaviors it actually uses), and the **provider**'s CI pipeline runs those expectations against its real implementation on every change. This catches breaking changes to an integration point automatically, in the provider's own pipeline, without needing a full end-to-end test suite or the consumer's service running at all.

## The idea
Lesson 11 introduced contract testing as the layer that gives most of end-to-end testing's integration confidence without its combinatorial cost. This lesson goes deep on the specific, most widely used mechanism for that: **consumer-driven contracts**, popularized by tools like Pact.

The core insight is a reversal of the usual direction of API testing responsibility. Normally, a service provider tests its own API against what it *believes* consumers need, and hopes it's right. Consumer-driven contracts flip this: **the consumer writes the contract.** Each team that consumes `inventory-service`'s API writes down, in an executable, machine-checkable form, exactly what it expects — which fields it reads, which status codes it handles, which behaviors it relies on. `inventory-service`'s own CI pipeline then runs every consumer's contract against its real implementation before every release, and fails the build if any contract would break.

This solves a real, recurring problem: a provider team, working in good faith, ships a change that looks harmless from their side — renaming a field they think is unused, tightening validation, changing a default — and it silently breaks a consumer they didn't know about or didn't think to check with. Consumer-driven contracts make that check automatic and continuous, instead of relying on the provider team remembering to ask around, or discovering the breakage only when the consumer's service errors in production.

## How it works

### The contract-testing flow (Pact-style)

1. **Consumer writes a contract.** `order-service` (the consumer) writes a test describing its expectations of `inventory-service` (the provider) — e.g., "when I call `POST /inventory/reserve` with `{sku, quantity}`, I expect a `200` response containing a `reservationId` field and a `status` field that is one of `RESERVED`/`UNAVAILABLE`." This is expressed as a **pact** — a machine-readable contract file (typically JSON) generated automatically by running `order-service`'s own consumer-side tests against a mock provider that's configured to honor exactly this expectation.
2. **The pact is published** to a shared broker (a Pact Broker, or an equivalent artifact store) that both teams' pipelines can read from — this is the coordination point that lets consumer and provider teams work independently without needing to synchronize manually.
3. **`order-service`'s own pipeline** runs its tests against the mock provider honoring the pact — fast, no real `inventory-service` needed, part of `order-service`'s own independent build (Lesson 09).
4. **`inventory-service`'s pipeline (the provider side) fetches every published pact** that names it as the provider — from `order-service`, and from any other consumer that has ever published a contract against it — and replays each one against `inventory-service`'s *real*, running implementation (typically spun up locally within the CI job, not the full `order-service`). If `inventory-service`'s actual behavior doesn't satisfy a consumer's contract, the build fails, right there in `inventory-service`'s own pipeline, before the change ever ships.

The critical property: this verification happens entirely within each service's own independent pipeline (Lesson 09) — `inventory-service`'s pipeline never needs `order-service` (or any other consumer) actually running, and vice versa. You get integration confidence without paying the cost or flakiness of spinning up multiple real services together (Lesson 11's core critique of heavy E2E suites).

### Worked example: a broken contract caught in CI

`inventory-service`'s API currently returns:
```json
{ "reservationId": "r-4471", "status": "RESERVED", "expiresAt": "2026-08-10T14:00:00Z" }
```

`order-service`'s published contract says: "the response must contain `reservationId` (string) and `status` (one of `RESERVED`/`UNAVAILABLE`)." Note `order-service` never asserts anything about `expiresAt` — it doesn't use that field, so it's correctly left out of the contract; this is deliberate and important (see below).

A developer on the `inventory-service` team, cleaning up the API, renames `reservationId` to `reservation_id` for naming consistency with a newer internal convention, and ships the change.

`inventory-service`'s CI pipeline, as part of its normal build, fetches `order-service`'s published pact and replays it: `POST /inventory/reserve` against the real, newly-changed implementation. The response no longer contains a `reservationId` field. The contract verification step fails immediately, with a clear message identifying exactly which consumer's expectation broke and why — *before* the change is merged or deployed, entirely within `inventory-service`'s own pipeline, with no `order-service` instance ever spun up. The developer either reverts the rename, or coordinates the rename with the `order-service` team and has them update their contract to expect the new field name, then re-verifies before shipping.

Compare this to the world without contract testing: the rename ships, passes `inventory-service`'s own unit tests (which know nothing about `order-service`'s expectations), and the break is discovered only when `order-service` starts throwing errors in production — a much slower, much more expensive, and much more customer-visible way to find the same bug.

### Why the consumer defines the contract, not the provider

A tempting alternative is provider-driven contracts — the provider documents its full API surface (e.g., via an OpenAPI spec) and everyone tests against that. The trouble: a provider's *full* API surface is usually much larger than what any single consumer actually depends on, and if the contract is "the whole API must never change in any way," it becomes overly rigid — the provider can't evolve its unused fields or add new optional behavior without triggering false-positive test failures for changes that don't actually affect anyone.

Consumer-driven contracts avoid this by having each consumer specify only the subset of behavior it actually relies on. This gives the provider real freedom to change anything a consumer doesn't care about (add new fields, remove fields no consumer asserts on, change internal behavior not covered by any contract) while still getting a hard, automatic guarantee that it can't silently break anything a consumer *does* rely on. This is Lesson 03's information-hiding principle applied to API evolution: the contract is exactly and only "what consumers actually need," nothing more.

### Handling multiple consumers, and provider evolution

A provider with several consumers (e.g., `inventory-service` consumed by `order-service`, `reporting-service`, and a mobile `bff-service`) accumulates one contract per consumer, and its pipeline verifies against all of them on every change. This gives the provider team a precise, always-up-to-date picture of "here is the exact set of things I must not break," aggregated automatically from real, currently-active consumers — rather than a stale wiki page or a guess based on who happens to be in the room.

When a provider genuinely needs to make a breaking change (not just an internal cleanup, but a real, intentional API change), consumer-driven contracts surface exactly which consumers need to be coordinated with — the failing contract verification identifies them by name — turning "who might this break?" from an open question requiring manual investigation into a concrete, actionable list generated by CI itself.

## Pros
- **Catches breaking changes automatically, in CI, before they reach production** — no reliance on the provider team remembering every consumer or manually reaching out.
- **Runs within each service's own independent pipeline** (Lesson 09) — no need to stand up multiple real services together, avoiding E2E's cost and flakiness (Lesson 11).
- **Gives the provider precise freedom** to change anything not covered by an active contract, rather than treating the entire API surface as frozen.
- **Makes "who depends on this?" a concrete, CI-generated answer** rather than institutional knowledge that erodes as teams and people change.

## Cons
- **Requires both sides to participate and maintain discipline** — a consumer that never writes or updates its contract gets none of this protection, and a stale, abandoned contract can give false confidence (or false failures) over time.
- **Adds real infrastructure** — a contract broker (or equivalent shared artifact store) both teams' pipelines must reach, plus tooling/library adoption (e.g., Pact) in every service.
- **Doesn't replace all E2E testing** — contract tests verify the shape and stated behavior of an integration point, not genuinely emergent multi-service behavior (e.g., a saga's overall correctness across several hops, Lesson 08) — a small, focused E2E suite (Lesson 11) is still valuable for that.
- **Async/event-based contracts are less mature tooling-wise** than the synchronous request-response case, though the same consumer-driven idea applies (a consumer specifies the event shape/fields it relies on, verified against the publisher's actual output).

## Alternatives
- **Provider-driven API specs (e.g., strict OpenAPI conformance testing)** — simpler to set up (one spec, not N per-consumer contracts), but tends toward over-rigid "nothing may ever change" contracts or under-protective "spec exists but nobody enforces it against real consumer usage" gaps; doesn't give the precision of "exactly what active consumers actually use."
- **Manual cross-team communication / API change review process** — works at small scale with few consumers and a stable team, but doesn't scale as the number of consumers and the org grows, and has no automatic enforcement — a missed conversation ships a break.
- **A full shared E2E suite as the primary integration safety net** — the alternative Lesson 11 argues against as the primary strategy, for cost and flakiness reasons; contract tests are the more scalable substitute for most integration-correctness concerns.

## When to use it
- Any synchronous (or event-based) integration point between two independently-deployed services, especially ones owned by different teams where informal communication doesn't reliably scale.
- When a provider service has multiple consumers and needs a reliable, automatic way to know what it's safe to change.

## When NOT to use it
- A single-team system where the same people own both the provider and every consumer, and coordination is trivial and immediate — the overhead of formal CDC tooling may not pay for itself yet, though it's worth adopting proactively before the team/consumer count grows.
- As a substitute for all E2E testing — CDC verifies individual integration points, not whole-system emergent behavior (e.g., a full saga's correctness); keep a small, targeted E2E suite alongside it (Lesson 11).

## Key takeaways / mental model
Flip who writes the API test: the consumer states exactly what it needs, the provider's own pipeline proves it still delivers that, on every change, without needing the consumer's service running at all. This turns "did I just break someone downstream?" from a question requiring manual investigation or a slow, flaky E2E suite into an automatic, fast, precise CI check — and gives the provider real freedom to evolve everything a consumer doesn't actually depend on.

## Self-check questions
1. Why does a consumer-driven contract only cover the specific fields/behaviors a consumer actually uses, rather than the provider's entire API surface — and why does that restraint matter for the provider's ability to evolve?
2. Walk through what happens when `inventory-service` renames a field that `order-service`'s contract asserts on: where does the failure surface, and why is that earlier/cheaper than catching it via a full E2E test or in production?
3. Why is a stale, unmaintained consumer contract potentially worse than no contract at all?
4. A provider has five consumers but only two have ever published a Pact contract. What protection does the provider actually have when it changes its API, and what's the gap?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 10: "Testing" (consumer-driven contract testing discussion)
- Related: `building-microservices/11` (Testing Microservices) for how CDC fits into the broader testing pyramid; `building-microservices/03` (Service Boundaries and Coupling) for the information-hiding principle CDC applies to API evolution.
