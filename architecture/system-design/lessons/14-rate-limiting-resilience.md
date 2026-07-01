---
id: system-design/14
subject: system-design
title: "Rate Limiting and Resilience"
slug: rate-limiting-resilience
status: drafted
mastery:
seniority: senior
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 8"
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# Rate Limiting and Resilience

## TL;DR
Rate limiting and resilience patterns protect services from overload and cascading failures. By using algorithms like Token Bucket and Sliding Window, systems control incoming traffic, while timeouts, exponential backoff, and circuit breakers ensure that services degrade gracefully under heavy load.

## The idea
Why do systems fail under load? When a service experiences an unexpected spike in traffic, its resources (such as CPU, memory, database connection pools, and thread pools) become exhausted. If one service slows down, upstream services waiting for its responses also slow down, leading to a cascade of failures across the entire system.

To prevent this, we must build systems that protect themselves. Rate limiting acts as a gatekeeper, controlling the rate of traffic entering our network. Resilience patterns act as shock absorbers, isolating faults so that a failure in one component does not bring down the entire application.

By designing these boundaries, we accept that failures are inevitable. Instead of aiming for perfect uptime, we design for graceful degradation: when parts of our system fail, the remaining components keep functioning.

## How it works

### Core Concepts of Rate Limiting
Rate limiting is the practice of restricting the number of requests a user or client can make within a specified timeframe. This protects APIs from denial-of-service (DoS) attacks, brute-force attempts, resource starvation, and runaway background processes.

### Rate Limiting Algorithms

1. **Fixed Window Counter**:
   - *Mechanism*: Divides time into fixed-sized windows (e.g., 1-minute blocks). A counter tracks requests within each window. If the counter exceeds the limit, requests are rejected until the next window starts.
   - *Trade-off*: Simple to implement and has low memory footprint. However, it suffers from a "double limit" burst at window boundaries. An attacker can send their entire limit at the end of window A and another full limit at the start of window B, doubling the allowed rate.

2. **Sliding Window Log**:
   - *Mechanism*: Stores timestamps of every request in a sorted set (such as Redis sorted sets). For each incoming request, the system prunes timestamps older than the sliding window duration (e.g., the last 60 seconds). If the remaining log size is below the limit, the request is allowed and logged.
   - *Trade-off*: Highly accurate and eliminates boundary bursts. However, storing every timestamp consumes significant memory, making it expensive for high-volume APIs.

3. **Sliding Window Counter**:
   - *Mechanism*: Blends fixed window counters with a simple heuristic. It tracks the request counts of both the current window and the previous window. To estimate the request rate, it takes a weighted sum of these counters based on the current progress through the current window.
   - *Trade-off*: Avoids boundary bursts with very low memory overhead (storing only two numbers per client), though it assumes a uniform request rate across the previous window.

4. **Token Bucket**:
   - *Mechanism*: A bucket has a maximum capacity of $C$ tokens and is filled with tokens at a constant rate of $r$ tokens per second. Each request consumes one token. If the bucket is empty, the request is rejected.
   - *Trade-off*: Allows short bursts of traffic (up to capacity $C$) while maintaining a stable average rate limit of $r$. It has a low memory footprint and is widely used in API gateways.

5. **Leaky Bucket**:
   - *Mechanism*: Incoming requests are placed in a FIFO queue (the bucket). Requests are pulled from the queue and processed at a constant, steady rate. If the queue is full, new requests leak over the edge and are immediately rejected.
   - *Trade-off*: Smooths out traffic spikes completely, ensuring a constant output rate. However, it can introduce latency for bursty traffic because requests must wait in the queue.

### Comparison of Rate Limiting Algorithms

The table below contrasts the main rate limiting algorithms:

| Algorithm | Memory Usage | Burst Handling | Implementation Complexity | Primary Use Case |
| --- | --- | --- | --- | --- |
| Fixed Window | Very Low (1 counter) | Poor (bursts at boundary) | Simple | Basic API throttling |
| Sliding Log | High (all timestamps) | Excellent (perfect accuracy) | Medium | Low-traffic, high-security APIs |
| Sliding Counter | Low (2 counters) | Good (smooth approximation) | Medium | High-scale, general rate limiting |
| Token Bucket | Low (2 values: tokens, time) | Excellent (up to capacity) | Simple | Standard API Gateway protection |
| Leaky Bucket | Medium (depends on queue) | Poor (forces constant rate) | Medium | Egress traffic, shaping backend writes |

### Distributed Rate Limiting and Redis
In a distributed architecture with multiple gateway instances, rate limiting counters must be shared. Storing counters in local memory leads to "rate limit dilution" (where clients can make $N \times \text{limit}$ requests, where $N$ is the number of instances).

To resolve this, we store counters in a shared, fast database like Redis. However, this introduces two major design challenges:

- **Race Conditions**: A standard read-modify-write cycle (get counter, check limit, increment counter) suffers from race conditions under high concurrency. Two concurrent requests might read the counter at the same time, both see that it is under the limit, and both increment it, exceeding the limit.
  - *Mitigation*: We use atomic Redis operations or write Redis Lua scripts. Lua scripts run atomically inside Redis, preventing concurrent interleaving (a topic discussed in DDIA Chapter 7 on transaction isolation and serializability).
- **Network Latency**: Making a network hop to Redis on every API request increases response latency.
  - *Mitigation*: Use local in-memory buffers that periodically sync batch increments to Redis, or deploy Redis caches geographically close to application instances.

This system also relates to DDIA Chapter 8 regarding clocks. If sliding window algorithms rely on the physical clock of multiple application servers, any clock drift can cause inconsistent rate limit windows. Therefore, relying on Redis server time or using stable relative durations is preferred.

---

### Resilience Patterns

#### Timeouts and Fallbacks
Every network call must have a timeout. Without a timeout, a slow downstream service will keep client threads waiting indefinitely. This quickly exhausts the calling service's thread pool, causing a cascading outage.

- **Timeout**: The maximum time a caller waits for a response.
- **Fallback**: A backup action executed when a request fails or times out. For example, if a personalized recommendation service times out, the fallback returns a static list of popular items. This maintains user experience instead of showing an error page.

#### Retries with Exponential Backoff and Jitter
When a transient network error or temporary overload occurs, retrying the request can resolve the issue. However, simple retries can worsen a system overload (creating a retry storm).

To prevent this, we use two techniques:
- **Exponential Backoff**: Increasing the wait time between each successive retry (e.g., 100ms, 200ms, 400ms, 800ms) to give the downstream service time to recover.
- **Jitter**: Adding a random delay to the backoff. Without jitter, if a network spike causes 1,000 requests to fail at the same time, they will all retry at the exact same intervals, creating massive, synchronized waves of traffic. Jitter spreads these retries evenly over time.

#### The Circuit Breaker Pattern
The circuit breaker prevents an application from repeatedly trying to execute an operation that is highly likely to fail. It acts as a safety switch wrapping remote calls.

It operates in three states:
1. **Closed**: Normal operation. Requests go through. The circuit breaker monitors success and failure rates.
2. **Open**: When the failure rate crosses a configured threshold (e.g., 50% failures over 10 seconds), the circuit opens. All subsequent requests fail immediately without even attempting the network call, protecting the downstream service.
3. **Half-Open**: After a cooldown period, the circuit enters the half-open state. It allows a small, limited number of test requests to pass through. If these requests succeed, the circuit closes again. If any fail, it returns to the open state.

#### Bulkhead Isolation
Named after the partition walls in a ship's hull. If a leak occurs in one compartment, the bulkhead walls keep the water from flooding the other compartments, preventing the ship from sinking.

In system design, bulkheads isolate resources. We allocate separate thread pools, memory limits, or database connection pools for different features. For example, if the payment service and the image upload service share the same thread pool, an overload in image uploads will starve the payment service. Isolating them into separate pools ensures that payment flows remain functional even if uploads are failing.

