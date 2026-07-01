---
id: system-design/11
subject: system-design
title: Pub/Sub and Distributed Queues
slug: pubsub-distributed-queues
status: drafted
mastery:
seniority: mid
source: System Design Guide for Software Professionals (Sinha & Chopra), Chapter 7
prerequisites: [ddia/15]
created: 2026-06-30
updated: 2026-06-30
---

# Pub/Sub and Distributed Queues

## TL;DR
Asynchronous message brokers decouple services by moving from direct communication to message-based interaction. They offer buffer zones for traffic spikes, asynchronous fan-out to multiple subscribers, and durable message storage. Choosing between traditional message queues and log-based distributed logs dictates whether messages are discarded on acknowledgment or retained for replay.

## The idea
When services call each other synchronously using HTTP or gRPC, they bind their lifecycles together. If Service A calls Service B, and Service B experiences a slowdown or crash, Service A suffers as well. This tight coupling degrades system reliability and limits peak throughput. It causes thread exhaustion in caller services, where threads sit idle waiting for downstream responses, eventually leading to cascading failures across the entire system.

Asynchronous messaging solves this by placing an intermediary, a message broker, between services. Instead of waiting for a downstream service to finish processing, the upstream service publishes a message to the broker and immediately responds to the user. Downstream workers process these messages at their own pace. This decoupling brings three main benefits:
1. Temporal decoupling: Services don't need to be online at the same time. The billing service can go offline for maintenance, and the order service can still accept new orders because the broker stores them safely.
2. Load buffering: The broker acts as a shock absorber during traffic spikes. Instead of overwhelming downstream databases with sudden surges, the broker holds the messages, and consumers pull them at a manageable, constant rate.
3. Logical decoupling: The producer doesn't know or care who consumes the messages. This allows developers to introduce new features and new consumer services without modifying the core producer code.

## How it works
Understanding asynchronous messaging requires analyzing how brokers store, route, and deliver messages.

### Message Patterns: Point-to-Point vs. Pub/Sub
Message systems generally follow one of two patterns:
1. Point-to-Point (Queue): One producer sends a message to a queue, and exactly one consumer processes it. If multiple consumers poll the queue, the broker distributes the messages among them (competing consumers pattern). This is ideal for distributing work, like resizing images, generating reports, or sending emails.
2. Publish/Subscribe (Topic): A producer publishes a message to a topic, and the broker fans it out to all active subscribers. Each subscriber receives its own copy of the message. This is ideal when one event, such as "OrderCreated", must trigger independent actions in multiple services, like inventory, shipping, and billing.

### Traditional Message Routing (AMQP Exchange Types)
Traditional brokers, particularly those using the Advanced Message Queuing Protocol (AMQP), use an exchange abstraction to route messages. Producers send messages to an exchange, which routes them to queues based on bindings:
- **Direct Exchange**: Routes messages to queues based on an exact match of a routing key. This is useful for routing specific tasks directly to dedicated worker pools. For instance, messages with key `pdf-generation` go to a queue for PDF workers, while `image-resize` goes to image workers.
- **Fanout Exchange**: Duplicates and routes messages to all queues bound to it, ignoring routing keys. This is the primary mechanism for implementing publish/subscribe fan-out behavior. Every service bound to the exchange gets a complete copy of every event.
- **Topic Exchange**: Routes messages using wildcard matches between routing keys and queue binding patterns. A routing key like `europe.orders.shipping` can match a binding pattern like `*.orders.#` where `*` matches exactly one word and `#` matches zero or more words. This allows complex routing like "all orders from Europe" or "all shipping events globally".
- **Headers Exchange**: Routes messages based on message header attributes instead of routing keys, offering highly specialized routing criteria. It uses arguments like `x-match: any` or `x-match: all` to match headers against queue bindings.

