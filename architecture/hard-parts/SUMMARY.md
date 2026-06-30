# The Hard Parts - Subject Summary

A comprehensive recap of *Software Architecture: The Hard Parts*, concept by concept.
The book's thesis: in distributed architecture there are no best practices, only
trade-offs, and the architect's core skill is finding and weighing them. It is
organized as *pulling things apart* (how to decompose a monolith and its data) and
*putting them back together* (how the resulting services communicate, share, own data,
and coordinate), all dramatized through the fictional "Sysops Squad" saga.

**Source book:** *Software Architecture: The Hard Parts* - Neal Ford, Mark Richards,
Pramod Sadalage, and Zhamak Dehghani (O'Reilly, 2021).

**Progress note:** all 17 lessons are `drafted`; none discussed yet, so mastery is
pending and no weak spots are recorded. See the table in [README.md](README.md).
Reading order is top to bottom (dependency-ordered).

## Foundations (the analytical toolkit)

- **[01] Trade-offs and "no best practices"** - why every distributed-architecture
  decision is a compromise; the iterative technique (find the entangled dimensions,
  analyze trade-offs, decide in context), plus the supporting tools the book leans on:
  architecture decision records (ADRs) and architecture fitness functions, and the
  architecture-vs-design distinction. ([lesson](lessons/01-tradeoffs-no-best-practices.md))
- **[02] The architecture quantum and static coupling** - the architecture quantum (an
  independently deployable unit with high functional cohesion and high static coupling),
  static coupling as how parts are *wired* together, and connascence as the vocabulary
  for the strength and locality of coupling. ([lesson](lessons/02-architecture-quantum-static-coupling.md))
- **[03] Dynamic coupling** - how parts *call* one another at runtime: synchronous vs
  asynchronous communication and the three dimensions - communication, consistency, and
  coordination - that frame every distributed interaction (and later generate the saga
  patterns). ([lesson](lessons/03-dynamic-coupling.md))

## Pulling things apart

- **[04] Architectural modularity** - the drivers that justify breaking a monolith into
  distributed pieces: maintainability, testability, deployability, scalability, and
  availability/fault tolerance; turning those drivers into a business case.
  ([lesson](lessons/04-architectural-modularity.md))
- **[05] Architectural decomposition** - is the codebase even decomposable? afferent and
  efferent coupling, abstractness and instability, distance from the main sequence; then
  choosing between component-based decomposition and tactical forking.
  ([lesson](lessons/05-architectural-decomposition.md))
- **[06] Component-based decomposition patterns** - the repeatable, low-risk pattern loop
  to migrate a monolith: identify and size components, gather common domain components,
  flatten components, determine component dependencies, create component domains, and
  create domain services. ([lesson](lessons/06-component-based-decomposition-patterns.md))
- **[07] Service granularity** - the central tension of microservices: granularity
  disintegrators (reasons to split a service) versus integrators (reasons to keep it
  whole), and how to find the right service size. ([lesson](lessons/07-service-granularity.md))
- **[08] Decomposing operational data** - data disintegrators vs integrators, monolithic
  vs distributed data, and choosing the right database type per data domain. Builds on
  DDIA 10. ([lesson](lessons/08-decomposing-operational-data.md))

## Putting things back together

- **[09] Reuse patterns** - sharing functionality without over-coupling: code
  replication, shared library, shared service, and the sidecar / service mesh; the
  coupling and change trade-offs of each. ([lesson](lessons/09-reuse-patterns.md))
- **[10] Data ownership** - assigning each table to a single service: single, joint, and
  common ownership, and how to resolve the joint-ownership write problem.
  ([lesson](lessons/10-data-ownership.md))
- **[11] Distributed transactions and eventual consistency** - life without cross-service
  ACID: the difference from ACID, BASE, and the three eventual-consistency patterns
  (background synchronization, orchestrated request-based, event-based). Builds on DDIA
  09 and 11. ([lesson](lessons/11-distributed-transactions-eventual-consistency.md))
- **[12] Distributed data access** - reading data a service does not own: inter-service
  communication, column schema replication, replicated caching, and the data-domain
  pattern. Builds on System Design 10. ([lesson](lessons/12-distributed-data-access.md))
- **[13] Distributed workflows: orchestration vs choreography** - the two coordination
  styles, who owns workflow state and error handling, and their coupling / scalability /
  responsiveness trade-offs. ([lesson](lessons/13-distributed-workflows-orchestration-choreography.md))
- **[14] Transactional sagas** - the eight saga patterns formed by combining communication
  (sync/async) x consistency (atomic/eventual) x coordination (orchestrated/choreographed);
  compensating updates, state management, and when each saga fits. Builds on DDIA 13.
  ([lesson](lessons/14-transactional-sagas.md))
- **[15] Contracts: strict vs loose** - contracts as a coupling spectrum, stamp coupling,
  consumer-driven contracts, and the trade-offs between strict and loose contracts.
  ([lesson](lessons/15-contracts.md))
- **[16] Managing analytical data** - operational vs analytical data and the evolution of
  analytical architectures: data warehouse, data lake, and data mesh (data products and
  the analytical data quantum). Builds on DDIA 05 and 16. ([lesson](lessons/16-managing-analytical-data.md))

## Capstone

- **[17] Build your own trade-off analysis** - the full technique end to end: find the
  entangled dimensions, model the relevant domain scenarios, assess trade-offs
  qualitatively versus quantitatively, and avoid "out of context" and "evangelism"
  decision traps. Synthesizes every prior concept.
  ([lesson](lessons/17-build-your-own-trade-off-analysis.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on concepts rated
`shaky` or `not-yet`.
