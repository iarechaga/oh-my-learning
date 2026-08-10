---
id: goos/06
subject: goos
title: Ports and Adapters at System Boundaries
slug: ports-and-adapters
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II/Chapter 8
prerequisites: [goos/05]
created: 2026-08-10
updated: 2026-08-10
---

# Ports and Adapters at System Boundaries

## TL;DR
Keep your domain logic entirely ignorant of the messy, external-world details (network protocols, third-party APIs, message formats) it ultimately depends on, by defining the domain's needs as small role interfaces ("ports") and writing thin, isolated "adapter" classes that translate between the messy external reality and those clean ports. This is the ports-and-adapters (hexagonal) architecture style, and in GOOS it emerges naturally from disciplined mock-driven design (`goos/05`) applied specifically at a system's external boundaries.

## The idea
Every real system has to talk to something outside its control — a third-party API, a message queue, a database, another team's service — and that outside world rarely speaks in terms that match your domain's vocabulary or is even stable over time (protocols change, libraries get upgraded, vendors alter behavior). If domain logic calls directly into a third-party library's types and methods, that messiness leaks throughout the codebase: domain classes end up littered with protocol-specific concepts, and any change to the external system or the desire to swap it out ripples through business logic that has nothing conceptually to do with, say, XMPP message parsing.

