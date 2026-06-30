---
id: ddia/02
subject: ddia
title: "Data Models: Relational, Document, and Graph"
slug: data-models
status: drafted
mastery:
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 2
prerequisites: [ddia/01]
created: 2026-06-30
updated: 2026-06-30
---

# Data Models: Relational, Document, and Graph

## TL;DR
The data model you choose shapes how you think about problems and determines which operations are simple and which are painful. Relational databases organize data into tables and excel at many-to-many relationships via joins. Document stores map data directly to hierarchical JSON structures, offering great read locality at the cost of poor join performance. Graph databases treat entities and their connections as first-class citizens, making complex, variable-length relationship traversals extremely fast and expressive.

## The idea
A data model is one of the most critical abstractions in software engineering. When building an application, you represent real-world concepts as code objects, map those objects to a database model (like tables or documents), and store them as raw bytes on disk. 

Every model makes assumptions about how data is read, written, and modified. Selecting a model that aligns with your relationship shapes (one-to-many, many-to-one, or many-to-many) simplifies application logic. Choosing the wrong model forces you to write convoluted code to perform joins, maintain consistency, or traverse paths, turning your database into a bottleneck.

## How it works

### The Evolution of Data Models
In the early days of computing, data management was dominated by mainframe databases:
* **The Hierarchical Model**: Used by IBM's Information Management System (IMS). This model represented data as trees of nested records. It worked well for simple one-to-many relationships but struggled with many-to-many structures. Because a record could only have one parent, representing interconnected data required duplicating records or manually managing raw pointers.
* **The CODASYL Network Model**: Developed to solve the hierarchical model's limitations. In a network database, a record could have multiple parents, allowing many-to-many relationships. However, queries required a manual "database path navigation" model. A developer had to write code that iterated through records using physical pointers, manually handling loops and dead ends.
* **The Relational Model**: Proposed by Edgar Codd in 1970. Relational databases grouped data into flat tables (relations) made of tuples (rows). Instead of navigating physical pointers, users wrote declarative queries in SQL. The database engine's **query optimizer** took responsibility for finding the most efficient way to access and join data. Relational won because it hid query optimization from developers, making application code simpler and less dependent on physical storage layouts.

---

### The JSON Document Model and Tree Structures
The modern document model emerged to address the object-relational impedance mismatch. In relational tables, nested tree structures (like a user résumé with experience, education, and contact details) must be split across multiple tables. To load a single profile, you must perform multiple SQL joins.

In a document database like MongoDB, this résumé is stored as a single, self-contained JSON document.

```json
{
  "_id": "user_101",
  "name": "Jane Doe",
  "contact": { "email": "jane@example.com", "phone": "555-0199" },
  "experience": [
    { "company": "Tech Corp", "role": "Senior Engineer", "years": 4 },
    { "company": "Web Inc", "role": "Full Stack Dev", "years": 2 }
  ],
  "education": [
    { "school": "State University", "degree": "BS Computer Science" }
  ]
}
```

This nested structure matches application-level objects, simplifying code.
* **Locality**: Fetching the document requires a single read operation from disk. Because all nested data is stored sequentially, the database avoids random disk seeks.
* **The Locality Cost**: To modify any part of the document (such as updating a single company name), the database must rewrite the entire JSON document to disk. Furthermore, the application must load and parse the full document into memory even if it only needs a tiny nested field.

---

### Relational vs. Document Models
The choice between relational and document models comes down to your relationship patterns:
* **One-to-Many Relationships**: If your data is naturally tree-shaped and you usually load the entire tree at once, the document model excels.
* **Many-to-One / Many-to-Many Relationships**: If entities reference shared metadata (such as referring to a common industry category or region), document databases struggle.

In a normalized relational model, the region or category is stored in a separate table. The user table references it with a foreign key. If you update the category name, you change a single row, and the change propagates to all users.

