---
id: ddia/15
subject: ddia
title: "Stream Processing"
slug: stream-processing
status: drafted
mastery:
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 11"
prerequisites: [ddia/14]
created: 2026-06-30
updated: 2026-06-30
---

# Stream Processing

## TL;DR
Stream processing handles continuous, unbounded flows of real-time events as they occur instead of waiting for daily or hourly batches. This model requires specialized messaging brokers, change data capture techniques, and stateful joins to keep distributed views in sync. Achieving high accuracy under network delays demands careful reasoning about event time, late data mitigation using watermarks, and fault-tolerant checkpointing.

## The idea
Batch processing operates on static, historical datasets that have a clear beginning and end. While MapReduce and other batch engines are excellent for analyzing past logs, they cannot easily handle ongoing events. Real-world systems generate data continuously. Users click links, financial markets trade assets, and industrial sensors emit readings throughout the day. Waiting for a daily cron job to run means responding to critical changes long after they happen.

Stream processing solves this limitation by treating all data as an unbounded, continuous flow. Instead of saving data to a file and closing it before any processing begins, a stream consumer handles each event immediately after it occurs. This approach reduces processing latency from hours to seconds or milliseconds. The ultimate goal is to provide a continuous, real-time mechanism for updating views, detecting anomalies, and coordinating responses across distributed applications.

## How it works
Unbounded stream processing relies on specialized messaging systems to transport events, techniques to capture database changes, and custom join algorithms. These systems must coordinate partitions, track processing offsets, and manage local memory buffers to ensure that continuous calculations remain both fast and correct even when network failures occur.

### Event and Record Basics
An event is a small, self-contained, immutable object that captures the details of an occurrence. It consists of a timestamp, a key (often used for routing and partitioning), and a payload containing the state.

Because events are immutable, they represent historical facts. You can never edit or delete an event once it is written. Any subsequent modification of state must be represented as a new event, ensuring that the complete sequence of actions is preserved. This immutability makes it safe to replay logs and reconstruct past state at any point.

### Producers and Consumers
A stream processing architecture separates event creation from event consumption. Producers are the systems or devices that generate events. They write messages directly to a transport layer, unaware of who will read them. Consumers are the applications that subscribe to these events. They process the incoming data and produce secondary actions, alerts, or updated views.

### Messaging Systems, Backpressure, and Durability
To move events from producers to consumers, we need an intermediary transport. We can classify these transport mechanisms into three distinct models:

1. **Direct Messaging**: Systems communicate directly over TCP, HTTP, or UDP. The producer pushes messages to the consumer. If the consumer is offline or slow, messages are dropped, or the producer must block. This model has minimal latency but lacks durability and fault tolerance.

2. **Transient Message Brokers**: A central broker manages queues of messages. When a producer sends a message, the broker writes it to disk or memory. It then forwards the message to an available consumer. Once the consumer acknowledges receipt, the broker deletes the message from its store. This pattern works well for distributing tasks among workers but does not maintain strict order across multiple consumers, and past messages cannot be replayed.

3. **Log-Based Message Brokers**: A broker stores messages as an append-only log on disk. The log is split into partitions, each residing on a different machine. Consumers read messages from a partition sequentially. They track their progress by periodically saving an integer offset, which acts as a pointer to the next message. Because the broker does not delete messages on acknowledgment, the same log can be read independently by multiple consumers, and historical data can be replayed by resetting the offset.

Managing backpressure is critical when consumers cannot keep up with producers. In direct messaging, backpressure forces the sender to block or drop events. Transient brokers must block the producer or spill messages to disk when queue limits are breached. Log-based brokers handle slow consumers naturally. Lagging consumers simply fall behind their offset, while the producer keeps writing at full speed. The log acts as a massive disk buffer, isolating the producer's write path from the consumer's performance.

### Traditional AMQP/JMS vs. Log-Based Brokers
Traditional message brokers (using protocols like AMQP or JMS) and log-based message brokers (like Apache Kafka) are optimized for entirely different workloads. The table below outlines these structural differences:

| Feature | Traditional Brokers (AMQP/JMS) | Log-Based Brokers (Kafka/Pulsar) |
| :--- | :--- | :--- |
| **Storage Model** | Transient: Messages are deleted upon consumer acknowledgment. | Durable: Messages are stored in append-only partitions on disk. |
| **Consumption Pattern** | Load balancer: Distributes messages dynamically to a pool of workers. | Sequential: Consumer groups assign partitions to specific workers. |
| **Ordering Guarantee** | Weak: Messages are processed out of order if consumers fail or retry. | Strong: Order is strictly preserved within each log partition. |
| **Message Replay** | Impossible: Once a message is deleted, it cannot be recovered. | Supported: Offsets can be reset to reprocess historical data. |
| **Scale Mechanism** | Adding more independent consumers to share queue load. | Adding more partitions to split the log across nodes. |

