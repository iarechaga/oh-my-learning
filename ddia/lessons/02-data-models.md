---
id: ddia/02
subject: ddia
title: "Data Models: Relational, Document, and Graph"
slug: data-models
status: drafted
mastery:
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 2
prerequisites: [ddia/01]
created: 2026-06-30
updated: 2026-06-30
---

# Data Models: Relational, Document, and Graph

## TL;DR
The data model you choose shapes how you think about the problem and decides which operations are easy and which are painful. Relational models excel at many-to-many relationships via joins, document models excel at self-contained one-to-many trees with great locality, and graph models excel when relationships themselves are the main thing you query.

## The idea
A data model is a layer of abstraction: the application sees objects, which are mapped down to a model (tables, documents, or a graph), which is mapped down to bytes on disk. The model at each layer determines what is natural to express. Real data is full of relationships - one-to-one, one-to-many, and many-to-many - and the three major models differ mostly in how gracefully they handle each shape. Picking the wrong model means fighting your database. This lesson builds on the reliability/scalability framing in [01-reliability-scalability-maintainability.md](01-reliability-scalability-maintainability.md), since model choice affects both.

## How it works

### Relational
Data lives in **relations** (tables) made of **tuples** (rows), queried with SQL. Relationships are expressed with foreign keys and resolved at query time with **joins**, which makes many-to-many relationships natural. The friction point is the **object-relational impedance mismatch**: application objects (often nested and graph-like) do not map cleanly onto flat tables, which is why object-relational mappers (ORMs) exist.

### Document
Data lives in self-contained **documents** (JSON/BSON), for example a résumé with nested `positions` and `education` arrays. Strengths:
- **Locality**: the whole tree is fetched in one read, no joins needed for the nested parts.
- **Schema flexibility** (schema-on-read): you can add fields without a migration.
- **Natural one-to-many**: nesting *is* the relationship.

Weaknesses: many-to-many relationships and joins are awkward. If many documents need to reference the same shared entity, you either denormalize (and risk inconsistency) or perform joins in application code, which the database would otherwise optimize for you. Deeply nested updates can also be clumsy.

### Graph
Data lives as **vertices** (nodes) and **edges** (relationships). Two common flavors: the **property graph** (Neo4j, queried with Cypher) and the **triple-store / RDF** model (queried with SPARQL). Graphs shine when many-to-many relationships dominate and the connections are first-class: social networks (who follows whom), road networks (shortest path), or recommendation graphs. A query like "friends of friends who live in Berlin" is a natural traversal in a graph and a painful pile of joins in SQL.

### Schema-on-write vs schema-on-read
Relational databases enforce a schema when data is written (**schema-on-write**, like static typing). Document stores typically interpret structure when data is read (**schema-on-read**, like dynamic typing). Schema-on-read is flexible for heterogeneous or evolving data but pushes the burden of handling inconsistent shapes onto application code.

## Pros
Focusing on the **document model** (the main modern contrast to relational):
- Excellent read locality for data that is loaded as a unit.
- Flexible, migration-free schema evolution.
- Maps cleanly to application objects, reducing impedance mismatch for tree-shaped data.

## Cons
- Many-to-many relationships and joins are weak; you reinvent joins in application code.
- Schema-on-read can hide data-quality problems until runtime.
- References to shared data are not enforced, so consistency is the application's job.

## Alternatives
- **Relational model** - mature, general-purpose, strong at many-to-many via joins, enforces a schema on write. Prefer it when relationships are rich and you want the database to optimize joins.
- **Graph model** - best when *everything* is many-to-many and traversal is the core query pattern; far more expressive than joins for deep, variable-length relationships, but a heavier tool for plain tabular data.
- Note that the models are converging: relational databases now support JSON columns, and some document databases add limited joins.

## When to use it
Choose a **document** model when your data is a self-contained tree that is usually loaded together and relationships are mostly one-to-many (a product with its variants, an invoice with line items). Choose **relational** when you have significant many-to-many relationships and want joins and a strong schema. Choose **graph** when the relationships between entities are themselves the primary thing you query.

## When NOT to use it
Do not force a document model onto highly interconnected, many-to-many data; you will end up writing slow, buggy joins by hand. Do not force a rigid relational schema onto a naturally hierarchical document that you always read whole and never query across. And do not reach for a dedicated graph database for simple tabular data that a couple of relational tables would handle - the operational overhead is not worth it.

## Key takeaways / mental model
A data model is an abstraction that makes some operations easy and others hard, so match it to your relationship shapes. One-to-many trees loaded together favor documents; many-to-many favors relational or graph; relationship-heavy traversal favors graph. Remember the axis of schema-on-read (flexible, interpreted late) versus schema-on-write (enforced, validated early).

## Self-check questions
1. What is the object-relational impedance mismatch, and what tool exists to paper over it?
2. Give a concrete situation where the document model hurts you, and explain why.
3. For a heavily many-to-many dataset, how do the relational and graph models differ in how they let you express queries?
4. Contrast schema-on-read with schema-on-write, and relate each to static versus dynamic typing.

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 2.
- Prerequisite: [01-reliability-scalability-maintainability.md](01-reliability-scalability-maintainability.md).