Ports and adapters (a term popularized by Alistair Cockburn as "hexagonal architecture," and adopted directly by Freeman & Pryce for the sniper's auction-house integration) solves this by drawing a hard line: the domain defines, in its own vocabulary, the narrow interface ("port") it needs from the outside world — discovered the same mock-driven way as `goos/05` — and a separate, isolated **adapter** class is responsible for implementing that port by translating to and from whatever the real external system actually speaks. The domain never sees the external system's real API, message format, or client library; it only ever talks to its own port.

## How it works

### The port: defined by the domain's needs, not the external system's shape
For the sniper, the domain needs to (a) be told when an auction's price changes or it closes, and (b) be able to place a bid. Those needs define two small ports: `AuctionEventListener` (price/close notifications flowing in) and something like an `Auction` bidding port (bid requests flowing out) — exactly the role interfaces discovered in `goos/05`. Crucially, these ports are shaped entirely by what `AuctionSniper` needs to say and hear, in the sniper's own vocabulary (`currentPrice(price, increment)`, `bid(amount)`) — not by the auction house's real message schema, which might encode prices as strings inside an XMPP chat-room message with vendor-specific formatting quirks.

### The adapter: isolates and absorbs the external system's mess
A separate class — say, `XMPPAuction` — implements the bidding port and, separately, translates incoming XMPP chat messages into calls on the domain's `AuctionEventListener` port. All of the ugly, protocol-specific work lives here and nowhere else: parsing the auction house's specific message format (`"SOLVersion: 1.1; Event: PRICE; CurrentPrice: 192; Increment: 6; Bidder: ..."`), handling connection setup and teardown, mapping malformed or unexpected messages to sensible domain-level behavior (or explicit failure), and serializing a domain-level `bid(amount)` call into the exact wire format the real auction house expects. If the auction house changes its message format, or the team swaps XMPP for a different protocol entirely, only `XMPPAuction` (and its tests) need to change — `AuctionSniper` and every test written against the clean port are completely unaffected.

**Worked example — before and after.** Without a port/adapter boundary, `AuctionSniper` might directly parse incoming XMPP stanzas: `if (message.getBody().contains("Event: CLOSE")) { ... }`. This couples core bidding logic to XMPP's wire format directly. With the boundary in place, `XMPPAuction` does that parsing internally and calls `sniperCollector.auctionClosed()` on the clean `AuctionEventListener` port; `AuctionSniper`'s code and tests never mention XMPP, chat rooms, or stanza parsing at all — they only ever see `auctionClosed()`.

### Testing each side independently, at the seam
The port/adapter split creates a natural, valuable seam for testing. `AuctionSniper`'s behavior is tested entirely against a mock or fake implementation of the port (fast, in-memory, no real network) — this is the bulk of the fast unit-test suite from `goos/01`. The adapter (`XMPPAuction`) gets its own, separate, narrower set of tests that specifically verify it translates correctly between the real wire protocol and the port's calls — these tests are fewer, slower, and closer to integration tests, but they're isolated to exactly the one place where the messy translation logic lives, so they don't need to be duplicated across every domain-level test.

### Ports and adapters vs. layered architecture
A traditional layered architecture (UI -> business logic -> data access) draws its boundaries by technical *layer*. Ports and adapters draws its boundary differently: the domain sits at the center, and *every* external dependency — a database, a UI, a third-party service, a message queue — is just another adapter around a port defined by the domain's needs, with no dependency arrow pointing back into the domain. This is why it's sometimes drawn as a hexagon rather than a stack: there's no privileged "top" or "bottom" layer, just the domain core and a ring of adapters, each swappable independently. For the sniper, both the real `XMPPAuction` adapter and a test double auction server are equally valid adapters around the same bidding/listener ports — the domain code can't tell them apart, which is exactly the point.

## Pros
- Isolates all protocol-specific, vendor-specific, or infrastructure-specific mess into a small number of adapter classes, keeping the domain clean, stable, and easy to reason about.
- Makes swapping an external dependency (a new auction house, a new message broker, a new database) a change localized to one adapter, not a change rippling through business logic.
- Enables fast, isolated domain-level testing against mocked or faked ports (`goos/05`), while confining slow, fragile, real-protocol tests to a small adapter-specific test suite.

## Cons
- Adds real indirection — an extra interface and an extra class — for every external dependency, which is overhead not worth paying for a dependency that's simple, stable, and unlikely to ever change or need isolated testing.
- Getting a port's shape right takes the same mock-driven discovery discipline as `goos/05`; a port designed around the external system's shape rather than the domain's actual needs (a common mistake under time pressure) gives you the extra indirection without the real benefit.
- The adapter itself still needs real, often slower and more fragile tests against the actual external system (or a realistic fake of it) — the pattern doesn't eliminate that testing burden, it just concentrates and isolates it.

## Alternatives
- **Direct integration (no port/adapter boundary)** — domain code calls third-party client libraries directly. Less code and indirection upfront, but couples business logic to external vendor APIs and makes both testing and future swaps much harder — the default a team drifts into without deliberate boundary design.
- **Anti-corruption layer (DDD)** — a closely related idea from Domain-Driven Design (see `domain-modeling/ddd-distilled`'s bounded-context lesson) that specifically translates between two different domain models at an integration boundary; ports and adapters is the general architectural mechanism, and an anti-corruption layer is often implemented as a specific kind of adapter.
- **Shared kernel / direct model reuse** — instead of isolating and translating, some integrations deliberately share types and models directly with an external system (appropriate only when you control both sides and genuinely want them coupled) — the opposite trade-off from ports and adapters' deliberate decoupling.

## When to use it
Use ports and adapters at any boundary where the external system's shape is likely to change, is out of your control, is awkward or slow to test against directly, or where you anticipate needing to swap implementations (a real auction house vs. a test double, a real payment gateway vs. a sandbox). This is essentially every meaningful external integration in a system expected to live and evolve.

## When NOT to use it
Don't introduce a port/adapter boundary around a dependency that's simple, stable, fully within your control, and unlikely to ever be swapped or need isolated testing — the extra interface and adapter class there is pure overhead. Also don't force one port to cover multiple, unrelated external systems just to "have one boundary" — that reintroduces the fat-interface problem `goos/05` warns against.

## Key takeaways / mental model
Draw a hard line around your domain: nothing outside that line may be spoken of in vocabulary from outside that line. Every external dependency talks to the domain only through a small, domain-shaped port; all translation and mess-absorption happens in a thin adapter sitting just outside that line. If you can swap an adapter (real auction house <-> test double) without the domain code noticing, the boundary is doing its job.

## Self-check questions
1. Explain why the `AuctionEventListener` port's method signatures should be designed around what `AuctionSniper` needs to know, rather than around the auction house's actual XMPP message schema.
2. The auction house changes its wire protocol from XMPP to a REST-based webhook. Walk through exactly which classes need to change under a ports-and-adapters design, and which are unaffected.
3. A teammate argues that adding a port/adapter boundary around a simple internal configuration-file reader is good practice "for consistency." Do you agree? What's the cost/benefit here compared to the auction-house integration?
4. How does the port/adapter boundary change what kinds of tests you write on each side of it, and why does that split matter for the fast-feedback goal from `goos/01`?

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II, Chapter 8: "Building on Third-Party Infrastructure."
- Alistair Cockburn, "Hexagonal Architecture" (ports and adapters, the original formulation this lesson's terminology comes from).
