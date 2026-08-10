---
id: distributed-systems/05
subject: distributed-systems
title: "Naming (Flat, Structured, Attribute-Based)"
slug: naming
status: drafted
mastery: 
seniority: senior
source: "Distributed Systems, 3rd ed. (van Steen & Tanenbaum), Chapter 5"
prerequisites: [distributed-systems/02, distributed-systems/04]
created: 2026-08-10
updated: 2026-08-10
---

# Naming (Flat, Structured, Attribute-Based)

## TL;DR
Naming is how a distributed system lets entities (machines, services, files, users) refer to each other stably, even as the underlying location or identity of the referenced thing changes. Flat naming resolves an opaque identifier to an address (via broadcast or a distributed lookup structure), structured naming organizes names hierarchically and resolves them step by step (DNS is the canonical worked example), and attribute-based naming finds entities by *what they are* rather than by a pre-known name (directory/LDAP-style lookup). Each trades resolution cost, flexibility, and scalability differently, and real systems typically layer all three.

## The idea
"Location transparency" (Lesson 01) requires that clients refer to resources without hard-coding their physical location - because location changes (a service moves hosts, a file replicates, a machine is replaced). A **name** is the stable handle a client uses; **name resolution** is the process of turning that name into something actionable (usually an address). Naming systems exist because a name and the thing it refers to must be allowed to evolve independently: you want to keep calling a service `payments-api` even after it moves from one data center to another, or gets replaced by a new set of machines entirely.

Van Steen and Tanenbaum organize naming schemes into three broad families based on how much structure the name itself carries and how resolution happens:
1. **Flat naming** - names are unstructured, opaque identifiers with no embedded information about location; resolution requires either broadcasting the query or consulting a lookup structure.
2. **Structured naming** - names are composed of a sequence of simpler names (like a path), and resolution proceeds hierarchically, delegating each segment to a more specific authority. DNS is the paradigm example.
3. **Attribute-based naming (directory services)** - instead of naming an entity directly, you describe the properties you want and the system finds entities matching that description. LDAP-style directories are the paradigm example.

## How it works

### 1. Flat naming: broadcast and distributed lookup
A flat name is just a bit string (e.g., a UUID, a MAC address, a content hash) with no internal structure a resolver can exploit - you cannot look at the name and infer anything about where the referenced entity lives. Resolving it requires one of two strategies:

- **Broadcast/multicast resolution** - ask every node on the network "who has entity X?" and let the owner respond. This is how ARP (Address Resolution Protocol) resolves an IP address to a MAC address on a local network. It works well at small scale (a LAN) but does not scale to a wide-area network - broadcasting a query to millions of nodes is prohibitively expensive.
- **Distributed lookup via a structured overlay (DHT)** - organize participating nodes into a distributed hash table, most commonly built on a hash ring like the one in `system-design/04`'s consistent hashing. A lookup for name X hashes X to a position on the ring and routes the query through the overlay (typically O(log N) hops in structured DHTs like Chord) to the node responsible for that position, which holds (or points to) the actual entity.

**Worked example.** A peer-to-peer file-sharing network wants to resolve a file's content hash to the set of peers currently hosting it. Broadcasting "who has hash H?" to every one of a million peers is infeasible. Instead, a Chord-style DHT places both peers and content hashes on a hash ring; a lookup for hash H is routed hop-by-hop toward the peer whose position on the ring is the closest successor to H, and that peer holds (or has a pointer to) the list of hosts serving that file. Each hop roughly halves the remaining distance around the ring, giving O(log N) hops for a million-node network - about 20 hops - versus O(N) for broadcast. This is the direct naming-layer analogue of consistent hashing's data-placement trick: instead of placing *data*, you're placing *name-to-location mappings*.

### 2. Structured naming: hierarchies and DNS as the worked example
A structured name is composed of a sequence of simpler component names, typically forming a tree (a **naming graph**), where each internal node can delegate resolution of the next component to a different authority. This is what lets naming scale to a wide-area network: no single node needs to know every name in the system, only the names (or delegation pointers) within its own local subtree.

**DNS (Domain Name System)** is the canonical worked example. A name like `api.payments.example.com` is resolved right-to-left through a hierarchy of authorities:

```
                    "." (root)
                   /    |    \
                 com   org   net   ...
                /
           example.com   (has its own nameserver)
              /
      payments.example.com   (may delegate further, or hold the record directly)
              /
   api.payments.example.com  -> A record: 203.0.113.42
```

Resolution proceeds as follows:
1. A resolver asks a **root server**: "who is authoritative for `.com`?" The root server returns the address of the `.com` **TLD (top-level domain) server** - it does not itself know about `example.com`.
2. The resolver asks the `.com` TLD server: "who is authoritative for `example.com`?" It returns the address of `example.com`'s **authoritative nameserver**.
3. The resolver asks `example.com`'s nameserver: "what is `api.payments.example.com`?" This nameserver either holds the record directly or points further down to a nameserver authoritative for the `payments.example.com` subdomain.
4. Eventually an authoritative server returns the actual **A record** (IP address) for `api.payments.example.com`.

