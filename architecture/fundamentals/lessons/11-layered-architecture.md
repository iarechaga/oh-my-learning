---
id: fundamentals/11
subject: fundamentals
title: Layered Architecture
slug: layered-architecture
status: drafted
mastery:
seniority: mid
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 11
prerequisites: [fundamentals/07]
created: 2026-06-30
updated: 2026-06-30
---

# Layered Architecture

## TL;DR
Layered architecture (or n-tier architecture) is the classic de facto standard for monolithic applications, organizing components into horizontal technical layers. Each layer has a specific technical responsibility and isolates its internals from other layers. Understanding the trade-offs of layered architecture—such as closed versus open layers, the dependency inversion principle, and the "architecture sinkhole" anti-pattern—is essential for managing coupling in a single deployment unit.

## The idea
The layered architecture style is organized technically rather than domain-centrically. It is based on the idea that components performing similar technical tasks should be grouped together into distinct horizontal tiers. 

In a standard four-layer system:
* The **Presentation Layer** handles user interface and API request routing.
* The **Business Layer** (or Service Layer) implements business logic.
* The **Persistence Layer** (or Data Access Layer) manages data mapping.
* The **Database Layer** stores the physical data.

This technical organization makes systems highly intuitive for developers: everyone knows exactly where to write code based on its technical category. 

However, this horizontal split creates a major trade-off. Business capabilities (like "billing") are sliced across all layers, meaning a single feature change often requires modifying classes in every single layer. This creates high vertical coupling across the system.

## How it works
The fundamental governing rule of layered architecture is the **direction of dependencies**: dependencies must always flow *downward*, never upward. A lower layer must never know about or import a component from a layer above it.

```
       Layered Architecture Topology
+------------------------------------------+
|            Presentation Layer            |
+------------------------------------------+
                     | (flows down)
                     v
+------------------------------------------+
|  Business Layer (Closed)                 |
+------------------------------------------+
                     | 
                     v
+------------------------------------------+
|  Persistence Layer (Closed)              |
+------------------------------------------+
                     | 
                     v
+------------------------------------------+
|  Database Layer                          |
+------------------------------------------+
```

### Closed vs. Open Layers
Layers in this style can be configured as either *closed* or *open*:
* **Closed Layer (Default):** A closed layer prevents requests from bypassing it. A request coming from the Presentation Layer *must* pass through the Business Layer before touching the Persistence Layer. It cannot skip directly to the database. Closed layers enforce **architectural isolation**, ensuring that a change in one layer's internals does not cascade and affect unrelated layers.
* **Open Layer:** An open layer allows requests to bypass it. If the Business Layer is open, the Presentation Layer can call the Persistence Layer directly. This can be useful for performance or utility purposes, but it destroys isolation and increases coupling.

### The Architecture Sinkhole Anti-Pattern
An "architecture sinkhole" occurs when a request passes through multiple layers of the system with little to no logic being applied at each layer.

For example, a user requests their profile details. The request flows as follows:
1. `ProfileController` (Presentation) receives the call and immediately forwards it to...
2. `ProfileService` (Business), which applies no business rules and immediately calls...
3. `ProfileRepository` (Persistence), which executes `SELECT * FROM profiles...` and returns the data.

If 80% or more of your requests are sinkholes, your application is a CRUD app. In this scenario, layered architecture adds massive boilerplate, serialization cost, and cognitive overhead for no real architectural benefit.

---

### Worked Example: Enforcing Layers with Dependency Inversion
Let's look at how to structure code inside a Layered Monolith to prevent high coupling between the Business Layer and the Database Layer.

#### The Wrong Way: Direct Coupling
If the Business Layer imports the physical persistence classes directly, it becomes coupled to the database technology.

```
+------------------+           +----------------------+
|  Business Layer  | --------> |  Persistence Layer   |
|  (BillingService)|           |  (PostgresRepository)|
+------------------+           +----------------------+
```

If we want to switch the database from PostgreSQL to MongoDB, we must rewrite the `BillingService` code because it is coupled to Postgres-specific client libraries and paradigms.

