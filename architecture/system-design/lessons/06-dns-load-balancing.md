---
id: system-design/06
subject: system-design
title: "DNS and Load Balancing"
slug: dns-load-balancing
status: drafted
mastery:
seniority: mid
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 4"
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# DNS and Load Balancing

## TL;DR
DNS and load balancers form the entry point of any large-scale web system. They split massive global traffic down to individual servers, matching scale requirements with high availability. This lesson covers how domain resolution redirects users, how Layer 4 and Layer 7 distribution works, and how to select the right load balancing algorithms.

## The idea
Single computers cannot handle millions of simultaneous users. When your application grows, you must deploy multiple servers. This scale introduces two hard challenges. First, how do clients find your system using a simple name like "example.com"? Second, once client requests arrive at your infrastructure, how do you spread them evenly so no single machine gets overloaded?

DNS (Domain Name System) solves the discovery challenge. It acts like a global phonebook, translating human-readable names into machine-readable IP addresses. Load balancing solves the distribution challenge. It acts like a traffic cop, routing incoming requests across a pool of backend servers. Together, they form a multi-tiered hierarchy that ensures high availability, fault tolerance, and low latency.

## How it works

### The First Layer: DNS Resolution
When a client types a domain name, the browser must find the correct IP address before opening a connection. This lookup is a hierarchical, distributed search.

#### Recursive vs Iterative Queries
Resolution involves two kinds of queries, recursive and iterative.
- **Recursive queries**: Clients ask a resolver (like your ISP or 1.1.1.1) to find the IP. This resolver takes full responsibility. It must return either the correct IP address or an error, handling all intermediate steps.
- **Iterative queries**: Resolvers contact authoritative name servers directly. If the server does not know the IP, it does not search further. Instead, it returns the address of the next-level name server down the chain. The resolver then queries that next server.

Here is the step-by-step lookup path:
1. Client browsers check their local cache. If empty, they check the operating system hosts file and local DNS cache.
2. A recursive query goes out from the browser to the local DNS resolver.
3. Next, the resolver sends an iterative query to the Root Name Server. Root servers respond with the location of the Top-Level Domain (TLD) server (e.g., .com).
4. This resolver then queries the TLD name server. TLD servers respond with the IP of the Authoritative Name Server for the domain (e.g., example.com).
5. Authoritative Name Servers receive the final query and return the exact IP address.
6. Lastly, the resolver returns this IP to the client and caches it locally.

```text
+----------+          (1) Recursive Query           +----------+
|  Client  | -------------------------------------> | Local    |
| Browser  | <------------------------------------- | Resolver |
+----------+          (6) IP Address Return         +----------+
                                                          |
                 +----------------------------------------+
                 |
                 | (2) Iterative: "Where is example.com?"
                 v
        +------------------+
        | Root Name Server |
        +------------------+
                 | (3) Iterative Response: "Go to .com TLD server"
                 |
                 v
        +------------------+
        | TLD Name Server  |
        +------------------+
                 | (4) Iterative Response: "Go to example.com Name Server"
                 |
                 v
        +------------------+
        | Authoritative NS |
        +------------------+
                   (5) Iterative Response: "The IP is 198.51.100.5"
```

#### Common Record Types
Name servers store records in specific formats to define routing behaviors.
- **A records**: Map a domain name to an IPv4 address.
- **AAAA records**: Map a domain name to an IPv6 address.
- **CNAME records**: Map a domain name to another domain name (aliases). This is useful for pointing subdomains to external services.
- **NS records**: Delegate a DNS zone to use a specific authoritative name server.
- **MX records**: Direct email traffic to mail servers.
- **TXT records**: Hold arbitrary text, commonly used for domain ownership verification and security policies like SPF or DKIM.

#### TTL (Time to Live) and Caching
DNS responses include a TTL value in seconds. Resolvers, operating systems, and browsers cache the IP for this duration. Caching reduces global network traffic and speeds up connection times. However, high TTL values slow down failover. If a server crashes, clients continue sending traffic to the dead IP until their cached TTL expires. Low TTL values allow rapid updates but increase lookup latency for users.

