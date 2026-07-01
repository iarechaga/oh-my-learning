---
id: ddia/05
subject: ddia
title: "OLTP vs OLAP and Column-Oriented Storage"
slug: oltp-olap-column-storage
status: drafted
mastery:
seniority: mid
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 3"
prerequisites: [ddia/04]
created: 2026-06-30
updated: 2026-06-30
---

# OLTP vs OLAP and Column-Oriented Storage

## TL;DR
Databases handle two primary workloads: OLTP for low-latency user transactions, and OLAP for aggregate business analysis. While OLTP systems store complete rows together on disk, OLAP warehouses store columns separately. Storing columns separately permits aggressive compression and speeds up scan queries over billions of records.

## The idea
In the early days of databases, a single system handled both operational business transactions and analytical reporting. As data grew, analytical queries scanning millions of rows began to saturate disk IO, slowing down critical user-facing transactions. This conflict led to the division between Online Transaction Processing (OLTP) and Online Analytical Processing (OLAP). 

OLTP represents daily operational data, usually storing whole rows together on disk so point reads are fast. OLAP serves the business analyst who wants to look at trends over time, such as calculating total revenue from last month. For OLAP, loading entire rows from disk is wasteful when a query only needs to aggregate two out of a hundred columns. Storing each column separately on disk solves this problem, making aggregations incredibly efficient.

Before learning about column-oriented storage, review the disk-level engine designs described in [Storage Engines: LSM-Trees and B-Trees](../lessons/04-storage-engines.md).

## How it works
This section covers workload profiles, warehouse schemas, physical layout differences, compression mechanics, sorting, vectorized execution, and write paths.

### Workload Profiles: OLTP vs OLAP
The two workloads serve completely different audiences and display distinct technical footprints. The following table highlights their fundamental differences:

| Metric | OLTP (Online Transaction Processing) | OLAP (Online Analytical Processing) |
| :--- | :--- | :--- |
| **Primary User** | End-user applications, customer-facing systems | Business analysts, data scientists, executives |
| **Read Pattern** | Small number of records per query, fetched by ID | Large scans over millions or billions of rows |
| **Write Pattern** | High frequency of small inserts, updates, and deletes | Bulk loads (ETL) or event streams, append-heavy |
| **Data Scale** | Gigabytes to Terabytes of active, current operational state | Terabytes to Petabytes of historical log data |
| **Main Bottleneck** | Disk seek times, lock contention, concurrency limits | Disk throughput, network transfer, CPU execution |

In OLTP workloads, transactions require high concurrency and low latency. The engine must read or write a handful of records, usually identified by a unique key. Disk seek times and lock contention are the main bottlenecks because multiple clients attempt to modify the same data concurrently.

In OLAP workloads, queries require reading massive amounts of historical logs to compile summaries. Concurrency is lower, but individual queries are highly complex and can run for seconds or minutes. Disk sequential throughput and CPU data processing speeds are the primary bottlenecks.

### The Architecture of Data Warehousing and ETL
To keep heavy analytical queries from slowing down the main application, companies build a dedicated data warehouse. This data warehouse is an analytical database optimized for read-heavy OLAP queries. Sparing production OLTP databases from heavy analytical scans ensures that customer checkout flows or profile updates remain highly responsive.

The warehouse receives data from the main transactional systems using a pipeline called ETL (Extract, Transform, Load).
1. **Extract**: The pipeline reads data from multiple operational OLTP databases, message brokers, and logs.
2. **Transform**: A transformation engine cleans up, de-duplicates, formats, and structures the data into an analytical schema.
3. **Load**: The pipeline writes the transformed data into the data warehouse.

This division decouples the production database from reporting tasks. Senders do not need to worry about locking production rows when executing huge aggregations.

### Dimensional Modeling: Star and Snowflake Schemas
Data warehouses organize tables in highly structured schemas that differ from the normalized tables of OLTP systems.

* **Star Schema**: A single central fact table contains individual transaction events, such as sales. Each row in the fact table contains numeric metrics (price, quantity) and foreign keys pointing to surrounding dimension tables. When mapped out, this structure creates a star shape.
* **Snowflake Schema**: Dimension tables are further normalized into sub-dimension tables. This normalization reduces redundancy but requires more table joins.

To see this in action, let's explore a concrete retail example. A central sales fact table might look like this:

`sales_fact`
* `sale_id` (Primary Key)
* `date_key` (Foreign Key to `dim_date`)
* `product_key` (Foreign Key to `dim_product`)
* `store_key` (Foreign Key to `dim_store`)
* `customer_key` (Foreign Key to `dim_customer`)
* `promotion_key` (Foreign Key to `dim_promotion`)
* `quantity` (Metric: number of items purchased)
* `unit_price` (Metric: price per item)
* `discount_amount` (Metric: discount applied)
* `tax_amount` (Metric: sales tax)
* `total_sales` (Metric: total price paid)

