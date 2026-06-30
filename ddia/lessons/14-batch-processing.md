---
id: ddia/14
subject: ddia
title: "Batch Processing"
slug: batch-processing
status: drafted
mastery:
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 10"
prerequisites: [ddia/06]
created: 2026-06-30
updated: 2026-06-30
---

# Batch Processing

## TL;DR
Batch processing handles large, bounded datasets by running offline jobs to produce derived output without strict execution time constraints. It borrows heavily from Unix philosophy concepts like small composable tools and uniform interfaces. MapReduce and newer dataflow engines use sorting, joins, and immutable datasets to build reproducible and highly resilient data pipelines.

## The idea
How do we process massive amounts of data when we don't need immediate, low latency responses? Online systems focus on serving user requests with sub-second response times, which requires keeping active connections open and managing concurrent modifications. In contrast, batch processing systems run offline. They take a fixed, predefined input dataset, run a sequence of operations over it, and produce a new output dataset.

This model exists to solve the problem of processing and analyzing vast quantities of historical records. Because the input dataset is bounded, the job has a clear start and end. There's no pressure to finish in milliseconds, so the system can optimize for throughput instead of latency. The conceptual foundation relies on immutability. Since input files are never modified, we can safely re-run failed jobs, experiment with different code, and recover from errors without corrupting the raw data.

Understanding how data is encoded and evolved is a critical dependency here. Our previous work in [06-encoding-and-schema-evolution.md](./06-encoding-and-schema-evolution.md) showed how formats like Avro or Parquet handle changes over time. Batch processing systems must read these exact schemas to deserialize the records they process.

## How it works
Batch systems function through structured stages of computation, heavily inspired by Unix pipes. Let's look at the mechanisms that power these processes.

### 1. Three Types of Systems
To place batch processing in context, we can divide all software systems into three distinct categories:

- **Online Systems (Services)**: These serve immediate user requests. A client sends a request and waits for a response, which should arrive in milliseconds or seconds. The metric we care about is response time (latency), and availability is critical. Online databases use indexes to serve queries with low latency.
- **Offline Systems (Batch Processing)**: These run scheduled jobs to process large, bounded datasets. A job takes a known input and produces an output, running for minutes, hours, or days. The main metric is throughput (the rate at which data is processed), and we don't care about real-time response times.
- **Near-Real-Time Systems (Stream Processing)**: These sit between online and offline models. They operate on unbounded input streams where data is processed continuously as events arrive. Stream processing reduces latency to seconds or milliseconds compared to batch, but introduces complex coordination challenges.

### 2. Unix Ancestry and Philosophy
In a single machine environment, Unix tools represent the ultimate composable batch system. Small programs like grep, awk, and sort do one thing well. They connect via pipes, which stream bytes from one process to the next without writing the entire dataset to disk first.

Let's look at a concrete worked example. We want to find the top 5 most frequently requested URL paths from a web server access log.

#### Worked Example 1: Unix Log-Analysis Pipeline
Suppose we have a log file at `/var/log/nginx/access.log`. Here's a pipeline that processes the log:

```bash
cat /var/log/nginx/access.log | awk '{print $7}' | sort | uniq -c | sort -r -n | head -n 5
```

Let's trace how this pipeline processes the input step-by-step:
1. `cat access.log`: Reads the file and writes the raw text to standard output.
2. `awk '{print $7}'`: Extracts the 7th whitespace-separated field from each line, which represents the URL path (e.g. `/home` or `/about`).
3. `sort`: Sorts the extracted URL paths alphabetically. This is necessary because the next step, `uniq`, only groups adjacent identical lines.
4. `uniq -c`: Filters out duplicates and prefixes each unique line with its occurrence count (e.g. `12 /home`).
5. `sort -r -n`: Sorts the output numerically (`-n`) and in reverse order (`-r`) to place the most frequent URLs at the top.
6. `head -n 5`: Outputs only the first 5 lines, discarding the rest of the stream.

