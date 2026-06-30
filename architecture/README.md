# Architecture

The architecture **domain** of this learning repository. It groups the book-subjects
that teach how to design software systems - the underlying theory and its applied
practice.

Concept IDs are subject-scoped (e.g. `ddia/07`, `system-design/03`), so this
`architecture/` folder organizes files on disk without changing how you refer to a
concept.

## Subjects

| Subject | What it is | Lessons | Index |
| --- | --- | --- | --- |
| **DDIA** | *Designing Data-Intensive Applications* (Kleppmann) - the theory of data systems: reliability/scalability, data models, storage, replication, partitioning, transactions, consistency/consensus, and batch/stream processing. | 16 | [ddia/README.md](ddia/README.md) |
| **System Design** | *System Design Guide for Software Professionals* (Sinha & Chopra) - applying that theory to real systems: load balancing, caching, sharding, queues, APIs, security, observability, plus end-to-end case studies. Cross-linked to DDIA. | 20 | [system-design/README.md](system-design/README.md) |
| **The Hard Parts** | *Software Architecture: The Hard Parts* (Ford, Richards, Sadalage, Dehghani) - trade-off analysis for distributed architectures: coupling, decomposition, service and data granularity, data ownership, distributed transactions and sagas, contracts, and analytical data. Cross-linked to DDIA and System Design. | 17 | [hard-parts/README.md](hard-parts/README.md) |

Planned next in this domain: *Fundamentals of Software Architecture* (consolidating the
architectural concepts and vocabulary).

See each subject's `README.md` for its concept index and progress, and the root
[SUMMARY.md](../SUMMARY.md) for the cross-domain overview.
