---
id: designing-distributed-systems/01
subject: designing-distributed-systems
title: "Why Distributed Patterns (Containers as Building Blocks)"
slug: why-distributed-patterns
status: drafted
mastery:
seniority: mid
source: "Designing Distributed Systems (Brendan Burns), Introduction and Chapter 1"
prerequisites: []
created: 2026-07-01
updated: 2026-07-01
---

# Why Distributed Patterns (Containers as Building Blocks)

## TL;DR
Distributed systems used to be rebuilt from scratch every time because we had no shared vocabulary of reusable pieces. Containers changed that: a container is a self-contained, independently deployable, boundary-enforcing unit, and once you have that unit you can name and reuse the arrangements of containers - the patterns - just like object-oriented programming named reusable arrangements of objects. This lesson explains why the container is the right building block, what properties make a good building block, and how the rest of this subject is a catalog of patterns built on top of it.

## The idea
Building a reliable distributed system is hard, and for most of computing history every team built one from the ground up. They re-invented the same load balancers, the same retry-and-timeout wrappers, the same leader-election dances, the same batch pipelines - each time slightly differently, each time with fresh bugs. There was craft but no engineering discipline, because there was no agreed set of reusable components and no vocabulary to describe how to assemble them.

Compare this to the history of software *inside* a single machine. Early programs were also written from scratch. Then came standard patterns: subroutines, then objects, then design patterns (Factory, Adapter, Observer). A "design pattern" is not code you copy; it is a *named, reusable solution to a recurring problem*, so two engineers can say "use an Adapter here" and immediately share a mental model. The pattern needs a **building block** to operate on. In object-oriented design that block is the object: a bundle of state and behavior with a clear interface and an enforced boundary (you cannot reach past `private`).

Distributed systems lacked an equivalent building block until containers matured. A **container** (as popularized by Docker and orchestrated by systems like Kubernetes) packages a process together with its dependencies into an image, runs it in an isolated sandbox, and exposes it only through declared interfaces (ports, files, environment). That isolation and self-containment is exactly the property that lets us treat a container the way we treat an object: as a reusable unit we can compose into larger structures. Once the unit exists, the *patterns* become nameable and reusable - and cataloging those patterns is what this whole subject is about.

The core claim of this subject: **the same forces that made object-oriented patterns valuable (reuse, shared vocabulary, separation of concerns, testability) apply to distributed systems, and containers are the object that makes distributed patterns possible.**

## How it works

### What makes something a good building block
Not every unit of software is a good building block for patterns. Burns identifies the properties a building block must have, and they map almost one-to-one onto the properties of a good object.

1. **Self-contained / a boundary of encapsulation.** The block hides its internals behind an interface. Other blocks depend on *what* it does, not *how*. A container image bundles the binary, libraries, and runtime so there is nothing to "also install" - the boundary is the image.
2. **Independently deployable and upgradeable.** You can ship, restart, roll back, or scale the block without touching the ones next to it. A container has its own lifecycle managed by the orchestrator.
3. **Well-defined interface.** Interaction happens only through declared contracts - network ports, mounted files, environment variables. Nothing reaches in through a side door.
4. **Reusable across contexts.** The same block can be dropped into many systems. A logging sidecar or a TLS-terminating proxy should not care what application it sits next to.
5. **Language- and runtime-agnostic at the boundary.** Because the interface is the network or the filesystem, a Go container can sit next to a Python container and neither knows the other's language. This is the distributed analog of "program to an interface, not an implementation."

```text
Object (in-process)                 Container (distributed)
+---------------------+             +-------------------------+
|  private state      |             |  process + deps (image) |
|  ------------------ |             |  ----------------------- |
|  public methods  <--+-- caller    |  network ports / files <-+-- other
+---------------------+             +-------------------------+
   boundary = access                    boundary = sandbox +
   modifiers (private)                  declared interface
```

The parallel is the whole point: if you already know why objects made in-process code reusable and testable, you already know why containers make distributed code reusable and testable.

### Why the container specifically (and not a VM or a bare process)
It is worth being precise about why the container, and not older units, unlocked patterns.

- **A bare process** is not self-contained: it depends on whatever happens to be installed on the host (the "works on my machine" problem). It has no portable boundary, so you cannot reliably drop it into another system.
- **A virtual machine (VM)** *is* self-contained and isolated, but it is heavy: it ships an entire guest operating system, boots in tens of seconds to minutes, and consumes gigabytes. You would not casually put five VMs around one application just to add logging, a proxy, and a config-watcher - the overhead dwarfs the app. Patterns need the block to be *cheap enough to use liberally*.
- **A container** is self-contained like a VM but shares the host kernel, so it starts in milliseconds and adds megabytes, not gigabytes. It is cheap enough that composing *several* containers into one deployable unit (the multi-container pod, covered by the sidecar/ambassador/adapter patterns) is practical.