In a document database, you must choose:
1. **Reference by ID**: Store the category ID in the document and perform joins. Because document databases handle joins poorly (requiring slow client-side queries or complex pipeline aggregation), this defeats the model's simplicity.
2. **Denormalize**: Duplicate the category name directly inside every user document. This speeds up reads but makes updates difficult. You must write a script to locate and update thousands of documents, introducing the risk of data inconsistency.

---

### Convergence of Models
The boundaries between models are blurring. 
* Relational databases (like PostgreSQL) support native JSON columns with indexing, letting you store document-style tree structures inside tables.
* Document databases (like MongoDB) support declarative joins via operators like `$lookup` and enforce structural validation.

You no longer have to select a pure model; you can mix table-based and document-based patterns in a single database.

---

### Schema-on-Read vs. Schema-on-Write Migrations
* **Schema-on-Write (Relational)**: The database enforces a rigid structure when you insert data. Schema changes require explicit Data Definition Language (DDL) migrations.
* **Schema-on-Read (Document)**: The database accepts any JSON payload. The application code must interpret the structure when reading the data.

This difference has a major impact on how you run schema migrations. Let us explore this in a worked example below.

---

### The Graph Data Model
When many-to-many relationships dominate and connections are highly interconnected, graph databases are the best choice.

A graph consists of:
1. **Vertices (Nodes)**: Entities like people, places, or products.
2. **Edges (Relationships)**: Connections between vertices. Edges can be directed and can store properties (like the date a friendship was created).

```
[Person: Alice] --(LIVES_IN)--> [City: New York]
       |
    (FRIEND)
       v
[Person: Bob]   --(LIVES_IN)--> [City: Berlin]
```

There are two primary graph representations:
* **The Property Graph**: Every vertex has a unique identifier, a set of outgoing edges, incoming edges, and a map of key-value properties. Every edge has an identifier, a starting vertex, an ending vertex, a label, and properties.
* **The Triple-Store Model**: Data is stored as three-part statements: `(Subject, Predicate, Object)`. For example: `(Alice, lives_in, New York)`.

#### Query Languages
* **Cypher**: A declarative query language used by property graph databases like Neo4j. It uses ASCII-art style patterns to describe graph traversals.
* **SPARQL**: Used to query triple-stores based on RDF standards.
* **Datalog**: A declarative logic programming language that serves as a foundation for databases like Datomic. It is highly expressive, using recursive rules to express complex queries.

#### When Graphs Beat Relational
Graphs excel at variable-length traversals. In a social network or supply chain, you might want to find "all suppliers of component X down to any depth of subcontractor." Doing this in SQL requires recursive Common Table Expressions (CTEs), which are verbose and difficult to optimize. In Cypher, this is a clean, single-line pattern.

---

## Worked Examples

### Worked Example 1: JSON Résumé Locality Cost Calculation
Let us evaluate the actual performance cost of using a document database for non-local updates, compared to a normalized relational database.

Suppose we have a large organization with 10,000 employees. Each employee has a rich profile document containing history, skills, and background. The average document size is 2 Megabytes (MB).

We need to update a single field for employee Jane Doe: marking her `is_active` status as `true`.

**Scenario A: Document Store (MongoDB)**
1. The application must update the document. Because JSON engines typically serialize and write entire documents, the database must write the modified 2 MB document back to disk.
2. *Disk write overhead*: 2,000,000 bytes.
3. *Network overhead*: The application must send the updated document payload (or a specific patch that MongoDB must apply by parsing, updating, and writing the 2 MB page).
4. If we must update the status of 1,000 employees in a batch, the system must rewrite 2 Gigabytes (GB) of data to disk.

**Scenario B: Relational Store (PostgreSQL)**
1. The schema is normalized. The `is_active` boolean field is stored in a flat `employees` table.
2. We run the query: `UPDATE employees SET is_active = true WHERE id = 101;`
3. PostgreSQL updates a single field in a fixed-size row.
4. *Disk write overhead*: The database writes only the modified page containing the row (typically 8 Kilobytes (KB)), plus a small Write-Ahead Log (WAL) entry of about 100 bytes.
5. Updating 1,000 employees in a batch requires modifying a few index pages and table pages, writing under 50 MB of data.

