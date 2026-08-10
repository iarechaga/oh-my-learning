---
id: goos/04
subject: goos
title: Outside-In Development from Acceptance Tests
slug: outside-in-development
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II/Chapter 4
prerequisites: [goos/03]
created: 2026-08-10
updated: 2026-08-10
---

# Outside-In Development from Acceptance Tests

## TL;DR
Start each new feature with a failing, end-to-end acceptance test that describes the feature from the outside — as a user or external system would observe it — and let that single failing test drive the creation of unit tests and code from the outermost layer inward, only writing production code that's actually needed to satisfy a test that's currently red. This is TDD (`goos/01`) applied at two nested levels simultaneously: an outer acceptance-test loop that stays red for as long as the whole feature takes, and many inner unit-test loops that go red-green in minutes.

## The idea
`goos/01` establishes TDD's inner loop: write a unit test, watch it fail, make it pass. But a single unit test can't tell you whether the *feature* the user actually asked for works — a system can have every unit test green while the parts don't actually fit together into working behavior. Outside-in development addresses this by adding an outer loop: before writing any unit tests for a feature, write one **acceptance test** that exercises the system exactly the way an end user or external caller would — through the real entry point, with no shortcuts into internals — and assert on the user-visible outcome.

That acceptance test starts red and, crucially, *stays red* for the entire duration of building the feature — sometimes hours or days — because the feature genuinely isn't done until it is green. This gives the team an unambiguous, outside-observer's definition of "done" that can't be gamed by unit tests passing in isolation: the acceptance test only turns green when the feature actually, verifiably works end-to-end.

Inside that long-running red acceptance test, the team works inward: what's the first object the acceptance test's entry point needs? What does *that* object need from its collaborators? Each of those questions gets answered with its own fast, focused unit test (`goos/01`'s inner loop), discovering the system's internal objects and their responsibilities one small step at a time — rather than designing them all upfront. This discovery-through-collaboration process is developed further in `goos/05` (mock objects) and `goos/07` (object protocols).

## How it works

### The outer loop: one acceptance test per feature, red until genuinely done
For the auction sniper, a new feature — say, "the sniper increases its bid when outbid, up to a stop price" — starts with an acceptance test written against the system's real, deployed shape (the one the walking skeleton in `goos/03` established): start a sniper process, connect it to a test auction server, simulate another bidder outbidding it, and assert that the sniper places a higher bid, observed the same way a real operator would observe it (e.g., via the sniper's UI or a log). This test is deliberately written before any of the supporting code exists, so it fails — often with a very unhelpful error at first (a missing class, a connection failure) — and that failure is expected and useful: it's the very first thing the team needs to fix.

### The inner loop: let the acceptance test's needs pull unit tests into existence
With the acceptance test red, the team asks: what's the smallest piece of code needed to make progress toward green? This typically means identifying the first missing collaborator (e.g., an `AuctionSniper` class that needs to react to price events) and writing a *unit* test for that collaborator in isolation — using mock objects (`goos/05`) to stand in for collaborators that don't exist yet. Each unit test drives one class or method into existence via the normal red-green-refactor cycle. Critically, the team writes only enough production code to satisfy the currently-failing unit test — not to satisfy some imagined future need — which is what keeps the design driven by actual, demonstrated requirements rather than speculation.

**Worked example — walking through one slice of the bid-increase feature:**
1. The acceptance test is red: no bid is placed when the sniper is outbid.
2. The team identifies that `AuctionSniper` needs to know when it's been outbid — but there's no code listening for auction events yet. They write a unit test for an `AuctionEventListener` role that `AuctionSniper` implements, using a mock `Auction` collaborator to simulate the "you've been outbid" event, and assert that `AuctionSniper` responds by calling `bid()` on the (mock) auction with a higher amount. Red, then green.
3. Running the acceptance test again, it's still red — but for a *different*, more specific reason (now it fails because the real `Auction` implementation doesn't actually deliver that event over the wire yet). This is progress: the outer test's failure message is moving closer to the finish line with each inner-loop cycle.
4. Repeat: the next-nearest missing piece (the real messaging adapter that translates wire events into `AuctionEventListener` calls) gets its own unit test, and so on, until the acceptance test finally goes green.

