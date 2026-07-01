# xUnit Test Patterns: Refactoring Test Code

This subject is a practical catalog for improving test code quality over time. It
teaches the shared vocabulary for test smells, root causes, and proven refactorings so
you can keep suites readable, trustworthy, and cheap to maintain. It complements
[Refactoring](../../software-engineering/refactoring/README.md) by applying the same
change-safely mindset to the tests themselves.

**Source book:** *xUnit Test Patterns: Refactoring Test Code* - Gerard Meszaros (Addison-Wesley, 2007).

**Seniority baseline:** mid (lessons range junior->senior).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`xunit-test-patterns/<NN>`* (e.g. *"discuss `xunit-test-patterns/03`"*). Ordered by
dependency: first the xUnit architecture and readability basics, then smells and
fixtures, then reliability and maintainability patterns.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Anatomy of an xUnit test and fixture | junior | drafted | — | — | [lesson](lessons/01-xunit-anatomy-and-fixture.md) | — |
| 02  | Four-phase test and intent-revealing style | junior | drafted | — | — | [lesson](lessons/02-four-phase-intent-revealing.md) | — |
| 03  | Assertion patterns and failure diagnostics | mid | drafted | — | — | [lesson](lessons/03-assertion-patterns.md) | — |
| 04  | Fixture setup and teardown patterns | mid | drafted | — | — | [lesson](lessons/04-fixture-setup-teardown.md) | — |
| 05  | Test doubles in xUnit patterns language | mid | drafted | — | — | [lesson](lessons/05-test-doubles-pattern-language.md) | — |
| 06  | Obscure test smell and readability refactorings | mid | drafted | — | — | [lesson](lessons/06-obscure-test-smell.md) | — |
| 07  | Fragile test smell and brittleness controls | senior | drafted | — | — | [lesson](lessons/07-fragile-test-smell.md) | — |
| 08  | Slow tests and suite execution economics | senior | drafted | — | — | [lesson](lessons/08-slow-tests-economics.md) | — |
| 09  | Data management patterns for repeatable tests | mid | drafted | — | — | [lesson](lessons/09-test-data-management.md) | — |
| 10  | Result verification and behavior vs state checks | mid | drafted | — | — | [lesson](lessons/10-result-verification.md) | — |
| 11  | Test code refactoring workflow and safety net | senior | drafted | — | — | [lesson](lessons/11-test-code-refactoring-workflow.md) | — |
| 12  | Building a maintainable test suite architecture | senior | drafted | — | — | [lesson](lessons/12-test-suite-architecture.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` · `mid` · `senior` · `staff` · `principal` - the band whose job the concept anchors.
