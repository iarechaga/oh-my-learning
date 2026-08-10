---
id: distributed-systems/02
subject: distributed-systems
title: "Architectures and Middleware"
slug: architectures-middleware
status: drafted
mastery: 
seniority: senior
source: "Distributed Systems, 3rd ed. (van Steen & Tanenbaum), Chapter 2"
prerequisites: [distributed-systems/01]
created: 2026-08-10
updated: 2026-08-10
---

# Architectures and Middleware

## TL;DR
Distributed-system architecture is the choice of how components are organized (layered, tiered, or microkernel-style) and how they are *coordinated* across the network (centralized client-server, fully decentralized peer-to-peer, or a hybrid). Middleware is the software layer that sits between the operating system and applications specifically to make that coordination easier - it provides the naming, communication, and consistency primitives so application code doesn't reinvent them. Choosing an architecture is choosing where control, state, and failure domains live, and that choice shapes every scalability and consistency trade-off downstream.

## The idea
Once you accept that a system will be distributed (Lesson 01), you face a design question that recurs at every layer: **how should the pieces be organized, and who talks to whom?** Van Steen and Tanenbaum separate this into two related but distinct questions:

1. **Software architecture** - how is a single application's logic structured into layers or components (independent of where those components physically run)? This is the layered / tiered / microkernel distinction.
2. **System architecture** - how are those components physically placed and how do they communicate at runtime? This is the centralized / decentralized / hybrid organization.

The two interact: a logically layered application (presentation, logic, data) can be deployed as a single process, or split across physical tiers (2-tier, 3-tier), or further decomposed into microservices communicating peer-to-peer. Middleware exists because, once you make these choices, you need reusable machinery - RPC stubs, message queues, naming services, transaction coordinators - so every team doesn't hand-roll socket code and ad hoc retry logic. Getting the architecture right early matters because architecture decisions are expensive to reverse: a system built assuming a single centralized database is hard to retrofit into a peer-to-peer, leaderless design without a rewrite.

## How it works

### 1. Software architecture: layers, tiers, and microkernels

**Layered architecture.** Each layer only calls the layer directly below it and only exposes services to the layer directly above it (a classic example: application logic sits on top of a data-access layer, which sits on top of a storage layer). This is a *logical* decomposition - it says nothing yet about which layer runs on which machine.

**Tiered architecture** takes a layered design and assigns each layer (or group of layers) to a physical tier:
- **1-tier**: everything (presentation, logic, data) on one machine - not really distributed.
- **2-tier (client-server)**: e.g., a "fat client" holds presentation and logic, a server holds data; or a "thin client" holds only presentation, and the server holds logic and data. The split point matters: pushing more logic to the client reduces server load but couples clients tightly to server-side data formats and complicates upgrades (every client must be updated together).
- **3-tier**: presentation, business logic, and data are each their own tier, typically presentation (web/mobile client) -> application server (business logic) -> database. This is the dominant pattern for web applications because it lets each tier scale and fail independently - you can add application servers without touching the database tier.

**Microkernel architecture** pushes decomposition further: a minimal core (the "microkernel") provides only the most essential mechanisms (e.g., message passing, basic scheduling), and everything else - file systems, network stacks, even device drivers in an OS context, or in an application context: plugins, extensions - runs as replaceable, independent modules that communicate with the core and each other through well-defined interfaces. The point is extensibility and fault isolation: a misbehaving module can be replaced or restarted without touching the trusted core. This pattern echoes in application-level "plugin" architectures and in service meshes, where a small trusted control plane manages many independently-deployed data-plane components.

### 2. System architecture: centralized, decentralized, and hybrid organizations

**Centralized (client-server).** One or a small number of servers hold state and process requests; many clients connect to them. Simple to reason about (there's one place state lives), easy to secure (one boundary to defend), and straightforward to keep consistent (Lesson 08's strong-consistency models are natural here). The cost is exactly the "hidden centralization" pitfall from Lesson 01: the server(s) become the scalability ceiling and a shared point of failure unless deliberately made redundant (with the redundancy itself needing coordination - see Lessons 07 and 10).

