# Oh My Learning - Cross-Domain Summary

A top-level view of every domain and subject, its coverage, and overall mastery.
Regenerated as lessons are added and after every discussion.

Every subject carries a **seniority baseline** (and every lesson a per-lesson band, from
`junior`/`mid`/`senior`/`staff`/`principal`) - see [SENIORITY.md](SENIORITY.md). The
baseline shown per subject below is the typical band; the per-lesson tags live in each
subject's table.

## Architecture

The domain covering how to design software systems - theory and applied practice.

### 1. DDIA - Designing Data-Intensive Applications

The theoretical foundation of the track.

- **Status:** 16/16 lessons authored (all `drafted`); not yet discussed, mastery pending.
- **Covers:** reliability, scalability and maintainability; data models and query languages; storage engines (OLTP/OLAP, column storage); encoding and schema evolution; replication; partitioning; transactions; distributed-systems failure modes; consistency and consensus; batch and stream processing.
- **Read:** [progress table](architecture/ddia/README.md) and [concept-by-concept recap](architecture/ddia/SUMMARY.md).

### 2. System Design - System Design Guide for Software Professionals

The applied layer of the track: takes DDIA theory and uses it to design real systems. Most lessons cross-link to the DDIA concept they build on.

- **Status:** 20/20 lessons authored (all `drafted`); not yet discussed, mastery pending.
- **Covers:** distributed-system attributes; CAP/PACELC and consensus; consistent hashing; DNS and load balancing; API gateways and proxies; databases, storage and sharding; distributed caching; pub/sub and queues; API design and communication; security and auth; rate limiting and resilience; observability; a repeatable design method; and case studies (URL shortener, news feed, real-time collaboration, video streaming, proximity service).
- **Read:** [progress table](architecture/system-design/README.md) and [concept-by-concept recap](architecture/system-design/SUMMARY.md).

### 3. The Hard Parts - Software Architecture: The Hard Parts

The trade-off layer of the track: how to pull a monolith apart and put it back together, reasoning about everything as explicit trade-offs. Cross-links to DDIA and System Design.

- **Status:** 17/17 lessons authored (all `drafted`); not yet discussed, mastery pending.
- **Covers:** trade-offs and "no best practices"; static and dynamic coupling and the architecture quantum; architectural modularity and decomposition; component-based decomposition patterns; service and data granularity; reuse patterns; data ownership; distributed transactions and eventual consistency; distributed data access; orchestration vs choreography; the eight transactional saga patterns; strict vs loose contracts; and analytical data (warehouse, lake, mesh).
- **Read:** [progress table](architecture/hard-parts/README.md) and [concept-by-concept recap](architecture/hard-parts/SUMMARY.md).

### 4. Fundamentals of Software Architecture

- **Status:** 22/22 lessons authored (all `drafted`); not yet discussed, mastery pending.
- **Covers:** architectural thinking and the architect role; architectural characteristics and how to discover, measure, and govern them; modularity, components, and architecture quanta; monolithic vs distributed topology and the fallacies of distributed computing; core architecture styles (layered, modular monolith, pipeline, microkernel, service-based, event-driven, space-based, SOA, microservices); choosing styles; ADRs; risk analysis; communication; leadership and career growth.
- **Read:** [progress table](architecture/fundamentals/README.md) and [concept-by-concept recap](architecture/fundamentals/SUMMARY.md).

### 5. Building Microservices

Service-decomposition practice: splitting a system into independently deployable services and keeping them shippable. Cross-links to DDIA and The Hard Parts.

- **Status:** 17/17 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** senior (mid->staff).
- **Covers:** what microservices are; modelling services and boundaries; splitting the monolith; communication styles (sync/async/event-driven); per-service data; distributed transactions and sagas; build/CI, deployment, testing, and consumer-driven contracts; observability; resilience; scaling; security; Conway's law and teams.
- **Read:** [progress table](architecture/building-microservices/README.md) and [concept-by-concept recap](architecture/building-microservices/SUMMARY.md).

### 6. Microservices Patterns

The microservices pattern catalog. Cross-links to DDIA and The Hard Parts.

- **Status:** 12/12 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** senior (mid->staff).
- **Covers:** the monolithic hell; decomposition strategies; IPC patterns; sagas; aggregates and domain events; event sourcing; CQRS; the API gateway; testing strategies; production-ready services; deployment patterns; refactoring a monolith.
- **Read:** [progress table](architecture/microservices-patterns/README.md) and [concept-by-concept recap](architecture/microservices-patterns/SUMMARY.md).

### 7. Designing Distributed Systems