This is **iterative resolution** (each server tells the resolver who to ask next, and the resolver does the asking) as opposed to **recursive resolution** (each server asks the next one on the resolver's behalf and passes back the final answer) - most real-world DNS resolvers use a mix: the client does one recursive query to a local resolver (e.g., its ISP's or a public resolver like 8.8.8.8), and that resolver performs the iterative walk down the hierarchy on the client's behalf, caching results along the way.

**Caching and TTLs.** Because walking the full hierarchy for every lookup would be slow, each DNS record carries a **TTL (time-to-live)**, and resolvers cache the answer for that duration. This is a direct, everyday instance of the classic distributed-systems trade-off: longer TTLs mean fewer lookups (better performance, less load on authoritative servers) but slower propagation of changes (if a record changes, clients with a cached, stale answer keep using the old value until the TTL expires) - this is why "DNS propagation" after a change can take anywhere from seconds to days depending on the TTL that was configured beforehand.

**Worked example: what happens when a company moves its API to a new IP.** `api.payments.example.com` currently has an A record `203.0.113.42` with a TTL of 3600 seconds (1 hour), cached by resolvers all over the internet. The company updates the record to `198.51.100.7`. Any resolver that already cached the old value continues returning `203.0.113.42` to clients for up to the remaining TTL - potentially up to an hour - even though the authoritative server now has the new answer. This is why teams planning a DNS-based migration often lower the TTL well in advance (e.g., to 60 seconds) so that, by the time the actual cutover happens, stale caches expire quickly and the new value propagates fast. Structured naming buys huge scalability (delegation means no single server is a bottleneck) at the direct cost of a caching-consistency lag that must be actively managed.

### 3. Attribute-based naming: directory services
Flat and structured naming both assume you already know the name you want to resolve. Sometimes you don't - you know *properties* of the thing you're looking for, not its name. **Attribute-based naming** (directory services) lets you query by attributes and get back matching entities.

The canonical example is **LDAP (Lightweight Directory Access Protocol)**: entries are organized in a tree (a Directory Information Tree), each entry has a set of attributes (e.g., `cn=Jane Doe`, `department=Engineering`, `email=jane@example.com`), and a query can search for entries matching an attribute filter (e.g., "find all entries where `department=Engineering` and `title=Manager`") rather than requiring you to already know a specific distinguished name.

**Worked example.** A corporate identity system needs to answer: "find every active employee in the `Payments` team whose role is `on-call engineer`." There is no single flat or hierarchical *name* that directly encodes this - you're searching by properties, not walking a known path. An LDAP-style directory stores each employee as an entry with attributes (`team=Payments`, `role=on-call-engineer`, `status=active`) and can execute this as an attribute filter across the directory, returning the matching set. Contrast this with DNS: DNS answers "what is the address of this known name?"; a directory service answers "which entities match this description?" - a fundamentally different query shape that structured naming alone cannot express efficiently (you would need either an exhaustive scan or a purpose-built index over every entity's attributes, which is exactly what a directory service provides).

### 4. How the three layer together in practice
Real systems rarely use only one naming style - they typically stack them:
- **Service discovery in a microservices platform** commonly uses structured naming (`payments.internal.example.com` resolved via internal DNS) *plus* attribute-based filtering at a higher layer (e.g., a service mesh routing based on labels like `version=canary` or `region=us-east`), *plus* flat naming underneath for content-addressed caching (e.g., referring to a specific deployed artifact by its content hash).
- **A CDN** uses structured naming (the customer-facing hostname resolves via DNS) to route to a *geographically appropriate* edge cluster, which is itself a form of attribute-based resolution (the "attribute" being "closest to this client's network location") layered under a structured name.

**Worked example: Kubernetes naming as a layered system.** A Kubernetes `Service` named `payments-api` in namespace `prod` gets a structured DNS name `payments-api.prod.svc.cluster.local`, resolved through the cluster's internal DNS hierarchy exactly like public DNS (delegation from cluster root down to the namespace). Underneath that structured name, Kubernetes performs attribute-based selection: the Service doesn't point to one fixed machine, it selects *any pod matching a label selector* (e.g., `app=payments-api`), which is attribute-based naming - the actual destination pod is found by matching attributes, not by a pre-known address. And at the lowest layer, each pod is ultimately addressed by a flat identifier (its IP, assigned dynamically, with no structure a human would recognize). This is the entire three-tier taxonomy from this lesson, operating in one production naming stack most engineers use daily without decomposing it this way.