### Traditional vs. Log-Based Message Brokers
The architectural split between traditional brokers (RabbitMQ, SQS) and log-based brokers (Kafka, Kinesis) is a central concept in stream processing (DDIA Concept 15: Stream Processing).

Traditional Brokers:
- Mechanism: They treat messages as transient jobs. The broker keeps track of which messages are in-flight or acknowledged. Once a consumer acknowledges a message, the broker deletes it from disk.
- Key properties: Excellent for fine-grained routing and work distribution. They support complex routing keys, selective message deletion, and individual message acknowledgements. However, they struggle with high-throughput stream processing and don't allow message replay.

Log-Based Brokers:
- Mechanism: They model topics as append-only log files on disk. A producer appends a message to the end of the log. Consumers read the log sequentially, keeping track of their position using an offset (a sequence number).
- Key properties: Because the log is append-only, reads are extremely fast and don't mutate the storage. The broker retains messages for a configured duration (e.g., 7 days) regardless of whether they have been read. This allows consumers to replay past messages by resetting their offsets. Consumer groups allow automatic scaling: each partition of a topic is assigned to exactly one consumer within a group.

### Log Compaction
In log-based brokers, log compaction is a storage policy that retains only the latest message for each message key. Instead of deleting messages based on age, the broker periodically scans the log and removes older records that have been superseded by newer updates with the same key. This is highly useful for rebuilding state caches after a crash: rather than replaying the entire history of edits, a consumer only needs to read the compacted log, which contains the final state for every key.

### Log Partitioning and Consumer Coordination
To scale consumption throughput, log-based brokers split topics into multiple partitions. Each partition is an ordered, immutable sequence of records.
Within a consumer group, the broker assigns each partition to exactly one consumer instance. This ensures that:
- Messages within a partition are processed in strict sequential order.
- Total processing throughput scales up to the number of partitions. Adding more consumers than partitions results in idle consumers.
When consumer instances join or leave the group (due to deployment or crashes), the broker triggers a rebalance. During a rebalance, partition assignments are recalculated. Eager rebalancing stops all consumption while assignments change, whereas cooperative rebalancing incrementally shifts partitions without a global halt, reducing latency spikes.

### Consumer Lag and Monitoring
An essential metric in message-driven systems is consumer lag. It represents the distance between the latest message written to a partition and the offset currently being processed by a consumer. High consumer lag indicates that consumers cannot keep pace with producers, warning developers of upcoming performance issues or resource exhaustion. Monitoring lag is critical to automatic scaling rules, allowing systems to provision more consumer instances when lag exceeds a threshold.

### Delivery Semantics and Idempotency
Guaranteeing message delivery over a network is difficult. Systems must choose a delivery semantic:
1. At-most-once: The consumer acknowledges the message before processing it. If the consumer crashes mid-process, the message is lost.
2. At-least-once: The consumer acknowledges the message only after successfully processing and saving the result. If the consumer crashes mid-process, the broker redelivers the message. This is the industry standard but requires consumers to be idempotent.
3. Exactly-once: The message is processed exactly once, and side effects occur exactly once. This typically requires coordinated transactions (like two-phase commit) or end-to-end idempotency where the message delivery and consumer state update are committed atomically.

Because true exactly-once delivery across distributed boundaries is expensive, most systems implement at-least-once delivery combined with idempotent consumer processing. An idempotent operation yields the same state whether run once or multiple times. For example, if a consumer receives a duplicate order message, it should check the database first. If the order has already been processed, it should skip any billing or email steps and simply acknowledge the message.

