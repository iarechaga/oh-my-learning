---
id: system-design-interview/15
subject: system-design-interview
title: "Design Google Drive"
slug: google-drive
status: drafted
mastery: 
seniority: senior
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 15"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03]
created: 2026-08-10
updated: 2026-08-10
---

# Design Google Drive

## TL;DR
A cloud file storage/sync service (Google Drive, Dropbox) must keep a file
consistent across multiple devices and, when the same file is edited on two devices
while offline, resolve the resulting conflict without silently losing data. The
interview deep dive centers on three linked hard problems: an efficient sync
algorithm that avoids re-uploading unchanged data (block-level, not whole-file,
diffing), a conflict-resolution strategy for concurrent edits, and storage-layer
deduplication that saves enormous space when many users store identical or
near-identical file content.

## The idea
Storing a file is the easy part (any object store handles that). The genuinely hard
part is *staying in sync*: a user edits a file on their laptop while offline, edits the
same file on their phone in the meantime, then reconnects both devices — the system
must detect this, decide what to do, and never silently discard either version. Add to
that the practical need to sync efficiently (uploading a full 2GB file again because
one paragraph changed in a document would be unacceptable) and to avoid storing
redundant copies of identical content across millions of users (many users legitimately
store the exact same public files, templates, or common attachments), and this becomes
a genuinely rich systems problem beneath a deceptively simple product surface.

## How it works

### Step 1: Clarify requirements
- **Core features.** Upload/download files, sync across multiple devices for a single
  user, share files with other users, handle offline edits and reconnection. (Assume:
  real-time simultaneous co-editing within a single document, like Google Docs'
  character-by-character collaboration, is explicitly out of scope — that's a
  materially different problem requiring operational transformation or CRDTs, covered
  in `system-design/18`; this design is file-level sync, not live co-editing.)
- **Scale.** Assume 500 million users, average 5 GB stored per user, syncing across an
  average of 3 devices per user.
- **Consistency expectation.** Eventual consistency across devices is acceptable (a
  short sync delay after an edit is fine); silently losing data on conflict is not.

### Step 2: Back-of-the-envelope
Total storage: `500,000,000 × 5 GB = 2,500,000,000 GB = 2.5 exabytes` — an enormous
figure that immediately rules out anything but a massively distributed, sharded object
storage layer (this single number is the strongest justification in this lesson for
why the storage design, covered in Step 6, must include deduplication — even a modest
percentage of redundant content across 2.5 exabytes is an enormous absolute amount of
wasted storage and cost). Sync events: if each user makes ~10 file changes/day across
their devices, that's `500M × 10 / 100,000 seconds/day = 50,000 sync events/sec
average` — each event potentially requiring propagation to the user's other ~2 other
devices, so effective sync-notification volume is roughly 2-3x that.

### Step 3: High-level design
```
[Client device] --> [Sync/Metadata Service] --> [Metadata DB: file tree, versions]
       |                      |
       v                      v
[Block Storage Service]  [Notification Service] --> [Other devices of same user]
       |
       v