The economic point matters: a building block is only useful for patterns if using it is cheap. Containers hit the sweet spot of "isolated enough to be a boundary, light enough to use everywhere."

### The two axes the patterns are organized along
This subject's patterns divide along two questions. Keeping them straight now makes the rest of the catalog easy to place.

1. **Single-node vs multi-node.** Some patterns coordinate containers that run *together on one machine* and share a lifecycle (a Kubernetes pod). These are the *single-node* patterns: **sidecar**, **ambassador**, **adapter**. Others coordinate containers *spread across many machines*. These are the *multi-node* patterns: **replicated load-balanced services**, **sharded services**, **scatter/gather**, **leader election**, **work queues**.
2. **Serving vs batch.** Some systems run forever and respond to requests as they arrive (*serving* systems: replicated, sharded, scatter/gather). Others process a finite body of work and finish (*batch* systems: work queues, event-driven batch, coordinated batch).

```text
                     single-node            multi-node
                 (share one machine)   (spread across machines)
                +--------------------+ +----------------------------+
   serving      | sidecar            | | replicated load-balanced   |
   (long-lived) | ambassador         | | sharded                    |
                | adapter            | | scatter/gather             |
                |                    | | leader election            |
                +--------------------+ +----------------------------+
   batch        |  (single-node      | | work queues                |
   (finite)     |   batch is rare)   | | event-driven batch         |
                |                    | | coordinated batch          |
                +--------------------+ +----------------------------+
```

### Worked example 1: the same problem solved twice, badly, then once as a pattern
Suppose two teams each need to add HTTPS to an existing plain-HTTP application they cannot modify (no source, or a frozen legacy binary).

- **Team A** forks a copy of the app's deployment scripts, bakes an nginx build into the same VM image, hand-writes an init script to start nginx before the app, and wires certificates through a custom shell step. It works, but it is glued to *this* app and *this* VM image.
- **Team B**, months later, needs the same thing for a different app. They cannot reuse Team A's work because it was fused to Team A's app. They rebuild it slightly differently, with a different cert-rotation bug.

Now the pattern version: define a **TLS-termination sidecar** container - a small nginx-or-envoy image that listens on 443, terminates TLS, and forwards plain HTTP to `localhost:8080`. Drop it into the pod next to *any* app that serves on 8080. Team A and Team B use the *identical* container; the only per-app difference is configuration. The pattern converted a bespoke, non-reusable hack into a named, reusable unit. (The sidecar pattern is lesson 02.)

The lesson of the example: the container did not just "run the proxy." It made the proxy *a reusable building block with a boundary*, which is what let the solution become a pattern instead of a one-off.

### Worked example 2: separation of concerns and independent teams
Consider an application pod with three containers: the **application** (owned by the product team), a **log-shipping sidecar** (owned by the observability team), and a **metrics-exporter sidecar** (owned by the SRE team).

Trace what independence buys you:

1. The observability team ships a new log-shipper version with a security patch. They update *only* the log-shipper image tag. The application container is not rebuilt, retested, or redeployed by the product team.
2. The application container crashes and restarts. The metrics exporter, in its own container, keeps running and can even report the restart.
3. The product team writes their app in Rust; the log shipper is a Go binary; the metrics exporter is written in whatever the SRE team prefers. None of them share a language, a dependency tree, or a release cadence - only the pod boundary and localhost interfaces.

This is separation of concerns realized at the deployment layer. Without a boundary-enforcing building block, all three concerns would be tangled into one binary, one release, one language, one on-call rotation.

### Worked example 3: numbers on why the block must be cheap
Imagine adding three helpers (proxy, log shipper, config-watcher) around one app instance, and you run 200 instances.

- **VM-based helpers:** each helper VM ~1 GB RAM and ~30 s boot. Three helpers x 200 instances = 600 helper VMs, ~600 GB of RAM just for helpers, and minutes of aggregate boot time on every rollout. Nobody does this - so instead the helpers get *baked into the app image*, destroying reuse and separation of concerns.
- **Container-based helpers:** each helper container ~20 MB RAM and ~50 ms start. Three x 200 = 600 helper containers, ~12 GB of RAM, near-instant start. Now it is *cheaper to keep them separate than to merge them*, so the good design (reusable, isolated helpers) is also the practical one.

