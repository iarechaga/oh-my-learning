---
id: distributed-systems/03
subject: distributed-systems
title: "Processes, Threads, and Virtualization"
slug: processes-threads
status: drafted
mastery: 
seniority: mid
source: "Distributed Systems, 3rd ed. (van Steen & Tanenbaum), Chapter 3"
prerequisites: [distributed-systems/02]
created: 2026-08-10
updated: 2026-08-10
---

# Processes, Threads, and Virtualization

## TL;DR
Distributed systems need units of concurrency (threads within a process for cheap parallelism, separate processes for isolation), models for how client and server processes are organized (multithreaded servers, worker pools, code that migrates itself to data), and a way to package and isolate those units for deployment (virtual machines for strong isolation, containers for lightweight isolation). Choosing the right combination is a trade-off between isolation, overhead, and how fast you can start/stop/move a unit of work.

## The idea
Every node in a distributed system ultimately runs processes and threads to do work, and how you structure that concurrency directly determines how well a single machine can serve many concurrent clients and how safely code can be deployed, updated, and moved. This lesson sits below the architecture decisions of Lesson 02: once you've decided a server exists, you still must decide how that server internally handles concurrent clients, and once you've decided a piece of code needs to run somewhere, you need a mechanism to package, isolate, and place it.

Three closely related questions this lesson answers:
1. **Concurrency**: threads vs. processes - how do you serve many things at once on one machine?
2. **Organization**: what shape does a client or server process take (single-threaded, multithreaded, worker-pool, or code that relocates itself)?
3. **Packaging/isolation**: how do you deploy a unit of code with predictable resource and security boundaries - full virtual machines or containers?

## How it works

### 1. Threads vs. processes for concurrency
A **process** has its own private address space (memory), its own file descriptors, and its own OS-level resources; creating one and switching between processes is relatively expensive, but a bug in one process cannot directly corrupt another process's memory - the OS enforces isolation. A **thread** shares its address space with every other thread in the same process; creating and switching threads is cheap (no separate address space to set up), which makes threads the natural choice for handling many concurrent requests inside one server - but a single wild thread (e.g., through a shared-memory bug) can corrupt state for every other thread in that process.

| Property | Process | Thread |
| --- | --- | --- |
| Address space | Private | Shared with siblings |
| Creation/switch cost | Expensive (new memory tables) | Cheap |
| Isolation from siblings | Strong (OS-enforced) | Weak (same memory) |
| Communication with siblings | Needs IPC (pipes, sockets, shared memory) | Direct (shared variables), but needs synchronization |
| Typical use in a server | Isolating independent workloads/tenants | Serving many concurrent requests within one workload |

**Worked example.** A web server handling 10,000 concurrent connections could, in principle, fork a new OS process per connection. Each connection gets full isolation, but with typical per-process overhead (megabytes of memory for page tables, kernel bookkeeping, and a relatively expensive `fork()`/context switch), 10,000 processes would exhaust memory and spend enormous CPU on context switching alone. Using a thread pool of, say, 200 threads sharing one process's address space, each thread handling a connection at a time, costs orders of magnitude less memory and switches far more cheaply - which is exactly why virtually every production server (nginx workers, JVM-based servers, Go's goroutines as an even lighter-weight variant) is built around threads or thread-like primitives rather than one-process-per-request. The trade is that a bug causing thread A to write to memory intended for thread B (a classic race condition) can silently corrupt another client's in-flight request - isolation is opt-in (via careful locking/immutable data), not free, the way OS process isolation is.

### 2. Server organization patterns
How a server structures its threads/processes to handle clients matters for both throughput and fault isolation:

- **Iterative server** - handles one request fully before starting the next. Simplest to reason about, but a single slow client (or slow downstream dependency) blocks every other client behind it - unacceptable for almost any real service.
- **Concurrent server, thread-per-request** - spawns (or pulls from a pool) a thread per incoming request, so slow requests don't block others. This is the dominant pattern for request/response servers (web servers, RPC servers).
- **Worker pool** - a fixed number of worker threads/processes pull work items off a shared queue. Bounds resource usage under load (you don't spawn unboundedly many threads when traffic spikes) at the cost of requests queueing when all workers are busy - this is a deliberate, tunable back-pressure mechanism rather than an accident, and it directly determines a service's saturation behavior under load.
- **Event-driven, single-threaded (reactor pattern)** - one thread handles many connections via non-blocking I/O and an event loop (Node.js, nginx's core event loop, Redis). Avoids thread-switching and locking overhead entirely for I/O-bound workloads, at the cost of a single CPU-bound operation stalling every other connection sharing that event loop - CPU-heavy work must be offloaded to a separate worker to avoid starving the loop.

**Worked example.** A payments API server chooses a worker pool of 50 threads, each backed by a connection to a downstream fraud-check service with a 200ms timeout. Under normal load, 50 concurrent in-flight requests comfortably keep up. During a downstream fraud-service slowdown (say, average latency rises to 190ms), all 50 workers saturate holding open, slow requests, and new incoming requests queue rather than fail outright - a graceful, boundeddegradation rather than an unbounded thread explosion that would eventually crash the process. This is the direct payoff of choosing worker-pool over unbounded thread-per-request: it converts an unbounded failure mode (out-of-memory from thread explosion) into a bounded, observable one (queue depth and latency), which is a strictly better failure to have to page someone about.

### 3. Client organization: code migration and mobile agents
Most clients are simple: a UI or CLI that talks to a server. But some systems move *code* to where the *data* lives instead of moving data to the code - useful when the data is large and the computation is small, so shipping the computation is cheaper than shipping the data over the network. This is **code migration**.

- **Weak mobility** - only the code (and maybe some initialization data) migrates; execution restarts from the beginning at the destination. Simpler to implement (e.g., shipping a script to run on a remote data node - the map-phase code in a MapReduce job moving to the node holding the data shard, rather than shipping the shard's data to a central compute node).
- **Strong mobility** - the code *and* its execution state (stack, program counter) migrate, so execution resumes exactly where it left off on the new machine. Far more powerful (e.g., live VM migration continues a running program mid-instruction) but also far more complex to implement correctly, since you must capture and faithfully restore an entire execution context.
- **Mobile agents** - a more general historical concept: autonomous pieces of code that travel between machines, carrying out tasks (gather price quotes from multiple stores, then return with results) without a continuous network connection back to their origin. Mobile agents never achieved mainstream adoption (the security implications of letting arbitrary foreign code execute on your machine were a major blocker, foreshadowing Lesson 12's threat-model discussion), but the *underlying idea* - moving computation to data instead of data to computation - persists directly in modern systems like MapReduce/Spark (ship the map function to the data node) and edge computing (ship inference code to an edge device rather than streaming raw sensor data to a data center).

**Worked example.** A log-analytics platform has 500GB of logs sitting on each of 20 storage nodes (10TB total). Instead of streaming all 10TB to a central compute cluster to run a grep-like filter (which would saturate the network for a long time), the platform ships a small filtering program (a few KB) to each of the 20 nodes, runs it locally against each node's 500GB, and only ships back the much smaller matched results. This is weak mobility in action: the code restarts fresh on each node, there's no need to preserve execution state across the move, and the trade (ship code, not data) is a direct, deliberate application of "which is smaller, the computation or the data?"

### 4. Virtualization: VMs vs. containers
Once you know what unit of work you want to run (a process, possibly multithreaded), you need to decide how to *package and isolate* it for deployment across a fleet of machines - this is where virtualization enters, and it operates at a different layer than the threads/processes above (it's about isolating and placing whole runtime environments, not about concurrency within one).

- **Full virtual machines (VMs)** - a hypervisor emulates entire virtual hardware, and each VM runs its own full OS kernel on top of that virtual hardware. Isolation is very strong (a VM cannot directly see or affect another VM's kernel or memory - the hypervisor mediates everything), but the overhead is significant: each VM duplicates an entire OS's memory footprint and boot time (often tens of seconds to minutes to start).
- **Containers** - processes that share the *host's* kernel but are isolated from each other using OS-level mechanisms (Linux namespaces for view isolation - PIDs, network, mounts - and cgroups for resource limits). Isolation is weaker than a VM (a kernel-level exploit can potentially escape a container and affect the host or siblings, since there's only one kernel underneath all of them), but overhead is dramatically lower: containers start in a fraction of a second to a few seconds and share the host kernel's memory rather than duplicating it.

| Property | VM | Container |
| --- | --- | --- |
| Isolation boundary | Hypervisor + separate kernel per VM | Shared host kernel, OS-level namespaces |
| Isolation strength | Strong | Weaker (shared kernel = larger attack surface) |
| Startup time | Seconds to minutes | Milliseconds to seconds |
| Resource overhead | High (duplicated OS per VM) | Low (shared kernel, thin layer per container) |
| Density per host | Lower | Higher |
| Typical use | Multi-tenant isolation where a kernel-level exploit must not cross tenants; running different OS kernels on one host | Fast-scaling microservices where tenants trust a common kernel/orchestrator |

**Worked example.** A cloud provider offering VMs to the general public (where a malicious customer's workload might sit on the same physical host as a competitor's) uses full VM isolation deliberately - the strong hypervisor boundary is worth the overhead because the isolation requirement is adversarial (Lesson 12's threat model applies directly: you cannot trust co-tenants). A company running its own 200 internal microservices, all owned by teams within the same organization and orchestrated by the same trusted platform (e.g., Kubernetes), uses containers - the isolation requirement is about fault/resource containment between services, not defending against actively adversarial co-tenants, so the lighter, faster, denser container model is the better trade. Many production platforms in fact combine both: containers running inside lightweight VMs (e.g., AWS Firecracker microVMs) to get container-like density and startup speed with closer-to-VM isolation strength, precisely because "container isolation is good enough" stops being true once workloads from mutually-untrusted parties share a host.

## Pros
- **Threads over processes**: dramatically cheaper concurrency, enabling servers to handle very large numbers of simultaneous clients.
- **Worker pools**: bounded, predictable resource usage and graceful (rather than catastrophic) degradation under overload.
- **Code migration**: avoids shipping large data across the network when computation is cheap to move instead.
- **Containers over VMs**: fast startup, high density, and simpler image-based deployment - a major enabler of modern elastic, microservice-based architectures.
- **VMs over containers**: strong isolation that tolerates mutually-untrusted or adversarial co-tenants.

## Cons
- **Threads**: weak isolation - a bug in one thread's shared-memory access can corrupt state used by every other thread in the process; requires careful synchronization discipline.
- **Worker pools**: under sustained overload, requests queue and latency rises rather than the system doing (bounded) more work - capacity planning and queue-depth alerting become necessary.
- **Code migration/mobile agents**: security risk of executing foreign code on a machine (never fully solved historically); complex to implement (especially strong mobility, which needs full execution-state capture).
- **Containers**: weaker isolation than VMs - a kernel-level vulnerability can, in principle, escape a container and affect the host or sibling containers.
- **VMs**: high resource overhead and slow startup make them a poor fit for fast elastic scaling or high-density multi-tenant workloads.

## Alternatives
- **Serverless/FaaS (functions-as-a-service)** - an even lighter-weight unit than a container: the platform manages process/container lifecycle entirely, you supply only a function. Trades control over the runtime environment for near-zero operational overhead; good for spiky, event-driven workloads, poor for long-running stateful processes.
- **Unikernels** - specialize an entire minimal OS image around a single application, compiled together, aiming for VM-level isolation with much smaller footprint and faster boot than a general-purpose VM. Niche adoption due to tooling and debugging immaturity relative to containers.
- **WebAssembly (Wasm) sandboxes** - an increasingly used lightweight isolation mechanism (sandboxing at the instruction level rather than OS level) for running untrusted code with near-native speed and very fast startup - an emerging alternative to containers for certain edge/plugin workloads.

## When to use it
- Use **threads/worker pools** whenever a server must handle many concurrent I/O-bound clients on one machine - almost always, for typical request/response services.
- Use **code migration** (weak mobility) when the data to be processed is large relative to the code that processes it and staying near the data avoids a network bottleneck (this is the entire justification behind MapReduce/Spark's execution model).
- Use **containers** as the default packaging/isolation unit for internal microservices owned by a single trusted organization needing fast, elastic scaling.
- Use **VMs** (or containers-inside-VMs) when workloads from mutually untrusted parties must share physical hardware, or when you need to run a different OS kernel than the host provides.

## When NOT to use it
- Don't reach for one-process-per-request under any significant concurrency - the memory and context-switch overhead will not scale; use threads or an event loop instead.
- Don't build custom code-migration/mobile-agent machinery for a problem that a simpler request/response call or a well-established batch framework (Spark, MapReduce) already solves - mobile agents' security and complexity costs rarely pay for themselves for anything short of "genuinely enormous data staying genuinely put."
- Don't use containers alone as your isolation boundary when tenants are truly adversarial (public multi-tenant cloud offerings, running arbitrary user-submitted code) - the shared kernel is a real attack surface; use VMs or a VM-backed container runtime instead.
- Don't use full VMs for fast-scaling internal microservices where startup latency and density matter and all workloads are mutually trusted - the overhead buys isolation strength you don't need at a real cost to elasticity.

## Key takeaways / mental model
Threads vs. processes is a *concurrency-within-a-machine* decision (cheap, shared-memory parallelism vs. expensive, isolated parallelism); VMs vs. containers is a *deployment/isolation-across-a-fleet* decision (strong hypervisor-enforced isolation vs. lightweight shared-kernel isolation); and code migration is a reminder that "move the computation to the data" is sometimes cheaper than the default "move the data to the computation." All three decisions trade isolation and safety against overhead and speed, and the right answer depends on how much you trust the thing you're isolating against - a co-located thread you wrote yourself, a container running your own team's code, or a VM running a stranger's.

## Self-check questions
1. Why do production servers overwhelmingly use threads (or event loops) rather than one process per connection, and what specific costs does the process-per-connection approach incur at scale?
2. Explain the difference between weak and strong code mobility. Give a real system that uses weak mobility and explain why strong mobility wasn't needed there.
3. A platform team wants to move 200 internally-owned microservices from VMs to containers to cut cloud costs. What isolation assumption are they implicitly relying on, and under what circumstance would that assumption break?
4. Design a worker-pool sizing strategy for a service with a 200ms downstream timeout and a target of surviving a downstream slowdown without running out of memory. What happens to latency and queue depth as the downstream service degrades?
5. Why is "container isolation is basically as good as VM isolation" a dangerous oversimplification for a public multi-tenant cloud provider, but a reasonable simplification for an internal microservices platform?

## References
- *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum), Chapter 3: Processes
- distributed-systems.net (free companion site for the source book)
