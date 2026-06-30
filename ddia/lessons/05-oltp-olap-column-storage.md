---
id: ddia/05
subject: ddia
title: "OLTP vs OLAP and Column-Oriented Storage"
slug: oltp-olap-column-storage
status: drafted
mastery:
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 3"
prerequisites: [ddia/04]
created: 2026-06-30
updated: 2026-06-30
---

# OLTP vs OLAP and Column-Oriented Storage

## TL;DR
Databases handle two primary workloads: OLTP for low-latency user transactions, and OLAP for aggregate business analysis. While OLTP systems store complete rows together on disk, OLAP warehouses store columns separately. Storing columns separately permits aggressive compression and speeds up scan queries over billions of records.

## The idea
In the early days of databases, a single system handled both operational business transactions and analytical reporting. As data grew, analytical queries scanning millions of rows began to saturate disk IO, slowing down critical user-facing transactions. This conflict led to the division between Online Transaction Processing (OLTP) and Online Analytical Processing (OLAP). OLTP represents daily operational data, usually storing whole rows together on disk so point reads are fast. OLAP serves the business analyst who wants to look at trends over time, such as calculating total revenue from last month. For OLAP, loading entire rows from disk is wasteful when a query only needs to aggregate two out of a hundred columns. Storing each column separately on disk solves this problem, making aggregations incredibly efficient.

Before learning about column-oriented storage, review the disk-level engine designs described in [Storage Engines: LSM-Trees and B-Trees](../lessons/04-storage-engines.md).

## How it works
This section covers workload patterns, warehouse schemas, and column storage mechanics.

### OLTP vs OLAP Workloads
The two workloads serve completely different audiences and display distinct technical footprints:

* **OLTP (Online Transaction Processing)**:
  * **Audience**: End users of the application.
  * **Queries**: Many small, point lookups and writes using keys (such as fetching a user profile or creating a comment).
  * **Data Layout**: Row-oriented. Complete rows are stored together on disk.
  * **Characteristics**: High concurrency (thousands of queries per second) and low latency (milliseconds).

* **OLAP (Online Analytical Processing)**:
  * **Audience**: Business analysts and data scientists.
  * **Queries**: Large scans that read millions or billions of rows to aggregate a few specific columns.
  * **Data Layout**: Column-oriented. Each column is stored in its own separate file on disk.
  * **Characteristics**: Low concurrency (dozens of complex queries) and longer latency (seconds to minutes).

### Data Warehousing and ETL
To keep heavy analytical queries from slowing down the main application, companies build a dedicated **data warehouse**. A data warehouse is a read-only database optimized for OLAP.

The warehouse receives data from the main transactional systems using a pipeline called **ETL (Extract, Transform, Load)**:
1. **Extract**: Read data from multiple operational OLTP databases.
2. **Transform**: Clean up, de-duplicate, format, and structure the data into an analytical schema.
3. **Load**: Write the transformed data into the data warehouse.

### Schemas in Data Warehousing
Data warehouses usually organize tables in one of two major patterns:

* **Star Schema**: A single central **fact table** contains individual transaction events (such as sales). Each row contains numeric metrics (price, quantity) and foreign keys pointing to surrounding **dimension tables** (product, customer, date). When mapped, this creates a star shape.
* **Snowflake Schema**: Similar to the star schema, but the dimension tables are further normalized into sub-dimension tables (such as product category pointing to a separate manufacturer table). This normalization reduces redundancy but requires more table joins.

### Column-Oriented Storage Mechanics
In a row-oriented database, a table with columns `id`, `name`, and `age` stores rows sequentially: `[1, "Alice", 25], [2, "Bob", 30]`.

In a column-oriented database, the same table stores columns in separate files on disk:
* File 1: `[1, 2]` (all IDs)
* File 2: `["Alice", "Bob"]` (all names)
* File 3: `[25, 30]` (all ages)

This separation saves massive amounts of disk IO. If a query only needs to calculate the average age, the engine only reads File 3 from disk.

