---
id: system-design/05
subject: system-design
title: "Probabilistic Data Structures for Scale"
slug: probabilistic-data-structures
status: drafted
mastery:
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 3"
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# Probabilistic Data Structures for Scale

## TL;DR
At hyper-scale, exact tracking of set membership, item frequency, or unique counts requires massive memory that degrades performance. Probabilistic data structures trade absolute certainty for fixed, sub-linear memory footprints. They use mathematical approximations to answer these queries in constant time and tiny space.

## The idea
When systems grow to billions of items, traditional data structures like hash sets or balanced trees consume unacceptable amounts of memory. For example, keeping track of every unique user who visited a website or checking if a username is taken becomes a bottleneck. If you store millions of string IDs in memory, you quickly run out of RAM.

Probabilistic data structures solve this memory constraint. They do not store the actual keys. Instead, they use compact representations, typically bit arrays or nested tables, updated via multiple independent hash functions. The core trade-off is accuracy. You accept a small, mathematically predictable error rate (such as false positives or slight frequency overestimations) to gain constant time complexity and a tiny, constant memory footprint.

## How it works
To understand these structures, we will explore three foundational types: Bloom filters, Count-Min sketches, and HyperLogLogs.

### 1. Bloom Filters (Set Membership)
A Bloom filter answers the question: "Is this item in the set?" It can return two answers:
- "No" (absolute certainty, no false negatives).
- "Yes" (with a small probability of being a false positive).

It consists of:
- A bit array of size m, initialized to all zeros.
- k independent, uniform hash functions that map any input key to an index in [0, m-1].

#### Insertion
To insert an item, run it through all k hash functions to get k indices. Set the bits at those indices to 1.

#### Query
To query an item, run it through all k hash functions. If any of the bits at those indices is 0, the item is definitely not in the set. If all bits are 1, the item might be in the set.

#### False Positive Intuition
As more items are added, more bits are set to 1. Eventually, a query for an uninserted item might hit indices that were set to 1 by other, unrelated items. This causes a false positive. We can tune the false positive rate by selecting appropriate values for m (bit array size) and k (number of hash functions) based on the expected number of items n.

#### Key System Integration: LSM-Tree Storage Engines
In Log-Structured Merge-tree (LSM-tree) storage engines, such as those in Apache Cassandra or RocksDB (concepts discussed in DDIA Chapter 4, Storage Engines), data is written to immutable SSTables on disk. When searching for a key, the engine might have to read multiple SSTables. This causes significant disk read overhead. Placing a Bloom filter in memory for each SSTable allows the engine to instantly skip tables that definitely do not contain the key. Doing so avoids expensive disk lookups.

Another use case is checking if a user has already seen a specific post in a social media recommendation feed. When the filter returns false, the post is definitely unseen. If it returns true, the post might have been seen, so we skip it to be safe.

### 2. Count-Min Sketch (Frequency Estimation)
A Count-Min sketch estimates the frequency of events in a stream, such as tracking heavy hitters or rate-limiting. It uses sub-linear memory and only overestimates frequency, never underestimating.

It consists of:
- A two-dimensional array (table) of depth d and width w.
- d independent hash functions, where each hash function corresponds to one row in the table and maps keys to a column index in [0, w-1].

#### Insertion
For each row i from 0 to d-1, hash the item using hash function h_i to get column index c. Increment the value at cell [i, c] by 1 (or the event count).

#### Query
To estimate the count of an item, hash it using each hash function to find the corresponding cell in each row. The estimated frequency is the minimum value among all these cells. Taking the minimum minimizes the impact of hash collisions across different rows.

### 3. HyperLogLog (Cardinality Estimation)
A HyperLogLog (HLL) estimates the number of unique elements (cardinality) in a dataset with an exceptionally small memory footprint, typically less than 2 kilobytes for millions of items.

#### Intuition
If you flip a coin and get a long sequence of heads, you expect that you have flipped the coin many times. Similarly, HLL hashes incoming items to binary strings and looks at the number of leading zeros. If the hash function distributes bits uniformly, seeing a hash starting with r zeros suggests that we have processed roughly 2^(r+1) unique items.

