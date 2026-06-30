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
Databases use two primary storage engine families to manage data on disk: Log-Structured Merge-Trees (LSM-trees) and B-trees. LSM-trees append data to logs in memory and periodically merge sorted files on disk, making them highly optimized for write workloads. B-trees partition disk space into fixed-size pages and update them in place, making them highly optimized for read-heavy workloads.

## The idea
A database must accomplish two fundamental tasks: store data safely when given, and retrieve that data quickly when asked. 

To make lookups fast, databases use an index. An index is an auxiliary data structure that is built from the primary data. It acts as a guide, mapping search keys to their physical disk locations. However, indexing is not free. Every index you add increases write latency because the database must update the index structures alongside the actual data. Selecting the right storage engine is a balancing act between write performance, read performance, and disk space usage.

Under the hood, almost all major databases rely on one of two structural families for their indexes: log-structured engines (LSM-trees) or page-oriented engines (B-trees).

## How it works

### The simplest database: Bitcask style log and hash index
The simplest possible database is an append-only log file. When you write a key-value pair, the database appends it to the end of the file. Appending is O(1) and extremely fast because it performs a sequential write, which avoids disk seek overhead. 

The downside is that reads are O(N). To find a key, you must scan the entire file from start to finish.

To speed up reads, we can keep an in-memory hash map where every key is mapped to the byte offset of its value in the data file. This is the core design of Bitcask.

#### Worked Example 1: Bitcask-style storage
Let's trace how writes and reads work in a Bitcask-style database.

Suppose we execute these three write commands:
1.  `set("alpha", "10")`
2.  `set("beta", "20")`
3.  `set("alpha", "15")`

On disk, the database appends these records to a file named `segment_1.log`. Let's assume each record is written in a simple format: `key_length,value_length,key,value`.
-   The first record `5,2,alpha,10` starts at byte offset `0`. It takes up `14` bytes.
-   The second record `4,2,beta,20` starts at byte offset `14`. It takes up `12` bytes.
-   The third record `5,2,alpha,15` starts at byte offset `26`. It takes up `14` bytes.

In RAM, the database maintains a hash map:
-   After write 1: `{"alpha": {offset: 0, size: 14}}`
-   After write 2: `{"alpha": {offset: 0, size: 14}, "beta": {offset: 14, size: 12}}`
-   After write 3: The key `"alpha"` is updated to point to the newest record: `{"alpha": {offset: 26, size: 14}, "beta": {offset: 14, size: 12}}`

When we execute `get("alpha")`, the engine looks up `"alpha"` in the in-memory hash map. It finds offset `26` and size `14`. It performs a single disk seek to byte `26` in `segment_1.log`, reads `14` bytes, and immediately returns `"15"`.

Since disk space is finite, the log will eventually fill up. To prevent this, the engine splits the log into segments of a specific size (such as 100MB). When a segment is closed, a background thread runs **compaction**. Compaction reads the closed segment, throws away all duplicate keys, and keeps only the latest update for each key.

This simple Bitcask model has two major limitations:
1.  **Memory Limit**: All keys must fit entirely in RAM. If you have billions of keys, the hash map will outgrow your server's memory.
2.  **Range Queries are Poor**: You cannot easily perform range queries. If you ask for all keys between `"alpha"` and `"delta"`, the hash map cannot help you because hash tables do not preserve key order. You would have to scan the entire disk database.

### Sorted String Tables (SSTables) and LSM-Trees
To overcome the limitations of the simple log, we can add a constraint: the sequence of key-value pairs on disk must be sorted by key. This format is called a **Sorted String Table** (SSTable).

When SSTables are written to disk, they are immutable. To maintain sorted files while handling continuous writes, we use a sorted in-memory tree (such as a red-black tree or AVL tree) called a **memtable**.

#### Worked Example 2: Writing, flushing, and compaction in an LSM-tree
Let's look at how writes and reads are executed in an LSM-tree storage engine step by step.

##### Writes and Crash Recovery
When a write command like `set("dog", "bark")` arrives:
1.  The engine immediately appends the command to an append-only **Write-Ahead Log** (WAL) on disk. This log is used solely for crash recovery and is not sorted.
2.  The engine inserts `"dog": "bark"` into the sorted in-memory **memtable**. 
3.  The write is now considered complete.

##### Flushing to Disk
As writes accumulate, the memtable grows. When it exceeds its size limit (for example, 32MB):
1.  The engine freezes the active memtable and opens a new one to handle incoming writes.
2.  A background thread writes the frozen sorted memtable to disk as an SSTable file. This write is highly efficient because the keys are already sorted in RAM.
3.  The old WAL associated with the frozen memtable is safely deleted.