Traditional systems treat message delivery as an active routing process. The broker tracks individual acknowledgements, which requires a complex state machine. If consumer A receives message 5 but crashes before replying, the broker must re-route message 5 to consumer B. This re-routing often breaks the original message ordering, meaning downstream applications must tolerate out-of-order data.

Log-based systems simplify this by using partitioned logs and consumer groups. A topic is divided into a fixed number of partitions, and each partition is assigned to exactly one consumer within a group. This assignment ensures that a single partition is processed in strict sequential order. Because the consumer only needs to persist a single integer offset representing its progress, the broker is freed from tracking individual message handshakes. This design allows log-based brokers to achieve massive throughput and durability.

### Databases and Streams: Dual-Writes, CDC, and Event Sourcing
Keeping separate databases, search indexes, and caches in sync is a major challenge. When an application attempts to write to multiple systems directly (a practice known as dual-writing), network partitions or crash failures can easily cause the systems to diverge. For example, if the application successfully writes to a database but crashes before writing to the search index, the index is permanently outdated.

Change Data Capture (CDC) resolves this by extracting updates directly from the database's transaction log. Since the transaction log contains the ordered sequence of all committed writes, a CDC tool can read this log and emit a stream of change events. Other downstream systems consume this stream to update their local indexes and caches. This ensures that all derived state eventually matches the primary database in the correct order.

Event Sourcing takes this idea further by storing the application's state as a sequence of immutable events rather than mutating rows in place. In this model, we must distinguish between commands and events:
* **Commands**: Requests from clients that can be validated, rejected, or modified (such as "Withdraw $50 from account 123").
* **Events**: Immutable facts that have already occurred and cannot be altered or rejected (such as "Account 123 withdrew $50").

Under event sourcing, the current application state is derived by computing a fold over the event log:
$$\text{Current State} = \text{fold}(\text{events}, \text{initial\_state})$$
As the event log grows, replaying it from the beginning becomes too slow. To optimize performance, the system uses log compaction. This process periodically sweeps the log and discards outdated versions of keys, retaining only the latest value for each key. Compaction allows the system to rebuild state quickly from the compacted log without sacrificing the history of active keys.

Command Query Responsibility Segregation (CQRS) is a common architectural pattern used alongside event sourcing. Because the event log is append-only, querying it directly for complex user requests is highly inefficient. CQRS separates the write path (the commands that append to the event log) from the read path (the read-optimized materialized views). Whenever an event is appended, stream processors immediately update the read-optimized views, allowing clients to query highly structured and indexed state with sub-millisecond response times.

### Common Uses of Stream Processing
Stream processors are used in a variety of systems to perform real-time computations:

* **Complex Event Processing (CEP)**: This pattern allows you to search for specific sequences of events over time. For example, an security system might trigger an alert if it detects three failed login attempts followed by a password change within a ten-minute window.
* **Streaming Analytics**: Stream processors continuously calculate aggregates over time windows. For instance, calculating website traffic per minute or monitoring the moving average of a CPU's temperature to spot server overloads.
* **Materialized Views**: Systems can maintain up-to-date copies of state in external datastores. When a database updates, the change is propagated through a stream processor to update search indexes or caches immediately.
* **Search**: Real-time updates to full-text search systems enable search results to reflect changes within seconds of their occurrence.
* **Alerting and Decision Making**: Event streams can be used to run business logic that reacts instantly to specific conditions. For example, a credit card transaction can be sent to a stream processor that runs fraud-detection models and automatically blocks the transaction before it is completed, protecting users from theft.

### Reasoning About Time
Managing time is one of the hardest aspects of stream processing. In batch processing, we can group data by timestamps in the records. In stream processing, there is a fundamental split between processing time and event time:
* **Processing Time**: The local system clock of the machine executing the stream processing code.
* **Event Time**: The timestamp when the event was originally generated on the device (for example, a smartphone or an IoT sensor).

These two timestamps can diverge significantly due to network lags, queue backlogs, or offline devices. If a mobile user loses connection while travelling through a tunnel, their device queues up events locally. When they emerge and reconnect, all those queued events are sent at once. If we analyze user behavior using processing time, we would see an artificial spike in activity, whereas event time preserves the actual sequence of actions.

