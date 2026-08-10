---
id: distributed-systems/04
subject: distributed-systems
title: "Communication: RPC, Messaging, Multicast"
slug: communication
status: drafted
mastery: 
seniority: mid
source: "Distributed Systems, 3rd ed. (van Steen & Tanenbaum), Chapter 4"
prerequisites: [distributed-systems/01, distributed-systems/02]
created: 2026-08-10
updated: 2026-08-10
---

# Communication: RPC, Messaging, Multicast

## TL;DR
Distributed components talk to each other in three fundamentally different styles: RPC (synchronous, call-looks-like-a-local-call, with delivery semantics ranging from at-most-once to at-least-once depending on retry behavior), message-oriented middleware/queues (asynchronous, decoupled in time, with its own delivery-semantics spectrum), and multicast/group communication (one message, many recipients, with its own ordering and reliability guarantees). Picking the wrong style - or not understanding the delivery semantics of the one you picked - is one of the most common sources of subtle distributed bugs.

## The idea
Once you've decided components will run on separate machines (Lesson 01) and organized them into an architecture (Lesson 02), they need to exchange information. The naive mental model - "a network call is just a function call over the wire" - breaks down immediately because of the fallacies from Lesson 01: messages can be lost, delayed, duplicated, or reordered, and the sender frequently cannot tell which of those happened. Communication mechanisms exist to manage that uncertainty in different, deliberate ways:

- **RPC (Remote Procedure Call)** hides the network behind a familiar function-call syntax, optimized for synchronous request/response interactions.
- **Message-oriented middleware (MOM)** embraces asynchrony explicitly - sender and receiver need not be running at the same time, connected via a durable, decoupling queue or topic.
- **Multicast/group communication** generalizes point-to-point communication to "one message, many recipients," with its own guarantees about who receives what, in what order.

None of these is strictly better than the others - each trades latency, coupling, durability, and complexity differently, and most real systems use more than one style for different parts of their communication.

## How it works

### 1. RPC: making remote calls look local
The core idea of RPC is **marshaling**: the caller's arguments are serialized into a message, sent over the network, deserialized on the server, used to invoke the actual function, and the result is serialized back and returned to the caller - all hidden behind client-side and server-side "stubs" that make the call site look like an ordinary function call.

```
Client code:            result = add(3, 4)
                              |
                     [client stub / marshal]
                              |
                        network message
                              |
                     [server stub / unmarshal]
                              |
Server code:             add(3, 4) executes
                              |
                     [server stub / marshal result]
                              |
                        network message
                              |
                     [client stub / unmarshal]
                              |
Client code:            result = 7
```

**The failure-semantics problem.** A local function call either runs exactly once or (if the process crashes) not at all, and you can tell which. An RPC call can fail in ways that have no local analogue: the request message can be lost before it reaches the server, the server can crash after executing the call but before the response reaches the client, or the response itself can be lost. From the client's point of view, a timeout after sending a request is ambiguous - it does not tell you whether the operation ran zero times or one time.

This ambiguity forces a choice of **delivery/retry semantics**:
- **At-most-once** - the client does not retry, so the call runs zero or one times, never more. Safe against duplication, but a lost request or response means the operation silently never happened, and the caller must find out via some other means.
- **At-least-once** - the client retries on timeout until it gets a response, so the call runs one or more times. Guarantees eventual execution (assuming the server eventually responds) but risks the server executing the operation multiple times if earlier responses were lost rather than the request itself.
- **Exactly-once** - what everyone actually wants, but exactly-once *delivery* is not achievable over an unreliable network (you cannot both retry to guarantee delivery and never risk duplication without additional information). What's actually achievable is **exactly-once effect** via idempotency: the server deduplicates retried requests (e.g., using a client-supplied request ID) so that at-least-once delivery produces at-most-once *effect*.

**Worked example.** A payments RPC `chargeCard(cardId, amount)` is called by a client that times out waiting for a response and retries. If the server is not idempotent, the retry could charge the card twice - the classic "double charge" bug. The fix is to have the client attach an idempotency key (e.g., a UUID generated once per logical charge attempt) and have the server store, keyed by that UUID, whether it has already processed this exact charge; a retry with the same key returns the already-computed result instead of charging again. This converts an at-least-once delivery mechanism (safe against lost messages) into an exactly-once *effect* (safe against duplicate execution) - and it's why idempotency keys are close to mandatory for any RPC that mutates state and might be retried.

### 2. Message-oriented middleware (MOM): decoupling in time
Where RPC assumes the caller waits synchronously for a response and both parties are simultaneously available, MOM decouples sender and receiver in three ways:
- **Time decoupling** - the receiver need not be running when the message is sent; it processes the message whenever it comes online and reads from the queue.
- **Space decoupling** - the sender need not know the receiver's address, only the name of the queue/topic.
- **Synchronization decoupling** - the sender does not block waiting for the message to be processed, only (usually) for the message to be durably enqueued.

