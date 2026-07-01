# Growing Object-Oriented Software, Guided by Tests

This subject teaches test-driven development as a design method for whole systems, not
just isolated units. You start from a thin end-to-end slice, grow behavior outside-in,
and use mock objects to discover object roles and boundaries. It pairs naturally with
[Refactoring](../../software-engineering/refactoring/README.md) and
[Working Effectively with Legacy Code](../../software-engineering/legacy-code/README.md)
when you need to evolve code safely after initial delivery.

**Source book:** *Growing Object-Oriented Software, Guided by Tests* - Steve Freeman & Nat Pryce (Addison-Wesley, 2009).

**Seniority baseline:** senior (lessons range mid->staff).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`goos/<NN>`* (e.g. *"discuss `goos/03`"*). Ordered by dependency: establish the TDD
feedback loop, grow an outside-in walking skeleton, then scale collaboration and
architecture decisions.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | TDD as fast feedback for behavior | mid | drafted | — | — | [lesson](lessons/01-tdd-fast-feedback.md) | — |
| 02  | Growing software in vertical slices | senior | drafted | — | — | [lesson](lessons/02-vertical-slices.md) | — |
| 03  | Walking skeleton and deployment pipeline | senior | drafted | — | — | [lesson](lessons/03-walking-skeleton.md) | — |
| 04  | Outside-in development from acceptance tests | senior | drafted | — | — | [lesson](lessons/04-outside-in-development.md) | — |
| 05  | Mock objects and role-based design | senior | drafted | — | — | [lesson](lessons/05-mock-objects-role-design.md) | — |
| 06  | Ports and adapters at system boundaries | senior | drafted | — | — | [lesson](lessons/06-ports-and-adapters.md) | — |
| 07  | Designing object protocols through collaboration tests | senior | drafted | — | — | [lesson](lessons/07-object-protocols.md) | — |
| 08  | Testing asynchronous and event-driven behavior | senior | drafted | — | — | [lesson](lessons/08-async-event-driven-testing.md) | — |
| 09  | Keeping tests expressive and diagnosing failures | senior | drafted | — | — | [lesson](lessons/09-expressive-tests-diagnostics.md) | — |
| 10  | Managing coupling and avoiding brittle interaction tests | senior | drafted | — | — | [lesson](lessons/10-managing-test-coupling.md) | — |
| 11  | Emergent architecture through continuous refactoring | senior | drafted | — | — | [lesson](lessons/11-emergent-architecture.md) | — |
| 12  | Test strategy across a service ecosystem | staff | drafted | — | — | [lesson](lessons/12-service-ecosystem-strategy.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` · `mid` · `senior` · `staff` · `principal` - the band whose job the concept anchors.