#### The Straggler Problem and Watermarks
Because events can be delayed or reordered during transit, stream processors must handle late-arriving data (known as the straggler or star runner problem). How do we know when we have received all events for a specific time window? If we are counting events in the 12:00 to 12:10 window, we cannot wait forever to output the result.

To solve this, stream processors use watermarks. A watermark is a temporal progress metric that flows through the event stream, asserting that no more events with timestamps prior to the watermark should arrive. For example, a watermark of 12:12 tells the processor that it can safely close the 12:00 to 12:10 window and emit the final count. If an event with timestamp 12:08 arrives after the 12:12 watermark, it is classified as a late event. The processor can handle these stragglers by writing them to a dead-letter queue, sending an update to the already closed window, or discarding them depending on application requirements.

#### Windowing Strategies
To aggregate unbounded data, we must slice the continuous event stream into bounded time intervals. The four primary windowing strategies are:
* **Tumbling Windows**: Fixed-size, non-overlapping intervals. For example, a 5-minute tumbling window groups events from 12:00 to 12:05, and then from 12:05 to 12:10. Every event belongs to exactly one window.
* **Hopping Windows**: Fixed-size, overlapping intervals. For instance, a 5-minute window that starts (hops) every 1 minute. This allows you to compute a 5-minute moving average refreshed every 60 seconds.
* **Sliding Windows**: Dynamic intervals defined relative to the events themselves. A sliding window of 5 minutes covers any period containing events where the gap between consecutive events is within the limit, or groups all events occurring within 5 minutes of each other.
* **Session Windows**: Dynamic, variable-sized windows defined by periods of inactivity. If a user clicks around on a website and then stops for 30 minutes, the session window closes. This is perfect for grouping a single user's continuous active session.

#### Whose Clock to Trust?
Client-side device clocks are notoriously unreliable. A user might manually set their phone's clock to the wrong timezone or drift hours off. To correct this, we can capture three timestamps for each event:
1. The device event time ($t_{\text{device}}$) when the occurrence happened according to the device's clock.
2. The transmission time ($t_{\text{send}}$) when the device uploaded the event.
3. The receipt time ($t_{\text{recv}}$) when the message broker received the event.

We can estimate the true event time ($t_{\text{true}}$) by calculating the offset between the broker's clock and the transmission time:
$$t_{\text{true}} = t_{\text{device}} + (t_{\text{recv}} - t_{\text{send}})$$
This formula assumes that the transmission latency is negligible compared to clock drift, allowing us to align user actions to a reliable server clock while preserving the relative order of device events.

Let's analyze why this mathematical offset correction works. Suppose a client's clock is running 5 minutes fast. The client generates an event at its local time 12:05:00, but the true universal time is 12:00:00. It then transmits this event at its local time 12:05:05. The server receives the event at 12:00:10 according to its highly accurate network-synchronized clock.

Using our formula:
$$t_{\text{offset}} = t_{\text{recv}} - t_{\text{send}} = 12:00:10 - 12:05:05 = -4\text{ minutes } 55\text{ seconds}$$
We calculate the true event time as:
$$t_{\text{true}} = t_{\text{device}} + t_{\text{offset}} = 12:05:00 + (-4\text{m } 55\text{s}) = 12:00:05$$
This corrected timestamp accounts for the device's clock drift and provides an accurate, consistent representation of when the event happened. The remaining 5-second discrepancy represents the network transmission delay. While this latency is not perfectly corrected, the margin of error is reduced from 5 minutes of clock drift down to a few seconds of network delay.

### Stream Joins and Their Time-Dependence
Joining dynamic streams requires keeping state over time. The three common patterns of stream joins are:

1. **Stream-Stream Join**: Both inputs are event streams. For example, a search engine joins a stream of search queries with a stream of ad clicks. The join matches events on a shared key (such as Query ID) within a specific time window (like a 1-minute window). To do this, the processor must keep a local buffer of recent queries and clicks. When a click event arrives, it is matched against the query buffer, and if a query event arrives, it checks the click buffer.

2. **Stream-Table Join**: An event stream is joined with a database table. For instance, enriching an e-commerce order stream with user profile data. The stream processor can keep a local copy of the user table in memory (using RocksDB or a similar local store) and keep it updated in real-time by subscribing to a Change Data Capture stream of user updates. When an order event arrives, the processor simply reads the current user state from its local database and emits the enriched event.

