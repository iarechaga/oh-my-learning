---
id: seven-databases/05
subject: seven-databases
title: "CouchDB: Replication-First Documents and Conflict-Oriented Workflows"
slug: couchdb-replication-first-documents
status: drafted
mastery:
seniority: mid
source: Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 5
prerequisites: [seven-databases/01, seven-databases/04]
created: 2026-08-10
updated: 2026-08-10
---

# CouchDB: Replication-First Documents and Conflict-Oriented Workflows

## TL;DR
CouchDB is a document database, like MongoDB (`seven-databases/04`), but built around a fundamentally different priority: multi-master, offline-friendly replication between any two nodes (server-to-server, or server-to-mobile-device), with conflicts surfaced explicitly rather than resolved automatically behind the scenes. It is an AP-leaning system by design — availability and replication convergence come first, and the application is expected to participate in conflict resolution.

## The idea
MongoDB's replica set model (`seven-databases/04`) has one primary accepting writes at a time — simple to reason about, but it assumes a mostly-connected cluster. CouchDB was designed for a harder problem: what if nodes are *routinely* disconnected — a mobile app that syncs when it finds WiFi, a field device that uploads once a day, two data centers on opposite sides of an unreliable link — and any of them might accept writes while disconnected from the others?

CouchDB's answer is **multi-master replication**: every CouchDB node (including embedded/mobile variants like PouchDB) can accept writes independently, and any two nodes can replicate with each other in either direction, at any time, in any topology (not just "leaf syncs with a central server" — peer-to-peer sync between two phones works the same way). The unavoidable consequence of letting any node write independently is that the *same document* can be edited differently on two disconnected nodes before they sync — CouchDB doesn't pretend this can't happen; it detects it, keeps both versions, and hands the conflict to the application to resolve.

## How it works

### Documents and revisions
Like MongoDB, a CouchDB document is a JSON object with a unique `_id`. Unlike MongoDB, every document also carries a `_rev` (revision) field, e.g. `3-a8f9c1...`, that changes on every update. Reads and writes are always scoped to a specific revision — a write must specify the revision it's updating *from*, and CouchDB rejects the write (a `409 Conflict`) if that revision is no longer current, i.e., if someone else already wrote a newer version. This is optimistic concurrency control, and it's the same mechanism (in spirit) that keeps a single node's edits from silently overwriting each other, before replication is even involved.

### Multi-master replication, concretely
**Worked example.** A field inspection app runs on tablets that are offline most of the day. An inspector opens record `site_204` (revision `4-abc...`) on Tablet A at 9am and edits the "condition" field. A colleague, also offline, opens the *same* record (still at revision `4-abc...`, since neither device has synced) on Tablet B at 9:15am and edits the "notes" field. Both tablets sync to the central CouchDB server that evening. Both writes are legitimate — from each device's perspective, it made the one authoritative edit to a document at revision `4`. CouchDB cannot know which edit should "win," so it keeps *both* as conflicting revisions (say `5-def...` and `5-ghi...`), picks one deterministically as the "winner" for default reads (so the app doesn't break), but flags the document as `_conflicts` so the application can detect and reconcile them explicitly — e.g., merge both the condition and notes changes, since they touched different fields.