Two common patterns sit on top of MOM:
- **Point-to-point (queue)** - each message is consumed by exactly one consumer, even if multiple consumers are listening (competing consumers). Used for distributing work items across a worker pool.
- **Publish/subscribe (topic)** - each message is delivered to every subscriber. Used for broadcasting events to multiple independent interested parties.

**Delivery semantics for MOM** mirror RPC's, with the same fundamental trade-off:
- **At-most-once** - the broker delivers a message and forgets it; if the consumer crashes before finishing, the message is lost.
- **At-least-once** - the broker keeps a message until the consumer explicitly acknowledges processing it; if the consumer crashes before acking, the message is redelivered - risking duplicate processing, which again pushes the burden onto the consumer to be idempotent.
- **Exactly-once effect** - achieved the same way as RPC: at-least-once delivery plus idempotent (often deduplicated-by-ID) processing on the consumer side. Some systems (e.g., Kafka's transactional producers/consumers within its own ecosystem) provide exactly-once *processing* guarantees internally, but the general lesson - "the network can always duplicate or reorder, so make consumers idempotent" - still applies at the boundary.

**Worked example: order processing with a queue.** An e-commerce system publishes an `OrderPlaced` event to a queue after checkout. A worker service consumes it, charges payment, and acknowledges the message only after the charge succeeds. If the worker crashes mid-charge (after calling the payment API but before acking), the broker redelivers the message to another worker after a visibility timeout, and that worker retries the charge. Without idempotency (an order ID checked against "have I already charged this order?"), the customer would be charged twice - exactly the same underlying problem as the RPC example, just manifesting through a queue instead of a direct call. This is not a coincidence: at-least-once delivery plus non-idempotent handling is the single most common root cause of "duplicate side effect" bugs across both RPC and MOM.

### 3. Multicast and group communication: one message, many recipients
Sometimes a message genuinely needs to reach a *group* of recipients rather than one - e.g., invalidating a cache entry across every replica, or replicating a write to every node in a cluster. Point-to-point RPC or MOM could simulate this by sending N individual messages, but that pushes the sender to track group membership and handle partial failure (what if 3 of 5 recipients get it and 2 don't?) manually. Multicast/group communication protocols formalize this with named guarantees:

- **Reliable multicast** - guarantees that if any correctly-functioning process in the group delivers the message, all correctly-functioning processes in the group eventually deliver it too (no partial delivery among the survivors, even if the original sender crashes mid-send).
- **Ordered multicast** - guarantees an ordering property across messages sent to the group, with several useful strengths:
  - **FIFO order** - messages from the same sender are delivered in the order that sender sent them (but messages from different senders can interleave arbitrarily).
  - **Causal order** - if message A "happens-before" message B (e.g., B was sent after receiving A), every recipient delivers A before B; unrelated messages can still interleave.
  - **Total order** - every recipient delivers all messages in exactly the same order, even messages from different senders that share no causal relationship. This is the strongest and most expensive guarantee (it typically requires something consensus-like under the hood, foreshadowing Lesson 10).
- **Atomic multicast** - combines reliable delivery with total order: either every correct process delivers the message (in the same total order as every other message), or none do. This is the guarantee needed for state-machine replication (Lesson 09, Lesson 10) - if every replica applies the same operations in the same order, they end up in the same state.

**Worked example.** A distributed cache with 5 replica nodes needs to process `INVALIDATE(key)` and `SET(key, value)` operations in a way that every replica ends up agreeing on the final value. If two operations - `SET(key, "A")` from client 1 and `SET(key, "B")` from client 2 - arrive at different replicas in different orders (replica 1 sees A-then-B, replica 2 sees B-then-A), the replicas permanently disagree about the final value. Using atomic multicast to disseminate these operations ensures every replica applies them in the identical order, so every replica converges to the same final value ("B" if B was totally ordered after A everywhere) - this is precisely why reliable, ordered group communication underpins consistent replication (Lesson 08) and is closely related to running consensus (Lesson 10) among the replicas.

### 4. Choosing between the three styles
| Style | Coupling | Latency | Delivery guarantee shape | Best for |
| --- | --- | --- | --- | --- |
| RPC | Tight (caller waits) | Low (single round trip) | At-most/at-least-once, needs idempotency | Synchronous request/response, "I need the answer now" |
| MOM (queue) | Loose (time/space decoupled) | Higher (queueing, async processing) | At-least-once typical, needs idempotency | Work distribution, background processing, buffering bursts |
| MOM (pub/sub) | Loose (many subscribers) | Higher | Per-subscriber at-least-once typical | Broadcasting events to independent interested parties |
| Multicast/group | Depends on guarantee chosen | Higher for stronger guarantees (total/atomic order) | Configurable: reliable, ordered, atomic | Replicating state consistently across a known group |

## Pros
- **RPC**: simple mental model (looks like a local call), low latency, easy to reason about synchronously.
- **MOM**: decouples producers and consumers in time and space, naturally buffers load spikes, enables independent scaling of producers/consumers.
- **Multicast/group communication**: gives strong, named guarantees (ordering, atomicity) across a whole group without every sender manually tracking membership and partial failure.

## Cons
- **RPC**: tight coupling means both parties must be available simultaneously; failure-semantics ambiguity (did it run or not?) pushes real complexity onto the caller.
- **MOM**: added latency and operational complexity (running and monitoring a broker); at-least-once delivery still requires idempotent consumers; ordering across partitions/consumers is often weaker than developers assume.
- **Multicast/group communication**: stronger guarantees (total order, atomicity) are expensive and often require consensus-like coordination, hurting throughput and latency; group membership changes (nodes joining/leaving) add real protocol complexity (Lesson 09).

## Alternatives
- **Shared storage as communication** - instead of messaging, components communicate indirectly by reading/writing a shared datastore (e.g., a database row as a mailbox). Simpler in some ways, but couples components to a shared schema and pushes coordination problems into the storage layer.
- **Streaming platforms (Kafka-style logs)** - a hybrid of MOM and multicast: an ordered, durable, replayable log that many independent consumers can read from their own offset. Gives FIFO-per-partition ordering plus replay, at the cost of stronger operational requirements (partitioning strategy, consumer-group management).
- **Gossip-based dissemination** - covered in depth in Lesson 07 - trades strong delivery/ordering guarantees for extreme scalability and resilience to churn, appropriate when eventual, probabilistic delivery is good enough.

## When to use it
- Use **RPC** when a caller genuinely needs a synchronous answer before proceeding, and both parties can reasonably be expected to be available (or the caller can tolerate blocking/retrying).
- Use **MOM (queues)** to distribute discrete work items across a pool of workers, especially when producers and consumers scale independently or bursts need buffering.
- Use **MOM (pub/sub)** when multiple independent, decoupled parties need to react to the same event without the publisher knowing who they are.
- Use **multicast/group communication with strong ordering** when multiple replicas must apply the same sequence of operations to converge on the same state (state-machine replication).

## When NOT to use it
- Don't use synchronous RPC for a chain of many dependent calls where any one being slow blocks the whole chain (fan-out delays compound) - consider async messaging or restructuring the call graph instead.
- Don't use a queue where a synchronous answer is actually required by the caller (e.g., "is this payment approved?" needed before showing a confirmation screen) - that forces an awkward polling or callback pattern instead of a direct RPC.
- Don't reach for atomic/total-order multicast for interactions that don't actually need cross-replica ordering agreement - it's the most expensive guarantee in the table, and using it "to be safe" where causal or even unordered delivery would do is paying for coordination you don't need.
- Don't assume at-least-once delivery (RPC retries or MOM redelivery) is safe without making the receiving operation idempotent - this is the single most common correctness bug in production distributed systems.

## Key takeaways / mental model
Every communication mechanism in a distributed system is really answering the same underlying question differently: *what happens when a message might be lost, duplicated, delayed, or reordered, and who is responsible for coping with that?* RPC hides the network but leaves you holding the delivery-semantics ambiguity; MOM makes the decoupling explicit and durable but still needs idempotent consumers; multicast/group communication lets you buy stronger ordering and atomicity guarantees at a real cost, up to and including consensus. The unifying fix for the messiest failure mode - duplicate execution from retries - is almost always idempotency at the receiver, regardless of which communication style you chose.

## Self-check questions
1. Explain why "exactly-once delivery" is not achievable over an unreliable network, and describe precisely how idempotency keys convert at-least-once delivery into exactly-once *effect*.
2. Compare point-to-point queues and publish/subscribe topics. Give a scenario where using pub/sub for a job that should really be point-to-point would cause a bug.
3. What is the difference between causal order and total order in group communication? Give an example where causal order is sufficient and one where only total order will do.
4. A team builds an RPC-based chain of five synchronous service calls, each with a 100ms timeout, to render one page. What failure mode does this design invite, and how would you restructure the communication style to avoid it?
5. Why does atomic multicast (reliable + totally ordered) tend to require something consensus-like underneath, and why does that make it expensive relative to plain reliable multicast?

## References
- *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum), Chapter 4: Communication
- distributed-systems.net (free companion site for the source book)
