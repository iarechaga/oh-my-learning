# Distributed Systems (principles)

The rigorous-theory layer beneath everything else in the track: the principles and
paradigms of distributed systems from first principles - architectures, processes and
threads, communication, naming, coordination, consistency and replication, fault
tolerance, and security. Where DDIA is data-system-centric and System Design is
applied, this subject is the formal foundation. Cross-links to DDIA (consistency,
consensus) and System Design.

**Source book:** *Distributed Systems* (3rd edition) - Maarten van Steen and Andrew S.
Tanenbaum (distributed-systems.net, 2017; freely available).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`distributed-systems/<NN>`* (e.g. *"discuss `distributed-systems/06`"*). Ordered by
dependency, following the book: foundations first, then coordination, consistency,
fault tolerance, and security.

**Seniority baseline:** senior (lessons range mid->staff).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | What a distributed system is: goals and pitfalls | mid | drafted | — | — | [lesson](lessons/01-goals-and-pitfalls.md) | — |
| 02  | Architectures and middleware | senior | drafted | — | — | [lesson](lessons/02-architectures-middleware.md) | — |
| 03  | Processes, threads, and virtualization | mid | drafted | — | — | [lesson](lessons/03-processes-threads.md) | — |
| 04  | Communication: RPC, messaging, multicast | mid | drafted | — | — | [lesson](lessons/04-communication.md) | — |
| 05  | Naming (flat, structured, attribute-based) | senior | drafted | — | — | [lesson](lessons/05-naming.md) | — |
| 06  | Clocks, logical time, and mutual exclusion | senior | drafted | — | — | [lesson](lessons/06-clocks-logical-time.md) | — |
| 07  | Coordination: election, gossip, distributed events | senior | drafted | — | — | [lesson](lessons/07-coordination.md) | — |
| 08  | Consistency and replication models | senior | drafted | — | — | [lesson](lessons/08-consistency-replication.md) | — |
| 09  | Fault tolerance and reliable group communication | senior | drafted | — | — | [lesson](lessons/09-fault-tolerance.md) | — |
| 10  | Consensus and agreement (Paxos/Raft foundations) | staff | drafted | — | — | [lesson](lessons/10-consensus-agreement.md) | — |
| 11  | Distributed commit and recovery | senior | drafted | — | — | [lesson](lessons/11-commit-recovery.md) | — |
| 12  | Security in distributed systems | senior | drafted | — | — | [lesson](lessons/12-security.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** (e.g. `ddia/12`, `ddia/13`) are listed per lesson in its
front matter and named in prose.
