---
id: system-design/16
subject: system-design
title: "A System-Design Method (URL Shortener)"
slug: design-method-url-shortener
status: drafted
mastery: 
seniority: mid
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapters 9, 15, 16"
prerequisites: [system-design/01]
created: 2026-06-30
updated: 2026-06-30
---

# A System-Design Method (URL Shortener)

## TL;DR
We can solve highly ambiguous system design problems using a repeatable, structured framework. Applying this method to a URL shortener teaches us how to balance read-heavy caching, sharding, and unique key generation. This practical approach forms a solid blueprint for designing large-scale web services.

## The idea
System design questions in interviews or real-world projects often begin with a single, highly ambiguous sentence. An engineer might be asked to design a platform like YouTube, Twitter, or a URL shortener without any further context. Starting without a plan leads to chaotic discussions, missed edge cases, and architectural dead ends.

This lesson introduces a repeatable, eight-step system-design method. We apply this method to a classic problem: designing a URL shortener. The system appears simple on the surface, yet it exposes fundamental challenges in high-throughput traffic, storage scaling, and unique key allocation. By working through this example, you will learn a structural checklist that you can apply to any complex design task.

## How it works
A systematic approach turns chaotic requirements into a working architecture. The checklist contains eight distinct phases, which we will apply to our URL shortener.

### The System-Design Checklist
Here is the general method you can apply to any design:
1. Clarify requirements and define system scope.
2. Estimate scale, QPS, bandwidth, and storage.
3. Design API endpoints to establish the service contract.
4. Establish the data model and choose storage technologies.
5. Sketch the high-level architecture.
6. Identify and solve core technical challenges.
7. Scale the architecture to handle traffic and data growth.
8. Resolve bottlenecks, edge cases, and operational concerns.

---

### Step 1: Clarification and Scope Definition
Never design a system based on assumptions. We must ask questions to clarify functional and non-functional requirements.

#### Functional Requirements
- The system must take a long URL and return a unique, short URL.
- When a user accesses the short URL, the system must redirect them to the original long URL.
- Users can optionally specify a custom alias for their short URL.
- The default expiration time for shortened links is five years.

#### Non-Functional Requirements
- The service must be highly available. Redirection failures directly impact user experience.
- Redirection latency must be under 100 milliseconds.
- Shortened keys must be unpredictable to prevent malicious users from scanning all active links.

#### Out of Scope
- User account creation, billing, and advanced click analytics dashboards are out of scope for this initial design phase.

---

### Step 2: Back-of-the-Envelope Estimation
Now we estimate the demands on our system. We assume a write-heavy or read-heavy distribution to size our infrastructure. For details on how to perform these calculations, refer to [01-fundamentals.md](01-fundamentals.md).

#### Assumptions
- New URLs shortened per day: 100 million.
- Read to write ratio: 100 to 1. This is a highly read-heavy system.

#### Query Per Second (QPS)
- New URLs per second (Writes): 100,000,000 / 86,400 seconds = ~1,157 writes/sec.
- URL redirections per second (Reads): 1,157 * 100 = 115,700 reads/sec.

#### Storage Estimation
- We assume each database entry takes up roughly 500 bytes. This includes the original URL, the shortened key, creation time, expiration time, and metadata.
- Daily storage growth: 100,000,000 * 500 bytes = 50,000,000,000 bytes (50 GB per day).
- Yearly storage requirement: 50 GB * 365 days = 18.25 TB per year.
- Five-year storage capacity: 18.25 TB * 5 = 91.25 TB.

#### Bandwidth Estimation
- Write ingress bandwidth: 1,157 writes/sec * 500 bytes = 578.5 KB/sec.
- Read egress bandwidth: 115,700 reads/sec * 500 bytes = 57.85 MB/sec.

#### Cache Memory Requirements
We apply the 80:20 rule, assuming 20% of the daily URLs generate 80% of the read traffic. Our goal is to cache these hot links.
- Daily reads cover 10 billion redirections. If we cache 20% of the daily created URLs, we need to store 20 million URLs.
- Memory size required: 20,000,000 * 500 bytes = 10 GB of RAM. This is easily managed by a single modern caching node.

---

### Step 3: API Design
We establish the system contract using REST endpoints. This defines how client applications interact with our service.

#### 1. Create a Short URL
- **HTTP Method**: POST
- **Endpoint**: `/api/v1/shorten`
- **Request Body** (JSON):
```json
{
  "longUrl": "https://example.com/very/long/path/to/some/resource",
  "customAlias": "my-custom-alias",
  "expiryDate": "2031-06-30T00:00:00Z"
}
```
- **Response Body** (JSON):
```json
{
  "shortUrl": "https://sh.rt/xyz1234",
  "customAlias": "my-custom-alias",
  "expiryDate": "2031-06-30T00:00:00Z"
}
```

