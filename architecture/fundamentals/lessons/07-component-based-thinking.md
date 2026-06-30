---
id: fundamentals/07
subject: fundamentals
title: Component-Based Thinking
slug: component-based-thinking
status: drafted
mastery:
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 8
prerequisites: [fundamentals/06]
created: 2026-06-30
updated: 2026-06-30
---

# Component-Based Thinking

## TL;DR
Components are the fundamental logical building blocks of software, wrapping a set of co-locatable code assets behind a clean interface. Component-based thinking requires architects to identify, size, and partition these logical blocks inside a system's domain before making physical deployment or service boundary decisions. Sizing components appropriately avoids both bloated mega-components and fine-grained, over-engineered micro-components.

## The idea
Many developers transition to architecture and immediately jump to physical architecture: "Let's build three microservices, a Kafka broker, and a React frontend." This physical-first approach bypasses the critical logical design phase. Slicing a system into services without first defining its logical boundaries leads to distributed monoliths, misplaced data ownership, and high dynamic coupling.

Component-based thinking provides a bridge between business domains and physical deployment units. A **component** is a modular package of code that implements a specific, cohesive business capability. It exposes a well-defined interface and hides its internal implementation details. 

By treating components as the primary unit of design, an architect can reason about dependencies, cohesion, and coupling at a high level of abstraction. Only after components are defined, stabilized, and sized should the architect decide how to group them into physical deployment units (such as libraries, modular monolith boundaries, or microservices).

## How it works
Component-based thinking is an iterative loop of identifying, sizing, naming, and partitioning.

```
+-------------------------------------------------------------+
|                                                             |
|   [1. Identify] ---> [2. Name] ---> [3. Size] ---> [4. Partition]
|         ^                                                 |
|         +------------------ Re-evaluate ------------------+
|                                                             |
+-------------------------------------------------------------+
```

### 1. Identifying Components (The Component Discovery Phase)
Architects use different inputs to find initial component candidates:
* **Domain Analysis:** Mapping domain nouns and verbs. In an e-commerce system, nouns like `Order`, `Inventory`, and `Customer` suggest initial component boundaries.
* **Workflow / Process Analysis:** Grouping steps in a business process (e.g., `Checkout`, `PaymentProcessing`).
* **Source Code Archeology:** If refactoring a monolith, analyzing package structures or class dependency graphs to find implicit clusters.

### 2. Sizing Components (Finding the "Goldilocks" Zone)
Components that are too large or too small create distinct architectural problems.

| Sizing Extremes | Symptoms | Consequences |
| --- | --- | --- |
| **Too Large (Mega-Component)** | High internal class count, mixed responsibilities, complex dependency graphs, slow build times. | Low cohesion, high risk of regression during changes, hard to test or reuse. |
| **Too Small (Nano-Component)** | Trivial logic wrapped in excessive boilerplate, huge numbers of components with high dynamic coupling. | High cognitive overhead, complex orchestration, performance degradation due to boundary crossings. |

**Sizing Indicators:**
* **Class Count / Line Count:** A rough but useful indicator. If a single component contains 100+ classes, it is likely a sub-monolith and should be split.
* **Cohesion Metrics:** Check if classes within the component share a common database schema or change frequency. High cohesion indicates a well-sized component.

### 3. Naming Components
Naming is a primary design tool, not just an aesthetic choice.
* **Rule:** A component's name must represent its single, primary responsibility.
* **Smell:** If you struggle to name a component without using "And" or "Or" (e.g., `BillingAndNotificationService`), the component is too large and should be partitioned.
* **Smell:** Generic names like `Common`, `Utility`, or `Manager` hide poor design. They act as magnets for unrelated code, destroying modularity.

### 4. Partitioning Components
Partitioning refers to dividing components based on technical or domain dimensions:
* **Technical Partitioning (Layered):** Separating components by technical role (e.g., presentation, business logic, persistence). This makes technical framework upgrades easier but increases coordination cost for business changes.
* **Domain Partitioning (Modular):** Partitioning components directly along business capability lines (e.g., Billing, Inventory). This aligns change boundaries with team boundaries, facilitating faster delivery of business features.

---

