# Patterns of Enterprise Application Architecture

The enterprise-patterns layer of the software-engineering track: the classic catalog for
structuring data-heavy business applications - where the domain logic lives, how objects
map to relational databases (the guts of every ORM), how to manage concurrency and
sessions in a stateless web tier, and how to distribute. It is the pattern language that
explains what tools like Hibernate, ActiveRecord, and JPA are actually doing.

**Source book:** *Patterns of Enterprise Application Architecture* - Martin Fowler
(Addison-Wesley, 2002).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`enterprise-patterns/<NN>`* (e.g. *"discuss `enterprise-patterns/03`"*). Ordered by
dependency: layering and domain-logic patterns first, then the data-source and O/R
mapping patterns, then web presentation, concurrency, and distribution.

**Seniority baseline:** senior (lessons range mid->senior).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Layering and the enterprise application | mid | drafted | — | — | [lesson](lessons/01-layering.md) | — |
| 02  | Domain logic: Transaction Script vs Domain Model | senior | drafted | — | — | [lesson](lessons/02-domain-logic-patterns.md) | — |
| 03  | Table Module and Service Layer | senior | drafted | — | — | [lesson](lessons/03-table-module-service-layer.md) | — |
| 04  | Data source: Row Data Gateway and Table Data Gateway | senior | drafted | — | — | [lesson](lessons/04-data-source-gateways.md) | — |
| 05  | Active Record | mid | drafted | — | — | [lesson](lessons/05-active-record.md) | — |
| 06  | Data Mapper | senior | drafted | — | — | [lesson](lessons/06-data-mapper.md) | — |
| 07  | Unit of Work | senior | drafted | — | — | [lesson](lessons/07-unit-of-work.md) | — |
| 08  | Identity Map and Lazy Load | senior | drafted | — | — | [lesson](lessons/08-identity-map-lazy-load.md) | — |
| 09  | Object-relational structural mapping (inheritance) | senior | drafted | — | — | [lesson](lessons/09-or-structural-mapping.md) | — |
| 10  | Object-relational metadata mapping | senior | drafted | — | — | [lesson](lessons/10-or-metadata-mapping.md) | — |
| 11  | Web presentation (MVC, Page/Front Controller) | mid | drafted | — | — | [lesson](lessons/11-web-presentation.md) | — |
| 12  | Concurrency: optimistic vs pessimistic locking | senior | drafted | — | — | [lesson](lessons/12-concurrency-locking.md) | — |
| 13  | Session state patterns | mid | drafted | — | — | [lesson](lessons/13-session-state.md) | — |
| 14  | Distribution and the Remote Facade / DTO | senior | drafted | — | — | [lesson](lessons/14-distribution-remote-facade-dto.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** (e.g. `ddia/11`, `design-patterns/09`) are listed per
lesson in its front matter and named in prose.
