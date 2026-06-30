---
id: fundamentals/12
subject: fundamentals
title: Modular Monolith
slug: modular-monolith
status: drafted
mastery:
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 12
prerequisites: [fundamentals/11]
created: 2026-06-30
updated: 2026-06-30
---

# Modular Monolith

## TL;DR
A modular monolith is an architectural style that structures a single physical deployment unit along logical domain boundaries. Unlike a traditional layered monolith, it enforces strict encapsulation and dependency rules between domain modules, ensuring they share nothing except explicit API contracts. This style provides the organizational and boundary benefits of microservices without the high operational complexity, performance cost, and network fallacies of a distributed system.

## The idea
For years, the software industry promoted a false dichotomy: you either build a messy, tightly coupled monolith, or you build a highly complex network of distributed microservices.

The **modular monolith** breaks this false choice. It proves that tight coupling is not an inherent property of monoliths, but rather a consequence of poor design. 

In a traditional layered monolith, classes are grouped by technical type. This leads to database tables and service classes being accessed arbitrarily by any part of the system, turning the codebase into spaghetti code.

In a modular monolith, we organize the codebase by **domain modules** (e.g., `Billing`, `Inventory`, `Shipping`). Each module is a self-contained logical unit. It has its own business logic, entry-point APIs, and its own logical database tables. One module *cannot* directly access the classes, memory, or database tables of another module without going through its public interface. Yet, all modules are built and run together inside the same physical process.

A modular monolith is the ultimate "default" architecture for complex systems. It offers the clean boundary discipline of microservices with the operational simplicity, performance, and transactional safety of a monolith.

## How it works
The modular monolith is governed by strict structural rules regarding module boundaries and data isolation.

```
                  Modular Monolith Topology
+-------------------------------------------------------------+
|                     Single Deployment Unit                  |
|                                                             |
|   +---------------+     In-Memory API     +---------------+ |
|   | Billing Module| <-------------------> | Order Module  | |
|   |  - Public API |                       |  - Public API | |
|   |  - Internals  |                       |  - Internals  | |
|   +---------------+                       +---------------+ |
+-------------------------------------------------------------+
            |                                       |
  (Logical Db Separation)                 (Logical Db Separation)
            v                                       v
+-----------------------+               +-----------------------+
|  [billing_tables]     |               |  [order_tables]       |
+-----------------------+               +-----------------------+
|                 Shared Physical Database                      |
+---------------------------------------------------------------+
```

### 1. Module Encapsulation
Each module must have a clear distinction between its public API and its private internal implementation details.
* **Java/C# Example:** Use language access modifiers (like Java's package-private visibility) or build-system tools (like ArchUnit or project references) to ensure that classes outside a module cannot import or instantiate classes marked as private internals.
* **TypeScript Example:** Use nested directories with strict `index.ts` barrel files, and enforce import boundaries using ESLint or lerna rules.

### 2. Logical Data Isolation (Shared-Nothing at Database Level)
A modular monolith must prevent modules from querying each other's database tables directly. There are two primary patterns:
* **Separate Schemas (Recommended):** All tables sit in the same physical database engine, but they are split into different schemas (e.g., `billing_schema.transactions` vs. `order_schema.orders`). A module's database credentials only allow it to read and write to its own schema.
* **Table Prefixing:** A simpler, less restrictive approach where tables are grouped by prefix (e.g., `bill_transactions`, `ord_orders`), and developers are forbidden from writing cross-prefix joins in SQL.

If Module A needs data from Module B, it must call Module B's public API in-memory. It cannot execute a database JOIN across module boundaries.

### 3. Communication Patterns
Because modules run in the same memory space, they can communicate via fast, in-memory mechanisms:
* **Direct Synchronous Calls:** Calling a method on another module's public service interface.
* **In-Memory Event Bus:** Publishing a lightweight event class (e.g., `OrderPlacedEvent`) to an in-memory event bus (using tools like Spring ApplicationEvents or Node.js EventEmitter), allowing consumer modules to react asynchronously without compile-time coupling.

---

### Worked Example: Decoupling Order and Inventory Modules
Let's see how to design a modular monolith where the `OrderModule` must verify stock in the `InventoryModule` during checkout.

#### The Monolithic "Spaghetti" Way:
In a traditional monolith, the `OrderController` or `OrderService` might write a SQL query that joins the `orders` table directly with the `inventory` table to check stock.

```sql
-- Direct join across domain boundaries - HIGH COUPLING
SELECT * FROM orders o 
JOIN inventory i ON o.product_id = i.product_id 
WHERE o.id = 123;
```

