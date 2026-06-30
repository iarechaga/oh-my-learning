---
id: fundamentals/13
subject: fundamentals
title: Pipeline Architecture
slug: pipeline-architecture
status: drafted
mastery:
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 13
prerequisites: [fundamentals/09, fundamentals/10]
created: 2026-06-30
updated: 2026-06-30
---

# Pipeline Architecture

## TL;DR
Pipeline architecture, also known as pipe-and-filter, structures processing tasks into sequential steps. Each step executes independently inside a filter, while pipes transfer data between them. This approach delivers exceptional modularity and testability for processing tasks that run in a linear flow.

## The idea
Software systems often need to transform data in a series of predictable steps. When you group validation, cleaning, calculations, and database updates into one massive codebase, it becomes hard to read. Changing a single business rule risks breaking unrelated logic.

Pipeline architecture solves this by breaking the entire task into self-contained units. Instead of one complex service, you build multiple small filters. Each filter focuses on one operation. Pipes connect these filters together, passing data unidirectionally from one to the next.

This isolation means you can swap, update, or remove filters without disturbing the rest of the application. It creates a highly flexible pipeline. The architecture models data as a stream flowing through a clean processing line.

## How it works
This style depends on two primary concepts: pipes and filters.

Pipes act as communication channels. They are unidirectional, point-to-point lines that carry data from one filter to another. Depending on your system design, pipes can be in-memory streams, network buffers, or distributed message queues.

Filters do the actual work. They are completely independent. A filter doesn't know which filter came before it, nor does it know which one follows. It only cares about receiving data from its input pipe, performing its specific task, and pushing the result to its output pipe.

Filters generally fall into four functional categories:

1. **Producer**: The source of data. It reads from a database, watches a directory, or listens to an external feed.
2. **Transformer**: This is the most common filter. It takes input, modifies it, and outputs the result.
3. **Tester**: It validates or checks conditions. It decides if data should continue down the main pipe or divert to an alternative branch.
4. **Consumer**: The final sink. It saves the final data to a database, generates a report, or sends a notification.

### An Order Ingestion Example
Let's trace a pipeline that processes raw customer orders.

1. **Order File Reader (Producer)**: Reads raw order records from an incoming CSV stream.
2. **First Pipe**: An in-memory queue that buffers the raw CSV records.
3. **Validator (Tester)**: Parses the fields. It ensures the email address contains an "@" symbol and that quantities are positive.
4. **Second Pipe**: Passes valid orders forward.
5. **Tax Calculator (Transformer)**: Inspects the customer's region and adds the appropriate sales tax.
6. **Third Pipe**: Transfers orders with calculated taxes.
7. **Database Writer (Consumer)**: Inserts the finished record into the transaction database.

Below is an ASCII representation of this unidirectional data flow:

```
[CSV Stream]
     |
     v
[Producer: File Reader]
     |
  (Pipe 1)
     v
[Tester: Validator] -----(Invalid Records)-----> [Error Log]
     |
  (Pipe 2)
     v
[Transformer: Tax Calculator]
     |
  (Pipe 3)
     v
[Consumer: DB Writer]
     |
     v
[Database]
```

## Architectural characteristics analysis
Let's analyze how the pipeline architecture style performs across key architectural characteristics:

- **Deployability**: Low. Filters are often bundled together into a single application package. If you make a change to one filter, you must redeploy the entire pipeline.
- **Scalability**: Low to Medium. While you can run multiple instances of a pipeline, scaling individual filters is difficult unless they are deployed as separate processes or services.
- **Elasticity**: Low. The pipeline cannot easily scale up or down instantly to handle sudden bursts of data unless it is integrated with an elastic queue infrastructure.
- **Reliability**: Low to Medium. A failure in one filter halts the entire sequence unless you implement complex retry logic or dead-letter queues.
- **Performance**: Medium. High data volume can cause bottlenecks in the slowest filter, and converting data between filters adds serialization overhead.
- **Simplicity**: High. This style is exceptionally simple to understand, design, and write.
- **Cost**: Low. Minimal runtime overhead and simple deployments keep operational costs very low.
- **Testability**: High. You can isolate each filter and test it with mock inputs and outputs, leading to high-quality code.
- **Team fit**: High. A single small team can easily own and maintain a pipeline, as boundaries between processing tasks are extremely clear.

## Pros
- **High Modularity**: Because filters are isolated, you can change one filter's internal logic without touching others.
- **Strong Testability**: It's easy to write unit tests for each filter because you can feed mock data directly into its input.
- **Easy Reusability**: You can reuse a filter (like a validator) across entirely different pipelines.
- **Simple Extensibility**: Adding a new step, like a fraud checker, is as simple as inserting it between two existing pipes.

## Cons
- **Performance Overhead**: Converting data formats between pipes and filters can consume valuable CPU cycles.
- **Linear Coupling**: The entire process is bound to a single sequence, making complex, interactive flows difficult.
- **Loss of ACID Guarantees**: Enforcing a single database transaction across multiple distributed filters is extremely complex.
- **State Complexity**: If a filter needs complex historical context, managing that state across steps becomes difficult.

## Alternatives
- **Layered Architecture**: Enforces technical divisions like UI, business logic, and database access. It's better for interactive applications.
- **Event-Driven Architecture**: Uses brokers or mediators to handle highly dynamic, non-linear workflows with complex routing.

## When to use it
Reach for pipeline architecture when your system processes data in a clear, sequential path. It's a great fit for:
- Data import and cleaning tools.
- Video and audio processing applications where data is manipulated in distinct phases.
- Compilers that run code parsing, semantic analysis, and code generation.

## When NOT to use it
Avoid this style for interactive, user-facing web applications. If your users expect instant feedback and make dynamic, circular requests, a pipeline will feel awkward and slow. Reach for a layered or microkernel style instead.

## Key takeaways / mental model
Filters process; pipes transfer. Think of it like a factory assembly line. One machine puts the product in a box, and the conveyor belt carries it to the next machine that slaps a label on it. Neither machine knows how the other works, they just do their job.

## Self-check questions
1. What happens if a filter in the middle of a pipeline takes twice as long as the other filters?
2. How do you handle branching logic, like sending bad data to an error log, in a pipeline?
3. Why should filters remain completely ignorant of upstream or downstream filters?

## References
- Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 13
