---
id: ddia/11
subject: ddia
title: Transactions: ACID, Isolation, and Serializability
slug: transactions
status: drafted
mastery:
seniority: senior
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 7
prerequisites: [ddia/01]
created: 2026-06-30
updated: 2026-06-30
---

# Transactions: ACID, Isolation, and Serializability

## TL;DR
A transaction groups multiple reads and writes into a single logical execution block. If any operation within that block fails, the database aborts the transaction and discards all partial writes to prevent database corruption. This abstraction shields applications from complex concurrency issues, hardware failures, and network glitches.

## The idea
In a perfect world, database engines would run without interruptions, hardware would never fail, and only one client would modify data at a time. Real-world systems are messy, filled with sudden power cuts, network disconnections, application crashes, and race conditions. Dealing with these errors manually requires writing extensive error-handling logic for every query.

Transactions solve this by packaging multiple operations into a single execute-or-rollback block. It simplifies the mental model of the application. The database guarantees that either all writes succeed or none do.

Despite its simple promise, the transaction concept is slippery. Different database engines implement varying isolation levels with inconsistent naming conventions. Historically, NoSQL databases in the late 2000s discarded transactions to optimize for horizontal scale, advocating for BASE. However, developers soon learned that managing soft state and eventual consistency manually is incredibly difficult, sparking a massive return to transactional guarantees in modern distributed systems.

## How it works
Understanding transactions requires breaking down their formal guarantees, analyzing execution errors, and exploring isolation levels.

### Single-Object vs Multi-Object Operations
A multi-object transaction coordinates changes across multiple rows, tables, or partitions. It requires a mechanism to track which operations belong together. This tracking is done via a transaction identifier.

In contrast, single-object operations target only one database record. Many databases offer atomic single-object guarantees, such as an increment operation or a compare-and-swap write. While these prevent lost updates on a single row, they are not transactions. They cannot protect you when updating a bank balance across two separate accounts, where both rows must change together or not at all.

### Aborts and the Caveats of Retries
The core of transaction atomicity is the abort. If a transaction cannot complete, the database aborts it, discarding all changes. The application must then decide how to handle the abort. Typically, the correct response is to retry the transaction.

However, retrying transactions is not a silver bullet. You must consider several major caveats:
1. **Network failures**: If the database successfully commits a transaction but the network drops before sending the acknowledgment, the application thinks it failed. Retrying it will execute the transaction twice, creating duplicate data unless you use an idempotent mechanism.
2. **Overload**: If the database aborts transactions due to high contention or congestion, retrying them immediately will worsen the overload. You must use exponential backoff to allow the system to recover.
3. **Side effects**: If a transaction sends an email or triggers an external API call, that side effect cannot be rolled back by the database. The external action will trigger again on every retry.

### Weak Isolation Levels in Depth
Executing transactions sequentially is slow, so databases use concurrent execution. This concurrency introduces race conditions. To control these risks, databases offer weak isolation levels.

#### Read Committed
The baseline isolation level for modern databases. It guarantees:
- **No Dirty Reads**: You only see data that has already been committed. You never see temporary, uncommitted writes from other transactions.
- **No Dirty Writes**: If transaction A is modifying a row, transaction B must wait until transaction A commits or aborts before it can overwrite that row.

To prevent dirty writes, databases use row-level locks. A transaction must acquire a lock on a row before writing to it, holding that lock until it finishes.

Preventing dirty reads with locks is highly inefficient because slow writes can block readers. Instead, most databases keep the old committed value of the row. Any transaction reading the row simply receives this old committed version. Only when the writing transaction commits does the database switch to serving the new value.

#### Snapshot Isolation (Repeatable Read)
Read Committed prevents dirty reads but still allows read skew. Read skew occurs when a transaction reads two different values at different points in time because a concurrent transaction committed a change in between.

Snapshot Isolation solves read skew. When a transaction starts, it reads a consistent snapshot of the database. It only sees data that was committed before the transaction started. Even if other transactions commit writes while this transaction is active, it sees the same consistent state throughout its lifetime.

