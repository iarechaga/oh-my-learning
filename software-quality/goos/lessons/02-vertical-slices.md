---
id: goos/02
subject: goos
title: Growing Software in Vertical Slices
slug: vertical-slices
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part I/Chapter 2
prerequisites: [goos/01]
created: 2026-08-10
updated: 2026-08-10
---

# Growing Software in Vertical Slices

## TL;DR
Grow a system feature by feature, end-to-end, rather than layer by layer: build one thin slice that touches every layer of the architecture (UI/entry point, domain logic, persistence, external integration) and works completely, then add the next slice. This keeps the whole system integrated and demonstrably working at every point in development, instead of leaving integration as a late, risky, all-at-once event.

## The idea
A common, intuitive way to build a system is horizontally, by layer: first build the whole data layer, then the whole domain/business logic layer, then the whole UI, then wire them all together at the end. It feels efficient — you finish one concern before moving to the next — but it defers the hardest and riskiest part, integration, to the very end, when you have the least time and the least appetite to discover that your layers don't actually fit together the way you assumed.

Freeman & Pryce argue for the opposite axis: grow the system **vertically**, one user-visible feature (or even a fragment of one) at a time, where each slice is a complete path through every layer the system has. The first slice might be almost embarrassingly small — "the sniper can join an auction and lose it because it never bids" — but it is *real*: it runs, it's deployed the way production code will be deployed, and it proves the layers actually connect. Every subsequent slice adds a bit more real behavior to an already-working system, rather than assembling a system that has never worked until the final integration step.

This connects directly to `goos/01`'s fast-feedback argument, but at a coarser grain: instead of just getting fast feedback on a single function's correctness, vertical slicing gets you fast feedback on the *system's actual integration* — the layer boundaries, the deployment pipeline, the real infrastructure — which is exactly the kind of thing that horizontal, layer-by-layer development discovers far too late.

## How it works

### Thin, not shallow: a slice must be end-to-end
The key discipline is that a slice is thin (it does very little) but not shallow (it doesn't skip any layer). For the auction sniper, a first slice is not "just the domain logic for placing a bid, tested in isolation" — that's shallow; it skips the auction house's messaging protocol, the UI, and deployment. A true first slice is something like: the sniper process starts, connects to a real (or realistically faked) auction server over the actual messaging protocol the real auction house uses, joins one auction, and shows in its UI that the auction is now being tracked. No bidding logic yet — that comes in later slices — but every architectural seam the finished system will have is already present and exercised, even if the behavior behind each seam is trivial.

**Worked example — three successive slices for the sniper:**
1. *Slice 1*: Sniper joins an auction, receives a "closed" event, and shows "Lost" in the UI. No bidding at all. This slice validates: can we connect to the auction protocol, receive events, and update a UI — the full vertical path — before any bidding logic exists.
2. *Slice 2*: Sniper places exactly one fixed bid when the auction starts, then behaves as before. This slice adds one more capability to the same working path — it doesn't touch the connection or UI code much, because that's already proven.
3. *Slice 3*: Sniper tracks the current price and increases its bid in response to being outbid, up to a stop price. This is where the "interesting" domain logic finally shows up — but it's being added to a system that has already been proven to work end-to-end twice over, so the risk is now isolated to the new bidding logic itself.

Compare this to a horizontal approach: build the full bidding algorithm first (in isolation, with no real connection to an auction house), then the UI, then the messaging integration — and only in week six do you discover the auction protocol doesn't deliver price updates the way your bidding algorithm assumed. Vertical slicing surfaces that mismatch in slice 1, in week one.

### Each slice should be independently valuable and deployable
Freeman & Pryce tie vertical slicing to the idea of always having *something releasable*. Even the very first slice — "join and lose" — should be able to go through the same build, test, and deployment pipeline the finished product will use (this is the seed of the walking skeleton, covered fully in `goos/03`). This matters because it means the deployment pipeline itself gets battle-tested from day one, rather than being a late-stage afterthought that turns out to be its own multi-week integration project.

### Choosing what goes in the first slice vs. later slices
Not every feature is equally suited to being "the first slice." The right first slice is the smallest one that still forces every architectural seam to exist — even in a trivial form. For the sniper, "join and lose" is deliberately almost useless as a product but maximally useful as an architecture-proving exercise: it forces you to solve auction discovery, the messaging protocol, and UI updates, without yet needing the hardest domain logic (the bidding strategy). Later slices then layer domain complexity onto an already-proven skeleton, one increment at a time, each validated the same red-green-refactor way as `goos/01` describes at the unit level.

## Pros
- Surfaces integration risk (mismatched assumptions between layers, unworkable protocols, deployment friction) in the first days of a project instead of the last.
- The system is releasable — in some minimal sense — from very early on, which supports genuine incremental delivery rather than a single all-or-nothing release.
- Each new slice is added to code that's already proven end-to-end, so the blast radius of a mistake is limited to the new slice, not the whole system.

## Cons
- Early slices can look unimpressive or even silly to stakeholders unfamiliar with the technique ("you spent a week and all it does is lose every auction?") — it requires managing expectations about what early progress looks like.
- Choosing the right first slice takes judgment; pick one too trivial and it doesn't actually prove the hard integration points, pick one too ambitious and you lose the "thin" benefit.
- Doesn't remove the need for architectural thinking — you still have to have a rough idea of the layers and boundaries before you can slice through them; vertical slicing structures the growth of an architecture, it doesn't invent one from nothing.

## Alternatives
- **Horizontal/layered development** — build each architectural layer fully before moving to the next. Familiar and lets specialists focus on one layer, but defers integration risk to the end, which is exactly what this lesson argues against for systems with real integration uncertainty.
- **Big-bang integration after parallel development** — teams build layers or components in parallel and integrate once, near the end. Can be faster if the interfaces between components are genuinely well-understood and stable in advance, but is high-risk when they aren't (which is common).
- **Prototype-then-throwaway** — build a quick end-to-end prototype to learn the integration points, then discard it and build the "real" system properly. Learns the same lessons vertical slicing does, but the learning isn't kept — vertical slicing's slices become the actual production code, not a disposable rehearsal.

## When to use it
Use vertical slicing whenever a project has real integration uncertainty — unfamiliar external systems, a new protocol, a new deployment target, or a team that hasn't built this kind of system together before. The less certain you are that the layers will fit together as assumed, the more valuable it is to prove that early with a thin real slice.

## When NOT to use it
If the architecture is already well-established (you're adding the fifth similar feature to a mature system with proven layers and pipeline), the integration-risk argument is weaker — you can reasonably do more work in a single layer at a time, because the seams are already known to work. Vertical slicing's overhead (constantly touching every layer for even tiny features) is most worth paying when the payoff — early proof of integration — is actually uncertain.

## Key takeaways / mental model
Picture the system as a set of vertical columns (features) crossing a set of horizontal rows (layers). Horizontal development fills in row by row, leaving the columns unproven until the last row is done. Vertical slicing fills in column by column, so every column, however thin, proves the full height of the system works — and the deployment pipeline that ships it — from the very first one.

## Self-check questions
1. Explain why "join an auction and immediately lose it" is a better first slice for the sniper than "implement the full bidding algorithm, unit-tested in isolation." What specific risk does the first slice retire that the second does not?
2. A stakeholder is frustrated that after two weeks the sniper "still can't actually bid." How would you explain, in terms of risk retirement rather than feature count, what those two weeks accomplished?
3. Describe a project where horizontal, layer-by-layer development would actually be a reasonable choice over vertical slicing, and explain what property of that project changes the trade-off.

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part I, Chapter 2: "Test-Driven Development with Objects."
