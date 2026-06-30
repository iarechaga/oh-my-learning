---
id: fundamentals/15
subject: fundamentals
title: Service-Based Architecture
slug: service-based-architecture
status: drafted
mastery:
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 15
prerequisites: [fundamentals/09, fundamentals/12]
created: 2026-06-30
updated: 2026-06-30
---

# Service-Based Architecture

## TL;DR
Service-based architecture is a hybrid style that groups applications into a small number of coarse-grained, independently deployable services. It offers a pragmatic middle ground between monolithic complexity and microservices fragmentation by allowing services to share a single database.

## The idea
Many development teams attempt to solve monolithic complexity by jumping directly to microservices. They often find themselves overwhelmed by distributed transactions, complex network routing, and high infrastructure costs. This shift can create more problems than it solves.

Service-based architecture provides a practical alternative. Instead of breaking an application into hundreds of tiny microservices, you divide it into a dozen large, domain-aligned services. These services represent broad business areas rather than atomic capabilities.

Crucially, this style relaxes the strict rule of data isolation. Services can share a single database. This compromise avoids the nightmare of distributed data coordination while preserving independent deployability.

## How it works
This style operates with a small set of coarse-grained services, a shared database, and an entry gateway.

Coarse-grained services focus on large, logical domains. For example, a single Billing Service handles invoices, payment processing, and subscription renewals. These services run as independent, deployable units, such as Docker containers.

The shared database is the central storage layer. Unlike microservices, where sharing a database is forbidden, service-based architecture embraces it. This structure allows you to use standard SQL joins and database transactions across domains.

The API gateway acts as the router. It receives incoming traffic from clients and forwards requests to the appropriate service.

### An Online Bookstore Example
Let's look at an online bookstore designed with this style.

Instead of writing separate microservices for searching, reviews, and book details, we build a single, coarse-grained "Catalog Service".

1. **Customer Service**: Handles logins, profile updates, and addresses.
2. **Catalog Service**: Manages book searches, descriptions, reviews, and stock levels.
3. **Billing Service**: Manages order checkout, credit card processing, and invoice generation.

These three services deploy independently. They connect to a single relational database. When the Billing Service needs to verify the price of a book, it runs a standard SQL join on the catalog tables, avoiding slow and fragile network calls.

Below is an ASCII diagram of this bookstore layout:

```
[Client Requests]
       |
       v
 [API Gateway]
  /    |    \
 /     |     \
v      v      v
[Cust] [Cat] [Bill]  (Coarse-grained services)
\      |      /
 \     |     /
  v    v    v
[Shared SQL Database]
```

## Architectural characteristics analysis
Let's analyze how the service-based architecture style performs across key architectural characteristics:

- **Deployability**: Medium to High. You can deploy services independently, which is a major upgrade from a monolithic deployment.
- **Scalability**: Medium. Since services are coarse, you can scale them independently (e.g. scaling Catalog during browsing spikes), but you are still scaling relatively large chunks of code.
- **Elasticity**: Medium. Better than a monolith, but worse than microservices because service startup times are higher.
- **Reliability**: High. Shared databases prevent distributed transaction failures, and service boundaries provide good fault isolation (if Catalog crashes, Customer logins still work).
- **Performance**: High. Sharing a database avoids expensive network calls and data replication latency.
- **Simplicity**: Medium. It's much simpler than microservices, avoiding sagas and service mesh complexity.
- **Cost**: Medium. It requires fewer container instances and infrastructure nodes than microservices.
- **Testability**: Medium to High. Testing is easier because services are logically grouped and you don't need extensive distributed mocks.
- **Team fit**: High. It maps perfectly to typical business divisions (e.g. the Billing team owns the Billing service).

## Pros
- **Lower Operational Complexity**: It avoids the challenges of distributed transactions, sagas, and constant network hops.
- **Pragmatic Data Sharing**: The shared database allows standard SQL joins and ACID transactions.
- **Independent Lifecycles**: Services can be built, tested, and deployed independently of other domains.
- **Cost Efficiency**: It requires significantly fewer computing resources and containers than a microservices setup.

## Cons
- **Database Coupling**: Changes to shared database schemas can break multiple services if not managed carefully.
- **Coarser Scalability**: You cannot scale specific tiny capabilities independently without scaling the entire domain service.
- **Higher Blast Radius**: If a coarse service crashes, multiple related features go down together.
- **Governance Challenges**: Teams must coordinate database modifications to prevent schema conflicts.

## Alternatives
- **Modular Monolith**: Enforces logical module boundaries, but runs them all inside a single process and memory space.
- **Microservices Architecture**: Breaks applications into fine-grained services that never share databases or schemas.

## When to use it
Choose service-based architecture when migrating from a monolith to a distributed system where data separation is too difficult. It is a great fit for:
- Medium-sized applications that need independent deployment cycles but have simple transactional needs.
- Organizations with small development teams that cannot afford the operational overhead of microservices.
- Systems where business domains are clear but data relations are highly interconnected.

## When NOT to use it
Avoid this style for extremely large applications that require distinct database technologies for different modules. If different capabilities have wildly different scale profiles, or if database schema conflicts become a constant bottleneck, move to microservices.

## Key takeaways / mental model
Think of it as "macroservices". It gives you the operational freedom of independent deployments without the pain of distributed databases.

## Self-check questions
1. Why is a shared database both a benefit and a risk in service-based architecture?
2. How does service-based architecture simplify transaction management compared to microservices?
3. When would a team decide to split a service-based architecture into microservices?

## References
- Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 15
