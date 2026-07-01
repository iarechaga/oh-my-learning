---
id: ddia/03
subject: ddia
title: Query Languages for Data
slug: query-languages
status: drafted
mastery:
seniority: junior
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 2
prerequisites: [ddia/02]
created: 2026-06-30
updated: 2026-06-30
---

# Query Languages for Data

## TL;DR
Declarative query languages let you specify what data you want without dictating how the database should retrieve it. This separation of concerns allows the underlying engine to optimize query execution, run tasks in parallel, and modify storage structures freely. Imperative code, by contrast, locks the engine into a single manual execution recipe.

## The idea
When relational databases first emerged, they competed against older database models like the CODASYL network model. CODASYL required application developers to write manual traversal code to navigate records. This was imperative data access. If you wanted a specific record, you wrote loops to follow pointers from one record to another. This approach coupled the application code directly to the physical storage layout on disk. If the database administrator restructured a table or added an index, the application code broke immediately.

To solve this coupling problem, declarative query languages were introduced. Instead of spelling out the execution steps, you describe the pattern of the data you want to retrieve. The database engine hides the traversal paths and takes responsibility for finding the data. Because the application specifies the what rather than the how, the database engine can change its physical storage formats, add or remove indexes, and rewrite execution paths without breaking existing queries. This design provides data independence and lets database engines get faster over time without requiring application changes.

## How it works

### Imperative vs declarative: Side-by-side animals example
To understand the difference, look at how an imperative system and a declarative system solve the same problem. Suppose you have a database of marine animals and want to retrieve all sharks.

In an imperative programming style, you write a loop to scan the collection. You control the exact sequence of instructions.

```javascript
// Imperative approach (Javascript)
function getSharks(animals) {
    let sharks = [];
    for (let i = 0; i < animals.length; i++) {
        if (animals[i].family === "Sharks") {
            sharks.push(animals[i]);
        }
    }
    return sharks;
}
```

In a declarative query language like SQL, you state the conditions of the target dataset.

```sql
-- Declarative approach (SQL)
SELECT * FROM animals WHERE family = 'Sharks';
```

#### Worked Example 1: Execution paths of the Sharks filter
Let's trace how a relational database engine processes the declarative SQL query under three different scenarios. The database optimizer reads the query, looks at table statistics, and chooses the best plan.

*   **Scenario A: No Index exists.**
    The engine analyzes the query and notes that no index is defined on the `family` column. It chooses a Sequential Scan. It reads the table pages from disk sequentially, checks the `family` column of each row, and adds matching rows to the result set. This is a fallback path with O(N) complexity.

*   **Scenario B: A B-Tree index exists on the `family` column.**
    The optimizer detects the index. Instead of scanning millions of records, it performs an index seek. It traverses the B-Tree index to find the pointer to the first entry where `family = 'Sharks'`, then reads subsequent index entries sequentially until the family changes. It retrieves the actual data rows from the heap file using the pointers stored in the index. The search complexity drops from O(N) to O(log N).

*   **Scenario C: Parallel Execution on a partitioned table.**
    The table is large and partitioned across four disk volumes. The query engine sees that the CPU has multiple cores. It splits the scan into four parallel tasks, each running on a separate core, scanning one partition. It merges the sub-results in memory before returning them.

If you had written the imperative Javascript loop, the engine would be forced to run the code exactly as written: sequentially, row by row, starting from index 0. The engine cannot automatically split your loop across cores or skip elements using an index because the loop dictates a rigid, single-threaded execution sequence.

### Why declarative queries enable optimization and parallelism
A declarative query language is essentially a domain-specific language that represents a logical expression. Because the expression does not specify execution mechanics, the database query planner can perform three major optimizations:

1.  **Index Selection**: The optimizer determines which indexes will minimize disk reads. If multiple indexes are available, it uses statistics like cardinality and histogram distributions to predict which index is more selective.
2.  **Join Ordering**: When a query joins five tables, there are 120 possible orderings to execute those joins. Some orderings might require scanning billions of temporary rows, while others require only a few dozen. Relational optimizers estimate the costs of different join strategies (such as nested loops, hash joins, or merge joins) and choose the most efficient path.
3.  **Parallel Execution**: The query optimizer can split the query plan into independent stages and execute them concurrently on different CPU cores or even across multiple machines in a distributed database cluster.

Additionally, because the application is decoupled from the storage format, database developers can rewrite the storage engine internals, introduce advanced compression algorithms, or change how data is laid out on disk. The declarative query continues to function without modifications, automatically gaining the performance benefits of those engine-level enhancements.

### The CSS and XSL web analogy
The web platform uses the same architectural pattern to separate visual styling from document structure.

Consider styling a web page to make selected list items blue. In CSS, which is a declarative language, you write a pattern match selector:

```css
/* Declarative CSS */
li.selected > p {
    color: blue;
}
```

The browser engine analyzes this selector and matches it against the Document Object Model (DOM). It applies the style to the correct nodes. The browser developer can optimize the matching engine, cache style evaluations, or run selector matching on background threads. Your CSS rule remains unchanged.

Now consider the imperative alternative where you manually walk the DOM tree in Javascript:

```javascript
// Imperative Javascript DOM manipulation
function styleSelectedParagraphs(root) {
    let listItems = root.getElementsByTagName("li");
    for (let i = 0; i < listItems.length; i++) {
        if (listItems[i].classList.contains("selected")) {
            let children = listItems[i].childNodes;
            for (let j = 0; j < children.length; j++) {
                if (children[j].nodeName === "P") {
                    children[j].style.color = "blue";
                }
            }
        }
    }
}
```

This code has several fatal flaws compared to the CSS rule. It is long and difficult to read. It hardcodes a specific structural assumption about the DOM. If the paragraph element is wrapped in a new container div later, the Javascript walk fails to style the text because it only checks immediate child nodes. The declarative CSS selector `li.selected > p` or `li.selected p` can easily adapt to these structural shifts.

### MapReduce in depth: The hybrid ground
MapReduce is a programming model popularized by Google for processing massive datasets in parallel across clusters of machines. It sits in a unique middle ground: it is neither fully declarative nor fully imperative.

You write the core logic using small, imperative snippets of code: a mapper function and a reducer function. However, you do not manage the execution. The MapReduce framework handles the distribution, data partitioning, machine failures, and network transfers.

#### Worked Example 2: Counting shark observations by month
Let's see how MapReduce works with a concrete example. We have raw records of shark observations:

```json
[
  { "id": 101, "species": "Great White", "month": "2026-06" },
  { "id": 102, "species": "Bull Shark", "month": "2026-06" },
  { "id": 103, "species": "Great White", "month": "2026-07" },
  { "id": 104, "species": "Tiger Shark", "month": "2026-06" }
]
```

We write the MapReduce functions in Javascript (using MongoDB syntax):

```javascript
// Imperative Map function: runs on each document independently
function mapSharkObservation() {
    // We emit the month as the key, and 1 as the value
    emit(this.month, 1);
}

// Imperative Reduce function: runs on groups of values sharing the same key
function reduceSharkCount(key, values) {
    // values is an array of emitted numbers, e.g., [1, 1, 1]
    return Array.sum(values);
}
```

Here is the step-by-step physical execution trace of this job:

1.  **Map Phase**: The framework runs `mapSharkObservation` on each node in the cluster where chunks of the database reside.
    *   Record 101 emits: `("2026-06", 1)`
    *   Record 102 emits: `("2026-06", 1)`
    *   Record 103 emits: `("2026-07", 1)`
    *   Record 104 emits: `("2026-06", 1)`