#### GeoDNS and Anycast
To reduce network latency, systems use advanced DNS routing.
- **GeoDNS**: Authoritative name servers inspect the source IP of the resolver. They return an IP address of a data center physically close to the user. A user in Tokyo gets a Tokyo server IP, while a user in London gets a London server IP.
- **Anycast**: Multiple physical servers across the world advertise the exact same IP address. Routers automatically send the user packets to the nearest server using BGP (Border Gateway Protocol). This routing handles high traffic loads at the network edge and mitigates massive distributed denial-of-service (DDoS) attacks.

---

### The Entry Point: Load Balancing Fundamentals
Once DNS routes a client to your public IP, a load balancer handles the incoming connection. It sits between the user and your private network, shielding your actual servers from direct exposure.

```text
[ Client ]
    │
    ├─(1) Resolve domain: api.example.com ──> [ DNS Server (Anycast / GeoDNS) ]
    │                                                    │
    ├─(2) Returns LB IP: 198.51.100.5 <──────────────────┘
    │
    ├─(3) HTTP Request (SSL Handshake / TCP) ──> [ L7 Load Balancer (SSL Terminated) ]
    │                                                        │
    │                                         ┌──────────────┼──────────────┐
    │                                         │ (Health Check│ Active)      │
    ▼                                         ▼              ▼              ▼
[ Server 1 (10.0.0.1) ]             [ Server 2 (10.0.0.2) ]       [ Server 3 (10.0.0.3) ]
```

#### Deployment Topologies
Load balancers must be highly available themselves. They are usually deployed in two configurations:
- **Active-Passive**: One primary load balancer handles all traffic. A secondary standby load balancer monitors the primary via a heartbeat signal. If the primary fails, the standby takes over the public IP instantly using virtual router redundancy protocol (VRRP).
- **Active-Active**: Multiple load balancers handle traffic simultaneously. DNS spreads requests across these load balancers, increasing the total capacity of the entry layer.

---

### OSI Layer Selection: L4 Transport vs L7 Application
Load balancers operate at different layers of the networking stack, defining how much of the packet they can read.

#### Layer 4 (L4) Transport Load Balancing
L4 load balancers work at the transport protocol level (TCP and UDP). They make routing decisions without inspecting the application payload.
- **Mechanism**: The load balancer reads the source IP, source port, destination IP, and destination port. It modifies the packet header (using Network Address Translation, or NAT) or routes it directly to a backend server.
- **Characteristics**: L4 routing is extremely fast. It requires minimal CPU because it does not decrypt SSL or parse HTTP headers. However, it cannot make smart decisions based on the actual request path, headers, or cookies.

#### Layer 7 (L7) Application Load Balancing
L7 load balancers work at the application protocol level (HTTP, HTTPS, gRPC). They parse and inspect the actual message content.
- **Mechanism**: The load balancer terminates the TCP connection, decrypts SSL, and parses the HTTP request. It reads HTTP headers, paths, cookies, and query parameters.
- **Characteristics**: L7 routing requires significant CPU and memory. However, it allows intelligent routing. For example, it can send requests for `/static/*` to an asset server, `/api/checkout` to a checkout service, and mobile users to a mobile-optimized backend.

| Metric | Layer 4 (L4) Load Balancing | Layer 7 (L7) Load Balancing |
| :--- | :--- | :--- |
| **OSI Layer** | Layer 4 (Transport) | Layer 7 (Application) |
| **Protocols** | TCP, UDP | HTTP, HTTPS, HTTP/2, gRPC, WebSocket |
| **Data inspected** | IP addresses, ports | HTTP headers, paths, cookies, post body |
| **CPU overhead** | Low (no packet payload parsing) | High (SSL decryption, header parsing) |
| **Routing features** | Simple connection distribution | Path routing, header inspection, rewrite |
| **Security** | Minimal (passes packets through) | Web Application Firewall (WAF), rate limiting |
| **TCP Connections** | Single end-to-end TCP connection | Two separate connections (Client-LB, LB-Server) |

