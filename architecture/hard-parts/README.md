# Software Architecture: The Hard Parts (trade-off analysis for distributed architectures)

The trade-off layer of the track: there are no best practices in distributed
architecture, only compromises. This subject teaches how to *pull a monolith apart and
put it back together* - reasoning about coupling, service and data granularity, data
ownership, distributed transactions and sagas, contracts, and analytical data - always
as explicit trade-offs. Many lessons cross-link to the DDIA and System Design concept
they build on.

**Source book:** *Software Architecture: The Hard Parts* - Neal Ford, Mark Richards,
Pramod Sadalage, and Zhamak Dehghani (O'Reilly, 2021).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`hard-parts/<NN>`* (e.g. *"discuss `hard-parts/07`"*). Ordered by dependency: the
analytical foundations (trade-offs, coupling) first, then *pulling things apart*, then
*putting them back together*, then the capstone trade-off method.

**Seniority baseline:** senior (lessons range senior->staff).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Trade-offs and "no best practices" | senior | drafted | — | — | [lesson](lessons/01-tradeoffs-no-best-practices.md) | — |
| 02  | The architecture quantum and static coupling | senior | drafted | — | — | [lesson](lessons/02-architecture-quantum-static-coupling.md) | — |
| 03  | Dynamic coupling | senior | drafted | — | — | [lesson](lessons/03-dynamic-coupling.md) | — |
| 04  | Architectural modularity | senior | drafted | — | — | [lesson](lessons/04-architectural-modularity.md) | — |
| 05  | Architectural decomposition | senior | drafted | — | — | [lesson](lessons/05-architectural-decomposition.md) | — |
| 06  | Component-based decomposition patterns | senior | drafted | — | — | [lesson](lessons/06-component-based-decomposition-patterns.md) | — |
| 07  | Service granularity | senior | drafted | — | — | [lesson](lessons/07-service-granularity.md) | — |
| 08  | Decomposing operational data | senior | drafted | — | — | [lesson](lessons/08-decomposing-operational-data.md) | — |
| 09  | Reuse patterns | mid | drafted | — | — | [lesson](lessons/09-reuse-patterns.md) | — |
| 10  | Data ownership | senior | drafted | — | — | [lesson](lessons/10-data-ownership.md) | — |
| 11  | Distributed transactions and eventual consistency | senior | drafted | — | — | [lesson](lessons/11-distributed-transactions-eventual-consistency.md) | — |
| 12  | Distributed data access | senior | drafted | — | — | [lesson](lessons/12-distributed-data-access.md) | — |
| 13  | Distributed workflows: orchestration vs choreography | senior | drafted | — | — | [lesson](lessons/13-distributed-workflows-orchestration-choreography.md) | — |
| 14  | Transactional sagas | staff | drafted | — | — | [lesson](lessons/14-transactional-sagas.md) | — |
| 15  | Contracts: strict vs loose | senior | drafted | — | — | [lesson](lessons/15-contracts.md) | — |
| 16  | Managing analytical data | staff | drafted | — | — | [lesson](lessons/16-managing-analytical-data.md) | — |
| 17  | Build your own trade-off analysis | staff | drafted | — | — | [lesson](lessons/17-build-your-own-trade-off-analysis.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** are listed per lesson in its front matter as IDs
(e.g. `ddia/11`, `system-design/10`); each lesson also names the concept it builds on
in prose.
