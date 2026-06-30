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
Stream processing operates on unbounded, continuous streams of events as they occur, providing low latency updates compared to offline batch jobs. It uses distinct messaging architectures, including transient message brokers and durable, replayable log-based brokers like Apache Kafka. Processing unbounded streams requires managing differences in time semantics, handling late data with windowing strategies, and executing exactly-once semantics using idempotence or distributed transactions.

## The idea
How do we handle data that is constantly being generated and never stops? In our discussion of batch processing in [14-batch-processing.md](./14-batch-processing.md), we saw how jobs run on bounded, static datasets. However, real-world data is often continuous: user activity, financial transactions, and sensor measurements happen around the clock. Waiting for a daily batch job to run means our systems are always reacting to yesterday's news.

Stream processing solves this by treating data as an unbounded, never-ending event stream. Instead of waiting for a file to close before reading it, a stream processor handles events as they arrive, reducing the latency between data generation and processing down to seconds or milliseconds. This model exists to provide continuous, near-real-time visibility and reaction to ongoing activity.

## How it works
Unbounded stream processing relies on messaging systems to transport events, techniques to capture database changes, and specialized windowing and join algorithms.

### Event Streams and Messaging Systems
An event is a small, self-contained, immutable object containing the details of something that happened at a specific point in time. A generator (or producer) writes an event once, and one or more consumers process it.

We can categorize messaging systems into three broad patterns:

1. **Direct Messaging**:
   Producers talk directly to consumers over network sockets (for example, HTTP or TCP). This requires both systems to be online at the same time and does not tolerate consumer downtime or network partitioning.

2. **Traditional Message Brokers (AMQP/JMS)**:
   A broker acts as a centralized intermediary. When a producer sends a message, the broker stores it in memory or on disk. The broker then delivers it to consumers. Once a consumer acknowledges that it processed the message, the broker deletes it. Examples include RabbitMQ or ActiveMQ. This pattern is ideal for distributing work to a pool of workers, but it doesn't preserve message order and is not replayable.

3. **Log-Based Message Brokers (Apache Kafka)**:
   A log-based broker combines the durability of a database with the low latency of a message broker. It stores messages as an append-only sequence on disk, partitioned across multiple machines. Consumers read the log sequentially and track their progress using an offset, which is just a pointer to the last read message. Multiple consumers can read the same log independently. The messages are not deleted upon acknowledgement. Instead, they remain in the log for a configured retention period, allowing consumers to replay historical events at any time.

### Change Data Capture (CDC) and Event Sourcing
How do we get streams of events out of a standard database?
* **Change Data Capture (CDC)**:
  CDC tools monitor a database's transaction log (like PostgreSQL's write-ahead log) and emit a stream of events representing every insert, update, or delete. This allows other systems (like search indexes or caches) to stay in sync with the database in real-time.
* **Event Sourcing**:
  This approach stores all changes to the application state as a sequence of immutable events. Instead of saving the current balance of a bank account, you store every single deposit and withdrawal. The current balance is derived by replaying the entire history of events.

### Stream Joins
Joining streams is much more complex than joining static tables because the data is constantly moving:

* **Stream-Stream Joins**:
  Both inputs are event streams (for example, joining a stream of search queries with a stream of search ad clicks). The processor must keep a window of recent events for both streams in memory. When a query event arrives, it looks for a matching click in its window, and vice versa.
* **Stream-Table Joins**:
  One input is a stream, and the other is a database table (for example, enriching a stream of user actions with user profile data). The processor can query the table for each event, or keep a local copy of the table in memory and update it using a CDC stream.
* **Table-Table Joins**:
  Both sides are tables, represented as streams of updates (for example, joining user profiles with user subscriptions). The output is a continuous stream of changes to the joined result.

