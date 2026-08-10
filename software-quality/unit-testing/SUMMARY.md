# Unit Testing: Principles, Practices, and Patterns

A compact recap of *Unit Testing: Principles, Practices, and Patterns* by Vladimir
Khorikov, concept by concept. This subject builds a rigorous framework for judging
test quality (not just writing tests): what a unit test actually is, how to evaluate
one against four independent quality pillars, how to keep tests coupled to behavior
rather than implementation, how to use test doubles without inviting brittleness, and
how to shape a whole suite's investment sensibly across a codebase.

This file is part of the repository's learning-content structure (see
`agent-docs/repository-model.md`) - every subject folder carries a `SUMMARY.md` as its
comprehensive per-concept recap, parallel to `domain-modeling/ddd-distilled/SUMMARY.md`.

Progress note: all 13 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded yet. This page will gain
depth (especially on the concepts the learner finds hard) as discussions happen - the
last section below will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom: test
anatomy and quality criteria first, then isolation and doubles, then broader system
strategy, integration boundaries, and anti-patterns.

## Foundations: what a test is and how it's structured

- **[unit-testing/01] What a unit test is and why it matters** - a unit test verifies a
  small piece of behavior, runs fast, and runs in isolation; its purpose is protecting
  the codebase against regressions cheaply, not hitting a coverage number.
  ([lesson](lessons/01-what-a-unit-test-is.md))
- **[unit-testing/02] AAA structure and test naming** - structure every test as
  Arrange-Act-Assert with exactly one behavior under test, and name it after that
  behavior in plain language, not after the method being called.
  ([lesson](lessons/02-aaa-and-naming.md))

## Evaluating and designing good tests

- **[unit-testing/03] The four pillars of good tests** - score any test on protection
  against regressions, resistance to refactoring, fast feedback, and maintainability;
  no test maximizes all four, and the central everyday trade-off is protection vs.
  speed, tuned per layer. ([lesson](lessons/03-four-pillars.md))
- **[unit-testing/04] Behavioral vs. implementation coupling** - couple tests to
  observable behavior (inputs -> outputs/effects), never to internal implementation
  details; implementation-coupled tests break on safe refactors and erode trust in
  "red means broken." ([lesson](lessons/04-behavioral-vs-implementation-coupling.md))
- **[unit-testing/05] Humble object and separating pure logic** - split code entangled
  with untestable dependencies (UI, DB, clock) into a rich, pure, exhaustively-tested
  logic piece and a thin, mostly-untested wrapper that just talks to the
  infrastructure. ([lesson](lessons/05-humble-object.md))

## Isolation, doubles, and mocking discipline

- **[unit-testing/06] Shared state, isolation, and deterministic tests** - eliminate
  shared mutable state between tests (statics, shared fixtures) and hidden
  non-determinism so every test gives the same result regardless of order or
  parallelism. ([lesson](lessons/06-isolation-and-determinism.md))
- **[unit-testing/07] Types of test doubles and trade-offs** - dummy, stub, spy, mock,
  and fake are five distinct tools with five distinct jobs; default to the least
  powerful double that lets the test check what actually matters.
  ([lesson](lessons/07-test-doubles-trade-offs.md))
- **[unit-testing/08] Mocking guidelines and interaction testing limits** - mock only
  true external dependencies whose call crosses the system boundary and is itself part
  of the requirement; verify narrowly, and treat "needs many mocks" as a design smell.
  ([lesson](lessons/08-mocking-guidelines.md))
- **[unit-testing/09] London vs. classical schools in practice** - London mocks every
  collaborator to isolate a class; classical isolates test cases from each other and
  keeps real, fast collaborators, mocking only true external dependencies - classical
  wins on resistance to refactoring for most of a suite.
  ([lesson](lessons/09-london-vs-classical.md))

## System boundaries and application structure

- **[unit-testing/10] Integration testing around external systems** - integration
  tests verify the real seams (schema, serialization, real error formats) that unit
  tests structurally cannot, using far fewer, deliberately isolated tests aimed
  precisely at those boundaries. ([lesson](lessons/10-integration-testing-boundaries.md))
- **[unit-testing/11] Testing controllers and application services** - the thin
  orchestration layer left after Humble Object gets a small number of focused wiring
  tests (happy path, error path), not exhaustive business-rule re-coverage that the
  domain layer already owns. ([lesson](lessons/11-testing-controllers-services.md))
- **[unit-testing/12] Handling time, randomness, and concurrency in tests** - inject
  the clock and random source explicitly to make time/randomness-dependent logic fully
  deterministic; concurrency is harder because the bug of interest (a race) is defined
  by the same non-determinism a test needs to eliminate - combine deterministic
  synchronization tests, probabilistic stress tests, and design that minimizes shared
  mutable state. ([lesson](lessons/12-time-randomness-concurrency.md))

## Whole-suite strategy

- **[unit-testing/13] Building a balanced test strategy for a codebase** - shape a
  suite like a portfolio: heaviest unit-test investment where complexity and domain
  significance are both high, a small integration layer at real boundaries, rare
  end-to-end tests, and active vigilance against anti-patterns (private-method
  testing, mirrored-logic assertions, mystery guests, creeping over-mocking).
  ([lesson](lessons/13-balanced-test-strategy.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
