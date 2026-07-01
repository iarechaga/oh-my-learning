# Working Effectively with Legacy Code

The rescue layer of the software-engineering track: how to make changes safely to code
that has no tests. Feathers defines legacy code as *code without tests*, and the subject
teaches how to find **seams** where behavior can be intercepted, break dependencies so a
class can be instantiated in a test, write **characterization tests** that pin down
current behavior, and then change with confidence. It is the practical prerequisite for
applying Refactoring to real, messy systems.

**Source book:** *Working Effectively with Legacy Code* - Michael C. Feathers (Prentice
Hall, 2004).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`legacy-code/<NN>`* (e.g. *"discuss `legacy-code/04`"*). Ordered by dependency: the
mental model and seams first, then dependency-breaking and characterization, then the
recurring "I need to change X but..." scenarios.

**Seniority baseline:** senior (lessons range mid->senior).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | What legacy code is: the change dilemma | mid | drafted | — | — | [lesson](lessons/01-the-change-dilemma.md) | — |
| 02  | Seams and enabling points | senior | drafted | — | — | [lesson](lessons/02-seams.md) | — |
| 03  | Characterization tests | mid | drafted | — | — | [lesson](lessons/03-characterization-tests.md) | — |
| 04  | Sensing and separation | senior | drafted | — | — | [lesson](lessons/04-sensing-and-separation.md) | — |
| 05  | Breaking dependencies (the toolkit) | senior | drafted | — | — | [lesson](lessons/05-breaking-dependencies.md) | — |
| 06  | It takes forever to make a change | senior | drafted | — | — | [lesson](lessons/06-slow-to-change.md) | — |
| 07  | Adding a feature to untested code | senior | drafted | — | — | [lesson](lessons/07-adding-a-feature.md) | — |
| 08  | I can't get this class into a test harness | senior | drafted | — | — | [lesson](lessons/08-class-into-harness.md) | — |
| 09  | I can't run a method in a test harness | senior | drafted | — | — | [lesson](lessons/09-method-into-harness.md) | — |
| 10  | Finding what and where to change | mid | drafted | — | — | [lesson](lessons/10-finding-where-to-change.md) | — |
| 11  | Dependency-breaking techniques catalog | senior | drafted | — | — | [lesson](lessons/11-techniques-catalog.md) | — |
| 12  | Working with big, tangled methods | senior | drafted | — | — | [lesson](lessons/12-big-tangled-methods.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** (e.g. `refactoring/03`, `clean-code/09`) are listed per
lesson in its front matter and named in prose.
