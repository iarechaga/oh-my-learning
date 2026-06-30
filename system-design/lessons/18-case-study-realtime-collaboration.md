---
id: system-design/18
subject: system-design
title: "Case Study: Real-Time Collaboration (Google Docs)"
slug: case-study-realtime-collaboration
status: drafted
mastery:
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 13"
prerequisites: [system-design/16, ddia/08]
created: 2026-06-30
updated: 2026-06-30
---

# Case Study: Real-Time Collaboration (Google Docs)

## TL;DR
Designing a collaborative editor requires synchronizing concurrent edits from many users over high-latency networks. This lesson covers how to resolve conflicting updates using Operational Transformation and Conflict-free Replicated Data Types. We explore how WebSockets, snapshot-based persistent storage, and stateless document servers combine to form a stable real-time editing architecture.

## The idea
Imagine three people writing a document together at the exact same moment. If User A deletes a word at index ten while User B inserts a word at the same index, their local screens immediately drift out of sync. Traditional databases reject concurrent changes or let the last write win, which destroys the user experience. Real-time collaboration systems must accept all user actions instantly on their local screens and resolve conflicts in the background.

This problem is a real-world instance of multi-leader replication, a concept examined in ddia/08. In this setting, every user acts as a local replication leader. They make local modifications immediately without waiting for database confirmation, then propagate changes asynchronously. The system must guarantee that all clients eventually converge on the exact same document state, regardless of network delays or out-of-order message delivery.

## How it works

### 1. Requirements

#### Functional Requirements
- **Real-Time Collaboration**: Many users can edit a single text document concurrently with low latency.
- **Presence Tracking**: Users can see who is currently viewing the document, along with their active selection and cursor positions.
- **Document Management**: Users can create, rename, delete, and share documents with specific permissions (owner, editor, viewer).
- **Revision History**: The system stores previous versions, letting users review changes and restore older states.
- **Offline Support**: Users can continue typing when disconnected, then sync their changes back to the cloud when they reconnect.

#### Non-Functional Requirements
- **Low Latency**: Local feedback must be instantaneous (under 50 milliseconds). Remote edits should propagate to other screens within 200 milliseconds.
- **Eventual Consistency**: All collaborators must eventually see the exact same document characters in the exact same order.
- **Durability**: Edits must never be lost. The system must persist document states reliably.
- **High Concurrency**: The design must support up to one hundred concurrent editors on a single document, and handle millions of active documents globally.

### 2. Estimations
Let's estimate the scale for a platform with 10 million Daily Active Users (DAU).

- **Active Sessions**: Assume 10% of DAU are online at peak hours, resulting in 1,000,000 concurrent sessions.
- **Active Documents**: If each active user works on a shared document with an average of 4 participants, we have 250,000 active documents at peak.
- **Operation Rate**: An average user types at 3 characters per second, which generates 3 edit operations per second.
- **Write Operations (Ingress)**: 1,000,000 active users typing at 3 ops/sec generates 3,000,000 operations per second at peak.
- **Data Size per Operation**: A single keystroke operation payload (index, character, operation type, user metadata) is roughly 200 bytes.
- **Ingress Bandwidth**: 3,000,000 ops/sec * 200 bytes = 600 MB/s.
- **Read Operations (Egress)**: Every edit must propagate to all other users in the session. If average session size is 4, each edit is broadcast to 3 peers. This means 3,000,000 edits/sec * 3 broadcasts = 9,000,000 operations/sec egress.
- **Egress Bandwidth**: 9,000,000 ops/sec * 200 bytes = 1.8 GB/s.

### 3. API Sketch
We use HTTP for metadata operations and WebSockets for low-latency bidirectional edit streams.

#### HTTP Endpoints
- `POST /api/v1/documents`: Creates a new document. Returns `doc_id`.
- `GET /api/v1/documents/{doc_id}`: Retrieves document metadata and a link to the latest snapshot.
- `POST /api/v1/documents/{doc_id}/share`: Manages access permissions. Payload: `{user_id: string, role: "editor" | "viewer"}`.

