# Data Engineering & Databases

This domain focuses on choosing, designing, and understanding storage systems
for real workloads. It combines internals knowledge, practical SQL performance
work, and cross-model database selection so decisions are grounded in both
mechanics and trade-offs.

Concept IDs are subject-scoped (e.g. `database-internals/07`), so this `data-engineering/` folder organizes files on disk without changing how you refer to a concept.

DDIA (*Designing Data-Intensive Applications*) is the theoretical foundation for this domain; it lives under the architecture domain at [architecture/ddia/README.md](../architecture/ddia/README.md) and is cross-referenced here rather than duplicated.

## Subjects

| Subject | What it is | Lessons | Index |
| --- | --- | --- | --- |
| **Database Internals** | *Database Internals: A Deep Dive into How Distributed Data Systems Work* (Alex Petrov) - storage-engine internals (B-Trees, LSM trees, logging, compaction) through replication, partitioning, and consensus mechanics. | 16 | [database-internals/README.md](database-internals/README.md) |
| **SQL Performance Explained** | *SQL Performance Explained* (Markus Winand) - practical index and query-shape reasoning for predictable SQL performance: joins, ordering, clustering, and pagination. | 10 | [sql-performance-explained/README.md](sql-performance-explained/README.md) |
| **Seven Databases in Seven Weeks** | *Seven Databases in Seven Weeks* (Luc Perkins, Eric Redmond, Jim Wilson) - comparative tour of relational, document, wide-column, graph, and key-value systems for workload-driven database selection. | 9 | [seven-databases/README.md](seven-databases/README.md) |

A sensible path is to start with SQL Performance Explained for immediate query
skills, then go deeper into Database Internals, and finish with Seven Databases
to sharpen cross-model selection judgment.

See each subject's `README.md` for its concept index and progress, and the root
[SUMMARY.md](../SUMMARY.md) for the cross-domain overview.