#### 2. Redirect a Short URL
- **HTTP Method**: GET
- **Endpoint**: `/{shortKey}`
- **Response**: HTTP 302 Redirect with the `Location` header containing the original long URL.

---

### Step 4: Data Model
We need to persist mappings between short keys and original long URLs.

#### Database Choice
We have two main choices: Relational (RDBMS) or NoSQL. Traditional relational databases like PostgreSQL can handle this mapping, but scaling them to store billions of records requires complex sharding. Choosing a NoSQL wide-column database like Cassandra is a better fit because it scales horizontally, offers sub-millisecond lookups, and doesn't require complex relations.

#### Database Schema
Our primary table mapping the keys can look like this:

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| **short_key** (Primary Key) | VARCHAR(7) | The unique generated short key. |
| **original_url** | VARCHAR(2048) | The original target URL. |
| **user_id** | VARCHAR(64) | Optional identifier for the owner. |
| **created_at** | TIMESTAMP | The creation timestamp. |
| **expires_at** | TIMESTAMP | The expiration timestamp. |

---

### Step 5: High-Level Architecture
The high-level architecture separates the write path from the read path.

```
                  [ Clients ]
                   |      |
        (Write:    |      | (Read:
         Shorten)  v      v  Redirect)
          +------------------------+
          |     Load Balancer      |
          +------------------------+
               |              |
               v              v
         +-----------+  +-----------+
         | Write API |  | Read API  |
         |  Servers  |  |  Servers  |
         +-----------+  +-----------+
            |      |       |      ^
            |      |       |      | (Cache Hit)
            |      |       v      |
            |      |    +------------+
            |      |    | Memory     |
            |      |    | Cache      |
            |      |    +------------+
            |      |       ^ (Cache Fill on Miss)
            v      v       |
         +-----------+-----+
         | Unique    |
         | Key Gen   |
         | Service   |
         +-----------+
            |
            v
         +------------+
         | NoSQL DB   |
         | (Cassandra)|
         +------------+
```

1. Clients send requests to the Load Balancer.
2. Write Requests go to the Write API Servers. These servers request a unique key, write the mapping to the database, and return the short URL.
3. Read Requests go to the Read API Servers. These servers check the Memory Cache first.
4. If a cache miss occurs, the Read Server fetches the mapping from the NoSQL Database, populates the cache, and redirects the client.

---

### Step 6: Core Challenge — Unique Key Generation
The central engineering problem is generating a unique, short, and unpredictable key for each long URL.

#### Key-Length Math
We decided on Base62 encoding, using the set `[a-zA-Z0-9]`. Let's calculate the capacity for different key lengths:
- Length 6: 62^6 = 56,800,235,584 (56.8 billion) unique keys.
- Length 7: 62^7 = 3,521,614,606,208 (3.52 trillion) unique keys.
With 100 million writes per day, length 7 keys will easily last for nearly a century. We will use a 7-character key length.

#### Option A: Hashing and Collision Handling
We can hash the original long URL using MD5 or SHA-256, then encode the hash using Base62.
- MD5 produces a 128-bit hash. Base62 encoding of a 128-bit value yields a string of about 21 characters.
- We only need the first 7 characters.
- **The Problem**: Truncating the hash increases the chance of collisions. Two different long URLs might produce the same first 7 characters.
- **The Solution**: If a collision occurs, we must append a random string or counter to the original URL and rehash. This requires checking the database on every write, adding database read latency.

#### Option B: Counter and Base62 Encoding
Instead of hashing, we use a central counter that starts at 1,000,000,000. For each new URL, we increment the counter and convert the integer to a Base62 string.
- This approach guarantees no collisions. We don't need to query the database during writes to verify uniqueness.
- To prevent a single counter from becoming a bottleneck or single point of failure, we use a Key Generator Service (KGS).
- **The Problem**: The KGS is a single point of failure.
- **The Solution**: We can run multiple KGS nodes and allocate ranges of keys to each node. Each node loads a batch of keys into memory.
- If a KGS node crashes, we lose its in-memory batch. However, because our key space is vast (3.52 trillion keys), losing a few million keys is acceptable.

---

### Step 7: Scaling the Architecture
A single database or server cannot handle 115,700 reads per second and 91 TB of data. We must partition our resources.

#### Caching and Content Delivery Networks (CDNs)
- We deploy an in-memory cache layer using Redis or Memcached. Popular links are served directly from cache, avoiding database lookups. Integrating CDNs caches redirections closer to users geographically. Edge nodes handle the HTTP 302 redirect, reducing latency to single-digit milliseconds.

