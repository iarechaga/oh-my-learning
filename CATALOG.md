# Full Lesson Catalog

Generated from lesson front matter by `scripts/generate_catalog.py` - do **not** hand-edit. Regenerate with `python3 scripts/generate_catalog.py` after adding, renumbering, or removing lessons, subjects, or domains, and commit the result in the same change. See [agent-docs/repository-model.md](agent-docs/repository-model.md).

**619 lessons across 9 domains, 46 subjects.** Every row links straight to the lesson; `status`/`mastery` are personal (per learner branch/fork), so this catalog only shows what exists, not who has studied it.

## Contents

- [Agentic Engineering](#agentic-engineering) - 1 subjects, 10 lessons
  - [Prompting & Context Engineering](#prompting-context-engineering) - 10 lessons
- [Architecture](#architecture) - 10 subjects, 152 lessons
  - [Building Microservices](#building-microservices) - 17 lessons
  - [Designing Data-Intensive Applications (DDIA)](#ddia) - 16 lessons
  - [Designing Distributed Systems](#designing-distributed-systems) - 12 lessons
  - [Distributed Systems (principles)](#distributed-systems) - 12 lessons
  - [Building Evolutionary Architectures](#evolutionary-architectures) - 9 lessons
  - [Fundamentals of Software Architecture](#fundamentals) - 22 lessons
  - [Software Architecture: The Hard Parts (trade-off analysis for distributed architectures)](#hard-parts) - 17 lessons
  - [Microservices Patterns](#microservices-patterns) - 12 lessons
  - [System Design (applying DDIA in practice)](#system-design) - 20 lessons
  - [System Design Interview](#system-design-interview) - 15 lessons
- [Computer Science Fundamentals](#cs-fundamentals) - 5 subjects, 74 lessons
  - [Algorithm Design (Kleinberg and Tardos)](#algorithm-design) - 12 lessons
  - [Algorithms (Sedgewick and Wayne)](#algorithms-sedgewick) - 14 lessons
  - [Introduction to Algorithms (CLRS)](#clrs) - 20 lessons
  - [Java Concurrency in Practice](#java-concurrency) - 15 lessons
  - [The Art of Multiprocessor Programming](#multiprocessor-programming) - 13 lessons
- [Data Engineering & Databases](#data-engineering) - 3 subjects, 35 lessons
  - [Database Internals: A Deep Dive into How Distributed Data Systems Work](#database-internals) - 16 lessons
  - [Seven Databases in Seven Weeks (2nd Edition)](#seven-databases) - 9 lessons
  - [SQL Performance Explained](#sql-performance-explained) - 10 lessons
- [DevOps, Cloud & Reliability](#devops-reliability) - 4 subjects, 54 lessons
  - [The DevOps Handbook](#devops-handbook) - 16 lessons
  - [The Phoenix Project: A Novel about IT, DevOps, and Helping Your Business Win](#phoenix-project) - 10 lessons
  - [Seeking SRE](#seeking-sre) - 12 lessons
  - [Site Reliability Engineering: How Google Runs Production Systems](#sre) - 16 lessons
- [Domain Modeling](#domain-modeling) - 4 subjects, 54 lessons
  - [Domain-Driven Design Distilled](#ddd-distilled) - 9 lessons
  - [Domain-Driven Design: Tackling Complexity in the Heart of Software](#ddd-evans) - 16 lessons
  - [Implementing Domain-Driven Design](#implementing-ddd) - 15 lessons
  - [Learning Domain-Driven Design](#learning-ddd) - 14 lessons
- [Software Engineering](#software-engineering) - 9 subjects, 114 lessons
  - [Clean Architecture](#clean-architecture) - 13 lessons
  - [Clean Code](#clean-code) - 12 lessons
  - [Code Complete](#code-complete) - 14 lessons
  - [Design Patterns](#design-patterns) - 11 lessons
  - [Patterns of Enterprise Application Architecture](#enterprise-patterns) - 14 lessons
  - [Working Effectively with Legacy Code](#legacy-code) - 12 lessons
  - [A Philosophy of Software Design](#philosophy-of-software-design) - 11 lessons
  - [The Pragmatic Programmer](#pragmatic-programmer) - 15 lessons
  - [Refactoring](#refactoring) - 12 lessons
- [Software Quality](#software-quality) - 3 subjects, 37 lessons
  - [Growing Object-Oriented Software, Guided by Tests](#goos) - 12 lessons
  - [Unit Testing: Principles, Practices, and Patterns](#unit-testing) - 13 lessons
  - [xUnit Test Patterns: Refactoring Test Code](#xunit-test-patterns) - 12 lessons
- [Technical Leadership](#technical-leadership) - 7 subjects, 89 lessons
  - [Accelerate: The Science of Lean Software and DevOps](#accelerate) - 12 lessons
  - [An Elegant Puzzle: Systems of Engineering Management](#elegant-puzzle) - 13 lessons
  - [How to Measure Anything: Finding the Value of Intangibles in Business](#how-to-measure-anything) - 11 lessons
  - [The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change](#managers-path) - 13 lessons
  - [Staff Engineer: Leadership Beyond the Management Track](#staff-engineer) - 12 lessons
  - [The Staff Engineer's Path](#staff-engineers-path) - 14 lessons
  - [Thinking, Fast and Slow](#thinking-fast-and-slow) - 14 lessons

---

<a id="agentic-engineering"></a>
## Agentic Engineering

<a id="prompting-context-engineering"></a>
### Prompting & Context Engineering

10 lessons - [subject index](agentic-engineering/prompting-context-engineering/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What LLMs Actually Do: Tokens, Context Windows, and Autoregression | junior | [lesson](agentic-engineering/prompting-context-engineering/lessons/01-what-llms-actually-do.md) |
| 02 | Prompt Anatomy: System, Developer, User, and Tool Turns | junior | [lesson](agentic-engineering/prompting-context-engineering/lessons/02-prompt-anatomy.md) |
| 03 | Core Prompting Techniques: Few-Shot, Role, and Output Formatting | mid | [lesson](agentic-engineering/prompting-context-engineering/lessons/03-core-prompting-techniques.md) |
| 04 | Chain-of-Thought and Reasoning Effort: What Actually Helps and What's Theater | mid | [lesson](agentic-engineering/prompting-context-engineering/lessons/04-chain-of-thought-and-reasoning-effort.md) |
| 05 | Structured Output: Constrained Decoding and Why It Beats Free-Form Parsing | mid | [lesson](agentic-engineering/prompting-context-engineering/lessons/05-structured-output.md) |
| 06 | The Limits of Prompting: Why Some Failures Aren't Prompt Problems | senior | [lesson](agentic-engineering/prompting-context-engineering/lessons/06-limits-of-prompting.md) |
| 07 | Context Engineering as a Discipline: The Context Window as a Budget | senior | [lesson](agentic-engineering/prompting-context-engineering/lessons/07-context-engineering-as-a-discipline.md) |
| 08 | Context Failure Modes: Poisoning, Distraction, and Confusion | senior | [lesson](agentic-engineering/prompting-context-engineering/lessons/08-context-failure-modes.md) |
| 09 | Retrieval and Memory: RAG, Long-Term Memory, and When to Use Which | senior | [lesson](agentic-engineering/prompting-context-engineering/lessons/09-retrieval-and-memory.md) |
| 10 | Context Compaction and Sub-Agent Handoff for Long-Horizon Tasks | staff | [lesson](agentic-engineering/prompting-context-engineering/lessons/10-context-compaction-and-handoff.md) |

---

<a id="architecture"></a>
## Architecture

<a id="building-microservices"></a>
### Building Microservices

17 lessons - [subject index](architecture/building-microservices/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What Microservices Are (and Are Not) | mid | [lesson](architecture/building-microservices/lessons/01-what-microservices-are.md) |
| 02 | Modelling Services Around Business Domains | senior | [lesson](architecture/building-microservices/lessons/02-modelling-services.md) |
| 03 | Defining Service Boundaries and Coupling/Cohesion | senior | [lesson](architecture/building-microservices/lessons/03-service-boundaries-coupling.md) |
| 04 | Splitting the Monolith (Migration Patterns) | senior | [lesson](architecture/building-microservices/lessons/04-splitting-the-monolith.md) |
| 05 | Inter-Service Communication Styles | mid | [lesson](architecture/building-microservices/lessons/05-communication-styles.md) |
| 06 | Synchronous vs Asynchronous and Event-Driven | senior | [lesson](architecture/building-microservices/lessons/06-sync-async-event-driven.md) |
| 07 | Managing Data: Per-Service Databases | senior | [lesson](architecture/building-microservices/lessons/07-per-service-data.md) |
| 08 | Distributed Transactions and Sagas | senior | [lesson](architecture/building-microservices/lessons/08-distributed-transactions-sagas.md) |
| 09 | Build, CI, and Artifact Management | mid | [lesson](architecture/building-microservices/lessons/09-build-ci-artifacts.md) |
| 10 | Deployment: Containers, Orchestration, and Patterns | senior | [lesson](architecture/building-microservices/lessons/10-deployment-patterns.md) |
| 11 | Testing Microservices (Unit to Contract to E2E) | mid | [lesson](architecture/building-microservices/lessons/11-testing-microservices.md) |
| 12 | Consumer-Driven Contracts | senior | [lesson](architecture/building-microservices/lessons/12-consumer-driven-contracts.md) |
| 13 | Observability: Logs, Metrics, Tracing, Correlation IDs | mid | [lesson](architecture/building-microservices/lessons/13-observability.md) |
| 14 | Resilience: Timeouts, Retries, Bulkheads, Circuit Breakers | senior | [lesson](architecture/building-microservices/lessons/14-resilience.md) |
| 15 | Scaling Microservices | senior | [lesson](architecture/building-microservices/lessons/15-scaling.md) |
| 16 | Security in a Microservice System | senior | [lesson](architecture/building-microservices/lessons/16-security.md) |
| 17 | Conway's Law and Team Organization | staff | [lesson](architecture/building-microservices/lessons/17-conways-law-teams.md) |

<a id="ddia"></a>
### Designing Data-Intensive Applications (DDIA)

16 lessons - [subject index](architecture/ddia/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Reliability, Scalability, and Maintainability | mid | [lesson](architecture/ddia/lessons/01-reliability-scalability-maintainability.md) |
| 02 | Data Models: Relational, Document, and Graph | junior | [lesson](architecture/ddia/lessons/02-data-models.md) |
| 03 | Query Languages for Data | junior | [lesson](architecture/ddia/lessons/03-query-languages.md) |
| 04 | Storage Engines: LSM-Trees and B-Trees | senior | [lesson](architecture/ddia/lessons/04-storage-engines.md) |
| 05 | OLTP vs OLAP and Column-Oriented Storage | mid | [lesson](architecture/ddia/lessons/05-oltp-olap-column-storage.md) |
| 06 | Encoding and Schema Evolution | mid | [lesson](architecture/ddia/lessons/06-encoding-and-schema-evolution.md) |
| 07 | Replication: Single-Leader | mid | [lesson](architecture/ddia/lessons/07-replication-single-leader.md) |
| 08 | Replication: Multi-Leader and Leaderless | senior | [lesson](architecture/ddia/lessons/08-replication-multi-leader-leaderless.md) |
| 09 | Replication Lag and Consistency Guarantees | senior | [lesson](architecture/ddia/lessons/09-replication-lag-and-consistency.md) |
| 10 | Partitioning (Sharding) | senior | [lesson](architecture/ddia/lessons/10-partitioning.md) |
| 11 | Transactions: ACID, Isolation, and Serializability | senior | [lesson](architecture/ddia/lessons/11-transactions.md) |
| 12 | The Trouble with Distributed Systems | senior | [lesson](architecture/ddia/lessons/12-distributed-systems-trouble.md) |
| 13 | Consistency and Consensus | staff | [lesson](architecture/ddia/lessons/13-consistency-and-consensus.md) |
| 14 | Batch Processing | senior | [lesson](architecture/ddia/lessons/14-batch-processing.md) |
| 15 | Stream Processing | senior | [lesson](architecture/ddia/lessons/15-stream-processing.md) |
| 16 | The Future of Data Systems | staff | [lesson](architecture/ddia/lessons/16-future-of-data-systems.md) |

<a id="designing-distributed-systems"></a>
### Designing Distributed Systems

12 lessons - [subject index](architecture/designing-distributed-systems/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Why Distributed Patterns (Containers as Building Blocks) | mid | [lesson](architecture/designing-distributed-systems/lessons/01-why-distributed-patterns.md) |
| 02 | The Sidecar Pattern | mid | [lesson](architecture/designing-distributed-systems/lessons/02-sidecar.md) |
| 03 | The Ambassador Pattern | mid | [lesson](architecture/designing-distributed-systems/lessons/03-ambassador.md) |
| 04 | The Adapter Pattern | mid | [lesson](architecture/designing-distributed-systems/lessons/04-adapter.md) |
| 05 | Replicated Load-Balanced Services | mid | [lesson](architecture/designing-distributed-systems/lessons/05-replicated-load-balanced.md) |
| 06 | Sharded Services | senior | [lesson](architecture/designing-distributed-systems/lessons/06-sharded-services.md) |
| 07 | Scatter/Gather | senior | [lesson](architecture/designing-distributed-systems/lessons/07-scatter-gather.md) |
| 08 | Functions and Event-Driven Processing | mid | [lesson](architecture/designing-distributed-systems/lessons/08-functions-event-driven.md) |
| 09 | Ownership Election (Leader Election) | senior | [lesson](architecture/designing-distributed-systems/lessons/09-ownership-election.md) |
| 10 | Work Queue Systems | mid | [lesson](architecture/designing-distributed-systems/lessons/10-work-queues.md) |
| 11 | Event-Driven Batch Processing | senior | [lesson](architecture/designing-distributed-systems/lessons/11-event-driven-batch.md) |
| 12 | Coordinated Batch Processing | senior | [lesson](architecture/designing-distributed-systems/lessons/12-coordinated-batch.md) |

<a id="distributed-systems"></a>
### Distributed Systems (principles)

12 lessons - [subject index](architecture/distributed-systems/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What a Distributed System Is: Goals and Pitfalls | mid | [lesson](architecture/distributed-systems/lessons/01-goals-and-pitfalls.md) |
| 02 | Architectures and Middleware | senior | [lesson](architecture/distributed-systems/lessons/02-architectures-middleware.md) |
| 03 | Processes, Threads, and Virtualization | mid | [lesson](architecture/distributed-systems/lessons/03-processes-threads.md) |
| 04 | Communication: RPC, Messaging, Multicast | mid | [lesson](architecture/distributed-systems/lessons/04-communication.md) |
| 05 | Naming (Flat, Structured, Attribute-Based) | senior | [lesson](architecture/distributed-systems/lessons/05-naming.md) |
| 06 | Clocks, Logical Time, and Mutual Exclusion | senior | [lesson](architecture/distributed-systems/lessons/06-clocks-logical-time.md) |
| 07 | Coordination: Election, Gossip, Distributed Events | senior | [lesson](architecture/distributed-systems/lessons/07-coordination.md) |
| 08 | Consistency and Replication Models | senior | [lesson](architecture/distributed-systems/lessons/08-consistency-replication.md) |
| 09 | Fault Tolerance and Reliable Group Communication | senior | [lesson](architecture/distributed-systems/lessons/09-fault-tolerance.md) |
| 10 | Consensus and Agreement (Paxos/Raft Foundations) | staff | [lesson](architecture/distributed-systems/lessons/10-consensus-agreement.md) |
| 11 | Distributed Commit and Recovery | senior | [lesson](architecture/distributed-systems/lessons/11-commit-recovery.md) |
| 12 | Security in Distributed Systems | senior | [lesson](architecture/distributed-systems/lessons/12-security.md) |

<a id="evolutionary-architectures"></a>
### Building Evolutionary Architectures

9 lessons - [subject index](architecture/evolutionary-architectures/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What an Evolutionary Architecture Is | senior | [lesson](architecture/evolutionary-architectures/lessons/01-what-evolutionary-architecture-is.md) |
| 02 | Fitness Functions | senior | [lesson](architecture/evolutionary-architectures/lessons/02-fitness-functions.md) |
| 03 | Categories of Fitness Functions | senior | [lesson](architecture/evolutionary-architectures/lessons/03-fitness-function-categories.md) |
| 04 | Incremental Change (Deployment Pipelines) | senior | [lesson](architecture/evolutionary-architectures/lessons/04-incremental-change.md) |
| 05 | Architectural Coupling and Quanta | senior | [lesson](architecture/evolutionary-architectures/lessons/05-coupling-and-quanta.md) |
| 06 | Evolutionary Data | senior | [lesson](architecture/evolutionary-architectures/lessons/06-evolutionary-data.md) |
| 07 | Building Evolvable Architectures (Retrofitting) | staff | [lesson](architecture/evolutionary-architectures/lessons/07-building-evolvable-architectures.md) |
| 08 | Evolutionary Architecture Pitfalls and Antipatterns | staff | [lesson](architecture/evolutionary-architectures/lessons/08-pitfalls-antipatterns.md) |
| 09 | Governing and Building an Evolutionary Practice | staff | [lesson](architecture/evolutionary-architectures/lessons/09-governance-practice.md) |

<a id="fundamentals"></a>
### Fundamentals of Software Architecture

22 lessons - [subject index](architecture/fundamentals/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Architectural Thinking | senior | [lesson](architecture/fundamentals/lessons/01-architectural-thinking.md) |
| 02 | Role of the Software Architect | senior | [lesson](architecture/fundamentals/lessons/02-role-of-the-software-architect.md) |
| 03 | Architectural Characteristics | senior | [lesson](architecture/fundamentals/lessons/03-architectural-characteristics.md) |
| 04 | Discovering Architectural Characteristics | senior | [lesson](architecture/fundamentals/lessons/04-discovering-architectural-characteristics.md) |
| 05 | Measuring and Governing Characteristics | senior | [lesson](architecture/fundamentals/lessons/05-measuring-governing-characteristics.md) |
| 06 | Modularity Fundamentals | mid | [lesson](architecture/fundamentals/lessons/06-modularity-fundamentals.md) |
| 07 | Component-Based Thinking | mid | [lesson](architecture/fundamentals/lessons/07-component-based-thinking.md) |
| 08 | Architecture Quanta | senior | [lesson](architecture/fundamentals/lessons/08-architecture-quanta.md) |
| 09 | Monolithic vs Distributed Architecture | mid | [lesson](architecture/fundamentals/lessons/09-monolithic-vs-distributed-architecture.md) |
| 10 | Fallacies of Distributed Computing | mid | [lesson](architecture/fundamentals/lessons/10-fallacies-of-distributed-computing.md) |
| 11 | Layered Architecture | mid | [lesson](architecture/fundamentals/lessons/11-layered-architecture.md) |
| 12 | Modular Monolith | mid | [lesson](architecture/fundamentals/lessons/12-modular-monolith.md) |
| 13 | Pipeline Architecture | mid | [lesson](architecture/fundamentals/lessons/13-pipeline-architecture.md) |
| 14 | Microkernel Architecture | mid | [lesson](architecture/fundamentals/lessons/14-microkernel-architecture.md) |
| 15 | Service-Based Architecture | senior | [lesson](architecture/fundamentals/lessons/15-service-based-architecture.md) |
| 16 | Event-Driven Architecture | senior | [lesson](architecture/fundamentals/lessons/16-event-driven-architecture.md) |
| 17 | Space-Based Architecture | senior | [lesson](architecture/fundamentals/lessons/17-space-based-architecture.md) |
| 18 | SOA and Microservices | senior | [lesson](architecture/fundamentals/lessons/18-soa-and-microservices.md) |
| 19 | Choosing an Architecture Style | senior | [lesson](architecture/fundamentals/lessons/19-choosing-an-architecture-style.md) |
| 20 | Architecture Decisions and ADRs | senior | [lesson](architecture/fundamentals/lessons/20-architecture-decisions-and-adrs.md) |
| 21 | Architecture Risk and Communication | staff | [lesson](architecture/fundamentals/lessons/21-architecture-risk-and-communication.md) |
| 22 | Architect Leadership and Career | staff | [lesson](architecture/fundamentals/lessons/22-architect-leadership-and-career.md) |

<a id="hard-parts"></a>
### Software Architecture: The Hard Parts (trade-off analysis for distributed architectures)

17 lessons - [subject index](architecture/hard-parts/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Trade-offs and "No Best Practices" | senior | [lesson](architecture/hard-parts/lessons/01-tradeoffs-no-best-practices.md) |
| 02 | The Architecture Quantum and Static Coupling | senior | [lesson](architecture/hard-parts/lessons/02-architecture-quantum-static-coupling.md) |
| 03 | Dynamic Coupling | senior | [lesson](architecture/hard-parts/lessons/03-dynamic-coupling.md) |
| 04 | Architectural Modularity | senior | [lesson](architecture/hard-parts/lessons/04-architectural-modularity.md) |
| 05 | Architectural Decomposition | senior | [lesson](architecture/hard-parts/lessons/05-architectural-decomposition.md) |
| 06 | Component-Based Decomposition Patterns | senior | [lesson](architecture/hard-parts/lessons/06-component-based-decomposition-patterns.md) |
| 07 | Service Granularity | senior | [lesson](architecture/hard-parts/lessons/07-service-granularity.md) |
| 08 | Decomposing Operational Data | senior | [lesson](architecture/hard-parts/lessons/08-decomposing-operational-data.md) |
| 09 | Reuse Patterns | mid | [lesson](architecture/hard-parts/lessons/09-reuse-patterns.md) |
| 10 | Data Ownership | senior | [lesson](architecture/hard-parts/lessons/10-data-ownership.md) |
| 11 | Distributed Transactions and Eventual Consistency | senior | [lesson](architecture/hard-parts/lessons/11-distributed-transactions-eventual-consistency.md) |
| 12 | Distributed Data Access | senior | [lesson](architecture/hard-parts/lessons/12-distributed-data-access.md) |
| 13 | Distributed Workflows: Orchestration vs Choreography | senior | [lesson](architecture/hard-parts/lessons/13-distributed-workflows-orchestration-choreography.md) |
| 14 | Transactional Sagas | staff | [lesson](architecture/hard-parts/lessons/14-transactional-sagas.md) |
| 15 | Contracts: Strict vs Loose | senior | [lesson](architecture/hard-parts/lessons/15-contracts.md) |
| 16 | Managing Analytical Data | staff | [lesson](architecture/hard-parts/lessons/16-managing-analytical-data.md) |
| 17 | Build Your Own Trade-Off Analysis | staff | [lesson](architecture/hard-parts/lessons/17-build-your-own-trade-off-analysis.md) |

<a id="microservices-patterns"></a>
### Microservices Patterns

12 lessons - [subject index](architecture/microservices-patterns/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | The Monolithic Hell and the Microservice Architecture | mid | [lesson](architecture/microservices-patterns/lessons/01-monolithic-hell.md) |
| 02 | Decomposition Strategies (by Capability and Subdomain) | senior | [lesson](architecture/microservices-patterns/lessons/02-decomposition-strategies.md) |
| 03 | Inter-Process Communication Patterns | senior | [lesson](architecture/microservices-patterns/lessons/03-ipc-patterns.md) |
| 04 | Managing Transactions with Sagas | senior | [lesson](architecture/microservices-patterns/lessons/04-sagas.md) |
| 05 | Designing Business Logic: Aggregates and Domain Events | senior | [lesson](architecture/microservices-patterns/lessons/05-business-logic-aggregates.md) |
| 06 | Event Sourcing | senior | [lesson](architecture/microservices-patterns/lessons/06-event-sourcing.md) |
| 07 | Implementing Queries with CQRS | senior | [lesson](architecture/microservices-patterns/lessons/07-cqrs.md) |
| 08 | External API Patterns and the API Gateway | senior | [lesson](architecture/microservices-patterns/lessons/08-external-api-gateway.md) |
| 09 | Testing Strategies for Microservices | senior | [lesson](architecture/microservices-patterns/lessons/09-testing-strategies.md) |
| 10 | Production-Ready Services | senior | [lesson](architecture/microservices-patterns/lessons/10-production-ready-services.md) |
| 11 | Deployment Patterns | mid | [lesson](architecture/microservices-patterns/lessons/11-deployment-patterns.md) |
| 12 | Refactoring to Microservices | staff | [lesson](architecture/microservices-patterns/lessons/12-refactoring-to-microservices.md) |

<a id="system-design"></a>
### System Design (applying DDIA in practice)

20 lessons - [subject index](architecture/system-design/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | System Design Fundamentals | junior | [lesson](architecture/system-design/lessons/01-fundamentals.md) |
| 02 | Distributed-System Attributes and Scaling | mid | [lesson](architecture/system-design/lessons/02-distributed-system-attributes.md) |
| 03 | CAP, PACELC, and Consensus in Practice | senior | [lesson](architecture/system-design/lessons/03-cap-pacelc-consensus.md) |
| 04 | Consistent Hashing | mid | [lesson](architecture/system-design/lessons/04-consistent-hashing.md) |
| 05 | Probabilistic Data Structures for Scale | mid | [lesson](architecture/system-design/lessons/05-probabilistic-data-structures.md) |
| 06 | DNS and Load Balancing | mid | [lesson](architecture/system-design/lessons/06-dns-load-balancing.md) |
| 07 | API Gateways and Reverse Proxies | mid | [lesson](architecture/system-design/lessons/07-api-gateways-proxies.md) |
| 08 | Choosing Databases and Storage | mid | [lesson](architecture/system-design/lessons/08-choosing-databases-storage.md) |
| 09 | Replication and Sharding in Practice | senior | [lesson](architecture/system-design/lessons/09-replication-sharding-in-practice.md) |
| 10 | Distributed Caching | mid | [lesson](architecture/system-design/lessons/10-distributed-caching.md) |
| 11 | Pub/Sub and Distributed Queues | mid | [lesson](architecture/system-design/lessons/11-pubsub-distributed-queues.md) |
| 12 | API Design and Communication | mid | [lesson](architecture/system-design/lessons/12-api-design-communication.md) |
| 13 | Security: Authentication and Authorization | mid | [lesson](architecture/system-design/lessons/13-security-auth.md) |
| 14 | Rate Limiting and Resilience | senior | [lesson](architecture/system-design/lessons/14-rate-limiting-resilience.md) |
| 15 | Observability: Logging, Metrics, and Tracing | mid | [lesson](architecture/system-design/lessons/15-observability.md) |
| 16 | A System-Design Method (URL Shortener) | mid | [lesson](architecture/system-design/lessons/16-design-method-url-shortener.md) |
| 17 | Case Study: News Feed and Timelines | senior | [lesson](architecture/system-design/lessons/17-case-study-news-feed.md) |
| 18 | Case Study: Real-Time Collaboration (Google Docs) | senior | [lesson](architecture/system-design/lessons/18-case-study-realtime-collaboration.md) |
| 19 | Case Study: Video Streaming (Netflix) | senior | [lesson](architecture/system-design/lessons/19-case-study-video-streaming.md) |
| 20 | Case Study: Proximity / Geo Service | senior | [lesson](architecture/system-design/lessons/20-case-study-proximity-service.md) |

<a id="system-design-interview"></a>
### System Design Interview

15 lessons - [subject index](architecture/system-design-interview/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | A Framework for System Design Interviews | mid | [lesson](architecture/system-design-interview/lessons/01-interview-framework.md) |
| 02 | Back-of-the-Envelope Estimation | junior | [lesson](architecture/system-design-interview/lessons/02-back-of-the-envelope.md) |
| 03 | Scaling from Zero to Millions of Users | mid | [lesson](architecture/system-design-interview/lessons/03-scaling-zero-to-millions.md) |
| 04 | Design a Rate Limiter | mid | [lesson](architecture/system-design-interview/lessons/04-rate-limiter.md) |
| 05 | Design Consistent Hashing | mid | [lesson](architecture/system-design-interview/lessons/05-consistent-hashing.md) |
| 06 | Design a Key-Value Store | senior | [lesson](architecture/system-design-interview/lessons/06-key-value-store.md) |
| 07 | Design a Unique ID Generator | mid | [lesson](architecture/system-design-interview/lessons/07-unique-id-generator.md) |
| 08 | Design a URL Shortener | junior | [lesson](architecture/system-design-interview/lessons/08-url-shortener.md) |
| 09 | Design a Web Crawler | mid | [lesson](architecture/system-design-interview/lessons/09-web-crawler.md) |
| 10 | Design a Notification System | mid | [lesson](architecture/system-design-interview/lessons/10-notification-system.md) |
| 11 | Design a News Feed System | senior | [lesson](architecture/system-design-interview/lessons/11-news-feed.md) |
| 12 | Design a Chat System | senior | [lesson](architecture/system-design-interview/lessons/12-chat-system.md) |
| 13 | Design a Search Autocomplete System | senior | [lesson](architecture/system-design-interview/lessons/13-search-autocomplete.md) |
| 14 | Design YouTube (Video Platform) | senior | [lesson](architecture/system-design-interview/lessons/14-youtube.md) |
| 15 | Design Google Drive | senior | [lesson](architecture/system-design-interview/lessons/15-google-drive.md) |

---

<a id="cs-fundamentals"></a>
## Computer Science Fundamentals

<a id="algorithm-design"></a>
### Algorithm Design (Kleinberg and Tardos)

12 lessons - [subject index](cs-fundamentals/algorithm-design/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Stable matching and algorithmic reasoning | mid | [lesson](cs-fundamentals/algorithm-design/lessons/01-stable-matching-reasoning.md) |
| 02 | Asymptotic analysis and recurrence solving | mid | [lesson](cs-fundamentals/algorithm-design/lessons/02-asymptotic-analysis-recurrences.md) |
| 03 | Divide and conquer with proof of correctness | mid | [lesson](cs-fundamentals/algorithm-design/lessons/03-divide-and-conquer-correctness.md) |
| 04 | Greedy algorithms and exchange arguments | mid | [lesson](cs-fundamentals/algorithm-design/lessons/04-greedy-exchange-arguments.md) |
| 05 | Dynamic programming: optimal substructure and state design | mid | [lesson](cs-fundamentals/algorithm-design/lessons/05-dynamic-programming-state-design.md) |
| 06 | Shortest paths and negative cycles | mid | [lesson](cs-fundamentals/algorithm-design/lessons/06-shortest-paths-negative-cycles.md) |
| 07 | Graph traversal, connectivity, and strongly connected components | mid | [lesson](cs-fundamentals/algorithm-design/lessons/07-graph-traversal-connectivity-scc.md) |
| 08 | Maximum flow and minimum cut | senior | [lesson](cs-fundamentals/algorithm-design/lessons/08-maximum-flow-minimum-cut.md) |
| 09 | Reductions and NP-completeness proofs | senior | [lesson](cs-fundamentals/algorithm-design/lessons/09-reductions-np-completeness.md) |
| 10 | Coping with NP-hardness: approximation algorithms | senior | [lesson](cs-fundamentals/algorithm-design/lessons/10-approximation-algorithms.md) |
| 11 | Coping with NP-hardness: local search and heuristic design | senior | [lesson](cs-fundamentals/algorithm-design/lessons/11-local-search-heuristics.md) |
| 12 | Intractability in practice: modeling choices and tractable relaxations | senior | [lesson](cs-fundamentals/algorithm-design/lessons/12-intractability-modeling-relaxations.md) |

<a id="algorithms-sedgewick"></a>
### Algorithms (Sedgewick and Wayne)

14 lessons - [subject index](cs-fundamentals/algorithms-sedgewick/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Union-find and connectivity modeling | junior | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/01-union-find-connectivity.md) |
| 02 | Algorithm analysis and cost models | junior | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/02-algorithm-analysis-cost-models.md) |
| 03 | Stacks, queues, and linked-list implementations | junior | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/03-stacks-queues-linked-lists.md) |
| 04 | Elementary sorting (selection, insertion, shellsort) | junior | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/04-elementary-sorting.md) |
| 05 | Mergesort and quicksort in practice | mid | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/05-mergesort-quicksort.md) |
| 06 | Priority queues and heapsort | mid | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/06-priority-queues-heapsort.md) |
| 07 | Symbol tables with binary search trees | mid | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/07-symbol-tables-bst.md) |
| 08 | Balanced search trees (red-black BSTs) | mid | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/08-balanced-search-trees.md) |
| 09 | Hash tables (separate chaining and linear probing) | junior | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/09-hash-tables.md) |
| 10 | Undirected and directed graph fundamentals | mid | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/10-graph-fundamentals.md) |
| 11 | Minimum spanning trees and shortest paths | mid | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/11-mst-shortest-paths.md) |
| 12 | Directed acyclic graphs and topological order | mid | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/12-dag-topological-order.md) |
| 13 | Tries and substring search algorithms | mid | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/13-tries-substring-search.md) |
| 14 | Data compression (Huffman and LZW) | senior | [lesson](cs-fundamentals/algorithms-sedgewick/lessons/14-data-compression-huffman-lzw.md) |

<a id="clrs"></a>
### Introduction to Algorithms (CLRS)

20 lessons - [subject index](cs-fundamentals/clrs/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Asymptotic growth and Big-O/Theta/Omega | junior | [lesson](cs-fundamentals/clrs/lessons/01-asymptotic-growth.md) |
| 02 | Recurrences and the Master method | mid | [lesson](cs-fundamentals/clrs/lessons/02-recurrences-master-method.md) |
| 03 | Divide and conquer as a design paradigm | mid | [lesson](cs-fundamentals/clrs/lessons/03-divide-and-conquer.md) |
| 04 | Probabilistic analysis and randomized algorithms | senior | [lesson](cs-fundamentals/clrs/lessons/04-probabilistic-analysis-randomization.md) |
| 05 | Elementary data structures (stacks, queues, linked lists) | junior | [lesson](cs-fundamentals/clrs/lessons/05-elementary-data-structures.md) |
| 06 | Hash tables and expected-time lookup | junior | [lesson](cs-fundamentals/clrs/lessons/06-hash-tables.md) |
| 07 | Heaps and priority queues | mid | [lesson](cs-fundamentals/clrs/lessons/07-heaps-priority-queues.md) |
| 08 | Quicksort and randomized partitioning | mid | [lesson](cs-fundamentals/clrs/lessons/08-quicksort-randomized.md) |
| 09 | Balanced search trees (red-black trees) | mid | [lesson](cs-fundamentals/clrs/lessons/09-balanced-search-trees.md) |
| 10 | Order statistics and selection in linear time | senior | [lesson](cs-fundamentals/clrs/lessons/10-order-statistics-selection.md) |
| 11 | Dynamic programming fundamentals | mid | [lesson](cs-fundamentals/clrs/lessons/11-dynamic-programming-fundamentals.md) |
| 12 | Greedy algorithms and exchange arguments | mid | [lesson](cs-fundamentals/clrs/lessons/12-greedy-algorithms.md) |
| 13 | Graph representations, BFS, and DFS | mid | [lesson](cs-fundamentals/clrs/lessons/13-graph-representations-bfs-dfs.md) |
| 14 | Shortest-path algorithms | mid | [lesson](cs-fundamentals/clrs/lessons/14-shortest-path-algorithms.md) |
| 15 | Minimum spanning trees | mid | [lesson](cs-fundamentals/clrs/lessons/15-minimum-spanning-trees.md) |
| 16 | Maximum flow and the max-flow min-cut theorem | senior | [lesson](cs-fundamentals/clrs/lessons/16-maximum-flow-min-cut.md) |
| 17 | Amortized analysis techniques | senior | [lesson](cs-fundamentals/clrs/lessons/17-amortized-analysis.md) |
| 18 | Disjoint sets and union-find analysis | mid | [lesson](cs-fundamentals/clrs/lessons/18-disjoint-sets-union-find.md) |
| 19 | NP-completeness and polynomial-time reductions | senior | [lesson](cs-fundamentals/clrs/lessons/19-np-completeness-reductions.md) |
| 20 | Approximation algorithms for NP-hard problems | senior | [lesson](cs-fundamentals/clrs/lessons/20-approximation-algorithms.md) |

<a id="java-concurrency"></a>
### Java Concurrency in Practice

15 lessons - [subject index](cs-fundamentals/java-concurrency/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Threads, shared state, and race conditions | mid | [lesson](cs-fundamentals/java-concurrency/lessons/01-threads-shared-state-races.md) |
| 02 | Immutability, confinement, and thread safety basics | mid | [lesson](cs-fundamentals/java-concurrency/lessons/02-immutability-confinement-thread-safety.md) |
| 03 | Java Memory Model and happens-before | senior | [lesson](cs-fundamentals/java-concurrency/lessons/03-java-memory-model-happens-before.md) |
| 04 | Synchronization with intrinsic locks | mid | [lesson](cs-fundamentals/java-concurrency/lessons/04-synchronization-intrinsic-locks.md) |
| 05 | Building and composing thread-safe classes | senior | [lesson](cs-fundamentals/java-concurrency/lessons/05-composing-thread-safe-classes.md) |
| 06 | Liveness hazards: deadlock, starvation, livelock | senior | [lesson](cs-fundamentals/java-concurrency/lessons/06-liveness-hazards.md) |
| 07 | Concurrent collections and blocking queues | mid | [lesson](cs-fundamentals/java-concurrency/lessons/07-concurrent-collections-blocking-queues.md) |
| 08 | Task execution with Executor framework | mid | [lesson](cs-fundamentals/java-concurrency/lessons/08-executor-framework.md) |
| 09 | Callable, Future, and asynchronous result handling | mid | [lesson](cs-fundamentals/java-concurrency/lessons/09-callable-future-async-results.md) |
| 10 | Cancellation, interruption, and shutdown policies | senior | [lesson](cs-fundamentals/java-concurrency/lessons/10-cancellation-interruption-shutdown.md) |
| 11 | Explicit locks, conditions, and advanced synchronizers | senior | [lesson](cs-fundamentals/java-concurrency/lessons/11-explicit-locks-conditions-synchronizers.md) |
| 12 | Atomic variables and nonblocking techniques | senior | [lesson](cs-fundamentals/java-concurrency/lessons/12-atomic-variables-nonblocking.md) |
| 13 | Performance and scalability under contention | senior | [lesson](cs-fundamentals/java-concurrency/lessons/13-performance-scalability-contention.md) |
| 14 | Testing and debugging concurrent Java programs | senior | [lesson](cs-fundamentals/java-concurrency/lessons/14-testing-debugging-concurrency.md) |
| 15 | Designing cancellation-safe and resilient services | senior | [lesson](cs-fundamentals/java-concurrency/lessons/15-cancellation-safe-resilient-services.md) |

<a id="multiprocessor-programming"></a>
### The Art of Multiprocessor Programming

13 lessons - [subject index](cs-fundamentals/multiprocessor-programming/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Concurrency model and shared-memory assumptions | mid | [lesson](cs-fundamentals/multiprocessor-programming/lessons/01-concurrency-model-shared-memory.md) |
| 02 | Mutual exclusion and lock correctness criteria | mid | [lesson](cs-fundamentals/multiprocessor-programming/lessons/02-mutual-exclusion-lock-correctness.md) |
| 03 | Classic lock algorithms (Peterson, bakery, tournament) | senior | [lesson](cs-fundamentals/multiprocessor-programming/lessons/03-classic-lock-algorithms.md) |
| 04 | Scalable locks (TAS, TTAS, CLH, MCS, backoff) | senior | [lesson](cs-fundamentals/multiprocessor-programming/lessons/04-scalable-locks.md) |
| 05 | Linearizability and correctness of concurrent objects | senior | [lesson](cs-fundamentals/multiprocessor-programming/lessons/05-linearizability-correctness.md) |
| 06 | Concurrent linked lists and skip lists | senior | [lesson](cs-fundamentals/multiprocessor-programming/lessons/06-concurrent-lists-skip-lists.md) |
| 07 | Progress guarantees: obstruction-free, lock-free, wait-free | senior | [lesson](cs-fundamentals/multiprocessor-programming/lessons/07-progress-guarantees.md) |
| 08 | Universal constructions with consensus primitives | staff | [lesson](cs-fundamentals/multiprocessor-programming/lessons/08-universal-constructions-consensus.md) |
| 09 | Consensus hierarchy and synchronization power | staff | [lesson](cs-fundamentals/multiprocessor-programming/lessons/09-consensus-hierarchy.md) |
| 10 | Atomic primitives (CAS, FAA) and ABA hazards | senior | [lesson](cs-fundamentals/multiprocessor-programming/lessons/10-atomic-primitives-aba.md) |
| 11 | Lock-free stacks and queues | senior | [lesson](cs-fundamentals/multiprocessor-programming/lessons/11-lock-free-stacks-queues.md) |
| 12 | Memory reclamation (hazard pointers, epochs) | staff | [lesson](cs-fundamentals/multiprocessor-programming/lessons/12-memory-reclamation.md) |
| 13 | Software transactional memory and composable synchronization | senior | [lesson](cs-fundamentals/multiprocessor-programming/lessons/13-software-transactional-memory.md) |

---

<a id="data-engineering"></a>
## Data Engineering & Databases

<a id="database-internals"></a>
### Database Internals: A Deep Dive into How Distributed Data Systems Work

16 lessons - [subject index](data-engineering/database-internals/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Hardware and IO Foundations for Storage Engines | mid | [lesson](data-engineering/database-internals/lessons/01-hardware-and-io-foundations.md) |
| 02 | Data Layout and File Organization on Disk | senior | [lesson](data-engineering/database-internals/lessons/02-data-layout-and-file-organization.md) |
| 03 | B-Tree Fundamentals and Page-Oriented Indexing | senior | [lesson](data-engineering/database-internals/lessons/03-b-tree-fundamentals.md) |
| 04 | Write-Ahead Logging and Crash Recovery Basics | senior | [lesson](data-engineering/database-internals/lessons/04-write-ahead-logging-and-recovery.md) |
| 05 | Buffer Management, Caching, and Compaction Pressure | senior | [lesson](data-engineering/database-internals/lessons/05-buffer-management-and-caching.md) |
| 06 | LSM-Tree Design and the Read-Write Amplification Trade-off | senior | [lesson](data-engineering/database-internals/lessons/06-lsm-tree-design.md) |
| 07 | SSTables, Compaction Strategies, and Tombstones | senior | [lesson](data-engineering/database-internals/lessons/07-sstables-compaction-and-tombstones.md) |
| 08 | B-Tree vs LSM-Tree: Workload-Driven Engine Selection | senior | [lesson](data-engineering/database-internals/lessons/08-b-tree-vs-lsm-selection.md) |
| 09 | In-Memory Structures and Lock-Free Indexing Patterns | senior | [lesson](data-engineering/database-internals/lessons/09-in-memory-structures-and-lock-free-indexing.md) |
| 10 | Transaction Internals: MVCC, Snapshots, and Isolation Mechanics | senior | [lesson](data-engineering/database-internals/lessons/10-transaction-internals-mvcc-and-isolation.md) |
| 11 | Engine Architecture: Separating Storage, Execution, and Control Planes | staff | [lesson](data-engineering/database-internals/lessons/11-engine-architecture-planes.md) |
| 12 | Replication Logs, Shipping Models, and Durability Semantics | senior | [lesson](data-engineering/database-internals/lessons/12-replication-logs-and-durability.md) |
| 13 | Quorums, Anti-Entropy, and Conflict Resolution in Replicated Stores | staff | [lesson](data-engineering/database-internals/lessons/13-quorums-anti-entropy-and-conflict-resolution.md) |
| 14 | Partitioning Internals and Rebalancing Algorithms | staff | [lesson](data-engineering/database-internals/lessons/14-partitioning-internals-and-rebalancing.md) |
| 15 | Consensus Internals with Raft and Log Agreement Mechanics | staff | [lesson](data-engineering/database-internals/lessons/15-consensus-internals-with-raft.md) |
| 16 | Building and Evolving a Distributed Storage Engine in Production | staff | [lesson](data-engineering/database-internals/lessons/16-evolving-a-distributed-storage-engine.md) |

<a id="seven-databases"></a>
### Seven Databases in Seven Weeks (2nd Edition)

9 lessons - [subject index](data-engineering/seven-databases/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Relational vs NoSQL Framing and CAP-Era Trade-offs | mid | [lesson](data-engineering/seven-databases/lessons/01-relational-vs-nosql-framing.md) |
| 02 | PostgreSQL: Relational Modeling, Constraints, and Transactional Strength | junior | [lesson](data-engineering/seven-databases/lessons/02-postgresql-relational-modeling.md) |
| 03 | HBase: Wide-Column Modeling and Access-Pattern-First Design | mid | [lesson](data-engineering/seven-databases/lessons/03-hbase-wide-column-modeling.md) |
| 04 | MongoDB: Document Modeling, Indexing, and Schema Flexibility Limits | mid | [lesson](data-engineering/seven-databases/lessons/04-mongodb-document-modeling.md) |
| 05 | CouchDB: Replication-First Documents and Conflict-Oriented Workflows | mid | [lesson](data-engineering/seven-databases/lessons/05-couchdb-replication-first-documents.md) |
| 06 | Neo4j: Graph Modeling and Traversal-Centric Query Design | mid | [lesson](data-engineering/seven-databases/lessons/06-neo4j-graph-modeling.md) |
| 07 | DynamoDB: Partition-Key Design, Throughput Units, and Access Constraints | senior | [lesson](data-engineering/seven-databases/lessons/07-dynamodb-partition-key-design.md) |
| 08 | Redis: In-Memory Data Structures, Caching Roles, and Persistence Modes | mid | [lesson](data-engineering/seven-databases/lessons/08-redis-data-structures-and-persistence.md) |
| 09 | Cross-Database Comparison and Workload-Driven Store Selection | senior | [lesson](data-engineering/seven-databases/lessons/09-cross-database-selection.md) |

<a id="sql-performance-explained"></a>
### SQL Performance Explained

10 lessons - [subject index](data-engineering/sql-performance-explained/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | How the Optimizer Chooses Access Paths | junior | [lesson](data-engineering/sql-performance-explained/lessons/01-optimizer-access-paths.md) |
| 02 | B-Tree Index Structure and Lookup Mechanics | junior | [lesson](data-engineering/sql-performance-explained/lessons/02-b-tree-index-structure.md) |
| 03 | Selectivity, Cardinality Estimates, and Predicate Shape | mid | [lesson](data-engineering/sql-performance-explained/lessons/03-selectivity-cardinality-and-predicates.md) |
| 04 | Multi-Column Indexes and Left-Prefix Behavior | mid | [lesson](data-engineering/sql-performance-explained/lessons/04-multi-column-indexes-and-left-prefix.md) |
| 05 | Covering Indexes and Index-Only Retrieval | mid | [lesson](data-engineering/sql-performance-explained/lessons/05-covering-indexes-and-index-only-retrieval.md) |
| 06 | Join Execution and Indexing Foreign-Key Relationships | mid | [lesson](data-engineering/sql-performance-explained/lessons/06-join-execution-and-fk-indexing.md) |
| 07 | ORDER BY, GROUP BY, and Avoiding Expensive Sorts | mid | [lesson](data-engineering/sql-performance-explained/lessons/07-order-by-group-by-and-sorts.md) |
| 08 | Pagination Patterns: OFFSET Pitfalls and Keyset Pagination | mid | [lesson](data-engineering/sql-performance-explained/lessons/08-pagination-offset-vs-keyset.md) |
| 09 | Clustering Effects and Physical Row Ordering Trade-offs | senior | [lesson](data-engineering/sql-performance-explained/lessons/09-clustering-and-row-ordering-trade-offs.md) |
| 10 | Reading Execution Plans and Validating Performance Hypotheses | mid | [lesson](data-engineering/sql-performance-explained/lessons/10-reading-execution-plans.md) |

---

<a id="devops-reliability"></a>
## DevOps, Cloud & Reliability

<a id="devops-handbook"></a>
### The DevOps Handbook

16 lessons - [subject index](devops-reliability/devops-handbook/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Applying the Three Ways as an Implementation Model | senior | [lesson](devops-reliability/devops-handbook/lessons/01-three-ways-implementation-model.md) |
| 02 | Value Stream Mapping for Software Delivery | senior | [lesson](devops-reliability/devops-handbook/lessons/02-value-stream-mapping.md) |
| 03 | Small Batch Sizes and Limiting Work in Process | mid | [lesson](devops-reliability/devops-handbook/lessons/03-small-batches-wip-limits.md) |
| 04 | Version Control for Code, Infrastructure, and Config | mid | [lesson](devops-reliability/devops-handbook/lessons/04-version-control-everything.md) |
| 05 | Continuous Integration as a Quality Gate | mid | [lesson](devops-reliability/devops-handbook/lessons/05-continuous-integration.md) |
| 06 | Continuous Delivery and Deployment Pipeline Design | senior | [lesson](devops-reliability/devops-handbook/lessons/06-continuous-delivery-pipelines.md) |
| 07 | Trunk-Based Development and Release Cadence | senior | [lesson](devops-reliability/devops-handbook/lessons/07-trunk-based-release-cadence.md) |
| 08 | Shift-Left Security and Compliance in Delivery Flow | senior | [lesson](devops-reliability/devops-handbook/lessons/08-shift-left-security-compliance.md) |
| 09 | Infrastructure as Code and Immutable Infrastructure | senior | [lesson](devops-reliability/devops-handbook/lessons/09-infrastructure-as-code-immutable.md) |
| 10 | Telemetry Foundations: Logs, Metrics, Traces, and Events | mid | [lesson](devops-reliability/devops-handbook/lessons/10-telemetry-foundations.md) |
| 11 | Production Monitoring and Actionable Alerting | senior | [lesson](devops-reliability/devops-handbook/lessons/11-monitoring-actionable-alerting.md) |
| 12 | Fast Incident Feedback into Engineering Work | senior | [lesson](devops-reliability/devops-handbook/lessons/12-incident-feedback-loops.md) |
| 13 | Blameless Postmortems and Systemic Root Cause Analysis | senior | [lesson](devops-reliability/devops-handbook/lessons/13-blameless-postmortems.md) |
| 14 | Enabling Team Topologies and Platform Capabilities | staff | [lesson](devops-reliability/devops-handbook/lessons/14-enabling-teams-platform.md) |
| 15 | Governance Through Standards and Self-Service Controls | staff | [lesson](devops-reliability/devops-handbook/lessons/15-governance-self-service-controls.md) |
| 16 | Measuring Outcomes: Delivery Performance and Reliability Metrics | staff | [lesson](devops-reliability/devops-handbook/lessons/16-delivery-reliability-metrics.md) |

<a id="phoenix-project"></a>
### The Phoenix Project: A Novel about IT, DevOps, and Helping Your Business Win

10 lessons - [subject index](devops-reliability/phoenix-project/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | The Parts Unlimited Crisis as a Systems Problem | senior | [lesson](devops-reliability/phoenix-project/lessons/01-parts-unlimited-systems-problem.md) |
| 02 | Work as Flow: From Projects to Value Streams | senior | [lesson](devops-reliability/phoenix-project/lessons/02-work-as-flow-value-streams.md) |
| 03 | Theory of Constraints for IT Operations | senior | [lesson](devops-reliability/phoenix-project/lessons/03-theory-of-constraints-it.md) |
| 04 | WIP Limits and Reducing Multitasking Damage | senior | [lesson](devops-reliability/phoenix-project/lessons/04-wip-limits-multitasking.md) |
| 05 | The First Way: Fast Left-to-Right Flow | staff | [lesson](devops-reliability/phoenix-project/lessons/05-first-way-flow.md) |
| 06 | The Second Way: Amplifying Feedback Loops | staff | [lesson](devops-reliability/phoenix-project/lessons/06-second-way-feedback.md) |
| 07 | The Third Way: Continual Learning and Experimentation | staff | [lesson](devops-reliability/phoenix-project/lessons/07-third-way-learning.md) |
| 08 | Managing Technical Debt as Operational Risk | senior | [lesson](devops-reliability/phoenix-project/lessons/08-technical-debt-operational-risk.md) |
| 09 | Changing Relationships Between Development, Ops, and Business | staff | [lesson](devops-reliability/phoenix-project/lessons/09-dev-ops-business-relationships.md) |
| 10 | Turning IT Into a Competitive Advantage Capability | principal | [lesson](devops-reliability/phoenix-project/lessons/10-it-competitive-advantage.md) |

<a id="seeking-sre"></a>
### Seeking SRE

12 lessons - [subject index](devops-reliability/seeking-sre/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Choosing an SRE Adoption Model for Your Organization | staff | [lesson](devops-reliability/seeking-sre/lessons/01-sre-adoption-models.md) |
| 02 | Defining Reliability Ownership Between Product and Platform Teams | staff | [lesson](devops-reliability/seeking-sre/lessons/02-reliability-ownership-models.md) |
| 03 | Evolving Incident Response Maturity Over Time | senior | [lesson](devops-reliability/seeking-sre/lessons/03-incident-response-maturity.md) |
| 04 | Building Sustainable On-Call Culture and Boundaries | senior | [lesson](devops-reliability/seeking-sre/lessons/04-on-call-culture-boundaries.md) |
| 05 | Psychological Safety and Blameless Reliability Culture | staff | [lesson](devops-reliability/seeking-sre/lessons/05-psychological-safety-blamelessness.md) |
| 06 | Reliability Communication with Executives and Stakeholders | staff | [lesson](devops-reliability/seeking-sre/lessons/06-reliability-stakeholder-communication.md) |
| 07 | Hiring and Developing SRE Capabilities | staff | [lesson](devops-reliability/seeking-sre/lessons/07-hiring-developing-sre.md) |
| 08 | Managing Toil at Organizational Scale | staff | [lesson](devops-reliability/seeking-sre/lessons/08-org-scale-toil-management.md) |
| 09 | Embedding Reliability in Product Planning and Prioritization | staff | [lesson](devops-reliability/seeking-sre/lessons/09-reliability-in-product-planning.md) |
| 10 | Reliability in Regulated and High-Risk Environments | staff | [lesson](devops-reliability/seeking-sre/lessons/10-reliability-regulated-environments.md) |
| 11 | Measuring SRE Program Impact and Organizational Health | principal | [lesson](devops-reliability/seeking-sre/lessons/11-sre-program-impact.md) |
| 12 | The Future of SRE as a Socio-Technical Discipline | principal | [lesson](devops-reliability/seeking-sre/lessons/12-future-of-sre.md) |

<a id="sre"></a>
### Site Reliability Engineering: How Google Runs Production Systems

16 lessons - [subject index](devops-reliability/sre/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What SRE Is and How It Differs from Traditional Operations | mid | [lesson](devops-reliability/sre/lessons/01-what-sre-is.md) |
| 02 | Service Level Indicators (SLIs): Measuring User-Visible Behavior | mid | [lesson](devops-reliability/sre/lessons/02-service-level-indicators.md) |
| 03 | Service Level Objectives (SLOs): Target-Setting for Reliability | senior | [lesson](devops-reliability/sre/lessons/03-service-level-objectives.md) |
| 04 | Error Budgets as a Release-Governance Mechanism | senior | [lesson](devops-reliability/sre/lessons/04-error-budgets.md) |
| 05 | Toil: Identifying, Quantifying, and Prioritizing Elimination | senior | [lesson](devops-reliability/sre/lessons/05-toil-elimination.md) |
| 06 | Automation Strategy for Repetitive Operational Work | senior | [lesson](devops-reliability/sre/lessons/06-automation-strategy.md) |
| 07 | Monitoring and Alerting Design for Actionable Signals | senior | [lesson](devops-reliability/sre/lessons/07-monitoring-alerting.md) |
| 08 | On-Call Engineering: Rotations, Load, and Sustainability | senior | [lesson](devops-reliability/sre/lessons/08-on-call-engineering.md) |
| 09 | Incident Command and Coordinated Response | senior | [lesson](devops-reliability/sre/lessons/09-incident-command.md) |
| 10 | Postmortems and Organizational Learning from Failure | senior | [lesson](devops-reliability/sre/lessons/10-postmortems-learning.md) |
| 11 | Capacity Planning and Demand Forecasting | senior | [lesson](devops-reliability/sre/lessons/11-capacity-planning.md) |
| 12 | Release Engineering and Progressive Delivery Safety | senior | [lesson](devops-reliability/sre/lessons/12-release-engineering.md) |
| 13 | Data Processing Reliability and Pipeline Operations | senior | [lesson](devops-reliability/sre/lessons/13-data-processing-reliability.md) |
| 14 | Handling Overload and Cascading Failure | senior | [lesson](devops-reliability/sre/lessons/14-overload-cascading-failure.md) |
| 15 | Multi-Team Reliability Interfaces and Support Boundaries | staff | [lesson](devops-reliability/sre/lessons/15-multi-team-reliability-interfaces.md) |
| 16 | Evolving SRE Practices with Service Maturity | staff | [lesson](devops-reliability/sre/lessons/16-sre-practice-maturity.md) |

---

<a id="domain-modeling"></a>
## Domain Modeling

<a id="ddd-distilled"></a>
### Domain-Driven Design Distilled

9 lessons - [subject index](domain-modeling/ddd-distilled/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What DDD is and when to use it | junior | [lesson](domain-modeling/ddd-distilled/lessons/01-what-ddd-is-and-when-to-use-it.md) |
| 02 | Ubiquitous language and collaborative modeling | mid | [lesson](domain-modeling/ddd-distilled/lessons/02-ubiquitous-language-and-collaborative-modeling.md) |
| 03 | Bounded contexts and context maps | mid | [lesson](domain-modeling/ddd-distilled/lessons/03-bounded-contexts-and-context-maps.md) |
| 04 | Distilling the core domain | senior | [lesson](domain-modeling/ddd-distilled/lessons/04-distilling-the-core-domain.md) |
| 05 | Entities and value objects | mid | [lesson](domain-modeling/ddd-distilled/lessons/05-entities-and-value-objects.md) |
| 06 | Aggregates and consistency boundaries | senior | [lesson](domain-modeling/ddd-distilled/lessons/06-aggregates-and-consistency-boundaries.md) |
| 07 | Repositories and domain services | mid | [lesson](domain-modeling/ddd-distilled/lessons/07-repositories-and-domain-services.md) |
| 08 | Domain events and eventual consistency | senior | [lesson](domain-modeling/ddd-distilled/lessons/08-domain-events-and-eventual-consistency.md) |
| 09 | Strategic redesign and incremental adoption | senior | [lesson](domain-modeling/ddd-distilled/lessons/09-strategic-redesign-and-incremental-adoption.md) |

<a id="ddd-evans"></a>
### Domain-Driven Design: Tackling Complexity in the Heart of Software

16 lessons - [subject index](domain-modeling/ddd-evans/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Knowledge crunching and ubiquitous language | mid | [lesson](domain-modeling/ddd-evans/lessons/01-knowledge-crunching-and-ubiquitous-language.md) |
| 02 | Model-driven design and the domain layer | mid | [lesson](domain-modeling/ddd-evans/lessons/02-model-driven-design-and-domain-layer.md) |
| 03 | Layered architecture for model integrity | mid | [lesson](domain-modeling/ddd-evans/lessons/03-layered-architecture-for-model-integrity.md) |
| 04 | Entities and continuity of identity | mid | [lesson](domain-modeling/ddd-evans/lessons/04-entities-and-continuity-of-identity.md) |
| 05 | Value objects and side-effect-free modeling | mid | [lesson](domain-modeling/ddd-evans/lessons/05-value-objects-and-side-effect-free-modeling.md) |
| 06 | Services when behavior does not fit an object | senior | [lesson](domain-modeling/ddd-evans/lessons/06-services-when-behavior-does-not-fit-an-object.md) |
| 07 | Modules as conceptual boundaries | mid | [lesson](domain-modeling/ddd-evans/lessons/07-modules-as-conceptual-boundaries.md) |
| 08 | Aggregates and transactional consistency boundaries | senior | [lesson](domain-modeling/ddd-evans/lessons/08-aggregates-and-transactional-consistency-boundaries.md) |
| 09 | Factories for complex creation and invariant safety | senior | [lesson](domain-modeling/ddd-evans/lessons/09-factories-for-complex-creation-and-invariant-safety.md) |
| 10 | Repositories for persistence ignorance | senior | [lesson](domain-modeling/ddd-evans/lessons/10-repositories-for-persistence-ignorance.md) |
| 11 | Associations and model navigation trade-offs | senior | [lesson](domain-modeling/ddd-evans/lessons/11-associations-and-model-navigation-trade-offs.md) |
| 12 | Supple design for expressive and malleable models | senior | [lesson](domain-modeling/ddd-evans/lessons/12-supple-design-for-expressive-and-malleable-models.md) |
| 13 | Distillation: core domain and generic subdomains | staff | [lesson](domain-modeling/ddd-evans/lessons/13-distillation-core-domain-and-generic-subdomains.md) |
| 14 | Bounded contexts and explicit model boundaries | senior | [lesson](domain-modeling/ddd-evans/lessons/14-bounded-contexts-and-explicit-model-boundaries.md) |
| 15 | Context mapping and anti-corruption boundaries | staff | [lesson](domain-modeling/ddd-evans/lessons/15-context-mapping-and-anti-corruption-boundaries.md) |
| 16 | Large-scale structure and continuous model refactoring | staff | [lesson](domain-modeling/ddd-evans/lessons/16-large-scale-structure-and-continuous-model-refactoring.md) |

<a id="implementing-ddd"></a>
### Implementing Domain-Driven Design

15 lessons - [subject index](domain-modeling/implementing-ddd/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Distilling strategic design into implementation decisions | senior | [lesson](domain-modeling/implementing-ddd/lessons/01-distilling-strategic-design-into-implementation-decisions.md) |
| 02 | Domain model building blocks in code | mid | [lesson](domain-modeling/implementing-ddd/lessons/02-domain-model-building-blocks-in-code.md) |
| 03 | Bounded contexts as autonomous service boundaries | senior | [lesson](domain-modeling/implementing-ddd/lessons/03-bounded-contexts-as-autonomous-service-boundaries.md) |
| 04 | Effective aggregate design and true invariants | senior | [lesson](domain-modeling/implementing-ddd/lessons/04-effective-aggregate-design-and-true-invariants.md) |
| 05 | Aggregate references by identity | senior | [lesson](domain-modeling/implementing-ddd/lessons/05-aggregate-references-by-identity.md) |
| 06 | Eventual consistency around aggregate boundaries | senior | [lesson](domain-modeling/implementing-ddd/lessons/06-eventual-consistency-around-aggregate-boundaries.md) |
| 07 | Domain events and immutable business facts | senior | [lesson](domain-modeling/implementing-ddd/lessons/07-domain-events-and-immutable-business-facts.md) |
| 08 | Repositories and persistence-mapping strategies | senior | [lesson](domain-modeling/implementing-ddd/lessons/08-repositories-and-persistence-mapping-strategies.md) |
| 09 | Application services and command orchestration | mid | [lesson](domain-modeling/implementing-ddd/lessons/09-application-services-and-command-orchestration.md) |
| 10 | Published language and context-map contracts | staff | [lesson](domain-modeling/implementing-ddd/lessons/10-published-language-and-context-map-contracts.md) |
| 11 | Anti-corruption layers and translation boundaries | staff | [lesson](domain-modeling/implementing-ddd/lessons/11-anti-corruption-layers-and-translation-boundaries.md) |
| 12 | Integrating bounded contexts with messaging | senior | [lesson](domain-modeling/implementing-ddd/lessons/12-integrating-bounded-contexts-with-messaging.md) |
| 13 | Event sourcing and stream-based aggregates | staff | [lesson](domain-modeling/implementing-ddd/lessons/13-event-sourcing-and-stream-based-aggregates.md) |
| 14 | CQRS and read-model segregation | senior | [lesson](domain-modeling/implementing-ddd/lessons/14-cqrs-and-read-model-segregation.md) |
| 15 | Sagas and process managers for long-running consistency | staff | [lesson](domain-modeling/implementing-ddd/lessons/15-sagas-and-process-managers-for-long-running-consistency.md) |

<a id="learning-ddd"></a>
### Learning Domain-Driven Design

14 lessons - [subject index](domain-modeling/learning-ddd/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Why domain complexity drives design choices | mid | [lesson](domain-modeling/learning-ddd/lessons/01-why-domain-complexity-drives-design-choices.md) |
| 02 | Subdomains: core, supporting, and generic | senior | [lesson](domain-modeling/learning-ddd/lessons/02-subdomains-core-supporting-and-generic.md) |
| 03 | Bounded contexts and autonomy boundaries | senior | [lesson](domain-modeling/learning-ddd/lessons/03-bounded-contexts-and-autonomy-boundaries.md) |
| 04 | Context maps and relationship patterns | senior | [lesson](domain-modeling/learning-ddd/lessons/04-context-maps-and-relationship-patterns.md) |
| 05 | Ubiquitous language in collaborative discovery | mid | [lesson](domain-modeling/learning-ddd/lessons/05-ubiquitous-language-in-collaborative-discovery.md) |
| 06 | Event storming to discover process and hotspots | mid | [lesson](domain-modeling/learning-ddd/lessons/06-event-storming-to-discover-process-and-hotspots.md) |
| 07 | Business logic patterns: transaction script, active record, domain model | mid | [lesson](domain-modeling/learning-ddd/lessons/07-business-logic-patterns-transaction-script-active-record-domain-model.md) |
| 08 | Aggregates and invariants in tactical design | senior | [lesson](domain-modeling/learning-ddd/lessons/08-aggregates-and-invariants-in-tactical-design.md) |
| 09 | Domain events and temporal modeling | senior | [lesson](domain-modeling/learning-ddd/lessons/09-domain-events-and-temporal-modeling.md) |
| 10 | Data ownership and consistency boundaries | senior | [lesson](domain-modeling/learning-ddd/lessons/10-data-ownership-and-consistency-boundaries.md) |
| 11 | Integration patterns between bounded contexts | senior | [lesson](domain-modeling/learning-ddd/lessons/11-integration-patterns-between-bounded-contexts.md) |
| 12 | Domain model to service architecture alignment | staff | [lesson](domain-modeling/learning-ddd/lessons/12-domain-model-to-service-architecture-alignment.md) |
| 13 | Evolutionary design and refactoring of contexts | staff | [lesson](domain-modeling/learning-ddd/lessons/13-evolutionary-design-and-refactoring-of-contexts.md) |
| 14 | Socio-technical alignment and team topologies for DDD | staff | [lesson](domain-modeling/learning-ddd/lessons/14-socio-technical-alignment-and-team-topologies-for-ddd.md) |

---

<a id="software-engineering"></a>
## Software Engineering

<a id="clean-architecture"></a>
### Clean Architecture

13 lessons - [subject index](software-engineering/clean-architecture/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What "Good Architecture" Is For | mid | [lesson](software-engineering/clean-architecture/lessons/01-what-architecture-is-for.md) |
| 02 | The Three Paradigms (Structured, OO, Functional) | senior | [lesson](software-engineering/clean-architecture/lessons/02-programming-paradigms.md) |
| 03 | SRP and OCP | mid | [lesson](software-engineering/clean-architecture/lessons/03-srp-ocp.md) |
| 04 | LSP, ISP, and DIP | senior | [lesson](software-engineering/clean-architecture/lessons/04-lsp-isp-dip.md) |
| 05 | Component Cohesion (REP, CCP, CRP) | senior | [lesson](software-engineering/clean-architecture/lessons/05-component-cohesion.md) |
| 06 | Component Coupling (ADP, SDP, SAP) | senior | [lesson](software-engineering/clean-architecture/lessons/06-component-coupling.md) |
| 07 | Business Rules: Entities and Use Cases | senior | [lesson](software-engineering/clean-architecture/lessons/07-business-rules.md) |
| 08 | The Dependency Rule and Clean-Architecture Layers | senior | [lesson](software-engineering/clean-architecture/lessons/08-dependency-rule.md) |
| 09 | Boundaries and the Humble Object Pattern | senior | [lesson](software-engineering/clean-architecture/lessons/09-boundaries-humble-object.md) |
| 10 | Policy, Level, and the Direction of Dependencies | senior | [lesson](software-engineering/clean-architecture/lessons/10-policy-and-level.md) |
| 11 | The Database and the Web Are Details | senior | [lesson](software-engineering/clean-architecture/lessons/11-details-database-web.md) |
| 12 | The Main Component and Partial Boundaries | senior | [lesson](software-engineering/clean-architecture/lessons/12-main-component-partial-boundaries.md) |
| 13 | Screaming Architecture and Test Boundaries | mid | [lesson](software-engineering/clean-architecture/lessons/13-screaming-architecture.md) |

<a id="clean-code"></a>
### Clean Code

12 lessons - [subject index](software-engineering/clean-code/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What Clean Code Is and Why It Matters | junior | [lesson](software-engineering/clean-code/lessons/01-what-clean-code-is.md) |
| 02 | Meaningful Names | junior | [lesson](software-engineering/clean-code/lessons/02-meaningful-names.md) |
| 03 | Functions: Small, One Thing, One Level | junior | [lesson](software-engineering/clean-code/lessons/03-functions.md) |
| 04 | Comments: Good, Bad, and Unnecessary | junior | [lesson](software-engineering/clean-code/lessons/04-comments.md) |
| 05 | Formatting and Vertical/Horizontal Ordering | junior | [lesson](software-engineering/clean-code/lessons/05-formatting.md) |
| 06 | Objects and Data Structures | mid | [lesson](software-engineering/clean-code/lessons/06-objects-and-data-structures.md) |
| 07 | Error Handling Without Clutter | mid | [lesson](software-engineering/clean-code/lessons/07-error-handling.md) |
| 08 | Boundaries and Third-Party Code | mid | [lesson](software-engineering/clean-code/lessons/08-boundaries.md) |
| 09 | Clean Tests and the F.I.R.S.T. Rules | mid | [lesson](software-engineering/clean-code/lessons/09-clean-tests.md) |
| 10 | Classes: Cohesion and SRP in the Small | mid | [lesson](software-engineering/clean-code/lessons/10-classes.md) |
| 11 | Systems and Separating Construction from Use | senior | [lesson](software-engineering/clean-code/lessons/11-systems.md) |
| 12 | Code Smells and Heuristics | senior | [lesson](software-engineering/clean-code/lessons/12-code-smells-heuristics.md) |

<a id="code-complete"></a>
### Code Complete

14 lessons - [subject index](software-engineering/code-complete/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Software Construction and Metaphors | junior | [lesson](software-engineering/code-complete/lessons/01-construction-metaphors.md) |
| 02 | Managing Complexity as the Core Problem | senior | [lesson](software-engineering/code-complete/lessons/02-managing-complexity.md) |
| 03 | Design in Construction (Heuristics) | mid | [lesson](software-engineering/code-complete/lessons/03-design-in-construction.md) |
| 04 | Working Classes: Cohesion and Abstraction | mid | [lesson](software-engineering/code-complete/lessons/04-working-classes.md) |
| 05 | High-Quality Routines | junior | [lesson](software-engineering/code-complete/lessons/05-high-quality-routines.md) |
| 06 | Defensive Programming | mid | [lesson](software-engineering/code-complete/lessons/06-defensive-programming.md) |
| 07 | Using Variables and Data Effectively | junior | [lesson](software-engineering/code-complete/lessons/07-variables-and-data.md) |
| 08 | Naming Variables Well | junior | [lesson](software-engineering/code-complete/lessons/08-naming-variables.md) |
| 09 | Organizing Straight-Line Code and Conditionals | junior | [lesson](software-engineering/code-complete/lessons/09-organizing-code-conditionals.md) |
| 10 | Controlling Loops and Unusual Control Structures | mid | [lesson](software-engineering/code-complete/lessons/10-loops-control-structures.md) |
| 11 | Taming Deep Nesting and Complexity Metrics | mid | [lesson](software-engineering/code-complete/lessons/11-taming-complexity.md) |
| 12 | Collaborative Construction and Code Reviews | mid | [lesson](software-engineering/code-complete/lessons/12-collaborative-construction.md) |
| 13 | Developer Testing | mid | [lesson](software-engineering/code-complete/lessons/13-developer-testing.md) |
| 14 | Refactoring and Code-Tuning Strategies | senior | [lesson](software-engineering/code-complete/lessons/14-refactoring-code-tuning.md) |

<a id="design-patterns"></a>
### Design Patterns

11 lessons - [subject index](software-engineering/design-patterns/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What Patterns Are; Program to an Interface | mid | [lesson](software-engineering/design-patterns/lessons/01-what-patterns-are.md) |
| 02 | Composition Over Inheritance | mid | [lesson](software-engineering/design-patterns/lessons/02-composition-over-inheritance.md) |
| 03 | Creational: Factory Method and Abstract Factory | mid | [lesson](software-engineering/design-patterns/lessons/03-factory-patterns.md) |
| 04 | Creational: Builder and Prototype | mid | [lesson](software-engineering/design-patterns/lessons/04-builder-prototype.md) |
| 05 | Creational: Singleton (and Its Problems) | junior | [lesson](software-engineering/design-patterns/lessons/05-singleton.md) |
| 06 | Structural: Adapter, Bridge, Composite | mid | [lesson](software-engineering/design-patterns/lessons/06-adapter-bridge-composite.md) |
| 07 | Structural: Decorator, Facade, Proxy | mid | [lesson](software-engineering/design-patterns/lessons/07-decorator-facade-proxy.md) |
| 08 | Structural: Flyweight | senior | [lesson](software-engineering/design-patterns/lessons/08-flyweight.md) |
| 09 | Behavioral: Strategy, Template Method, Observer | mid | [lesson](software-engineering/design-patterns/lessons/09-strategy-template-observer.md) |
| 10 | Behavioral: Command, State, Chain of Responsibility | senior | [lesson](software-engineering/design-patterns/lessons/10-command-state-chain.md) |
| 11 | Behavioral: Iterator, Mediator, Visitor, and the Rest | senior | [lesson](software-engineering/design-patterns/lessons/11-iterator-mediator-visitor.md) |

<a id="enterprise-patterns"></a>
### Patterns of Enterprise Application Architecture

14 lessons - [subject index](software-engineering/enterprise-patterns/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Layering and the Enterprise Application | mid | [lesson](software-engineering/enterprise-patterns/lessons/01-layering.md) |
| 02 | Domain Logic: Transaction Script vs Domain Model | senior | [lesson](software-engineering/enterprise-patterns/lessons/02-domain-logic-patterns.md) |
| 03 | Table Module and Service Layer | senior | [lesson](software-engineering/enterprise-patterns/lessons/03-table-module-service-layer.md) |
| 04 | Data Source: Row Data Gateway and Table Data Gateway | senior | [lesson](software-engineering/enterprise-patterns/lessons/04-data-source-gateways.md) |
| 05 | Active Record | mid | [lesson](software-engineering/enterprise-patterns/lessons/05-active-record.md) |
| 06 | Data Mapper | senior | [lesson](software-engineering/enterprise-patterns/lessons/06-data-mapper.md) |
| 07 | Unit of Work | senior | [lesson](software-engineering/enterprise-patterns/lessons/07-unit-of-work.md) |
| 08 | Identity Map and Lazy Load | senior | [lesson](software-engineering/enterprise-patterns/lessons/08-identity-map-lazy-load.md) |
| 09 | Object-Relational Structural Mapping (Inheritance) | senior | [lesson](software-engineering/enterprise-patterns/lessons/09-or-structural-mapping.md) |
| 10 | Object-Relational Metadata Mapping | senior | [lesson](software-engineering/enterprise-patterns/lessons/10-or-metadata-mapping.md) |
| 11 | Web Presentation (MVC, Page/Front Controller) | mid | [lesson](software-engineering/enterprise-patterns/lessons/11-web-presentation.md) |
| 12 | Concurrency: Optimistic vs Pessimistic Locking | senior | [lesson](software-engineering/enterprise-patterns/lessons/12-concurrency-locking.md) |
| 13 | Session State Patterns | mid | [lesson](software-engineering/enterprise-patterns/lessons/13-session-state.md) |
| 14 | Distribution and the Remote Facade / DTO | senior | [lesson](software-engineering/enterprise-patterns/lessons/14-distribution-remote-facade-dto.md) |

<a id="legacy-code"></a>
### Working Effectively with Legacy Code

12 lessons - [subject index](software-engineering/legacy-code/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What Legacy Code Is: The Change Dilemma | mid | [lesson](software-engineering/legacy-code/lessons/01-the-change-dilemma.md) |
| 02 | Seams and Enabling Points | senior | [lesson](software-engineering/legacy-code/lessons/02-seams.md) |
| 03 | Characterization Tests | mid | [lesson](software-engineering/legacy-code/lessons/03-characterization-tests.md) |
| 04 | Sensing and Separation | senior | [lesson](software-engineering/legacy-code/lessons/04-sensing-and-separation.md) |
| 05 | Breaking Dependencies (the Toolkit) | senior | [lesson](software-engineering/legacy-code/lessons/05-breaking-dependencies.md) |
| 06 | It Takes Forever to Make a Change | senior | [lesson](software-engineering/legacy-code/lessons/06-slow-to-change.md) |
| 07 | Adding a Feature to Untested Code | senior | [lesson](software-engineering/legacy-code/lessons/07-adding-a-feature.md) |
| 08 | I Can't Get This Class into a Test Harness | senior | [lesson](software-engineering/legacy-code/lessons/08-class-into-harness.md) |
| 09 | I Can't Run a Method in a Test Harness | senior | [lesson](software-engineering/legacy-code/lessons/09-method-into-harness.md) |
| 10 | Finding What and Where to Change | mid | [lesson](software-engineering/legacy-code/lessons/10-finding-where-to-change.md) |
| 11 | Dependency-Breaking Techniques Catalog | senior | [lesson](software-engineering/legacy-code/lessons/11-techniques-catalog.md) |
| 12 | Working with Big, Tangled Methods | senior | [lesson](software-engineering/legacy-code/lessons/12-big-tangled-methods.md) |

<a id="philosophy-of-software-design"></a>
### A Philosophy of Software Design

11 lessons - [subject index](software-engineering/philosophy-of-software-design/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Complexity Is the Enemy: Symptoms and Causes | mid | [lesson](software-engineering/philosophy-of-software-design/lessons/01-complexity-is-the-enemy.md) |
| 02 | Working Code Is Not Enough (Strategic vs Tactical) | senior | [lesson](software-engineering/philosophy-of-software-design/lessons/02-strategic-vs-tactical.md) |
| 03 | Modules Should Be Deep | senior | [lesson](software-engineering/philosophy-of-software-design/lessons/03-deep-modules.md) |
| 04 | Information Hiding and Leakage | senior | [lesson](software-engineering/philosophy-of-software-design/lessons/04-information-hiding.md) |
| 05 | General-Purpose Modules Are Deeper | senior | [lesson](software-engineering/philosophy-of-software-design/lessons/05-general-purpose-modules.md) |
| 06 | Pulling Complexity Downward | senior | [lesson](software-engineering/philosophy-of-software-design/lessons/06-pulling-complexity-downward.md) |
| 07 | Different Layer, Different Abstraction | senior | [lesson](software-engineering/philosophy-of-software-design/lessons/07-different-layer-different-abstraction.md) |
| 08 | Define Errors (and Special Cases) Out of Existence | senior | [lesson](software-engineering/philosophy-of-software-design/lessons/08-define-errors-out-of-existence.md) |
| 09 | Comments Describe Things the Code Cannot | mid | [lesson](software-engineering/philosophy-of-software-design/lessons/09-comments.md) |
| 10 | Choosing Names and Consistency | mid | [lesson](software-engineering/philosophy-of-software-design/lessons/10-naming-consistency.md) |
| 11 | Design Tensions and When Principles Conflict | senior | [lesson](software-engineering/philosophy-of-software-design/lessons/11-design-tensions.md) |

<a id="pragmatic-programmer"></a>
### The Pragmatic Programmer

15 lessons - [subject index](software-engineering/pragmatic-programmer/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | The Pragmatic Philosophy and Taking Responsibility | junior | [lesson](software-engineering/pragmatic-programmer/lessons/01-pragmatic-philosophy.md) |
| 02 | Software Entropy and the Broken-Windows Theory | junior | [lesson](software-engineering/pragmatic-programmer/lessons/02-software-entropy.md) |
| 03 | DRY and the Evils of Duplication | junior | [lesson](software-engineering/pragmatic-programmer/lessons/03-dry-duplication.md) |
| 04 | Orthogonality and Decoupling | mid | [lesson](software-engineering/pragmatic-programmer/lessons/04-orthogonality.md) |
| 05 | Reversibility and Tracer Bullets | senior | [lesson](software-engineering/pragmatic-programmer/lessons/05-reversibility-tracer-bullets.md) |
| 06 | Prototyping and Estimating | mid | [lesson](software-engineering/pragmatic-programmer/lessons/06-prototyping-estimating.md) |
| 07 | The Power of Plain Text and the Shell | junior | [lesson](software-engineering/pragmatic-programmer/lessons/07-plain-text-shell.md) |
| 08 | Debugging and Rubber Ducking | junior | [lesson](software-engineering/pragmatic-programmer/lessons/08-debugging.md) |
| 09 | Design by Contract and Assertive Programming | mid | [lesson](software-engineering/pragmatic-programmer/lessons/09-design-by-contract.md) |
| 10 | Decoupling: The Law of Demeter and Configuration | mid | [lesson](software-engineering/pragmatic-programmer/lessons/10-decoupling-demeter.md) |
| 11 | Concurrency and Temporal Coupling | senior | [lesson](software-engineering/pragmatic-programmer/lessons/11-concurrency-temporal-coupling.md) |
| 12 | Transforming Programming and Error Handling | mid | [lesson](software-engineering/pragmatic-programmer/lessons/12-transforming-programming.md) |
| 13 | Pragmatic Testing and Property-Based Testing | mid | [lesson](software-engineering/pragmatic-programmer/lessons/13-pragmatic-testing.md) |
| 14 | Requirements and the Requirements Pit | senior | [lesson](software-engineering/pragmatic-programmer/lessons/14-requirements.md) |
| 15 | Pragmatic Teams and Pride in Your Work | senior | [lesson](software-engineering/pragmatic-programmer/lessons/15-pragmatic-teams.md) |

<a id="refactoring"></a>
### Refactoring

12 lessons - [subject index](software-engineering/refactoring/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What Refactoring Is (and Is Not) | junior | [lesson](software-engineering/refactoring/lessons/01-what-refactoring-is.md) |
| 02 | Why Refactor, and When | mid | [lesson](software-engineering/refactoring/lessons/02-why-and-when.md) |
| 03 | Tests as the Safety Net | mid | [lesson](software-engineering/refactoring/lessons/03-tests-safety-net.md) |
| 04 | Code Smells: A Catalog | mid | [lesson](software-engineering/refactoring/lessons/04-code-smells.md) |
| 05 | Composing Methods (Extract/Inline) | junior | [lesson](software-engineering/refactoring/lessons/05-composing-methods.md) |
| 06 | Moving Features Between Objects | mid | [lesson](software-engineering/refactoring/lessons/06-moving-features.md) |
| 07 | Organizing Data | mid | [lesson](software-engineering/refactoring/lessons/07-organizing-data.md) |
| 08 | Simplifying Conditional Logic | mid | [lesson](software-engineering/refactoring/lessons/08-simplifying-conditionals.md) |
| 09 | Refactoring APIs and Parameters | mid | [lesson](software-engineering/refactoring/lessons/09-refactoring-apis.md) |
| 10 | Dealing with Inheritance | mid | [lesson](software-engineering/refactoring/lessons/10-inheritance.md) |
| 11 | Big Refactorings and Breaking Dependencies | senior | [lesson](software-engineering/refactoring/lessons/11-big-refactorings.md) |
| 12 | Refactoring, Architecture, and YAGNI | senior | [lesson](software-engineering/refactoring/lessons/12-refactoring-architecture-yagni.md) |

---

<a id="software-quality"></a>
## Software Quality

<a id="goos"></a>
### Growing Object-Oriented Software, Guided by Tests

12 lessons - [subject index](software-quality/goos/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | TDD as Fast Feedback for Behavior | mid | [lesson](software-quality/goos/lessons/01-tdd-fast-feedback.md) |
| 02 | Growing Software in Vertical Slices | senior | [lesson](software-quality/goos/lessons/02-vertical-slices.md) |
| 03 | Walking Skeleton and Deployment Pipeline | senior | [lesson](software-quality/goos/lessons/03-walking-skeleton.md) |
| 04 | Outside-In Development from Acceptance Tests | senior | [lesson](software-quality/goos/lessons/04-outside-in-development.md) |
| 05 | Mock Objects and Role-Based Design | senior | [lesson](software-quality/goos/lessons/05-mock-objects-role-design.md) |
| 06 | Ports and Adapters at System Boundaries | senior | [lesson](software-quality/goos/lessons/06-ports-and-adapters.md) |
| 07 | Designing Object Protocols Through Collaboration Tests | senior | [lesson](software-quality/goos/lessons/07-object-protocols.md) |
| 08 | Testing Asynchronous and Event-Driven Behavior | senior | [lesson](software-quality/goos/lessons/08-async-event-driven-testing.md) |
| 09 | Keeping Tests Expressive and Diagnosing Failures | senior | [lesson](software-quality/goos/lessons/09-expressive-tests-diagnostics.md) |
| 10 | Managing Coupling and Avoiding Brittle Interaction Tests | senior | [lesson](software-quality/goos/lessons/10-managing-test-coupling.md) |
| 11 | Emergent Architecture Through Continuous Refactoring | senior | [lesson](software-quality/goos/lessons/11-emergent-architecture.md) |
| 12 | Test Strategy Across a Service Ecosystem | staff | [lesson](software-quality/goos/lessons/12-service-ecosystem-strategy.md) |

<a id="unit-testing"></a>
### Unit Testing: Principles, Practices, and Patterns

13 lessons - [subject index](software-quality/unit-testing/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What a Unit Test Is and Why It Matters | junior | [lesson](software-quality/unit-testing/lessons/01-what-a-unit-test-is.md) |
| 02 | AAA Structure and Test Naming | junior | [lesson](software-quality/unit-testing/lessons/02-aaa-and-naming.md) |
| 03 | The Four Pillars of Good Tests | senior | [lesson](software-quality/unit-testing/lessons/03-four-pillars.md) |
| 04 | Behavioral vs. Implementation Coupling | senior | [lesson](software-quality/unit-testing/lessons/04-behavioral-vs-implementation-coupling.md) |
| 05 | Humble Object and Separating Pure Logic | mid | [lesson](software-quality/unit-testing/lessons/05-humble-object.md) |
| 06 | Shared State, Isolation, and Deterministic Tests | mid | [lesson](software-quality/unit-testing/lessons/06-isolation-and-determinism.md) |
| 07 | Types of Test Doubles and Trade-offs | mid | [lesson](software-quality/unit-testing/lessons/07-test-doubles-trade-offs.md) |
| 08 | Mocking Guidelines and Interaction Testing Limits | senior | [lesson](software-quality/unit-testing/lessons/08-mocking-guidelines.md) |
| 09 | London vs. Classical Schools in Practice | senior | [lesson](software-quality/unit-testing/lessons/09-london-vs-classical.md) |
| 10 | Integration Testing Around External Systems | senior | [lesson](software-quality/unit-testing/lessons/10-integration-testing-boundaries.md) |
| 11 | Testing Controllers and Application Services | mid | [lesson](software-quality/unit-testing/lessons/11-testing-controllers-services.md) |
| 12 | Handling Time, Randomness, and Concurrency in Tests | senior | [lesson](software-quality/unit-testing/lessons/12-time-randomness-concurrency.md) |
| 13 | Building a Balanced Test Strategy for a Codebase | staff | [lesson](software-quality/unit-testing/lessons/13-balanced-test-strategy.md) |

<a id="xunit-test-patterns"></a>
### xUnit Test Patterns: Refactoring Test Code

12 lessons - [subject index](software-quality/xunit-test-patterns/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Anatomy of an xUnit Test and Fixture | junior | [lesson](software-quality/xunit-test-patterns/lessons/01-xunit-anatomy-and-fixture.md) |
| 02 | Four-Phase Test and Intent-Revealing Style | junior | [lesson](software-quality/xunit-test-patterns/lessons/02-four-phase-intent-revealing.md) |
| 03 | Assertion Patterns and Failure Diagnostics | mid | [lesson](software-quality/xunit-test-patterns/lessons/03-assertion-patterns.md) |
| 04 | Fixture Setup and Teardown Patterns | mid | [lesson](software-quality/xunit-test-patterns/lessons/04-fixture-setup-teardown.md) |
| 05 | Test Doubles in xUnit Patterns Language | mid | [lesson](software-quality/xunit-test-patterns/lessons/05-test-doubles-pattern-language.md) |
| 06 | Obscure Test Smell and Readability Refactorings | mid | [lesson](software-quality/xunit-test-patterns/lessons/06-obscure-test-smell.md) |
| 07 | Fragile Test Smell and Brittleness Controls | senior | [lesson](software-quality/xunit-test-patterns/lessons/07-fragile-test-smell.md) |
| 08 | Slow Tests and Suite Execution Economics | senior | [lesson](software-quality/xunit-test-patterns/lessons/08-slow-tests-economics.md) |
| 09 | Data Management Patterns for Repeatable Tests | mid | [lesson](software-quality/xunit-test-patterns/lessons/09-test-data-management.md) |
| 10 | Result Verification and Behavior vs State Checks | mid | [lesson](software-quality/xunit-test-patterns/lessons/10-result-verification.md) |
| 11 | Test Code Refactoring Workflow and Safety Net | senior | [lesson](software-quality/xunit-test-patterns/lessons/11-test-code-refactoring-workflow.md) |
| 12 | Building a Maintainable Test Suite Architecture | senior | [lesson](software-quality/xunit-test-patterns/lessons/12-test-suite-architecture.md) |

---

<a id="technical-leadership"></a>
## Technical Leadership

<a id="accelerate"></a>
### Accelerate: The Science of Lean Software and DevOps

12 lessons - [subject index](technical-leadership/accelerate/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Why software delivery performance is a strategic capability | senior | [lesson](technical-leadership/accelerate/lessons/01-delivery-performance-as-capability.md) |
| 02 | The DORA model and validated research approach | senior | [lesson](technical-leadership/accelerate/lessons/02-dora-model-and-research.md) |
| 03 | Deployment frequency and lead time for changes | senior | [lesson](technical-leadership/accelerate/lessons/03-deployment-frequency-and-lead-time.md) |
| 04 | Change failure rate and time to restore service | senior | [lesson](technical-leadership/accelerate/lessons/04-change-failure-and-restore-time.md) |
| 05 | Continuous delivery foundations and small-batch flow | senior | [lesson](technical-leadership/accelerate/lessons/05-continuous-delivery-foundations.md) |
| 06 | Architecture for flow: loosely coupled teams and systems | staff | [lesson](technical-leadership/accelerate/lessons/06-architecture-for-flow.md) |
| 07 | Test automation and build quality as throughput constraints | senior | [lesson](technical-leadership/accelerate/lessons/07-test-automation-and-build-quality.md) |
| 08 | Security as an integrated delivery practice | staff | [lesson](technical-leadership/accelerate/lessons/08-integrated-security-practice.md) |
| 09 | Lean management and generative culture | staff | [lesson](technical-leadership/accelerate/lessons/09-lean-management-and-culture.md) |
| 10 | Measuring productivity without vanity metrics | senior | [lesson](technical-leadership/accelerate/lessons/10-measuring-productivity.md) |
| 11 | Leading transformation using capability-based interventions | staff | [lesson](technical-leadership/accelerate/lessons/11-leading-transformation.md) |
| 12 | Sustaining high performance and preventing local optimization | staff | [lesson](technical-leadership/accelerate/lessons/12-sustaining-high-performance.md) |

<a id="elegant-puzzle"></a>
### An Elegant Puzzle: Systems of Engineering Management

13 lessons - [subject index](technical-leadership/elegant-puzzle/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Engineering management as systems design | staff | [lesson](technical-leadership/elegant-puzzle/lessons/01-management-as-systems-design.md) |
| 02 | Debugging organizations with systems thinking | staff | [lesson](technical-leadership/elegant-puzzle/lessons/02-debugging-organizations.md) |
| 03 | Team sizing, composition, and cognitive load | staff | [lesson](technical-leadership/elegant-puzzle/lessons/03-team-sizing-and-load.md) |
| 04 | Organizational design: functional, product, and matrix shapes | principal | [lesson](technical-leadership/elegant-puzzle/lessons/04-organizational-design.md) |
| 05 | Splitting and merging teams as the organization evolves | staff | [lesson](technical-leadership/elegant-puzzle/lessons/05-splitting-and-merging-teams.md) |
| 06 | Technical strategy as a management instrument | staff | [lesson](technical-leadership/elegant-puzzle/lessons/06-technical-strategy.md) |
| 07 | Planning and execution in medium and large organizations | senior | [lesson](technical-leadership/elegant-puzzle/lessons/07-planning-and-execution.md) |
| 08 | Hiring systems and onboarding for sustainable growth | staff | [lesson](technical-leadership/elegant-puzzle/lessons/08-hiring-and-onboarding-systems.md) |
| 09 | Career ladders and calibration frameworks | principal | [lesson](technical-leadership/elegant-puzzle/lessons/09-career-ladders-and-calibration.md) |
| 10 | Feedback systems and performance management | staff | [lesson](technical-leadership/elegant-puzzle/lessons/10-feedback-and-performance-systems.md) |
| 11 | Managing incidents and reliability as organizational practice | staff | [lesson](technical-leadership/elegant-puzzle/lessons/11-incident-and-reliability-practice.md) |
| 12 | Reorganizations and change management without chaos | principal | [lesson](technical-leadership/elegant-puzzle/lessons/12-reorganizations-and-change.md) |
| 13 | Building resilient engineering leadership at scale | principal | [lesson](technical-leadership/elegant-puzzle/lessons/13-resilient-leadership-at-scale.md) |

<a id="how-to-measure-anything"></a>
### How to Measure Anything: Finding the Value of Intangibles in Business

11 lessons - [subject index](technical-leadership/how-to-measure-anything/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Why "intangibles" are usually measurable enough for decisions | senior | [lesson](technical-leadership/how-to-measure-anything/lessons/01-intangibles-are-measurable.md) |
| 02 | Measurement as uncertainty reduction, not perfect precision | senior | [lesson](technical-leadership/how-to-measure-anything/lessons/02-measurement-as-uncertainty-reduction.md) |
| 03 | Calibrated estimation and confidence intervals | senior | [lesson](technical-leadership/how-to-measure-anything/lessons/03-calibrated-estimation.md) |
| 04 | Decomposition: breaking fuzzy variables into observable parts | senior | [lesson](technical-leadership/how-to-measure-anything/lessons/04-decomposition-of-variables.md) |
| 05 | Designing useful metrics tied to concrete decisions | staff | [lesson](technical-leadership/how-to-measure-anything/lessons/05-designing-useful-metrics.md) |
| 06 | Sampling methods for fast, low-cost evidence gathering | senior | [lesson](technical-leadership/how-to-measure-anything/lessons/06-sampling-methods.md) |
| 07 | Monte Carlo simulation for decision uncertainty | staff | [lesson](technical-leadership/how-to-measure-anything/lessons/07-monte-carlo-simulation.md) |
| 08 | Bayesian updates and integrating new evidence | staff | [lesson](technical-leadership/how-to-measure-anything/lessons/08-bayesian-updates.md) |
| 09 | Value of information and when measurement is worth the cost | staff | [lesson](technical-leadership/how-to-measure-anything/lessons/09-value-of-information.md) |
| 10 | Quantifying risk and opportunity in portfolio decisions | principal | [lesson](technical-leadership/how-to-measure-anything/lessons/10-portfolio-risk-and-opportunity.md) |
| 11 | Embedding measurement discipline in organizational decision-making | principal | [lesson](technical-leadership/how-to-measure-anything/lessons/11-embedding-measurement-discipline.md) |

<a id="managers-path"></a>
### The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change

13 lessons - [subject index](technical-leadership/managers-path/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | Mentoring as the first leadership responsibility | senior | [lesson](technical-leadership/managers-path/lessons/01-mentoring-as-first-leadership.md) |
| 02 | Tech lead responsibilities and hybrid leadership | senior | [lesson](technical-leadership/managers-path/lessons/02-tech-lead-responsibilities.md) |
| 03 | Becoming an engineering manager: role reset and priorities | staff | [lesson](technical-leadership/managers-path/lessons/03-becoming-an-engineering-manager.md) |
| 04 | Running one-on-ones and building trust loops | senior | [lesson](technical-leadership/managers-path/lessons/04-one-on-ones-and-trust.md) |
| 05 | Giving feedback and managing performance conversations | staff | [lesson](technical-leadership/managers-path/lessons/05-feedback-and-performance.md) |
| 06 | Managing healthy teams: communication, conflict, and delivery | staff | [lesson](technical-leadership/managers-path/lessons/06-managing-healthy-teams.md) |
| 07 | Hiring and interviewing as a management system | staff | [lesson](technical-leadership/managers-path/lessons/07-hiring-and-interviewing.md) |
| 08 | Managing managers and creating leadership layers | principal | [lesson](technical-leadership/managers-path/lessons/08-managing-managers.md) |
| 09 | Technical strategy for engineering managers and directors | staff | [lesson](technical-leadership/managers-path/lessons/09-technical-strategy-for-managers.md) |
| 10 | Director scope: organization design and cross-team planning | principal | [lesson](technical-leadership/managers-path/lessons/10-director-scope.md) |
| 11 | VP of engineering scope: multi-org alignment and execution | principal | [lesson](technical-leadership/managers-path/lessons/11-vp-engineering-scope.md) |
| 12 | CTO scope: technology vision and company strategy | principal | [lesson](technical-leadership/managers-path/lessons/12-cto-scope.md) |
| 13 | Navigating growth transitions and your own leadership evolution | principal | [lesson](technical-leadership/managers-path/lessons/13-navigating-growth-transitions.md) |

<a id="staff-engineer"></a>
### Staff Engineer: Leadership Beyond the Management Track

12 lessons - [subject index](technical-leadership/staff-engineer/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | What staff-plus means and how impact is evaluated | staff | [lesson](technical-leadership/staff-engineer/lessons/01-what-staff-plus-means.md) |
| 02 | Staff archetypes: tech lead, architect, solver, and right hand | staff | [lesson](technical-leadership/staff-engineer/lessons/02-staff-archetypes.md) |
| 03 | Expanding scope from team outcomes to organizational outcomes | staff | [lesson](technical-leadership/staff-engineer/lessons/03-expanding-scope.md) |
| 04 | Choosing an archetype that matches business and organizational needs | staff | [lesson](technical-leadership/staff-engineer/lessons/04-choosing-archetype.md) |
| 05 | Earning the staff title: promotion packets, sponsors, and timing | senior | [lesson](technical-leadership/staff-engineer/lessons/05-earning-staff-title.md) |
| 06 | Writing strategy documents that align technical and business direction | staff | [lesson](technical-leadership/staff-engineer/lessons/06-writing-strategy-documents.md) |
| 07 | Leading without authority through influence networks | staff | [lesson](technical-leadership/staff-engineer/lessons/07-leading-without-authority.md) |
| 08 | Operating rhythms: planning, reviews, and executive communication | senior | [lesson](technical-leadership/staff-engineer/lessons/08-operating-rhythms.md) |
| 09 | Running critical initiatives across multiple teams | staff | [lesson](technical-leadership/staff-engineer/lessons/09-running-critical-initiatives.md) |
| 10 | Partnering effectively with engineering managers and peers | staff | [lesson](technical-leadership/staff-engineer/lessons/10-partnering-with-managers.md) |
| 11 | Multiplying impact by developing successors and technical leaders | principal | [lesson](technical-leadership/staff-engineer/lessons/11-developing-successors.md) |
| 12 | Sustaining a long-term staff-plus career and avoiding common traps | principal | [lesson](technical-leadership/staff-engineer/lessons/12-sustaining-staff-career.md) |

<a id="staff-engineers-path"></a>
### The Staff Engineer's Path

14 lessons - [subject index](technical-leadership/staff-engineers-path/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | The three pillars of staff engineering | staff | [lesson](technical-leadership/staff-engineers-path/lessons/01-three-pillars.md) |
| 02 | Finding and framing high-leverage problems | staff | [lesson](technical-leadership/staff-engineers-path/lessons/02-framing-high-leverage-problems.md) |
| 03 | Making better bets with strategic context | staff | [lesson](technical-leadership/staff-engineers-path/lessons/03-making-better-bets.md) |
| 04 | Seeing systems, not components: broad technical context | staff | [lesson](technical-leadership/staff-engineers-path/lessons/04-seeing-systems.md) |
| 05 | Defining and communicating technical direction | staff | [lesson](technical-leadership/staff-engineers-path/lessons/05-technical-direction.md) |
| 06 | Navigating ambiguity with incremental execution plans | senior | [lesson](technical-leadership/staff-engineers-path/lessons/06-navigating-ambiguity.md) |
| 07 | Driving execution through collaboration and delegation | staff | [lesson](technical-leadership/staff-engineers-path/lessons/07-driving-execution.md) |
| 08 | Decision records and alignment artifacts that scale | senior | [lesson](technical-leadership/staff-engineers-path/lessons/08-alignment-artifacts.md) |
| 09 | Raising quality bars with reviews and technical standards | staff | [lesson](technical-leadership/staff-engineers-path/lessons/09-raising-quality-bars.md) |
| 10 | Sponsoring projects so teams can move faster independently | staff | [lesson](technical-leadership/staff-engineers-path/lessons/10-sponsoring-projects.md) |
| 11 | Mentoring and coaching for durable capability growth | staff | [lesson](technical-leadership/staff-engineers-path/lessons/11-mentoring-and-coaching.md) |
| 12 | Building communities of practice across teams | staff | [lesson](technical-leadership/staff-engineers-path/lessons/12-communities-of-practice.md) |
| 13 | Managing your energy, reputation, and sustainable pace | senior | [lesson](technical-leadership/staff-engineers-path/lessons/13-sustainable-pace.md) |
| 14 | Becoming a force multiplier at organization scale | principal | [lesson](technical-leadership/staff-engineers-path/lessons/14-force-multiplier.md) |

<a id="thinking-fast-and-slow"></a>
### Thinking, Fast and Slow

14 lessons - [subject index](technical-leadership/thinking-fast-and-slow/README.md)

| # | Concept | Seniority | Lesson |
| - | ------- | --------- | ------ |
| 01 | System 1 and System 2: two modes of thinking | mid | [lesson](technical-leadership/thinking-fast-and-slow/lessons/01-system-1-and-system-2.md) |
| 02 | Attention, effort, and cognitive load | mid | [lesson](technical-leadership/thinking-fast-and-slow/lessons/02-attention-effort-and-load.md) |
| 03 | Heuristics as useful shortcuts and failure sources | mid | [lesson](technical-leadership/thinking-fast-and-slow/lessons/03-heuristics-shortcuts.md) |
| 04 | Anchoring and adjustment bias | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/04-anchoring-and-adjustment.md) |
| 05 | Availability bias and salience-driven judgment | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/05-availability-bias.md) |
| 06 | Representativeness and base-rate neglect | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/06-representativeness-base-rates.md) |
| 07 | Overconfidence, planning fallacy, and optimism bias | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/07-overconfidence-planning-fallacy.md) |
| 08 | Confirmation bias and coherence illusions | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/08-confirmation-and-coherence.md) |
| 09 | Framing effects and decision architecture | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/09-framing-effects.md) |
| 10 | Regression to the mean and causal misattribution | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/10-regression-and-causality.md) |
| 11 | Prospect theory: value functions and loss aversion | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/11-prospect-theory.md) |
| 12 | Risk preferences in gains versus losses | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/12-risk-preferences.md) |
| 13 | The remembering self versus the experiencing self | mid | [lesson](technical-leadership/thinking-fast-and-slow/lessons/13-remembering-vs-experiencing-self.md) |
| 14 | Practical debiasing for better decisions | senior | [lesson](technical-leadership/thinking-fast-and-slow/lessons/14-practical-debiasing.md) |

---

Back to [README.md](README.md#domains-at-a-glance) for the condensed domain overview and how to get started.
