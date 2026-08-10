---
id: seven-databases/04
subject: seven-databases
title: "MongoDB: Document Modeling, Indexing, and Schema Flexibility Limits"
slug: mongodb-document-modeling
status: drafted
mastery:
seniority: mid
source: Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 4
prerequisites: [seven-databases/01, seven-databases/02]
created: 2026-08-10
updated: 2026-08-10
---

# MongoDB: Document Modeling, Indexing, and Schema Flexibility Limits

## TL;DR
MongoDB stores data as JSON-like documents (BSON) that can nest related data directly rather than splitting it across normalized tables, trading PostgreSQL's join-time correctness for read-time convenience when an application's dominant access pattern is "fetch one aggregate object, whole." Its schema flexibility is real and useful, but not free — it shifts consistency and structure decisions from the database (constraints, foreign keys) to the application, and denormalization creates its own update-consistency risks.

## The idea
PostgreSQL (`seven-databases/02`) normalizes data across tables and reassembles it at query time via joins. Many applications, though, naturally think in terms of a single aggregate object — a blog post with its comments, a product with its variants and reviews, a user profile with nested preferences — that is almost always read and written as one whole. Forcing that natural unit through relational normalization means a join (or several) on every read, even though the pieces never really vary independently.

MongoDB's document model lets you store that natural unit as one JSON-like document, so "fetch the whole thing" becomes a single lookup by ID instead of a multi-table join. The cost: documents can vary in shape from one to the next (no enforced schema by default, though MongoDB does support optional schema validation), and denormalized, embedded data can drift out of sync if the same fact is duplicated across multiple documents.

## How it works

### The document model, concretely
A blog post with embedded comments might look like:

```json
{
  "_id": "post_9182",
  "title": "Why Row Keys Matter",
  "author": { "name": "Dana Lee", "id": "user_42" },
  "tags": ["databases", "hbase"],
  "comments": [
    { "user": "user_88", "text": "Great explanation!", "created": "2026-08-09T10:00Z" },
    { "user": "user_12", "text": "What about salting?", "created": "2026-08-09T11:15Z" }
  ],
  "createdAt": "2026-08-08T09:00Z"
}
```

Fetching this post and every comment on it is one `findOne({_id: "post_9182"})` — no join required, because the comments are physically embedded in the same document. Compare this to the PostgreSQL equivalent in `seven-databases/02`, which would need a `posts` table joined to a `comments` table.

### Embedding vs. referencing — the central modeling decision
MongoDB gives you two ways to represent a relationship, and choosing between them is the document-modeling equivalent of HBase's row-key design (`seven-databases/03`) — get it wrong and either performance or correctness suffers.

**Embed** when the related data is (a) always accessed together with the parent, (b) bounded in size (a post has dozens of comments, not millions), and (c) doesn't need to be queried or updated independently of the parent very often. The blog post/comments example above is a good embedding candidate — assuming comment volume per post stays bounded (MongoDB documents have a 16MB size cap, which becomes a real constraint for unbounded embedded arrays like "every view event ever").

**Reference** (store an ID and look it up separately, application-side join) when the related data is large, shared across many parents, or updated independently. The `author` field above only embeds a name and ID snapshot — the full user profile lives in a separate `users` collection, referenced by `id`, because a user's bio might be edited and you don't want to update every post they ever wrote to reflect it.

**Worked example — the wrong call.** A team embeds a full `product` document (name, price, description) inside every `order` line item "for speed." Six months later, a product's price changes, and now every historical order that embedded the old price shows the *current* price wherever the UI happens to read from the embedded copy, not the price actually charged — a subtle correctness bug caused by denormalizing something that legitimately changes independently of the orders that reference it. The fix: embed only a point-in-time snapshot explicitly labeled as such (`priceAtOrderTime`), or reference the product by ID and accept the extra lookup.

### Indexing
MongoDB supports secondary indexes (unlike HBase's row-key-only design), including compound indexes, on any field or nested field — `db.posts.createIndex({"comments.user": 1})` lets you efficiently find all posts a given user commented on. This is closer to PostgreSQL's indexing flexibility than to HBase's rigidity, and it's a large part of why MongoDB supports more varied ad hoc query patterns than HBase does. The trade-off: as with any database, every index speeds reads on that field at the cost of slower writes (the index must be updated) and extra storage.

### Schema flexibility, and its real limits
Because MongoDB doesn't enforce a schema by default, two documents in the same collection can have different fields entirely — useful when different product categories genuinely need different attributes (a book has an ISBN, a shirt has a size, neither has both). But "schemaless" is not "structureless": application code still needs to agree, implicitly or via a schema-validation layer (MongoDB's optional `$jsonSchema` validators), on what shape to expect — otherwise you get "schema drift," where old documents lack a field a newer code path assumes exists, causing null-pointer-style bugs at read time instead of write-time constraint violations. This is the direct cost side of the schema-flexibility axis introduced in `seven-databases/01`: PostgreSQL catches a malformed write immediately; MongoDB (without validators) lets it through and the bug surfaces later, at read time, potentially far from where the bad write happened.