This fact table links to several dimension tables that hold the details of the event:

* `dim_date`: contains `date_key`, `calendar_date`, `day_of_week`, `month`, `quarter`, `year`, `is_holiday`.
* `dim_product`: contains `product_key`, `sku`, `product_name`, `category`, `brand`, `size`, `color`.
* `dim_store`: contains `store_key`, `store_number`, `store_name`, `city`, `state`, `country`, `manager_name`.
* `dim_customer`: contains `customer_key`, `customer_id`, `first_name`, `last_name`, `email`, `postal_code`, `signup_date`.
* `dim_promotion`: contains `promotion_key`, `promotion_name`, `promotion_type`, `discount_percentage`.

Analytical queries frequently join these tables to filter and aggregate data. Here is a SQL query searching for holiday sales:

```sql
SELECT d.year, p.category, SUM(f.total_sales) AS revenue
FROM sales_fact f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_product p ON f.product_key = p.product_key
WHERE d.is_holiday = true
GROUP BY d.year, p.category;
```

In a snowflake schema, the product dimension `dim_product` might normalize `category` into a separate `dim_category` table and `brand` into a separate `dim_brand` table. This normalization reduces storage duplication for text fields, but it forces analytical queries to run expensive multi-way joins.

### Physical Layout of Data: Row vs Column Stores
Row-oriented and column-oriented databases lay out their bytes differently on the storage media.

```
Row-Oriented Layout (Contiguous rows in one file):
+-----------------------------------------------------------------+
| Row 1: [1, Alice, 25] | Row 2: [2, Bob, 30] | Row 3: [3, Charlie, 22] |
+-----------------------------------------------------------------+

Column-Oriented Layout (Separate files/segments per column):
+-------------------------------------------------+
| File 1 (ID):     | 1 | 2 | 3 |                      |
+-------------------------------------------------+
| File 2 (Name):   | Alice | Bob | Charlie |          |
+-------------------------------------------------+
| File 3 (Age):    | 25 | 30 | 22 |                    |
+-------------------------------------------------+
```

In a row-oriented database like PostgreSQL, the engine stores all columns of a single row next to each other on disk. If you want to load a user's record, you can fetch it in a single disk read.

In a column-oriented database like Snowflake, the engine splits the table into columns. Each column is stored in its own separate file on disk. When a query only needs a few columns, the engine bypasses the files of the other columns, saving massive amounts of disk IO.

### Column Compression: Bitmaps and Run-Length Encoding
Since columns contain values of the exact same data type, they compress far better than row-oriented records. 

#### Bitmap Encoding
If a column has low cardinality (few unique values), the database creates a binary bitmap (zeros and ones) for each unique value. Imagine a column `membership` with values: `[Bronze, Silver, Bronze, Bronze, Silver]`. The engine produces two separate bitmaps:
* Bitmap for Bronze: `1, 0, 1, 1, 0`
* Bitmap for Silver: `0, 1, 0, 0, 1`

These bitmaps are compact. If a query filters for `membership = 'Silver'`, the engine only reads the Silver bitmap and skips scanning any values.

Furthermore, if we have a compound query like `WHERE membership = 'Silver' AND brand = 'Nike'`, the database loads the Silver membership bitmap and the Nike brand bitmap. It then performs a fast CPU bitwise `AND` on them. This produces the result bitmap without scanning any strings or reading unnecessary columns.

#### Run-Length Encoding (RLE)
We can compress these bitmaps further using run-length encoding. Suppose a bitmap is `0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0`. RLE represents this sequence by tracking the lengths of consecutive runs of 0s and 1s. This bitmap has 4 zeros, 5 ones, and then 2 zeros. The compressed RLE representation is just `(4, 5, 2)`. This turns millions of bits into a tiny array of integers.

### Sort Orders in Column Storage
Storing columns in a sorted order speeds up queries and improves compression. The database administrator can choose which columns to sort by, similar to choosing clustering keys.

If a query frequently filters by a specific column, sorting by that column makes it easy for the database to locate the matching rows. Because sorting groups identical values together, run-length encoding compresses the sorted columns even more.

A column-oriented database can sort by multiple columns, such as sorting first by `product_key` and then by `date_key`. This makes queries filtered by `product_key` incredibly fast. If there are multiple dates for the same product, those dates are also stored contiguously.

A columnar database can store data replicas with different sort orders. This lets different replicas optimize for different queries. For example, Replica A could sort by date, making temporal queries fast, while Replica B could sort by product, making inventory lookups highly efficient.