**Decentralized (peer-to-peer, P2P).** No node is privileged; every node can act as both client and server ("servent"). Two common sub-structures:
- **Structured P2P** - nodes are organized into a specific topology (commonly a distributed hash table, or DHT, built on a ring like the one in `system-design/04`'s consistent hashing), so a lookup for a given key follows a predictable path, typically O(log N) hops.
- **Unstructured P2P** - nodes connect somewhat arbitrarily and lookups happen by flooding or gossip (Lesson 07 covers gossip protocols in depth). Easier to build and more resilient to churn, but lookups are less efficient and less predictable.

P2P systems scale well precisely because there is no central bottleneck, and they tolerate node churn gracefully (nodes joining and leaving is the normal case, not an exception). The cost is operational and consistency complexity: with no authoritative node, achieving a strongly consistent view of the system (Lesson 08) or running consensus (Lesson 10) is substantially harder, and security is harder too (Lesson 12's Sybil-attack discussion is a direct consequence of "no privileged node to vouch for identity").

**Hybrid architectures** combine both. Two important patterns:
- **Edge-server / CDN architectures** - a centralized origin holds authoritative data, but edge servers (geographically close to users) cache and serve copies, pushing computation and data physically near clients to cut latency (this is "geographical scalability" from Lesson 01 made concrete).
- **Cloud/superpeer architectures** - most nodes are ordinary peers, but a subset of more capable nodes ("superpeers") take on coordination duties (e.g., indexing which peers hold which data), forming a two-level hierarchy. This gets some of P2P's scalability without fully giving up the ease of coordination that a bit of hierarchy provides. Modern cloud-native systems (a Kubernetes control plane coordinating many stateless worker pods, for example) are a hybrid in this spirit: centralized control plane, decentralized data plane.

**Worked example: three architectures for the same feature.** Suppose you're building a global chat presence service (who's online right now). 
- *Centralized*: every client connects to one presence server cluster; the cluster holds all online/offline state. Simple, strongly consistent, but the server cluster is a single scaling bottleneck and, if it's in one region, adds real latency for distant users.
- *Decentralized P2P*: presence is gossiped between clients directly (Lesson 07's gossip protocols), with no server at all. Scales beautifully and has no central point of failure, but "who is online" becomes eventually consistent - two users might briefly disagree about a third user's status, and building this correctly (handling churn, avoiding stale rumors) is meaningfully harder engineering.
- *Hybrid (regional edge)*: each region runs its own presence cluster (a "superpeer" per region); regions gossip aggregate state between each other. Users get low latency to their region's cluster, the system survives a single region's failure, and full global consistency is relaxed to eventual consistency only between regions, which is usually an acceptable trade for a presence feature.

This is the recurring shape of the decision: centralization buys consistency and simplicity, decentralization buys scale and resilience, and hybrids are usually where production systems land once the trade-offs are made explicit.

### 3. Middleware: what it actually provides
Middleware is software that sits logically between the operating system (which manages one machine) and distributed applications (which need many machines to behave like one). It exists because the primitives an OS gives you - sockets, threads, files - are too low-level to build distributed applications productively; every team would otherwise reinvent request/response framing, retries, service discovery, and failure handling. Concretely, middleware provides:

- **RPC middleware** - makes a remote procedure call look like a local function call (marshaling arguments, handling the network round trip, unmarshaling the result). Covered in depth in Lesson 04; examples include gRPC, Java RMI, and older CORBA/DCOM systems.
- **Message-oriented middleware (MOM)** - provides asynchronous, queue-based communication between components that don't need to be up at the same time (e.g., RabbitMQ, Kafka, or a cloud provider's managed queue). Also covered in Lesson 04.
- **Distributed transaction / commit coordination middleware** - implements protocols like two-phase commit (Lesson 11) so multiple independent resource managers can agree on committing or aborting a transaction together.
- **Naming and directory middleware** - services like DNS (Lesson 05) or LDAP that let components find each other by name rather than hard-coded address.
- **Object/service middleware** - frameworks (historically CORBA, today things like service meshes) that manage the lifecycle, discovery, and communication of distributed components as a set of addressable services.

The unifying theme: middleware absorbs the fallacies from Lesson 01 (network unreliability, latency, security) into a reusable layer, so application developers can write closer to "call this function" or "publish this event" and rely on the middleware to handle the actually-hard distributed parts underneath - imperfectly, but consistently, instead of every team getting it wrong slightly differently.

### 4. Worked example: evolving an architecture as an organization grows
A startup begins with a monolith: 1-tier, a single server process talking to a single database - the whole "distributed system" is really just one machine plus a database, which itself may or may not be on a separate box. As traffic grows, they split into a classic 3-tier design: stateless web/app servers (scaled horizontally, load balanced) in front of a single primary database (still centralized at the data tier). This is centralized client-server dressed up with a scalable middle tier - a very common and very sound production shape.

As the company grows further and multiple teams need to deploy independently, the app tier decomposes into microservices - each owning its own data store, communicating via RPC (Lesson 04) for synchronous needs and message queues (MOM) for asynchronous ones. This is architecturally a move toward decentralization at the service level, though each individual service is often still internally centralized (one primary datastore per service). Full peer-to-peer only shows up if the company builds something like a CDN edge layer, a P2P content-distribution feature, or a blockchain-adjacent product - most business systems never need to go that far, and shouldn't, because P2P's consistency and security costs (Lessons 08, 12) are steep for problems that don't need P2P's scale/resilience profile.

## Pros
- **Centralized**: simplest to reason about, easiest to keep strongly consistent, easiest to secure (few boundaries), fastest to build.
- **Decentralized/P2P**: no single point of failure, scales with the number of participants, tolerates churn gracefully, no organization needs to own or trust a central authority.
- **Hybrid**: captures most of the latency/resilience benefits of decentralization while keeping coordination tractable through limited centralization (superpeers, regional clusters).
- **Middleware generally**: eliminates duplicated, error-prone reimplementation of communication, naming, and coordination logic across every team/service.

## Cons
- **Centralized**: single scaling ceiling and (absent deliberate redundancy) a single point of failure; geographically distant users pay latency to reach the center.
- **Decentralized/P2P**: hard to achieve strong consistency or run consensus cheaply; harder to secure (no privileged node to anchor trust, Sybil attacks - Lesson 12); operationally harder to debug (no single place to look).
- **Hybrid**: adds architectural complexity - now you must reason about two different consistency/failure models (within a region and across regions) instead of one.
- **Middleware generally**: another layer of abstraction that can hide failure in ways that surprise you (over-eager retries, silent timeouts) if you don't understand what it's doing underneath; version/compatibility management across services becomes its own maintenance burden.

## Alternatives
- **Serverless/FaaS platforms** - push architecture decisions (scaling, placement, even some coordination) onto the cloud provider's middleware entirely; you write handlers and the platform decides physical topology. Good when operational ownership is the scarce resource, less good when you need fine control over consistency or latency characteristics.
- **Service mesh (Istio, Linkerd)** - a specific hybrid pattern: a decentralized data plane of service proxies coordinated by a centralized control plane, providing middleware-like capabilities (retries, mTLS, discovery) transparently at the network layer instead of in each application's code.
- **Shared-nothing vs. shared-disk architectures** (a lower-level cousin of this decision) - shared-nothing (each node owns its own storage, communicates only via network, the default assumption throughout this subject) versus shared-disk clusters (multiple nodes access the same physical storage, common in some enterprise databases). Shared-disk sidesteps some partitioning problems but reintroduces a form of centralization at the storage layer.

## When to use it
- **Centralized client-server**: when strong consistency, simplicity, and fast time-to-build matter more than raw horizontal scale or resilience to a single region/data-center outage - the default starting point for most applications.
- **Decentralized/P2P**: when there is no natural single owner of the system (file sharing, some blockchain and collaborative applications), when resilience to any single node's failure is paramount, or when the scale genuinely exceeds what any centralized design could serve.
- **Hybrid**: when you need low latency for a geographically spread user base (edge/CDN) or need to combine centralized governance with decentralized execution (cloud control-plane/data-plane patterns, superpeer designs) - this is where most large production systems actually sit.

## When NOT to use it
- Don't reach for decentralized/P2P just because it sounds more "modern" or "webscale" - if a small team can operate a well-replicated centralized service reliably, the operational and consistency costs of full decentralization are rarely worth paying without a concrete scale or trust requirement forcing the issue.
- Don't adopt heavy middleware (a full service mesh, a distributed transaction coordinator) before the number of services or the cross-service coordination need justifies it - middleware has real operational cost (another system to run, understand, and debug) and is not free insurance against complexity you don't yet have.
- Don't build a microkernel-style plugin architecture for a system with a small, stable, well-known set of components - the extensibility microkernels buy you is wasted machinery if nothing is actually going to be swapped or extended independently.

## Key takeaways / mental model
Software architecture (layered/tiered/microkernel) answers "how is the logic decomposed?" System architecture (centralized/decentralized/hybrid) answers "where does that logic physically run and who talks to whom?" Middleware is the load-bearing glue that makes the second question tractable: it absorbs the fallacies of distributed computing into reusable primitives (RPC, messaging, naming, transactions) so application code doesn't have to. When evaluating any distributed design, separate these two questions explicitly - a "microservices" system can still be architecturally centralized if every service ultimately depends on one shared database, and a "monolith" can be internally layered cleanly without being distributed at all.

## Self-check questions
1. Explain the difference between a layered software architecture and a tiered system architecture. Can a 3-tier system architecture host a non-layered application? Why does this distinction matter when discussing "architecture" with colleagues?
2. Compare centralized client-server, structured P2P, and unstructured P2P along three axes: consistency, scalability, and resilience to node churn. Give one system that fits each.
3. A team says "we moved to microservices, so we're now decentralized." Under what circumstances would that claim be false despite the service decomposition?
4. Name three concrete responsibilities middleware takes off an application developer's plate, and for each, describe a bug class that appears when a team reimplements that responsibility badly by hand instead of using established middleware.
5. Design a hybrid architecture for a global multiplayer game's matchmaking service. Where would you centralize, where would you decentralize, and why?

## References
- *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum), Chapter 2: Architectures
- distributed-systems.net (free companion site for the source book)
