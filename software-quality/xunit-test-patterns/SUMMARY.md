# xUnit Test Patterns: Refactoring Test Code

A compact recap of *xUnit Test Patterns: Refactoring Test Code* by Gerard Meszaros,
concept by concept. This subject builds the shared vocabulary for test structure, test
smells, and their matching refactorings, complementing
[software-engineering/refactoring](../../software-engineering/refactoring/README.md) by
applying the same change-safely discipline to test code itself.

Progress note: all 12 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded yet. This page will gain
depth (especially on the concepts the learner finds hard) as discussions happen - the
last section below will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom: the
xUnit architecture and readability basics first, then fixtures and test doubles, then
the smell catalog, then reliability and maintainability patterns, then suite-level
architecture.

## Foundations: anatomy, structure, and assertions

- **[xunit-test-patterns/01] Anatomy of an xUnit test and fixture** - the shared
  vocabulary (SUT, DOC, fixture, outcome) needed to diagnose any test precisely instead
  of vaguely calling it "messy." ([lesson](lessons/01-xunit-anatomy-and-fixture.md))
- **[xunit-test-patterns/02] Four-phase test and intent-revealing style** - every test
  is setup, exercise, verify, teardown, kept visually distinct, paired with a name that
  states the expected behavior rather than the input.
  ([lesson](lessons/02-four-phase-intent-revealing.md))
- **[xunit-test-patterns/03] Assertion patterns and failure diagnostics** - prefer the
  most specific assertion available; extract a Custom Assertion once a multi-field check
  repeats, so failures stay diagnostic instead of a bare "expected true but was false."
  ([lesson](lessons/03-assertion-patterns.md))

## Fixtures and test doubles

- **[xunit-test-patterns/04] Fixture setup and teardown patterns** - Fresh Fixture
  (build per test) is the safe default; Shared/Prebuilt Fixture trades independence for
  speed and is only safe for genuinely read-only data.
  ([lesson](lessons/04-fixture-setup-teardown.md))
- **[xunit-test-patterns/05] Test doubles in xUnit patterns language** - Dummy (never
  used), Stub (feeds an answer), Mock (verifies an interaction), Fake Object (a real
  lightweight implementation) each answer a different question; over-reaching for Mock
  is the most common misuse. ([lesson](lessons/05-test-doubles-pattern-language.md))

## The smell catalog

- **[xunit-test-patterns/06] Obscure test smell and readability refactorings** - four
  named causes (Eager Test, Mystery Guest, General Fixture, Conditional Test Logic),
  each with its own targeted fix. ([lesson](lessons/06-obscure-test-smell.md))
- **[xunit-test-patterns/07] Fragile test smell and brittleness controls** - four
  sensitivities (Interface, Behavior, Data, Context) that each cause a test to break for
  reasons unrelated to a real regression, each with a distinct mitigation.
  ([lesson](lessons/07-fragile-test-smell.md))
- **[xunit-test-patterns/08] Slow tests and suite execution economics** - a suite's
  value depends on how often it actually runs; unnecessary real I/O is the dominant
  cause of slowness, and a tiered pyramid (unit/integration/E2E) is the structural fix.
  ([lesson](lessons/08-slow-tests-economics.md))

## Data, verification, and reliability

- **[xunit-test-patterns/09] Data management patterns for repeatable tests** - Test Data
  Builder (fluent, defaulted construction) makes the relevant field visible per test;
  Object Mother names recurring, meaningful combinations.
  ([lesson](lessons/09-test-data-management.md))
- **[xunit-test-patterns/10] Result verification and behavior vs state checks** - prefer
  State Verification (check the resulting state, robust to refactoring) over Behavior
  Verification (check an interaction happened) except when there's genuinely no state to
  check. ([lesson](lessons/10-result-verification.md))

## Maintaining the suite over time

- **[xunit-test-patterns/11] Test code refactoring workflow and safety net** - never
  refactor tests and the SUT in the same step; verify a test refactor by checking the
  pass/fail verdict is unchanged, and for assertion-strategy changes, confirm the test
  still catches a deliberately injected bug.
  ([lesson](lessons/11-test-code-refactoring-workflow.md))
- **[xunit-test-patterns/12] Building a maintainable test suite architecture** - shared
  builder/assertion infrastructure and enforced tiering keep the marginal cost of each
  new test low as a suite scales; suite health is capped by how testable the production
  architecture itself is. ([lesson](lessons/12-test-suite-architecture.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