Suppose we flushed two memtables over time, resulting in two SSTable files on disk:
-   `sstable_1.db`: `[ "apple": "fruit", "cat": "meow", "dog": "bark" ]`
-   `sstable_2.db`: `[ "banana": "yellow", "cat": "purr" ]`

##### Sparse Indexes and Reads
To read a key like `"cat"`, we do not need to keep an offset for every single key in memory. Instead, we keep a **sparse index** in memory that lists the offsets of every few thousand blocks.

```
Sparse Index in RAM:
[ "apple" -> offset 0, "dog" -> offset 500 ]
```

To find `"cat"` in `sstable_1.db`:
1.  We look at the sparse index and see that `"cat"` falls alphabetically between `"apple"` and `"dog"`.
2.  We seek to offset `0` on disk and scan forward. Since the file is sorted, we either find `"cat"` or know it does not exist within that block.

##### Mergesort Compaction
Because we have multiple SSTable files on disk, we might have multiple versions of a key. To reclaim space and clean up old data, a background thread merges SSTable files using a mergesort-style algorithm.

Let's merge `sstable_1.db` and `sstable_2.db`:

```
sstable_1.db: [ "apple": "fruit", "cat": "meow", "dog": "bark" ]
sstable_2.db: [ "banana": "yellow", "cat": "purr" ]

Step-by-step merge:
1. Compare "apple" (sstable_1) and "banana" (sstable_2). 
   "apple" comes first. Output: "apple": "fruit".
2. Compare "cat" (sstable_1) and "banana" (sstable_2). 
   "banana" comes first. Output: "banana": "yellow".
3. Compare "cat" (sstable_1, value "meow") and "cat" (sstable_2, value "purr").
   Since sstable_2 is newer, we keep its value and discard "meow". 
   Output: "cat": "purr".
4. Output remaining keys. Output: "dog": "bark".

Final Compacted SSTable:
[ "apple": "fruit", "banana": "yellow", "cat": "purr", "dog": "bark" ]
```

##### ASCII Sketch 1: LSM Merge and Compaction

```
Disk Segment A (Older)       Disk Segment B (Newer)
+-----------------------+    +-----------------------+
| apple  : fruit        |    | banana : yellow       |
| cat    : meow         |    | cat    : purr         |
| dog    : bark         |    +-----------------------+
+-----------------------+                |
            \                            /
             \                          /
              \                        /
          MERGESORT COMPACTION (Background Thread)
                        ||
                        \/
             Compacted Disk Segment C
             +-----------------------+
             | apple  : fruit        |
             | banana : yellow       |
             | cat    : purr         |
             | dog    : bark         |
             +-----------------------+
```

##### Bloom Filters
If a key does not exist in the database, the engine would have to search the memtable first, and then check every single SSTable file on disk. This would be incredibly slow. 

To prevent this, LSM-tree engines use **Bloom filters** in RAM. A Bloom filter is a probabilistic data structure that can tell if a key is definitely not in an SSTable, letting the engine skip checking files that do not contain the target key.

##### Compaction Strategies
LSM-tree engines organize SSTables into levels or tiers using one of two strategies:
-   **Size-tiered compaction**: Newer and smaller SSTables are merged into progressively larger SSTables when enough files of a similar size accumulate.
-   **Leveled compaction**: The database partitions disk space into levels (Level 1, Level 2, etc.). Each level has a strict total size limit, and the SSTables within a single level contain non-overlapping key ranges. This strategy is used by RocksDB and Cassandra to reduce read amplification.