This is implemented using Multi-Version Concurrency Control (MVCC). The database keeps multiple versions of each row. Each version is marked with the transaction ID that created it, and the transaction ID that deleted it, if applicable.

When a transaction reads, the database uses visibility rules to filter rows:
1. The reader ignores any row created by a transaction that was still active (uncommitted) when the reader started.
2. The reader ignores any row created by an aborted transaction.
3. The reader ignores any row with a creation transaction ID higher than the reader's own transaction ID.
4. All other rows are visible.

The SQL-standard definition of repeatable read is deeply flawed. It was written in the 1990s based on lock-based implementations, failing to account for MVCC. Consequently, different databases use different terms. Oracle calls its snapshot isolation "Serializable", while Postgres and MySQL call theirs "Repeatable Read".

### Preventing Lost Updates
A lost update occurs when two transactions read a value, modify it, and write it back concurrently. The second write overwrites the first, losing one of the modifications. We can prevent this using five main approaches:

1. **Atomic Operations**: The database performs the modify-and-write step in a single step using internal database locks.
   ```sql
   UPDATE accounts SET balance = balance + 10 WHERE user_id = 42;
   ```
2. **Explicit Locking**: The application forces a lock on the rows it reads, preventing other transactions from reading or writing them concurrently.
   ```sql
   SELECT * FROM accounts WHERE user_id = 42 FOR UPDATE;
   ```
3. **Automatic Detection**: The database executes transactions concurrently. If it detects a lost update about to happen, it automatically aborts the offending transaction, forcing it to retry. Postgres and Oracle implement this.
4. **Compare-and-Set**: The update only succeeds if the value has not changed since the last read.
   ```sql
   UPDATE wiki SET content = 'New text' WHERE id = 101 AND content = 'Old text';
   ```
5. **Conflict Resolution**: In replicated databases with multi-leader or leaderless topologies, concurrent writes create multiple versions of a row. The system merges these versions using Last-Write-Wins (LWW) or CRDTs.

### Write Skew and Phantoms in Depth
Write skew is a generalization of the lost update problem. In write skew, transactions read the same data, make a decision, and then write to different rows. This can violate application-level invariants.

Consider these classic write-skew examples:
- **On-Call Doctors**: Alice and Bob are doctors on call. At least one doctor must remain active. Both check if `active_count >= 2`. Seeing `2`, both submit transactions updating their status to inactive. Both transactions commit because they modify different rows (Alice's status and Bob's status). The system is left with zero doctors on call.
- **Meeting-Room Booking**: Two clients check if room A is booked at 10 AM. Finding no bookings, both insert a booking row. Both insert different rows, so they commit concurrently, creating a double-booking.
- **Claiming a Username**: Two users check if the username "skywalker" exists. Seeing no matches, both insert a registration row.
- **Multiplayer Game**: Two players move their avatars to the exact same cell simultaneously. Each transaction checks if the cell is occupied, finds it empty, and updates its avatar's coordinate.
- **Double-Spending**: A user has $100. They submit two concurrent withdrawal requests for $100 through different channels. Both check the balance, see $100, and insert a withdrawal record.

These anomalies share a pattern. A transaction queries for rows matching some condition, makes a decision, and writes a change. That write changes the result of the search query for the concurrent transaction, which is called a **phantom**.

We can solve this by **Materialising Conflicts**. This means transforming a phantom into a physical row in the database. For meeting rooms, you could create a table representing every room and hour slot. Transactions lock the specific room-hour row using `FOR UPDATE`. If the row doesn't exist or is locked, the transaction blocks.

### Serializability
The strongest isolation level, serializability guarantees that concurrent transactions yield the exact same outcome as if they had run one after another, sequentially. There are three primary implementations:

#### 1. Actual Serial Execution
The simplest approach is to remove all concurrency. Transactions run sequentially on a single thread. This performs exceptionally well for in-memory databases like Redis or VoltDB, because it avoids the overhead of managing locks.

