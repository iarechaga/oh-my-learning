---
id: designing-distributed-systems/09
subject: designing-distributed-systems
title: "Ownership Election (Leader Election)"
slug: ownership-election
status: drafted
mastery:
seniority: senior
source: "Designing Distributed Systems (Brendan Burns), Chapter 8 (Ownership Election)"
prerequisites: [designing-distributed-systems/05]
created: 2026-07-01
updated: 2026-07-01
---

# Ownership Election (Leader Election)

## TL;DR
Many replicated systems need exactly one replica to own a particular responsibility at a time - one writer, one scheduler, one holder of a lock - even though you run several replicas for availability. Leader election is the mechanism that lets a group of identical replicas agree on which one currently holds that ownership, and, crucially, safely hand it over when the current owner dies. The whole difficulty lives in one word: *exactly*. Getting "at least one" or "at most usually one" is easy; guaranteeing never-two-at-once across network failures is what forces you to lean on a consensus system rather than home-grown logic.

## The idea
Replication (lesson 05) makes replicas interchangeable so *any* of them can serve *any* request. But some responsibilities must not be done by more than one replica at the same time:

- Only one replica should be the **primary writer** to a database, or two of them will make conflicting writes.
- Only one replica should run the **cron scheduler**, or a nightly job fires three times.
- Only one replica should hold a **distributed lock** guarding a resource.

Yet you still run several replicas, because if the single owner were a lone process, its death would be an outage. So you want the best of both: *N replicas for availability, but only 1 acting as owner at any instant, with automatic, safe handover when the owner fails.* That is exactly what leader election provides. One replica is elected **leader** (the owner); the others stand by; if the leader disappears, the survivors elect a new one.

The reason this is a genuinely hard, senior-level topic is the **safety requirement under partial failure**: the system must never have two replicas each believing they are the leader (a "split brain"), because that reintroduces exactly the conflicting-writes / double-scheduling problems you were trying to avoid. Networks drop packets, pause processes, and partition - so "the old leader looks dead" is not the same as "the old leader *is* dead," and an election that ignores that distinction will eventually elect a second leader while the first is still alive.

## How it works

### Leases, not permanent crowns
The foundational idea is the **lease**: leadership is not granted forever, it is *rented* for a bounded time and must be continually renewed. A replica becomes leader by acquiring a lease with a time-to-live (TTL), say 15 seconds. To stay leader it must renew (heartbeat) the lease before it expires. If it stops renewing - because it crashed, hung, or got partitioned - the lease **expires**, and another replica may acquire it.

Leases convert an impossible question ("is the leader alive?") into a decidable one ("has the lease expired?"). Nobody has to detect a crash reliably; they only have to observe a clock and a lease record.

```text
time ->
Leader A:  [acquire]--renew--renew--X (crashes)
lease:     |<----- TTL 15s ----->|.......expires
Replica B:                        [sees expired lease]--[acquire]-> new leader
```

### Why you need a consensus store underneath
The lease has to live *somewhere* that itself is reliable and linearizable, or the whole scheme is a lie. If two replicas could both be told "you got the lease" because they asked two different, out-of-sync copies of the lease record, you would have two leaders instantly. So leader election is built on a **strongly consistent, consensus-backed store**: etcd, ZooKeeper, or Consul. These use consensus protocols (Raft, ZAB, Paxos) to guarantee that a lease acquisition is an atomic, agreed-upon fact across the cluster - see [ddia/13 - Consistency and consensus](../../ddia/lessons/13-consistency-and-consensus.md).

The critical primitive they provide is an **atomic compare-and-swap (CAS)**: "set the leader key to *me*, but only if it is currently empty (or only if its version is exactly V)." Because CAS is atomic and agreed by consensus, *only one* contender can win, even if a thousand ask simultaneously. This is the bedrock: election reduces to "everyone races to CAS the leader key; the consensus store guarantees exactly one winner."

```text
Replicas A, B, C all attempt at once:
   CAS(leader_key, expected=<empty>, new="A")   -> etcd/ZK/Consul
   CAS(leader_key, expected=<empty>, new="B")      (consensus)
   CAS(leader_key, expected=<empty>, new="C")
        \______________ exactly ONE succeeds ______________/
   winner holds a lease with TTL; must renew or lose it
```

