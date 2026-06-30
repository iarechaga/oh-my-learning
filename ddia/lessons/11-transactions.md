---
id: ddia/11
subject: ddia
title: Transactions: ACID, Isolation, and Serializability
slug: transactions
status: drafted
mastery:
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 7
prerequisites: [ddia/01]
created: 2026-06-30
updated: 2026-06-30
---

# Transactions: ACID, Isolation, and Serializability

## TL;DR
A transaction is a way for an application to group multiple reads and writes together into a single logical unit. If any part of the transaction fails, the entire transaction is aborted and rolled back, preventing partial updates. This abstracts away the complexity of managing hardware errors, software crashes, and concurrency bugs, allowing developers to write simpler and safer code.

## The idea
In a real-world system, many things can go wrong. The network can drop connections, the database server can lose power, multiple clients can write to the same record simultaneously, or an application crash can interrupt a multi-step update. Without transactions, handling these partial failures is incredibly difficult, forcing developers to write complex error-handling logic for every single database operation.
Transactions solve this by grouping multiple database operations into a single execute-or-rollback block. It simplifies the application's mental model. Instead of worrying about partial failures, the application can assume that either everything succeeded or nothing happened at all.
As we discussed in [01-reliability-scalability-maintainability.md](01-reliability-scalability-maintainability.md), building reliable systems is hard. Transactions are one of the most powerful tools databases provide to keep application logic clean and resilient.

## How it works
To understand transactions, we must examine the formal definition of ACID, the classic concurrency anomalies that occur when safety is compromised, and the isolation levels databases use to prevent them.

### The Real Meaning of ACID
While relational databases have used the term "ACID" since the 1980s, its exact meaning is often obscured by marketing. Let us define what each letter actually means:

- **Atomicity (Abortability)**: Unlike the chemical definition of atomicity, in databases, atomicity is not about concurrency. It describes what happens when a transaction is interrupted mid-execution. This guarantee ensures that if a transaction consists of five writes and the system crashes on the fourth, all previous writes are discarded, returning the database to its pristine pre-transaction state.
- **Consistency (Application Invariants)**: Consistency is the odd one out because it is primarily an application-level property rather than a database guarantee. It means that the transaction must transition the database from one valid state to another, maintaining application-level invariants (e.g., a bank account balance must never fall below zero). While the database can enforce basic constraints like foreign keys or unique indexes, it cannot understand your custom business logic. Thus, consistency is the application's responsibility.
- **Isolation (Concurrency Control)**: Isolation ensures that concurrently running transactions do not interfere with or corrupt each other's state. In a perfect world, isolation makes every transaction feel as though it is the only transaction running on the entire database.
- **Durability (Persistence)**: Once a transaction completes successfully, any data it wrote is guaranteed to survive even if the hardware crashes or the system loses power. In single-node databases, durability usually means writing data to a non-volatile write-ahead log on disk.

In contrast, many NoSQL systems reject ACID in favor of "BASE" (Basically Available, Soft state, Eventual consistency), which prioritizes scaling and availability over strict correctness guarantees.

### Concurrency Anomalies
When databases execute transactions concurrently without strict isolation, they suffer from several well-known anomalies:

1. **Dirty Reads**: A transaction reads data that was written by another transaction but has not yet been committed. If the other transaction aborts, the first transaction has read data that technically never existed.
2. **Dirty Writes**: A transaction overwrites data that was written by another active, uncommitted transaction. This can lead to mixed states where parts of one transaction are overwritten by another, breaking database consistency.
3. **Read Skew (Non-Repeatable Reads)**: A client reads a record at time A, another transaction updates and commits that record, and the client reads it again at time B, seeing a different value. For instance, reading a bank account balance across two accounts while a transfer is in progress can show a temporarily incorrect total balance.
4. **Lost Updates**: Two concurrent transactions read a value, modify it (e.g., incrementing a counter), and write it back. One update overwrites the other, causing the database to lose one of the increments.
5. **Write Skew**: This is a generalization of the lost update problem. Two transactions read the same data, make a decision based on those values, and write different records, which breaks an application invariant. Both doctors try to take time off at the same time. Each doctor checks the database, sees that two doctors are on call, and approves their own leave. The system now has zero doctors on call.
6. **Phantoms**: A transaction queries a set of rows matching a search condition, another transaction inserts or deletes rows matching that condition, and the first transaction queries again, seeing a different set of rows (the "phantoms").

### Weak Isolation Levels
To balance performance and safety, databases offer different isolation levels. The weaker levels offer better performance but permit certain anomalies.

