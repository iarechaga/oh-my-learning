# Unit Testing: Principles, Practices, and Patterns

This subject focuses on what makes tests actually useful: high signal, low maintenance,
and fast feedback. You will learn to evaluate tests with clear quality criteria,
structure suites around behavior and boundaries, and choose doubles and integration
tests intentionally. It cross-links well with
[Refactoring](../../software-engineering/refactoring/README.md) because test quality
determines how safely you can change design.

**Source book:** *Unit Testing: Principles, Practices, and Patterns* - Vladimir Khorikov (Manning, 2020).

**Seniority baseline:** senior (lessons range junior->staff).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`unit-testing/<NN>`* (e.g. *"discuss `unit-testing/03`"*). Ordered by dependency:
start with test anatomy and value criteria, then isolation and doubles, then broader
system strategy and anti-patterns.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | What a unit test is and why it matters | junior | drafted | — | — | [lesson](lessons/01-what-a-unit-test-is.md) | — |
| 02  | AAA structure and test naming | junior | drafted | — | — | [lesson](lessons/02-aaa-and-naming.md) | — |
| 03  | The four pillars of good tests | senior | drafted | — | — | [lesson](lessons/03-four-pillars.md) | — |
| 04  | Behavioral vs implementation coupling | senior | drafted | — | — | [lesson](lessons/04-behavioral-vs-implementation-coupling.md) | — |
| 05  | Humble object and separating pure logic | mid | drafted | — | — | [lesson](lessons/05-humble-object.md) | — |
| 06  | Shared state, isolation, and deterministic tests | mid | drafted | — | — | [lesson](lessons/06-isolation-and-determinism.md) | — |
| 07  | Types of test doubles and trade-offs | mid | drafted | — | — | [lesson](lessons/07-test-doubles-trade-offs.md) | — |
| 08  | Mocking guidelines and interaction testing limits | senior | drafted | — | — | [lesson](lessons/08-mocking-guidelines.md) | — |
| 09  | London vs classical schools in practice | senior | drafted | — | — | [lesson](lessons/09-london-vs-classical.md) | — |
| 10  | Integration testing around external systems | senior | drafted | — | — | [lesson](lessons/10-integration-testing-boundaries.md) | — |
| 11  | Testing controllers and application services | mid | drafted | — | — | [lesson](lessons/11-testing-controllers-services.md) | — |
| 12  | Handling time, randomness, and concurrency in tests | senior | drafted | — | — | [lesson](lessons/12-time-randomness-concurrency.md) | — |
| 13  | Building a balanced test strategy for a codebase | staff | drafted | — | — | [lesson](lessons/13-balanced-test-strategy.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` · `mid` · `senior` · `staff` · `principal` - the band whose job the concept anchors.