## Pros
- **Flat naming**: names remain stable and meaningful even when the referenced entity relocates completely (a content hash names data, not a location); DHT-based resolution scales to huge numbers of participants without any single bottleneck.
- **Structured naming**: human-friendly, hierarchical delegation means no single authority needs global knowledge, enabling internet-scale name resolution (DNS resolves billions of names/day without any single server knowing them all); caching (TTLs) makes repeated lookups cheap.
- **Attribute-based naming**: lets you find entities by what you actually know about them (properties), rather than requiring a pre-known exact name - essential when the caller doesn't know (or care about) a specific identifier.

## Cons
- **Flat naming**: resolution requires either expensive broadcast (doesn't scale beyond a LAN) or a purpose-built distributed lookup structure (DHT) that adds real operational complexity and its own failure modes (churn, hot spots on the ring).
- **Structured naming**: caching for performance directly trades away consistency (stale TTLs); the hierarchy itself is a soft dependency chain - if an intermediate delegation point is unreachable, everything below it becomes unresolvable even if the final answer would otherwise be available.
- **Attribute-based naming**: query cost scales with how selective the attributes are and how the directory is indexed; poorly indexed attribute queries can require scanning large portions of the directory, and keeping attributes fresh (e.g., an employee's team) requires active synchronization from a source of truth.

## Alternatives
- **Hard-coded addresses (no naming layer at all)** - the simplest possible approach; works only for tiny, static systems where relocation never happens, and fails the instant anything needs to move, scale, or fail over.
- **Service registries with health-checked dynamic registration** (e.g., Consul, etcd-backed discovery, ZooKeeper) - a specialized, often lower-latency alternative to DNS for internal service discovery, typically combining structured naming (hierarchical keys) with active health checking so stale/dead entries are pruned faster than a DNS TTL would allow.
- **Content-addressed naming** (naming data by a cryptographic hash of its content, as in Git or IPFS) - a specific, powerful form of flat naming where the name itself guarantees integrity (the content can't change without the name changing), at the cost of names being unreadable to humans and requiring a separate mechanism (like structured naming) to give human-friendly aliases.

## When to use it
- Use **structured naming (DNS-style)** for anything a human needs to reference, anything crossing organizational/administrative boundaries, or anything needing internet-wide scale with delegated authority.
- Use **flat naming with a DHT** when entities need location-independent, content- or identity-based names at very large peer-to-peer or content-addressable scale, and no natural hierarchy exists.
- Use **attribute-based naming (directories)** when callers need to find entities by properties they know, not by an identifier they don't - user/employee directories, dynamic service selection by label (canary routing, region affinity), and any "find matching X" query.

## When NOT to use it
- Don't use flat naming with full broadcast resolution beyond a small local network - it does not scale, full stop; use a DHT or a structured/attribute-based alternative instead.
- Don't rely on very long DNS TTLs for anything that might need to fail over quickly (e.g., disaster recovery, blue-green cutovers) - the caching that makes DNS efficient is the same mechanism that will delay your emergency cutover; use short TTLs (or a purpose-built low-latency service registry) for anything requiring fast failover.
- Don't build an attribute-based directory query path for lookups that are actually always by a known, stable identifier - you're paying indexing and query complexity for flexibility nobody needs; plain structured or flat naming is simpler and faster.

## Key takeaways / mental model
Naming answers "how do I refer to something whose location or identity might change?" and the three families differ in what the name itself carries: flat names carry no structure (resolution needs broadcast or a DHT), structured names carry a hierarchy that lets resolution be delegated (DNS is the everyday example, and its TTL caching is the everyday example of the consistency-vs-performance trade-off), and attribute-based names aren't names at all but descriptions, resolved by matching properties rather than walking a path. Most production systems - as the Kubernetes example shows - stack all three, and recognizing which layer you're looking at (a structured hostname, an attribute-selected target, a flat content-addressed identifier) clarifies what guarantees and failure modes actually apply.

## Self-check questions
1. Explain why flat naming cannot scale using broadcast resolution beyond a small network, and describe how a DHT-based lookup achieves scalable resolution instead. What is the approximate hop complexity, and why?
2. Walk through, step by step, how a DNS resolver resolves `api.payments.example.com` from scratch (no cache), naming each authority consulted along the way.
3. A company sets a DNS TTL of 24 hours on a record it now needs to change urgently for an incident failover. What goes wrong, and what should the team have done differently in advance?
4. What makes attribute-based naming fundamentally different from structured naming as a query model? Give an example query that structured naming cannot answer efficiently but a directory service can.
5. Using the Kubernetes naming example, identify which part of the stack is structured naming, which is attribute-based, and which is flat, and explain what each layer buys.

## References
- *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum), Chapter 5: Naming
- `system-design/04` (Consistent Hashing) - the hash-ring mechanism underlying DHT-based flat-name resolution
- distributed-systems.net (free companion site for the source book)