- **Read Committed**: The baseline isolation level for many databases. It prevents dirty reads by only returning committed data, and prevents dirty writes by using row-level locks on active transactions.
- **Repeatable Read / Snapshot Isolation**: This level prevents read skew. It is usually implemented using Multi-Version Concurrency Control (MVCC). When a transaction starts, it receives a transaction ID. The database keeps multiple versions of each row, with headers indicating which transaction created and deleted each version. When reading, the transaction only sees data that was committed before its start time, ensuring a consistent snapshot of the database.

### Preventing Lost Updates
Lost updates can be prevented using several techniques:
- **Atomic Operations**: Many databases support atomic write operations (e.g., `UPDATE counters SET value = value + 1 WHERE id = 1`), eliminating the need to read the value into the application.
- **Explicit Locking**: Applications can explicitly lock the row they want to update using `SELECT ... FOR UPDATE`, forcing other transactions to wait.
- **Compare-and-Set**: Database engines only apply an update if the value has not changed since the application last read it (e.g., `UPDATE wiki SET content = 'new' WHERE id = 1 AND content = 'old'`).

### Serializability
The strongest isolation level is serializability. It guarantees that the outcome of running transactions concurrently is identical to running them one after another, sequentially. There are three main ways to implement serializability:

1. **Literal Serial Execution**: We remove all concurrency and execute every single transaction sequentially on a single thread. This is highly efficient for in-memory databases like Redis, but requires transactions to be short and fit in memory.
2. **Two-Phase Locking (2PL)**: Used by relational databases for decades. It is a pessimistic approach. If transaction A wants to read a row, it must acquire a shared lock. Writing a row requires an exclusive lock instead. If transaction B wants to write to a row that transaction A is reading, it must wait until transaction A commits or aborts. The "two phases" mean locks are acquired in the first phase and only released at the end of the transaction in the second phase. This prevents all anomalies but can cause massive performance bottlenecks and frequent deadlocks.
3. **Serializable Snapshot Isolation (SSI)**: A modern, optimistic approach. It runs transactions on snapshot isolation without locking. However, as the transaction executes, the database tracks when it reads data that might have changed. Before committing, the database checks if any of those reads were invalidated by concurrent writes. If so, the transaction is aborted and must be retried. This performs beautifully when conflict rates are low.

## Pros
- Drastically simplifies application code by offloading error-handling, retry, and concurrency logic to the database engine.
- Prevents database corruption and race conditions, ensuring that business-critical data remains correct and consistent.
- Allows developers to reason about database state deterministically without worrying about unexpected partial failures.

## Cons
- Strong isolation levels can severely degrade database performance, throughput, and latency due to lock contention or frequent transaction aborts and retries.
- Implementing transactions across multiple partitioned databases or microservices requires expensive distributed transaction protocols like Two-Phase Commit (2PC), which are fragile and slow.
- Active transactions can consume significant database resources, such as memory for MVCC version tracking or lock tables.

## Alternatives
- **BASE (Basically Available, Soft State, Eventual Consistency)**: Often used in NoSQL databases. It differs by giving up strict transactional consistency to achieve extremely high write availability and horizontal scalability, leaving the application to handle any inconsistencies.
- **Sagas / Compensation-Based Workflows**: Used in distributed microservice architectures. Instead of a single database transaction, the system runs a sequence of local transactions. If one step fails, the system executes compensation transactions to reverse the previous changes. This differs because it does not lock database rows across services, but it is much more complex to implement.

## When to use it
Use transactions when your application performs multi-step read and write operations where data correctness is paramount. This is essential for financial ledgers, booking systems, inventory management, user authentication, and any scenario where a partial update would lead to corrupted business states.

## When NOT to use it
Avoid heavy database transactions when building high-throughput, low-latency systems that process independent, transient, or low-value data. Examples include real-time log ingestion, IoT sensor telemetry, and social media clickstream tracking. For these workloads, a highly available, eventually consistent key-value store or stream processor is far more appropriate.

## Key takeaways / mental model
Think of a transaction like boarding an international flight. You must drop your bags, clear security, and scan your boarding pass. If you fail any of these steps, you do not get to fly, and your bags are returned to you. The entire process is aborted, and your physical location is reverted to where you started. Isolation is like having your own private security lane, ensuring other passengers cannot interfere with your boarding process.

## Self-check questions
1. What is the precise difference between Atomicity and Isolation in the context of ACID?
2. Explain how Multi-Version Concurrency Control (MVCC) implements snapshot isolation without requiring read locks.
3. Describe the "write skew" anomaly and explain why Read Committed and Snapshot Isolation are unable to prevent it.
4. How does Two-Phase Locking (2PL) differ from Two-Phase Commit (2PC), and what concurrency problems does each solve?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 7
- [01-reliability-scalability-maintainability.md](01-reliability-scalability-maintainability.md)