[Object Storage: deduplicated blocks]
```

- **Metadata Service/DB**: tracks the file/folder tree structure, per-file version
  history, and which storage blocks make up each file version — the source of truth
  for "what does this user's Drive look like right now."
- **Block Storage Service**: splits files into fixed-size blocks (chunks) for storage
  and dedup (Step 6), storing/retrieving individual blocks rather than whole files.
- **Notification Service**: informs a user's other connected devices that something
  changed, so they can sync (a lightweight push, similar in spirit to
  `system-design-interview/12`'s presence/delivery mechanism, but notifying "something
  changed, go fetch the delta" rather than delivering the content directly).

### Step 4: Deep dive — efficient sync via block-level diffing
Re-uploading an entire file on every edit is wasteful, especially for large files with
small changes (a 500-page document where one sentence changed). The standard technique:
split every file into fixed-size blocks (e.g., 4 MB each — this exact size is a tunable
trade-off, covered below), and on an edit, only the blocks whose content actually
changed need to be re-uploaded; unchanged blocks are simply referenced again by the new
file version's block list.

*Worked example:* a 20 MB file is split into five 4 MB blocks: `[B1, B2, B3, B4, B5]`.
A user edits a small section that falls entirely within B3's byte range. On save, the
client computes a hash of each block and compares it against the previous version's
block hashes; B1, B2, B4, B5 hash identically to before (unchanged), B3's hash differs.
Only the new B3 needs to be uploaded — 4 MB instead of the full 20 MB, an 80% reduction
in this example, and the savings grow further for larger files with proportionally
small edits (a 2 GB file with the same one-block change uploads 4 MB instead of 2 GB,
a >99% reduction).

**Block size trade-off.** Smaller blocks (e.g., 1 MB) mean finer-grained diffing (less
wasted re-upload when a small edit happens to straddle a block boundary) but more
metadata overhead (more block hashes to store and compare per file) and more per-block
request overhead. Larger blocks (e.g., 16 MB) reduce metadata overhead but risk larger
re-uploads when an edit touches a block boundary. Google Drive's real-world choice (and
the book's reference point) is in the low single-digit MB range as a reasonable middle
ground — worth stating as a tunable parameter you'd validate against real edit-pattern
data rather than a number to defend dogmatically.

**Determining which blocks changed without re-reading the whole file naively.** For
text-based or structured files, a rolling hash technique (conceptually similar to the
algorithm behind `rsync`) can detect insertions/deletions that shift byte offsets
without re-hashing every block from the shift point onward — a refinement worth
mentioning if the interviewer wants to go deeper on the sync algorithm itself, though
the fixed-block-hash-comparison approach above is sufficient to explain the core idea
clearly.

### Step 5: Deep dive — conflict resolution
Because devices can edit offline and reconnect later, two devices can produce two
different versions of the same file descending from the same starting point, and the
system must detect and handle this rather than silently picking one and discarding the
other.

**Detecting a conflict.** Each file version tracks a reference to the version it was
based on (its parent version, forming a version history, conceptually similar to a
commit graph). When device A uploads a new version based on parent version V3, and
device B *also* uploads a new version based on parent V3 (i.e., neither device had seen
the other's edit when it made its own), the metadata service detects that both new
versions claim the same parent — this is the signature of a genuine conflict, as
opposed to a normal sequential edit where the new version's parent is the current
latest version.

*Worked example:* File `report.docx` is at version V3 on the server. User edits it on
their laptop while offline, producing what will become V4-laptop (still based on parent
V3, since the laptop hasn't seen anything newer). Independently, the same user (or a
collaborator) edits the file on their phone while also offline, producing V4-phone
(also based on parent V3). Both devices reconnect and attempt to sync:
1. The laptop's V4-laptop syncs first; the server accepts it as the new latest version
   (V3 → V4, no conflict yet, since it was the first to arrive with parent V3).
2. The phone's V4-phone then attempts to sync, also claiming parent V3 — but the
   server's current latest version is now V4-laptop, not V3. The server detects that
   V4-phone's parent (V3) is stale (superseded by V4-laptop) — this is the conflict
   signal.
3. Resolution: rather than silently overwriting V4-laptop with V4-phone (which would
   lose the laptop edit) or rejecting the phone's edit outright (which would lose the
   phone edit), the system keeps **both** as separate files — e.g., `report.docx`
   (the version that synced first) and `report (conflicted copy from [device], [date])
   .docx` (the version that lost the race) — surfacing the conflict to the user rather
   than resolving it silently. This mirrors the general principle from
   `system-design-interview/06`'s key-value store lesson: when a system can't safely
   auto-merge concurrent writes, push the decision to the layer that can (there, the
   application; here, the end user).

This "keep both, name the loser a conflicted copy" strategy is deliberately simple and
data-safe — it never guesses wrong about which edit "matters more," at the cost of
occasionally requiring manual user cleanup, which is judged an acceptable trade-off
given the alternative (silent data loss) is much worse for a file storage product.

### Step 6: Deep dive — storage deduplication
Given the 2.5-exabyte total from Step 2, avoiding redundant storage of identical
content is a major cost lever, not a nice-to-have.

**Content-addressable block storage.** Instead of storing blocks keyed by
"which file, which position," key them by a hash of their own content (a
content-addressable scheme): `block_key = hash(block_content)`. If two different
users' files happen to contain a byte-identical block (e.g., both stored the exact
same PDF template, or both have a common boilerplate section), that block is physically
stored exactly once; each file's metadata simply references the same block key.

*Worked example:* User A uploads a company-wide onboarding PDF that many other
employees also happen to have saved to their own Drive. Instead of storing 500 separate
physical copies of an identical 10 MB file (5 GB total), content-addressable block
storage recognizes that every user's file decomposes into the same set of block hashes
already present in storage, stores the blocks once (10 MB total), and gives every
user's file metadata a reference to those same blocks — a ~500x storage reduction for
this one file across the user base. At exabyte scale, even modest overall dedup rates
translate into very large absolute cost savings.

**Interaction with block-level sync (Step 4):** these two mechanisms reinforce each
other — the same block-hashing infrastructure used to detect "which blocks changed"
during sync doubles as the key used for dedup during storage, so the design doesn't
need two separate hashing schemes.

### Step 7: Wrap-up — additional considerations
- **Sharing and permissions.** File/folder sharing needs an access-control layer in the
  metadata service (who can view/edit a given file or folder), a separate concern from
  sync/storage but touching the same metadata model.
- **Bandwidth-constrained sync.** Mobile clients on limited data plans benefit from
  configurable sync behavior (e.g., "only sync on WiFi," "don't auto-download large
  files") — a product-level consideration worth naming.
- **Version history and retention.** Keeping old versions (not just the latest) has its
  own storage-growth implications, and typically needs a retention policy (e.g., keep
  version history for 30 days, or a limited number of recent versions) rather than
  unbounded retention.

## Pros
- Block-level diffing dramatically reduces sync bandwidth for large files with small
  edits, which is the common case for real documents.
- The "keep both, mark the loser as a conflicted copy" conflict strategy is simple and
  never silently loses data.
- Content-addressable dedup and sync-diffing share the same underlying hashing
  mechanism, avoiding duplicated infrastructure.

## Cons
- Conflicted copies require manual user cleanup — a real (if intentional) UX cost of
  choosing safety over automatic merging.
- Block-level dedup requires careful block-size tuning and adds metadata overhead
  (tracking which blocks compose which file version) compared to naive whole-file
  storage.
- Version history retention adds ongoing storage growth that must be actively managed
  with a retention policy.

## Alternatives
- **Whole-file sync (no block-level diffing)** — much simpler to implement, but wastes
  enormous bandwidth re-uploading unchanged content on every edit to a large file;
  acceptable only for a system dealing exclusively with small files.
- **Automatic merge instead of "keep both" conflict handling** — works well for
  structured, mergeable content (e.g., version control systems merging non-overlapping
  code changes line-by-line), but is unsafe for opaque binary file formats where the
  system cannot understand *what* changed well enough to merge safely — which is why
  file-storage products like this one default to the safer "keep both" strategy rather
  than attempting automatic merges.
- **Real-time operational transformation/CRDTs** (as in Google Docs) — solves
  conflicts by design, at the character level, continuously, rather than detecting them
  after the fact at the file-version level; a fundamentally different (and more
  complex) architecture appropriate for live co-editing, explicitly scoped out in
  Step 1. See `system-design/18` for that design.

## When to use it
Any product offering cross-device file storage and sync: personal cloud storage,
enterprise file sync, backup services. The block-diffing and dedup techniques
specifically apply any time large files are stored redundantly or edited incrementally
at scale.

## When NOT to use it
For a system storing small, rarely-updated files where whole-file re-upload cost is
negligible (e.g., user profile pictures, small config files), block-level diffing adds
complexity without meaningful benefit — simpler whole-object storage and replacement is
appropriate. Also, if the product's actual requirement is live, simultaneous
co-editing rather than device-to-device sync, this file-version-based design is the
wrong starting point; reach for the CRDT/OT-based collaborative editing pattern
instead.

## Key takeaways / mental model
Three ideas, all keyed off the same underlying trick (content hashing of fixed-size
blocks): sync efficiently by only moving blocks whose hash changed; deduplicate storage
by keying blocks on their content hash so identical content across different users'
files is physically stored once; and detect conflicts by tracking each version's parent
and noticing when two versions claim the same parent — a signal that two devices
edited without knowledge of each other. None of these three problems is solved by
"just store the file" — they're solved by treating a file as a *composition of
content-addressed blocks plus a version history*, which is the mental model to lead
with in the interview before diving into any one deep-dive area.

## Self-check questions
1. Walk through why block-level diffing reduces sync bandwidth so dramatically for a
   large file with a small edit, and what determines how large the savings are for a
   given edit.
2. In the conflict-resolution worked example, why does the server treat V4-phone as a
   conflict rather than just accepting it as the new latest version?
3. Why does content-addressable block storage naturally deduplicate identical content
   across different users' files, without any explicit "check if this file already
   exists" step?
4. Why would you reject "automatically merge conflicting edits" as a strategy for this
   system, in contrast to a system like Google Docs?
5. Given the 2.5-exabyte total storage estimate, explain in your own words why
   deduplication is a first-order design concern here rather than an optional
   optimization.

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 15
- Cross-reference: `system-design/18` (case study: real-time collaboration) for the
  OT/CRDT-based approach to live co-editing, the harder problem this design explicitly
  excludes.