#### WebSocket Events (Duplex channel)
- `join_session(doc_id, user_id, last_seen_version)`: Client requests to join an active editing room.
- `send_operation(doc_id, operation)`: Client submits an edit operation.
- `broadcast_operation(doc_id, operation)`: Server propagates an operation to other clients.
- `presence_update(doc_id, cursor_position)`: Client shares cursor index or text selection.

### 4. Document and Operation Data Model

#### Operational Transformation (OT) Representation
In OT, we don't send the entire document state. We transmit discrete operations that mutate the document. A basic text operation contains three primitives:

- `Insert(position, character)`: Adds a character at the specified index.
- `Delete(position)`: Removes the character at the index.
- `Retain(count)`: Skips a specific number of characters.

Here is a typical client-to-server operation payload:

```json
{
  "doc_id": "doc_99a8f",
  "user_id": "user_45c",
  "client_version": 14,
  "type": "insert",
  "position": 12,
  "value": "h"
}
```

#### CRDT Representation
Instead of relying on relative indexes, Conflict-free Replicated Data Types (CRDTs) assign a globally unique, immutable identifier to every single character. The document is modeled as an ordered list of character structures rather than a raw string.

```json
{
  "id": {
    "site_id": "user_45c",
    "logical_clock": 105,
    "position_fraction": [0.15, 0.2]
  },
  "value": "h",
  "is_deleted": false
}
```

The `position_fraction` field uses fractional indexing. It allows inserting a new character between any two existing characters without shifting or recalculating any other character's index.

### 5. High-Level Architecture
The system separates heavy, real-time collaboration sessions from metadata management.

```
+--------------------------------------------------------------+
|                         Web Browsers                         |
|   [Client A]             [Client B]             [Client C]   |
+-------+----------------------+----------------------+--------+
        |                      |                      |
        | WebSocket Connection |                      |
        v                      v                      v
+--------------------------------------------------------------+
|                  API Gateway / Load Balancer                 |
|            (Routes WebSocket sessions to targets)            |
+------------------------------+-------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                     Collaboration Servers                    |
|             (Stateful, sharded by Document ID)               |
|  +------------------------+      +------------------------+  |
|  |     [Collab Server 1]  |      |     [Collab Server 2]  |  |
|  |  * Handles Doc 01-100  |      |  * Handles Doc 101-200 |  |
|  |  * In-memory OT Engine |      |  * In-memory OT Engine |  |
|  +-----------+------------+      +-----------+------------+  |
+--------------|-------------------------------|---------------+
               |                               |
               v                               v
+--------------------------------------------------------------+
|                      Pub/Sub Message Bus                     |
|           (Redis / Kafka: coordinates session state)         |
+--------------+-------------------------------+---------------+
               |                               |
               |                               |
               v                               v
+------------------------------+ +-----------------------------+
|      Document Service        | |      Presence Service       |
|  (Stateless metadata, auth)  | |   (Tracks active editors)   |
+--------------+---------------+ +--------------+--------------+
               |                               |
               v                               v
+------------------------------+ +-----------------------------+
|    Document Metadata DB      | |     In-Memory Cache         |
|  (PostgreSQL: Users, Roles)  | |  (Redis: ephemeral cursors) |
+------------------------------+ +-----------------------------+
               |
               v
+--------------------------------------------------------------+
|                     Distributed NoSQL DB                     |
|         (Cassandra/MongoDB: Operations log & snapshots)       |
+--------------------------------------------------------------+
```

### 6. Dynamic Walkthrough: OT vs CRDT in Action

To understand how these concepts solve concurrency, let's examine a scenario where two users edit the same string simultaneously.

#### The Scenario
- **Initial Document State**: `"cat"`
- **User A's Intention**: Append `"s"` to make `"cats"`. This generates: `Op A = Insert(position: 3, value: "s")`.
- **User B's Intention**: Prepend `"h"` to make `"hcat"`. This generates: `Op B = Insert(position: 0, value: "h")`.