This is the central design choice this lesson tests understanding of: CouchDB does **not** silently pick a "correct" merge (there often isn't one, semantically) — it makes the conflict visible and puts resolution in the hands of code that understands the domain, rather than a generic last-write-wins rule that could silently discard real work.

### Why not just "last write wins"?
A simpler alternative — discard the loser, keep the most recent timestamp's write — is exactly what many AP-leaning systems (including DynamoDB by default, `seven-databases/07`) do, and it's cheaper to reason about. CouchDB's designers judged that for a lot of real offline-sync workloads (field data collection, personal note-taking apps, collaborative documents), silently discarding one user's edit is worse than surfacing a conflict for the application (or the user) to resolve deliberately — especially because "most recent timestamp" is itself unreliable across devices with unsynchronized clocks. The cost is that application code must actually handle the `_conflicts` case; a naive app that ignores it will show only the "winning" revision and silently lose the other edit anyway, which defeats the purpose.

### The replication protocol
CouchDB replication works by comparing each side's list of `(doc_id, revision tree)` and exchanging only the deltas — documents or revisions the other side doesn't have yet. This is designed to be cheap and resumable over unreliable networks (a sync can be interrupted and resumed without corrupting state), and it works identically whether replicating between two full CouchDB servers or between a mobile PouchDB instance and a central server — there is no special "client sync protocol" distinct from "server-to-server replication"; it's the same mechanism at every scale, which is a deliberate simplicity choice.

### Views: how you query a schemaless document store without joins
Like MongoDB, CouchDB documents have no fixed schema. Unlike MongoDB's flexible ad hoc query language, CouchDB's primary query mechanism is **map/reduce views**: you write a JavaScript (or other language) `map` function that emits key-value pairs for each document, and CouchDB builds and incrementally maintains an index (a B-tree) over the emitted keys.

**Worked example.** To query "all inspection records by site, ordered by inspection date," a view's map function might be:
```javascript
function(doc) {
  if (doc.type === 'inspection') {
    emit([doc.site_id, doc.inspected_at], doc.condition);
  }
}
```
CouchDB indexes the emitted `[site_id, inspected_at]` keys, and querying the view with a key range returns matching documents efficiently — conceptually close to HBase's range-scan-over-sorted-keys model (`seven-databases/03`), except the "key" here is derived by your own function rather than being the row's primary identifier, and the index updates incrementally as documents change rather than needing a full rebuild.

### Consistency model
CouchDB is deliberately AP-leaning per the CAP framing in `seven-databases/01`: every node accepts reads and writes independently, even fully disconnected from every other node, and consistency across nodes is achieved *eventually*, through replication, with conflicts surfaced rather than silently resolved. This is the opposite operational posture from HBase's strong per-row consistency (`seven-databases/03`) — CouchDB would rather have every node stay fully available and reconcile later than have any node refuse a write while partitioned.

## Pros
- Multi-master, resumable replication over unreliable networks makes it a strong, well-tested fit for offline-first and edge/mobile applications where connectivity cannot be assumed.
- Conflicts are surfaced explicitly rather than silently resolved, avoiding the class of bugs where a "smart" automatic merge silently discards legitimate work.
- The same replication mechanism works identically from mobile client to server and server to server, simplifying the sync architecture rather than needing bespoke client-sync logic.

## Cons
- Map/reduce views are less flexible than an ad hoc query language (MongoDB's query API or SQL) — a new query pattern often means writing and deploying a new view, then waiting for it to index, rather than an ad hoc query against existing data.
- Applications must actively handle `_conflicts` for correctness; a team that doesn't design for this from the start will silently lose data on conflicting concurrent edits, exactly the failure mode CouchDB is trying to make visible instead of hidden.
- Weaker fit than HBase or DynamoDB for very high-throughput, single-writer-style workloads where multi-master conflict resolution is pure overhead you don't need.

## Alternatives
- **MongoDB** (`seven-databases/04`) — a simpler single-primary replication model with a much richer ad hoc query language; the right choice when offline multi-master sync isn't actually a requirement.
- **DynamoDB** (`seven-databases/07`) — also AP-leaning under partition, but resolves conflicts with last-write-wins or vector-clock-based strategies by default rather than surfacing them for explicit application handling; appropriate when automatic resolution is acceptable for the data in question.
- **A dedicated sync engine on top of a different database** — some teams implement CouchDB-style conflict-aware sync manually on top of PostgreSQL or another store when they need it for only one part of the system, at higher engineering cost but without adopting CouchDB's full model.

## When to use it
Reach for CouchDB when your application genuinely needs offline-capable, multi-master replication — mobile/edge devices that write independently and sync intermittently, or peer-to-peer data sharing — and your domain can meaningfully resolve conflicting concurrent edits (or tolerate surfacing them to the user).

## When NOT to use it
Avoid it when there's a natural single point of write authority (most conventional web applications), when you need a rich ad hoc query language over evolving query needs, or when your team isn't prepared to actually implement conflict-resolution logic (in which case CouchDB's conflict safety net provides no real benefit over a simpler last-write-wins system). See `seven-databases/09` for the comparison framework.

## Key takeaways / mental model
CouchDB's entire design centers on one bet: connectivity cannot be assumed, so every node must be able to write independently, and the price of that bet is that conflicts are real and must be handled explicitly rather than wished away. If your system doesn't actually have disconnected, independently-writing nodes, you're paying CouchDB's conflict-handling cost for a problem you don't have.

## Self-check questions
1. Walk through the field-inspection worked example and explain, step by step, why CouchDB cannot automatically produce a single "correct" merged document in that scenario.
2. Why might "last write wins" (as many AP systems default to) be actively worse than CouchDB's explicit-conflict approach for some workloads, and actively better for others? Give one example of each.
3. Compare CouchDB's map/reduce views to HBase's row-key range scans (`seven-databases/03`). What do they have in common, and where do they diverge?
4. A team is building a note-taking app that syncs across a user's phone, tablet, and laptop, sometimes offline for days. Would you reach for CouchDB or MongoDB, and what specific requirement drives that choice?

## References
- Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 5: "CouchDB."
- See also: `seven-databases/01` (CAP framing), `seven-databases/04` (MongoDB's contrasting single-primary model), `ddia/10` (partitioning and replication) for deeper background.
