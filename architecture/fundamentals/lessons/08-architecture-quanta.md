---
id: fundamentals/08
subject: fundamentals
title: Architecture Quanta
slug: architecture-quanta
status: drafted
mastery:
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 9
prerequisites: [fundamentals/07]
created: 2026-06-30
updated: 2026-06-30
---

# Architecture Quanta

## TL;DR
An architectural quantum is an independently deployable artifact with high functional cohesion, high static coupling, and high dynamic coupling. It represents the smallest unit of physical architecture that can operate autonomously while maintaining its own structural integrity. Understanding architecture quanta allows architects to determine the actual physical boundaries of scalability, transactionality, and deployment isolation in a system.

## The idea
How small can we split a software system before it breaks? 
In physics, a *quantum* is the minimum amount of any physical entity involved in an interaction. In software architecture, an **architecture quantum** is the smallest physical unit that can be deployed independently and operate self-sufficiently.

Many teams believe they have built a system of thirty independent microservices. However, if those services share a single database, or if they cannot complete a business request without making synchronous, blocking API calls to four other services, they are not actually independent. They are statically and dynamically bound together. In reality, they form a single, distributed architectural quantum.

Identifying and defining your system's quanta is crucial because architectural characteristics (like scalability, reliability, and security) are governed at the quantum boundary. You cannot scale a single class inside a quantum; you must scale the entire quantum. You cannot secure one module within a quantum with a completely different protocol without crossing boundaries. The quantum is the boundary of architectural governance.

## How it works
An architectural quantum is defined by three intersecting forces:
1. **Independent Deployability:** Can the artifact be built, tested, and shipped to production without requiring the simultaneous release of other artifacts?
2. **High Static Coupling:** Does the artifact share compile-time, build-time, or database-schema dependencies with other artifacts?
3. **High Dynamic Coupling:** Does the artifact rely on synchronous, blocking communication (like REST or gRPC) with other artifacts to complete a business transaction?

```
+--------------------------------------------------------------+
| Architectural Quantum                                        |
|                                                              |
|   +------------------------------------------------------+   |
|   | Independent Deployability (artifact boundary)        |   |
|   |                                                      |   |
|   |   +----------------------------------------------+   |   |
|   |   | Static Coupling (database, memory space)     |   |   |
|   |   |                                              |   |   |
|   |   |   +--------------------------------------+   |   |   |
|   |   |   | Dynamic Coupling (sync REST/gRPC)    |   |   |   |
|   |   |   +--------------------------------------+   |   |   |
|   |   +----------------------------------------------+   |   |
|   +------------------------------------------------------+   |
+--------------------------------------------------------------+
```

### Static Coupling vs Dynamic Coupling in Quanta
* **Static Coupling:** This includes shared databases, shared libraries, or co-located memory space. If two services share a single relational database schema, they are statically coupled. A change to a table structure in service A can break service B. Thus, they reside within the *same* architecture quantum, even if they are deployed as separate Docker containers.
* **Dynamic Coupling:** This refers to runtime communication. If service A calls service B synchronously to fulfill a request, and service B calls service C, any failure or latency spike in C directly impacts A. This synchronous chain binds them into a single dynamic quantum.

### The Formula for a Quantum
To qualify as a separate, distinct architecture quantum, a unit must possess:
* **Separate Database:** No shared database schemas.
* **Independent Deployment pipeline:** Changes can be promoted to production without coordination.
* **Asynchronous Communication (or isolation):** Any interaction with other quanta must be asynchronous (message queues, event streams, or eventual consistency), preventing runtime dependencies from cascading.

---

### Worked Example: The Booking & Payment Flow
Let's analyze two different physical implementations of a flight booking system.

#### Design A: The "Microservices" Illusion (Single Quantum)
In this design, we have three services:
1. `BookingService` (handles customer flight selection).
2. `SeatService` (handles seat assignments).
3. `PaymentService` (processes credit cards).

They are deployed in three separate Kubernetes pods. However, they share a single MySQL database schema (`flight_db`). Furthermore, when a user books a flight, the following flow occurs:

```
[User] -> (POST) -> [BookingService]
                         |
                   (sync gRPC)
                         v
                    [SeatService]
                         |
                   (sync REST)
                         v
                   [PaymentService]
```