---

### Load Balancing Algorithms
Algorithms determine how the load balancer selects a backend server.

- **Round-Robin**: Requests are distributed sequentially down the list of servers. This assumes all servers have equal capacity and all requests have equal processing cost.
- **Weighted Round-Robin**: Each server gets a weight based on its hardware capacity. A server with weight 3 receives three times more requests than a server with weight 1.
- **Least-Connections**: The load balancer tracks active connections on each server and sends new requests to the server with the fewest active sessions. This works well for requests with highly variable processing times.
- **Least-Response-Time**: Sends traffic to the server with the fewest active connections and the lowest average response latency.
- **IP Hash**: Hashes the client IP address to map it to a specific server. This ensures a client reaches the same backend server consistently, keeping local state valid.
- **Consistent Hashing**: Minimizes disruption when servers are added or removed from the pool. It maps both servers and request hashes onto a circular ring. Adding a node only shifts a fraction of the keys, preserving most session states.

---

### Advanced LB Mechanisms

#### Health Checks
To prevent sending traffic to failed servers, load balancers perform active or passive checks.
- **Active health checks**: The load balancer pings a specific endpoint (e.g., `/healthz`) at fixed intervals. If a server fails to respond with a 200 OK status within a threshold (like 3 consecutive checks), it is pulled out of the rotation.
- **Passive health checks**: The load balancer monitors real client traffic. If a server starts throwing 5xx errors frequently, the load balancer temporarily stops sending new connections to it.

#### Sticky Sessions (Session Affinity)
Sometimes, an application stores user session data on a specific backend server. To keep the user on that same server, the load balancer uses sticky sessions. It injects a cookie or hashes the client IP.
- **Downsides**: This breaks uniform load distribution. If many active users get grouped on one server, that server gets overloaded while others sit idle. It also complicates server failure. If a server crashes, all users pinned to it lose their session data.

#### SSL/TLS Termination
Securing traffic requires encryption. Decrypting HTTPS packets requires substantial CPU.
- **SSL Termination**: The load balancer decrypts incoming HTTPS traffic, inspects it, and forwards plain HTTP to backend servers over a secure private network. This frees backend servers from cryptographic overhead.
- **SSL Pass-through**: The load balancer passes the encrypted packets directly to backend servers without decryption. This is highly secure but prevents L7 routing decisions because the load balancer cannot read the HTTP headers.

---

### Worked Examples

#### Example 1: Full Request Path
Let us trace a user making an API request to `api.example.com/v1/users`.

1. **DNS Phase**: Client browsers query the local resolver first. This resolver then contacts the authoritative name server for `example.com`.
2. **GeoDNS Resolution**: The authoritative name server detects the client is in San Francisco. It returns a low-latency IP address of the US West Coast load balancer: `198.51.100.5` with a TTL of 300 seconds.
3. **TCP Connection**: The client browser establishes a TCP handshake with the load balancer at `198.51.100.5` on port 443.
4. **SSL Handshake**: Both client and load balancer complete the TLS handshake. This load balancer decrypts the packet using its certificate.
5. **L7 Inspection**: The load balancer reads the HTTP request header and path. It detects the path starts with `/v1/users`.
6. **Routing Decision**: The load balancer uses a weighted round-robin algorithm. It selects Server A (`10.0.0.1`) because Server B (`10.0.0.2`) has a lower weight.
7. **Internal Request**: The load balancer opens a plain HTTP connection to Server A at `10.0.0.1:80` over the private network.
8. **Response Path**: Server A processes the database request, returns the JSON payload to the load balancer. The load balancer encrypts it and sends it back to the client browser.

