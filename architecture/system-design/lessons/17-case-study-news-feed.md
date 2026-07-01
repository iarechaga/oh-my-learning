---
id: system-design/17
subject: system-design
title: "Case Study: News Feed and Timelines"
slug: case-study-news-feed
status: drafted
mastery:
seniority: senior
source: System Design Guide for Software Professionals (Sinha & Chopra), Chapters 11 and 12
prerequisites: [system-design/16, ddia/01, ddia/10, ddia/15]
created: 2026-06-30
updated: 2026-06-30
---

# Case Study: News Feed and Timelines

## TL;DR
Building a scalable news feed requires balancing read and write loads. We compare fan-out on write, where posts are pre-pushed to active follower timelines, against fan-out on read, which pulls and merges posts on demand. A hybrid system routes celebrity posts through a pull path while active users get a push path, ensuring low latencies for millions of concurrent feeds.

## The idea
The fundamental goal of a news feed system is to publish updates from followed entities into a consolidated stream for a user. In small applications, querying the database for a user's following list and pulling their latest posts is straightforward. When traffic scales, this read-heavy query becomes incredibly expensive and slow.

In systems with hundreds of millions of users, retrieving updates on demand triggers massive database scan operations. Every time a user refreshes their home feed, the system must fetch the followings list, query posts for all those accounts, sort them, and return the top results. This is known as fan-out on read. It places a severe load on the relational or document store, resulting in high read latencies.

To protect read latency, systems can precompute feeds by pushing new posts directly to each follower's pre-allocated timeline cache. This is known as fan-out on write. When a user posts an update, background workers find all their followers and append the new post ID to their cached feed arrays. Reading the timeline is then a fast, constant-time cache read. 

However, this approach breaks when a high-profile user with millions of followers posts. Pushing a single post to fifty million caches requires immense database and memory activity, which is known as the celebrity or hot-user problem. 

This case study designs a hybrid timeline architecture. We combine push and pull patterns to maintain fast home timeline reads while preventing celebrity write storms. Our approach directly applies concepts of load, scalability, stream processing, and partitioning from DDIA.

## How it works

### 1. Functional and Non-Functional Requirements

#### Functional Requirements:
* Users can publish posts containing text and media like images or videos.
* Users can view a chronological home timeline of posts from people they follow.
* Users can follow and unfollow other users.
* The system supports pagination when reading the timeline.

#### Non-Functional Requirements:
* **High Availability**: The timeline service must be highly available, prioritizing availability over strict consistency.
* **Low Read Latency**: Loading the home timeline must take less than 100 milliseconds for the 99th percentile (p99) of requests.
* **Acceptable Write Latency**: Publishing a post should feel instantaneous to the creator, with followers seeing it within 5 seconds.
* **Scale**: The architecture must support 100 million daily active users (DAU).

### 2. Back-of-the-Envelope Estimation

Let's establish our design scale with key metrics:
* Daily Active Users (DAU): 100,000,000 users.
* Read Volume: A user views their timeline 10 times per day.
  * Total daily timeline views: `100,000,000 * 10 = 1,000,000,000` views per day.
  * Average timeline read QPS: `1,000,000,000 / 86,400 seconds = 11,574` read QPS.
* Write Volume: A user posts an average of 1 time per day.
  * Total daily posts: `100,000,000 * 1 = 100,000,000` posts per day.
  * Average write QPS: `100,000,000 / 86,400 seconds = 1,157` write QPS.
  * Peak write QPS: 3,000 posts per second.
* Media Storage Estimates:
  * Assume 10% of posts contain an image, and 2% contain a video.
  * Average image size: 200 kilobytes.
  * Average video size: 3 megabytes.
  * Daily image storage: `10,000,000 * 200 KB = 2` terabytes per day.
  * Daily video storage: `2,000,000 * 3 MB = 6` terabytes per day.
  * Total new media storage: 8 terabytes per day.
* Memory Cache Estimates:
  * We cache the home timeline of active users only.
  * We define an active user as someone who logged in within the last 3 days (approx. 150 million users).
  * We cache the top 100 post IDs for each active timeline.
  * Each post ID is a 64-bit integer (8 bytes).
  * Total timeline cache memory: `150,000,000 * 100 * 8 bytes = 120` gigabytes of RAM. This is manageable on a small cluster of Redis nodes.