### Consistency and scaling model
A single MongoDB replica set has one primary (accepting writes) and secondaries (replicating asynchronously by default, though writes can request synchronous acknowledgment from a majority via write concern settings). Reads from the primary are strongly consistent; reads from secondaries (if allowed) can be stale — a tunable choice, similar in spirit to DynamoDB's tunable consistency (`seven-databases/07`). For horizontal write scaling beyond a single primary, MongoDB supports sharding by a chosen shard key, conceptually similar to HBase's row-key-driven region splitting (`seven-databases/03`) — pick the shard key so writes spread evenly and your dominant queries can target one or few shards, or you get the same "hot shard" problem HBase suffers from a bad row key.

## Pros
- Matches how many applications naturally think about their data (one aggregate, fetched whole), reducing join overhead for read-heavy, aggregate-shaped access patterns.
- Flexible schema accommodates genuinely varying document shapes without the friction of altering a rigid relational schema for every new attribute.
- Rich secondary indexing and a expressive query language keep ad hoc querying much closer to PostgreSQL's flexibility than HBase's rigidity.

## Cons
- Denormalized/embedded data can drift out of sync when the same fact is duplicated across documents and later changes — a correctness risk PostgreSQL's foreign keys and normalization structurally prevent.
- No enforced schema by default means structural mistakes surface at read time, in production, rather than at write time as a rejected constraint — schema validators mitigate but must be deliberately configured.
- Multi-document transactions exist but are more expensive and less idiomatic than MongoDB's document-at-a-time model; a workload that genuinely needs frequent multi-row ACID transactions across different documents fits PostgreSQL's model more naturally.

## Alternatives
- **CouchDB** (`seven-databases/05`) — also document-oriented, but built around multi-master replication and conflict resolution rather than MongoDB's single-primary model; a better fit when offline-first sync across many nodes is the dominant requirement.
- **PostgreSQL with JSONB** (`seven-databases/02`) — gets meaningful schema flexibility for a subset of columns while keeping full relational guarantees elsewhere; a common middle ground when only part of the data is genuinely variable-shaped.
- **DynamoDB** (`seven-databases/07`) — a managed, key-value-first alternative with a stricter access-pattern-driven design discipline and different operational trade-offs (no cluster to run, but partition-key design is far less forgiving).

## When to use it
Use MongoDB when the dominant access pattern is "fetch one aggregate object, whole," the object's shape genuinely varies across records or evolves quickly, and you don't need frequent multi-row ACID transactions spanning unrelated documents. It shines for content-management-style data (posts, profiles, catalogs) and rapid-iteration products where the schema is still settling.

## When NOT to use it
Avoid it when your data has many genuinely independent entities that need frequent, ad hoc joining and multi-row transactional guarantees (reach for PostgreSQL, `seven-databases/02`), or when unbounded array growth (comments, events) would blow past the document size limit — in that case, reference rather than embed, or reach for a database designed for unbounded append-heavy access like HBase (`seven-databases/03`). See `seven-databases/09` for the full framework.

## Key takeaways / mental model
MongoDB trades relational normalization for read-time convenience: embed what's always read together and bounded in size, reference what's shared, large, or independently updated — and remember that "schemaless" only moves structural enforcement from write-time (PostgreSQL) to read-time (your application code), it doesn't remove the need for structure.

## Self-check questions
1. Given a `users` collection where each user has an `orders` array embedded directly in their document, and order volume per user is unbounded and growing, what problem will you eventually hit, and how would you redesign it?
2. Explain the price-drift bug in the worked example above in your own words, and describe two different fixes with different trade-offs.
3. A team argues "MongoDB doesn't need a schema, so we don't need to agree on document shape across the team." What will go wrong, and how would you mitigate it without giving up MongoDB's flexibility entirely?
4. Given a workload that needs both (a) flexible per-item attributes and (b) strong multi-row transactional guarantees across many entities, would you reach for MongoDB, PostgreSQL with JSONB, or something else? Justify your answer.

## References
- Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 4: "MongoDB."
- See also: `seven-databases/01` (schema-flexibility axis), `seven-databases/05` (CouchDB's contrasting replication model), `ddia/02` (data models) for deeper background.
