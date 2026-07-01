# The Art of Multiprocessor Programming

This subject develops the deep correctness model for concurrent algorithms and data
structures on modern multiprocessors. It covers locking and lock-free design, then
connects abstract guarantees to practical concurrent structures.

**Source book:** *The Art of Multiprocessor Programming* - Maurice Herlihy and Nir Shavit (Morgan Kaufmann, 2012).

**Seniority baseline:** senior (lessons range mid->staff).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`multiprocessor-programming/<NN>`* (e.g. *"discuss `multiprocessor-programming/03`"*). Ordered by dependency: correctness model first, then lock-based structures, then nonblocking algorithms and advanced synchronization.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Concurrency model and shared-memory assumptions | mid | drafted | — | — | [lesson](lessons/01-concurrency-model-shared-memory.md) | — |
| 02  | Mutual exclusion and lock correctness criteria | mid | drafted | — | — | [lesson](lessons/02-mutual-exclusion-lock-correctness.md) | — |
| 03  | Classic lock algorithms (Peterson, bakery, tournament) | senior | drafted | — | — | [lesson](lessons/03-classic-lock-algorithms.md) | — |
| 04  | Scalable locks (TAS, TTAS, CLH, MCS, backoff) | senior | drafted | — | — | [lesson](lessons/04-scalable-locks.md) | — |
| 05  | Linearizability and correctness of concurrent objects | senior | drafted | — | — | [lesson](lessons/05-linearizability-correctness.md) | — |
| 06  | Concurrent linked lists and skip lists | senior | drafted | — | — | [lesson](lessons/06-concurrent-lists-skip-lists.md) | — |
| 07  | Progress guarantees: obstruction-free, lock-free, wait-free | senior | drafted | — | — | [lesson](lessons/07-progress-guarantees.md) | — |
| 08  | Universal constructions with consensus primitives | staff | drafted | — | — | [lesson](lessons/08-universal-constructions-consensus.md) | — |
| 09  | Consensus hierarchy and synchronization power | staff | drafted | — | — | [lesson](lessons/09-consensus-hierarchy.md) | — |
| 10  | Atomic primitives (CAS, FAA) and ABA hazards | senior | drafted | — | — | [lesson](lessons/10-atomic-primitives-aba.md) | — |
| 11  | Lock-free stacks and queues | senior | drafted | — | — | [lesson](lessons/11-lock-free-stacks-queues.md) | — |
| 12  | Memory reclamation (hazard pointers, epochs) | staff | drafted | — | — | [lesson](lessons/12-memory-reclamation.md) | — |
| 13  | Software transactional memory and composable synchronization | senior | drafted | — | — | [lesson](lessons/13-software-transactional-memory.md) | — |

**Cross-subject prerequisites** (recommended): `java-concurrency/03` for Java Memory Model context when mapping these ideas to JVM code.

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` · `mid` · `senior` · `staff` · `principal` - the band whose job the concept anchors.