#### Sharding the Key Space
- We partition our wide-column database to distribute storage and load. Sharding by the hash of the `short_key` is the most effective approach. The hash of the `short_key` determines which database node stores the record. This creates an even distribution of writes and reads across the cluster.

#### Database Replication
- We use a leader-follower replication model. Write operations go to the leader node, which synchronizes updates with followers. Read operations are distributed across multiple follower replicas. This handles the read-heavy traffic and provides high availability.

---

### Step 8: Bottlenecks and Edge Cases

#### 301 vs 302 Redirects
We must choose the right HTTP status code:
- **301 Moved Permanently**: The browser caches this redirect. Subsequent clicks don't hit our servers, reducing our load.
- **302 Found (Temporary Redirect)**: The browser doesn't cache this redirect. Every click hits our servers. This is necessary if we want to track accurate click analytics or implement dynamic link expiration.
We will use HTTP 302 to support link expiration and analytics tracking.

#### Custom Aliases
- Users can choose custom keys, like `sh.rt/my-promo`.
- When a user requests a custom alias, the API server must verify that the key doesn't exist in the database. If the alias is free, we write it immediately to lock it. This operation bypasses the Key Generator Service.

#### Expiry and Background Cleanup
- We run a daily background cleanup job to delete expired links. Removing old keys frees up storage and allows us to recycle keys if needed. Querying a database of 100 billion records to find expired entries is slow. To speed this up, we index the database by the expiration timestamp or use Cassandra's Time-To-Live (TTL) feature to let records expire automatically.

#### Analytics and Click Tracking
- High-volume click tracking can overwhelm the database. Instead of writing directly to the database on every read, we push click events to a message queue like Apache Kafka. Downstream consumer services process these events in batches, updating a separate data warehouse for analytics.

## Pros
- Highly predictable scaling using pre-allocated keys, avoiding collision checks.
- Extremely low redirection latency due to aggressive edge caching and CDN distribution.
- Simple, horizontally scalable data model using NoSQL wide-column stores.
- Clear separation of read and write paths prevents write spikes from slowing down redirections.

## Cons
- The Key Generator Service introduces synchronization overhead and memory state management.
- Pre-allocated keys are wasted if the database runs out of space or keys are lost during server crashes.
- Tracking accurate click analytics requires a separate message queuing infrastructure to prevent write bottlenecks.
- Serving temporary redirects (HTTP 302) increases the load on our servers compared to permanent redirects (HTTP 301).

## Alternatives
- **Zookeeper-based Range Allocations**: Use Apache Zookeeper to distribute token ranges to API servers. This avoids a separate KGS by letting API servers generate keys locally using counters. It is highly reliable but increases infrastructure complexity.
- **Base62 Hashing with On-Collision Retry**: Generate short keys by hashing the original URL and encoding it in Base62. When a collision occurs, append a counter and retry. This avoids running a KGS entirely, but it introduces extra database reads during link creation.

## When to use it
- High-throughput public link sharing platforms like Bitly or TinyURL.
- Enterprise applications requiring trackable marketing links and dynamic redirect behavior.
- Internal company services that need short, predictable URLs for system-to-system communications.

## When NOT to use it
- Private, low-volume bookmarking tools where scaling is not a concern. A simple relational database with auto-incrementing IDs is sufficient here.
- High-security environments where redirecting through a third-party service exposes sensitive URL query parameters. Use direct, peer-to-peer redirection or encrypted links instead.

## Key takeaways / mental model
A structured system-design method breaks an open-ended problem into logical, sequential steps. When designing a URL shortener, the main challenge is managing a high read-to-write ratio and generating unique keys. Pre-generating keys using a Key Generator Service eliminates database read checks on write paths. Serving redirects with HTTP 302 enables tracking but requires a caching layer to keep redirection latency low.

## Self-check questions
1. Why does a URL shortener benefit more from an HTTP 302 redirect than an HTTP 301 redirect?
2. How does the Key Generator Service (KGS) prevent write-path bottlenecks compared to hashing methods?
3. What is the database storage capacity if we choose a 6-character Base62 key instead of a 7-character key?
4. How do we ensure that two users trying to claim the same custom alias at the same moment don't both succeed?
5. Why is sharding by the hash of the short key better than sharding by user ID in this architecture?
6. If a KGS node fails, what happens to the keys loaded in its memory? How does the system handle this failure?
7. How does a lazy deletion strategy help prevent database performance degradation when cleaning up expired records?

## References
- *System Design Guide for Software Professionals*, Sinha & Chopra, Packt 2024, Chapters 9, 15, 16.
- URL Shortener System Design, Sibling Lesson 01: [01-fundamentals.md](01-fundamentals.md).
