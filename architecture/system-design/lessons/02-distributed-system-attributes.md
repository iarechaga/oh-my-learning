---
id: system-design/02
subject: system-design
title: Distributed-System Attributes and Scaling
slug: distributed-system-attributes
status: drafted
mastery:
source: "System Design Guide for Software Professionals (Sinha & Chopra, Packt 2024), Chapter 2"
prerequisites: [ddia/01]
created: 2026-06-30
updated: 2026-06-30
---

# Distributed-System Attributes and Scaling

## TL;DR
Distributed systems must balance availability, reliability, durability, latency, throughput, fault tolerance, and maintainability. This lesson explores these core attributes, discusses the differences between vertical and horizontal scaling, and explains why statelessness is essential for scaling horizontally. You will learn to calculate component availability in series versus parallel architectures and compute downtime metrics.

## The idea
A single-machine system is easy to reason about because it succeeds or fails as a whole. In a distributed system, machines fail independently, networks partition, and messages get lost. Designing distributed architectures is about accepting these failures and organizing resources to meet business guarantees. We can't build a system that is perfectly reliable and fast in all scenarios. Instead, we make trade-offs between availability, consistency, speed, and cost.

These attributes form the foundation of how we build systems. They directly connect to the core concerns of reliability, scalability, and maintainability, DDIA concept 01. Reliability means making the system work correctly even in the presence of hardware or software faults. Scalability is our capacity to handle increased load without degrading performance. Maintainability ensures that the engineers who inherit the system can operate and evolve it over time.

## How it works
This section covers the quantitative metrics and design choices that define distributed system behavior.

### Availability, Reliability, and Durability
These three terms are often used interchangeably, but they represent distinct concepts:

- **Availability:** This is the fraction of time that a system is operational and able to process requests. It's typically measured in "nines" of availability. A highly available system is accessible when the user needs it. Availability failures often stem from network routing loops, DNS misconfigurations, or load balancer failures.
- **Reliability:** This measures the probability that a system will perform its required function correctly under specified conditions for a defined period. A system can be available but unreliable if it stays online but constantly returns HTTP 500 errors. Common reliability issues include transient network hiccups, memory leaks, and unhandled exceptions.
- **Durability:** This is the guarantee that data, once committed to the system, remains intact and won't be lost or corrupted. Durability is a property of storage engines, ensuring data survives disk failures or power outages. Durability failures occur due to disk bit rot, physical head crashes, or RAID controller bugs.

### SLA, SLO, and SLI
Measuring system performance requires clear terminology. To illustrate this, let's look at an e-commerce checkout service. We can define our indicators, objectives, and agreements as follows:

- **Service Level Indicator (SLI):** A quantitative measure of service performance. For our checkout service, this might be the percentage of successful checkout requests (HTTP 200) completed in under 500 ms.
- **Service Level Objective (LO):** A target value or range for a service level that is measured by an SLI. Our checkout target might state that the SLI must remain at or above 99.9% over any rolling 30-day window.
- **Service Level Agreement (SLA):** A formal business contract between a service provider and its customers. It defines the SLOs and outlines the financial or legal penalties if those objectives are missed. For instance, the company might promise a 10% service fee refund if checkout availability falls below the SLO.

### SLA and Downtime Reference Table
The table below maps availability percentages to their respective allowable downtime budgets over different time horizons:

| Availability | Downtime per Year | Downtime per Month | Downtime per Week |
| --- | --- | --- | --- |
| 90% ("one nine") | 36.5 days | 2.5 days | 16.8 hours |
| 99% ("two nines") | 3.65 days | 7.3 hours | 1.68 hours |
| 99.9% ("three nines") | 8.76 hours | 43.8 minutes | 10.1 minutes |
| 99.99% ("four nines") | 52.56 minutes | 4.38 minutes | 1.01 minutes |
| 99.999% ("five nines") | 5.26 minutes | 26.3 seconds | 6.05 seconds |