To implement an idempotent consumer, developers often use a dedicated deduplication table in their database:
```sql
CREATE TABLE processed_messages (
    message_id VARCHAR(255) PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
Inside a database transaction, the consumer inserts the incoming `message_id` into this table. If the insert throws a unique constraint violation, the transaction is aborted and the message is skipped as a duplicate. This simple database-backed check protects the system from duplicate side-effects.

### Ordering Guarantees
Log-based brokers guarantee message ordering only within a single partition. If a topic has four partitions, messages sent to Partition 1 are guaranteed to be read in the order they were written. But there is no global ordering guarantee across Partitions 1, 2, 3, and 4. To preserve ordering for related events (e.g., all events for Customer 456), producers must use a partition key (e.g., Customer ID) so that all events for that key land in the same partition.

### Backpressure, Buffering, and Dead-Letter Queues
When consumers can't keep up with producers, the broker buffers the messages. If the buffer fills up, backpressure must be applied: either the broker rejects new messages, or the producer slows down. This prevents the broker from running out of memory or disk space.
If a message repeatedly fails to process due to a bug or bad data (poison pill), the consumer shouldn't block the entire queue. Instead, after a set number of retries, the consumer routes the message to a Dead-Letter Queue (DLQ) for manual inspection and debugging, allowing the rest of the queue to keep flowing.

---

### Comparison: Queue vs. Pub/Sub
| Feature | Queue (Point-to-Point) | Pub/Sub (Publish/Subscribe) |
| :--- | :--- | :--- |
| Message Destination | Single consumer | Multiple independent subscribers |
| Primary Use Case | Task distribution, job processing | Event-driven architecture, system integration |
| Message Lifespan | Deleted after single consumption | Copied to all interested subscribers |
| Scaling Pattern | Add more competing consumers to one queue | Add new queues or consumer groups for each topic |

### Comparison: Traditional vs. Log-Based
| Feature | Traditional Brokers (RabbitMQ, SQS) | Log-Based Brokers (Kafka, Kinesis) |
| :--- | :--- | :--- |
| Storage Model | Transient heap/disk, deleted on ack | Durable, append-only log, retained by time/size |
| Message Replay | Not possible | Supported by resetting the consumer offset |
| Scale Factor | Scales with number of active messages | Scales with throughput and partition count |
| Routing | Highly flexible (wildcards, routing keys) | Simple partitioning, no complex broker-side routing |
| Consumer State | Tracked by the broker | Tracked by the consumer using offsets |

---

### Worked Example 1: Idempotent Order Processing Pipeline (At-Least-Once Queue)
This example shows an order service pushing orders to a traditional queue, processed by workers that use an idempotency check in the database to prevent duplicate charges.

```
+---------------+      Publish       +-----------------+
|               | -----------------> |  Pending Orders |
| Order Service |                    |     Queue       |
|               |                    +-----------------+
+---------------+                             |
                                              | Pull
                                              v
+------------------+     Ack Msg     +-----------------+
|                  | <-------------- |  Order Worker   |
|  Database        |                 +-----------------+
|  (Unique Const.) |                          |
+------------------+                          | Write Order
         ^                                    v
         |                              +--------------+
         +----------------------------- |  Postgres DB |
               Transaction Boundary     +--------------+
```

Sequence of events:
1. The Order Service publishes an order message: `{"order_id": "ORD-9912", "amount": 150.00}`.
2. A worker pulls the message from the queue.
3. The worker starts a database transaction:
   a. It attempts to insert the order into the `orders` table. The `order_id` has a primary key constraint.
   b. If the insert succeeds, the worker processes the payment and commits the transaction.
   c. If the insert fails with a unique constraint violation, the worker knows this message is a duplicate. It skips payment processing, rolls back the transaction, and safely acknowledges the message to clear it from the queue.
4. After committing the database transaction, the worker sends an acknowledgment (ACK) to the queue broker.

Failure scenario details:
If the database transaction commits successfully (step 3b), but the network drops before the worker can ACK the queue broker (step 4), the broker will eventually mark the message as timed out. It will then redeliver the message to another worker instance. The second worker will pull the exact same message. When it attempts the insert in step 3a, the database will throw a unique constraint violation. Because of this, the second worker skips payment processing and sends the ACK. This ensures the customer is charged exactly once despite the network failure.

### Worked Example 2: Fan-Out via Pub/Sub
An e-commerce site needs to trigger multiple actions when a user completes a purchase. Using pub/sub, the Order Service publishes a single event, and three independent subscribers handle their respective tasks.

```
                              +--------------------+
                              |  Fan-out Exchange  |
                              +--------------------+
                                    /   |   \
                     +-------------+    |    +-------------+
                     |                  |                  |
                     v                  v                  v
              +------------+     +------------+     +------------+
              | Inventory  |     |  Shipping  |     | Marketing  |
              |   Queue    |     |   Queue    |     |   Queue    |
              +------------+     +------------+     +------------+
                     |                  |                  |
                     v                  v                  v
              +------------+     +------------+     +------------+
              | Inventory  |     |  Shipping  |     | Email      |
              |  Service   |     |  Service   |     |  Service   |
              +------------+     +------------+     +------------+