### The fencing problem: the dangerous edge every real design must handle
Here is the trap that separates a toy from a correct implementation. Suppose leader A holds the lease, then its process **pauses** - a long garbage-collection pause, or the VM is descheduled - for 20 seconds. Meanwhile its 15-second lease expires, B legitimately acquires leadership, and B starts writing. Then A wakes up. A does not know it was gone; from A's point of view no time passed and it is *still the leader*. Now A and B both issue writes: split brain, despite the lease.

The fix is a **fencing token**: each time the lease is granted, the consensus store also hands out a monotonically increasing number (1, 2, 3, ...). Every protected operation carries the token, and the protected resource (the database, the storage service) **rejects any operation with a token older than the highest it has seen**.

```text
A acquires lease -> token 33; A pauses.
B acquires lease -> token 34; B writes with token 34. Resource remembers max=34.
A wakes, still thinks it is leader, writes with STALE token 33.
Resource: 33 < 34 -> REJECT. Split-brain write blocked.
```

Leader election tells you who *should* be leader; **fencing tokens enforce it at the resource** so a zombie ex-leader cannot cause damage. A design that has election but no fencing is not safe under process pauses - and process pauses always happen.

### Clock skew and why TTLs must be generous
Lease expiry depends on time, and clocks on different machines drift. If the leader thinks the lease is valid for 2 more seconds but a follower's clock runs fast and thinks it already expired, the follower might grab leadership early. Real systems handle this by (a) using the *consensus store's* notion of expiry rather than each client's wall clock, and (b) choosing a TTL comfortably larger than the worst-case renewal delay + clock skew + network jitter. The trade-off is directness vs. safety: a short TTL means fast failover but risks premature expiry under a hiccup; a long TTL is safe but means a dead leader's responsibility stalls for up to that TTL before anyone takes over.

### Worked example 1: electing a single cron scheduler across 3 replicas
You run 3 identical replicas of a service; exactly one must run the nightly billing job.

1. All 3 start and each tries `CAS(scheduler_leader, expected=empty, new=self)` against etcd. Consensus guarantees exactly one - say replica B - wins and receives a 15 s lease and fencing token 7.
2. B renews the lease every 5 s (well inside the 15 s TTL) and is the only replica that runs scheduled jobs. A and C sit idle as followers, periodically watching the key.
3. At 02:00 the billing job fires - once, on B. A and C do nothing. No triple-billing.
4. B's node crashes at 02:03. B stops renewing. The lease expires ~15 s later.
5. A and C both attempt CAS; consensus picks one - say A - which gets token 8 and becomes leader. A resumes scheduling. Total ownership gap: ~15 s, and never two schedulers.

### Worked example 2: a GC pause causes a would-be double write, stopped by fencing
Leader A owns writes to an object store; TTL 10 s; A holds token 41.

1. A begins a long stop-the-world GC pause lasting 14 s. It renews nothing.
2. At 10 s the lease expires. B acquires it, token 42, and writes object X with token 42. The store records "highest token for X = 42."
3. At 14 s A resumes. Its clock and state say it is still leader (it never saw the gap). A issues a write to X carrying its stale token 41.
4. The store compares 41 against its recorded 42 and **rejects** A's write. A's client sees the rejection, realizes it has been superseded, and steps down.

Without fencing, step 3 would corrupt X with a write from a leader that no longer legitimately exists. The election alone did not save you; the token enforced at the resource did.

### Worked example 3: choosing the TTL - failover speed vs. false failovers
You must pick a lease TTL for a leader that renews every `R = 3 s`, with observed network jitter up to `J = 1 s` and clock skew up to `S = 0.5 s`.

- **Aggressive TTL = 4 s:** failover after a real crash is fast (~4 s). But a single 2 s network blip that delays a renewal past 4 s makes the lease expire while the leader is perfectly healthy - a *false* failover, causing an unnecessary handover (and, briefly, more fencing-token churn). Under load, false failovers can flap.
- **Conservative TTL = 15 s:** a delayed renewal of a few seconds is easily absorbed - almost no false failovers. The cost is that a genuinely dead leader's responsibility is unowned for up to ~15 s.
- **Reasoning:** set `TTL` safely above `R + J + S` plus headroom - here maybe 10-15 s - accepting slower failover to avoid flapping. If your workload truly needs sub-second failover, you must invest in tighter clocks, faster health signals, and accept the added risk, or design the responsibility to be resumable/idempotent so brief double-ownership is harmless.