This join couples the database structure of the Inventory domain directly to the Order domain. If the Inventory team refactors their table layout, the Order code breaks.

#### The Modular Monolith Way:
1. `InventoryModule` exposes a clean public interface: `InventoryApi.checkStock(productId, quantity)`.
2. `OrderModule` calls this method in-memory.
3. If database schemas are separated, `OrderModule` only queries tables in the `order` schema. `InventoryModule` only queries tables in the `inventory` schema.

```
[OrderModule] --(in-memory method call)--> [InventoryApi] --(query)--> [inventory_tables]
```

At runtime, there is no network call. The performance is sub-microsecond. However, the logical boundary is absolute.

---

### The Migration Path to Microservices
If a modular monolith is designed correctly, migrating a module to a separate physical microservice is trivial.

Because the `InventoryModule` shares no code dependencies and no database schemas with the rest of the monolith, we can easily pull the entire directory into a separate repository and wrap its public interface in a REST or gRPC controller.

```
       Step 1: Modular Monolith             Step 2: Microservice Extraction
+-----------------------------------+      +-----------------+      +-----------------+
|          Deployment Unit          |      |  Deploy Unit A  |      |  Deploy Unit B  |
|  [Order] --(In-Memory)--> [Inven] | ---> |     [Order]     | ---> |     [Inven]     |
+-----------------------------------+      +-----------------+      +-----------------+
        |                    |                     |                        |
        v                    v                     v                        v
  [order_schema]      [inven_schema]         [order_schema]           [inven_schema]
```

The rest of the monolith continues to call `InventoryApi`, but the implementation of that class is swapped from a direct method call to a network client (e.g., using WebClient or gRPC).

## Pros
- **High Performance:** No network serialization, latency, or transport costs (unlike microservices).
- **Transactional Safety:** You can still use local ACID transactions across modules if absolutely necessary, avoiding the complexity of eventual consistency and distributed Sagas.
- **Microservices Refactoring Runway:** Provides a safe, low-risk playground to discover and stabilize domain boundaries before spending money on distributed infrastructure.
- **Lower Operational Complexity:** One deployment pipeline, one server registry, and one database to monitor.

## Cons
- **Single Point of Failure (Low Fault Isolation):** A memory leak or CPU-intensive thread in the `Billing` module can still crash the entire application process, taking down `Order` and `Inventory`.
- **Coarse-Grained Scaling:** You cannot scale a single module independently. If `Billing` has heavy load, you must scale the entire monolith.
- **Stack Monoculture:** All modules must be written in the same language and run on the same runtime environment (e.g., all JVM, all .NET, or all Node.js).

## Alternatives
- **Traditional Layered Monolith:** Simpler to write initially because it lacks modular boundaries, but degrades rapidly into spaghetti code under team growth.
- **Distributed Microservices:** Necessary when you require completely independent scaling, polyglot technology stacks, or ultimate fault isolation (independent crash boundaries).

## When to use it
- **The Golden Default:** For almost all greenfield enterprise applications where domain complexity is high but traffic does not yet require massive physical scale.
- **Refactoring Chaotic Monoliths:** A mandatory intermediate stage when breaking up a legacy application. Never skip modularization and go straight to microservices.
- **Small-to-Medium Engineering Teams:** Teams of 10 to 50 developers who want domain separation without microservices operational overhead.

## When NOT to use it
- **Polyglot Stacks:** If certain components must be written in Python (for ML) and others in Go (for low-latency streaming), a single monolith runtime is impossible.
- **Ultra-High Availability / High Blast Radius Risks:** If a failure in a minor, experimental component cannot under any circumstances be allowed to impact the core billing engine.

## Key takeaways / mental model
A modular monolith is a microservices architecture written in a single codebase and deployed in a single process. It gives you the best of both worlds: strict, domain-driven boundaries and logical data isolation, coupled with the performance, transactionality, and operational simplicity of a monolith. Keep your database schemas split, enforce encapsulation at package boundaries, and only distribute when physical boundaries (scaling, fault isolation) force your hand.

## Self-check questions
1. How does a modular monolith differ from a traditional layered monolith?
2. What are the two main techniques for achieving data isolation between modules in a single physical database?
3. Why does a modular monolith serve as a perfect stepping stone to microservices?

## References
- *Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025)*, Chapter 12: Monolithic Architecture Styles
- Cross-subject prerequisites: [fundamentals/11]
- Cross-subject connections: [hard-parts/04], [hard-parts/05], [system-design/02]
