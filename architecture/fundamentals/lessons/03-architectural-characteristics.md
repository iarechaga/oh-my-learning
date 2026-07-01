---
id: fundamentals/03
subject: fundamentals
title: Architectural Characteristics
slug: architectural-characteristics
status: drafted
mastery:
seniority: senior
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 4
prerequisites: [fundamentals/01, ddia/01, system-design/02]
created: 2026-06-30
updated: 2026-06-30
---

# Architectural Characteristics

## TL;DR
Architectural characteristics, also called quality attributes or non-functional requirements, define how a system operates under specific conditions. They are the core design drivers that shape a system's structure and performance. Choosing which characteristics to support is an exercise in managing trade-offs.

## The idea
Software must do more than just work. Functional requirements describe what a system does, like "allow a user to submit a support ticket." Architectural characteristics describe how well the system performs those actions, like "ensure ticket submission is available 99.9% of the time and can handle sudden spikes in traffic."

A system can have perfect functional code, but it fails if it's too slow, constantly crashes, or cannot be updated without breaking other parts. An architect's primary job is to identify and protect these systemic qualities.

## How it works
Architects categorize quality attributes to analyze their impact systematically. Richards & Ford group these characteristics into three main categories: operational, structural, and cross-cutting.

### Operational Characteristics
These qualities describe how the system runs in production:
- **Scalability**: The ability to handle a sustained increase in load by adding resources.
- **Elasticity**: The ability to handle sudden, volatile spikes in traffic by dynamically scaling resources up and down in real-time.
- **Availability**: The percentage of time the system is operational and accessible to users.
- **Reliability**: The ability of the system to perform its intended functions without failure under specified conditions.

The distinction between scalability and elasticity is a frequent source of confusion:

```
Scalability (Planned & Sustained)            Elasticity (Dynamic & Volatile)
Resource count                               Resource count
      ^                                            ^
      |      /------                               |      /\
      |     /                                      |     /  \  /\
      |    /                                       |    /    \/  \
      +----------> Time                            +--------------> Time
```

Scalability handles a steady growth of users over months. Elasticity handles a sudden flood of users who log on during a flash sale and log off an hour later.

### Structural Characteristics
These qualities describe the internal code and deployment structure:
- **Maintainability**: How easily developers can modify the codebase to fix bugs or add features.
- **Testability**: The ease of writing automated tests to verify system behavior.
- **Deployability**: How easily and safely a new release can be pushed to production.
- **Modularity**: The degree to which a system's components are decoupled and independent.

### Cross-Cutting Characteristics
These qualities span both operational and structural areas:
- **Security**: Protecting the system and its data from unauthorized access.
- **Compliance**: Adhering to legal and industry regulations, like GDPR or PCI-DSS.
- **Feasibility**: The ability to build and operate the system within budget and time constraints.

### Managing Conflicts
You cannot maximize all characteristics. They exist in direct conflict:

```
+------------------+------------------+------------------------------------+
| Characteristic A | Characteristic B | The Nature of the Conflict         |
+------------------+------------------+------------------------------------+
| Security         | Performance      | Encryption & checks add latency.   |
| Scalability      | Consistency      | Network hops lag data sync.        |
| Agility (Speed)  | Reliability      | Quick deploys increase bug risks.  |
+------------------+------------------+------------------------------------+
```

An architect must identify the top 3 to 5 core characteristics that are critical to the system's success, and accept compromises on the rest.

### Worked Example: Splitting Characteristics at Sysops Squad
Suppose Sysops Squad has two primary needs:
1. Customers must be able to submit support tickets during major outages.
2. Managers must run complex analytical reports on ticket history to spot trends.

Attempting to build a single system that handles both requirements perfectly is incredibly difficult. Forcing the transaction database to handle massive analytical reporting queries degrades the performance of the write operations, which hurts availability for customers submitting tickets.

To solve this, the architect prioritizes different characteristics for each area:
- The Ticket Submission module is designed with event-driven queues to prioritize **Availability** and **Elasticity**.
- The Reporting module is designed with a read-optimized data warehouse to prioritize **Performance** and **Feasibility**.

This separation of concerns allows each part of the system to succeed without fighting over conflicting quality attributes.

## Pros
- Provides a clear, standardized taxonomy for talking about system qualities with stakeholders.
- Guides major architectural decisions based on hard requirements rather than technical trends.
- Prevents over-engineering by focusing only on the characteristics that truly matter.

## Cons
- Demands strong negotiation skills, as stakeholders naturally want every quality to be high priority.
- Increases system complexity when trying to support too many characteristics at once.
- Hard to measure or verify some qualities without proper instrumentation and observability tools.

## Alternatives
- **Implicit quality attributes (organic architecture)**: Building the system and hoping it turns out fast and reliable enough. This is faster initially but usually leads to major architectural re-writes when the system hits real-world load.
- **Monolithic prioritization**: Setting a blanket policy that all systems must meet the same high standard of security, scalability, and availability. This is wasteful and slows down teams working on low-risk internal tools.

## When to use it
- When planning a new software system or refactoring a legacy application.
- When defining service boundaries and communication patterns in a distributed system.

## When NOT to use it
- Small, single-user scripts or prototypes where functional correctness is the only goal.
- Very simple CRUD applications with no significant scaling, security, or availability concerns.

## Key takeaways / mental model
Do not try to support every architectural characteristic. A system that tries to do everything ends up doing nothing well. Identify the 3 to 5 characteristics that are critical to business success, and deliberately compromise on the rest.

## Self-check questions
1. What is the fundamental difference between scalability and elasticity?
2. Why do performance and security often exist in direct conflict?
3. How should an architect handle a stakeholder who demands that the system be highly scalable, highly secure, highly available, and cheap to build?

## References
- Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 4
- [ddia/01](../../ddia/lessons/01-reliability-scalability-maintainability.md)
- [system-design/02](../../system-design/lessons/02-distributed-system-attributes.md)