To reduce variance, HLL divides the hash space into m registers (where m is a power of 2).
- First, a few bits of the hash determine which register to update.
- Remaining bits are used to count leading zeros.
- Each register stores the maximum number of leading zeros seen for that bucket.
- Calculating the final estimate uses the harmonic mean of the register values, scaled by a correction factor.

---

### Worked Examples

#### Worked Example 1: Bloom Filter Insert and Query
Let's build a Bloom filter with a bit array size m = 8 (indices 0 to 7) and k = 2 hash functions:
- h_1(x) = (hash(x) * 3 + 5) mod 8
- h_2(x) = (hash(x) * 7 + 2) mod 8

Initially, our bit array is:
`[0, 0, 0, 0, 0, 0, 0, 0]`

##### Step 1: Insert "user_123"
Assume hash("user_123") = 10.
- h_1("user_123") = (10 * 3 + 5) mod 8 = 35 mod 8 = 3
- h_2("user_123") = (10 * 7 + 2) mod 8 = 72 mod 8 = 0

We set bits at indices 0 and 3 to 1.
The bit array becomes:
`[1, 0, 0, 1, 0, 0, 0, 0]`

##### Step 2: Insert "user_456"
Assume hash("user_456") = 17.
- h_1("user_456") = (17 * 3 + 5) mod 8 = 56 mod 8 = 0
- h_2("user_456") = (17 * 7 + 2) mod 8 = 121 mod 8 = 1

We set bits at indices 0 and 1 to 1.
The bit array becomes:
`[1, 1, 0, 1, 0, 0, 0, 0]`

##### Step 3: Query "user_789" (True Negative)
Assume hash("user_789") = 22.
- h_1("user_789") = (22 * 3 + 5) mod 8 = 71 mod 8 = 7
- h_2("user_789") = (22 * 7 + 2) mod 8 = 156 mod 8 = 4

We check indices 7 and 4. Both are 0.
This is a true negative. We know for sure that "user_789" is not in the set.

##### Step 4: Query "user_abc" (False Positive)
Assume hash("user_abc") = 2.
- h_1("user_abc") = (2 * 3 + 5) mod 8 = 11 mod 8 = 3
- h_2("user_abc") = (2 * 7 + 2) mod 8 = 16 mod 8 = 0

We check indices 3 and 0 in our bit array `[1, 1, 0, 1, 0, 0, 0, 0]`. Both are 1.
The filter returns "Yes, this item is in the set", even though we never inserted "user_abc".
This is a false positive. It happened because other insertions set those bits.

---

#### Worked Example 2: Count-Min Sketch Frequency Counting
Let's build a Count-Min Sketch with depth d = 3 (rows 0, 1, 2) and width w = 4 (columns 0, 1, 2, 3).
Initially, the sketch table is:
```
Row 0: [0, 0, 0, 0]
Row 1: [0, 0, 0, 0]
Row 2: [0, 0, 0, 0]
```
Our 3 hash functions:
- h_0(x) = (hash(x) * 3) mod 4
- h_1(x) = (hash(x) + 2) mod 4
- h_2(x) = (hash(x) * 5 + 1) mod 4

##### Step 1: Insert "item_A" (Count = 1)
Assume hash("item_A") = 5.
- Row 0: h_0("item_A") = (5 * 3) mod 4 = 15 mod 4 = 3. Increment cell [0, 3].
- Row 1: h_1("item_A") = (5 + 2) mod 4 = 7 mod 4 = 3. Increment cell [1, 3].
- Row 2: h_2("item_A") = (5 * 5 + 1) mod 4 = 26 mod 4 = 2. Increment cell [2, 2].

The sketch table becomes:
```
Row 0: [0, 0, 0, 1]
Row 1: [0, 0, 0, 1]
Row 2: [0, 0, 1, 0]
```

##### Step 2: Insert "item_B" (Count = 1)
Assume hash("item_B") = 2.
- Row 0: h_0("item_B") = (2 * 3) mod 4 = 6 mod 4 = 2. Increment cell [0, 2].
- Row 1: h_1("item_B") = (2 + 2) mod 4 = 4 mod 4 = 0. Increment cell [1, 0].
- Row 2: h_2("item_B") = (2 * 5 + 1) mod 4 = 11 mod 4 = 3. Increment cell [2, 3].