### MTBF and MTTR
The availability of a component can be mathematically defined using two metrics:
- **Mean Time Between Failures (MTBF):** The average time a component operates before failing.
- **Mean Time To Repair (MTTR):** The average time required to repair a failed component and bring it back online.

We calculate the availability percentage of a component using this formula:
```
Availability = MTBF / (MTBF + MTTR)
```
To increase availability, we must either increase MTBF (make components more reliable) or decrease MTTR (recover from failures faster).

To meet a 99.9% availability target (no more than 8.76 hours of downtime per year), we must carefully balance MTBF and MTTR. For example, if our system fails on average once a month (MTBF is 730 hours):
```
0.999 = 730 / (730 + MTTR)
729.27 + 0.999 * MTTR = 730
0.999 * MTTR = 0.73
MTTR = 0.73 / 0.999 = 0.73 hours (approx. 44 minutes)
```
This calculation means that if our system crashes once a month, our team has only 44 minutes on average to detect, diagnose, and fully recover the service. If our MTTR is 2 hours, we must increase our MTBF to at least 2,000 hours (about 3 months of continuous operation) to maintain that same three-nines SLA.

### Latency vs Throughput
These two attributes define system performance:
- **Latency:** The time required to process a single request, from the user's perspective. It's measured in milliseconds.
- **Throughput:** The volume of requests or data a system can process in a given timeframe. It's typically measured in Queries Per Second (QPS) or bytes per second.

A common metric used to express throughput is QPS. Latency, on the other hand, describes the time budget of a single transaction. In high-load scenarios, these two concepts collide. When system throughput reaches maximum capacity, request queues begin to form, causing latency to climb exponentially.

```
Latency ^
        |             /  <- Queue exhaustion / exponential bottleneck
        |            /
        |           /
        |_________/
        +-------------------> Throughput (Load)
```

#### Tail Latency and Percentiles
A common mistake when measuring latency is relying on average or median values. Averages mask the experience of users in the tail end of the distribution. To understand system performance accurately, we use percentiles such as p95, p99, and p99.9. For example, a p99 latency of 500 ms means that 99% of requests complete within 500 ms, while 1% take longer. This tail latency is critical because power users, who often have the largest datasets or make the most requests, are the ones most likely to experience these slow responses.

In distributed systems, fan-out amplifies tail latency. When a single client request triggers parallel requests to dozens of downstream services, the overall response time is bound by the slowest downstream component. If a downstream service has a 1% chance of taking over a second, a fan-out of 100 services means the client request has a 63% chance of waiting over a second. This is known as tail latency amplification, and it explains why reducing the latency of the slowest services is a major focus in high-scale system design.

### Fault Tolerance and Resilience
Fault tolerance is the ability of a system to continue operating in the presence of faults. Since hardware will eventually fail, we use specific strategies to build resilience:
- **Redundancy:** Keeping duplicate components active so that if one fails, another can take over immediately. Active-passive redundancy uses a standby instance that takes over during a crash, while active-active redundancy distributes traffic across multiple live instances simultaneously.
- **Failover:** The automatic process of transferring traffic to a redundant component when the primary component fails.
- **Graceful Degradation:** Designing services to shut down non-critical features under stress to keep core functionality working. For example, an e-commerce site might disable its product recommendation engine if the database is overloaded, allowing users to still complete purchases.

To prevent cascading failures in a distributed architecture, we must build resilient services. Several patterns help mitigate risks:
- **Circuit Breakers:** These stop requests to a failing downstream dependency. By failing fast, they protect resources on the caller.
- **Exponential Backoff with Jitter:** This prevents thundering herd situations by adding randomized delays to retries.
- **Rate Limiting:** This stops clients from overwhelming our service, establishing a clear traffic ceiling.

#### Circuit Breaker State Transitions
A circuit breaker has three main states that define its operational behavior:
- **Closed:** Requests pass through normally. If the failure rate of downstream calls exceeds a configured threshold, the breaker trips into the Open state.
- **Open:** Requests fail immediately without calling the downstream dependency. This gives the failing service time to recover and prevents exhausting local threads.
- **Half-Open:** After a cool-down period, a limited number of test requests are allowed through. If these succeed, the circuit closes again; if they fail, the circuit returns to the Open state.