```

Mechanism:
1. The user completes an order. The Order Service publishes an `OrderCompleted` event:
   ```json
   {
     "event_id": "evt-771",
     "order_id": "ORD-9912",
     "customer_id": "cust-456",
     "items": [{"sku": "SKU-11", "qty": 1}]
   }
   ```
   to a fan-out exchange.
2. The exchange duplicates the event and routes a copy into three distinct queues: `inventory-queue`, `shipping-queue`, and `marketing-queue`.
3. Each service consumes from its designated queue. If the `Email Service` goes offline for maintenance, messages accumulate in the `marketing-queue` without impacting the `Inventory Service` or `Shipping Service`. Once online, the `Email Service` processes its backlog at its own speed.

### Worked Example 3: Partitioned Ordering and Concurrency Failure
This example shows how partitioning maintains ordering, and how a developer's mistake can break that ordering guarantee.

We have a topic with two partitions. We use `user_id` as the partition key.

```
Producers send messages:
Msg A (User 1, "Create Account") -> Hash(User 1) -> Partition 0
Msg B (User 1, "Update Profile") -> Hash(User 1) -> Partition 0
Msg C (User 2, "Create Account") -> Hash(User 2) -> Partition 1

Partition 0: [ Msg A, Msg B ]  (Ordered)
Partition 1: [ Msg C ]         (Ordered)
```

How concurrency breaks ordering:
Suppose we have a consumer service with a consumer group. One consumer instance reads from Partition 0. To speed up processing, the developer writes multi-threaded code inside the consumer:

```
Consumer Instance
  |
  +-- Read Msg A, Msg B from Partition 0
  |
  +-- Thread 1: Process Msg A ("Create Account") -> Takes 500ms
  |
  +-- Thread 2: Process Msg B ("Update Profile") -> Takes 50ms