3. **Table-Table Join**: Both inputs are database tables, represented as streams of updates. This join maintains a materialized view of two tables (for example, joining a user table and a subscription table). The processor listens to CDC streams from both tables and updates a local join view. Every incoming update triggers a recalculation of the joined record, emitting a stream of change events for the final materialized table.

A major complication in stream joins is time-dependence. If an order event arrives with event time 12:05, but we enrich it with the user table state at 12:10 (because the user changed their address in those 5 minutes), we might emit an incorrect join result that uses future state. To guarantee consistency, stream-table joins must use versioned table states. The processor must join the order event at 12:05 against the user profile *as it existed* at 12:05, requiring temporal indexing of the table state.

### Fault Tolerance, Checkpointing, and State Rebuilding
How do we ensure that a stream processor can recover from crashes without corrupting its state or duplicating outputs? There are two primary paradigms for achieving fault tolerance in unbounded processing:

1. **Microbatching**: The stream processor slices the incoming stream into tiny batches (for example, every 1 second) and processes each batch as a small batch job. This is the approach taken by Apache Spark Streaming. It allows the system to reuse standard batch-processing fault tolerance mechanisms. If a node crashes, the system simply re-runs the microbatch on another node. However, this introduces an inherent latency floor of at least the batch interval.

2. **Checkpointing**: The system processes events individually to minimize latency, but periodically takes a snapshot of its local state (such as RocksDB contents) and saves it to a durable store (like HDFS or S3). This is the approach used by Apache Flink, often utilizing the Chandy-Lamport distributed snapshot algorithm. A checkpoint acts as a global, consistent savepoint. If a crash occurs, all nodes roll back to the last successful checkpoint and replay events from the offsets recorded during that checkpoint.

To guarantee exactly-once processing (or "effectively-once"), we must couple state updates with output messages. An atomic commit is required so that the offset progress, the local database state, and the outgoing messages are committed together. If the state updates but the output fails, or vice versa, the system will become inconsistent. Some stream processors use two-phase commit protocols to write downstream transactionally.

Idempotence is the most reliable fallback for downstream systems. If an event is replayed and processed twice, an idempotent system ensures the final state is unchanged. For example, updating a user's address to "123 Main St" is idempotent, whereas incrementing their balance by $10 is not. By designing downstream operations to be idempotent, we can tolerate event duplication during recovery without corrupting the final state.

Rebuilding state from a crash is the final piece of the fault tolerance puzzle. If a node fails, the job manager reallocates its partition to a healthy standby node. This standby node retrieves the last recorded checkpoint and loads it into its local RocksDB store. It then looks up the committed offset corresponding to that checkpoint and requests the message broker to replay all subsequent events. Because the broker retained those events on disk, the standby node can sequentially catch up to the current stream head, restoring full processing state with minimal interruption.

### Worked Examples with Numbers

Let's explore three detailed scenarios to see how stream processing handles joins, late events, and consistency.

#### Example 1: Stream-Stream Join with a 1-Minute Window
Imagine we are building an ad-tech pipeline to join a stream of search queries and a stream of ad clicks. The goal is to detect which queries resulted in a click within 1 minute.
* **Query Stream**: Emits `(query_id, query_term, event_time)`
* **Click Stream**: Emits `(query_id, ad_id, event_time)`

Suppose the following events occur:
1. At event time `12:01:05`, Query A arrives: `(Q101, "running shoes", 12:01:05)`.
2. At event time `12:01:10`, Query B arrives: `(Q102, "water bottle", 12:01:10)`.
3. At event time `12:01:50`, Click A arrives: `(Q101, AD_A, 12:01:50)`.
4. At event time `12:02:15`, Click B arrives: `(Q102, AD_B, 12:02:15)`.

Let's trace how the stream processor evaluates these with a 1-minute sliding join window:
- When Query A `Q101` arrives at `12:01:05`, the processor stores it in the query state buffer. It checks the click state buffer for `Q101`. No click is found, so it waits.
- When Query B `Q102` arrives at `12:01:10`, it is also stored in the query state buffer. The click state buffer is empty, so it waits.
- When Click A `(Q101, AD_A)` arrives at `12:01:50`, the processor checks the query state buffer. It finds Query `Q101`, then calculates the time difference: `12:01:50 - 12:01:05 = 45 seconds`. Since 45 seconds is within the 1-minute window, a join is successful. The processor emits `(Q101, "running shoes", AD_A)` and can purge both from the buffers.
- When Click B `(Q102, AD_B)` arrives at `12:02:15`, the processor checks the query state buffer. It finds Query `Q102`, then calculates the time difference: `12:02:15 - 12:01:10 = 1 minute 5 seconds (65 seconds)`. Since 65 seconds exceeds the 1-minute window, the processor determines that the click is too late to be joined. The query `Q102` is eventually evicted from the state buffer as the window slides forward, and Click B is discarded or logged as an unjoined click.