The sketch table becomes:
```
Row 0: [0, 0, 1, 1]
Row 1: [1, 0, 0, 1]
Row 2: [0, 0, 1, 1]
```

##### Step 3: Insert "item_A" again (Count = 2 total)
We increment the same cells as in Step 1: [0, 3], [1, 3], and [2, 2].
The sketch table becomes:
```
Row 0: [0, 0, 1, 2]
Row 1: [1, 0, 0, 2]
Row 2: [0, 0, 2, 1]
```

##### Step 4: Estimate frequency of "item_A"
We check the cells for "item_A":
- Row 0, column 3: value is 2
- Row 1, column 3: value is 2
- Row 2, column 2: value is 2

Minimum is min(2, 2, 2) = 2. This matches the actual count of 2.

##### Step 5: Estimate frequency of "item_C" (Uninserted item)
Assume hash("item_C") = 1.
- Row 0: h_0("item_C") = (1 * 3) mod 4 = 3. Cell [0, 3] value is 2.
- Row 1: h_1("item_C") = (1 + 2) mod 4 = 3. Cell [1, 3] value is 2.
- Row 2: h_2("item_C") = (1 * 5 + 1) mod 4 = 6 mod 4 = 2. Cell [2, 2] value is 2.

Our cells are [0, 3] = 2, [1, 3] = 2, and [2, 2] = 2.
Minimum is min(2, 2, 2) = 2.
This is an overestimation (actual count is 0). The collision happened because our table size is extremely small. In a real system with wider tables and more rows, collisions are rare.

---

#### Worked Example 3: HyperLogLog Cardinality Estimation
Let's build a small HyperLogLog with m = 4 registers (R_0, R_1, R_2, R_3).
The registers are initialized to zero:
`[0, 0, 0, 0]`

Our hash function maps items to a 6-bit binary string.
The first 2 bits determine the register index (0 to 3).
The remaining 4 bits are searched for leading zeros. We count the position of the first 1-bit from the left (starting at 1). For example:
- `1000` has 0 leading zeros, so first 1-bit is at position 1.
- `0100` has 1 leading zero, so first 1-bit is at position 2.
- `0001` has 3 leading zeros, so first 1-bit is at position 4.

##### Step 1: Process "item_alpha"
Assume hash("item_alpha") = 010100 (binary).
- Register bits: `01` (binary) = 1 (decimal). This maps to R_1.
- Value bits: `0100` (binary). The first 1-bit is at position 2 (1 leading zero).
- Update R_1: max(0, 2) = 2.
Registers: `[0, 2, 0, 0]`

##### Step 2: Process "item_beta"
Assume hash("item_beta") = 110001 (binary).
- Register bits: `11` = 3. This maps to R_3.
- Value bits: `0001`. The first 1-bit is at position 4 (3 leading zeros).
- Update R_3: max(0, 4) = 4.
Registers: `[0, 2, 0, 4]`

##### Step 3: Process "item_gamma"
Assume hash("item_gamma") = 011000 (binary).
- Register bits: `01` = 1. This maps to R_1.
- Value bits: `1000`. The first 1-bit is at position 1 (0 leading zeros).
- Update R_1: max(2, 1) = 2.
Registers: `[0, 2, 0, 4]`

##### Step 4: Estimate Cardinality
The standard HyperLogLog estimation formula uses the harmonic mean of the registers:
`Estimate = alpha_m * m^2 * (sum_{j=0}^{m-1} 2^{-R_j})^{-1}`

Where alpha_m is a correction constant. For m=4, let's simplify and use alpha_m = 0.673.
- R_0 = 0 -> 2^(-0) = 1.0
- R_1 = 2 -> 2^(-2) = 0.25
- R_2 = 0 -> 2^(-0) = 1.0
- R_3 = 4 -> 2^(-4) = 0.0625

Sum of values: 1.0 + 0.25 + 1.0 + 0.0625 = 2.3125.
Harmonic term: 2.3125^(-1) approx 0.4324.
Multiply by m^2 = 16: 16 * 0.4324 approx 6.918.
Multiply by correction factor alpha_4 = 0.673: 6.918 * 0.673 approx 4.65.