```

Because Thread 2 completes in 50ms while Thread 1 takes 500ms, the database receives the "Update Profile" write before the "Create Account" write. The update fails because the account does not exist yet.
To prevent this, the consumer must process messages from a partition sequentially on a single thread. If concurrency is required, the topic must be split into more partitions, allowing more single-threaded consumer instances to run in parallel. Each partition is mapped to a single thread or consumer instance, preserving ordering while scaling throughput.

## Pros
- **Temporal Decoupling**: Systems can operate asynchronously, meaning downstream systems can fail or experience maintenance without blocking the upstream producer.
- **Improved Throughput**: Web servers offload slow work to background workers, allowing them to handle more incoming requests without blocking resource pools.
- **Traffic Spiking Buffer**: The message queue stores spikes in traffic, letting consumers process the work at a steady, sustainable pace, protecting database connections from saturation.
- **System Extensibility**: Adding new features is simple, as developers can attach new subscribers to an existing pub/sub topic without modifying the producer code.
- **Error Isolation**: If one consumer service fails or throws exceptions, it does not stop other consumer services from receiving and processing messages from the same topic.

## Cons
- **Operational Complexity**: Managing a message broker cluster adds overhead, requiring monitoring of consumer lag, queue depth, disk space, and partition health.
- **Lack of Immediate Feedback**: Because processing is asynchronous, the user doesn't know if the background operation succeeded or failed immediately, requiring polling or websockets on the frontend.
- **Data Consistency Challenges**: Since updates occur across different databases asynchronously, the system is eventually consistent, requiring complex retry patterns or saga orchestrations.
- **Debugging Difficulty**: Tracing a transaction that spans multiple services, queues, and async workers requires distributed tracing tools and unified correlation IDs.
- **Message Duplication**: Due to network failures during acknowledgment, consumers must expect duplicate messages, forcing developers to build defensive, idempotent logic.

## Alternatives
- **Synchronous RPC/REST**: Directly calling services over HTTP/gRPC. Pick this when immediate confirmation of the outcome is required, or when the system must be strongly consistent.
- **Database as a Queue (Transactional Outbox)**: Writing events to a database table in the same transaction as business data, then polling that table with a worker to dispatch events. Pick this when you need strict atomic guarantees between database updates and message publishing.
- **Batch Processing and File Transfers**: Writing events to a shared storage system like S3, and processing them in hourly or daily batches. Pick this for large volume analytical workloads that don't need sub-second responsiveness.
- **In-Memory Event Bus**: Using local language-level event emitters or thread pools inside a single process. Pick this only for simple monolithic systems where distributed fault tolerance and persistent queuing are not required.

## When to use it
- **High-throughput asynchronous tasks**: Tasks like video encoding, report generation, and third-party API integration should be offloaded to queues.
- **Event-driven system architectures**: When multiple microservices must react to the same domain event, pub/sub fan-out is the standard approach.
- **Highly volatile traffic**: Applications like ticketing systems or flash-sale platforms should use queues to buffer sudden incoming request volumes.
- **Change Data Capture**: Replicating database changes to search indexes or read replicas in real-time, where log-based replay guarantees consistency.

## When NOT to use it
- **Low-latency synchronous operations**: Don't use queues when the frontend needs the result of the calculation before it can render the next screen. Use direct gRPC or REST instead.
- **Strict transactional consistency**: When three database writes must succeed or fail together across boundaries, relying on async queues is dangerous. Use distributed transactions or synchronous coordination instead.
- **Small-scale, simple applications**: Adding a distributed queue to a small system with low traffic adds unnecessary architectural complexity and operational cost.
- **Resource-constrained systems**: Brokers require significant memory and disk storage, making them inappropriate for edge devices or small serverless environments.

## Key takeaways / mental model
Think of a traditional queue as a post office box: once you pick up a letter, it's gone from the box, and nobody else can read it.
Think of a log-based broker as an endless roll of paper tape: anyone can read the tape at their own speed by keeping track of where they are with a bookmark. You can pull the tape back and re-read it as many times as you want.
To handle failures, pair at-least-once delivery with idempotent consumer designs, ensuring that duplicates are caught and ignored safely.

## Self-check questions
1. What is the fundamental difference in message consumption between a traditional queue (like RabbitMQ) and a log-based queue (like Kafka)?
2. Why is an idempotency key crucial when implementing at-least-once delivery semantics?
3. A developer partition-keys order events by `user_id` to maintain chronological ordering. However, their consumer service spawns five threads to process messages in parallel. Explain why this breaks ordering guarantees and how to fix it.
4. How does a log-based broker scale its consumption throughput, and what is the limit to this scaling?
5. Under what scenarios should you choose a Dead-Letter Queue (DLQ), and how do you handle messages that land there?
6. Compare how RabbitMQ and Kafka handle message acknowledgements. What are the performance and storage implications of each?

## References
- System Design Guide for Software Professionals (Sinha & Chopra), Chapter 7
- Designing Data-Intensive Applications (Kleppmann), Chapter 11: Stream Processing (DDIA/15)