This pipeline embodies the **Unix Philosophy**:
- Write programs that do one thing well.
- Write programs to work together.
- Write programs to handle text streams, because that is a universal interface.

The uniform interface of standard input (stdin) and standard output (stdout) allows us to plug any tool into another. By agreeing on text (specifically newline-separated records) as the common currency, different languages and tools can be mixed and matched freely without any translation layers.

Furthermore, the pipeline relies on **Input Immutability**: the raw log file is never modified. If we want to change our analysis (e.g., to find the top 10 URLs instead of 5), we can simply rewrite the command and run it again. This gives us high human fault tolerance.

### 3. MapReduce and Distributed Filesystems (HDFS)
MapReduce scales this single-machine pattern to a cluster of machines. Instead of a single disk, it runs on a distributed filesystem like HDFS (Hadoop Distributed File System). HDFS operates on a **shared-nothing architecture**, meaning the cluster consists of commodity hardware connected by an ethernet network. Nodes don't share memory or disk space.

HDFS splits files into large blocks (e.g., 128MB) and replicates them across multiple machines to handle node failures.

A MapReduce job runs in three main phases:
1. **Map Phase**: Multiple mapper tasks run in parallel across the cluster. The framework tries to schedule mapper tasks on the physical machines where the input data blocks are stored (data locality). Each mapper reads its block and outputs key-value pairs.
2. **Shuffle and Sort Phase**: The framework takes all key-value pairs produced by all mappers, sorts them by key, and partitions them. It guarantees that all values for a given key end up on the same reducer machine, shuffling the data across the network.
3. **Reduce Phase**: The reducer function runs on each unique key and its list of associated values. It aggregates or transforms the data, then writes the final output back to HDFS.

Let's look at how this works with a concrete example.

#### Worked Example 2: Distributed URL-Access Count
We have a massive web server log stored in HDFS. We want to find the request count for each URL path across the entire cluster.

```
+---------------+      +---------+      +----------------+      +------------+      +---------------+
| Input Blocks  | ---> | Mappers | ---> | Shuffle & Sort | ---> |  Reducers  | ---> | Output Files  |
| (Raw logs)    |      | (Map)   |      | (Group by Key) |      |  (Reduce)  |      | (HDFS files)  |
+---------------+      +---------+      +----------------+      +------------+      +---------------+
```

1. **Input**: A dataset of log lines on HDFS, split across three blocks.
2. **Map Phase**:
   - Mapper 1 processes lines from Block 1:
     - Input: `192.168.1.1 - [30/Jun/2026:10:00:00] "GET /home HTTP/1.1"`
     - Output: `("/home", 1)`
     - Input: `192.168.1.2 - [30/Jun/2026:10:01:00] "GET /about HTTP/1.1"`
     - Output: `("/about", 1)`
   - Mapper 2 processes lines from Block 2:
     - Input: `192.168.1.1 - [30/Jun/2026:10:02:00] "GET /home HTTP/1.1"`
     - Output: `("/home", 1)`
3. **Shuffle and Sort Phase**:
   - The framework gathers all outputs, sorts them, and routes them to reducers based on the hash of the key.
   - Reducer 1 gets key `/about` with list of values `[1]`.
   - Reducer 2 gets key `/home` with list of values `[1, 1]`.
4. **Reduce Phase**:
   - Reducer 1 sums the list: `("/about", 1)`
   - Reducer 2 sums the list: `("/home", 2)`
5. **Output**: The output is written as part files back to HDFS (e.g., `part-r-00001` and `part-r-00002`).

**Speculative Execution**: In a large cluster, some nodes might be slow due to failing hardware, network congestion, or competing background tasks. To prevent these slow machines (stragglers) from dragging down the entire job, MapReduce uses speculative execution. If a task runs slower than expected, the coordinator schedules a duplicate copy of the task on another machine. Whichever copy finishes first is kept, and the other is killed.