Reusable container/orchestration patterns and batch-processing patterns. Cross-links to DDIA and System Design.

- **Status:** 12/12 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** mid-senior (mid->senior).
- **Covers:** containers as building blocks; sidecar, ambassador, adapter; replicated load-balanced and sharded services; scatter/gather; event-driven functions; leader election; work queues; event-driven and coordinated batch processing.
- **Read:** [progress table](architecture/designing-distributed-systems/README.md) and [concept-by-concept recap](architecture/designing-distributed-systems/SUMMARY.md).

### 8. Distributed Systems (principles)

The formal principles of distributed systems. Cross-links to DDIA and System Design.

- **Status:** 12/12 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** senior (mid->staff).
- **Covers:** goals and pitfalls; architectures and middleware; processes and threads; communication (RPC, messaging, multicast); naming; clocks and logical time; coordination; consistency and replication models; fault tolerance; consensus and agreement; distributed commit and recovery; security.
- **Read:** [progress table](architecture/distributed-systems/README.md) and [concept-by-concept recap](architecture/distributed-systems/SUMMARY.md).

### 9. Building Evolutionary Architectures

Guiding architectural change over time with fitness functions. Cross-links to Fundamentals and The Hard Parts.

- **Status:** 9/9 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** staff (senior->staff).
- **Covers:** what an evolutionary architecture is; fitness functions and their categories; incremental change; architectural coupling and quanta; evolutionary data; retrofitting evolvability; pitfalls and antipatterns; governance.
- **Read:** [progress table](architecture/evolutionary-architectures/README.md) and [concept-by-concept recap](architecture/evolutionary-architectures/SUMMARY.md).

### 10. System Design Interview

A repeatable interview framework plus worked end-to-end designs. Cross-links to System Design and DDIA.

- **Status:** 15/15 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** mid-senior (junior->senior).
- **Covers:** the interview framework; back-of-the-envelope estimation; scaling zero-to-millions; and case studies (rate limiter, consistent hashing, key-value store, unique ID generator, URL shortener, web crawler, notifications, news feed, chat, autocomplete, YouTube, Google Drive).
- **Read:** [progress table](architecture/system-design-interview/README.md) and [concept-by-concept recap](architecture/system-design-interview/SUMMARY.md).

## Software Engineering

The domain covering how to write maintainable, evolvable software - the craft and
discipline of code itself, as distinct from system-level design.

### 1. The Pragmatic Programmer

The pragmatic philosophy and everyday habits of effective developers.

- **Status:** 15/15 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** mid (junior->senior).
- **Covers:** the pragmatic philosophy and responsibility; software entropy; DRY; orthogonality; reversibility and tracer bullets; prototyping and estimating; plain text and the shell; debugging; design by contract; decoupling and the Law of Demeter; concurrency; transforming programming; pragmatic testing; requirements; pragmatic teams.
- **Read:** [progress table](software-engineering/pragmatic-programmer/README.md) and [concept-by-concept recap](software-engineering/pragmatic-programmer/SUMMARY.md).

### 2. Code Complete

Construction-level craftsmanship in the small.

- **Status:** 14/14 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** mid (junior->senior).
- **Covers:** construction metaphors; managing complexity; design in construction; working classes; high-quality routines; defensive programming; variables and data; naming; organizing code and conditionals; loops and control structures; taming complexity; collaborative construction; developer testing; refactoring and code tuning.
- **Read:** [progress table](software-engineering/code-complete/README.md) and [concept-by-concept recap](software-engineering/code-complete/SUMMARY.md).

### 3. Clean Architecture

SOLID, component principles, and the dependency rule. Cross-links to Fundamentals.

- **Status:** 13/13 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** senior (mid->senior).
- **Covers:** what architecture is for; the three paradigms; SOLID (SRP/OCP/LSP/ISP/DIP); component cohesion and coupling; business rules (entities/use cases); the dependency rule and layers; boundaries and the humble object; policy and level; details (DB/web); the main component; screaming architecture.
- **Read:** [progress table](software-engineering/clean-architecture/README.md) and [concept-by-concept recap](software-engineering/clean-architecture/SUMMARY.md).

### 4. Clean Code

Readable code in the small: naming, functions, comments, smells.

- **Status:** 12/12 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** junior-mid (junior->senior).
- **Covers:** what clean code is; meaningful names; functions; comments; formatting; objects vs data structures; error handling; boundaries; clean tests (F.I.R.S.T.); classes; systems; code smells and heuristics.
- **Read:** [progress table](software-engineering/clean-code/README.md) and [concept-by-concept recap](software-engineering/clean-code/SUMMARY.md).

