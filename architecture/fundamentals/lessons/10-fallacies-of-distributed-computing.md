---
id: fundamentals/10
subject: fundamentals
title: Fallacies of Distributed Computing
slug: fallacies-of-distributed-computing
status: drafted
mastery:
seniority: mid
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 10
prerequisites: [fundamentals/09]
created: 2026-06-30
updated: 2026-06-30
---

# Fallacies of Distributed Computing

## TL;DR
Coined by L. Peter Deutsch and others at Sun Microsystems, the eight fallacies of distributed computing are false assumptions that developers and architects make when transitioning from monolithic to distributed systems. Ignoring these fallacies leads to fragile designs, unpredictable latency spikes, security vulnerabilities, and massive cost overruns. An architect must design with the explicit assumption that the network is unreliable, insecure, slow, and constrained.

## The idea
When writing code inside a monolith, certain physical realities are guaranteed by the operating system and the local hardware: calling a method takes nanoseconds, memory access is safe, and if the process is running, the destination class is guaranteed to exist.

When we move to a distributed system, we replace in-memory function calls with network packets. Yet, our brains naturally carry over monolithic assumptions. We write code like:

```java
// Monolithic-style thinking in a distributed service
User user = userClient.getUser(userId); 
```

This line of code hides a profound danger. It assumes that retrieving a user over a network is as simple and reliable as reading a memory reference.

The eight fallacies of distributed computing represent the gap between monolithic assumptions and distributed reality. Understanding these fallacies is not about learning low-level networking protocols (like TCP/IP window sizes), but about making correct high-level **architectural decisions** regarding timeouts, retries, security, service boundaries, and performance.

## How it works
Let's dissect each of the eight fallacies from an architectural decision-making perspective.

```
       Monolithic Assumption                    Distributed Reality
+---------------------------------+      +---------------------------------+
| Local Call:                     |      | Network Call:                   |
| - Latency = Nanoseconds         |  vs  | - Latency = Milliseconds        |
| - Reliability = 100% (local)    |      | - Reliability = Variable (fail) |
| - Security = OS memory isolated |      | - Security = Vulnerable wire    |
+---------------------------------+      +---------------------------------+
```

### 1. The network is reliable
* **The Fallacy:** Assuming that a packet sent will always arrive at its destination.
* **Architectural Impact:** Services will hang indefinitely waiting for lost responses, exhausting thread pools.
* **Decision-making:** You must design for failure. Implement circuit breakers, retries with exponential backoff and jitter, and fallback behaviors (like returning cached data or a default response).

### 2. Latency is zero
* **The Fallacy:** Assuming that network calls are as fast as local calls.
* **Architectural Impact:** Moving a set of components into separate services can degrade performance by orders of magnitude (e.g., from sub-millisecond to hundreds of milliseconds).
* **Decision-making:** Avoid "chatty" APIs. Design coarse-grained contracts (see `hard-parts/15`) that transfer all necessary data in a single payload rather than making multiple sequential requests.

### 3. Bandwidth is infinite
* **The Fallacy:** Assuming the network can carry any volume of data without bottlenecking.
* **Architectural Impact:** Serializing and transmitting massive payloads (like large JSON objects or raw database dumps) clogs network cards and increases CPU serialization overhead.
* **Decision-making:** Minimize payload sizes. Use efficient serialization formats (like Protocol Buffers or Avro) instead of verbose XML/JSON, and use pagination for collection endpoints.

### 4. The network is secure
* **The Fallacy:** Assuming that because your services run inside a private network or VPC, they are safe from snooping or manipulation.
* **Architectural Impact:** Once an attacker gains access to the perimeter (e.g., via a compromised dependency or web vulnerability), they can sniff all internal communication and forge requests.
* **Decision-making:** Adopt a Zero Trust Architecture. Use mutual TLS (mTLS) to encrypt and authenticate all inter-service communication, and validate JWTs or service-to-service contracts at every boundary.

### 5. Topology doesn't change
* **The Fallacy:** Assuming that IP addresses, server counts, and routing paths remain constant.
* **Architectural Impact:** Hardcoding IP addresses in configuration files leads to major outages during cloud autoscaling or server migrations.
* **Decision-making:** Implement Dynamic Service Discovery (e.g., Consul, Eureka, or Kubernetes DNS). Decouple service locations from their logical names.

### 6. There is one administrator
* **The Fallacy:** Assuming a single person or team manages and understands the entire system.
* **Architectural Impact:** When an incident occurs, teams point fingers because they lack visibility into how other services behave. Upgrades in one service break others without warning.
* **Decision-making:** Invest in comprehensive observability (distributed tracing, centralized logging). Standardize contract versioning schemes and establish clear service ownership (SLAs/SLOs).

### 7. Transport cost is zero
* **The Fallacy:** Assuming that sending data over the network does not cost money or resources.
* **Architectural Impact:** Massive cloud provider bills due to cross-availability-zone or egress data transfers. High CPU overhead dedicated purely to network serialization.
* **Decision-making:** Optimize physical deployment layouts (e.g., keeping highly coupled services in the same region or availability zone). Use caching layers to avoid unnecessary remote fetches (see `system-design/10`).