However, this requires strict constraints:
- All data must fit in RAM.
- Transactions must be written as stored procedures to avoid network I/O during execution.
- You can partition the database to scale, but cross-partition transactions are extremely slow and should be avoided.

#### 2. Two-Phase Locking (2PL)
A pessimistic approach used by relational databases for decades. It must not be confused with Two-Phase Commit (2PC).

In 2PL, locks are used to block concurrent operations:
- To read a row, a transaction must acquire a shared lock. Many transactions can hold shared locks on the same row.
- To write a row, a transaction must acquire an exclusive lock. Only one transaction can hold an exclusive lock.
- If a transaction holds a shared lock, writers are blocked. If a transaction holds an exclusive lock, readers are blocked.

The "two phases" refer to:
1. **Growing Phase**: The transaction acquires locks but releases none.
2. **Shrinking Phase**: The transaction releases locks but acquires no new ones (typically done when the transaction commits or aborts).

To prevent phantoms, databases use **Predicate Locks** or **Index-Range Locks**. A predicate lock applies to all objects matching a search condition, even those not yet inserted. Since predicate locks are slow to evaluate, databases approximate them using index-range locks, which lock a range of index entries.

The main drawback of 2PL is performance. High lock contention slows down transactions, and deadlocks are common, requiring the database to abort and retry blocked transactions.

#### 3. Serializable Snapshot Isolation (SSI)
An optimistic approach that runs transactions on snapshot isolation without locks. Instead of blocking, transactions execute freely.

As transactions run, the database tracks two kinds of events:
- When a transaction reads a row that was modified by another transaction but not yet committed.
- When a transaction writes to a row that was read by another active transaction.

Before a transaction commits, the database checks if any of its reads were invalidated by concurrent writes. If the read data has changed, the database aborts the transaction, forcing a retry.

SSI performs beautifully when conflict rates are low, as it avoids the locking overhead of 2PL. Under high write contention, the frequent aborts and retries can degrade performance.

### Isolation Level and Anomaly Matrix
The table below summarizes which anomalies can occur at each isolation level.

| Isolation Level | Dirty Reads | Dirty Writes | Read Skew | Lost Updates | Write Skew / Phantoms |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Read Uncommitted** | Allowed | Prevented | Allowed | Allowed | Allowed |
| **Read Committed** | Prevented | Prevented | Allowed | Allowed | Allowed |
| **Repeatable Read** | Prevented | Prevented | Prevented | Prevented | Allowed |
| **Serializable** | Prevented | Prevented | Prevented | Prevented | Prevented |

---

### Concrete Worked Examples

#### Example 1: Bank Account Transfer (MVCC Visibility Rules)
Let us trace how snapshot isolation prevents read skew during a balance transfer between Account 1 ($100) and Account 2 ($50).

```
Database state:
- Row Account_1: Value = 100, Created_By_Tx = 50, Deleted_By_Tx = Null
- Row Account_2: Value = 50,  Created_By_Tx = 50, Deleted_By_Tx = Null

Active transactions: None. Next Transaction ID: 100.
```

1. **Tx 100 Starts (Transfer)**: Client A initiates Tx 100 to transfer $30 from Account 1 to Account 2.
2. **Tx 101 Starts (Audit)**: An auditor starts Tx 101 to check the total balance across both accounts.
   - Currently, Tx 100 is still active.
   - The database adds Tx 100 to Tx 101's list of active transactions.
3. **Tx 100 writes to Account 1**:
   - It subtracts $30 from Account 1.
   - A new row version is written: `Value = 70, Created_By_Tx = 100, Deleted_By_Tx = Null`.
   - This updates the old version: `Deleted_By_Tx = 100`.
4. **Tx 101 reads Account 1**:
   - The auditor reads Account 1.
   - Under visibility rules, it sees `Value = 100` because the $70 version belongs to Tx 100, which was active when Tx 101 began.
