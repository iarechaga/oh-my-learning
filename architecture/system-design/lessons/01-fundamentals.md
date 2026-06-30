---
id: system-design/01
subject: system-design
title: System Design Fundamentals
slug: fundamentals
status: drafted
mastery:
source: "System Design Guide for Software Professionals (Sinha & Chopra, Packt 2024), Chapter 1"
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# System Design Fundamentals

## TL;DR
System design defines the architecture, components, modules, interfaces, and data for a system to satisfy specified requirements. This lesson covers high-level versus low-level design, a repeatable design process, and back-of-the-envelope estimation. You will learn to translate vague requests into concrete technical requirements and estimate scale from daily active users.

## The idea
When building simple applications, we focus on correctness, algorithms, and data structures. As systems grow to serve millions of users, single-machine constraints break. System design exists to address these scaling challenges. It's about making deliberate technical choices to balance scalability, availability, reliability, and cost. A structured approach then helps transition from an abstract product vision to a concrete, deployable architecture that survives real-world load.

Without proper design, systems grow as a chaotic collection of patches. They become impossible to scale and fragile under stress. By understanding the core building blocks, we can design systems that can evolve over time. This foundational knowledge allows us to build reliable, scalable, and maintainable systems, which applies the reliability/scalability framing, DDIA concept 01.

## How it works
This section covers the core concepts and mechanics of designing software systems.

### High-Level Design (HLD) vs Low-Level Design (LLD)
High-level design and low-level design represent two different phases and zoom levels of the engineering process.

- **High-Level Design (HLD):** The focus is on the global architecture. Its scope covers major components, databases, cache layers, message queues, and external integrations. We use it to outline how data flows across the system, how scalability is achieved, and how components fail gracefully. HLD is the view from 10,000 feet.
- **Low-Level Design (LLD):** The focus zooms into the individual components defined in HLD. The engineer specifies class structures, database table schemas, precise API endpoints, data structures, and algorithms. This translates architectural components into implementable code modules.

| Dimension | High-Level Design (HLD) | Low-Level Design (LLD) |
| --- | --- | --- |
| Focus | Overall architecture and data flow | Class structures, schemas, and APIs |
| Key Questions | What are the components? How do they talk? | What are the classes? What data structures? |
| Audience | Architects, Product Managers, Leads | Developers, QA Engineers |
| Output | System topology, component diagrams | Class diagrams, database schemas, API specs |

### A Repeatable Design Process
Designing a complex system can feel overwhelming. To manage this complexity, engineers follow a repeatable, four-step design process:

1. **Clarify Requirements:** Start by scope definition. Don't guess what the system should do. Ask clarifying questions to establish functional and non-functional bounds. This prevents wasted engineering cycles on wrong assumptions.
2. **High-Level Architecture:** Sketch the major building blocks. Identify the client, API gateway, application servers, and storage layers. Define the primary data flow. Keep this step simple, avoiding deep component detail.
3. **Deep Dive:** Drill down into specific bottlenecks. This is where you design the database schema, choose specific database types, explain partitioning strategies, and describe cache eviction policies. Focus on the core system trade-offs here.
4. **Identify Bottlenecks and Failures:** Analyse failure points. Explain how the system handles database crashes, network partitions, or sudden traffic spikes. Plan for redundancy and graceful degradation to maintain uptime.

### Functional vs Non-Functional Requirements
Requirements fall into two distinct categories:

- **Functional Requirements:** These define what the system actually does from a user perspective. They are the specific features the application must support. Examples include: "Users can post photos" or "Users can follow other users."
- **Non-Functional Requirements:** These define how well the system performs its duties. They place constraints on the system's behavior, establishing the operational quality. Examples include: availability, latency, scalability, security, and durability.

The two requirement types interact constantly. A functional requirement like "Users can upload 10 MB files" immediately creates non-functional constraints. It impacts bandwidth, read-write latency, and storage consumption.

### Back-of-the-Envelope Estimation
Back-of-the-envelope calculations are rough estimates used to choose architectural patterns and storage technologies. They help determine if an architecture can handle the expected scale before any code is written.

To perform these estimations, we use powers of two, data size conversions, and standard latency benchmarks.

#### Powers of Two and Data Sizes
It helps to remember the relation between data sizes and powers of two:

```
2^10 = 1,000 (Thousand) = 1 Kilobyte (KB)
2^20 = 1,000,000 (Million) = 1 Megabyte (MB)
2^30 = 1,000,000,000 (Billion) = 1 Gigabyte (GB)
2^40 = 1,000,000,000,000 (Trillion) = 1 Terabyte (TB)
2^50 = 1,000,000,000,000,000 (Quadrillion) = 1 Petabyte (PB)
```

#### Latency Numbers Every Engineer Should Know
Understanding approximate latency numbers is critical for performance tuning. These benchmarks highlight why certain designs avoid disk seeks or remote network calls.