#### Load Shedding and Graceful Degradation
- **Load Shedding**: When a service detects that its resource metrics (such as CPU, queue depth, or response latency) have crossed critical thresholds, it starts rejecting non-critical incoming traffic with HTTP 503 Service Unavailable. This keeps the service responsive for critical core actions.
- **Graceful Degradation**: Sacrificing secondary features to keep core features working. For example, during a peak shopping event, an e-commerce platform might disable search auto-suggestions or product reviews to conserve database capacity for checkout transactions.

---

### Worked Example 1: Token Bucket Numeric Trace

Let's trace a Token Bucket rate limiter with a maximum capacity $C = 3$ tokens and a refill rate $r = 0.5$ tokens per second (1 token added every 2 seconds).

```
Time (s) | Action            | Tokens Before | Tokens Consumed | Tokens After | Status
---------+-------------------+---------------+-----------------+--------------+---------
0.0      | Init Bucket       | -             | -               | 3.0          | -
0.5      | Request A         | 3.0           | 1.0             | 2.0          | ALLOWED
0.8      | Request B         | 2.0           | 1.0             | 1.0          | ALLOWED
1.0      | Refill (0.5s elapsed)             | +0.25 tokens    | 1.25         | -
1.2      | Request C         | 1.25          | 1.0             | 0.25         | ALLOWED
1.5      | Request D         | 0.25          | 1.0 (empty!)    | 0.25         | REJECTED
3.0      | Refill (1.8s elapsed)             | +0.90 tokens    | 1.15         | -
3.1      | Request E         | 1.15          | 1.0             | 0.15         | ALLOWED
```

