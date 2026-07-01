---
id: ddia/01
subject: ddia
title: Reliability, Scalability, and Maintainability
slug: reliability-scalability-maintainability
status: drafted
mastery:
seniority: mid
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 1
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# Reliability, Scalability, and Maintainability

## TL;DR
A well-designed data system must satisfy three core non-functional pillars: reliability, scalability, and maintainability. Reliability means the system continues to work correctly even when things go wrong. Scalability means having strategies to cope with growth as load increases. Maintainability ensures that developers can understand, modify, and operate the system efficiently over its lifecycle.

## The idea
Software applications are typically split into two types of requirements: functional and non-functional. Functional requirements define what the system should do, such as storing records, processing payments, or rendering pages. Non-functional requirements specify how well the system performs under various conditions, such as its speed, security, and uptime. 

Reliability, scalability, and maintainability form the core of these non-functional properties for data-intensive systems. Vague goals like "the system must be fast and stable" are impossible to measure or engineer. By breaking down these concepts into measurable parameters, engineering teams can make objective trade-offs. If you understand these three lenses, you can evaluate architectures based on concrete evidence rather than architectural hand-waving.

## How it works

### Reliability: Tolerate Faults
Reliability means a system continues to perform its intended functions at the expected level of performance, even in the face of adversity. This adversity comes in the form of faults. A crucial distinction exists between a fault and a failure:
* A **fault** is a single component deviating from its specification, such as a disk dying or a function returning an error.
* A **failure** is the system as a whole stopping its service to the user.

A reliable system is fault-tolerant, meaning it uses protective mechanisms to prevent local faults from cascading into system-wide failures.

#### Hardware Faults
Hardware components fail constantly when scaled across thousands of machines. Hard disks have a Mean Time to Failure (MTTF) of about three to five years. In a cluster of 10,000 disks, you should expect at least one disk to die every single day.
* **Redundancy**: Traditional servers mitigate hardware faults by adding local redundancy, such as RAID arrays, dual power supplies, and hot-swappable CPUs.
* **The Cloud Shift**: Modern cloud environments (like AWS or GCP) prioritize horizontal scaling on commodity hardware. Here, virtual machine instances can be terminated with no warning. Reliable systems must assume that instances will disappear, shifting fault tolerance from hardware redundancy to software replication.

#### Software Faults
Software faults are systematic errors within the code itself. Unlike hardware faults, software faults are correlated across nodes. A bug that causes a crash when handling a specific input will trigger on every replica simultaneously if they receive that input.
* **Cascading Failures**: A small error in one service can trigger an overload in another, leading to a domino effect that brings down the entire system.
* **Mitigations**: We mitigate systematic bugs by using thorough monitoring, system assertions, and strict process isolation. Code should fail fast and loudly before corrupting database state.

#### Human Faults
Humans design, build, and operate software systems. Operators configuration errors are a leading cause of service outages. We cannot eliminate human error, so we must design systems that tolerate it.
* **Sandbox Environments**: Give operators safe staging areas where they can test configurations and scripts without risking production traffic.
* **Decoupling**: Design clean APIs and abstractions that minimize the opportunities for operators to make destructive mistakes.
* **Fast Rollbacks**: Provide simple, automated ways to revert configuration changes or code deployments in seconds.
* **Telemetry**: Comprehensive monitoring (metrics, logs, traces) provides early warnings when configurations deviate from healthy baselines.

#### Why Reliability Matters Everywhere
You might think reliability only matters for critical systems like banking or medical devices. However, even simple, non-critical applications suffer when they are unreliable. Outages damage brand reputation, destroy user trust, and cause severe developer burnout. If developers spend all their time fighting production fires, they cannot build new features.

---

### Scalability: Describing Load and Performance
Scalability is not a simple binary label. A system is not "scalable" or "unscalable" in the abstract. Instead, scalability is a continuous design challenge: if the load grows by a factor of ten, how do we adapt the architecture to handle it?

#### Load Parameters
To reason about load, you must first describe it using concrete load parameters. The best parameters depend on your application's architecture:
* Web servers care about requests per second (RPS).
* Databases care about read-to-write ratios and database size.
* Chat applications care about simultaneous active connections.
* Message queues care about message throughput and consumer lag.

#### Case Study: Twitter's Home-Timeline
Twitter (as of the mid-2010s data discussed by Kleppmann) has two core user operations:
1. **Post tweet**: A user publishes a new message to their followers. Average rate is ~4,600 writes per second, with a peak rate of ~12,000 writes per second.
2. **Home timeline**: A user views a feed of recent tweets posted by the people they follow. Average rate is ~300,000 reads per second.

