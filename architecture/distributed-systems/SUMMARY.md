# Distributed Systems (Principles) - Subject Summary

A comprehensive recap of the formal-theory layer of the track, concept by concept. This
subject builds the rigorous foundation - architectures, communication, naming,
coordination, consistency, fault tolerance, consensus, and security - underneath the
more applied treatment in DDIA and System Design. Cross-links to `ddia/12` and `ddia/13`
where the practical and formal treatments meet.

**Source book:** *Distributed Systems* (3rd edition) - Maarten van Steen and Andrew S.
Tanenbaum (distributed-systems.net, 2017; freely available).

**Progress note:** all 12 lessons are `drafted`; none discussed yet, so mastery is
pending and no weak spots are recorded. See the table in [README.md](README.md). Reading
order is top to bottom (dependency-ordered, following the book).

## Foundations

- **[01] What a distributed system is: goals and pitfalls** - defines a distributed
  system by what it lacks (shared memory, shared clock) and what that forces (partial
  failure as a first-class concern). Covers the eight fallacies of distributed
  computing, the eight kinds of transparency (and why full transparency isn't always
  desirable), and scalability pitfalls like hidden centralization.
  ([lesson](lessons/01-goals-and-pitfalls.md))
- **[02] Architectures and middleware** - separates *software* architecture (layered,
  tiered, microkernel) from *system* architecture (centralized client-server,
  decentralized P2P, hybrid edge/superpeer designs), and explains middleware's role
  (RPC, MOM, naming, transaction coordination) in absorbing the fallacies from 01 into
  reusable machinery. ([lesson](lessons/02-architectures-middleware.md))
- **[03] Processes, threads, and virtualization** - threads vs. processes for cheap
  concurrency, server organization patterns (iterative, thread-per-request, worker pool,
  event-driven), code migration (weak vs. strong mobility, mobile agents), and VMs vs.
  containers as deployment/isolation mechanisms. ([lesson](lessons/03-processes-threads.md))

## Communication and naming

- **[04] Communication: RPC, messaging, multicast** - RPC's failure-semantics problem
  (at-most-once vs. at-least-once vs. exactly-once *effect* via idempotency),
  message-oriented middleware (queues and pub/sub, with the same delivery-semantics
  spectrum), and multicast/group communication guarantees (reliable, FIFO/causal/total
  order, atomic multicast). ([lesson](lessons/04-communication.md))
- **[05] Naming (flat, structured, attribute-based)** - flat naming resolved via
  broadcast or a DHT; structured naming with DNS as the fully worked example
  (delegation, iterative resolution, TTL caching trade-offs); attribute-based naming via
  directory services (LDAP-style); and how a real system (Kubernetes) layers all three.
  ([lesson](lessons/05-naming.md))

## Time, coordination, and consistency

- **[06] Clocks, logical time, and mutual exclusion** - why physical clock sync
  (Cristian's algorithm, NTP) can only ever be approximate; Lamport timestamps (a total
  order consistent with causality, but blind to true concurrency) and vector clocks
  (which can detect it); centralized, distributed (Ricart-Agrawala), and token-ring
  mutual exclusion algorithms. Parallels `ddia/12`'s practical warning against relying on
  synchronized clocks for correctness. ([lesson](lessons/06-clocks-logical-time.md))
- **[07] Coordination: election, gossip, distributed events** - the Bully and Ring
  election algorithms for picking a coordinator after a failure; gossip/epidemic
  protocols for scalable, churn-resilient dissemination (push/pull, anti-entropy vs.
  rumor-mongering, `O(log N)` convergence); distributed termination detection and the
  Chandy-Lamport consistent-snapshot algorithm. ([lesson](lessons/07-coordination.md))
- **[08] Consistency and replication models** - data-centric models (strict, sequential,
  causal, eventual) and client-centric models (read-your-writes, monotonic reads/writes,
  writes-follow-reads), paired with the replication strategies (primary-backup,
  multi-primary, leaderless/quorum) that implement them. Parallels `ddia/13`'s treatment
  of linearizability and causal consistency. ([lesson](lessons/08-consistency-replication.md))

## Fault tolerance, consensus, and commit

- **[09] Fault tolerance and reliable group communication** - the failure-model
  hierarchy (crash, omission, timing, response, Byzantine) and why the choice matters;
  reliable multicast and virtual synchrony for staying consistent when a sender crashes
  mid-broadcast; checkpointing, logging, and coordinated recovery.
  ([lesson](lessons/09-fault-tolerance.md))
- **[10] Consensus and agreement (Paxos/Raft foundations)** - the staff-level anchor
  lesson. States the consensus problem formally, explains the FLP impossibility result
  intuitively (why no protocol can guarantee both safety and termination in a fully
  async system with one crash failure), walks a full Paxos round (proposers, acceptors,
  the overlapping-majorities safety argument) and a full Raft leader election and log
  replication cycle, and covers operational nuance - split-brain risk, why quorums must
  be a strict majority, and why adding nodes doesn't scale write throughput.
  ([lesson](lessons/10-consensus-agreement.md))
- **[11] Distributed commit and recovery** - two-phase commit's mechanics and its
  blocking problem when the coordinator crashes mid-decision; three-phase commit's fix
  for that specific blocking window (at the cost of an extra round trip, and without
  fixing the general network-partition case); durable-log recovery discipline. Cross-
  links to `hard-parts/11`'s sagas as the alternative that avoids blocking entirely.
  ([lesson](lessons/11-commit-recovery.md))
- **[12] Security in distributed systems** - the threat model unique to distribution
  (untrusted network, no shared trust anchor by default); authentication (shared-secret
  vs. public-key/CA-based) and secure channels (TLS bundling confidentiality, integrity,
  authenticity); centralized vs. capability-based access control; the attack shapes -
  replay, man-in-the-middle, and Sybil attacks (specific to P2P/gossip systems).
  ([lesson](lessons/12-security.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on concepts rated
`shaky` or `not-yet`.
