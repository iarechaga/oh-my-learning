# Seven Databases in Seven Weeks

A comparative tour of major database models, concept by concept. This subject builds
the vocabulary to reason about storage selection as a workload-fit decision rather than
a technology preference: name the read/write ratio, consistency needs, query shape, and
scale trajectory first, and let those answers narrow the field of candidate databases.

Progress note: all 9 lessons are `drafted`; none have been discussed yet, so mastery is
pending across the board and no weak spots are recorded yet. This page will gain depth
(especially on the concepts the learner finds hard) as discussions happen - the last
section below will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom: the
relational/NoSQL and CAP framing first, then one concept per database family (PostgreSQL,
HBase, MongoDB, CouchDB, Neo4j, DynamoDB, Redis), then a synthesis that compares all
seven and gives a concrete selection framework.

## Framing

- **[seven-databases/01] Relational vs NoSQL framing and CAP-era trade-offs** - the
  relational model's single-node-centric ACID guarantees versus the several distinct
  NoSQL families (key-value, wide-column, document, graph) that each relax different
  guarantees for scale or shape fit; the CAP theorem names the CP-vs-AP choice every
  distributed database makes under partition, and schema rigidity is tracked as a
  separate, orthogonal axis. ([lesson](lessons/01-relational-vs-nosql-framing.md))

## The seven databases

- **[seven-databases/02] PostgreSQL: relational modeling, constraints, and
  transactional strength** - the relational anchor point: typed columns, foreign keys,
  and check constraints push correctness enforcement into the database itself; ACID
  transactions guarantee multi-row writes are all-or-nothing; scaling is vertical-first,
  with horizontal write-scaling needing extensions or manual sharding.
  ([lesson](lessons/02-postgresql-relational-modeling.md))
- **[seven-databases/03] HBase: wide-column modeling and access-pattern-first design** -
  a distributed, sorted map keyed by row key, scaling writes natively via region
  splitting; row-key design (and avoiding hot regions via salting) is the entire game,
  since only exact-key lookups and sorted-range scans are efficient; strongly consistent
  per row (CP). ([lesson](lessons/03-hbase-wide-column-modeling.md))
- **[seven-databases/04] MongoDB: document modeling, indexing, and schema flexibility
  limits** - JSON-like documents let a natural aggregate (a post with its comments) be
  fetched whole instead of joined at query time; the central modeling decision is embed
  (bounded, always-together data) vs. reference (large, shared, independently-updated
  data); schema flexibility shifts structural enforcement from write-time to read-time.
  ([lesson](lessons/04-mongodb-document-modeling.md))
- **[seven-databases/05] CouchDB: replication-first documents and conflict-oriented
  workflows** - multi-master replication lets any node (including mobile/offline
  devices) accept writes independently; conflicting concurrent edits are surfaced
  explicitly via `_conflicts` rather than silently resolved, an AP-leaning design built
  for offline-first sync. ([lesson](lessons/05-couchdb-replication-first-documents.md))
- **[seven-databases/06] Neo4j: graph modeling and traversal-centric query design** -
  index-free adjacency stores relationships as direct physical pointers, so multi-hop
  traversal cost tracks the size of the traversed neighborhood, not the whole database;
  Cypher's pattern-matching syntax mirrors the relationship shape being queried; ACID,
  CP-leaning, write-scaling bounded by a single primary.
  ([lesson](lessons/06-neo4j-graph-modeling.md))
- **[seven-databases/07] DynamoDB: partition-key design, throughput units, and access
  constraints** - a fully-managed, partition-key-hashed store demanding
  access-pattern-first design: every query pattern must be known upfront and mapped to
  the base table's key or a Global Secondary Index; a poorly-chosen partition key causes
  silent throttling under load; tunable eventual/strong consistency per read.
  ([lesson](lessons/07-dynamodb-partition-key-design.md))
- **[seven-databases/08] Redis: in-memory data structures, caching roles, and
  persistence modes** - typed, atomic data structures (strings, lists, sets, sorted
  sets, hashes) eliminate whole classes of read-modify-write races; primarily a caching
  layer (cache-aside pattern with TTLs) but usable as a lightweight queue or primary
  store if RDB/AOF persistence and replication are deliberately configured for
  durability. ([lesson](lessons/08-redis-data-structures-and-persistence.md))

## Synthesis

- **[seven-databases/09] Cross-database comparison and workload-driven store
  selection** - a four-dimension framework (read/write ratio, consistency needs, query
  shape, scale/ops trajectory) for choosing among the seven systems, with worked
  scenarios (SaaS invoicing, IoT telemetry, social recommendations, offline field data,
  evolving product catalogs) and the observation that combining multiple stores per
  access pattern is the normal, not the exceptional, real-world architecture.
  ([lesson](lessons/09-cross-database-selection.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