The pattern catalog only exists because the container made the "right" structure the affordable structure. When the building block is cheap, good architecture stops fighting economics.

## Pros
- **Reuse:** patterns turn bespoke distributed hacks into named, shareable components (a TLS sidecar, a sharding proxy) that drop into many systems.
- **Shared vocabulary:** "put an ambassador in front of it" or "this is a scatter/gather" lets engineers communicate designs precisely, the same way "use a Factory" does in OOP.
- **Separation of concerns:** each concern (the app, logging, proxying, config) lives in its own container with its own lifecycle, owner, and language.
- **Testability:** a container with a declared interface can be tested in isolation and swapped for a stub, just like an object behind an interface.
- **Independent deployment and scaling:** blocks upgrade, roll back, and scale on their own schedule.

## Cons
- **Orchestration overhead:** patterns assume an orchestrator (Kubernetes or similar) to schedule pods, restart failures, and manage lifecycles - a real operational cost and learning curve.
- **More moving parts:** three containers in a pod is three things to monitor, secure, and reason about instead of one process.
- **Boundary tax:** communication across the container boundary (even localhost) is serialization plus a network hop, not a function call - slightly slower and requiring a wire format.
- **Not every problem is a distributed one:** wrapping a trivial single-process app in the full pattern machinery is over-engineering (see When NOT to use it).

## Alternatives
- **Monolithic single binary:** put every concern in one process. Simplest to deploy and fastest in-process, but no reuse across systems, no independent scaling, no separation of concerns, and one language for everything.
- **Virtual machines as the unit:** isolated and self-contained, but too heavy to compose liberally; forces you to bake helpers into the app image, losing reuse.
- **Language-level libraries / frameworks:** share a logging or retry *library* instead of a *container*. Works only within one language and couples every service to the library's release; the container boundary is language-agnostic where a library is not.
- **Serverless functions:** an even smaller unit than a container for event-driven work (covered in lesson 08), but not a general replacement for long-lived serving containers.

## When to use it
- You are building or operating a system that must scale across multiple machines, tolerate partial failure, or evolve independently by team.
- You want to reuse infrastructure concerns (proxying, TLS, logging, sharding) across many services rather than re-implementing them each time.
- You have (or can adopt) a container orchestrator, so the lifecycle management the patterns assume actually exists.
- Multiple teams or languages must cooperate in one system and you want boundaries between their concerns.

## When NOT to use it
- The application is a single small process with modest, single-machine load and no reuse or multi-team pressure - the orchestration and multi-container overhead is pure cost.
- You have no orchestrator and no appetite to run one; many patterns (restart-on-failure, replication, leader election) lean on the orchestrator's guarantees.
- Ultra-low-latency in-process paths where even a localhost boundary hop is unacceptable - keep that hot path inside one process and apply patterns only around it.

## Key takeaways / mental model
Think of the container as the **object of distributed systems**. An object made in-process code reusable by giving state+behavior a boundary and an interface; the container does the same for a whole process, so arrangements of containers - the *patterns* - become nameable and reusable. Two rules of thumb:

1. **A building block is only useful if it is cheap to use.** Containers won because they are isolated like VMs but light like processes, making the "separate, reusable" design the affordable one.
2. **Place every pattern on two axes:** single-node vs multi-node (does it share one machine or span many?) and serving vs batch (does it run forever answering requests, or process a finite job and stop?). Every later lesson is one cell of that grid.

## Self-check questions
1. What five properties make something a good "building block" for patterns, and how does a container satisfy each?
2. Why did containers, rather than virtual machines or bare processes, unlock reusable distributed-system patterns? Give both the isolation argument and the cost argument.
3. In what sense is a container the distributed-systems analog of an object in OOP? Where does the analogy hold and where does it strain?
4. Classify each of these on the single-node/multi-node and serving/batch axes: a TLS sidecar, a sharded cache, a work queue, a scatter/gather search.
5. Using worked example 3's reasoning, explain why "cheap building block" is a precondition for good architecture rather than a mere convenience.
6. Give a concrete situation where applying these patterns would be over-engineering, and say what you would do instead.

## References
- Designing Distributed Systems (Brendan Burns), Introduction and Chapter 1: "Introduction to Distributed Systems"
- [system-design/06 - DNS and Load Balancing](../../system-design/lessons/06-dns-load-balancing.md)
- [hard-parts/01 - Trade-offs and "No Best Practices"](../../hard-parts/lessons/01-tradeoffs-no-best-practices.md)