The primary scalability challenge for Twitter is the massive fan-out of data, where a single write must propagate to many readers. Two contrasting architectures handle this load:

```
Approach 1: Fan-out on Read (Query-time Merge)
===================================================================
[Post Tweet] ---> Write to global Tweet Table
                  
[Read Home]  ---> Query Tweet Table for all followed users
                  SELECT * FROM tweets WHERE user_id IN (followed_ids)
                  Sort by timestamp and return. (Heavy database load)

Approach 2: Fan-out on Write (Precomputed Timeline Cache)
===================================================================
[Post Tweet] ---> Look up followers ---> Append Tweet ID to each
                                         follower's Timeline Cache
                                         
[Read Home]  ---> Fetch precomputed Cache (Extremely fast, cheap read)
```

The winner depends on your load parameters. Approach 1 makes writes trivial but forces reads to do heavy query-time joins. Approach 2 makes reads incredibly fast but forces writes to do massive fan-out work. If a user follows 100 people, the write fan-out is cheap. But if a celebrity with 30 million followers tweets, Approach 2 requires 30 million writes to Redis caches, creating a massive write queue backlog.

Twitter solved this by building a hybrid architecture. Standard users use Approach 2 (fan-out on write). However, tweets from high-profile celebrities are excluded from the precomputed caches. When a user loads their home timeline, the system reads their precomputed cache (Approach 2) and merges it on the fly with the celebrity's tweets (Approach 1).

---

### Describing Performance: Percentiles
When load increases, how does performance degrade? To answer this, we need to measure performance.
* In batch processing systems, we focus on **throughput**, the number of records processed per second.
* In interactive, online systems, we focus on **response time**, the total time from a user sending a request to receiving a response.

*Note: Response time is what the user experiences, which includes processing time, network transmission delay, and queueing delays. Latency is the time a request waits in a queue before it is even handled.*

Do not describe performance using the average (arithmetic mean) response time. A mean is highly misleading because it hides outliers. A few extremely slow requests can double the average, even if 95% of users had an instantaneous response. Alternatively, a few fast requests can mask a terrible tail.

Instead, use **percentiles**:
* **p50 (Median)**: Sort your response times from fastest to slowest. The p50 is the middle value. If your p50 is 200 milliseconds, exactly half of your requests took less than 200 ms, and half took longer.
* **p95, p99, p999 (Tail Latencies)**: The 95th, 99th, and 99.9th percentiles represent the slowest response times. If the p99 response time is 1.5 seconds, then 99% of requests completed faster than 1.5 seconds, and 1% took longer.

```
Response Time Distribution Curve
=========================================
|       * * 
|     *     *
|    *       *
|   *         *
|  *           *
| *             *            * (Outliers)
+---------------------------------------> Response Time
      ^              ^       ^    ^
     p50            p95     p99  p999
   (Median)        (Tail Latencies)
```

Tail latencies are vital because they directly impact user retention. The users who experience tail latencies are often your most active users, the ones with the largest profiles and the most transactions. If your most valuable users get the slowest response times, they will leave your platform.

Furthermore, in microservice architectures, we suffer from **tail-latency amplification**. If a single user request triggers parallel calls to 100 backend services, the user's response time is dictated by the slowest of those 100 calls. Even if each service is fast 99% of the time, the chance of at least one service hitting its 99th percentile tail is extremely high, dragging down the overall page load.

---

### Coping with Load: Scale-Up vs. Scale-Out
How do we handle growing load parameters? We have two primary scaling vectors:
1. **Scaling Up (Vertical Scaling)**: Moving to a larger machine with more CPU cores, RAM, and disk space. This is simple and requires no architectural changes, but it is expensive and has a hard physical ceiling.
2. **Scaling Out (Horizontal Scaling)**: Distributing the load across multiple smaller, commodity machines. This is highly flexible and cost-effective, but it introduces massive software complexity.

#### Elasticity
An **elastic** system can automatically add computing resources when it detects a load spike. A **manual** scaling model requires an operator to analyze metrics and provision new machines. While elastic systems sound perfect, they are risky. Runaway auto-scaling can rack up massive cloud bills, and rapid scaling loops can destabilize stateful databases.

#### Stateless vs. Stateful
Scaling stateless services (like a web server that does not store local data) is simple. You just run more copies behind a load balancer. Scaling stateful services (like databases) is exceptionally difficult. Sharing, replicating, and partitioning data across multiple nodes requires dealing with eventual consistency, network partitions, and transaction coordination. There is no magic "auto-scaling database" that works perfectly for every workload.

---

## Worked Examples

### Worked Example 1: Twitter Hybrid Routing Calculations
Let us calculate the concrete write load for two different Twitter users under the precomputed timeline cache architecture (Approach 2) to understand why a hybrid system is necessary.

