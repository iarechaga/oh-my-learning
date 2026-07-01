# Clean Architecture

The structure layer of the software-engineering track: the principles that keep a
system's business rules independent of its delivery mechanisms - SOLID at the class
level, the component cohesion/coupling principles at the package level, and the
dependency rule that points all source-code dependencies inward toward policy. Where
Clean Code is about lines and functions, this subject is about how the pieces fit into a
whole. Cross-links to the architecture domain (styles, boundaries).

**Source book:** *Clean Architecture: A Craftsman's Guide to Software Structure and
Design* - Robert C. Martin (Prentice Hall, 2017).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`clean-architecture/<NN>`* (e.g. *"discuss `clean-architecture/06`"*). Ordered by
dependency: paradigms and SOLID first, then component principles, then architecture
boundaries and the dependency rule.

**Seniority baseline:** senior (lessons range mid->senior).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | What "good architecture" is for | mid | drafted | — | — | [lesson](lessons/01-what-architecture-is-for.md) | — |
| 02  | The three paradigms (structured, OO, functional) | senior | drafted | — | — | [lesson](lessons/02-programming-paradigms.md) | — |
| 03  | SRP and OCP | mid | drafted | — | — | [lesson](lessons/03-srp-ocp.md) | — |
| 04  | LSP, ISP, and DIP | senior | drafted | — | — | [lesson](lessons/04-lsp-isp-dip.md) | — |
| 05  | Component cohesion (REP, CCP, CRP) | senior | drafted | — | — | [lesson](lessons/05-component-cohesion.md) | — |
| 06  | Component coupling (ADP, SDP, SAP) | senior | drafted | — | — | [lesson](lessons/06-component-coupling.md) | — |
| 07  | Business rules: entities and use cases | senior | drafted | — | — | [lesson](lessons/07-business-rules.md) | — |
| 08  | The dependency rule and clean-architecture layers | senior | drafted | — | — | [lesson](lessons/08-dependency-rule.md) | — |
| 09  | Boundaries and the humble object pattern | senior | drafted | — | — | [lesson](lessons/09-boundaries-humble-object.md) | — |
| 10  | Policy, level, and the direction of dependencies | senior | drafted | — | — | [lesson](lessons/10-policy-and-level.md) | — |
| 11  | The database and the web are details | senior | drafted | — | — | [lesson](lessons/11-details-database-web.md) | — |
| 12  | The main component and partial boundaries | senior | drafted | — | — | [lesson](lessons/12-main-component-partial-boundaries.md) | — |
| 13  | Screaming architecture and test boundaries | mid | drafted | — | — | [lesson](lessons/13-screaming-architecture.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** (e.g. `fundamentals/05`) are listed per lesson in its
front matter and named in prose.
