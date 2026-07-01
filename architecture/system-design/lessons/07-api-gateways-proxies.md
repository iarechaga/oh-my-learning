---
id: system-design/07
subject: system-design
title: "API Gateways and Reverse Proxies"
slug: api-gateways-proxies
status: drafted
mastery:
seniority: mid
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapters 4 and 8"
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# API Gateways and Reverse Proxies

## TL;DR
Modern distributed systems require a unified entry point to manage client traffic, secure backend resources, and abstract internal complexity. API gateways and reverse proxies act as this front door, handling cross-cutting concerns like routing, authentication, and rate limiting. Employing these intermediaries protects internal microservices, simplifies client interactions, and forms the bedrock of API-driven architectures.

## The idea
When microservices communicate directly with clients, clients must know every endpoint, handle multiple protocols, and authenticate against every single service. This creates tight coupling, increases security risk, and clutters client-side logic. Intermediaries solve this by separating the internal network from the public internet.

By inserting a reverse proxy or API gateway between clients and backends, we establish a single point of entry. This layer shields internal services, translates protocols, and aggregates multiple backend responses into one. Clients talk to a single server, while backend teams remain free to refactor, scale, and secure services independently.

## How it works

### Forward Proxies vs. Reverse Proxies
The distinction between these two types of proxies lies in which party they represent and hide from the other side.

A forward proxy sits in front of clients. It acts on behalf of clients to fetch resources from the internet, hiding client identities and enabling caching, content filtering, or access control. Corporate networks use forward proxies to restrict employee web access, while individuals use them to bypass regional firewalls.

In contrast, a reverse proxy sits in front of servers. It acts on behalf of backend systems, receiving requests from the public internet and routing them to the appropriate server. Clients believe they are interacting directly with the destination server, unaware of the complex infrastructure behind it. Reverse proxies provide load balancing, SSL termination, and security shielding.

### API Gateway Responsibilities
An API gateway is an advanced, application-aware reverse proxy. While a reverse proxy typically focuses on routing and network-level tasks, an API gateway handles application-level concerns:

1. **Request Routing (Reverse Proxying)**: The gateway inspects the incoming HTTP request path, headers, or query parameters to determine which microservice should handle it. For example, a request to `/api/v1/orders` goes to the Order Service, while `/api/v1/users` routes to the User Service. Most gateways utilize efficient data structures, such as Radix Trees, to match route paths quickly and route requests with minimal overhead.
2. **Authentication and Authorization Offload**: Validating security credentials at the edge prevents downstream services from duplicating this logic. The gateway validates API keys, session cookies, or JSON Web Token (JWT) signatures. Once validated, it forwards the request with enriched user metadata headers.
3. **Rate Limiting and Throttling**: To protect backend services from denial-of-service attacks or noisy neighbors, the gateway tracks requests per client identity or IP address. It implements algorithms like Token Bucket, Leaky Bucket, or Sliding Window Counter, using Redis to coordinate rate limits across multiple stateless gateway nodes. If a threshold is crossed, it rejects subsequent requests immediately with a 429 status.
4. **Request Aggregation and Composition**: Instead of a mobile client making five separate network requests to load a page, the gateway exposes a single endpoint. It fires those five requests internally over high-speed networks, aggregates the results, and returns a single response.
5. **Protocol Translation**: Public-facing clients often use REST over HTTP/1.1 or HTTP/2. The gateway can accept these public JSON payloads and translate them into faster, binary internal protocols like gRPC (HTTP/2 with Protocol Buffers) or AMQP. This conversion is often done using transcoders (like Envoy's gRPC-JSON transcoder) which map JSON paths directly to gRPC service methods.
6. **Response Caching**: Caching frequently requested, semi-static data (like product catalogs) directly at the edge reduces backend server load and improves response times. Eviction strategies like time-to-live (TTL) expiration or explicit cache invalidation via pub/sub messages ensure data freshness.
7. **Observability**: As the single point of entry, the gateway is the perfect spot to collect access logs, record latency metrics, and inject distributed tracing correlation IDs.
8. **SSL/TLS Termination**: Handling the expensive cryptographic handshake of SSL/TLS at the gateway offloads CPU-intensive operations from the microservices.
9. **CORS Management**: The gateway can handle Cross-Origin Resource Sharing (CORS) preflight options requests (`OPTIONS`) directly, preventing useless preflight requests from flooding internal backend systems.

### The Gateway Lifecycle: Inside the Event Loop
To understand how modern gateways handle millions of concurrent connections, we must examine their underlying I/O model. Traditional web servers used a thread-per-connection model. Under high load, this approach fails because operating system context-switching overhead and thread memory consumption exhaust system resources.

Modern proxies like Nginx, Envoy, or HAProxy utilize an asynchronous, event-driven, non-blocking I/O model.

A small number of worker processes, usually matching the number of CPU cores, run continuously. Each worker runs an active event loop that monitors thousands of network sockets using system calls like `epoll` on Linux or `kqueue` on macOS. When a socket becomes ready for reading or writing, the kernel notifies the event loop, which triggers a callback to process that specific chunk of data.

```
 [Network Sockets] ──> [OS Kernel (epoll/kqueue)] ──> [Event Loop] ──> [Non-Blocking Callback]
```

This ensures that workers never sleep or block waiting for network responses. While a downstream microservice is processing a request, the gateway worker immediately moves on to handle other incoming client connections. This highly efficient architecture allows a single API gateway node to maintain hundreds of thousands of open TCP connections with minimal memory and CPU consumption.

### Gateway vs. Load Balancer vs. Service Mesh
Understanding where these three components fit prevents architectural redundancy.

* **Load Balancer (Layer 4 or Layer 7)**: Primarily focuses on high availability and traffic distribution. A Layer 4 load balancer distributes raw TCP/UDP packets. A Layer 7 load balancer can route based on HTTP headers or paths, but it does not understand application-level concepts like user authentication, rate limits, or API composition.
* **API Gateway (Layer 7)**: Sits between the external clients and internal load balancers. It is highly intelligent, managing API lifecycle, security policies, and request transformations.
* **Service Mesh (East-West Traffic)**: Manages communication between internal services within the secure network. While the API gateway handles incoming traffic from the outside world (North-South traffic), a service mesh handles inter-service security, retries, and circuit breaking via sidecar proxies co-located with each service instance.

| Feature | Load Balancer | API Gateway | Service Mesh |
| --- | --- | --- | --- |
| Primary Traffic Focus | North-South (Client to Cluster) | North-South (Client to Cluster) | East-West (Service to Service) |
| Protocol Layer | Layer 4 (TCP/UDP) or Layer 7 (HTTP) | Layer 7 (HTTP, WebSockets, gRPC) | Layer 7 (HTTP, gRPC, TCP) |
| Key Responsibilities | Traffic distribution, health checks, SSL offload | Routing, auth offload, rate limiting, BFF, composition | Mutual TLS, service discovery, retries, circuit breaking |
| Deployment Pattern | Dedicated cluster edge appliance | Cluster edge entry point proxy | Sidecar container next to every service |

Administrative boundaries differ across these tiers. Typically, infrastructure and operations teams manage the edge load balancer. Security teams or frontend teams configure the API gateway to implement client-facing policies. Platform engineering teams manage the service mesh to ensure reliable inter-service networking.

Service meshes, like Istio or Linkerd, utilize lightweight sidecars to intercept traffic silently. These sidecars negotiate mutual TLS (mTLS) and rotate certificates automatically. This configuration guarantees that internal cluster communication remains secure without requiring changes to application code. Under the hood, these containers manipulate network routing rules using `iptables` inside the pod namespace, forcing all outbound and inbound loopback traffic through the proxy container.

### Gateway Software Comparison
When building an API gateway, teams choose from several well-established open-source and commercial products:

* **Nginx and Kong**: Nginx is a lightning-fast C-based reverse proxy. Kong is built on top of Nginx, utilizing Lua scripts via OpenResty to provide a highly extensible plugin architecture for authentication, rate limiting, and transformations.
* **Envoy**: Built in C++ by Lyft, Envoy is designed from the ground up for microservices. It features dynamic configuration APIs (xDS), making it the primary choice for modern cloud-native ingress and service mesh sidecars.
* **HAProxy**: A highly optimized C-based proxy focused strictly on raw load balancing performance and security at Layers 4 and 7.
* **Spring Cloud Gateway**: Built on Java and Project Reactor, it offers a non-blocking developer-friendly framework for Spring and JVM-based microservice environments.

| Software | Language | Strengths | Ideal Use Case |
| --- | --- | --- | --- |
| Nginx / Kong | C / Lua | Extremely low footprint, rich plugin ecosystem | Standard enterprise gateways |
| Envoy | C++ | Dynamic APIs, advanced observability, cloud-native | Kubernetes clusters and service mesh |
| HAProxy | C | Peerless performance, robust load balancing | Raw Layer 4 and Layer 7 distribution |
| Spring Cloud | Java | Deep JVM integration, easy Java customization | Java-centric microservices |

### The Backend-for-Frontend (BFF) Pattern
A single, universal API gateway can become a bottleneck when supporting diverse client types. A mobile device requires compact payloads to save battery and data, while a desktop web application needs rich, comprehensive details.

The BFF pattern solves this by deploying dedicated, lightweight gateways for each distinct client type.

The mobile BFF handles specific aggregation and payloads optimized for phones. The web BFF provides full-fidelity data structures for desktop browsers. Third-party API consumers connect to their own integration gateway with stricter rate limits and stable versioning. This prevents teams from blocking each other on changes to a shared gateway configuration.

Furthermore, this pattern improves organizational alignment. Frontend teams gain ownership over their respective BFF services. They can modify API schemas and deploy changes rapidly without coordinating with backend microservice owners, increasing overall delivery speed.

Additionally, BFFs solve session management issues in modern browser environments. Instead of storing sensitive access tokens in local storage, a Web BFF can act as a confidential OAuth 2.0 client. It issues secure, HTTP-only, SameSite cookies to the browser. Whenever a request arrives, the BFF translates this cookie-based session into a stateless JWT token before forwarding it to downstream microservices, keeping the frontend completely immune to token theft.

### Advanced Routing Techniques: Canary, Blue-Green, and A/B Testing
The centralized nature of the gateway enables sophisticated deployment strategies. Because all public requests flow through this layer, the routing engine can split traffic dynamically based on precise rules.

For a canary deployment, the gateway can route 95% of traffic to version 1.0 of a service and 5% to version 2.0. This division can be controlled by static weights, or it can target specific groups of users based on cookies or custom headers. If error metrics spike for the 5% group, the gateway instantly rolls back all traffic to the stable version.

This approach builds directly on the concepts of zero-downtime migrations. It allows the system to roll out schema and application changes gradually, mitigating risks of cascading failures during software releases.

### Failure Modes and Mitigations
Because the gateway sits at the center of all traffic, it introduces specific structural risks:

1. **Single Point of Failure (SPOF)**: If the gateway crashes, the entire platform goes dark.
   - *Mitigation*: Deploy the gateway as a stateless, horizontally scaled cluster behind a high-availability Layer 4 load balancer (like AWS NLB) or using DNS Anycast.
2. **Cascading Failures and Resource Exhaustion**: A single slow downstream service can cause the gateway to hold connections open. This depletes the gateway socket and thread pools, blocking traffic to healthy services.
   - *Mitigation*: Implement strict, aggressive timeouts and circuit breakers inside the gateway. Allocate dedicated thread or connection pools (bulkheads) per downstream service so one failing service cannot consume all gateway resources.
3. **Latency Overhead**: Every network hop adds latency. Adding a gateway means extra serialization and parsing.
   - *Mitigation*: Keep the gateway lightweight. Run only critical cross-cutting policies at this layer. Avoid executing heavy business logic, database queries, or CPU-intensive computations on the gateway. Use high-performance, non-blocking asynchronous event loops like Netty, Envoy, or Nginx.
4. **Cryptographic Bottlenecks**: Decrypting SSL/TLS certificates and verifying thousands of JWT signatures per second consumes significant CPU.
   - *Mitigation*: Delegate SSL termination to an upstream hardware load balancer or cloud-managed edge. Cache verified public keys and user session data in a fast, local cache. Pass validated user identity to downstream services using lightweight, unencrypted custom headers.
5. **Security Vulnerabilities and Perimeter Hardening**: Attackers target the gateway with injection attacks, cross-site scripting, and credential stuffing.
   - *Mitigation*: Enforce strict CORS policies, drop headers that do not match expected schemas, and validate all incoming request payload sizes. Keep the gateway software updated with security patches.
6. **Configuration Drift and Release Bottlenecks**: Managing hundreds of routes across multiple teams can lead to conflicting configuration rules and unstable deployments.
   - *Mitigation*: Treat the gateway configuration as code (GitOps). Run linting and automated routing tests in continuous integration pipelines to validate changes before they reach production.
7. **Thundering Herd and Retry Storms**: When a backend service temporarily fails, retries from the gateway can flood it, preventing it from recovering.
   - *Mitigation*: Configure retry policies inside the gateway to use exponential backoff with random jitter. Implement circuit breakers to fail-fast and stop sending traffic when success rates drop below a specific threshold.

### Worked Examples

#### Example 1: Client Request Flow with Gateway Aggregation
Consider a product details page that displays information from three distinct microservices: the Product Service, the Inventory Service, and the Reviews Service.

```
       [ Client Device ]
               │
               │ (1) GET /products/123 (HTTP/1.1 JSON)
               ▼
   ┌────────────────────────────────────────┐
   │              API GATEWAY               │
   │  - Auth Offload & Rate Limiting        │
   │  - Request Aggregation Engine          │
   └───────┬──────────────┬──────────────┬──┘
           │              │              │
           │ (2)          │ (3)          │ (4)
           │ gRPC         │ gRPC         │ gRPC
           ▼              ▼              ▼
     ┌───────────┐  ┌───────────┐  ┌───────────┐
     │  Product  │  │ Inventory │  │  Reviews  │
     │  Service  │  │  Service  │  │  Service  │
     └───────────┘  └───────────┘  └───────────┘
```

When the client makes a single HTTP call to `GET /products/123`, the gateway interceptor acts:
1. It validates the client session and rate limits.
2. It splits the request into three internal sub-requests.
3. It dispatches these calls concurrently to the internal services.
4. It collects the responses. If one service fails, the gateway gracefully degrades the response. For example, if the Reviews Service times out, the gateway returns the product details and inventory status, while inserting an empty list for reviews.
5. It constructs a clean, single response:
   ```json
   {
     "id": "123",
     "name": "Wireless Headphones",
     "price": 99.99,
     "in_stock": true,
     "rating": 4.8,
     "reviews_status": "partially_degraded"
   }
   ```
This reduces cellular network utilization, improving the mobile user experience significantly.

#### Example 2: Edge Security, Authentication, and Rate Limiting
Let us trace the security path of a request through our gateway.

```
 [Client]             [Gateway]              [Redis]            [Order Service]
    │                     │                     │                      │
    │ ──(1) POST order ──>│                     │                      │
    │                     │ ──(2) Check rate ──>│                      │
    │                     │ <──(3) Rate OK ─────│                      │
    │                     │                     │                      │
    │                     │ ──(4) Validate JWT ────────────────────────> [ID Provider] (Cached)
    │                     │                     │                      │
    │                     │ ──(5) Strip JWT & inject X-User-Id ───────>│
    │                     │                                            │ ──(6) Execute order
```

A client sends a request to `POST /api/v1/orders` containing a JWT in the `Authorization` header.
The gateway receives the request. First, it extracts the client's IP address and checks a Redis-backed rate limiter. Redis shows the client has used 12 out of their allowed 100 requests per minute. The counter increment succeeds.

Next, the gateway inspects the JWT. It verifies the signature against the identity provider's cached public key. Once verified, the gateway decodes the claims. It finds the user ID is `user_884` and their role is `customer`.

Before forwarding, the gateway strips the heavy, sensitive JWT. It appends trusted headers:
- `X-User-Id: user_884`
- `X-User-Role: customer`

It forwards the request to the Order Service. The Order Service accepts the request, knowing it has been pre-authenticated and rate-limited. It trusts the headers implicitly, avoiding expensive token verification or database checks.

#### Example 3: Forward Proxy vs. Reverse Proxy Real-World Scenarios
Let us compare two common security scenarios to solidify our mental models.

* **Scenario A (Forward Proxy in a Bank)**: A bank enforces a policy where employees cannot visit non-work websites. All employee laptops are configured to route external traffic through a corporate forward proxy. When an employee tries to visit `https://malicious-site.com`, the forward proxy intercepts the TCP connection, checks its blocklist, logs the block event, and rejects the request. The target website only sees the IP address of the forward proxy, never the employee laptop.
* **Scenario B (Reverse Proxy for a SaaS Platform)**: A SaaS company hosts its software on a cluster of ten application servers. They point their public domain name to a reverse proxy running Nginx. When a user visits `https://saas-app.com`, the reverse proxy intercepts the connection, decrypts the TLS layer, and forwards the plain HTTP request to the least-loaded application server. The application servers sit in a private subnet, totally invisible to the public internet.

## Pros
- **Centralized security and compliance**: Moving SSL termination, CORS policies, and authentication to the edge prevents security policy fragmentation across services.
- **Improved developer velocity**: Backend teams focus purely on business logic rather than rebuilding auth, rate limiting, and logging utilities for every new service.
- **Minimized client footprint**: Aggregating API calls and translating protocols abstracts microservice complexity, keeping clients lightweight and fast.
- **Zero-downtime migrations**: The gateway can dynamically re-route traffic from old legacy endpoints to new microservices, enabling seamless refactoring behind a stable URL.
- **Optimized network usage**: Using fast internal protocols like gRPC behind the gateway, while exposing standard REST to the outside world, maximizes cluster throughput.

## Cons
- **Single point of failure**: Misconfiguring or crashing the gateway cluster takes down the entire application ecosystem, making it a critical infrastructure risk.
- **Increased latency hop**: Serializing, deserializing, and routing packets through an intermediate layer adds a non-zero latency penalty to every transaction.
- **Development bottleneck**: If a single shared gateway is used, every backend change that alters paths or security requirements requires modifying the gateway, causing release dependencies.
- **Operational and cost overhead**: Running, monitoring, and autoscaling a highly available gateway tier introduces significant operational complexity and cloud billing costs.
- **Debugging complexity**: Tracing a failed request becomes harder when it passes through an intermediate proxy, requiring a robust distributed tracing setup to match logs across boundaries.

## Alternatives
- **Direct Client-to-Service Communication**: Clients connect directly to backend services over the internet. This works well for small, simple architectures with a few services, avoiding proxy latency, but it exposes internal network endpoints and duplicates security rules.
- **Service Mesh Ingress Controllers**: Using a lightweight Kubernetes Ingress controller to handle raw routing, while delegating authentication, circuit breaking, and rate limiting directly to the service mesh sidecars. This keeps the edge thin but increases internal cluster management complexity.
- **Client-Side Discovery and Routing**: Clients contact a service registry like Eureka or Consul to fetch service instance IPs, then execute load balancing and routing directly from the client code. This removes the gateway hop but makes clients fat, complex to maintain, and highly coupled to internal topology.

## When to use it
- **Complex microservice ecosystems**: When you are managing dozens of independent services written in different programming languages and need unified policies.
- **Multi-client application suites**: When web, mobile, and third-party integrations require different payload shapes, rate limits, and access controls.
- **Legacy monolith strangulation**: When gradually breaking down a massive legacy monolith into microservices, the gateway acts as a facade, keeping migrations invisible to clients.

## When NOT to use it
- **Simple monolithic systems**: If your backend is a single, unified database and application server, adding a gateway introduces useless latency, complexity, and operational risk. A basic Layer 4 or Layer 7 load balancer is much better.
- **Ultra-low latency platforms**: In environments like high-frequency trading, IoT sensor data ingestion, or multiplayer game servers, the added latency and serialization overhead of a gateway are unacceptable.
- **Small-scale, single-team setups**: If a small team manages three or four services, the operational cost of managing a gateway cluster outweighs the organizational benefits of centralized policy enforcement.

## Key takeaways / mental model
Think of the API gateway as the concierge of a luxury hotel. Instead of guests wandering through hallways trying to find the chef, the cleaner, and the accountant, they talk only to the concierge. The concierge checks their keycard, answers their questions, routes their requests to the right staff, aggregates their services, and presents a single, seamless experience.

Furthermore, remember these core structural identities:
- Reverse proxies represent and protect the backend servers.
- Forward proxies represent and protect the client devices.
- API gateways apply application-specific policies and handle Backend-for-Frontend (BFF) patterns at the cluster edge.
- Service meshes handle secure internal pod-to-pod networking inside the cluster.

## Self-check questions
1. Explain how a forward proxy protects client anonymity, while a reverse proxy protects server infrastructure.
2. In a high-throughput microservice system, why does performing JWT token verification at the API gateway level improve security, and how does it change downstream service authorization?
3. How does the Backend-for-Frontend (BFF) pattern prevent an API gateway from becoming a bloated development bottleneck for multiple frontend teams?
4. Imagine a scenario where a downstream microservice is responding very slowly. How can circuit breakers and bulkheads inside the API gateway prevent this slow service from taking down the entire system?
5. Construct an argument comparing when you would use a layer 7 load balancer versus an API gateway at the edge of your cluster.
6. Under what circumstances would you bypass the API gateway completely and let clients query services directly?
7. Explain the difference between thread-per-connection and asynchronous event-driven I/O models in proxies. Why does the latter enable high scalability under massive connection concurrency?

## References
- Sinha, D. & Chopra, T. (2024). *System Design Guide for Software Professionals*, Chapters 4 and 8. Packt Publishing.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly Media.