## Pros
- **Availability with singleton semantics:** run N replicas for fault tolerance yet guarantee exactly one active owner, with automatic failover.
- **No custom crash detection:** leases turn "is it alive?" into "has the lease expired?", which is decidable from a record and a clock.
- **Correctness under contention:** an atomic compare-and-swap in a consensus store makes "exactly one winner" a hard guarantee, even with many simultaneous contenders.
- **Reusable and off-the-shelf:** etcd/ZooKeeper/Consul provide election primitives; you rarely build the consensus yourself.

## Cons
- **Depends on a consensus system:** you must run (or rent) etcd/ZooKeeper/Consul, itself a non-trivial, quorum-based system to operate correctly.
- **Fencing is mandatory and easy to forget:** without fencing tokens enforced at the resource, process pauses cause split-brain writes; election alone is not safe.
- **Failover latency:** there is always an ownership gap of up to the lease TTL between a leader dying and a new one taking over.
- **Tuning is subtle:** TTLs trade failover speed against false failovers under jitter/skew; getting it wrong causes either slow recovery or leadership flapping.

## Alternatives
- **Static/manual assignment:** designate one instance as owner by configuration. Trivial, but no automatic failover - its death is an outage until a human intervenes.
- **Stateless + idempotent design (avoid the singleton):** make the operation safe to run from many replicas at once (idempotent writes, dedup keys) so you never need a single owner. Best when feasible - it sidesteps election entirely.
- **Partitioned ownership (sharding of responsibility):** instead of one global leader, shard the responsibility so each replica owns a disjoint slice (see [sharded services](06-sharded-services.md)); reduces the blast radius of any one owner but each partition may still need election.
- **Database-native leader/primary election:** let the datastore (e.g. a replicated SQL cluster) elect its own primary rather than doing it in your app tier.

## When to use it
- A responsibility must be performed by exactly one replica at a time (single writer, single scheduler, lock holder), but you still need multiple replicas for availability.
- You require automatic, safe failover when the current owner dies, not a manual restart.
- You already have or can run a consensus store (etcd/ZooKeeper/Consul) and can enforce fencing tokens at the protected resource.
- Brief windows of no-owner (up to the lease TTL) are acceptable.

## When NOT to use it
- The work can be made idempotent or partitioned so multiple replicas can safely do it concurrently - then avoid the complexity of election altogether.
- You cannot enforce fencing at the resource, so a paused ex-leader could still cause damage - do not rely on election alone for safety-critical writes.
- The responsibility genuinely cannot tolerate even a lease-TTL ownership gap and you cannot make it resumable - reconsider the design; election always has a failover window.
- The overhead of running a consensus system is unjustified for a trivial, low-stakes singleton.

## Key takeaways / mental model
Think of a single "on-call pager" that must be held by exactly one engineer, but the team rotates so someone always has it. The pager is a *lease*: you hold it only while you keep checking in; stop checking in (you fell asleep) and after a timeout it auto-forwards to the next person. The subtle danger is the engineer who wakes from a nap still clutching the pager after it already forwarded - so every action taken "as the on-call" is stamped with a rotation number, and the systems ignore actions stamped with an old number. Two rules of thumb:

1. **Election gives you "exactly one *should* lead"; fencing tokens give you "exactly one *can* act."** You need both - a paused zombie leader is inevitable, and only fencing enforced at the resource stops its writes.
2. **Lease TTL is a dial between failover speed and stability.** Short = fast recovery but flaps under jitter/skew; long = rock-solid but a longer unowned gap. Build on a real consensus store (etcd/ZooKeeper/Consul) - never hand-roll the agreement.

## Self-check questions
1. Why can a system that runs multiple replicas still need "exactly one" of them to hold a given responsibility, and give three concrete responsibilities where two-at-once is a bug.
2. What is a lease, and how does it convert the hard problem "is the leader alive?" into something decidable? What role does the TTL play?
3. Why must leader election be built on a consensus store with atomic compare-and-swap rather than, say, a flag in a regular replicated cache?
4. Walk through the GC-pause split-brain scenario and explain exactly how a fencing token prevents the stale leader's write from taking effect. Why is election without fencing unsafe?
5. How do clock skew and network jitter influence the choice of lease TTL, and what goes wrong at each extreme (too short, too long)?
6. You have a job that must run once per hour and is *naturally idempotent* (running it twice has no extra effect). Do you still need leader election? Argue both sides and state what you would choose.

## References
- Designing Distributed Systems (Brendan Burns), Chapter 8: "Ownership Election"
- [designing-distributed-systems/05 - Replicated Load-Balanced Services](05-replicated-load-balanced.md)
- [ddia/13 - Consistency and consensus](../../ddia/lessons/13-consistency-and-consensus.md)