#### Example 2: Round-Robin vs Least-Connections Under Uneven Request Cost
Let us compare performance under two algorithms. We have 2 servers: Server X and Server Y. Both are currently idle.
- Server X has a capacity of 10 concurrent requests.
- Server Y has a capacity of 10 concurrent requests.

Our clients send 10 requests in rapid succession:
- Requests 1, 2: Heavy exports (takes 10 seconds of CPU time each).
- Requests 3, 4, 5, 6, 7, 8, 9, 10: Lightweight page loads (takes 0.1 seconds of CPU time each).

**Scenario A: Round-Robin Algorithm**
The requests are distributed sequentially, alternating between X and Y.
1. Request 1 (heavy) -> Server X (X active: 1, Y active: 0)
2. Request 2 (heavy) -> Server Y (X active: 1, Y active: 1)
3. Request 3 (light) -> Server X (X active: 2, Y active: 1)
4. Request 4 (light) -> Server Y (X active: 2, Y active: 2)
5. Request 5 (light) -> Server X (X active: 3, Y active: 2)
6. Request 6 (light) -> Server Y (X active: 3, Y active: 3)
7. Request 7 (light) -> Server X (X active: 4, Y active: 3)
8. Request 8 (light) -> Server Y (X active: 4, Y active: 4)
9. Request 9 (light) -> Server X (X active: 5, Y active: 4)
10. Request 10 (light) -> Server Y (X active: 5, Y active: 5)

*Result*: Both servers are quickly choked. The lightweight requests (3 to 10) are queued behind the heavy exports on both machines. Response times for simple pages spike from 0.1 seconds to several seconds.

**Scenario B: Least-Connections Algorithm**
The load balancer tracks active connections and routes to the lowest count.
1. Request 1 (heavy) -> Server X (X active: 1, Y active: 0)
2. Request 2 (heavy) -> Server Y (X active: 1, Y active: 1)
3. Request 3 (light) -> Server X (Both have 1. LB picks X. X active: 2, Y active: 1. Server X processes light request but is slow. However, let us assume Server Y finishes its light requests fast.)
Wait, let us trace more precisely based on completion speed.
- At t=0s, Request 1 (heavy) goes to X. Connection states: X: 1 (heavy), Y: 0.
- At t=0.01s, Request 2 (heavy) goes to Y. Connection states: X: 1 (heavy), Y: 1 (heavy).
- At t=0.02s, Request 3 (light) goes to X. Connection states: X: 2, Y: 1.
- At t=0.03s, Request 4 (light) goes to Y. Connection states: X: 2, Y: 2.
- At t=0.12s, Request 2 still runs, but Request 4 (light) is completed on Y. Connection states: X: 2 (still processing light request 3 and heavy 1), Y: 1 (heavy 2).
- At t=0.13s, Request 5 (light) arrives. Y has fewer connections (1 vs 2). The load balancer routes Request 5 to Y. Connection states: X: 2, Y: 2.
- At t=0.23s, Y completes Request 5. Connection states: X: 2, Y: 1.
- At t=0.24s, Request 6 (light) arrives. LB routes it to Y. Connection states: X: 2, Y: 2.
- At t=0.34s, Y completes Request 6. Connection states: X: 2, Y: 1.
- At t=0.35s, Request 7 (light) arrives. LB routes it to Y. Connection states: X: 2, Y: 2.

*Result*: Server Y handles almost all lightweight requests dynamically because its active connection count drops quickly. Server X is left to deal with its heavy report and the single light request it was assigned early on. The overall system latency remains low for the majority of users.

#### Example 3: L4 vs L7 Routing Decision with Direct Server Return
A retail website has three major components:
- Static assets (images, CSS, JS files, size 100 KB each).
- API checkout requests (complex calculations, database writes).
- File uploads (large PDF invoices, size 10 MB each).

The company initially uses a single L4 load balancer. However, file uploads hog all TCP connections on server instances. Static asset requests get queued behind slow database operations.