### 8. The network is homogeneous
* **The Fallacy:** Assuming all servers, routers, and client devices run on the same operating systems and hardware configurations.
* **Architectural Impact:** Integrating services written in different languages or running on different CPU architectures leads to integration failures due to encoding mismatches or protocol incompatibilities.
* **Decision-making:** Rely on open, standard communication protocols (like HTTP/JSON, gRPC, or WebSockets) and standard schema formats (like OpenAPI or AsyncAPI) rather than proprietary runtime serialization.

---

### Worked Example: The Synchronous Cascading Failure
Let's see what happens to a system when an architect ignores Fallacy #1 (Reliability) and Fallacy #2 (Latency).

We have an online portal with three services in a synchronous chain:

```
[User Web Browser] 
       |
    (calls)
       v
[PortalGateway] --(sync http)--> [OrderProcessor] --(sync http)--> [InventoryService]
```

#### The Monolithic View:
If this were a monolith, the whole process is fast and 100% atomic. If the database is up, the transaction succeeds.

#### The Distributed Reality:
One day, the network router connecting the `OrderProcessor` subnet to the `InventoryService` subnet begins dropping 15% of its packets. Latency on the remaining packets spikes from 10ms to 4.5 seconds due to TCP retransmissions.

* **Chain Reaction:**
  1. `InventoryService` takes 4.5 seconds to respond.
  2. `OrderProcessor` blocks its execution thread, waiting for `InventoryService`.
  3. Since new customer orders keep arriving, `OrderProcessor` rapidly exhausts its thread pool (e.g., 200 threads).
  4. Now, `OrderProcessor` cannot accept *any* new requests, even those that don't require `InventoryService`. It appears "dead" to `PortalGateway`.
  5. `PortalGateway` thread pool also blocks, waiting for `OrderProcessor`.
  6. The entire customer portal crashes, returning HTTP 504 Gateway Timeouts to users.

#### The Architectural Remedy:
To address this, the architect makes two decisions:
1. **Apply Fallacy #1 & #2 remedy:** Add a 1-second timeout and a circuit breaker on the `OrderProcessor` client calling `InventoryService`. If calls take too long, the circuit trips, and `OrderProcessor` immediately returns a graceful fallback (e.g., "Order placed; inventory will be confirmed shortly") without blocking its threads.
2. **Apply Fallacy #3 & #7 remedy:** Refactor the synchronous REST call to an asynchronous message queue. `OrderProcessor` writes a "VerifyInventory" message and instantly frees up its resources.

```
[OrderProcessor] --(write)--> [Message Queue] --(read)--> [InventoryService]
```

## Pros
- **Resilient Architectures:** Your systems will continue functioning (potentially in a degraded state) even during network partitions, packet loss, or service crashes.
- **Predictable Performance:** By avoiding chatty APIs and infinite timeouts, your end-to-end response times remain bounded and stable.
- **Accurate Cost Projection:** Factoring in transport costs prevents unexpected cloud infrastructure bills.

## Cons
- **Increased Code Complexity:** Code must handle various network failure states, retry logic, timeouts, and fallback mechanisms.
- **Slower Initial Delivery:** Building asynchronous message flows and zero-trust security layers takes more time than writing simple synchronous REST clients.
- **Difficult Testing:** Verifying how a system handles network latency and failures requires specialized tools (like Chaos Mesh or Toxiproxy) and complex infrastructure setups.

## Alternatives
- **Do Not Distribute (Keep the Monolith):** The absolute best alternative if you cannot afford the complexity of mitigating the eight fallacies.
- **Technical Mesh Layer (Service Mesh):** Offloading concerns like mTLS, timeouts, retries, and service discovery to a service mesh infrastructure layer (like Istio or Linkerd) so the application code remains simple.

## When to use it
- **Every Distributed System Design:** The fallacies must be front of mind whenever designing any distributed system, microservice landscape, or service-oriented architecture.
- **Cloud Migrations:** When moving an existing monolithic application from on-premise hardware to highly dynamic cloud environments.

## When NOT to use it
- **Pure Monoliths:** Inside a single OS process, you do not need to worry about network latency, transport costs, or topology changes. Standard programming tools manage these.

## Key takeaways / mental model
The network is not your friend. It is a hostile, volatile, and slow medium that sits directly in the middle of your application's critical path. Whenever you draw an arrow between two boxes in a diagram, do not think of it as a clean line. Think of it as a bridge built over an active volcano. Design your systems so that if that bridge collapses, the buildings on both sides remain standing.

## Self-check questions
1. How does ignoring Fallacy #2 ("Latency is zero") lead to the creation of "chatty" distributed systems, and what is the cure?
2. What architectural pattern helps mitigate Fallacy #1 ("The network is reliable") and Fallacy #5 ("Topology doesn't change") simultaneously?
3. How can transport cost (Fallacy #7) affect decisions regarding database replication or service grouping?

## References
- *Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025)*, Chapter 10: Monolithic vs. Distributed Architectures
- Cross-subject prerequisites: [fundamentals/09]
- Cross-subject connections: [ddia/12], [system-design/02]