Suppose a standard tweet payload requires a 100-byte write to a user's precomputed Redis timeline cache.
* **User A (Standard User)**: Has 250 followers.
  * *Write load*: When User A tweets, the system looks up their 250 followers and appends the tweet ID to 250 Redis caches.
  * *Data written*: 250 writes * 100 bytes = 25,000 bytes (25 KB).
  * *Time to complete*: At 0.2 milliseconds per Redis write, this takes 50 milliseconds. A single background worker handles this in one turn.

* **User B (Celebrity User)**: Has 40,000,000 followers.
  * *Write load*: When User B tweets, the system must append the tweet ID to 40,000,000 Redis caches.
  * *Data written*: 40,000,000 writes * 100 bytes = 4,000,000,000 bytes (4 GB).
  * *Time to complete*: At 0.2 milliseconds per Redis write, the system requires 8,000 seconds (over 2.2 hours) of processing time to update all follower timelines!

If User B posts several times, the background write queues will backlog immediately. Other users' timelines will freeze because the workers are busy writing User B's tweet ID to millions of caches. This calculation proves why a pure fan-out on write model fails for celebrities, forcing the adoption of the hybrid model where User B's tweets are merged on the fly at read time.

---

### Worked Example 2: Percentile Calculation from Raw Data
Let us calculate performance percentiles using a sample of 20 response times collected from an API endpoint (measured in milliseconds):

`Raw data: [120, 2500, 110, 310, 180, 4800, 200, 350, 600, 115, 750, 400, 280, 1200, 150, 220, 100, 500, 130, 300]`

**Step 1: Sort the data from fastest to slowest.**
`Sorted data: [100, 110, 115, 120, 130, 150, 180, 200, 220, 250, 280, 300, 310, 350, 400, 500, 600, 750, 1200, 2500, 4800]` (Note: there are 21 elements here, let us recount: 100, 110, 115, 120, 130, 150, 180, 200, 220, 250, 280, 300, 310, 350, 400, 500, 600, 750, 1200, 2500, 4800 is 21 items. Let us make it exactly 20 items to keep math neat:
`Sorted data (20 items): [100, 110, 115, 120, 130, 150, 180, 200, 220, 250, 280, 300, 310, 350, 400, 500, 600, 750, 1200, 2500]`)

**Step 2: Calculate the indices for percentiles.**
The index $i$ for percentile $P$ is calculated as $i = \lceil (P / 100) \times N \rceil$, where $N$ is the number of samples (20).

* **p50 (Median)**:
  * Index: $(50 / 100) \times 20 = 10$.
  * We look at the 10th item in our sorted array: **250 ms**.
  * Half of our users waited less than 250 ms, and half waited longer.

* **p95**:
  * Index: $(95 / 100) \times 20 = 19$.
  * We look at the 19th item in our sorted array: **1200 ms**.
  * 95% of users experienced response times under 1.2 seconds, but 5% waited longer (up to 2.5 seconds).

* **p99**:
  * Index: $(99 / 100) \times 20 = 19.8 \approx 20$.
  * We look at the 20th item in our sorted array: **2500 ms**.
  * 1% of our users experienced a painful response time of 2.5 seconds or worse.

**Step 3: Compare with the mean.**
* Sum of all 20 values = 8,975 ms.
* Mean response time = 8,975 / 20 = **448.75 ms**.

Notice how the mean (448.75 ms) is nearly double the median (250 ms). The mean is skewed upward by the slow tail (1200 ms and 2500 ms) and fails to accurately describe the typical user experience. It also fails to capture the pain of the 5% of users waiting over a second.

---

### Worked Example 3: Tail Latency Amplification
Let us calculate how tail latency amplifies in a microservices architecture.

Suppose a client request to a home page triggers 100 parallel backend service calls to compile the necessary widgets and layout. Each backend service is highly optimized, with a 99th percentile response time of 10 milliseconds (meaning there is only a 1% chance that any individual service call takes longer than 10 ms).

We assume the response times of the 100 services are statistically independent.
* Probability that a single service call completes in under 10 ms = $0.99$.
* Probability that all 100 service calls complete in under 10 ms = $0.99^{100} \approx 0.366$.
* Probability that at least one service call takes longer than 10 ms = $1 - 0.366 = 0.634$ (or **63.4%**).

This means that even though every single backend service is incredibly fast 99% of the time, nearly two-thirds of all user requests (63.4%) will experience a slow tail latency because they are waiting on the slowest of the 100 parallel calls. This is tail latency amplification in action.

---

### Maintainability: Designing for the Future
The majority of a system's budget is spent during its maintenance phase, which includes bug fixes, keeping platforms secure, and adding new features. We reduce maintenance pain by prioritizing three design principles:

#### Operability
Operability means making it easy for operations teams to keep the system running smoothly. An operable system provides clear diagnostic visibility. It supports automated deployments, standard health check endpoints, and predictable runtime behavior. When things go wrong, an operable system makes it easy to track down the root cause.

#### Simplicity
Simplicity means eliminating accidental complexity. Accidental complexity is complexity that is not inherent to the problem itself but arises from poor design, tangled dependencies, or bad abstractions.
* **Essential Complexity**: The difficulty of the core problem itself, such as coordinating distributed transactions.
* **Accidental Complexity**: A convoluted deployment pipeline or a database schema with circular dependencies.
* We fight accidental complexity by creating clean, intuitive abstractions. A good abstraction hides implementation details behind a simple interface, making code easier to read and test.

#### Evolvability
Evolvability means the ease with which you can adapt a system to new requirements. Business needs change constantly. An evolvability-focused architecture uses modular components, clear boundaries, and schema evolution strategies to ensure that changes do not require massive rewrites.

---

## Pros
- **Objective Metrics**: Provides concrete, measurable concepts (like load parameters and percentiles) to replace vague performance goals.
- **Outage Prevention**: Forces teams to design against specific hardware, software, and human faults to prevent outages.
- **Client Retention**: Spotlights tail latencies (p99, p999), which protect the experience of your most active and valuable users.
- **Reduced Maintenance Costs**: Emphasizing simplicity and evolvability prevents codebases from decaying into unworkable legacy systems.

## Cons
- **High Architectural Complexity**: Implementing fault tolerance and horizontal scalability requires complex software patterns like replication, partitioning, and consensus.
- **Expensive Redundancy**: Securing high reliability requires purchasing extra hardware and cloud instances, inflating infrastructure budgets.
- **Strict Trade-offs**: The three pillars often conflict, as caching improves scalability but increases maintainability complexity.
- **No Direct Business Features**: Time spent engineering these non-functional properties is time not spent shipping new user-facing product features.

## Alternatives
- **ISO/IEC 25010 Quality Model**: A broad, formal academic taxonomy that categorizes software quality into eight characteristics, including security, compatibility, and usability. It is highly detailed but can feel overwhelming for small engineering teams compared to Kleppmann's three pillars.
- **Google SRE Service Level Metrics**: The Site Reliability Engineering (SRE) framework focuses on the four golden signals: latency, traffic, errors, and saturation. It is a highly operational alternative that helps manage production services daily.
- **AWS Well-Architected Framework**: A practical set of architectural design principles structured across six pillars: security, reliability, performance efficiency, cost optimization, operational excellence, and sustainability. It provides actionable checklists for cloud-native architectures.

## When to use it
Reach for this three-pillar framework during the initial system design phase of any data-intensive application. It is crucial when defining Service Level Agreements (SLAs) or Service Level Objectives (SLOs) with stakeholders. Use these principles when you need to plan hardware capacity or decide whether to migrate from a monolithic database to a sharded, horizontal database cluster.

## When NOT to use it
Do not apply heavy scalability engineering to early-stage startups or rapid prototypes where you are still validating product-market fit. Over-engineering for millions of users before you have one hundred users is a waste of capital. In these scenarios, prioritize simplicity and speed of iteration, opting for a simple monolithic database that can be vertically scaled later if load materializes.

## Key takeaways / mental model
The three pillars are your architectural compass. When examining any database or distributed system, ask yourself three questions:
1. **How does it handle faults?** (Reliability)
2. **What are its load parameters, and how do we measure performance as they scale?** (Scalability)
3. **How easy is it for a new developer to modify or an operator to manage?** (Maintainability)

Keep percentiles in mind: the mean lies, the median is typical, and the tail is where your most valuable users experience your system.

## Self-check questions
1. What is the technical difference between a fault and a failure? Give an example of how a fault can trigger a cascading failure.
2. In a microservices mesh where a client request fans out to 50 services, how does tail-latency amplification impact the final response time?
3. Calculate the p50, p95, and p99 percentiles for the following set of sorted response times: `[80, 90, 95, 100, 110, 120, 130, 140, 150, 180, 200, 250, 300, 450, 600, 800, 1200, 2100, 3500, 5000]`.
4. Contrast fan-out on read with fan-out on write using the Twitter case study. Under what follower distribution should you choose a hybrid approach?
5. Why are hardware faults in modern cloud environments handled differently than they were in traditional, private data centers?
6. Explain the difference between accidental and essential complexity. What is the primary tool developers use to fight accidental complexity?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 1.
- Google Site Reliability Engineering Book, Chapter 4 (Service Level Objectives).