### Maintainability and its Three Pillars
Often, the majority of a system's lifecycle cost goes into ongoing maintenance rather than initial development. To keep this cost manageable, we design for maintainability. There are three core pillars of maintainability that guide our architectural choices:

- **Operability:** This is about making it easy for operations teams to keep the system running smoothly. It involves creating high-quality visibility into system health, providing tools for automated deployments, and establishing standard procedures for recovery. A system with good operability has clear logging, rich metrics, and straightforward configuration.
- **Simplicity:** This is the practice of removing accidental complexity from the system, making it easy for new engineers to understand. Accidental complexity arises when implementation choices introduce difficulties that are not inherent to the problem domain (such as using an overly complex data store or a tightly-coupled microservice graph when a simple monolith would suffice).
- **Evolvability:** This is the capacity of a system to adapt to new requirements as business needs change. A system has good evolvability if its components are decoupled, allowing engineers to modify or replace one part without causing a domino effect of breakages across the entire codebase.

### Scaling: Vertical vs Horizontal
As system load increases, we must scale our infrastructure:

- **Vertical Scaling (Scaling Up):** Adding more power (CPU, RAM, disk space) to a single server.
- **Horizontal Scaling (Scaling Out):** Adding more servers to the system.

| Dimension | Vertical Scaling (Scale Up) | Horizontal Scaling (Scale Out) |
| --- | --- | --- |
| Limit | Hard hardware ceiling | Virtually unlimited |
| Complexity | Very low (no code changes) | High (requires load balancers, sharding) |
| Single Point of Failure | High risk | Low risk (redundancy is built-in) |
| Cost | Exponential increase at high specs | Linear increase with commodity hardware |
| Downtime | Often requires restart | Zero downtime during scaling |

#### Elasticity
Elasticity represents a system's capability to adjust resource allocation dynamically as load changes. While scalability refers to the structural ability to handle growth, elasticity is about operational automation. An elastic system automatically provisions additional server instances during a midday traffic spike and shuts them down when traffic subsides at night. This automation is highly valuable in cloud environments, helping companies minimize operational expenses by paying only for active infrastructure.

### Statelessness and Horizontal Scale
Statelessness is the key that unlocks horizontal scaling. An application is stateless if it doesn't store session data, local files, or persistent state on the application server itself. Each request from a user contains all the information needed to process it.

When the application tier is stateless, any server can handle any request. We can easily place a load balancer in front of our servers. If traffic spikes, we simply launch more server instances, and the load balancer distributes requests among them.

Stateful tiers (such as databases or caches) are much harder to scale horizontally. They require complex synchronization protocols, consensus algorithms, replication strategies, and data partitioning keys to ensure consistency.

### Worked Examples

#### Example 1: Component Availability in Series vs Parallel
Let's calculate the availability of two different system designs. Assume we use independent service components, and each component has an availability of 99.9% (0.999).

**Case A: Series Connection**
Suppose a user request must travel sequentially through Service A and Service B to succeed. If either service fails, the request fails.
```
Overall Availability = P(A is up) * P(B is up)
Overall Availability = 0.999 * 0.999 = 0.998001
Overall Availability = 99.8%
```
This result demonstrates that chaining independent components in series reduces the overall availability below that of any individual component.

**Case B: Parallel Connection (Redundancy)**
Suppose we have a web service with two redundant web servers running behind a load balancer. The system is available as long as at least one server is operational.
```
Probability of Server A failing = 1 - 0.999 = 0.001
Probability of Server B failing = 1 - 0.999 = 0.001
Probability of both servers failing = 0.001 * 0.001 = 0.000001
Overall Availability = 1 - (Probability of both failing)
Overall Availability = 1 - 0.000001 = 0.999999
Overall Availability = 99.9999%
```
This calculation highlights how introducing redundancy in parallel massively boosts availability, turning three nines of component availability into six nines of system availability.