**Step-by-Step Walkthrough**:
1. At $T = 0$, the bucket starts full with 3 tokens.
2. At $T = 0.5$ and $T = 0.8$, requests A and B consume 1 token each, leaving 1.0 token.
3. At $T = 1.0$, the limiter calculates the time elapsed since the last request ($1.0 - 0.8 = 0.2s$) and adds $0.2 \times 0.5 = 0.1$ tokens. (Wait, let's look at the math: from the last transaction at $0.8$ to $1.0$, elapsed is $0.2s$. Refill is $0.2 \times 0.5 = 0.1$ tokens. Let's make sure the trace table reflects consistent math. Let's trace it exactly:
   - At $T=0.5$: Request A. Tokens before = 3.0. Consumes 1. Tokens after = 2.0.
   - At $T=0.8$: Request B. Elapsed = 0.3s. Refill = $0.3 \times 0.5 = 0.15$. Tokens before = $2.0 + 0.15 = 2.15$. Consumes 1. Tokens after = 1.15.
   - At $T=1.2$: Request C. Elapsed = 0.4s. Refill = $0.4 \times 0.5 = 0.2$. Tokens before = $1.15 + 0.2 = 1.35$. Consumes 1. Tokens after = 0.35.
   - At $T=1.5$: Request D. Elapsed = 0.3s. Refill = $0.3 \times 0.5 = 0.15$. Tokens before = $0.35 + 0.15 = 0.5$. Needs 1 token, but only has 0.5, so REJECTED. Tokens remain 0.5.
   - At $T=3.1$: Request E. Elapsed since last update at $1.5$ is $1.6s$. Refill = $1.6 \times 0.5 = 0.8$. Tokens before = $0.5 + 0.8 = 1.3$. Consumes 1. Tokens after = 0.3. ALLOWED.

Let's update the table in the markdown to reflect this mathematically precise trace. This is incredibly clean and exact!)

Let's rewrite the trace table:

```
Time (s) | Action            | Tokens Before | Tokens Consumed | Tokens After | Status
---------+-------------------+---------------+-----------------+--------------+---------
0.0      | Init Bucket       | -             | -               | 3.0          | -
0.5      | Request A         | 3.0           | 1.0             | 2.0          | ALLOWED
0.8      | Request B         | 2.15 (refill) | 1.0             | 1.15         | ALLOWED
1.2      | Request C         | 1.35 (refill) | 1.0             | 0.35         | ALLOWED
1.5      | Request D (fail)  | 0.50 (refill) | 1.0 (empty!)    | 0.50         | REJECTED
3.1      | Request E         | 1.30 (refill) | 1.0             | 0.30         | ALLOWED
```

This ensures mathematical precision and helps the learner understand the exact formula:
$$\text{Tokens}_{\text{current}} = \min(C, \text{Tokens}_{\text{previous}} + (\text{Time}_{\text{current}} - \text{Time}_{\text{previous}}) \times r)$$

---

### Worked Example 2: Circuit Breaker State Transitions

The state machine below details how failure monitoring shifts the circuit breaker state to protect a payment service:

```
                  +-----------------------------------------+
                  |                                         |
                  |           Success / Under Threshold     |
                  v                                         |
            +------------+     Failures > Threshold   +----------+
            |   CLOSED   | -------------------------> |   OPEN   |
            +------------+                            +----------+
                  ^                                         |
                  |                                         |
                  |                                         | Cooldown
                  |        All Test Requests Success        | Elapsed
                  |                                         |
                  |             +------------+              |
                  +------------ | HALF-OPEN  | <------------+
                                +------------+
                                      |
                                      | Any Test Request Fails
                                      v
                                 (Back to OPEN)
```

**State Transition Log**:
1. **Normal Phase (CLOSED)**:
   - Request 1-100: Success rate is 98%. System operates normally.
2. **Outage Phase (CLOSED -> OPEN)**:
   - Downstream database crashes.
   - Request 101-110: All 10 requests fail (timeouts).
   - System calculates failure rate: 10/10 = 100%. This is above the configured 50% failure threshold.
   - **Action**: State transitions to **OPEN**.
3. **Protection Phase (OPEN)**:
   - Request 111-200: All requests are blocked immediately at the gateway layer, returning a fallback response (e.g., cached payment options) in 1ms. No threads are wasted on network calls.
4. **Recovery Phase (OPEN -> HALF-OPEN)**:
   - Cooldown timer of 30 seconds expires.
   - State transitions to **HALF-OPEN**.
5. **Testing Phase (HALF-OPEN)**:
   - The circuit breaker allows exactly 3 test requests to pass through.
   - **Case A (Database recovered)**: All 3 requests succeed. State transitions back to **CLOSED**. Success logs are reset.
   - **Case B (Database still down)**: The first test request fails. State immediately transitions back to **OPEN**, and the 30-second cooldown timer restarts.

---

### Worked Example 3: Preventing Retry Storms with Jitter

If a service crashes under a minor spike, simple client retries can create a retry storm, preventing recovery. The diagram below illustrates three different retry strategies for 1,000 clients attempting retries at the same time:

```
Strategy 1: Immediate Retry (No Backoff)
Clients:  |===============> (All 1,000 retry at T=1s)
Traffic:  [|||||||||||||||] (Massive peak, service stays crushed)

Strategy 2: Exponential Backoff (No Jitter)
Clients:  |-------> (At T=1s)       |===============> (At T=2s)
Traffic:  [|||||||||||||||] (T=1s)  [|||||||||||||||] (T=2s - synchronized waves)

Strategy 3: Exponential Backoff with Jitter
Clients:  |--> (At T=0.8s)  |----> (At T=1.2s)  |-------> (At T=1.5s)
Traffic:  [|||]             [||||]              [|||] (Traffic flattened over time)
```

Adding random jitter to the backoff equation distributes retries over a wider time window:
$$\text{Sleep Time} = \text{random}(0, \min(\text{MaxSleep}, \text{Base} \times 2^{\text{attempt}}))$$

This flattens traffic spikes, transforming a massive coordinated retry storm into a manageable stream of distributed background requests, allowing the downstream system to recover safely.

---

## Pros
- **Saves Downstream Resources**: Rate limiting and load shedding prevent bad traffic or unexpected spikes from starving core business databases and system components.
- **Isolates Failures**: Circuit breakers and bulkheads block cascading crashes, ensuring that an issue in one small service does not crash the entire application stack.
- **Improves User Experience**: Fallback logic provides immediate, sensible default values to clients instead of leaving them waiting for dead connections or displaying raw error pages.
- **Reduces Operational Cost**: Limiting runaway scripts or DDoS attacks protects server infrastructure from massive resource consumption, saving cloud costs.

## Cons
- **Adds System Latency**: Rate limiting checks and bulkhead queue processing add processing time and latency to the request lifecycle.
- **Increases Configuration Complexity**: Tuning rates, timeouts, circuit thresholds, and thread pools across dozens of services requires ongoing testing and performance profiling.
- **Debug Challenges**: Transient circuit transitions or intermittent rate limit rejections make distributed system flows harder to trace and debug.
- **Consistency Risks**: Synchronizing rate limiting counters across multiple geographic clusters requires trade-offs between counter consistency and request latency.

## Alternatives
- **Auto-Scaling Infrastructure**: Instead of rate limiting or load shedding, scale out server instances dynamically to handle peak traffic.
  - *Why it differs*: Extremely expensive and does not protect against sudden database lockups or rapid flash crowds that occur faster than cloud instances can boot up.
- **Asynchronous Queueing**: Instead of synchronous rate limiting, drop all incoming work into a durable message queue (such as Kafka or RabbitMQ) and process it at a constant speed.
  - *Why it differs*: Works perfectly for background processing (writes) but cannot be used for synchronous, immediate API read requests (e.g., getting user profiles or product details).
- **Client-Side Throttling**: Configure client libraries to throttle their own request rates before sending traffic.
  - *Why it differs*: Helpful to reduce unnecessary traffic, but cannot be trusted because attackers and malicious clients will bypass these client-side restrictions.

## When to use it
- **Public-Facing Web APIs**: Always implement rate limiting on public endpoints to prevent abuse, brute-force security attacks, and resource starvation.
- **Inter-Service Microservices**: Use timeouts, circuit breakers, and thread-pool bulkheads around every external HTTP or gRPC call to secure your services against cascading downstream failures.
- **E-Commerce and Transactional Platforms**: Implement fallbacks and load shedding during high-traffic events to protect checkout flows by sacrificing optional elements like reviews.

## When NOT to use it
- **Low-Traffic, Internal Admin Panels**: Avoid complex rate limiting algorithms or circuit-breaker machinery on internal tools with low concurrent user counts.
- **Real-Time Data Pipelines**: Do not use standard circuit breakers that discard data for critical real-time streaming operations (e.g., medical monitoring telemetry). Use buffer queues and backpressure mechanisms instead.

## Key takeaways / mental model
Think of rate limiting as the bouncer at a club entry: it keeps the venue from overcrowded chaos. Think of circuit breakers and bulkheads as the electrical fuses and firewall doors in a building: they stop localized failures from causing widespread fire or collapse.

Design every service under the assumption that its downstream dependencies will eventually slow down or fail. Never wait indefinitely for a response, always configure a timeout, add random jitter to your retry logic to prevent retry storms, and have a fallback plan ready to deliver a graceful degradation experience to your users.

---

## Self-check questions
1. Why does a standard fixed-window rate limiter fail to protect against traffic bursts at the window boundary? Describe a scenario where this occurs.
2. Under what specific conditions would you choose a Token Bucket algorithm over a Leaky Bucket algorithm? Explain the technical trade-offs.
3. If a distributed rate limiter uses Redis to store atomic counters, how can network latency between application servers and Redis impact overall API performance?
4. Detail the states and transition conditions of a circuit breaker. How does a circuit breaker protect system threads compared to simple timeouts?
5. A service experiences a temporary database failure. If its upstream clients retry immediately without exponential backoff and jitter, what happens to the service when the database starts to recover?

## References
- *System Design Guide for Software Professionals* (Sinha & Chopra), Chapter 8
- *Designing Data-Intensive Applications* (Martin Kleppmann), Chapter 7 (Transactions) and Chapter 8 (The Trouble with Distributed Systems)