5. **Tx 100 writes to Account 2**:
   - It adds $30 to Account 2.
   - The database writes a new row version: `Value = 80, Created_By_Tx = 100, Deleted_By_Tx = Null`.
   - This updates the old version: `Deleted_By_Tx = 100`.
6. **Tx 100 Commits**: The database marks Tx 100 as committed.
7. **Tx 101 reads Account 2**:
   - Even though Tx 100 has committed, Tx 101's snapshot was taken when Tx 100 was active.
   - Tx 101 reads Account 2. It sees `Value = 50` because the newer version (`Value = 80`) was created by Tx 100, which is still ignored under Tx 101's snapshot rules.
   - Total balance read by Tx 101: `100 + 50 = 150`.
8. **Tx 101 Commits**: The audit completes with a perfectly consistent view of the database. Read skew was avoided.

#### Example 2: Lost Update Prevention (Compare-and-Set vs Explicit Locking)
Suppose two clients try to update a shared wiki page counter concurrently. The current counter value is 42.

**Scenario A: Compare-and-Set (without transactions)**
1. Client 1 reads counter: `42`.
2. Client 2 reads counter: `42`.
3. Client 1 issues:
   ```sql
   UPDATE wiki SET counter = 43 WHERE id = 1 AND counter = 42;
   ```
   The database finds the row with `counter = 42`, updates it to `43`, and returns a success status.
4. Client 2 issues:
   ```sql
   UPDATE wiki SET counter = 43 WHERE id = 1 AND counter = 42;
   ```
   Since the counter is now `43`, the `counter = 42` condition fails. The database updates zero rows, alerting Client 2 that the write failed. Client 2 must reread the value and retry.

*Edge Case Warning*: If the database is replicated with a multi-leader or leaderless topology, multiple nodes might accept these writes concurrently without communicating. Compare-and-set will fail to prevent lost updates in this scenario unless it runs on a single leader or uses strict consensus protocols.

**Scenario B: Explicit Locking**
1. Client 1 starts a transaction and runs:
   ```sql
   SELECT counter FROM wiki WHERE id = 1 FOR UPDATE;
   ```
   The database returns `42` and places an exclusive lock on this row.
2. Client 2 starts a transaction and runs:
   ```sql
   SELECT counter FROM wiki WHERE id = 1 FOR UPDATE;
   ```
   Because Client 1 holds an exclusive lock on the row, Client 2's query blocks.
3. Client 1 updates the value:
   ```sql
   UPDATE wiki SET counter = 43 WHERE id = 1;
   ```
4. Client 1 commits, releasing the lock.
5. Client 2's blocked query unblocks. It reads the updated value of `43`.
6. Client 2 updates the value:
   ```sql
   UPDATE wiki SET counter = 44 WHERE id = 1;
   ```
7. Client 2 commits. The counter is updated to `44`. No updates were lost.

#### Example 3: Write Skew (On-Call Doctors under Snapshot Isolation vs SSI)
Let us trace Alice (Tx 150) and Bob (Tx 151) trying to take leave under different isolation levels.

```
On-call table:
- Row Alice: Status = Active
- Row Bob: Status = Active
```

**Under Snapshot Isolation:**
1. Tx 150 (Alice) queries active count:
   ```sql
   SELECT COUNT(*) FROM doctors WHERE status = 'Active';
   ```
   Database returns `2`.
2. Tx 151 (Bob) queries active count:
   ```sql
   SELECT COUNT(*) FROM doctors WHERE status = 'Active';
   ```
   Database returns `2`.
3. Tx 150 updates Alice:
   ```sql
   UPDATE doctors SET status = 'OnLeave' WHERE name = 'Alice';
   ```
4. Tx 151 updates Bob:
   ```sql
   UPDATE doctors SET status = 'OnLeave' WHERE name = 'Bob';
   ```
5. Both transactions commit. Since they updated different rows, Snapshot Isolation detects no conflicts.
   - Result: 0 active doctors. The application invariant is broken.