### Vectorized Processing
Modern column engines use vectorized processing to match CPU speeds. Traditional row engines interpret queries by evaluating an expression tree on one row at a time. This introduces substantial function-call overhead and wastes CPU instruction cache.

Column stores load contiguous blocks of column data (such as arrays of 1,000 values) into CPU cache. The engine runs tight loops over these arrays, letting the compiler optimize execution and utilize SIMD (Single Instruction Multiple Data) instructions. This lets the CPU process multiple values in a single clock cycle with zero function-call overhead. 

Using contiguous arrays matches CPU cache line prefetching perfectly, ensuring that data is already in L1/L2 cache before the CPU execution pipeline requests it.

### Writing to Columnar Storage: LSM-Trees on Columns
Writing data to a column store is a challenge. If you insert a single row, the database must write to every single column file on disk. Doing this for every single insert causes a massive random IO bottleneck.

To solve this, columnar databases employ LSM-tree architectures.
1. **In-Memory Write**: All inserts, updates, and deletes go first to an in-memory, row-oriented write buffer (memtable) and a write-ahead log (WAL) for durability.
2. **Columnar Flush**: When the memtable is full, the engine flushes it to disk. During the flush, the engine converts the row-oriented memory data into sorted, column-oriented disk segments. Each column is written to its own file within that segment.
3. **Compaction**: A background process merges these segments asynchronously. This merges multiple sorted columnar files and writes out consolidated, compressed files.

This architecture turns random disk writes into high-performance sequential flushes.

### Materialized Views and Data Cubes
To speed up common aggregate queries, data warehouses use precomputed results.

* **Materialized Views**: A materialized view is a query result that is calculated once and saved on disk. When the underlying data changes, the view is updated. These are highly beneficial when a specific aggregate is queried repeatedly by dashboard applications.
* **Data Cubes**: A data cube is a multidimensional materialized view. It pre-aggregates values along dimensions like product, location, and time. For example, a three-dimensional data cube stores pre-calculated sales totals for every combination of product, store, and date. While data cubes speed up summary queries, they consume substantial storage and lack the flexibility of raw column scans.

Data cubes are structured as grids where each axis represents a dimension. For a retail business, the three axes could be Product, Store, and Date. If you want to know the sales of shoes in New York on Christmas, you simply look up the cell at those coordinates. This makes reporting queries instantaneous. However, if an analyst suddenly wants to group sales by customer age, the data cube cannot answer this query because age was not one of the pre-aggregated axes. The database must fall back to a full scan of the raw columns.

### Three Concrete Worked Examples

#### Example 1: Analytical Query Cost (Row vs Column Store Disk IO)
Suppose we have a `sales` table with 10,000,000 rows. Each row contains 100 columns, with an average row size of 1,000 bytes. The total size of the table is 10,000,000 * 1,000 bytes = 10,000,000,000 bytes (10 GB).

An analyst runs this query:
`SELECT SUM(revenue) FROM sales;`

The `revenue` column is stored as an 8-byte integer.

* **Row-Oriented Engine**: The database must read the entire 10 GB table from disk into memory because rows are stored contiguously. The engine parses every row, extracts the 8-byte revenue field, and discards the remaining 992 bytes of unused columns.
* **Column-Oriented Engine**: The database only opens the `revenue.col` file. This file contains 10,000,000 * 8 bytes = 80,000,000 bytes (80 MB). Even without compression, the column store reads only 80 MB instead of 10 GB. This is a 125x reduction in disk IO.

#### Example 2: Bitmap and Run-Length Encoding Compression Math
Suppose a column has 1,000,000 rows. The column is `customer_membership_level` with three possible values: `Bronze`, `Silver`, and `Gold`.

Because there are only 3 distinct values, the engine creates 3 bitmaps, each 1,000,000 bits long. The uncompressed size of one bitmap is 1,000,000 bits / 8 = 125,000 bytes (125 KB). Storing all three uncompressed bitmaps takes 375 KB.

Suppose we sort the table by membership level, grouping similar values together:
* The first 600,000 rows are `Bronze`.
* The next 300,000 rows are `Silver`.
* The final 100,000 rows are `Gold`.

Let's calculate the RLE representation of these bitmaps:
* **Bronze Bitmap**: 600,000 ones followed by 400,000 zeros. RLE represents this as two numbers: `(600000, 400000)`. Storing this requires just 8 or 16 bytes.
* **Silver Bitmap**: 600,000 zeros, 300,000 ones, and then 100,000 zeros. RLE represents this as: `(600000, 300000, 100000)`. Storing this requires just 12 or 24 bytes.
* **Gold Bitmap**: 900,000 zeros followed by 100,000 ones. RLE represents this as: `(900000, 100000)`. Storing this requires just 8 or 16 bytes.

