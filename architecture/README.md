# Architecture

The architecture **domain** of this learning repository. It groups the book-subjects
that teach how to design scalable, maintainable, distributed systems - the underlying
theory, its applied practice, service decomposition, distributed-systems principles,
and evolving architectures over time.

Concept IDs are subject-scoped (e.g. `ddia/07`, `system-design/03`), so this
`architecture/` folder organizes files on disk without changing how you refer to a
concept.

## Subjects

| Subject | What it is | Lessons | Index |
| --- | --- | --- | --- |
| **DDIA** | *Designing Data-Intensive Applications* (Kleppmann) - the theory of data systems: reliability/scalability, data models, storage, replication, partitioning, transactions, consistency/consensus, and batch/stream processing. | 16 | [ddia/README.md](ddia/README.md) |
| **System Design** | *System Design Guide for Software Professionals* (Sinha & Chopra) - applying that theory to real systems: load balancing, caching, sharding, queues, APIs, security, observability, plus end-to-end case studies. Cross-linked to DDIA. | 20 | [system-design/README.md](system-design/README.md) |
| **The Hard Parts** | *Software Architecture: The Hard Parts* (Ford, Richards, Sadalage, Dehghani) - trade-off analysis for distributed architectures: coupling, decomposition, service and data granularity, data ownership, distributed transactions and sagas, contracts, and analytical data. Cross-linked to DDIA and System Design. | 17 | [hard-parts/README.md](hard-parts/README.md) |
| **Fundamentals** | *Fundamentals of Software Architecture* (Richards & Ford) - the consolidation layer: architectural thinking, characteristics, modularity, architecture styles, decisions, risk, communication, and architect leadership. Cross-linked to DDIA, System Design, and The Hard Parts. | 22 | [fundamentals/README.md](fundamentals/README.md) |
| **Building Microservices** | *Building Microservices*, 2nd ed. (Newman) - splitting a system into independently deployable services and keeping them shippable: boundaries, communication, per-service data, delivery, testing, observability, resilience, and team organization. | 17 | [building-microservices/README.md](building-microservices/README.md) |
| **Microservices Patterns** | *Microservices Patterns* (Richardson) - the pattern catalog for microservices: decomposition, IPC, sagas, event sourcing, CQRS, external API, testing, and production concerns. | 12 | [microservices-patterns/README.md](microservices-patterns/README.md) |
| **Designing Distributed Systems** | *Designing Distributed Systems* (Burns) - reusable container/orchestration patterns (sidecar, ambassador, adapter, sharding, scatter/gather, leader election) and batch-processing patterns. | 12 | [designing-distributed-systems/README.md](designing-distributed-systems/README.md) |
| **Distributed Systems** | *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum) - the formal principles: architectures, processes, communication, naming, coordination, consistency/replication, fault tolerance, consensus, and security. | 12 | [distributed-systems/README.md](distributed-systems/README.md) |
| **Evolutionary Architectures** | *Building Evolutionary Architectures*, 2nd ed. (Ford, Parsons, Kua, Sadalage) - guiding architectural change over time with fitness functions, incremental change, appropriate coupling, and governance. | 9 | [evolutionary-architectures/README.md](evolutionary-architectures/README.md) |
| **System Design Interview** | *System Design Interview*, Vol. 1 (Xu) - a repeatable interview framework, back-of-the-envelope estimation, and worked end-to-end designs (rate limiter, key-value store, news feed, chat, YouTube, and more). | 15 | [system-design-interview/README.md](system-design-interview/README.md) |

The current architecture track moves from data-system theory (DDIA), to applied system
design, to advanced distributed trade-off analysis (The Hard Parts), then consolidates
the broader architecture vocabulary in Fundamentals. It then extends into service
decomposition (Building Microservices, Microservices Patterns), the reusable and formal
foundations of distributed systems (Designing Distributed Systems, Distributed Systems),
evolving architectures over time (Evolutionary Architectures), and interview-style
end-to-end design practice (System Design Interview).

DDIA also underpins the future **Data Engineering** domain; it is kept here as the
architectural theory foundation and cross-referenced rather than duplicated.

See each subject's `README.md` for its concept index and progress, and the root
[SUMMARY.md](../SUMMARY.md) for the cross-domain overview.