The actual number of unique elements we processed is 3 ("item_alpha", "item_beta", "item_gamma"). Our estimate is 4.65. While small registers show higher variance, a production deployment with 1024 registers yields highly accurate estimations within a 1-2% standard error.

---

### Space-vs-Accuracy Comparison

| Structure | Typical Memory Footprint | Query Time Complexity | Type of Error | Key Tuning Parameters |
| :--- | :--- | :--- | :--- | :--- |
| **Hash Set (Exact)** | O(N * size) | O(1) | None (Exact) | None |
| **Bloom Filter** | 9.6 bits per item (for 1% error) | O(k) | False positives only | Array size m, hash count k |
| **Count-Min Sketch** | Fixed (e.g., a few kilobytes) | O(d) | Overestimation only | Depth d, width w |
| **HyperLogLog** | Fixed (typically 1.5 KB) | O(1) | Cardinality standard error (~ 1.04 / sqrt(m)) | Register count m |

---

## Pros
- Tiny, constant, or sub-linear memory footprints that fit entirely in fast CPU cache or RAM.
- Constant-time query and insertion operations that do not degrade as the dataset size grows.
- Easily parallelizable, allowing distributed nodes to merge filters or sketches with simple bitwise operations.
- Strong privacy protection because the data structures never store the actual keys, making them impossible to reverse-engineer.

## Cons
- Inability to list or retrieve the actual items inserted into the data structure.
- Absolute lack of support for item deletion, unless you use more complex variants like counting Bloom filters that consume more memory.
- Inherent, mathematically predictable error rates that make them unsuitable for safety-critical or financially audited systems.
- Heavy reliance on independent, uniform, and cryptographically secure or highly distributed hash functions to avoid skewed error rates.

## Alternatives
- **In-memory Hash Sets**: Perfect when exact results are required and the maximum dataset size fits safely within available physical memory.
- **External Databases or Key-Value Stores**: Preferable when you must retrieve the exact keys or values, using SSD-backed indexes or caching to manage latency.
- **Lossy Storage / Sampling**: Ideal when you only need a rough sample of events to analyze patterns rather than maintaining an active set or running exact counts on every item.

## When to use it
- Use a Bloom filter when you want to guard a slow disk or database lookup by first checking if the key is definitely absent.
- Use a Bloom filter to track whether a user has already seen a specific item in a recommendations list without storing millions of historic IDs per user.
- Use a Count-Min Sketch to rate-limit high-volume API clients, where a slight overestimation of requests is acceptable and prevents memory exhaustion.
- Use a HyperLogLog to calculate unique daily active users or unique search queries across millions of sessions where a 1% margin of error is completely acceptable.

## When NOT to use it
- Do not use a Bloom filter when false positives are unacceptable, such as verifying user password hashes or checking security permissions.
- Do not use any probabilistic structure if you need to display the list of items to the user or iterate over the elements in the dataset.
- Do not use a Count-Min Sketch for financial ledger audits or precise billing systems where every single transaction must count exactly once.
- Do not use a HyperLogLog if you need to know exactly which users visited a page, rather than just the total number of unique visitors.

## Key takeaways / mental model
Think of probabilistic data structures as lossy compression for high-volume data streams. Instead of recording the precise details of every passenger on a train, you record general statistics using smart, overlapping indicators. You swap the impossible quest for absolute accuracy at massive scale for lightning-fast answers, predictable errors, and a tiny, rock-solid memory footprint that stays constant forever.

## Self-check questions
1. Why does a Bloom filter guarantee zero false negatives, and under what circumstances can a false positive occur?
2. How does LSM-tree based storage engines use Bloom filters in memory to accelerate read paths? Refer to RocksDB or Cassandra mechanisms.
3. In a Count-Min sketch, why do we take the minimum value across all row hashes rather than the maximum or the average?
4. How does the size of the register array in a HyperLogLog affect the standard error of its cardinality estimate?
5. Why is deleting an item from a standard Bloom filter impossible, and how does a Counting Bloom filter attempt to address this limitation?
6. If you have a budget of 10 bits per item, how would you calculate the optimal number of hash functions for a Bloom filter?

## References
- System Design Guide for Software Professionals (Sinha & Chopra), Chapter 3
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 4, Storage Engines
