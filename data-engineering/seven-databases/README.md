# Seven Databases in Seven Weeks (2nd Edition)

This subject gives you a comparative tour of major database models through
hands-on mental models instead of abstract taxonomy. You will see what each
database family is optimized for, which workloads fit naturally, and where each
choice creates operational or modeling friction. The end goal is better storage
selection decisions, not tool memorization.

**Source book:** *Seven Databases in Seven Weeks* - Luc Perkins, Eric Redmond, Jim Wilson (Pragmatic Bookshelf, 2018).

**Seniority baseline:** mid (lessons range junior->senior).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`seven-databases/<NN>`* (e.g. *"discuss `seven-databases/03`"*). Ordered by dependency: data-model framing first, then one concept per database family, then a synthesis for selection trade-offs.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Relational vs NoSQL framing and CAP-era trade-offs | mid | drafted | — | — | [lesson](lessons/01-relational-vs-nosql-framing.md) | — |
| 02  | PostgreSQL: relational modeling, constraints, and transactional strength | junior | drafted | — | — | [lesson](lessons/02-postgresql-relational-modeling.md) | — |
| 03  | HBase: wide-column modeling and access-pattern-first design | mid | drafted | — | — | [lesson](lessons/03-hbase-wide-column-modeling.md) | — |
| 04  | MongoDB: document modeling, indexing, and schema flexibility limits | mid | drafted | — | — | [lesson](lessons/04-mongodb-document-modeling.md) | — |
| 05  | CouchDB: replication-first documents and conflict-oriented workflows | mid | drafted | — | — | [lesson](lessons/05-couchdb-replication-first-documents.md) | — |
| 06  | Neo4j: graph modeling and traversal-centric query design | mid | drafted | — | — | [lesson](lessons/06-neo4j-graph-modeling.md) | — |
| 07  | DynamoDB: partition-key design, throughput units, and access constraints | senior | drafted | — | — | [lesson](lessons/07-dynamodb-partition-key-design.md) | — |
| 08  | Redis: in-memory data structures, caching roles, and persistence modes | mid | drafted | — | — | [lesson](lessons/08-redis-data-structures-and-persistence.md) | — |
| 09  | Cross-database comparison and workload-driven store selection | senior | drafted | — | — | [lesson](lessons/09-cross-database-selection.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` · `mid` · `senior` · `staff` · `principal` - the band whose job the concept anchors.

**Cross-subject prerequisites:** related background from `ddia/02` (data models), `ddia/10` (partitioning), and `database-internals/08` (engine trade-offs) sharpens the selection discussion.