### Event Time vs. Processing Time
A major challenge in stream processing is managing time.
* **Processing Time**: The time on the machine running the stream processor when it processes the event.
* **Event Time**: The time when the event actually occurred on the device (for example, a mobile phone's clock).

These two times can differ significantly due to network delays, offline mobile devices, or queue backlogs. If a user loses connection on a train, their phone might queue up events for hours and send them all at once when they reconnect. If we analyze user behavior using processing time, we get a huge, artificial spike of activity when they reconnect, whereas event time shows the true distributed nature of their behavior.

### Windowing and Late Events
To aggregate unbounded data, we must slice it into chunks using windows:
* **Tumbling Window**: Fixed-size, non-overlapping time intervals (such as 10:00 to 10:05, 10:05 to 10:10).
* **Hopping Window**: Fixed-size, overlapping intervals (such as a 5-minute window that starts every 1 minute).
* **Sliding Window**: Moving intervals based on actual event occurrences (such as any 5-minute interval containing events).
* **Session Window**: Dynamic windows defined by periods of inactivity (such as grouping events until there is a 30-minute gap).

To handle late-arriving events (where event time falls outside the currently active window), stream processors use **watermarks**. A watermark is a temporal progress indicator that estimates how far behind the stream is. If a watermark passes a certain timestamp, the processor assumes no more events prior to that timestamp will arrive and closes the window. Any events arriving after the watermark are considered late and are handled using special rules, like writing them to a dead-letter queue or updating the already-emitted window results.

### Exactly-Once Semantics
What happens if a stream processor crashes halfway through processing an event?
To achieve exactly-once processing (which actually means "effectively once" execution), the system must guarantee that any side effects of processing an event (like updating a database or writing a message) occur exactly once, even if the event is re-delivered.
We can achieve this using two main approaches:
1. **Idempotence**: Designing the processing logic so that running it multiple times has the exact same effect as running it once (for example, setting a value instead of incrementing it).
2. **Atomic Commits**: Using a two-phase commit protocol or a unified state store where state updates and output messages are committed together in a single transaction (for example, Apache Flink's Chandy-Lamport checkpointing algorithm).

## Pros
- **Very Low Latency**: Processing events as they arrive enables near-real-time alerting, monitoring, and reaction.
- **Accurate Time Analytics**: Using event time allows systems to accurately group and analyze historical actions, even when network delays or offline devices cause out-of-order delivery.
- **Decoupled Architecture**: Log-based messaging systems allow producers and consumers to scale independently, tolerating spikes in traffic and machine failures.
- **Continuous Integration of State**: CDC and event sourcing enable real-time replication and caching, ensuring secondary indexes remain consistent with primary databases.

## Cons
- **High Operational Complexity**: Managing distributed stream processors and log partitions is significantly harder than running simple batch jobs.
- **Handling Out-of-Order Data**: Dealing with watermarks, late events, and clock drift on client devices requires careful tuning and design.
- **State Storage Overhead**: Keeping large windows of state in memory for joins or aggregations requires durable local state stores (like RocksDB) and increases memory consumption.
- **Lack of Global Consistency**: Implementing transactions and consensus across independent streams is extremely difficult and requires complex coordination protocols.

## Alternatives
- **Batch Processing**: Slices the incoming stream into periodic files (such as hourly chunks) and runs a batch job over each file. This reduces system complexity and simplifies error handling, but it increases latency to hours.
- **Request-Response Services**: Online microservices that communicate synchronously via APIs. This is simple and low latency, but it lacks the scalability, persistence, and durability of log-based stream processors.
- **Polling Databases**: Periodically querying a database for new rows using timestamps. This is simple to implement on top of existing SQL databases, but it places a heavy query load on the database and introduces latency.

## When to use it
Stream processing is the correct approach when you need to act on data immediately as it occurs. Typical use cases include:
- Real-time fraud detection and security alerting.
- Monitoring critical system metrics and generating immediate alerts.
- Maintaining read caches, search indexes, or materialized views updated from a primary database via CDC.
- Calculating rolling metrics, like website visits or trending hashtags, over sliding windows.

## When NOT to use it
Do not use stream processing when:
- You need to perform massive, complex historical analysis over years of data. Use batch processing or an analytical data warehouse instead.
- Your computations require a globally consistent view of all data at a single point in time. Batch processing is far more reliable and easier to coordinate for this task.
- You are building a standard CRUD application with low transaction rates. A relational database with synchronous API calls is a simpler, more stable choice.

## Key takeaways / mental model
Think of stream processing as an active, moving river of events. Producers dump logs into the river, and consumers stand on the banks, processing the water as it flows past. Some consumers might filter the water, others might count the fish passing by within five-minute windows, and some might redirect the water to secondary reservoirs (caches). If a consumer falls over, they don't lose their place because they can look at their physical position along the riverbank (their offset) and pick up right where they left off.

## Self-check questions
1. What is the fundamental architectural difference between an AMQP message broker and a log-based message broker like Kafka?
2. Why is event time usually preferred over processing time, and what challenges does it introduce?
3. How does a tumbling window differ from a sliding window?
4. How can we achieve exactly-once processing semantics in a system that can experience failures?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 11