2.  **Shuffle and Sort Phase**: The framework automatically groups the emitted values by key. This is a massive distributed operation. It transfers data across the network so that all values for a given key land on the same reducer node.
    *   Grouped intermediate data:
        *   `"2026-06" -> [1, 1, 1]`
        *   `"2026-07" -> [1]`
3.  **Reduce Phase**: The framework invokes `reduceSharkCount` for each key with its accumulated array of values.
    *   `reduceSharkCount("2026-06", [1, 1, 1])` returns `3`.
    *   `reduceSharkCount("2026-07", [1])` returns `1`.

This model is powerful because the mapper and reducer functions are isolated. They cannot modify database state or communicate with each other directly. This strict limitation allows the framework to run them in parallel and rerun failed tasks on another machine without side effects.

However, writing MapReduce is complex. MongoDB eventually introduced a declarative Aggregation Pipeline to express the same logic without requiring developers to write custom Javascript functions:

```json
// Declarative Aggregation Pipeline
[
  { "$match": { "species": { "$exists": true } } },
  { "$group": { "_id": "$month", "totalCount": { "$sum": 1 } } }
]
```

The aggregation pipeline is declarative. The query planner can inspect this pipeline, reorder steps, optimize memory usage, or decide to use indexes for the `$match` stage. With raw MapReduce, the database engine treats the Javascript functions as black boxes. It cannot optimize what happens inside them, and running Javascript code inside a database engine incurs a massive serialization and execution performance penalty.

### Graph query languages: Cypher, SPARQL, and recursive SQL CTEs
In relational databases, relationships are represented as foreign keys. To traverse a network of relationships, you must perform joins. If you want to traverse a deep, arbitrary path (for example, finding friends of friends of friends), relational SQL queries become complex and slow.

Graph query languages are declarative languages designed specifically to traverse networks of nodes and edges. Let's compare Cypher (used in Neo4j) with relational SQL.

#### Worked Example 3: Finding mutual connections
Suppose you want to find people who are connected to a scientist named Alice through exactly two degrees of separation (Alice knows someone who knows the target person, but Alice does not know the target person directly).

Let's look at the declarative Cypher query:

```cypher
// Declarative Cypher
MATCH (alice:Person {name: 'Alice'})-[:KNOWS]->(middle)-[:KNOWS]->(target:Person)
WHERE NOT (alice)-[:KNOWS]->(target)
RETURN DISTINCT target.name;
```

This query draws a visual ASCII pattern of the relationship path: `(alice)-[:KNOWS]->(middle)-[:KNOWS]->(target)`. The query engine reads this pattern and chooses how to traverse the graph: it might start from Alice and follow outgoing edges, or start from target nodes and work backward, depending on which node has fewer connections.

Now consider the equivalent relational SQL query, assuming we have a `persons` table and a `friendships` join table:

```sql
-- Relational SQL equivalent
SELECT DISTINCT p3.name
FROM persons p1
JOIN friendships f1 ON p1.id = f1.person_id
JOIN persons p2 ON f1.friend_id = p2.id
JOIN friendships f2 ON p2.id = f2.person_id
JOIN persons p3 ON f2.friend_id = p3.id
WHERE p1.name = 'Alice'
  AND p3.id != p1.id
  AND p3.id NOT IN (
    SELECT friend_id 
    FROM friendships 
    WHERE person_id = p1.id
  );
```

This SQL query is extremely difficult to read. You must manually chain multiple joins on the `friendships` table. If you want to expand the search to five degrees of separation, you must add five more joins, making the SQL query explode in size.

If you wanted a path of arbitrary length (such as finding any path of any depth between Alice and Bob), standard SQL joins cannot express it. You would have to use a recursive Common Table Expression (CTE), which is famously verbose and difficult to write:

```sql
-- Recursive SQL CTE to find paths of arbitrary depth
WITH RECURSIVE FriendPath AS (
    SELECT person_id, friend_id, 1 AS depth
    FROM friendships
    WHERE person_id = 1 -- Alice's ID
  UNION
    SELECT fp.person_id, f.friend_id, fp.depth + 1
    FROM FriendPath fp
    JOIN friendships f ON fp.friend_id = f.person_id
    WHERE fp.depth < 10
)
SELECT DISTINCT name 
FROM FriendPath fp
JOIN persons p ON fp.friend_id = p.id;
```

In Cypher, arbitrary path traversal is simple:

```cypher
MATCH (alice:Person {name: 'Alice'})-[:KNOWS*1..10]->(target:Person)
RETURN target.name;
```

Graph query languages demonstrate the power of declarative abstraction: by matching the query language to the data model, you make complex relationship traversals easy to write and optimize.

---

## Pros
- **Conciseness**: You express complex search logic in a few lines of readable code rather than writing long, nested loop structures.
- **Query Optimization**: The database optimizer dynamically chooses execution strategies based on real-time data statistics without requiring code rewrites.
- **Physical Decoupling**: You can change disk storage layouts, add compression, or introduce indexes without breaking application queries.
- **Automatic Parallelism**: The query engine can automatically split work across multiple CPU cores or machines in a distributed cluster.

## Cons
- **Indirect Execution Control**: You cannot force a specific step-by-step execution path easily, which can lead to performance issues if the optimizer chooses a sub-optimal plan.
- **Expressiveness Limitations**: Certain highly customized algorithms or complex computational tasks are awkward or impossible to write in pure declarative syntax.
- **Abstraction Leaks**: When queries run slowly, you must read execution plans, inspect index behavior, and sometimes rewrite the query to hint the optimizer.
- **Optimizer Complexity**: Relational optimizers are incredibly complex pieces of software, and bugs in the optimizer can lead to unpredictable query plan regressions.

## Alternatives
- **Imperative Graph Traversals (Gremlin)**: An alternative for graph models where you write chained traversal steps in code, giving you manual control over graph navigation paths.
- **Procedural Stored Procedures**: Code executed directly inside the database engine that combines imperative loops with declarative SQL statements.
- **Custom Distributed Dataflow Engines (Apache Spark, Flink)**: Systems that execute computations on distributed clusters using structured dataflows, combining the programmatic control of imperative languages with the optimizations of declarative systems.

## When to use it
Reach for a declarative query language (such as SQL or Cypher) for standard application features, transactional operations, and reporting. It should be your default interface for any database interaction. The database engine will always be better at selecting indexes, ordering joins, and managing memory than manual application-level loops.

## When NOT to use it
Do not use a declarative query language if your application needs to execute a complex numerical simulation, a highly iterative machine learning algorithm, or custom byte-level data transformations. For these tasks, the rigid structures of SQL are restrictive, and you should instead pull the dataset into an imperative application layer or use a distributed compute engine like Apache Spark.

## Key takeaways / mental model
The mental model of declarative query languages is the separation of intent from execution. You act as the architect who designs the blueprint (the "what"), while the query engine acts as the construction crew that decides the tools and steps to build it (the "how"). By restricting your input to a logical description of the result, you empower the engine to optimize your requests over time as technology improves.

## Self-check questions
1. How does a database query optimizer use table statistics to choose between a sequential scan and an index seek?
2. Why does the declarative nature of CSS make it more resilient to changes in a web page's HTML structure than manual Javascript DOM loops?
3. What is the main structural limitation of MapReduce that allows it to execute safely in parallel across thousands of machines?
4. In what ways does MapReduce represent a hybrid of the declarative and imperative paradigms?
5. Why are recursive relationships (like finding connections of arbitrary depth) so difficult to write in SQL compared to graph query languages like Cypher?
6. Imagine a query that runs fast in test environments but crawls to a halt in production. Explain how this performance degradation represents an abstraction leak in declarative languages.

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 2: Organising Data.
- Prerequisite: [02-data-models.md](02-data-models.md).
