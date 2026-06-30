---
id: ddia/03
subject: ddia
title: Query Languages for Data
slug: query-languages
status: drafted
mastery:
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 2
prerequisites: [ddia/02]
created: 2026-06-30
updated: 2026-06-30
---

# Query Languages for Data

## TL;DR
Declarative query languages (like SQL) describe *what* result you want and let the database engine decide *how* to compute it; imperative code spells out the *how* step by step. Declarative wins for data work because hiding the "how" lets the engine optimize, parallelize, and change its internals without breaking your queries.

## The idea
A query language is the interface to a data model, and it comes in two broad styles. **Imperative** code tells the machine the exact sequence of operations: loop, test, mutate, repeat. **Declarative** code states the properties of the desired result and leaves the algorithm to the system. The problem with imperative data access is that it freezes one execution strategy in place; the engine cannot reorder, index, or parallelize it, because you already committed to a specific recipe. Declarative queries give that freedom back to the database. This follows directly from the data models in [02-data-models.md](02-data-models.md), since each model comes with its own query language.

## How it works

### Imperative vs declarative, side by side
Suppose you want all animals in the family "Sharks".

Imperative (pseudocode): you write the loop yourself.
```
sharks = []
for animal in animals:
    if animal.family == "Sharks":
        sharks.append(animal)
return sharks
```
You dictated the order, the iteration, and the method.

Declarative (SQL):
```
SELECT * FROM animals WHERE family = 'Sharks';
```
You said nothing about *how*. The query optimizer is free to use an index on `family`, choose a join order, or run the scan in parallel across cores and machines. Because the query does not mention the implementation, the database can add a new index or switch storage engines later and your query still works unchanged. Imperative loops are hard to parallelize precisely because their fixed ordering implies dependencies between steps.

### A web analogy
Kleppmann points out the same split on the web. A CSS rule like `li.selected > p { color: blue; }` is **declarative**: you describe which elements to style and the browser figures out how. Doing the same by manually walking and mutating the DOM in JavaScript is **imperative**, longer, and breaks when the page structure changes. The declarative version is both shorter and more robust.

### MapReduce: the middle ground
**MapReduce** sits between the two. You supply small snippets of imperative code - a `map()` function and a `reduce()` function - but the framework owns the distribution, sorting, and parallel execution. For example, to count sharks sighted per month, `map` emits `(month, 1)` for each shark observation and `reduce` sums the counts per month. It is more flexible than SQL for custom distributed computation but more cumbersome to write. Many systems offer a more declarative alternative on top (for instance, MongoDB's aggregation pipeline expresses the same logic without hand-written map/reduce functions).

## Pros
Focusing on **declarative** query languages:
- Concise: you write the intent, not the algorithm.
- The engine optimizes automatically (index selection, join ordering).
- Automatic parallelism across cores and machines.
- Decoupled from storage internals, so engine improvements do not break your queries.

## Cons
- Less direct control over execution; a bad query plan can surprise you.
- Expressiveness limits: some logic is awkward or impossible in pure SQL.
- The abstraction can leak, forcing you to read and hand-tune query plans.
- Low-level approaches like raw MapReduce are harder to write than an equivalent declarative aggregation.

## Alternatives
- **Imperative APIs / procedural code** - full control over execution, but no automatic optimization or parallelism, and tightly coupled to one strategy.
- **MapReduce** - a distributed, lower-level model between declarative and imperative; use it when you need custom computation that a query language cannot express.
- **Declarative graph languages** (Cypher, SPARQL, Datalog) - the declarative idea applied to the graph model, expressing traversals you would otherwise write as many joins.

## When to use it
Use a declarative language (SQL, an aggregation pipeline, or a graph query language) for almost all data access, and let the engine do the optimizing. Reach for MapReduce or a custom dataflow only when you genuinely need distributed computation beyond what the declarative language can express.

## When NOT to use it
Do not drop down to imperative, row-by-row processing in application code for work the database can do in a single query; you lose the optimizer and pull far too much data over the network. And do not use raw MapReduce when a declarative aggregation pipeline produces the same result more simply and readably.

## Key takeaways / mental model
Declarative means "what, not how", which is exactly what lets the engine optimize, parallelize, and evolve underneath you. Imperative means "how", which gives control but rigidly fixes the execution. MapReduce is the hybrid: imperative fragments plugged into a framework that handles distribution. When in doubt, say what you want and let the database figure out the rest.

## Self-check questions
1. Why can declarative queries be parallelized and optimized more easily than imperative loops?
2. Explain the CSS-versus-DOM analogy for declarative versus imperative.
3. Where does MapReduce sit on the imperative/declarative spectrum, and why might you prefer a declarative aggregation instead?
4. Name one real downside of declarative query languages.

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 2.
- Prerequisite: [02-data-models.md](02-data-models.md).
