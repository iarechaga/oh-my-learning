---
id: ddia/04
subject: ddia
title: "Storage Engines: LSM-Trees and B-Trees"
slug: storage-engines
status: drafted
mastery:
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 3"
prerequisites: [ddia/02]
created: 2026-06-30
updated: 2026-06-30
---

# Storage Engines: LSM-Trees and B-Trees

## TL;DR
Databases use two primary storage engine families to manage data on disk: LSM-trees and B-trees. LSM-trees append data to logs and merge sorted files, which makes writes extremely fast. B-trees partition disk space into fixed-size pages and update them in place, providing excellent read performance.

## The idea
A database needs to do two things well: store data safely on disk, and find that data quickly when asked. The simplest database is just an append-only text file. While appending a new line is incredibly fast, retrieving a specific key requires a full scan of the file. To solve this read performance problem, we use indexes. An index is a separate structure built from the primary data to speed up lookups. Unfortunately, maintaining an index introduces a trade-off because every write must also update the index. Engineers designed two major classes of storage engines to navigate this trade-off. LSM-trees focus on write speed by keeping writes sequential. B-trees prioritize read speed by keeping data structured in fixed-size blocks.

Before diving into storage engines, make sure you understand the underlying data models described in [Data Models](../lessons/02-data-models.md).

## How it works
This section explains how both families organize and manage data on disk and in memory.

### Log-Structured Merge-Trees (LSM-Trees)
LSM-trees rely on a clean, append-only workflow that treats files as immutable once written. They combine three main components to manage data:

1. **Memtable**: An in-memory balanced tree (typically a red-black tree). When a write arrives, the database adds it to this memtable.
2. **SSTables (Sorted String Tables)**: Files on disk where keys are stored in sorted order. Once the memtable reaches a size threshold, the database writes its sorted keys to disk as a new SSTable file.
3. **Write-Ahead Log (WAL)**: An append-only log on disk. Because the memtable lives in volatile RAM, the database writes every transaction to this log immediately. If the database crashes, the log reconstructs the memtable.

As the database runs, disk space accumulates many SSTables. A background process runs **compaction** to merge these files and discard deleted or overwritten keys. Since SSTables are already sorted by key, compaction uses a highly efficient merge-sort algorithm.

To find a key, the engine searches the memtable first, then the most recent SSTables. To avoid scanning many SSTables for missing keys, the engine uses **Bloom filters**. A Bloom filter is a memory-efficient probabilistic data structure that can tell if a key is definitely not in an SSTable, preventing useless disk reads.

Popular examples of LSM-tree engines include LevelDB, RocksDB, Cassandra, and HBase.

### Page-Oriented Engines (B-Trees)
B-trees are the oldest and most widely used index structure. They divide the database into fixed-size blocks or pages, which are typically 4KB or 8KB. The database reads or writes an entire page at a time.

A B-tree has a single root page at the top. This page contains several keys and pointers to child pages. Each child page responsible for a continuous range of keys eventually leads down to the leaf pages. Leaf pages hold the actual data or references to where the data is stored.

Unlike LSM-trees, B-trees update data in place. When a write occurs, the database:
1. Appends the change to its Write-Ahead Log (WAL) on disk for crash recovery.
2. Finds the target page containing the key range.
3. Loads that page into memory, updates the value, and marks the page as dirty.
4. Flushes the dirty page back to its original location on disk later.

If a page runs out of space during a write, the engine splits it into two half-full pages and updates the parent page pointer. Relational databases like MySQL, PostgreSQL, Oracle, and SQL Server default to B-tree engines.

### Comparative Example
Suppose you update a record: `user_99 -> "Bob"`.

In an LSM-tree:
The database appends the change to its WAL and inserts it into the memtable. The write is complete. The database does not search for the old value.

In a B-tree:
The database appends the update to its WAL. It searches the index to find the page containing `user_99`, loads it, overwrites the old value in memory, and writes the entire page back to disk.

## Pros
- LSM-trees handle high-volume write workloads with superior throughput because they write sequentially.
- LSM-trees compress better and have less overhead, saving storage space on disk.
- B-trees provide predictable, low-latency point reads because lookups require loading a small, fixed number of pages.
- B-trees simplify transaction boundaries because each key exists in exactly one place in the index.

## Cons
- LSM-trees suffer from unpredictable response times during compaction because background merges compete for limited disk bandwidth.
- LSM-trees require expensive multi-file checks and Bloom filters to locate keys that are not present.
- B-trees suffer from high write amplification because they write entire pages to disk for tiny updates.
- B-trees experience page fragmentation over time as splits leave empty gaps in storage blocks.

## Alternatives
- **In-memory databases**: Systems like Redis keep all data in RAM, avoiding disk layouts entirely for active workloads.
- **Fractal Trees**: These structures buffer writes inside tree nodes, reducing write amplification while keeping a B-tree-like search hierarchy.

## When to use it
Choose an LSM-tree when your application writes constantly, reads are less frequent, and you need to maximize SSD lifespan by avoiding random writes. Choose a B-tree when your application requires fast point lookups, predictable latency, and stable transactional consistency.

## When NOT to use it
Do not use LSM-trees if your application requires highly consistent latency with zero write stalls, or if you need strong SQL transaction isolation. Reach for a page-oriented B-tree engine like PostgreSQL instead. Do not use B-trees if your write volume is so high that it saturates your disk bandwidth due to page overwrites. Reach for an LSM-tree engine like RocksDB or Cassandra in those cases.

## Key takeaways / mental model
Think of an LSM-tree as a sorted stack of paper where you write new notes on a notepad in memory, then periodically bind them into neat, sorted booklets on your shelf. Compaction is the librarian who merges duplicate or deleted entries from old booklets into a single, clean booklet. Think of a B-tree as a large, pre-allocated binder index. To update a page, you find the exact sheet, erase the old value, and write the new one. If the sheet gets too full, you split it into two sheets and update the index pointers.

## Self-check questions
1. Why does a B-tree require a write-ahead log (WAL) for safety, while an LSM-tree can recover using its memtable write-ahead log?
2. How does write amplification affect SSD longevity, and which engine family generally handles this better?
3. What is the role of a Bloom filter in an LSM-tree storage engine, and how does it optimize reads?
4. What happens when B-tree pages split, and why does this cause storage fragmentation?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 3: Storage and Retrieval.
- Prerequisites: [02-data-models.md](../lessons/02-data-models.md)