#### Example 2: Event Time Windowing, Watermarks, and Late Events
Let's monitor user high scores in a mobile game over a tumbling 10-minute event-time window (specifically, `12:00:00` to `12:10:00`).

Suppose we have a user whose cellular connection is spotty. Here is the timeline of events:
1. **Event A**: User scores 100 points. Event time on phone is `12:03:00`. It arrives at the broker at processing time `12:05:00`.
2. **Event B**: User scores 150 points. Event time on phone is `12:08:00`. Due to a network drop, it does not arrive immediately.
3. **Event C**: User scores 200 points. Event time on phone is `12:09:00`. This event also stalls in transit.
4. **Watermark update**: The system's watermark (defined as `Max Event Time Seen - 3 minutes` to tolerate minor network lag) moves as events arrive.

Let's watch how the system processes this step-by-step:
- At processing time `12:05:00`, Event A `(score=100, event_time=12:03:00)` is processed. This updates the maximum event time seen to `12:03:00`, which sets the watermark to `12:00:00` (calculated as `12:03:00 - 3 minutes`). The tumbling window `12:00:00 - 12:10:00` is currently open, so the score 100 is added to its aggregate.
- At processing time `12:11:00`, another user's event arrives: `(score=50, event_time=12:12:00)`. This pushes the maximum event time seen to `12:12:00`. Consequently, the watermark advances to `12:09:00` (calculated as `12:12:00 - 3 minutes`). Since the watermark `12:09:00` is still less than `12:10:00`, the `12:00:00 - 12:10:00` window remains open.
- At processing time `12:14:00`, a third user's event arrives: `(score=80, event_time=12:14:00)`. This changes the maximum event time seen to `12:14:00`. As a result, the watermark advances to `12:11:00`. Since the watermark `12:11:00` has crossed the window end boundary of `12:10:00`, the system assumes no more events from before `12:10:00` will arrive. It closes the `12:00:00 - 12:10:00` window and emits the total score: `100` (from Event A).
- At processing time `12:15:00`, the network reconnects, and the delayed Event B `(score=150, event_time=12:08:00)` and Event C `(score=200, event_time=12:09:00)` finally arrive. The system looks at their event times. Because the watermark is already at `12:11:00`, these events are classified as late. Windows representing that period are closed, meaning they cannot be included in the normal aggregate. They are routed to a dead-letter storage, or used to trigger a retroactive correction stream.

#### Example 3: Dual-Write Inconsistency vs. CDC Sequencing
Suppose we are building an e-commerce platform with a PostgreSQL database and an Elasticsearch index. A product's price is updated twice in rapid succession:
* Update 1: Change price from $100 to $120.
* Update 2: Change price from $120 to $130.

Let's examine how failures can occur in both architectures:

**Scenario A: The Dual-Write Approach**
1. The application attempts to execute Update 1. It successfully writes the price `$120` to Postgres.
2. Concurrent with Update 1, another application thread runs Update 2. It successfully writes `$130` to Postgres.
3. Due to network routing delays, the Elasticsearch write for Update 2 arrives at the index first, setting the price to `$130`.
4. The delayed Elasticsearch write for Update 1 arrives at the index last, overwriting the price to `$120`.
5. Postgres now shows `$130` (correct), but Elasticsearch shows `$120` (incorrect). The search index is permanently out of sync because there was no centralized ordering mechanism for the writes.

**Scenario B: The CDC-Based Log Approach**
1. The application writes Update 1 to Postgres, which appends a price-change log record to the database's write-ahead log (WAL).
2. Subsequent to this, the application writes Update 2 to Postgres, appending a second record to the WAL.
3. A CDC tool (like Debezium) continuously tails the Postgres WAL and pushes these change events into a partitioned Kafka log. Because Kafka partitions guarantee strict FIFO ordering, the events are written to the Kafka partition as:
   - Partition log slot 101: `(Product_ID=999, Price=$120)`
   - Partition log slot 102: `(Product_ID=999, Price=$130)`