#### Operational Transformation (OT) Resolution
In OT, clients apply operations locally immediately, then send them to a central server. The server acts as the single source of truth. It tracks the document version and transforms incoming operations against concurrent ones.

1. User A applies `Op A` locally. Local state becomes `"cats"`. They send `Op A` to the server at version 0.
2. User B applies `Op B` locally. Local state becomes `"hcat"`. They send `Op B` to the server at version 0.
3. The server receives `Op A` first. It accepts it, updates its master state to `"cats"` (version 1), and broadcasts `Op A` to User B.
4. The server receives `Op B` next. However, the server is now at version 1. It detects that `Op B` was created at version 0, meaning it's concurrent with `Op A`.
5. The server runs the transformation function: `Transform(Op B, Op A)`.
   - Since `Op A` inserted `"s"` at index 3, and `Op B` wants to insert `"h"` at index 0, the position of `Op B` remains unaffected.
   - Our transformed operation `Op B'` is still `Insert(position: 0, value: "h")`.
   - Applying `Op B'` to the master state yields `"hcats"` (version 2).
   - Server then broadcasts `Op B'` to User A.
6. The server transforms `Op A` relative to `Op B` for User B: `Transform(Op A, Op B)`.
   - Since `Op B` inserted a character at index 0, all subsequent character positions shift right by one.
   - Our transformed operation `Op A'` becomes `Insert(position: 4, value: "s")`.
   - Client B receives this `Op A'` from the server.
7. User A receives `Op B'` and applies it. State: `"cats"` -> `"hcats"`.
8. User B receives `Op A'` and applies it. State: `"hcat"` -> `"hcats"`.
9. Both clients converge on `"hcats"`.

#### CRDT Resolution
In CRDT, there is no need for central transformation logic. Every character has a globally ordered, unique position ID.

1. The initial characters are assigned fractional IDs:
   - `'c'` -> `0.1`
   - `'a'` -> `0.2`
   - `'t'` -> `0.3`
2. User A inserts `"s"` after `'t'`. The client generates a new fractional ID between `0.3` and `1.0`, say `0.4`.
   - `Op A = Insert(id: 0.4, value: "s")`
3. User B inserts `"h"` before `'c'`. The client generates a new fractional ID between `0.0` and `0.1`, say `0.05`.
   - `Op B = Insert(id: 0.05, value: "h")`
4. Both operations are sent across the network. Because the identifiers are absolute and immutable, the arrival order doesn't matter.
5. Every client merges the updates and sorts the characters by their position IDs:
   - `0.05` -> `"h"`
   - `0.10` -> `"c"`
   - `0.20` -> `"a"`
   - `0.30` -> `"t"`
   - `0.40` -> `"s"`
6. The resulting string is `"hcats"` on all nodes, with zero coordinate transformation.

### 7. How it Scales

#### Stateful Collaboration Servers
To handle OT transformations efficiently, we must route all users editing the same document to the same physical collaboration server. This stateful architecture avoids costly database lookups for every keystroke. We shard document sessions across a pool of servers. A central routing layer (such as consistent hashing or a registry using Consul) maps `doc_id` to a specific server instance.

#### Event Pub/Sub
When a document session gets too large, or when we need to distribute events across multiple nodes for high availability, we use a low-latency pub/sub system like Redis. The collaboration servers subscribe to document channels to propagate updates.

#### Snapshotting
Saving every single keystroke to a database is too expensive. The collaboration server keeps the active document in memory. Every few seconds, or after a specific number of operations, the server flushes a snapshot of the document state to a NoSQL database (Cassandra or MongoDB). Old operation logs can then be pruned or archived to cold storage, keeping the active operation chain short.

### 8. Bottlenecks and Edge Cases

#### High-Concurrency Hotspots
If hundreds of users edit the exact same paragraph simultaneously, the OT transformation load spikes. The server can become a bottleneck. We solve this by implementing rate-limiting on the client side. Instead of sending a network packet for every single keystroke, the client batches operations locally and flushes them every 100-200 milliseconds.

