---
id: goos/11
subject: goos
title: Emergent Architecture Through Continuous Refactoring
slug: emergent-architecture
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part III/Chapter 10
prerequisites: [goos/02, goos/10]
created: 2026-08-10
updated: 2026-08-10
---

# Emergent Architecture Through Continuous Refactoring

## TL;DR
Rather than fixing the system's architecture upfront and implementing to match it, GOOS treats architecture as something that emerges and improves continuously through disciplined, test-protected refactoring applied at every scale — from renaming a variable to reshaping how major components collaborate — driven by what real, growing requirements actually reveal, not by upfront prediction.

## The idea
Every earlier lesson in this subject has been building toward this one. `goos/02` grows the system in thin vertical slices instead of committing to a full design upfront. `goos/04` lets acceptance tests pull new objects and structure into existence only as needed. `goos/05` and `goos/07` discover object roles and protocols from real usage rather than speculative design. `goos/10` keeps the resulting tests resilient enough that the code underneath them can keep changing safely. The synthesis: a GOOS-style team never claims to have "the architecture" finished and locked at the start — they maintain, continuously, an architecture that fits the *current, real* shape of the requirements, using refactoring (safe, behavior-preserving code transformation, covered in depth in this repo's `refactoring` subject) as the mechanism that keeps that fit good as requirements grow and change.

This is a deliberate rejection of Big Design Up Front for systems where requirements are genuinely still being discovered (which describes most real software, and certainly the auction sniper as it's built incrementally throughout the book). The alternative isn't "no design" — it's design happening continuously, in small, safe, test-protected steps, informed by the best evidence available at each point: the actual, currently-known requirements, not a guess about future ones.

## How it works

### Refactoring at multiple scales, not just "clean up small stuff"
Freeman & Pryce distinguish small-scale refactoring (renaming a method, extracting a helper, inlining a needless abstraction) from larger, architectural-scale refactoring (splitting a class's responsibilities into two collaborating classes because it's grown incoherent, introducing a new interface — and hence a new port/adapter boundary per `goos/06` — because a dependency has grown complex enough to need isolating, or reshaping how several existing classes collaborate because their current protocol, discovered per `goos/07`, has turned out to be awkward under real usage). Both scales use the same underlying safety mechanism — a fast, trustworthy test suite (`goos/01`) that lets you make the change and immediately confirm behavior is preserved — but the larger-scale refactorings are exactly what let the system's *architecture*, not just its code style, keep evolving safely.

**Worked example — an architectural refactor driven by real growth.** Early in the sniper's development, one auction connection per sniper might be entirely adequate, and `AuctionSniper` might reasonably hold a direct reference to its one `Auction` collaborator. As the system grows to track many auctions simultaneously for one user, the original one-to-one assumption baked into the early design turns out not to fit — but this mismatch was invisible until the multi-auction requirement actually arrived; guessing at it upfront would have been speculative. The team responds by refactoring: introducing a collection-managing collaborator responsible for tracking multiple `AuctionSniper` instances, without rewriting the individual sniper's own bidding logic, which stays correct and fully tested throughout. Because the existing test suite (unit tests per `goos/05`/`goos/07`, plus the acceptance test per `goos/04`) covers the sniper's actual behavior, not its internal structure, this restructuring can proceed with continuous verification that nothing broke — the tests don't need to be discarded and rewritten, they need to keep passing throughout.

### Why this depends on everything upstream in this subject
Emergent architecture through refactoring only works if refactoring is actually *safe* — which is precisely what the earlier lessons set up. A fast test suite (`goos/01`) makes each refactoring step cheap to verify. Tests that assert on genuine behavior rather than brittle implementation coupling (`goos/10`) don't break spuriously during a legitimate restructuring, which is what makes larger refactorings tractable rather than terrifying. Role-based interfaces discovered from real need (`goos/05`) tend to already be smaller and more independently movable than interfaces designed monolithically upfront, which makes architectural refactoring (splitting, recombining, re-routing collaborators) more localized and less risky. Remove any of these supports and architectural refactoring becomes what it is in many real, poorly-tested codebases: something everyone agrees is theoretically a good idea and nobody actually dares to do.

### The role of "smells" in triggering architectural refactoring
Freeman & Pryce, echoing the broader refactoring literature (see this repo's `refactoring` subject for the canonical catalog of code smells and techniques), treat certain recurring frictions as signals that an architectural refactor is due, not just a local cleanup: a class accumulating unrelated responsibilities over successive features (a "God object" forming), a growing number of conditional branches checking what "kind" of collaborator is present (suggesting a missing polymorphic role), or tests that are consistently awkward to write for one particular area of the code (per `goos/09`'s "listening to hard-to-write tests"). None of these individually demand an immediate architectural response — but their persistence and growth across several feature additions is the evidence that this lesson relies on to justify architectural change, replacing upfront prediction with accumulated, concrete evidence.

### Emergent does not mean undirected
A common misreading of "emergent architecture" is that no architectural thinking happens at all — that the design simply falls out of following TDD mechanically. Freeman & Pryce don't advocate this: the walking skeleton (`goos/03`) still requires an initial, deliberate (if minimal and revisable) architectural sketch — roughly which major components will exist and how they'll be deployed — before any code is written. What's emergent is the *detail and evolution* of that architecture, not its complete absence at the outset. Judgment, informed by experience (recognizing likely seams, per `goos/06`), still guides where the walking skeleton's initial boundaries go; refactoring is what keeps those boundaries honest and current as real requirements test them, rather than requiring that initial judgment to have been perfect and permanent.

## Pros
- Keeps the architecture continuously fitted to real, evidenced requirements rather than requirements guessed months or years in advance, avoiding both under-design (a naive structure that can't handle real complexity) and over-design (speculative flexibility for needs that never materialize).
- Spreads architectural risk across many small, verified steps instead of concentrating it in one high-stakes upfront design phase or one risky big-bang rewrite later.
- Directly reuses this subject's entire toolkit (fast tests, role-based interfaces, ports and adapters, disciplined interaction testing) as the safety mechanism, rather than requiring a separate, additional practice.

## Cons
- Requires sustained team discipline over the system's entire life — a team that lets its test suite degrade (slow, flaky, or brittle per `goos/10`) loses the safety net this entire approach depends on, and architectural refactoring quietly stops happening even though everyone still believes it's possible.
- Some architectural decisions are genuinely expensive to unwind even with excellent refactoring discipline (a foundational data storage choice at real production scale, a public API with many external consumers) — "we can refactor it later" isn't equally true for every kind of decision, echoing `refactoring/12`'s caution about YAGNI's limits.
- Without any upfront architectural sketch at all, teams can drift for a long time before the accumulating friction (per the "smells" discussion above) becomes obvious enough to act on — emergent architecture benefits from periodic, deliberate reflection, not purely reactive triggering.

## Alternatives
- **Big Design Up Front (BDUF)** — commit to a comprehensive architecture before implementation begins. Appropriate when requirements are genuinely well-understood and stable, or when the cost of a wrong architectural guess is severe enough to justify upfront rigor — the direct alternative this lesson's incremental approach is positioned against.
- **Architecture review boards / formal governance** — a more structured, less code-driven process where architectural changes go through explicit review and approval, often used in larger organizations for compliance or cross-team coordination reasons that continuous, code-level refactoring alone doesn't address.
- **Evolutionary architecture with fitness functions** (see `architecture/evolutionary-architectures` if authored) — a system-level complement that adds automated checks (fitness functions) verifying architectural qualities are preserved as the system evolves, formalizing what this lesson otherwise relies on team judgment and test coverage to catch.

## When to use it
Rely on emergent architecture through refactoring whenever requirements are still genuinely being discovered — most new products, most systems in an actively evolving business domain — and whenever the team has (or is willing to build) the test-suite discipline this whole subject depends on. It's the natural complement to `goos/02`'s vertical-slice growth strategy.

## When NOT to use it
Don't rely on pure emergent architecture for decisions that are genuinely, severely expensive to reverse (foundational data architecture at scale, contracts with many external consumers) — invest more upfront care there specifically because refactoring's usual cost-reduction doesn't apply as fully. Also don't treat "emergent" as license to skip the walking skeleton's initial architectural sketch (`goos/03`) — some deliberate initial judgment about major boundaries is still required; what's emergent is the evolution from that starting point, not its total absence.

## Key takeaways / mental model
Treat architecture as a living hypothesis, continuously tested against real requirements as they arrive, and continuously corrected — safely, because of the test suite — when reality disagrees with the current shape. The whole toolkit built up across this subject (fast feedback, vertical slices, outside-in discovery, role-based design, port/adapter isolation, disciplined interaction testing) exists to make that continuous correction safe and cheap enough to actually happen, rather than being a nice idea nobody has the courage to act on.

## Self-check questions
1. Using the multi-auction worked example, explain specifically why the original one-sniper-per-connection assumption wasn't a design mistake at the time it was made, and why refactoring (rather than "getting it right the first time") was the appropriate response.
2. Name two things from earlier lessons in this subject (`goos/01` through `goos/10`) that this lesson's approach to emergent architecture directly depends on, and explain what would go wrong if one of them were missing.
3. Describe a kind of architectural decision where "we'll refactor it later if needed" is a weaker argument than usual, and explain what extra upfront care that decision deserves.
4. A team claims to be doing "emergent design" but has no walking skeleton and no initial sense of major component boundaries — they're "just writing tests and seeing what happens." What's missing from their understanding of this lesson's idea?

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part III, Chapter 10: "Listening to the Tests" and the book's closing chapters on sustainable design.
- See also: `refactoring/11` and `refactoring/12` (this repo's `refactoring` subject) for the underlying refactoring mechanics and the YAGNI/architecture trade-off this lesson extends.