Because columns store the same data type repeatedly, they compress beautifully. A common compression technique is **bitmap encoding**. If a column has low cardinality (few unique values), the database creates a binary bitmap (zeros and ones) for each unique value. For example, if a `gender` column has values `[M, F, M, M, F]`, the engine stores:
* Bitmap for M: `1, 0, 1, 1, 0`
* Bitmap for F: `0, 1, 0, 0, 1`

These bitmaps are extremely compact and allow the database to resolve filter queries using fast, CPU-level bitwise operations.

To speed up queries even more, warehouses use **materialized views** and **data cubes**. A materialized view is a precomputed query result stored on disk. A data cube is a specific multidimensional materialized view that pre-aggregates values along dimensions like product, location, and time.

### Concrete Query Execution Example
Suppose an analyst runs:
`SELECT SUM(price), SUM(tax) FROM sales WHERE purchase_date >= '2026-06-01'`

In a row-oriented database:
The engine loads every single row of the `sales` table from disk, parses the entire row to find `purchase_date`, reads `price` and `tax`, and discards the other unused columns. This causes huge disk bottlenecks.

In a column-oriented database:
The engine only opens three files on disk: `purchase_date.col`, `price.col`, and `tax.col`. It skips all other columns entirely. It uses the compressed `purchase_date.col` file to find row indexes matching the date, reads the corresponding indexes in `price.col` and `tax.col`, and sums them up. The query transfers a fraction of the data compared to the row-oriented approach.

## Pros
- Column storage reduces disk IO dramatically for analytical queries because it only loads requested columns.
- Column files compress extremely well using bitmap encoding and run-length encoding.
- Separate warehouse systems isolate heavy reporting workloads from user-facing transactions.
- Materialized views and data cubes provide sub-millisecond response times for common aggregate queries.

## Cons
- Column storage slows down write workloads because inserting or updating a row requires writing to many separate column files on disk.
- Row-oriented lookups of a single complete record become slow and complex in column-oriented systems.
- Maintaining ETL pipelines introduces operational complexity, latency, and data drift risk.
- Materialized views consume extra storage and require background updates when underlying data changes.

## Alternatives
- **Row-oriented databases with indexes**: Standard OLTP databases using B-trees can run reporting queries by using secondary indexes, which works well for small datasets.
- **In-memory column stores**: Engines like DuckDB can store column data directly in memory, making local analytical queries fast without disk bottlenecks.

## When to use it
Choose OLTP databases when your system requires high-concurrency, low-latency writes, and handles single-row lookups for user interactions. Choose OLAP databases with column-oriented storage when you need to run aggregate queries, scans, and analytical reports over millions or billions of records.

## When NOT to use it
Do not use OLAP column-oriented storage as your primary application database where users update their profiles or create individual comments. Reach for a row-oriented OLTP database like PostgreSQL instead. Do not use an OLTP database to scan and analyze entire historical logs of user actions over the last five years. Reach for a dedicated column-oriented data warehouse like Snowflake or BigQuery in those cases.

## Key takeaways / mental model
Think of a row-oriented database as a book where each page represents a single record. If you want to find the average age of all users, you must turn every page in the book and read the whole sheet just to extract the age. Think of a column-oriented database as a set of index card boxes, where one box contains all the ages, another contains all the first names, and another contains all the registration dates. To find the average age, you only need to grab the age box, saving you from reading any names or registration dates.

## Self-check questions
1. Why does a column-oriented storage engine struggle with frequent INSERT statements compared to a row-oriented engine?
2. What is the main structural difference between a star schema and a snowflake schema, and how does normalization play a role?
3. How does bitmap encoding help compress data, and how can a database run-filter queries directly on compressed bitmaps?
4. What are the operational challenges of maintaining an ETL pipeline between OLTP and OLAP systems?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 3: Storage and Retrieval.
- Prerequisites: [04-storage-engines.md](../lessons/04-storage-engines.md)