#### Offline Re-syncing
When a user disconnects, goes offline, writes several pages, and reconnects, they bring a massive batch of operations.
- **In OT**: The client must track its base version. When it reconnects, it sends its operations. If the server has moved forward too many versions, transforming this giant backlog gets expensive. The server might have pruned its transformation history, requiring the client to fetch a full fresh snapshot, run a local diff, and merge the changes.
- **In CRDT**: Re-sync is easier. The offline client simply uploads its locally created character structures. Since each character has a unique ID, the receiving server inserts them directly into the document list. The main challenge here is structural divergence. If two offline users edited the same sentence, the merged result can look like interleaved gibberish. We mitigate this using semantic merge heuristics.

#### Ephemeral Presence
Broadcasting cursors and text selections generates massive network traffic. Cursors don't require persistence. If a cursor update packet gets dropped, it's immediately superseded by the next one. We route cursor updates through ephemeral Redis channels, bypassing the primary database completely.

## Pros

- **Interactive User Experience**: Collaborators see updates immediately, making the product feel fast and responsive.
- **Offline Resilience**: Using local data structures lets users continue working during network outages.
- **Accurate History**: Storing the log of operations provides an audit trail, letting users roll back to any historical character state.
- **Bandwidth Efficiency**: Sending individual edit operations is far cheaper than transmitting the entire document text on every change.

## Cons

- **Extremely High Complexity**: Writing correct OT or CRDT merge algorithms is notoriously difficult. Edge cases are hard to replicate and test.
- **Stateful Memory Overhead**: Collaboration servers must keep active documents in memory. If a node crashes, active sessions must be re-routed, and state must be rebuilt from the database.
- **Interleaving Errors**: Under heavy concurrent edits, text characters can interleave incorrectly, creating mixed words that require manual cleanup.
- **Storage Growth**: Retaining every single operation log for historical tracking leads to massive storage requirements over time.

## Alternatives

- **Pessimistic Locking**: The system locks the document or paragraph when a user starts typing. Other users must wait until the lock is released. This avoids conflict resolution completely, but it ruins the real-time collaborative experience.
- **Differential Synchronization**: The client and server periodically exchange complete document diffs using patch algorithms. This is simpler to implement than OT or CRDT, but it consumes more bandwidth and struggles with high-frequency updates.

## When to use it
- Use this architecture for rich, interactive, multi-user productivity tools where immediate visual feedback is essential. Examples include document editors, collaborative digital whiteboards, design tools, and shared spreadsheets.

## When NOT to use it
- Avoid this design for systems where correctness and strict ordering are more important than real-time synchronization. Examples include financial transaction engines, inventory management, or medical records systems. For these use cases, traditional ACID transactions and optimistic concurrency control are better choices.

## Key takeaways / mental model
Think of real-time collaboration as a multi-leader database replication problem where each browser is a local leader.
- **Operational Transformation (OT)** is a centralized model. It keeps the data model simple (a raw string) but requires a smart, stateful coordinator server to transform index positions dynamically.
- **Conflict-free Replicated Data Types (CRDTs)** are decentralized models. They make the data model complex (every character is an object with a fractional ID) but simplify synchronization since updates can be merged in any order without a central coordinator.

## Self-check questions

1. Why do traditional databases using optimistic concurrency control fail in a real-time collaborative editing environment?
2. How does Operational Transformation handle index shifting when two concurrent operations occur at different positions?
3. What is fractional indexing in CRDTs, and how does it prevent index recalculation when inserting characters?
4. How do stateless document services and stateful collaboration servers divide their responsibilities?
5. Why are document snapshots necessary in an OT-based collaboration system, and how do they impact storage cleanups?
6. How does a client-side edit batching interval of 150ms protect the collaboration server during high-concurrency spikes?

## References
- *System Design Guide for Software Professionals* (Sinha & Chopra), Chapter 13.
- *Designing Data-Intensive Applications* (Martin Kleppmann), Chapter 5 (Multi-Leader Replication) and Chapter 8 (Conflict-free Replicated Data Types).