```
L1 cache reference ......................... 0.5 ns
Branch mispredict .......................... 5   ns
L2 cache reference ......................... 7   ns
Mutex lock/unlock .......................... 25  ns
Main memory reference ....................... 100 ns
Send 1K bytes over 1 Gbps network .......... 10,000 ns (10 us)
Read 4K randomly from SSD .................. 150,000 ns (150 us)
Read 1 MB sequentially from memory ......... 250,000 ns (250 us)
Round trip within same datacenter .......... 500,000 ns (0.5 ms)
Read 1 MB sequentially from SSD ............ 1,000,000 ns (1 ms)
Disk seek (HDD random read) ................ 10,000,000 ns (10 ms)
Read 1 MB sequentially from HDD ............ 20,000,000 ns (20 ms)
WAN network round trip (cross-Atlantic) .... 150,000,000 ns (150 ms)
```

```
[L1 Cache: 0.5ns] -> [L2 Cache: 7ns] -> [RAM: 100ns] -> [SSD random: 150us] -> [HDD seek: 10ms]
-------------------------------------------------------------------------------------------->
                                       Latency Scale (Logarithmic)
```

These numbers guide database selection. For instance, caching data in memory (100ns) is 100,000 times faster than reading from a spinning disk seek (10ms).

#### Estimating Bandwidth and Memory (RAM)
In addition to QPS and storage, we must calculate bandwidth and memory requirements. These figures dictate network provisioning and cache cluster sizing.

- **Bandwidth Estimation:** Bandwidth is the volume of data passing through a network per second. We calculate both inbound (ingress) bandwidth from uploads and outbound (egress) bandwidth from downloads.
- **Memory Estimation:** Memory estimation typically focuses on caching strategies. A common rule of thumb is the 80/20 rule: caching 20% of the daily hot data can serve 80% of the read requests.

### Worked Examples

#### Example 1: Photo-Sharing Service Scale Estimation
Let's estimate QPS, storage, bandwidth, and memory requirements for a photo-sharing platform.

**Assumptions:**
- Daily Active Users (DAU) = 10 million.
- Average photos uploaded per active user per day = 0.1 (1 photo per 10 days per user).
- Average photo file size = 2 MB.
- Average metadata size per photo in database = 500 bytes.
- Ratio of read requests to write requests = 10:1 (Read-heavy system).

**Step 1: Calculate Queries Per Second (QPS) for Writes**
```
Daily uploads = 10,000,000 DAU * 0.1 uploads = 1,000,000 uploads per day
Seconds in a day = 24 * 3600 = 86,400 seconds (approx. 100,000 seconds for simpler math)
Write QPS = 1,000,000 uploads / 100,000 seconds = 10 write QPS
Using precise seconds: 1,000,000 / 86,400 = 11.57 writes per second. We will design for 12 write QPS.
```

**Step 2: Calculate Queries Per Second (QPS) for Reads**
```
Read QPS = 12 write QPS * 10 = 120 read QPS
```
Total peak QPS can reach 3 to 5 times the average QPS during high-traffic events. This means we should design for at least 600 read QPS.

**Step 3: Storage Estimation for Photos (Blob Storage)**
```
Daily uploads = 1,000,000 photos
Daily storage required = 1,000,000 * 2 MB = 2,000,000 MB = 2 TB per day
Annual storage required = 2 TB/day * 365 days = 730 TB per year
```
To account for backup replicas and future growth, we should factor in a redundancy multiplier of 3, requiring 2.19 PB of raw storage per year.

**Step 4: Metadata Database Storage Estimation**
```
Daily database records = 1,000,000 records
Daily metadata storage = 1,000,000 * 500 bytes = 500,000,000 bytes = 500 MB per day
Annual metadata storage = 500 MB/day * 365 days = 182.5 GB per year
```
This calculation shows that photo metadata easily fits into a standard relational database on a single large node. The photos themselves must go to a dedicated object store.

**Step 5: Bandwidth Estimation**
Let's calculate the required network throughput.
```
Inbound (Ingress) Bandwidth = 12 uploads/sec * 2 MB/photo = 24 MB/s (approx. 192 Mbps)
Outbound (Egress) Bandwidth = 120 reads/sec * 2 MB/photo = 240 MB/s (approx. 1.92 Gbps)
```
This egress rate is significant. We will need a Content Delivery Network (CDN) to offload photo delivery and prevent our servers from choking on image downloads.

**Step 6: Cache Memory (RAM) Estimation**
Assuming we want to cache the metadata of hot photos using the 80/20 rule.
```
Daily uploaded photos = 1,000,000
Metadata per photo = 500 bytes
Daily metadata size = 500 MB
Metadata to cache (20% of daily photos) = 500 MB * 0.20 = 100 MB
```
If we want to cache photo metadata for the last 30 days to handle historical reads, the total memory needed is:
```
Total Memory Required = 100 MB * 30 days = 3 GB
```
This easily fits into a small Redis instance, confirming that memory caching is highly viable for metadata access patterns.

#### Example 2: Translating a Vague Request
Let's translate a vague requirement: "We need an internal messaging tool like Slack."

**Vague Request:** "Build a chat app."

**Functional Requirements:**
1. Users must be able to send one-on-one direct messages.
2. Users must be able to create public group channels.
3. Users must see if a contact is online or offline.
4. Users must be able to upload file attachments up to 10 MB.

