# Growing Object-Oriented Software, Guided by Tests

A comprehensive recap of *Growing Object-Oriented Software, Guided by Tests* by Steve
Freeman & Nat Pryce, concept by concept. This subject teaches test-driven development as
a whole-system design method, not just a unit-testing habit: start from a thin,
end-to-end walking skeleton, grow behavior outward one vertical slice at a time, and use
mock-driven collaboration tests to discover object roles and system boundaries as you
go, letting architecture emerge through continuous, test-protected refactoring rather
than being fixed upfront. The running example throughout is an auction sniper - a
program that watches an online auction and places a last-moment bid on the user's
behalf - reused consistently across all twelve lessons.

Progress note: all 12 lessons are `drafted`; none have been discussed yet, so mastery is
pending across the board and no weak spots are recorded yet. This page will gain depth
(especially on the concepts the learner finds hard) as discussions happen - the last
section below will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
establish the TDD feedback loop and growth strategy first, then work through the worked
example of growing the sniper end-to-end, then the practices that sustain a codebase
(and, eventually, a whole service ecosystem) as it keeps growing.

## The process: feedback and growth strategy

- **[goos/01] TDD as fast feedback for behavior** - a failing test is a precise
  statement of what should happen next; the red-green-refactor cycle keeps the system
  (and your understanding of it) in a known, working state, advancing in small, checked
  steps. Fast wall-clock test speed is what actually delivers the feedback-loop benefit,
  not just the logical correctness of the tests. ([lesson](lessons/01-tdd-fast-feedback.md))
- **[goos/02] Growing software in vertical slices** - build one thin, end-to-end feature
  slice that touches every architectural layer and works completely, then add the next
  slice, rather than building layer by layer and integrating only at the end. Surfaces
  integration risk in week one instead of week six.
  ([lesson](lessons/02-vertical-slices.md))

## Growing the sniper end-to-end (the worked example)

- **[goos/03] Walking skeleton and deployment pipeline** - the smallest system that
  connects every major architectural piece and can be built, tested, and deployed
  through the real pipeline before it does anything useful; built first, deployed for
  real from day one, and never thrown away - it becomes the first production slice.
  ([lesson](lessons/03-walking-skeleton.md))
- **[goos/04] Outside-in development from acceptance tests** - start each feature with
  one failing, end-to-end acceptance test that stays red until the feature genuinely
  works, and let that outer loop pull unit tests and code into existence from the
  outside in, discovering the system's inner objects from real, demonstrated need rather
  than upfront design. ([lesson](lessons/04-outside-in-development.md))
- **[goos/05] Mock objects and role-based design** - writing a mock-based unit test is a
  design act: it forces you to decide exactly what message an object needs to send a
  collaborator, discovering minimal, role-shaped interfaces and pushing toward "tell,
  don't ask" rather than state-querying. Distinguishes mocks (verify an action was
  requested) from stubs (supply needed state).
  ([lesson](lessons/05-mock-objects-role-design.md))
- **[goos/06] Ports and adapters at system boundaries** - define what the domain needs
  from the outside world as small ports, shaped by the domain's own vocabulary, and
  isolate all translation to/from a messy external protocol inside thin adapter classes,
  so a changed or swapped external system never ripples into business logic.
  ([lesson](lessons/06-ports-and-adapters.md))
- **[goos/07] Designing object protocols through collaboration tests** - an object's
  protocol is the meaningful sequence of messages it exchanges with collaborators over
  time, not just one method's signature; multi-step scenario tests surface state-handling
  and ordering problems that single-call tests miss, and an awkward-to-write scenario
  test is a signal the protocol itself needs rethinking.
  ([lesson](lessons/07-object-protocols.md))
- **[goos/08] Testing asynchronous and event-driven behavior** - assert on eventual
  outcomes via bounded polling/waiting helpers rather than fixed sleeps or synchronous
  assumptions, and keep as much of the suite synchronous as possible by isolating real
  asynchrony behind the ports and adapters from `goos/06`; testing for the absence of an
  async event is pushed down to a synchronous, mock-based test instead.
  ([lesson](lessons/08-async-event-driven-testing.md))

## Sustaining a growing codebase

- **[goos/09] Keeping tests expressive and diagnosing failures** - tests are executable
  specifications; invest in readable structure (builders, intention-revealing names) and
  diagnostic assertions (custom matchers reporting expected-vs-actual) so a failure is
  understood in seconds, and treat a test that's painful to write as design feedback
  about the production code, not just testing friction.
  ([lesson](lessons/09-expressive-tests-diagnostics.md))
- **[goos/10] Managing coupling and avoiding brittle interaction tests** - mock only
  collaborators the object under test genuinely depends on for its own decisions, and
  assert only on calls and parameters that are actually part of the behavior's contract;
  overmocking couples tests to implementation detail and produces the familiar complaint
  that refactoring keeps breaking tests for no real reason.
  ([lesson](lessons/10-managing-test-coupling.md))
- **[goos/11] Emergent architecture through continuous refactoring** - the synthesis of
  the whole subject: architecture is a continuously-tested hypothesis, corrected safely
  through refactoring at every scale (from a rename to a major restructuring) as real
  requirements reveal where the current design no longer fits, rather than being fixed
  and predicted upfront. Depends directly on `goos/01`'s fast tests and `goos/10`'s
  non-brittle interaction tests to be safe in practice.
  ([lesson](lessons/11-emergent-architecture.md))
- **[goos/12] Test strategy across a service ecosystem** - extends the subject's
  discipline to many independently-deployed, team-owned services: keep full end-to-end
  tests deliberately few (they don't scale the way unit tests do), and use
  consumer-driven contracts - a direct organizational-scale extension of `goos/06`'s
  ports-and-adapters idea - to verify each pairwise boundary cheaply, without requiring
  every service to be live during another team's development.
  ([lesson](lessons/12-service-ecosystem-strategy.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject. Once discussions begin,
expect the highest-value areas to revisit to be `goos/10` (the mocking discipline that
keeps everything else honest) and `goos/11`/`goos/12` (the synthesis and its scaling to
multiple teams), since these lessons depend most heavily on the earlier ones landing
correctly.