This calculation shows that while document databases are fast for fetching a whole tree, they introduce massive write and serialization overhead when making small updates to large documents.

---

### Worked Example 2: Schema Migration Execution
Let us compare how a schema change is executed in both models. We want to split a single `name` field into `first_name` and `last_name`.

#### Relational Migration (Schema-on-Write)
In a relational database, you must run an explicit migration script before shipping the new code:

```sql
-- 1. Add the new columns
ALTER TABLE users ADD COLUMN first_name VARCHAR(255);
ALTER TABLE users ADD COLUMN last_name VARCHAR(255);

-- 2. Populate the new columns by splitting the existing name field
UPDATE users 
SET first_name = split_part(name, ' ', 1),
    last_name = split_part(name, ' ', 2);

-- 3. Drop the old column (usually done after verifying the deployment)
ALTER TABLE users DROP COLUMN name;
```

*Trade-off*: This migration guarantees that every row in the database conforms to the new schema. However, running an update on a table with millions of rows can lock the database, causing a production outage unless managed with advanced online schema change tools.

#### Document Migration (Schema-on-Read)
In a document database, you do not need to run an immediate database migration. You simply ship application code that can handle both the old and new data structures:

```javascript
// Application reading user documents
function getUserProfile(userId) {
  const user = db.users.findOne({ _id: userId });
  
  // If the document still has the old single 'name' field, split it on the fly
  if (user.name && (!user.first_name || !user.last_name)) {
    const parts = user.name.split(' ');
    user.first_name = parts[0];
    user.last_name = parts[1] || '';
  }
  
  return user;
}
```

*Trade-off*: This avoids table-locking migrations and makes deployment instant. However, it shifts the complexity to the application code, which must permanently maintain fallback logic to handle old document versions.

---

### Worked Example 3: Relational SQL vs. Graph Cypher
Let us compare the same query written in SQL and Cypher. 

**The Task**: Find all friends of friends of Alice (a 2-hop friendship traversal) who live in "Berlin", returning their names.

#### Relational SQL Approach
We have two tables: `users` and `friendships`.

```sql
SELECT DISTINCT u2.name
FROM users u0
JOIN friendships f1 ON u0.id = f1.user_id
JOIN users u1       ON f1.friend_id = u1.id
JOIN friendships f2 ON u1.id = f2.user_id
JOIN users u2       ON f2.friend_id = u2.id
WHERE u0.name = 'Alice'
  AND u2.city = 'Berlin'
  AND u2.id <> u0.id; -- Exclude Alice herself
```

To run this, the SQL query optimizer must perform four joins across two tables. If we wanted to search 3 or 4 hops deep (friends of friends of friends), the SQL query would explode in length and complexity, requiring additional joins for every hop.

#### Graph Cypher Approach
The graph database stores `Person` vertices connected by `FRIEND` and `LIVES_IN` edges.

```cypher
MATCH (alice:Person {name: 'Alice'})-[:FRIEND*2]-(fof:Person)-[:LIVES_IN]->(:City {name: 'Berlin'})
WHERE fof <> alice
RETURN DISTINCT fof.name
```

*Comparison*: Cypher uses a visual pattern matcher (`-[:FRIEND*2]-`) that natively represents the hops. Under the hood, the graph database does not perform heavy table joins. Instead, it starts at the Alice vertex and traverses the memory-mapped pointers representing the `FRIEND` edges, resulting in significantly higher performance for deep traversals.

---

## Comparison Table

| Attribute | Relational Model | Document Model | Graph Model |
| --- | --- | --- | --- |
| **Primary Relationship** | Many-to-Many and Many-to-One | Tree-like One-to-Many | Deeply interconnected Many-to-Many |
| **Schema Paradigm** | Schema-on-Write (Strict, early validation) | Schema-on-Read (Flexible, late interpretation) | Dynamic or Flexible schema |
| **Read Locality** | Poor (Requires joining multiple tables) | Excellent (Loads whole document at once) | Good (Traverses connected pointers in memory) |
| **Joins** | Excellent (Native, query optimizer managed) | Poor (Requires application-level handling) | Excellent for traversals, poor for full-table scans |

