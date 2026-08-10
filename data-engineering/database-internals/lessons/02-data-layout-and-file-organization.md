---
id: database-internals/02
subject: database-internals
title: "Data Layout and File Organization on Disk"
slug: data-layout-and-file-organization
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part I, Chapter 2 (Data Structures Preliminaries) and Chapter 3 (File Formats)
prerequisites: [database-internals/01]
created: 2026-08-10
updated: 2026-08-10
---

# Data Layout and File Organization on Disk

## TL;DR
Storage engines don't write raw application objects to disk; they write fixed-size **pages** (typically 4-16 KB) that are organized into files with headers, checksums, and internal slot directories, so that the engine can find, validate, and update individual records without reading (or corrupting) the whole file. The page is the fundamental unit of I/O, and almost every other design decision in a storage engine (buffering, indexing, recovery) is built on top of the page abstraction.

## The idea
Random-access files on disk are just flat byte arrays from the OS's point of view — there is no built-in concept of "records" or "rows." A storage engine has to impose its own structure on that byte array so it can: (1) read/write in units that match the underlying hardware's I/O granularity (`database-internals/01`), (2) locate a specific record without scanning the whole file, (3) detect corruption from partial writes or crashes, and (4) update records in a way that doesn't require rewriting the entire file. The page (also called a block) is the answer to all four needs: a fixed-size chunk of the file, self-contained enough to be read, validated, and modified independently of every other page.

## How it works

### The page as the atomic unit of I/O
A page is typically 4 KB, 8 KB, or 16 KB — chosen to align with the filesystem block size and/or the underlying storage medium's page size (`database-internals/01`), so a single page read/write corresponds to a single physical I/O operation rather than spanning multiple. Every page in a file is the same fixed size, and every page carries:
- A **header**: page ID, page type (e.g. leaf node, internal node, overflow page), a pointer/offset to free space, and often a checksum of the page's contents.
- A **body**: the actual record data, laid out according to the page type.
- Sometimes a **trailer**: another checksum or a "magic number" so a partially-written page (torn write) can be detected on recovery.

**Worked example — locating record 500,000 in a 2 GB file.** Suppose a table has 500,000 fixed-size 200-byte rows stored across 8 KB pages, roughly 40 rows per page (8192 / 200, minus header overhead). To read row 500,000, the engine doesn't scan the file; it computes `page_number = 500000 / 40 = 12500`, seeks directly to byte offset `12500 * 8192 = 102,400,000`, reads that one 8 KB page, and finds the row within it. This O(1) addressing (page_number x page_size = byte_offset) is only possible because every page is the same fixed size — variable-size pages would require an index just to find where a page starts.

### Slotted pages: handling variable-length records inside a fixed-size page
Real rows are rarely fixed-size (a VARCHAR column, a JSON blob). The standard solution, used by nearly every relational and document database, is the **slotted page** layout:

```
+----------------+---------------------------+------------------+
| Page Header    | Slot Directory (grows -->)|  <-- (grows) Records |
| (page_id, ...) | [off1,len1][off2,len2]... |  ...  Record2  Record1|
+----------------+---------------------------+------------------+
```

The slot directory (an array of small `(offset, length)` pairs) grows forward from just after the header; the actual record bytes are appended backward from the end of the page. A record is referenced not by its raw byte offset (which would break if the record moved) but by its **slot number** — a stable logical ID.

**Worked example — updating a variable-length record in place.** Suppose slot 3 currently points to a 40-byte record at offset 8100. An UPDATE changes that record to 60 bytes. The engine can't simply overwrite in place (it would clobber the neighboring record). Instead: (1) if there's enough free space between the slot directory and the record area, write the new 60-byte version into that free space, and update slot 3's `(offset, length)` entry to point to it; (2) mark the old 40 bytes as a "hole" (fragmentation) to be reclaimed later by a page-compaction pass that slides records together. Crucially, every *other* record's slot number is untouched — any external reference (e.g. a B-Tree leaf pointer or a secondary index entry) that points to "slot 3 of page 12500" still resolves correctly, because indirection through the slot directory absorbed the change. Without this indirection, every update that changed a record's size would force rewriting every index that referenced it by raw offset.

### File organization: heap files vs. sorted/clustered files
Once you know how a single page is laid out, the next question is how pages are organized *across* the file:
- **Heap file**: records are appended wherever there's free space, in no particular order relative to any key. Fast inserts (append to first page with room, or a free-space map), but finding a specific record requires an index (a heap file alone offers no ordering to exploit) — this is the classic pairing behind "heap table + B-Tree index" in databases like PostgreSQL.
- **Clustered/sorted file**: records are kept physically ordered by a key (often directly as the leaf level of a B-Tree, `database-internals/03`). This makes range scans on that key extremely fast (sequential I/O, per `database-internals/01`) but makes inserts more expensive when they land in the middle of the sorted order (may require a page split).

**Worked example — heap file with a free-space map.** A heap file with 10,000 pages keeps a small in-memory (or separately-stored) **free-space map**: a compact array recording, per page, roughly how much free space it has (often bucketed, e.g. "0-25% full," "25-50% full," etc., rather than tracked exactly, to keep the map small). On INSERT, the engine consults the map to find *any* page with enough room (often reusing a page with existing holes from prior deletes) rather than always appending at the end — this keeps the file from growing unboundedly as rows are deleted and re-inserted, at the cost of losing any physical row ordering.