### 3. API Sketch

We define three core RESTful endpoints to handle post creation, feed retrieval, and social graph changes.

* `POST /v1/posts`: Create a new post.
  * Request payload:
    ```json
    {
      "text": "Hello world! This is my news feed post.",
      "media_ids": ["media_abc123"]
    }
    ```
  * Response:
    ```json
    {
      "post_id": "post_xyz789",
      "user_id": "usr_999",
      "created_at": 1782782400
    }
    ```

* `GET /v1/timelines/home`: Retrieve the user's home timeline.
  * Query parameters: `limit=20`, `cursor=post_98765` (for keyset pagination).
  * Response payload:
    ```json
    {
      "posts": [
        {
          "post_id": "post_xyz789",
          "user_id": "usr_999",
          "text": "Hello world!",
          "media_urls": ["https://cdn.example.com/media_abc123.jpg"],
          "created_at": 1782782400
        }
      ],
      "next_cursor": "post_abc456"
    }
    ```

* `POST /v1/users/{user_id}/follow`: Follow another user.
  * Request: empty payload.
  * Response: `{"status": "success"}`.

### 4. Data Model

To handle relations, posts, and timelines, we use a polyglot storage approach:

* **Social Graph Database**: Follow connections form a graph. A relational database with a composite primary key on a `follows` table works best.
  * Table `follows`: `follower_id` (VARCHAR), `followee_id` (VARCHAR), `created_at` (TIMESTAMP). We create a composite clustered index on `(follower_id, followee_id)` and a secondary index on `followee_id` to quickly fetch both followers and following lists.
* **Post Database**: Posts are write-once, read-heavy, and occasionally edited. A distributed NoSQL document store like Cassandra offers excellent scale.
  * Table `posts`: `post_id` (VARCHAR, Clustered Key), `user_id` (VARCHAR), `content` (TEXT), `media_links` (LIST[TEXT]), `created_at` (TIMESTAMP).
* **Home Timeline Cache**: Fast retrieval is paramount. We store user timelines in an in-memory database like Redis.
  * Data structure: Redis Sorted Set (ZSET). For each sorted set, the key is structured as `timeline:user_id`. Members within the set contain the `post_id` value, while scores are set to the epoch timestamp `created_at`. This structure allows fast pagination by score and quick insertion of new items.

We can visualize Cassandra's physical layout for posts, where `user_id` is the partition key and `post_id` acts as the clustering column:

```
 Cassandra Node (Partition Hash: usr_999 -> Token Range 45000-50000)
 +-------------------------------------------------------------------------+
 | Partition Key: usr_999                                                  |
 | +-----------------------+-------------------------+-------------------+ |
 | | Clustering Key: post_2 | content: "Another post" | media_links: []   | |
 | | Clustering Key: post_1 | content: "First post!"  | media_links: [url]| |
 | +-----------------------+-------------------------+-------------------+ |
 +-------------------------------------------------------------------------+
```

### 5. High-Level Architecture

The diagram below represents the flow of a new post and feed retrieval under our hybrid push-pull design:

```
                  +------------------+
                  |    Client App    |
                  +--------+---------+
                           |
            +--------------+--------------+
            |                             |
      (Write Post)                   (Read Timeline)
            v                             v
  +---------+--------+          +---------+--------+
  |   API Gateway    |          |   API Gateway    |
  +---------+--------+          +---------+--------+
            |                             |
            v                             v
  +---------+--------+          +---------+--------+
  |   Post Service   |          | Timeline Service |
  +----+--------+----+          +----+----+----+---+
       |        |                    |    |    |
       |  (Publish Event)            |    |    |
       v        v                    |    |    |
 +-----+--+  +--+-------+            |    |    |
 | DB/S3  |  | Message  |            |    |    v
 +--------+  | Broker   |            |    |  +-------------+
             +----+-----+            |    |  | Post DB /   |
                  |                  |    |  | Follow DB   |
                  v                  |    |  +-------------+
             +----+-----+            |    v
             | Fan-out  +------------+  +------------------+
             | Workers  | (Updates)     | Timeline Cache   |
             +----------+               | (Redis Cluster)  |
                                        +------------------+
```

