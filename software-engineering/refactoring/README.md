# Refactoring

The change-safely layer of the software-engineering track: how to improve the design of
existing code without changing its behavior, driven by tests and applied in small,
reversible steps. Teaches the vocabulary of **code smells** and a **catalog of named
refactorings**. It builds directly on Clean Code (recognizing bad code) and pairs with
Working Effectively with Legacy Code (when there are no tests yet).

**Source book:** *Refactoring: Improving the Design of Existing Code* (2nd edition) -
Martin Fowler (Addison-Wesley, 2018).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`refactoring/<NN>`* (e.g. *"discuss `refactoring/03`"*). Ordered by dependency:
principles and the safety net first, then smells, then the refactoring catalog grouped
by purpose.

**Seniority baseline:** mid (lessons range junior->senior).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | What refactoring is (and is not) | junior | drafted | — | — | [lesson](lessons/01-what-refactoring-is.md) | — |
| 02  | Why refactor, and when | mid | drafted | — | — | [lesson](lessons/02-why-and-when.md) | — |
| 03  | Tests as the safety net | mid | drafted | — | — | [lesson](lessons/03-tests-safety-net.md) | — |
| 04  | Code smells: a catalog | mid | drafted | — | — | [lesson](lessons/04-code-smells.md) | — |
| 05  | Composing methods (extract/inline) | junior | drafted | — | — | [lesson](lessons/05-composing-methods.md) | — |
| 06  | Moving features between objects | mid | drafted | — | — | [lesson](lessons/06-moving-features.md) | — |
| 07  | Organizing data | mid | drafted | — | — | [lesson](lessons/07-organizing-data.md) | — |
| 08  | Simplifying conditional logic | mid | drafted | — | — | [lesson](lessons/08-simplifying-conditionals.md) | — |
| 09  | Refactoring APIs and parameters | mid | drafted | — | — | [lesson](lessons/09-refactoring-apis.md) | — |
| 10  | Dealing with inheritance | mid | drafted | — | — | [lesson](lessons/10-inheritance.md) | — |
| 11  | Big refactorings and breaking dependencies | senior | drafted | — | — | [lesson](lessons/11-big-refactorings.md) | — |
| 12  | Refactoring, architecture, and YAGNI | senior | drafted | — | — | [lesson](lessons/12-refactoring-architecture-yagni.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** (e.g. `clean-code/12`, `legacy-code/03`) are listed per
lesson in its front matter and named in prose.