The compressed size of all three bitmaps is less than 100 bytes. This demonstrates how sorting combined with run-length encoding turns megabytes of raw data into bytes.

#### Example 3: Query Execution and CPU Cache Optimization with Vectorized Processing
Suppose we want to apply a 10% tax rate to a column of 100,000 product prices:
`SELECT price * 1.10 FROM sales;`

The `price` column is stored as a 64-bit float.

* **Row-Oriented Engine**: The database processes one row at a time. It uses an expression interpreter, calling a virtual function or evaluating an abstract syntax tree (AST) node for every single multiplication. This introduces 100,000 virtual function calls, pointer chasing in memory, and high CPU cache-miss rates.
* **Column-Oriented Engine**: The database loads a contiguous array of float prices (say, 1,000 values at a time) into L1 CPU cache. The engine runs a tight, compiled loop over this array. This loop fits entirely within the L1/L2 cache and executes multiple multiplications per clock cycle using SIMD hardware. 

The column store runs this query with only 100 loop iterations (processing batches of 1,000 values) and zero function-call overhead. This executes up to 10 to 100 times faster.

## Pros
- Loading only the requested columns reduces disk IO dramatically for analytical queries.
- Storing identical data types in contiguous files allows highly effective compression like bitmap and run-length encoding.
- Separating analytical databases from transactional databases keeps heavy reporting workloads from degrading user experience.
- Materialized views and data cubes provide rapid response times for common aggregate queries.
- Running SIMD loop instructions on contiguous arrays maximizes CPU instruction pipeline efficiency.

## Cons
- Writing data is slow because inserting or updating a single row requires writing to many separate files.
- Fetching a single complete row is expensive because the database must stitch together values from separate column files.
- Maintaining ETL pipelines adds operational complexity, data drift risk, and synchronization delays.
- Storing materialized views consumes extra disk space and requires background updates when underlying data changes.
- Loading unstructured or dynamic schema-less data is difficult because columns require rigid data definitions.

## Alternatives
- **Row-oriented databases with indexes**: Standard OLTP databases using B-trees can run reporting queries by using secondary indexes, which works well for small datasets.
- **In-memory column stores**: Engines like DuckDB can store column data directly in memory, making local analytical queries fast without disk bottlenecks.
- **Hybrid Row-Columnar Stores**: Some databases use hybrid storage (HTAP), storing recent data in a row format for writes and older data in a column format for analytics.
- **Pre-aggregated data stores**: Timeseries databases store pre-aggregated metrics, which is useful when historical raw records are not needed.
- **NoSQL document stores with MapReduce**: Dynamic collections like MongoDB can compile aggregations, but they run slowly because they parse complete records without columnar optimization.

## When to use it
Use column-oriented databases in data warehouses when you must scan and aggregate billions of rows of historical data. Reach for a columnar engine like Snowflake, ClickHouse, or Google BigQuery when your queries use fields like `SUM`, `AVG`, or `GROUP BY` across a small subset of columns.

## When NOT to use it
Do not use column-oriented storage as your primary application database where users update profiles or create comments. Reach for a row-oriented OLTP database like PostgreSQL instead. Do not use columnar storage when your application requires low-latency, single-row lookups or high-concurrency writes.

## Key takeaways / mental model
Think of a row-oriented database as a book where each page represents a single record. To find the average age of all users, you must turn every page in the book and read the whole sheet just to extract the age. Think of a column-oriented database as a set of index card boxes, where one box contains all the ages, another contains all the first names, and another contains all the registration dates. To find the average age, you only need to grab the age box, saving you from reading any names or registration dates.

## Self-check questions
1. Why does inserting a single row into a columnar database cause a performance bottleneck, and how do LSM-trees resolve this issue?
2. When would a snowflake schema be preferred over a star schema, and what is the trade-off regarding join costs?
3. Suppose a column has 10,000,000 rows and 500,000 unique values. Why is bitmap encoding a bad choice for this column, and what compression technique would work better?
4. How do different sort orders across database replicas improve analytical query performance?
5. Why are virtual function calls in row-oriented expression evaluation slow, and how does vectorized processing solve this?
6. Imagine you have a retail database with a sales table. You want to query the total sales of shoe brands in store locations on weekends. Explain how a data cube can answer this query quickly, and why raw column scans are still necessary for other queries.
7. What is the role of an ETL pipeline in a data warehouse architecture, and why is it dangerous to run heavy OLAP queries directly on an active production OLTP database?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 3: Storage and Retrieval.
- Prerequisites: [04-storage-engines.md](../lessons/04-storage-engines.md)