**Chaining Jobs into Workflows**: A single MapReduce job can only perform a single step of data transformation. To build complex pipelines, we must chain jobs into workflows, where the output of one job becomes the input of the next. Workflow schedulers like Apache Oozie or Apache Airflow are used to manage these dependencies.

### 4. Joins in Batch Processing
When we need to combine two datasets (like a user table and an activity log), batch systems use different join strategies depending on the size and partitioning of the data.

#### Reduce-Side Joins (Sort-Merge Joins)
In a reduce-side join, the system reads both datasets, extracts a join key, and uses the shuffle phase to group records with the same join key together.

#### Worked Example 3: Sort-Merge Join (Reduce-Side Join)
Suppose we have two datasets:
- **Users (Dataset 1)**:
  - `{"id": 1, "name": "Alice"}`
  - `{"id": 2, "name": "Bob"}`
- **PageViews (Dataset 2)**:
  - `{"user_id": 1, "url": "/home"}`
  - `{"user_id": 2, "url": "/about"}`
  - `{"user_id": 1, "url": "/contact"}`

Let's trace how a Sort-Merge Join executes:
1. **Map Phase**:
   - Mapper A reads User block, outputs: `(1, ("profile", "Alice"))`, `(2, ("profile", "Bob"))`.
   - Mapper B reads PageViews block, outputs: `(1, ("view", "/home"))`, `(2, ("view", "/about"))`, `(1, ("view", "/contact"))`.
2. **Shuffle & Sort Phase**:
   - Group by key (`userId`) and sort:
     - Key `1` gets values: `[("profile", "Alice"), ("view", "/home"), ("view", "/contact")]`.
     - Key `2` gets values: `[("profile", "Bob"), ("view", "/about")]`.
3. **Reduce Phase**:
   - Reducer 1 processes Key 1. It scans the values, identifies the profile data `"Alice"`, and merges it with each view: `("Alice", "/home")`, `("Alice", "/contact")`.
   - Reducer 2 processes Key 2. It identifies the profile data `"Bob"`, and merges it: `("Bob", "/about")`.