#### Example 2: Computing Downtime for 99.9% vs 99.99%
Let's calculate the maximum allowed downtime per year for different SLA targets. Assume a standard non-leap year has 365 days.
```
Total minutes in a year = 365 days * 24 hours/day * 60 minutes/hour = 525,600 minutes
```

**Step 1: Compute Downtime for 99.9% Availability (Three Nines)**
```
Allowed downtime percentage = 100% - 99.9% = 0.1% = 0.001
Allowed downtime per year = 525,600 minutes * 0.001 = 525.6 minutes
525.6 minutes = 8 hours and 45.6 minutes (8.76 hours)
```

**Step 2: Compute Downtime for 99.99% Availability (Four Nines)**
```
Allowed downtime percentage = 100% - 99.99% = 0.01% = 0.0001
Allowed downtime per year = 525,600 minutes * 0.0001 = 52.56 minutes
```

**Step 3: Analyze Operational Implications**
- **Three Nines (99.9%):** The system can be down for almost 9 hours a year. This budget allows for manual human intervention. If an alert fires at 2:00 AM, an on-call engineer can wake up, log in, diagnose the issue, and restart the service within an hour or two without violating the SLA.
- **Four Nines (99.99%):** The system can only be down for 52 minutes a year. This requires fully automated processes. Human intervention is too slow. The system must use automatic health checks, automated failover, self-healing orchestration, and automated rolling deployments to keep downtime minimal.

#### Example 3: Scaling Decision Scenario
Suppose you operate a relational database that stores user accounts and financial balances. During peak hours, the CPU utilization of the database server consistently hits 85%, causing query latencies to spike and violating the 200 ms latency SLO. Let's analyze the scaling paths.

**Option A: Vertical Scaling (Scale Up)**
Upgrade the database server from a 16-core CPU with 64 GB RAM to a 64-core CPU with 256 GB RAM.
- **Why it fits:** Relational databases rely on strict ACID transactions and table joins. By scaling vertically, we keep all data on a single machine. The application code remains unchanged, and we avoid the complexity of distributed transactions.
- **Trade-off:** This is a temporary fix. We will eventually hit the hardware limits of available cloud instances. Upgrading the hardware may also require scheduled downtime during the server migration.

**Option B: Horizontal Scaling (Scale Out)**
Split the database by partitioning user accounts across multiple database servers (sharding) based on a `user_id` hash key.
- **Why it fits:** Sharding provides a theoretically infinite scaling path. We can keep adding cheap commodity servers to handle growth.
- **Trade-off:** This path introduces massive software complexity. Joins across different shards become impossible without executing multiple database queries and stitching results together in the application tier. We must also manage distributed transactions and write custom routing logic in our application.