---

## Pros
- **Optimized for Context**: Each model is tailored to a specific relationship pattern, making matching application data shapes simple.
- **Read Speed (Document)**: Storing entire nested structures as a single document eliminates disk seek latency and join overhead.
- **Traversal Speed (Graph)**: Graph databases use index-free adjacency, allowing queries to follow edges in constant time regardless of the overall graph size.
- **Expressive Queries (Graph)**: Complex relationship patterns that would take dozens of lines of nested SQL joins are written in single-line patterns in Cypher.

## Cons
- **Limited Flexibility (Document)**: Document stores struggle when relationships change from one-to-many to many-to-many, leading to performance issues or data inconsistency.
- **Object-Relational Mismatch**: Relational tables force nested application structures to be flattened, requiring complex ORMs.
- **Operational Overhead (Graph)**: Operating dedicated graph databases increases system maintenance complexity, requiring distinct backup, scaling, and indexing strategies.
- **Higher Application Complexity (Document)**: Schema-on-read pushes data quality verification and fallback logic onto the application code.

## Alternatives
- **The Relational Model**: Mature, general-purpose, and incredibly reliable. It is the default baseline database for almost any project unless proven otherwise.
- **NoSQL Document Model**: MongoDB or Couchbase. Pick this when you are dealing with self-contained, rapidly changing JSON documents with few external relationships.
- **Graph Databases**: Neo4j or Amazon Neptune. Choose this for recommendation systems, fraud detection network analysis, or identity mapping.
- **Multi-Model Databases**: PostgreSQL or ArangoDB. They support multiple paradigms simultaneously, allowing you to use JSON, relational tables, and graph structures in one engine.

## When to use it
Choose a **document** database when you have self-contained data structures (like product catalogs or user settings) where you fetch the entire document together and do not need complex queries across documents. Choose a **relational** database for core transactional applications (such as banking, e-commerce checkouts, and inventory) where you need strict schemas, data integrity, and complex joins. Reach for a **graph** database when the value of your data lies in the connections between entities, such as in social graphs or recommendation systems.

## When NOT to use it
Do not use a document database if you find yourself writing code to join multiple collections together. You are fighting the database model, and you should switch to a relational system. Do not use a graph database for plain, tabular transactional data (such as listing simple customer logs) where relationships are basic. Doing so adds unnecessary query and deployment complexity. Do not use a relational database for unstructured data feeds with hundreds of varying attributes where you cannot define a stable schema.

## Key takeaways / mental model
Data models are layers of abstraction that prioritize some operations at the expense of others. 
* To load hierarchical tree data as a unit, use the document model.
* To manage structured, many-to-many data with strict consistency, use the relational model.
* To discover deep, variable-length patterns across interconnected nodes, use the graph model.

Mismatching your application's data shape with your database model forces you to rebuild missing database features (like joins or traversals) in your application layer, introducing bugs and performance problems.

## Self-check questions
1. Explain how the relational model solved the "database navigation" problem introduced by the CODASYL network model.
2. In a document database, how does denormalization trade read latency for write latency and consistency?
3. Suppose you must query a hierarchical organization chart to find "all managers above employee X up to the CEO." Why does a graph model handle this better than a relational database?
4. What is the fundamental difference between schema-on-read and schema-on-write? How do they relate to static and dynamic programming languages?
5. Identify the performance and disk overhead trade-offs when making small updates to a large document in MongoDB compared to updating a single cell in PostgreSQL.
6. Write a simple Cypher pattern that finds any paths from a user to a recommended product through mutual friends who purchased that product.

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 2.
- Ed Codd's 1970 paper: "A Relational Model of Data for Large Shared Data Banks".
- Neo4j Graph Database Documentation (Cypher Query Language Guide).