### Why "outside-in" rather than "inside-out"
The alternative order — build the domain classes first based on your best guess of what they'll need, then wire them up to the outside world, then finally check whether the whole thing satisfies the user-facing requirement — routinely produces internal designs that don't quite fit the real entry point's needs, discovered only at the very end (echoing the horizontal-layering risk in `goos/02`). Outside-in avoids this by always deriving the *need* for a new class or method from a currently-failing test one level up — the acceptance test, or a unit test that itself exists because the acceptance test needed it. Nothing gets built "because it'll probably be useful"; everything gets built because a real, currently-red test says it's needed right now.

### Handling a long-red outer test without losing confidence
A multi-hour or multi-day red acceptance test can feel uncomfortable — "is anything actually broken, or is this just expected?" Freeman & Pryce's answer is to trust the inner loop's fast green cycles as the real signal of progress moment-to-moment, and to check the acceptance test's *failure message* changing (not just "still red") as the signal that the outer loop is converging, per the worked example above. A test failing for a new, more specific reason than it failed five minutes ago is evidence of real progress, even though the test itself hasn't gone green yet.

## Pros
- Ties every piece of new code to a real, demonstrated need — either the acceptance test's or an inner unit test's — which curbs speculative design.
- Produces an unambiguous, outside-observer definition of "feature done," resistant to the common trap of "all my unit tests pass but the feature doesn't actually work."
- Naturally discovers the system's internal object structure bottom-up from real usage, rather than requiring it to be designed correctly upfront.

## Cons
- The outer acceptance test can stay red for a long time on a non-trivial feature, which requires discipline and trust in the process rather than a quick, reassuring green.
- Acceptance tests that exercise the real system end-to-end tend to be slower and more fragile than unit tests (touching real or realistic infrastructure), so they must be used sparingly — one per feature, not one per class (contrast with `goos/01`'s much larger volume of fast unit tests).
- Requires the walking skeleton (`goos/03`) to already exist — outside-in development doesn't work well if there's no real "outside" entry point yet to write the acceptance test against.

## Alternatives
- **Inside-out (bottom-up) development** — build low-level components first based on anticipated needs, then assemble and integrate them upward into a working feature. Can feel more comfortable (each low-level piece is easy to get green quickly) but risks building the wrong shape of component, discovered only at integration.
- **Big-design-upfront with test coverage added after** — fully design the classes and their interactions before writing any tests, then backfill unit and acceptance tests. Skips the discovery benefit of outside-in entirely and tends to produce tests that just confirm the pre-chosen design rather than pressure-testing it.
- **Acceptance-test-only (no inner TDD loop)** — write only the acceptance test and implement the feature without a disciplined inner unit-test loop. Still gets the outside observer's definition of done, but loses the fine-grained design pressure and fast feedback that the inner loop provides.

## When to use it
Use outside-in, acceptance-test-driven development for any feature of real complexity spanning multiple collaborating objects or crossing a system boundary — which is most features in a growing system past its walking skeleton. It's most valuable exactly where the risk of "unit tests pass, feature doesn't actually work" is highest.

## When NOT to use it
For a genuinely trivial, single-class change with no meaningful integration risk, writing a full end-to-end acceptance test may be disproportionate ceremony — a focused unit test (`goos/01`) alone may suffice. Also reconsider the practice if your system has no stable "outside" to test against yet (pre-walking-skeleton, per `goos/03`) — get that in place first.

## Key takeaways / mental model
Picture two nested loops: an outer one (one acceptance test per feature, red until the feature genuinely works end-to-end) and many inner ones (fast unit tests, red-green in minutes, each triggered by whatever the outer loop currently needs next). Progress is measured not by the outer test turning green (that's the finish line) but by its failure message getting more specific, cycle after cycle, as the inner loop fills in the gap.

## Self-check questions
1. Explain why writing the acceptance test before any unit tests changes what gets built, compared to writing unit tests first and an acceptance test at the end.
2. Your acceptance test has been red for three hours on a complex feature. What signal, short of the test going green, would tell you the work is genuinely converging rather than stuck?
3. A junior developer wants to write ten acceptance tests for ten small variations of one feature, the same way they'd write ten unit tests. What would you tell them about the appropriate granularity of acceptance vs. unit tests, and why?

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II, Chapter 4: "A Walking Skeleton" and Chapter 6: "Object-Oriented Style."