Other popular LSM-tree engines include LevelDB, HBase, and Lucene (the search library's term dictionary is essentially an LSM-tree-like sorted index).

### Page-Oriented Engines: B-Trees
B-trees are the standard storage engine family for most relational databases. 

Unlike LSM-trees, which write files sequentially, B-trees divide the database into fixed-size blocks or **pages**, typically 4KB or 8KB in size. The database reads or writes one entire page at a time. This design maps directly to how underlying disk hardware is structured.

A B-tree index is a balanced tree where each page contains several keys and child page pointers. The number of child pointers a page can hold is called the **branching factor** or fan-out. A high branching factor keeps the depth of the tree extremely small (typically 3 or 4 levels for millions of records).

#### Worked Example 3: B-Tree lookup and page split
Let's trace how a B-tree lookup, update, and split occur.

Assume our B-tree has a branching factor of 3 and uses 4KB pages.

```
                  Root Page [ 20, 50 ]
                 /         |          \
                /          |           \
               v           v            v
        Page A [ 5, 10 ]  Page B [ 30, 40 ]  Page C [ 60, 70 ]
```

##### 1. Lookup
We want to read key `35`:
1.  We load the Root Page and see that key `35` falls between `20` and `50`.
2.  We follow the middle pointer to Page B.
3.  We load Page B, find key `35`, and retrieve its value.

##### 2. In-place Update
We want to execute `set(35, "new_value")`:
1.  We navigate to Page B.
2.  We load Page B into memory, modify the value for `35`, and write the entire 4KB Page B back to its exact same location on disk.

##### 3. Page Split and Crash Recovery
Suppose we want to insert key `32` into Page B. However, Page B is already at its maximum capacity of three keys (it has `30, 35, 40` and can hold no more).
1.  **WAL Append**: Before doing anything, the engine appends the split operation to its disk WAL. If the database crashes mid-split, the WAL is used to restore the indexes to a consistent state.
2.  **Page Split**: Page B is split into two half-full pages: Page B1 `[ 30, 32 ]` and Page B2 `[ 35, 40 ]`.
3.  **Parent Update**: The boundary key `35` is pushed up to the Root Page. The Root Page now becomes `[ 20, 35, 50 ]` with pointers to Page A, Page B1, Page B2, and Page C.

If the Root Page also runs out of space, the split cascades upward, eventually splitting the root and increasing the depth of the tree by one level.

To protect the B-tree from concurrent writes and reads, we use **latches** (lightweight in-memory locks) to lock pages while they are being split or modified.

##### ASCII Sketch 2: B-Tree Page Split

```
BEFORE SPLIT:
                  Root Page [ 20, 50 ]
                        |
                        v
               Page B [ 30, 35, 40 ] (Full)


AFTER SPLIT (Inserting key 32):
                  Root Page [ 20, 35, 50 ]
                            /      \
                           /        \
                          v          v
            Page B1 [ 30, 32 ]    Page B2 [ 35, 40 ]
```

### Comparing LSM-Trees and B-Trees
To evaluate which engine family fits a workload, engineers compare write amplification, read latency, and space usage.

*   **Write Amplification**: When a single byte update causes multiple bytes to be written to disk, it is called write amplification. In B-trees, writing a single 10-byte change requires rewriting an entire 4KB or 8KB page. In LSM-trees, writes are buffered in memory and flushed in bulk, though compaction causes files to be rewritten multiple times. LSM-trees generally exhibit lower write amplification.
*   **Write Throughput**: LSM-trees offer significantly higher write throughput because they convert random writes into sequential appends. B-trees require random disk writes to update pages in place.
*   **Read Throughput**: B-trees offer superior read performance. Every key exists in exactly one place in a B-tree, whereas an LSM-tree may need to check multiple SSTables at different levels before confirming a value.
*   **Compaction Noise**: LSM-trees suffer from periodic write stalls. When background compaction threads compete with active client writes for disk bandwidth, response times can spike unexpectedly. B-tree latencies are far more predictable.

| Metric / Characteristic | LSM-Tree Storage Engine | B-Tree Storage Engine |
| :--- | :--- | :--- |
| **Write Amplification** | Low to moderate | High to very high |
| **Write Throughput** | Extremely high (sequential) | Moderate (random) |
| **Read Throughput** | Lower (must check multiple files) | Extremely high (single path) |
| **Tail Latency Consistency** | Variable (compaction stalls) | Predictable and stable |
| **Disk Space Overhead** | Low (better compaction/compression) | High (fragmentation/empty page gaps) |
| **Duplicate Keys** | Yes (older copies exist until merged) | No (exactly one copy in place) |

### Other Indexing Mechanisms
So far, we have discussed primary indexes. Databases also use several other indexing strategies:

#### Secondary Indexes
A secondary index is built to speed up lookups on columns other than the primary key. In a secondary index, the keys are not unique, and the values point either to the actual row data (in a heap file) or to the primary key.

#### Clustered vs Non-Clustered Indexes
-   **Clustered Index**: The actual row data is stored directly inside the index leaf pages. This makes reads extremely fast because once you find the key, you have the entire row. A table can have only one clustered index (usually the primary key).
-   **Non-Clustered Index**: The index leaf pages store only pointers to a separate heap file where the row data resides. This introduces an extra disk seek to fetch the row data.

#### Covering Indexes
A covering index is a non-clustered index that stores both the index key and the values of additional columns. If a query only requests columns that are stored within the index, the database can answer the query entirely from the index page, skipping the disk seek to the heap file.

#### Multi-Column Indexes
A multi-column index handles queries on multiple fields simultaneously. The most common type is a concatenated index, which glues columns together (such as `surname_firstname`). 

For spatial queries (like finding restaurants within a two-mile radius), databases use specialized multi-dimensional indexes like R-trees, which partition space geographically rather than alphabetically.

#### In-Memory Databases
In-memory databases like Redis keep all data in RAM. They are extremely fast not just because they avoid disk reads, but because they do not have to translate data structures into flat disk layouts. They can store pointers directly in memory. 

For safety, they still write change logs to disk or use periodic snapshots, but active execution is handled entirely in RAM.

---

## Pros

### LSM-Trees
- **Superior Write Throughput**: Converts random writes into fast sequential writes.
- **Lower Write Amplification**: Extends SSD lifespan by reducing the volume of redundant writes.
- **Better Storage Density**: Compacts sorted files efficiently, leading to smaller disk footprints.
- **Zero Page Fragmentation**: Writes immutable files sequentially, eliminating storage gaps.

### B-Trees
- **Predictable Read Performance**: Requires loading a small, fixed number of pages to locate any key.
- **Stable Tail Latency**: Avoids the sudden latency spikes caused by heavy background compaction.
- **Simple Isolation**: Each key exists in exactly one place, making row locking and transaction isolation simpler.
- **Low CPU Overhead**: Avoids continuous background file merging and data compression passes.

---

## Cons

### LSM-Trees
- **Background Compaction Noise**: Merging processes compete with client operations, occasionally causing severe write stalls.
- **Read Amplification**: Finding a key might require searching the memtable and multiple disk SSTables.
- **Expensive Non-Existent Key Checks**: Requires Bloom filters to avoid major performance hits when searching for missing keys.
- **Storage Headroom Requirements**: Needs extra disk space available to complete compaction merges.

### B-Trees
- **High Write Amplification**: Rewrites an entire page to update a single, small record.
- **Random Disk seeks**: Modifying data requires jumping to different pages on disk, slowing down writes.
- **Page Fragmentation**: Frequent inserts and page splits leave empty gaps, wasting disk space.
- **Fragile Crash States**: Updating pages in place risks corrupting data if a crash happens mid-split.

---

## Alternatives
- **Fractal Trees**: An alternative that buffers writes inside interior tree nodes, combining B-tree search paths with the low write amplification of LSM-trees.
- **Append-only Heap Files with Hash Indexes**: Structures like Bitcask that append records sequentially and index them in RAM, providing O(1) performance at the cost of high memory usage.
- **In-Memory Cache Stores (Memcached)**: Volatile RAM-only key-value stores that bypass disk synchronization completely for maximum throughput.

---

## When to use it
Choose an LSM-tree storage engine (such as RocksDB, Cassandra, or HBase) if your application is write-heavy, handles continuous streams of incoming logs or telemetry data, and operates on storage hardware with limited write durability. 

Choose a B-tree storage engine (such as PostgreSQL, MySQL, or SQLite) if your application is read-heavy, requires strong transactional isolation, and needs consistent, low-latency point reads.

---

## When NOT to use it
Do not use an LSM-tree engine if your application requires highly predictable tail latencies (such as high-frequency trading platforms) or absolute consistency with zero compaction-induced stalls. 

Do not use a B-tree engine if your write volume is so massive that it saturates disk write bandwidth due to random page updates, or if you are running out of storage space and cannot afford page fragmentation overhead.

---

## Key takeaways / mental model
The core trade-off is between sequential writes and in-place updates. 

Think of an LSM-tree as writing notes in a diary. You write entries sequentially as they happen. Periodically, you sit down, sort the entries alphabetically, and merge them into a collection of bound books. 

Think of a B-tree as a giant filing cabinet. Each folder is a page. To update an entry, you search the index, pull out the exact folder, erase the old value, write the new one, and slip the folder back in place. If a folder gets too full, you split its contents into two folders and update the labels.

---

## Self-check questions
1. How does a write-ahead log (WAL) protect a B-tree from leaving the database in an inconsistent state during a page split crash?
2. Why is compaction necessary in LSM-tree engines, and what are the trade-offs between size-tiered and leveled compaction?
3. Under what scenario would a read in an LSM-tree be forced to check multiple SSTable files on disk, and how do Bloom filters mitigate this?
4. What is write amplification, and why is it typically much higher in a B-tree than in an LSM-tree?
5. Why are in-memory databases like Redis faster than disk-based databases, even when the disk-based database has its entire dataset cached in RAM?
6. You are designing a service that stores real-time GPS coordinates of delivery vehicles. Writes occur every second per vehicle, and reads are rare. Which storage engine family would you choose and why?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 3: Storage and Retrieval.
- Prerequisites: [02-data-models.md](../lessons/02-data-models.md).