### Checksums, page headers, and detecting corruption
Because a page might be partially written when a crash happens mid-write (a "torn page"), storage engines add a checksum (e.g. CRC32) computed over the page's contents and stored in the header or trailer. On every page read, the engine recomputes the checksum and compares — a mismatch means the page is corrupt (from a torn write, bit rot, or a hardware fault) and recovery must fall back to the write-ahead log (`database-internals/04`) to reconstruct the page's correct state, rather than trusting what's on disk.

**Worked example — detecting a torn write.** A page is being updated when the OS or hardware crashes after writing only the first 4 KB of an 8 KB page (a torn write can happen because disks/OSes don't guarantee atomicity above their own native sector size, often 512 bytes or 4 KB, while the database's page might be a multiple of that). On restart, the engine reads the page, recomputes its checksum over the full 8 KB, and finds it doesn't match the stored checksum (because half the page is stale data, half is new). The engine now knows this page is untrustworthy and must be repaired from the WAL rather than served to a query — without the checksum, the engine would silently return corrupted data.

### Copy-on-write pages: an alternative to in-place slot updates
Some engines (notably LMDB, and the copy-on-write B-Trees covered more in `database-internals/03`) never modify a page in place at all. Instead, any update to a page writes an entirely new page at a new location, and the parent pointer is updated to point to the new page — cascading up to the root. This trades extra write volume (every update touches every ancestor page up to the root, not just the leaf) for a powerful property: readers never see a torn or half-updated page, because old pages are never mutated while a reader might be looking at them, only replaced. This is the same idea DDIA (`ddia/04`) touches on with LSM-Trees' immutable SSTables, applied at the single-page granularity instead of whole-file granularity.

## Pros
- Fixed page sizes give O(1) addressing (page_number -> byte_offset) without a separate index just to find pages.
- Slotted pages let variable-length records live inside fixed-size pages while keeping external references (slot numbers) stable across in-page updates.
- Checksums make corruption detectable rather than silently served to queries.

## Cons
- Slotted pages fragment over time (deleted/shrunk records leave holes) and need periodic compaction passes to reclaim space.
- Fixed page size is a one-size-fits-all compromise: too small wastes header/slot-directory overhead proportionally; too large wastes I/O bandwidth reading/writing unused bytes for small updates.
- Copy-on-write avoids in-place corruption risk but multiplies write volume for every update (an update near the leaf still rewrites every ancestor page to the root).

## Alternatives
- **Log-structured storage (no in-place pages at all)** — instead of updating pages, always append new versions and let compaction reclaim old ones; this is the LSM-Tree approach (`database-internals/06`), trading page-level update complexity for a different (log/compaction) complexity.
- **Fixed-length-only records (no slotted pages)** — some specialized engines (e.g. column stores with fixed-width encodings) avoid slotted pages entirely by only storing fixed-width values, trading flexibility for simpler, denser page layout and O(1) intra-page addressing without a slot directory.
- **Row-major vs. column-major layout** — this lesson assumes row-major (a full record together in one place); OLAP-oriented engines instead lay data out column-major (all values of one column together across many rows) to improve compression and scan throughput for analytical queries — see `ddia/05` for the OLTP/OLAP and column-storage framing.

## When to use it
Any disk-based storage engine needs some version of this page/slot/checksum design — it's not an optional layer, it's the substrate everything else (B-Trees, LSM-Trees, buffer pools, WAL replay) is built on top of. Understanding it is what lets you reason about why a specific engine behaves the way it does under updates, deletes, and crashes.

## When NOT to use it
If you're building a purely in-memory data structure with no persistence requirement, none of this page machinery is needed — direct pointer-based structures in RAM don't need fixed-size addressable units, slot indirection, or checksums, because there's no "torn write" risk and no disk-seek cost to amortize.

## Key takeaways / mental model
Think of a page as a self-contained, checksummed "safe deposit box" of fixed size: the box itself never changes address (page_number -> offset is fixed math), but what's inside can be rearranged (slot directory) as long as the box's own integrity (checksum) can always be verified before trusting its contents. Every higher-level structure in this subject (B-Tree, LSM-Tree, WAL) is built by chaining these safe deposit boxes together with pointers.

## Self-check questions
1. Why does the slotted-page design use an indirection layer (slot number -> offset/length) instead of just storing raw byte offsets directly in the B-Tree or index that references a record?
2. A page is 8 KB and rows currently average 100 bytes but a migration will make some rows grow to 500 bytes with a long text field. What page-layout consequence should you anticipate, and why does slotted-page indirection make the migration survivable without touching every external index reference?
3. Explain, in your own words, why a checksum mismatch on page read is not just a "nice to have" but load-bearing for crash recovery correctness (link this to `database-internals/04`'s write-ahead logging).
4. Contrast heap file organization with clustered/sorted file organization: which one would you pick for a table that's mostly written once and then range-scanned by timestamp, and why?

## References
- Database Internals (Alex Petrov), Part I, Chapter 2: "Data Structures Preliminaries" and Chapter 3: "File Formats."
- See also: `database-internals/01` for the hardware I/O reasoning behind fixed page sizes, and `ddia/04` for the broader storage-engine context.