4. An Elasticsearch sync consumer reads Kafka sequentially. It processes slot 101 first, setting the price to `$120`. Next, it processes slot 102, overwriting the price to `$130`.
5. Both Postgres and Elasticsearch end up at `$130`. Eventual consistency is guaranteed because all updates are forced through the same sequential, partitioned log.

## Pros
- **Near-Real-Time Responsiveness**: Low latency processing allows immediate detection and response to critical business events.
- **Improved Fault Isolation**: Log-based systems decouple producers from consumers, protecting writing applications from downstream crashes.
- **Accurate Time-Based Calculations**: Event-time semantics ensure aggregations are logically correct even when client data arrives delayed.
- **Flexible Scalability**: Partitioned logs allow both storage and processing power to scale horizontally by adding more partitions.
- **Simplified Reprocessing**: Log preservation makes it easy to deploy a new feature by simply replaying the historical event stream from any past offset.

## Cons
- **High System Complexity**: Running distributed log brokers and streaming engines demands substantial operational overhead.
- **Eventually Consistent State**: Derived views are inherently laggy, meaning downstream reads can be out of sync with the primary database.
- **State Storage Demands**: Windowed aggregations and joins require storing large datasets in memory or local RocksDB instances.
- **Difficult Global Consistency**: Coordinating transactional boundaries across different streams is hard and requires complex protocols.
- **Operational Monitoring Burden**: Substantial telemetry is required to track consumer lag, buffer sizes, and watermark alignment across hundreds of partitions.

## Alternatives
- **Batch Processing**: Slices continuous data into fixed chunks (such as hourly files) and runs a MapReduce or Spark job over them. It differs by sacrificing real-time speed for operational simplicity and exact determinism. Choose this option when latency is not a priority and you need a simple, consistent view of historical data.
- **Synchronous Request-Response**: Uses direct HTTP or gRPC API calls to communicate updates immediately between microservices. It differs by lacking durable buffering and decoupling. Choose this approach for standard CRUD workloads where transactional consistency is more important than massive throughput.
- **Database Polling**: Runs cron jobs to periodically query a database for new or modified rows using an incremental ID or timestamp. It differs by placing a heavy query load on the primary transactional database. Choose this method for simple, low-frequency updates where setting up dedicated streaming infrastructure is not justified.

## When to use it
Reach for stream processing when you have high-volume, continuous data feeds that require immediate response or real-time views. Typical scenarios include:
* Real-time security auditing and financial fraud detection systems.
* Continuous monitoring of infrastructure health with alert generation under a second.
* Maintaining up-to-date read replicas, search indexes, or caches via CDC streams.
* Calculating rolling aggregate metrics (like hourly active users or daily trending topics).

## When NOT to use it
Avoid stream processing when:
* You need to perform massive, complex historical reporting over years of data. Reach for a column-oriented analytical data warehouse and run standard SQL batch queries instead.
* Immediate, absolute consistency is required across all user-facing read views. Use a single transactional relational database with synchronous API calls instead.
* The system is a simple CRUD application with low traffic. Implement standard synchronous API routes with local database transactions to avoid unnecessary infrastructure overhead.

## Key takeaways / mental model
Think of stream processing as an active, flowing river of events. Producers are like tributaries dumping water (messages) into the river, and consumers are like waterwheels on the bank processing the flow as it passes. Some waterwheels count passing items, some filter out dirt, and others divert water into storage reservoirs (caches). If a waterwheel breaks down, it does not lose any data. It simply checks its physical position along the riverbank (its offset) and resumes processing from that exact spot once it is repaired.

## Self-check questions
1. What are the main operational and architectural differences between a transient message broker like RabbitMQ and a log-based broker like Kafka?
2. Explain how a client device's clock drift can corrupt event-time analytics. How can a three-timestamp approach help resolve this issue?
3. What is a watermark, and how does it help a stream processor decide when to close a time window and handle late-arriving events?
4. Compare stream-stream joins with stream-table joins. Why do stream-stream joins require keeping state in bounded memory windows?
5. Imagine a system where you need to calculate real-time fraud alerts and also generate a daily billing report. Would you use stream processing for both, or would you use a combination of batch and stream? Why?
6. Describe the dual-write problem. Why is Change Data Capture (CDC) a more reliable alternative for keeping a database and search index in sync?
7. Describe how the Chandy-Lamport distributed snapshot algorithm coordinates checkpointing across multiple parallel stream operators. Why must an operator align its input barriers before taking a state snapshot?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 11
- Streaming Systems (Tyler Akidau, Slava Chernyak, Reuven Lax)