**Non-Functional Requirements:**
1. **Low Latency:** Message delivery latency must be under 200 ms to preserve real-time conversations.
2. **High Availability:** The system must achieve 99.9% availability, which equals about 8.76 hours of downtime per year.
3. **Consistency:** Channel message order must be consistent across all participants in a channel.
4. **Scale:** The architecture must support up to 10,000 concurrent users per channel.

#### Example 3: Powers-of-Two and Latency Calculation
Suppose you need to design a system that reads user profile records. Each record is 1 KB. You have a choice between storing these records in memory (Redis cache) or on a traditional hard disk drive (HDD). You need to fetch 100 random records to build a user's dashboard. Let's calculate the latency difference.

**Option A: HDD Random Reads**
An HDD random read requires a disk seek, taking around 10 ms.
To fetch 100 random records sequentially:
```
Total Latency = 100 reads * 10 ms/read = 1,000 ms = 1 second
```
This latency is unacceptable for a web page request, which should complete in under 200 ms.

**Option B: Memory Random Reads (Redis)**
A memory read takes about 100 ns.
Even with a network round trip within the same datacenter (0.5 ms) for each read:
```
Total Latency = 100 reads * (100 ns + 0.5 ms) = 100 * 0.5001 ms = 50.01 ms
```
If we use pipelining to batch the 100 requests into a single network round trip, the latency drops further:
```
Total Latency = 1 network round trip + 100 memory lookups
Total Latency = 0.5 ms + (100 * 100 ns) = 0.5 ms + 10 us = 0.51 ms
```
This calculation shows that using memory caching with pipelining is roughly 2,000 times faster than random disk reads. It explains why caching is the first tool engineers reach for to solve read latency issues.

## Pros
- **Clarity of purpose:** Clear functional requirements ensure the engineering team builds exactly what the business needs.
- **Improved scalability:** Performing early scale estimations helps choose partitioning keys and database technologies that avoid rebuilds.
- **Cost reduction:** Back-of-the-envelope calculations prevent over-provisioning expensive cloud hardware.
- **Faster debugging:** Separating HLD and LLD provides clear system boundaries, speeding up issue isolation when crashes occur.

## Cons
- **Analysis paralysis:** Teams can spend too much time estimating edge cases instead of writing prototype code.
- **Inaccurate assumptions:** Early estimations rely on user traffic assumptions that may turn out to be completely wrong.
- **Design overhead:** Maintaining separate HLD and LLD documentation takes time and resources away from feature delivery.
- **Fragile designs:** Over-optimizing for a specific initial scale estimate can make the architecture brittle when traffic patterns change.

## Alternatives
- **Prototyping first:** Instead of formal system design, teams build a minimal viable product (MVP) immediately. This is preferable in early-stage startups where market fit is unknown.
- **Monolithic default:** Build a simple single-server monolith first without worrying about microservices. This is better when the initial team is small and traffic is low.
- **Fully serverless architectures:** Rely completely on managed services like AWS Lambda and DynamoDB. This is preferable when you want to outsource operational scalability entirely, though it increases vendor lock-in.

## When to use it
- **Greenfield projects:** Use system design when launching a new service to establish clean boundary structures and data flows.
- **Scale transitions:** Use when an existing system reaches its scaling limits and needs to migrate from a monolith to a distributed architecture.
- **Technical interviews:** Use this structured process to demonstrate architectural thinking during software engineering hiring loops.

## When NOT to use it
- **Small utility tools:** Do not use full system design for internal scripts, command-line tools, or simple landing pages where simple code suffices.
- **High-uncertainty MVPs:** Avoid detailed design sessions for throwaway prototypes where the primary goal is validating customer interest rather than supporting scale.
- **Low-traffic monoliths:** If your system will only ever serve a few hundred requests a day, do not design for millions of concurrent users. It leads to wasted engineering hours.

## Key takeaways / mental model
The mental model of system design is one of deliberate trade-offs. You cannot optimize for every attribute simultaneously. Every technical choice (like choosing a database or introducing a cache) is a trade-off between complexity, latency, consistency, and cost. Always start by defining functional and non-functional requirements. Use back-of-the-envelope calculations to justify your choices, and let the latency numbers guide your architectural boundaries.

## Self-check questions
1. What is the fundamental difference between high-level design and low-level design, and which developers are the target audience for each?
2. Why is a random disk seek on an HDD so slow compared to a memory read, and how does this affect database index designs?
3. If a photo upload service receives 50 photos per second, and each photo averages 4 MB, how much raw storage is required per month?
4. Explain how a functional requirement differs from a non-functional requirement using a real-world example of an online shopping cart.
5. In your own words, outline the repeatable four-step design process and describe what can go wrong if you skip the first step.
6. Under what circumstances would you skip back-of-the-envelope estimation in favor of immediate prototyping?

## References
- System Design Guide for Software Professionals (Sinha & Chopra, Packt 2024), Chapter 1.
- Designing Data-Intensive Applications (Martin Kleppmann, O'Reilly 2017).