Let's trace how the post-creation (write) and timeline-loading (read) paths behave in detail.

#### Post-Creation and Fan-Out Path (Write)
1. A user publishes a new post. The client uploads media to Amazon S3 (an object store) and sends metadata to the API Gateway.
2. The Post Service persists the record in the NoSQL Post Database and fires a `PostCreated` event into a message broker (Apache Kafka).
3. Fan-out workers consume this event. They query the Follow Database to fetch the author's followers.
4. If the author is a regular user, the workers append the new `post_id` to the Redis Sorted Sets of all active followers. This is the push path.
5. Celebrity authors (e.g. more than 10,000 followers) trigger a push-path skip. The event is ignored for follower caches, and the post is only saved in the main Post Database to prevent write storms.

#### Loading-Timeline Path (Read)
1. A user requests their home timeline.
2. The Timeline Service queries the Follow Database to get the list of followed users who are marked as celebrities.
3. Precomputed timeline lists containing post IDs from regular users are pulled from the Redis Sorted Set cache.
4. Simultaneously, the service queries the Post Database to get the latest posts from the followed celebrities. This is the pull path.
5. The service merges these two lists in memory, sorts them chronologically by timestamp, fetches the full post metadata, and returns the results.

### 6. How it Scales

#### Caching Strategy
Redis is the core of our timeline retrieval. We restrict the cached timeline to 100 posts per active user to conserve memory. If a user scrolls past 100 items, the Timeline Service falls back to querying the Post Database. 

To handle massive read traffic, we replicate our Redis cluster using a leader-follower pattern (DDIA Concept 05). All writes go to the Redis leaders, while reads are distributed across multiple read replicas.

#### Partitioning
Our databases are partitioned to distribute load (DDIA Concept 10).
* **Posts Table**: Partitioned by `user_id` using consistent hashing (DDIA Concept 10). This groups posts by the same author on the same database node, making bulk reads of a single user's posts extremely fast.
* **Follows Table**: Partitioned by `follower_id`. When a user requests their timeline, we can fetch all of their followings from a single database shard with a quick query.
* **Redis Cluster**: Partitioned by `user_id`. Each Redis node holds a subset of user timeline keys.

#### Stream Processing for Fan-out
We use stream processing concepts (DDIA Concept 15) to decouple post creation from fan-out delivery. When a post is created, the system publishes it to a Kafka topic. Multiple consumer groups read from this topic. 

One group handles push fan-out to Redis. Another group handles search indexing, and a third group updates user statistics. If the Redis cluster experiences high latency, Kafka buffers the events, preventing write failures in the Post Service.

#### Media Distribution
All media assets are served via a Content Delivery Network (CDN) such as Cloudflare or Amazon CloudFront. The Post Service stores original media files in an S3 bucket and returns signed CDN URLs to the client. CDNs cache media at edge locations close to users, reducing load on our servers and slashing image load times.

### 7. Bottlenecks and Edge Cases

#### How the Hybrid Handles a Celebrity
Let's consider a worked detail of our hybrid model in action. 

Suppose User A has 100 followers. User A posts an update. The fan-out worker finds 100 followers, and updates 100 Redis ZSET keys. This operation takes less than 10 milliseconds.

Now, suppose Celebrity B has 10,000,000 followers. Celebrity B posts an update. The system recognizes Celebrity B as a hot user. Background workers do nothing to followers' Redis caches. 

Instead, when Follower C (who follows both User A and Celebrity B) opens their app, the Timeline Service queries Redis for User A's post and reads Celebrity B's post from the database. The service merges both posts in memory. This avoids pushing Celebrity B's post to 10,000,000 Redis caches, shielding the cluster from memory and network exhaustion.

#### Inactive User Cache Eviction
If a user hasn't logged in for 3 days, their timeline is evicted from Redis. When they log in again, the Timeline Service detects a cache miss. It reads their followed accounts, queries the Post Database to construct their timeline, and populates the Redis cache.