**Under Serializable Snapshot Isolation (SSI):**
1. Tx 150 queries active count. The database registers that Tx 150 read the active status of Alice and Bob.
2. Tx 151 queries active count. The database registers that Tx 151 read the active status of Alice and Bob.
3. Tx 150 updates Alice's status to 'OnLeave'. This write invalidates Tx 151's previous read of Alice's status.
4. Tx 151 updates Bob's status to 'OnLeave'. This write invalidates Tx 150's previous read of Bob's status.
5. Tx 150 attempts to commit. The database checks if any transaction has written to rows that Tx 150 read. Since Tx 151 is still uncommitted, the database lets Tx 150 commit.
6. Tx 151 attempts to commit. The database sees that Tx 150 committed a write that invalidated Tx 151's read of Alice's status. The database aborts Tx 151, forcing Bob's client to retry.
   - Result: Only Alice goes on leave. The invariant remains intact.

## Pros
- Prevents database corruption: Grouping writes ensures that partial updates from crashes never leave the database in an inconsistent state.
- Simplifies application logic: Offloading error recovery to the database engine means developers do not need to write manual rollback code.
- Manages concurrency safely: Strong isolation levels eliminate race conditions and keep concurrent operations predictable.
- Guarantees durability: Committing a transaction ensures that data survives physical hardware failures and power cuts.

## Cons
- Reduces system throughput: Strict concurrency control creates lock contention and queueing, slowing down operations.
- Triggers transaction aborts: Optimistic isolation levels can cause frequent aborts under high write contention, forcing expensive client-side retries.
- Escalates scaling difficulty: Distributing transactions across multiple partitions or nodes requires complex coordination protocols that increase latency.
- Increases resource usage: Maintaining MVCC history or tracking lock tables consumes significant memory and processing power in the database.

## Alternatives
- **BASE (Basically Available, Soft State, Eventual Consistency)**: This model scales horizontally across massive clusters by giving up immediate consistency, making it ideal for globally distributed social networks.
- **Sagas (Compensation-Based Workflows)**: Used in microservices, this pattern runs a sequence of independent local transactions and triggers compensating transactions to reverse previous steps on failure.
- **Single-Machine Scale-Up**: Rather than dealing with distributed transaction overhead, you run a single powerful machine with a traditional relational database, which avoids network partitioning and clock issues completely.

## When to use it
Use transactions in environments where data accuracy is non-negotiable. Perfect examples include bank transfers, stock trading platforms, inventory management systems, and medical booking portals. You should also choose them when multiple writes across different tables must succeed or fail as a single unit to preserve domain invariants.

## When NOT to use it
Avoid transactions in high-throughput, low-value data pipelines where occasional data loss or duplication is acceptable. Examples include real-time log streaming, IoT telemetry collection, and user clickstream analytics. For these workloads, use distributed message queues like Kafka or highly available key-value stores like Cassandra instead.

## Key takeaways / mental model
Think of a transaction as an all-or-nothing shipping container. You pack multiple packages inside it. If even one package fails customs inspections, the entire container is returned to the origin port, leaving the destination untouched. Isolation is like giving each cargo ship its own exclusive shipping channel, ensuring that concurrent ships cannot collide or affect each other's path.

## Self-check questions
1. What is the precise difference between database atomicity and concurrency isolation?
2. Explain how MVCC visibility rules determine if a specific row version should be seen by a transaction.
3. Why does Snapshot Isolation fail to prevent write skew, and how does SSI solve this limitation?
4. You are building a seat booking system. Two users click "Book" on the last seat. Explain how you would prevent double-booking using explicit locking versus compare-and-set.
5. In a distributed key-value store, why might compare-and-set fail to prevent lost updates without a leader or consensus?
6. When are transaction retries dangerous, and what steps should an application take to mitigate those dangers?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 7
- [01-reliability-scalability-maintainability.md](01-reliability-scalability-maintainability.md)