* **Analysis:**
  * **Deployability:** If `BookingService` changes a database field, it might break the queries in `SeatService`. They are not truly independent.
  * **Dynamic Coupling:** If `PaymentService` experiences latency, both `SeatService` and `BookingService` threads will block, potentially exhausting the thread pool of the entire system.
  * **Result:** This system has **1 Architectural Quantum**, despite having 3 deployment units. It is a distributed monolith.

#### Design B: True Quantum Separation (Multiple Quanta)
We refactor the system:
1. `BookingService` now has its own private MongoDB instance.
2. `SeatService` has its own PostgreSQL database.
3. `PaymentService` has its own database.
4. The communication style is shifted:

```
[User] -> [BookingService] --(publishes "BookingPending" event)--> [Event Broker]
                                                                        |
                                                                  (async stream)
                                                                        v
                                                                  [SeatService]
                                                                        |
                                                                  (async stream)
                                                                        v
                                                                  [PaymentService]
```

* **Analysis:**
  * **Deployability:** Each service can modify its database schema without affecting the others.
  * **Dynamic Coupling:** If `PaymentService` is down, `BookingService` can still accept bookings and write them to its local database. The events will buffer in the broker until `PaymentService` recovers.
  * **Result:** This system has **3 Architectural Quanta**. Each quantum can scale, fail, and evolve completely independently.

## Pros
- **Accurate Domain Slicing:** Prevents architects from falling into the trap of "accidental microservices" where they split services physically but leave them tightly bound.
- **Granular Architectural Characteristics:** Allows different parts of the system to have completely different characteristics. The `Payment` quantum can prioritize high security and transactionality (ACID), while the `Telemetry` quantum can prioritize extreme scale and write performance.
- **Improved Fault Isolation:** True quantum separation guarantees that a failure in one area of the system cannot cascade and take down other business areas.

## Cons
- **Consistency Complexity:** Splitting quanta forces you to move from atomic, distributed transactions (two-phase commit) to eventual consistency, which requires sagas, compensating transactions, and complex error-handling code (see `hard-parts/11` and `hard-parts/14`).
- **Data Duplication:** To avoid static coupling, data must often be replicated across quanta. For example, `PaymentService` might need to store its own copy of a technician's profile to avoid synchronously querying `TechnicianProfiles` (see `hard-parts/12`).
- **Operational Overhead:** Managing multiple quanta means maintaining multiple databases, deployment pipelines, and messaging brokers.

## Alternatives
- **Single Quantum Monolith:** Keeping all components in a single deployment unit and a single database. This is highly efficient and offers strong consistency but restricts independent scaling and deployment.
- **Service-Oriented Architecture (SOA):** High reuse via shared database tables and centralized enterprise service buses (ESBs). This reduces data duplication but creates massive static coupling and a single, fragile quantum.

## When to use it
- **Modernizing Monoliths:** Use quanta analysis to define where to draw the first boundaries. If you cannot decouple the databases, do not split the services.
- **Designing High-Scale Distributed Systems:** When different business capabilities have vastly different scalability requirements (e.g., millions of catalog reads vs. hundreds of checkout writes).

## When NOT to use it
- **Simple, Low-Scale Applications:** If your system handles small traffic and has basic domain rules, a single quantum (layered monolith or simple modular monolith) is highly superior.
- **Teams with Low Operational Maturity:** If a team cannot manage asynchronous messaging, eventual consistency, or separate database deployments, they should avoid creating multiple quanta.

## Key takeaways / mental model
An architectural quantum is the true boundary of independence. If you change a service and have to coordinate its release with another service, or if a database change in one service breaks another, you do not have independent services—you have a single quantum wrapped in network overhead. To split your architecture safely, focus on decoupling static dependencies (databases) and dynamic dependencies (synchronous calls) first.

## Self-check questions
1. Why does sharing a database schema merge two services into a single architectural quantum?
2. What is the difference between static coupling and dynamic coupling in the context of quanta?
3. How does shifting from synchronous HTTP calls to asynchronous message streams affect the number of quanta in a system?

## References
- *Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025)*, Chapter 9: Architecture Quanta
- Cross-subject prerequisites: [fundamentals/07]
- Cross-subject connections: [hard-parts/02], [hard-parts/03], [hard-parts/11], [hard-parts/14]