**The Decision:**
The optimal engineering choice is to scale vertically first. Upgrading the database server is the fastest way to resolve the performance issue without changing the application architecture. While doing this, we should prepare for the future by implementing read replication. This offloads read traffic (which doesn't modify state) to replica nodes, preserving the primary node's CPU for write transactions. We should only migrate to horizontal sharding when we hit the absolute physical limits of vertical hardware.

## Pros
- **High availability:** Redundant parallel components ensure the system remains accessible even during hardware failures.
- **Infinite scaling potential:** Horizontal scaling allows the system to grow continuously by adding cheap commodity hardware.
- **Exceptional fault tolerance:** Isolation between nodes prevents a single component's crash from bringing down the entire platform.
- **Operational flexibility:** Stateless application tiers allow zero-downtime rolling updates and rapid auto-scaling based on real-time traffic.
- **Localized maintenance:** Distributed components can be upgraded or restarted individually without causing a global outage.

## Cons
- **High software complexity:** Shifting from a single machine to a distributed architecture requires complex coordination, service discovery, and data replication.
- **Data consistency issues:** Maintaining consistent state across horizontally scaled nodes requires eventual consistency models and handles replication lag.
- **Increased network latency:** Distributing components across different servers introduces network hops, slowing down individual request latency.
- **Operational overhead:** Monitoring, logging, and debugging become significantly harder when requests span multiple microservices.
- **High distributed coordination cost:** Protocols like two-phase commit or consensus algorithms consume CPU and network resources to keep data synchronized.

## Alternatives
- **Monolithic scaling:** Keep the entire application as a single large codebase on a vertically scaled server. This is preferable for small teams and early-stage products to minimize operational complexity.
- **Serverless architectures:** Outsource scaling and server provisioning completely to cloud providers using functions-as-a-service. This is best when traffic is highly bursty and unpredictable, though it can become expensive at scale.
- **Mainframe hosting:** Run critical, transaction-heavy systems on specialized mainframe hardware instead of distributed commodity servers. This is common in banking where absolute reliability and single-thread throughput are paramount.
- **Hybrid scaling (Hybrid Cloud):** Split workload between a local private cloud and public cloud resources. This is preferred for compliance or latency reasons, burst-scaling non-sensitive tasks while maintaining strict control over core customer records locally.

## When to use it
- **High-traffic applications:** Use horizontal scaling when serving millions of active users where single-machine memory and CPU limits are easily exceeded.
- **SLA-bound systems:** Use redundancy and failover mechanisms when building enterprise systems that must guarantee 99.99% availability or higher.
- **Global products:** Use distributed deployments across multiple regions to reduce network latency for international users.
- **High-concurrency streaming and analytics:** Use when designing large-scale real-time telemetry systems, clickstream analysis platforms, or financial ticker services that process massive volumes of concurrent data feeds.

## When NOT to use it
- **Early startups:** Avoid horizontal scaling and complex distributed architectures when validating product-market fit. Stick to a simple monolith to move fast.
- **Low-budget projects:** Do not use redundant multi-region architectures if the business cannot justify the cost of maintaining idle standby resources.
- **Batch processing tools:** If your application runs nightly data migrations or local reporting scripts, focus on optimizing single-threaded performance rather than horizontal distribution.
- **Simple static landing pages:** Avoid horizontal scaling infrastructure for static websites, documentation portals, or blogs. A content delivery network (CDN) combined with basic object hosting (like AWS S3) is far more cost-effective and simpler to operate than a cluster of servers.

## Key takeaways / mental model
The mental model of distributed scaling is about managing state. Stateless tiers are easy to scale horizontally because any server can handle any request. Stateful tiers are hard to scale because data must be consistent, durable, and synchronized across nodes. When designing for high availability, always remember that series connections multiply failures, while parallel connections isolate them. Choose vertical scaling as long as it is cost-effective, and only introduce horizontal state distribution when physical limits force your hand. Finally, build your operational metrics around percentiles rather than averages, as averages hide the critical tail latency experienced by your most active users.

## Self-check questions
1. Explain the difference between reliability and availability. Can a system be available but unreliable, or reliable but unavailable?
2. If three independent database replicas each have an availability of 99%, what is the overall availability of the database tier if only one replica needs to be online to serve reads?
3. Why does statelessness enable easy horizontal scaling of the application tier, and what technologies do we use to store state off the application servers?
4. How does manual intervention impact our ability to meet a 99.99% availability SLA, and what automation must be put in place to achieve it?
5. A system has an MTBF of 4,000 hours and an MTTR of 4 hours. Calculate its availability percentage.
6. What architectural complexities arise when we choose to partition and shard a relational database horizontally?
7. How does fan-out latency amplification affect the design of downstream microservices, and what strategies can be used to mitigate it?

## References
- System Design Guide for Software Professionals (Sinha & Chopra, Packt 2024), Chapter 2.
- Designing Data-Intensive Applications (Martin Kleppmann, O'Reilly 2017), Chapter 1.
- Google Site Reliability Engineering Book (Betsy Beyer et al., O'Reilly 2016), Chapter 4: "Service Level Objectives".