#### The Right Way: Dependency Inversion
We use the **Dependency Inversion Principle (DIP)**. We define a Java/TypeScript interface inside the Business Layer and force the Persistence Layer to implement it.

```
  Business Boundary (Core)
+----------------------------------------------+
|   [BillingService] --> (uses) --> [IPayRepo] |  <-- (Interface defined here)
+----------------------------------------------+
                                       ^
                                       | (implements/flows up statically)
  Persistence Boundary (Infrastructure) |
+----------------------------------------------+
|   [PostgresPayRepository] -------------------+
+----------------------------------------------+
```

* **How it works at runtime:**
  1. The request flows down physically: Presentation -> Business -> Database.
  2. The dependency flows down logically, but the static compile-time dependency has been inverted: the Infrastructure layer now depends on the Core Business layer.
  3. We can replace `PostgresPayRepository` with `MongoPayRepository` without modifying a single line of business logic in `BillingService`.

## Pros
- **Easy Onboarding:** The most familiar pattern in software. New developers can instantly understand where a piece of code belongs.
- **Isolates Technological Changes:** If the Persistence Layer is closed, switching from Oracle to PostgreSQL or upgrading an ORM version only affects the Persistence Layer. The Business and Presentation layers remain unchanged.
- **Easy to Test:** Layers can be isolated and tested independently using mocks or stubs. For example, you can test business logic by mocking the Persistence interfaces.

## Cons
- **Vertical Coupling (The "Change Cascade"):** Because business concepts are sliced horizontally, adding a single database column often requires changing files in the Persistence, Business, and Presentation classes.
- **The Monolithic Bottleneck:** Hard to scale or deploy a single layer independently. If the presentation layer needs a framework upgrade, the entire monolith must be rebuilt and redeployed.
- **Tendency toward "Big Ball of Mud":** Over time, developers add "utility" open layers or bypass layers for convenience, leading to spaghetti dependencies and architectural decay.

## Alternatives
- **Hexagonal Architecture (Ports and Adapters):** Organizing code into inside-out concentric rings (Domain Core, Application Services, Adapters) rather than top-down horizontal layers. This places domain logic at the absolute center, keeping it pure and free from framework code.
- **Domain-Driven Design (Feature Folders):** Grouping classes by business capability (e.g., `billing/`, `inventory/`) rather than by technical type (e.g., `controllers/`, `services/`, `repositories/`).

## When to use it
- **Simple, Structured Monoliths:** Small-to-medium applications with predictable business logic and clear, technical divisions.
- **Greenfield Prototypes:** When you need to establish a structured codebase quickly and your team is familiar with MVC/n-tier architectures.
- **Migration Stepping Stone:** As a first step in organizing a chaotic "Big Ball of Mud" before migrating to modular monoliths or microservices.

## When NOT to use it
- **Complex, Domain-Heavy Applications:** Systems with rich, volatile domain rules where feature-based organization (Domain-Driven Design) is superior.
- **Highly Dynamic, Scalable Systems:** If different features have vastly different scaling, deployment, or technology needs (use distributed styles instead).
- **Pure CRUD Systems:** Where 90% of requests are simple pass-through "sinkholes." A simpler two-tier controller-to-database structure is far more efficient.

## Key takeaways / mental model
Layered architecture organizes your system by technical function (controllers, services, repositories). It relies on closed layers to establish clean boundaries and isolate technical concerns. However, it suffers from the "change cascade" because business features are sliced vertically across every technical layer. If you use this style, enforce dependency direction strictly, keep layers closed to maintain isolation, and use Dependency Inversion to keep your business core free of database and infrastructure coupling.

## Self-check questions
1. What is the architectural purpose of a "closed" layer, and what is the trade-off of making a layer "open"?
2. How does the Dependency Inversion Principle prevent the Business Layer from being coupled to specific database technologies?
3. How do you identify the "architecture sinkhole" anti-pattern, and what does it tell you about your choice of architecture style?

## References
- *Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025)*, Chapter 11: Layered Architecture Style
- Cross-subject prerequisites: [fundamentals/07]
- Cross-subject connections: [system-design/02]