### Worked Example: The Sysops Squad Ticketing System
Let's design the component layout for an automated ticketing system where users submit problems and technicians get assigned to fix them.

#### Step 1: Initial Component Discovery
We start with domain-centric components:
* `TicketSubmission`
* `TechnicianAssignment`
* `Billing`
* `Notification`

#### Step 2: Sizing and Naming Analysis
We evaluate the `TechnicianAssignment` component. Its class list includes:
* `ManualAssignmentRouter`
* `AutoAssignmentEngine`
* `SkillsMatcher`
* `TechnicianProfileManager`
* `LocationTracker`
* `TravelEstimator`
* `NotificationDispatcher`

We notice that `NotificationDispatcher` is coupled to sending SMS/emails. This is a separate concern from matching skills and routing.
We also notice that `LocationTracker` and `TravelEstimator` handle geospatial data, which changes at a completely different frequency than skills mapping.

#### Step 3: Partitioning
We partition `TechnicianAssignment` into smaller, highly cohesive components:
1. `AssignmentEngine` (handles pure matchmaking algorithms).
2. `TechnicianProfiles` (manages skill registers and availability).
3. `GeoTracking` (manages real-time location data and travel estimates).

We extract the notification dispatching logic and push it to the existing `Notification` component.

Our new logical component diagram exhibits lower coupling and higher cohesion:

```
[TicketSubmission] --(create)--> [AssignmentEngine] --(lookup)--> [TechnicianProfiles]
                                        |
                                        +----(distance)---------> [GeoTracking]
                                        |
                                        +----(alert)------------> [Notification]
```

## Pros
- **Enables Incremental Decisions:** Postpones expensive physical architecture decisions (like microservices) until logical boundaries are understood and stable.
- **Isolates Change:** High internal cohesion and low external coupling mean changes to a component's implementation do not leak into other parts of the system.
- **Improves Testability:** Clear interfaces allow components to be mocked easily, making integration and unit testing straightforward.
- **Simplifies Team Alignment:** Clean component boundaries map naturally to team ownership (Conway's Law), reducing delivery friction.

## Cons
- **Cognitive Overhead:** Requires disciplined design upfront before writing functional code.
- **Performance Trade-offs:** Crossing component boundaries (even via local method calls) can add minor overhead if interfaces are excessively chatty or require deep serialization.
- **Interface Maintenance:** If component boundaries are poorly chosen, interfaces will change frequently, forcing cascading updates across consumer components.

## Alternatives
- **No Logical Layering (Big Ball of Mud):** Writing classes directly with global import/export freedoms. While fast initially, it leads to rapid structural decay and high technical debt.
- **Technical-First Partitioning (Strict Layered-Only):** Focusing purely on database-tier, controller-tier, and service-tier components. This separates tech concerns but makes business domain changes touch every layer of the system.

## When to use it
- **Greenfield Projects:** To map out the domain cleanly before committing to a physical deployment structure.
- **Monolith Decompositions:** When breaking up a "big ball of mud," use component discovery to find logical seams before pulling code into separate repositories or services.
- **Complex Domain Applications:** Any system with intricate business rules where domain logic is likely to evolve over time.

## When NOT to use it
- **Simple CRUD Applications:** In simple, low-complexity systems, component-based overhead may exceed the benefits. A basic controller-to-database structure is often sufficient.
- **Prototype / Throwaway Code:** When speed-to-market is the only priority and the code will be discarded, detailed component planning is a waste of time.

## Key takeaways / mental model
Never draw a physical service boundary before you can draw a logical component boundary. Components are the bricks; service boundaries are the rooms. If you do not know how to size and shape your bricks, your rooms will collapse. Keep your components cohesive (one name, one job) and decoupled, and let physical deployment requirements (scalability, availability, deployability) dictate where the physical walls are eventually built.

## Self-check questions
1. What is the difference between a logical component and a physical service?
2. How does the "And/Or" naming rule help identify components that are too large?
3. If a component has high dynamic coupling with three other components, what architectural smell does this suggest, and how would you resolve it?

## References
- *Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025)*, Chapter 8: Component-Based Thinking
- Cross-subject prerequisites: [fundamentals/06]
- Cross-subject connections: [hard-parts/05], [hard-parts/06], [system-design/02]