**The Hot-Key / Skew Problem**: If a few keys have an exceptionally large number of records (for example, a celebrity's user profile on a social network), all those records will be sent to a single reducer. This reducer will take much longer to finish than others, dragging down the performance of the entire job.
- **Solution**: We can use a **skewed join (sharded join)**. We run a sampling job first to identify keys that exceed a threshold of occurrences (hot keys). The system then appends a random number to the key to shard it across multiple reducers. The other join table is replicated to all those shard reducers, balancing the load.

#### Map-Side Joins
Map-side joins avoid the expensive shuffle and sort phases completely by performing the join entirely in the mapper. However, they make strong assumptions about the size and partitioning of the input data.

- **Broadcast Hash Join**: If one of the two datasets is small enough to fit entirely in memory, we can copy it to every mapper. Each mapper loads the small dataset into a hash table, reads the large dataset block-by-block, and performs the join locally. The main limitation is that the small dataset must fit within the memory of each map task; otherwise, it will throw an OutOfMemoryError.
- **Partitioned Hash Join (Bucket Map Join)**: If both datasets are partitioned by the join key in the same way (meaning they have the same number of partitions and use the same hash function), we can schedule mapper tasks so that each mapper only loads the corresponding partition of the smaller dataset, performing the join locally.
- **Map-Side Merge Join**: If both datasets are partitioned and sorted by the join key, each mapper can read both sorted partitions concurrently and merge them line-by-line, without loading entire partitions into memory.

#### Comparing Join Strategies
Let's summarize how these common join strategies compare:

| Join Strategy | Join Phase | Memory Requirement | Input Data Requirements |
|---|---|---|---|
| **Sort-Merge Join** | Reduce-side | Low (spills to disk) | None |
| **Broadcast Hash Join** | Map-side | High (one dataset must fit in memory) | One dataset must be small |
| **Partitioned Hash Join** | Map-side | Medium (one bucket must fit in memory) | Both datasets partitioned by join key in the same way |
| **Map-Side Merge Join** | Map-side | Very Low | Both datasets partitioned and sorted by join key |

### 5. Output of Batch Jobs
What do we do with the output of a batch job? It's not usually queried directly by web servers because HDFS is optimized for sequential scans, not low-latency random access. Instead, we use batch jobs to build:

- **Search Indexes**: We can use MapReduce to parse documents and build an inverted index (e.g., mapping terms to document IDs). The output is written as static index files, which are shipped to search nodes (like Solr or Elasticsearch) to serve low-latency search queries.
- **Key-Value Stores**: We can build static database files (like RocksDB SSTables or Voldemort files) in batch and copy them to storage servers to serve read-only queries with high performance.

This relies on **immutable output**, which enables **human fault tolerance**: if we deploy a bug that corrupts the database, we don't try to patch the live database. We simply fix the bug in our code, roll back the output directory, and rerun the batch job over the original immutable inputs to produce correct data.

### 6. Beyond MapReduce: Dataflow Engines (Spark, Tez, Flink)
While MapReduce was a major breakthrough, it has a massive efficiency problem: it writes all intermediate state to HDFS between jobs. If you have a chain of five MapReduce jobs, the output of job 1 must be fully written to disk and replicated across three nodes before job 2 can start reading it. This materialization adds immense disk I/O and network replication overhead.

Newer dataflow engines solve this by modeling the entire pipeline as a Directed Acyclic Graph (DAG) of operators:

```
                  +---------------+
                  |  Raw Input    |
                  +---------------+
                          |
                 [Map / Filter]
                          |
                  +---------------+
                  | Intermediate  |  (Held in memory or sent via network sockets)
                  +---------------+
                          |
                 [Join / Aggregate]
                          |
                  +---------------+
                  | Final Output  |  (Written to HDFS)
                  +---------------+
```

Instead of strict map and reduce phases, dataflow engines offer flexible operators (like filter, join, and flatMap). They pass data directly through memory or network sockets from one stage to the next, only writing to disk when necessary (like during a shuffle).

**Lazy Evaluation vs Actions**: Dataflow engines use lazy evaluation. Transformations (like map, filter, join) do not calculate their results immediately. They simply record the DAG of operations. The computation is only executed when an action (like `count`, `collect`, or `saveAsTextFile`) is explicitly called. This allows the engine to optimize the entire execution plan globally.

**Fault Tolerance via Lineage**: Since dataflow engines don't write intermediate state to disk, how do they handle node failures? Replicating data is expensive, so they use **lineage**. They track the exact sequence of transformations (the DAG) used to build each partition of data (using Resilient Distributed Datasets, or RDDs).

Let's visualize a simple lineage graph:
```
[HDFS File] ---> RDD 1 (lines) ---> RDD 2 (URLs) ---> RDD 3 (counts)
                  (map)               (filter)             (reduceByKey)
```

In Spark, an RDD is a read-only, partitioned collection of records. If partition 2 of RDD 2 is lost due to a node crash, Spark doesn't need to recompute the entire dataset. It looks at the RDD's lineage graph and sees that partition 2 of RDD 2 was derived from partition 2 of RDD 1 via a simple filter transformation. It schedules a task to re-run that specific filter transformation on the corresponding input partition, which is extremely fast and efficient.

**Graph Processing**: Systems like Google's Pregel or Apache Giraph use a bulk synchronous parallel (BSP) model to process graph datasets. Nodes represent vertices, and they send messages to their neighbors. Each superstep executes a user-defined function on all vertices in parallel, which is much more efficient than traditional MapReduce for traversing networks, such as calculating PageRank. In each superstep, a vertex executes a user-defined function that reads messages sent to it from the previous superstep, updates its state, and sends messages to its neighbors. Vertices can vote to halt when they have no more work, terminating the execution.

## Pros
- **High Throughput**: Batch systems optimize for scanning massive datasets efficiently, making full use of parallel disk reads and network bandwidth.
- **Fault Tolerance**: Because inputs are immutable, the engine can simply re-run any failed task on a different machine without risking inconsistent state.
- **Idempotence and Safety**: Running the same job twice on the same input produces the exact same output. This makes debugging, testing, and schema migrations safe and predictable.
- **Human Fault Tolerance**: If a bug is introduced, you can roll back the code and re-run the job over the original immutable input to overwrite the corrupt data.

## Cons
- **High Latency**: Batch jobs take minutes, hours, or even days to complete. They cannot be used for real-time user-facing features.
- **High Resource Overhead**: The sorting and shuffling phases consume enormous amounts of memory, CPU, and disk input/output, which can overwhelm shared clusters.
- **Stale Data**: Outputs reflect the state of the world when the batch run started. Any data arrived after that moment must wait for the next run.
- **Materialization Overhead**: Traditional MapReduce jobs must write all intermediate state to disk, which adds immense performance costs compared to in-memory processing.

## Alternatives
- **Online Transaction Processing (OLTP)**: Databases designed for low latency queries and frequent, small updates. They are best for interactive applications but fail when performing scans over millions of records.
- **Stream Processing**: Continuous processing of unbounded event streams as they arrive. This reduces latency to seconds or milliseconds but introduces complex coordination challenges around windowing and out-of-order events.
- **Massively Parallel Processing (MPP) Databases**: Analytical databases like Snowflake or Redshift that use SQL queries to analyze data. They are highly optimized for interactive exploration, while batch engines are better for custom, multi-stage data transformations.

## When to use it
Batch processing is the right tool when you have a large, bounded historical dataset and need to perform heavy computations. Common use cases include:
- Generating periodic reports, like daily financial summaries or monthly active user reports.
- Building search indexes or training machine learning models from scratch.
- Performing complex ETL (Extract, Transform, Load) tasks to clean and prepare raw logs for data warehouses.
- Running offline simulations or migrations where correctness is far more important than speed.

## When NOT to use it
Don't use batch processing when:
- You need a response in less than a few minutes. If a user is waiting for an update, use an OLTP database.
- You need to respond to events as they happen, like fraud detection or real-time alerting. Use a stream processing engine like Flink or Spark Streaming instead.
- Your dataset is constantly growing and you want to see updates continuously. Streaming is a much better fit for this requirement.

## Key takeaways / mental model
Think of batch processing as a factory assembly line for data. The input materials are stacked in a warehouse (HDFS), and they never change during production. Workers (mappers and reducers) perform specific, isolated tasks, passing items down the line in batches. If a worker drops a box, you don't try to repair the broken items: you just throw them away, fetch a fresh batch of raw materials from the warehouse, and start that step again. The process is completely predictable, reproducible, and highly resilient.

## Self-check questions
1. Why does MapReduce rely so heavily on sorting, and which phase is responsible for doing this work?
2. What is the fundamental difference between a reduce-side join and a map-side join, and when should you choose one over the other?
3. How do dataflow engines like Apache Spark achieve better performance than traditional MapReduce jobs?
4. How does the concept of idempotence simplify error recovery in batch pipelines?
5. What is the difference between a broadcast hash join and a partitioned hash join, and what is the main size limitation of each?
6. How do dataflow engines handle node failures without writing intermediate datasets to disk?
7. What is speculative execution, and how does it prevent slow machines from dragging down batch jobs?
8. Why is input immutability so valuable for human fault tolerance, and how does it compare to fixing errors in an OLTP database?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 10
- For how batch processing interacts with serialization schemas, see [06-encoding-and-schema-evolution.md](./06-encoding-and-schema-evolution.md).
