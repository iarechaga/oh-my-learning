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

### The Unix Ancestry
In a single machine environment, Unix tools represent the ultimate composable batch system. Small programs like grep, awk, and sort do one thing well. They connect via pipes, which stream bytes from one process to the next without writing the entire dataset to disk first.

Unix tools are composable because they share a uniform interface: standard input (stdin) and standard output (stdout), structured as newline-separated text. The shell manages the connections, handles input and output redirection, and schedules execution.

### MapReduce and HDFS
MapReduce scales this pattern to a cluster of machines. Instead of a single disk, it runs on a distributed filesystem like HDFS (Hadoop Distributed File System). HDFS splits files into large blocks and replicates them across multiple nodes to ensure durability and local data access.

A MapReduce job runs in three main phases:
1. **Map**: The system runs a mapper function on each input record, reading data from HDFS. The mapper extracts key-value pairs from each record.
2. **Shuffle and Sort**: This is the core magic of MapReduce. The framework takes all key-value pairs produced by all mappers, sorts them by key, and partitions them so that all values for a given key end up on the same reducer machine.
3. **Reduce**: The reducer function runs on each unique key and its list of associated values. It aggregates or transforms the data, then writes the final output back to HDFS.

### Concrete Example: Log Analysis
Imagine we have a web server access log stored in HDFS. Each line represents a request. We want to find the number of requests per URL path.

1. **Input**: A dataset of log lines on HDFS.
   ```
   192.168.1.1 - - [30/Jun/2026:10:00:00] "GET /home HTTP/1.1" 200
   192.168.1.2 - - [30/Jun/2026:10:01:00] "GET /about HTTP/1.1" 200
   192.168.1.1 - - [30/Jun/2026:10:02:00] "GET /home HTTP/1.1" 200
   ```
2. **Map Phase**: Multiple mapper tasks run in parallel across the cluster. Each mapper parses its chunk of log lines and outputs URL-count pairs:
   - Mapper 1 outputs: `("/home", 1)`, `("/about", 1)`
   - Mapper 2 outputs: `("/home", 1)`
3. **Shuffle and Sort**: The framework groups these pairs by key.
   - Key `/about` gets values `[1]`
   - Key `/home` gets values `[1, 1]`
4. **Reduce Phase**: Reducer tasks sum the values for each key.
   - Reducer 1 receives `/about` and outputs `("/about", 1)`
   - Reducer 2 receives `/home` and outputs `("/home", 2)`
5. **Output**: The output is written to a set of text files in HDFS.

### Joins in Batch Processing
When we need to combine two datasets, batch systems use different join strategies depending on the size and partitioning of the data:

* **Reduce-Side Joins (Sort-Merge Joins)**:
  The system reads both datasets, extracts a join key, and uses the shuffle phase to group records with the same join key together. The reducer then receives the records from both sides for a given key and merges them. This works for datasets of any size, but sorting and copying data over the network is expensive.

* **Map-Side Joins**:
  These joins avoid the shuffle and sort phases completely by doing the work in the mapper.
  - *Broadcast Joins*: If one dataset is small enough to fit entirely in memory, the system sends a copy of it to every mapper. Each mapper loads the small dataset into a hash table, reads the large dataset, and performs the join locally.
  - *Partitioned Joins (Bucket Map Joins)*: If both datasets are partitioned by the join key in the same way, each mapper only needs to load the corresponding partition of the other dataset, joining them locally.

### Dataflow Engines (Spark, Tez, Flink)
While MapReduce was a breakthrough, it has a major efficiency problem: it writes all intermediate state to HDFS between jobs. If you have a chain of five MapReduce jobs, the output of job one must be fully written to disk and replicated before job two can start reading it.

Newer dataflow engines solve this by modeling the entire pipeline as a Directed Acyclic Graph (DAG). Instead of strict map and reduce phases, they offer flexible operators. They pass data directly through memory or network sockets from one stage to the next, only writing to disk when necessary (like during a shuffle). This makes them much faster and easier to program.

## Pros
- **High Throughput**: Batch systems optimize for scanning massive datasets efficiently, making full use of parallel disk reads and network bandwidth.
- **Fault Tolerance**: Because inputs are immutable, the engine can simply re-run any failed task on a different machine without risking inconsistent state.
- **Idempotence and Safety**: Running the same job twice on the same input produces the exact same output. This makes debugging, testing, and schema migrations safe and predictable.
- **Data Locality**: Scheduling tasks on the physical machines where the data block is stored minimizes network traffic during the read phase.

## Cons
- **High Latency**: Batch jobs take minutes, hours, or even days to complete. They cannot be used for real-time user-facing features.
- **High Resource Overhead**: The sorting and shuffling phases consume enormous amounts of memory, CPU, and disk input/output, which can overwhelm shared clusters.
- **Stale Data**: Outputs reflect the state of the world when the batch run started. Any data arrived after that moment must wait for the next run.

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

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 10