### 5. Refactoring

Improving the design of existing code safely, driven by tests. Cross-links to Clean Code and Legacy Code.

- **Status:** 12/12 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** mid (junior->senior).
- **Covers:** what refactoring is; why and when; tests as the safety net; the code-smells catalog; composing methods; moving features; organizing data; simplifying conditionals; refactoring APIs; inheritance; big refactorings; refactoring, architecture, and YAGNI.
- **Read:** [progress table](software-engineering/refactoring/README.md) and [concept-by-concept recap](software-engineering/refactoring/SUMMARY.md).

### 6. A Philosophy of Software Design

Complexity as the enemy: deep modules and information hiding. A deliberate counterpoint to Clean Code on specifics.

- **Status:** 11/11 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** senior (mid->senior).
- **Covers:** complexity (symptoms and causes); strategic vs tactical programming; deep modules; information hiding; general-purpose modules; pulling complexity downward; layers and abstractions; defining errors out of existence; comments; naming and consistency; design tensions.
- **Read:** [progress table](software-engineering/philosophy-of-software-design/README.md) and [concept-by-concept recap](software-engineering/philosophy-of-software-design/SUMMARY.md).

### 7. Working Effectively with Legacy Code

Getting untested code under test: seams, dependency-breaking, characterization tests. Cross-links to Refactoring.

- **Status:** 12/12 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** senior (mid->senior).
- **Covers:** the change dilemma; seams and enabling points; characterization tests; sensing and separation; breaking dependencies; slow-to-change codebases; adding features to untested code; getting classes and methods into a test harness; finding where to change; the dependency-breaking techniques catalog; big tangled methods.
- **Read:** [progress table](software-engineering/legacy-code/README.md) and [concept-by-concept recap](software-engineering/legacy-code/SUMMARY.md).

### 8. Patterns of Enterprise Application Architecture

The enterprise pattern catalog: domain logic, O/R mapping, concurrency, sessions, distribution. Cross-links to DDIA and Design Patterns.

- **Status:** 14/14 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** senior (mid->senior).
- **Covers:** layering; domain-logic patterns (Transaction Script, Domain Model, Table Module, Service Layer); data-source gateways; Active Record; Data Mapper; Unit of Work; Identity Map and Lazy Load; O/R structural and metadata mapping; web presentation (MVC); concurrency and locking; session state; distribution (Remote Facade, DTO).
- **Read:** [progress table](software-engineering/enterprise-patterns/README.md) and [concept-by-concept recap](software-engineering/enterprise-patterns/SUMMARY.md).

### 9. Design Patterns (Gang of Four)

The classic 23 object-oriented patterns. Underpins the later pattern catalogs.

- **Status:** 11/11 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** mid (junior->senior).
- **Covers:** what patterns are and programming to an interface; composition over inheritance; creational (Factory Method, Abstract Factory, Builder, Prototype, Singleton); structural (Adapter, Bridge, Composite, Decorator, Facade, Proxy, Flyweight); behavioral (Strategy, Template Method, Observer, Command, State, Chain of Responsibility, Iterator, Mediator, Visitor, and the rest).
- **Read:** [progress table](software-engineering/design-patterns/README.md) and [concept-by-concept recap](software-engineering/design-patterns/SUMMARY.md).

## Domain Modeling

The domain covering how to model business complexity so software reflects real
organizational language and constraints - Domain-Driven Design, strategic and tactical.

### 1. Domain-Driven Design (Evans, the "blue book")

- **Status:** scaffolded - 16 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (mid->staff).
- **Covers:** ubiquitous language and model-driven design; entities, value objects, services; aggregates, repositories, factories; bounded contexts and context mapping; distillation of the core domain; strategic design and large-scale structure.
- **Read:** [progress table](domain-modeling/ddd-evans/README.md).

### 2. Implementing Domain-Driven Design (Vernon, the "red book")

- **Status:** scaffolded - 15 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (mid->staff).
- **Covers:** practical strategic design; aggregates and consistency boundaries in depth; domain events; integrating bounded contexts; application/architecture concerns for DDD execution.
- **Read:** [progress table](domain-modeling/implementing-ddd/README.md).

### 3. Learning Domain-Driven Design (Khononov)

- **Status:** scaffolded - 14 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (mid->staff).
- **Covers:** a modern, accessible route starting from strategic design (subdomains, bounded contexts) and connecting it to tactical implementation and evolving architectures.
- **Read:** [progress table](domain-modeling/learning-ddd/README.md).

### 4. Domain-Driven Design Distilled (Vernon)