#### Feed Ranking (Chronological vs Algorithmic)
While our primary design uses chronological sorting, real systems often use ranking models. To scale ranking, the system pre-ranks posts during fan-out using machine learning scoring. In our Redis ZSET, the score is set to the calculated feed rank score rather than the raw timestamp.

#### Keyset Pagination (Cursor-Based)
We use keyset pagination instead. Clients send a `cursor` parameter containing the timestamp and ID of the last viewed post. The service queries only the items older than the cursor, ensuring stable, constant-time database reads.

#### Unfollowing a Hot User
When Follower C unfollows Celebrity B, we must remove Celebrity B's posts from Follower C's view. Since celebrity posts are never pushed to Redis, we do not need to clean up Redis keys. The Follow Database simply removes the association. On the next read, the Timeline Service skips querying Celebrity B's posts entirely, and the change is reflected immediately.

## Pros
- **Low p99 Read Latency**: Most timeline reads are served directly from Redis, allowing sub-50ms feed load times.
- **Resilience to Celebrity Write Storms**: Celebrity posts bypass the push queue, keeping write traffic predictable even when major events happen.
- **Decoupled Architecture**: Message queues handle fan-out processing, which keeps the post-creation API fast and isolated from cache failures.

## Cons
- **Increased System Complexity**: Maintaining two separate paths requires sophisticated merge logic and monitoring.
- **Dual-Write Consistency Challenges**: It's possible for Redis timeline caches to fall out of sync with the main SQL follow tables during quick follow-unfollow actions.
- **Memory Overhead**: Caching precomputed timelines for hundreds of millions of active users requires substantial Redis RAM.

## Alternatives
- **Pure Fan-out on Read (Pull Model)**: All timelines are constructed dynamically at read time. This is much simpler to implement and uses zero Redis cache memory. However, read latency spikes dramatically as follow lists grow, making it unsuitable for high-read social networks.
- **Pure Fan-out on Write (Push Model)**: Every user post is pushed to all followers, including celebrities. This keeps the read path extremely simple because it's always a single Redis read. However, writing a post for a celebrity with 80 million followers takes minutes, causing extreme timeline delivery delays for followers.
- **Relational SQL Database with Heavy Indexing**: Running the system entirely on a single relational database cluster. This reduces data duplication but cannot scale to the write and read QPS of modern social media networks.

## When to use it
- High-volume social networking platforms like Twitter, Threads, or Instagram where read traffic is orders of magnitude larger than write traffic.
- Systems with an extreme asymmetry in follower counts, where some users have millions of followers and others have very few.
- Applications that require highly predictable, low-latency rendering of home timelines.

## When NOT to use it
- Standard enterprise applications or blogs where users only follow a handful of channels and real-time feeds aren't a core feature.
- Low-latency chat applications, where direct message delivery mechanics are a better fit than timeline caches.
- Pure chronological logging systems, where distributed query engines or search indexes are more appropriate.

## Key takeaways / mental model
A news feed is a classic read-versus-write trade-off (DDIA Concept 01). Precomputing feeds during the write phase (push) guarantees lightning-fast reads. However, hot spots (celebrities) force a shift back to on-demand computation (pull). Think of the hybrid news feed as a system that pushes when it is cheap and pulls when push becomes too expensive.

## Self-check questions
1. Why does the pure fan-out on write (push) model fail when a celebrity posts a new status?
2. How does keyset (cursor-based) pagination prevent duplicated posts when scrolling through an active feed?
3. Where is the data partitioned in our hybrid news feed, and why do we partition posts and follows differently?
4. What happens when an inactive user logs back in after several weeks of absence?
5. How would you modify the Redis Sorted Set score to support algorithmic feed ranking instead of simple reverse-chronological order?
6. Under what circumstances would a fan-out worker queue back up, and how does Kafka protect the system during such spikes?

## References
- Sinha, D. & Chopra, T. (2024). *System Design Guide for Software Professionals*, Chapters 11 and 12. Packt Publishing.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*, Chapter 1 (Twitter Home Timeline case study), Chapter 6 (Partitioning), and Chapter 11 (Stream Processing). O'Reilly Media.