To fix this, they deploy a hybrid tier:
1. **L4 Layer with Direct Server Return (DSR)**: An active-active edge layer of L4 load balancers receives the raw TCP traffic at high speeds. DSR is enabled. The L4 load balancers modify only the destination MAC address of incoming packets and forward them to the L7 tier. When backend servers respond, they send packets directly to the client gateway, bypassing the L4 load balancer entirely. This prevents the L4 load balancer from bottlenecking on outgoing network bandwidth.
2. **L7 Layer**: The L7 load balancers terminate the TLS connections. They read the URI paths of incoming requests:
   - Path `/static/*` gets routed to a lightweight Nginx pool tuned for static files.
   - Path `/api/checkout` gets routed to a high-compute Application Server pool.
   - Path `/api/upload` gets routed to a dedicated worker pool with long timeout limits.

This architectural shift prevents slow uploads from starving fast static asset deliveries. Decoupling the routes ensures targeted scaling for each specific bottleneck.

## Pros
- **High Availability**: Removes single points of failure. If a server crashes, the load balancer detects it and routes traffic around it.
- **Horizontal Scalability**: Allows you to add or remove servers seamlessly without client configuration changes.
- **SSL Offloading**: Centralizes decryption, saving valuable CPU cycles on your backend application servers.
- **Security Guard**: Serves as a reverse proxy, hiding your internal server IP addresses and filtering out DDoS attacks at the edge.

## Cons
- **Increased Complexity**: Adds a new infrastructure component to configure, monitor, maintain, and secure.
- **Potential Bottleneck**: If under-provisioned, the load balancer itself can become a performance bottleneck or a single point of failure.
- **State Management Pain**: Demands stateless backend architectures. Using sticky sessions to bypass this leads to uneven scaling and data loss on server failure.
- **Debugging Difficulty**: Tracing network errors becomes harder because requests transit through intermediate proxies and network address translation steps.

## Alternatives
- **Client-Side Load Balancing**: The client queries a service registry (like Consul or Eureka) to get a list of active server IPs. The client application then selects which server to contact directly, bypassing the central load balancer. This reduces hop latency but increases client complexity.
- **P2P / Mesh Architecture**: Services within a network communicate directly with each other using a sidecar proxy (like Envoy in a service mesh). The proxies negotiate routing decisions dynamically, eliminating the need for standalone physical load balancing appliances inside the private network.

## When to use it
- You are scaling an application past a single server instance to handle increased traffic.
- Your business requires continuous availability, and you must perform zero-downtime rolling deployments.
- You need to protect backend databases and APIs from direct public internet exposure.
- You want to distribute users geographically to minimize latency.

## When NOT to use it
- Your application runs easily on a single small server with 99% utilization headroom. Adding a load balancer introduces pointless cost and complexity.
- You have highly stateful legacy backends that store massive files or session states locally. A load balancer will break the application unless you rewrite the storage mechanism or rely heavily on problematic sticky sessions.

## Key takeaways / mental model
Think of DNS as a global map. It tells the driver which highway leads to the city, routing them based on general region. Think of the load balancer as the toll booth and lane distributor at the city entrance. It makes sure cars are sent down different lanes based on vehicle type (L7 routing) or raw numbers (L4 routing) so no single street becomes a bottleneck.

## Self-check questions
1. Why does a high TTL on DNS records slow down emergency failover during a data center outage?
2. What is the fundamental difference between Layer 4 and Layer 7 load balancing in terms of data visibility and CPU load?
3. How does the least-connections algorithm prevent the hotspot issues that commonly occur with round-robin distribution?
4. What are the operational risks of using sticky sessions, and how does consistent hashing provide a better alternative?
5. Why would an active-passive deployment configuration be selected over an active-active one for the load balancer tier itself?
6. When a client makes an HTTPS request, what are the security trade-offs of SSL termination versus SSL pass-through?

## References
- System Design Guide for Software Professionals (Sinha & Chopra), Chapter 4
- RFC 1035: Domain Names - Implementation and Specification