- **Status:** scaffolded - 9 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** mid (junior->senior).
- **Covers:** a concise primer of core DDD ideas - bounded contexts, ubiquitous language, subdomains, aggregates, domain events - and adoption patterns.
- **Read:** [progress table](domain-modeling/ddd-distilled/README.md).

## Data Engineering & Databases

The domain covering how to choose, design, and understand storage systems. DDIA is the
theoretical foundation and lives under `architecture/` ([ddia](architecture/ddia/README.md)),
cross-referenced here rather than duplicated.

### 1. Database Internals (Petrov)

- **Status:** scaffolded - 16 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (mid->staff).
- **Covers:** storage-engine internals (B-Trees, LSM trees, logging, compaction) through the distributed layer - replication, partitioning, and consensus mechanics.
- **Read:** [progress table](data-engineering/database-internals/README.md).

### 2. SQL Performance Explained (Winand)

- **Status:** scaffolded - 10 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** mid (junior->senior).
- **Covers:** practical index and query-shape reasoning for predictable SQL performance - B-tree indexes, joins, ordering, clustering, and pagination.
- **Read:** [progress table](data-engineering/sql-performance-explained/README.md).

### 3. Seven Databases in Seven Weeks (Perkins, Redmond, Wilson)

- **Status:** scaffolded - 9 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** mid (junior->senior).
- **Covers:** a comparative tour of relational, document, wide-column, graph, and key-value systems, ending in workload-driven database selection.
- **Read:** [progress table](data-engineering/seven-databases/README.md).

## Computer Science Fundamentals

The domain covering the core CS layer: algorithm analysis, data structures, algorithm
design paradigms, and concurrency correctness.

### 1. Introduction to Algorithms (CLRS)

- **Status:** scaffolded - 20 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** mid (junior->senior).
- **Covers:** the comprehensive algorithms reference - analysis and asymptotics, sorting, fundamental data structures, trees and hashing, graph algorithms, dynamic programming, greedy algorithms, flow, and complexity.
- **Read:** [progress table](cs-fundamentals/clrs/README.md).

### 2. Algorithms (Sedgewick & Wayne)

- **Status:** scaffolded - 14 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** mid (junior->senior).
- **Covers:** a practical, implementation-focused treatment of core algorithms and data structures - sorting, searching, symbol tables, graphs, and strings.
- **Read:** [progress table](cs-fundamentals/algorithms-sedgewick/README.md).

### 3. Algorithm Design (Kleinberg & Tardos)

- **Status:** scaffolded - 12 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** mid-senior (mid->senior).
- **Covers:** design techniques and proof patterns - greedy, divide and conquer, dynamic programming, network flow, and NP-completeness.
- **Read:** [progress table](cs-fundamentals/algorithm-design/README.md).

### 4. Java Concurrency in Practice (Goetz et al.)

- **Status:** scaffolded - 15 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (mid->senior).
- **Covers:** the definitive JVM guide to thread safety - the memory model, building thread-safe classes, concurrent collections, synchronizers, thread pools, and liveness/performance.
- **Read:** [progress table](cs-fundamentals/java-concurrency/README.md).

### 5. The Art of Multiprocessor Programming (Herlihy & Shavit)

- **Status:** scaffolded - 13 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (mid->staff).
- **Covers:** the theory and practice of concurrent data structures - mutual exclusion, linearizability, locks, and lock-free/wait-free structures.
- **Read:** [progress table](cs-fundamentals/multiprocessor-programming/README.md).

## Software Quality

The domain covering testing and reliability - fast feedback loops that let you change
code with confidence through better test design and strategy.

### 1. Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce)

- **Status:** scaffolded - 12 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (mid->staff).
- **Covers:** outside-in TDD, the walking skeleton, mock objects, and designing a system through its tests.
- **Read:** [progress table](software-quality/goos/README.md).

### 2. Unit Testing: Principles, Practices, and Patterns (Khorikov)

- **Status:** scaffolded - 13 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (junior->staff).
- **Covers:** what makes a test valuable vs brittle, the four pillars, the London vs classical schools, test doubles, and integration-testing strategy.
- **Read:** [progress table](software-quality/unit-testing/README.md).

### 3. xUnit Test Patterns (Meszaros)

- **Status:** scaffolded - 12 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** mid (junior->senior).
- **Covers:** the canonical catalog of test smells, test patterns, and test-code refactorings for long-term maintainability.
- **Read:** [progress table](software-quality/xunit-test-patterns/README.md).

## DevOps, Cloud & Reliability

The domain covering how software is operated in production - delivery flow, fast
feedback, and reliability engineering as one operating model.

### 1. The Phoenix Project (Kim, Behr, Spafford)

- **Status:** scaffolded - 10 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** staff (senior->principal).
- **Covers:** a narrative introduction to the Three Ways, flow, work-in-progress limits, the Theory of Constraints applied to IT, and business-level transformation.
- **Read:** [progress table](devops-reliability/phoenix-project/README.md).

### 2. The DevOps Handbook (Kim, Humble, Debois, Willis)

- **Status:** scaffolded - 16 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (mid->staff).
- **Covers:** the practical implementation of the Three Ways - flow (CI/CD, deployment), feedback (telemetry, monitoring), and continual learning.
- **Read:** [progress table](devops-reliability/devops-handbook/README.md).

### 3. Site Reliability Engineering (Beyer, Jones, Petoff, Murphy)

- **Status:** scaffolded - 16 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** senior (mid->staff).
- **Covers:** SLIs/SLOs and error budgets, eliminating toil, on-call and incident management, release engineering, and running production systems reliably.
- **Read:** [progress table](devops-reliability/sre/README.md).

### 4. Seeking SRE (Blank-Edelman, ed.)

- **Status:** scaffolded - 12 concepts listed (all `drafted`), lesson bodies not yet authored; not yet discussed. **Seniority baseline:** staff (senior->principal).
- **Covers:** applying and evolving SRE across different organizations - culture, human factors, and long-term reliability strategy.
- **Read:** [progress table](devops-reliability/seeking-sre/README.md).

## Technical Leadership

The domain covering growth beyond coding - staff-plus IC leadership, engineering
management, evidence-based delivery, and the judgment/measurement skills behind
high-stakes decisions. This is the most senior-weighted domain in the library.

### 1. Staff Engineer (Larson)

- **Status:** 12/12 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** staff (senior->principal).
- **Covers:** what staff-plus roles are, the archetypes, earning the title, and operating with broad technical influence.
- **Read:** [progress table](technical-leadership/staff-engineer/README.md) - [subject summary](technical-leadership/staff-engineer/SUMMARY.md).

### 2. The Staff Engineer's Path (Reilly)

- **Status:** 14/14 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** staff (senior->principal).
- **Covers:** practical staff engineering through the three pillars - big-picture thinking, execution, and leveling up others.
- **Read:** [progress table](technical-leadership/staff-engineers-path/README.md) - [subject summary](technical-leadership/staff-engineers-path/SUMMARY.md).

### 3. An Elegant Puzzle (Larson)

- **Status:** 13/13 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** staff (senior->principal).
- **Covers:** engineering management as systems - org design, team sizing and topology, planning, systems thinking, and career ladders.
- **Read:** [progress table](technical-leadership/elegant-puzzle/README.md) - [subject summary](technical-leadership/elegant-puzzle/SUMMARY.md).

### 4. The Manager's Path (Fournier)

- **Status:** 13/13 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** staff (senior->principal).
- **Covers:** the management ladder from mentoring and tech lead through engineering manager, director, and up to CTO scope.
- **Read:** [progress table](technical-leadership/managers-path/README.md) - [subject summary](technical-leadership/managers-path/SUMMARY.md).

### 5. Accelerate (Forsgren, Humble, Kim)

- **Status:** 12/12 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** senior (senior->staff).
- **Covers:** the research behind the four key (DORA) delivery metrics, the capabilities that predict performance, and capability-based improvement.
- **Read:** [progress table](technical-leadership/accelerate/README.md) - [subject summary](technical-leadership/accelerate/SUMMARY.md).

### 6. Thinking, Fast and Slow (Kahneman)

- **Status:** 14/14 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** senior (mid->senior).
- **Covers:** System 1/System 2, the major cognitive biases and heuristics, and prospect theory - a decision-maker's toolkit for judgment under uncertainty.
- **Read:** [progress table](technical-leadership/thinking-fast-and-slow/README.md) - [subject summary](technical-leadership/thinking-fast-and-slow/SUMMARY.md).

### 7. How to Measure Anything (Hubbard)

- **Status:** 11/11 lessons authored (all `drafted`); not yet discussed, mastery pending. **Seniority baseline:** staff (senior->principal).
- **Covers:** applied measurement - calibrated estimation, reducing uncertainty, and the value of information for high-stakes decisions.
- **Read:** [progress table](technical-leadership/how-to-measure-anything/README.md) - [subject summary](technical-leadership/how-to-measure-anything/SUMMARY.md).

## Focus areas (aggregated weak spots)

None yet - discussions have not started. As discussions happen across subjects, the
open weak spots (especially concepts rated `shaky` or `not-yet`) will be collected
here so it is clear what to revisit.
