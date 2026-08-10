# Changelog

All notable changes to the **Oh My Learning** library are documented here.

This project tracks *library content and agent rules* - domains, subjects, lessons, the
agent's operating manual, templates, and tooling. Personal learning artifacts (discussion
records, status/mastery edits, progress tables) are never released and never appear here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with
categories adapted for a learning library, and versioning follows a content-adapted
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). See
[agent-docs/release-policy.md](agent-docs/release-policy.md) for the rules that govern
this file.

## [Unreleased]

### Added

- **Structured progress tracking** - a new `agent-docs/progress-tracking.md` defines
  `PROGRESS.md`, a per-learner, LLM-optimized index (structured track, Next up, Focus
  areas, Stats, Recent sessions) derived from lesson front matter, plus Workflow P for
  answering progress questions from that file alone. `templates/progress-template.md`
  seeds new instances. Onboarding (`learner-profile.md`, Step 4) now produces this
  structured track alongside the prose learning path, and discussions
  (`learning-workflows.md`, Workflow C) update it after every session.
  `repository-model.md` and `git-policy.md` document its place in the repo layout and
  its commit/anti-conflict treatment (personal, committed on the learner's branch/fork,
  never on `main`).

### Changed

- **Website redesign** - the static reading site (`website/`) got a full visual
  overhaul: a light/dark theme with a persisted toggle and system-preference default;
  refined typography and a constrained reading measure; a landing hero with library
  stats; progress bars on domain and subject cards; and richer lesson rows showing
  seniority, status, and estimated reading time. Lesson pages now render a sticky "On
  this page" table of contents, previous/next navigation within a subject, and properly
  styled code blocks (the generator now emits theme-aware Pygments syntax-highlighting
  CSS, which was previously missing). `website/build.py` computes reading time, the TOC,
  and lesson neighbors; the templates and stylesheet were rewritten to match.

## [0.2.0] - 2026-07-02

### Added

- **Learner onboarding and personalization** - on first contact (and at the start of
  every session) the agent now gets to know the learner before advising: it first makes
  sure the session is on a personal `learn/<name>` branch - creating and switching to one
  itself so the learner never runs git commands and personal progress never lands on
  `main` - then asks their name and how they want to be addressed, their seniority (briefly
  assessing it when the learner is unsure), and their goals/concerns, then proposes a
  learning path calibrated to their level. It keeps durable, per-learner notes in a
  personal `LEARNER.md` at the repo root - read at the start of every session and updated
  whenever the learner changes their name, address, seniority, goals, or how they want to
  be treated. New authoritative agent doc
  [agent-docs/learner-profile.md](agent-docs/learner-profile.md) (wired into
  [AGENTS.md](AGENTS.md) as a load-on-demand doc, a core-loop step, and a non-negotiable)
  and a copyable [templates/learner-profile-template.md](templates/learner-profile-template.md);
  the agent-managed learner-branch rule is documented in
  [agent-docs/git-policy.md](agent-docs/git-policy.md). `LEARNER.md` is personal: it is
  gitignored and never committed to `main` (like discussion records and progress).
- **Seniority model** - every lesson now carries a `seniority` band
  (`junior`/`mid`/`senior`/`staff`/`principal`) and every subject declares a seniority
  baseline. The band measures whose job a concept anchors, not reading difficulty, and it
  calibrates how deeply the agent runs a Socratic discussion. New authoritative agent doc
  [agent-docs/seniority-model.md](agent-docs/seniority-model.md) (wired into
  [AGENTS.md](AGENTS.md)) and learner-facing [SENIORITY.md](SENIORITY.md); the lesson
  template, [repository-model.md](agent-docs/repository-model.md), and
  [learning-workflows.md](agent-docs/learning-workflows.md) updated accordingly. Every
  existing subject `README.md` gained a **Seniority** column and a baseline line.
- **Six new subject scaffolds in the `architecture/` domain** - subject `README.md`
  indexes with dependency-ordered concept lists (all `drafted`) and empty `lessons/` and
  `discussions/` folders; lesson bodies are not yet authored:
  - **Building Microservices** - *Building Microservices*, 2nd ed. (Newman): 17 concepts.
    See [architecture/building-microservices/README.md](architecture/building-microservices/README.md).
  - **Microservices Patterns** - *Microservices Patterns* (Richardson): 12 concepts.
    See [architecture/microservices-patterns/README.md](architecture/microservices-patterns/README.md).
  - **Designing Distributed Systems** - *Designing Distributed Systems* (Burns): 12
    concepts. See
    [architecture/designing-distributed-systems/README.md](architecture/designing-distributed-systems/README.md).
  - **Distributed Systems** - *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum): 12
    concepts. See [architecture/distributed-systems/README.md](architecture/distributed-systems/README.md).
  - **Evolutionary Architectures** - *Building Evolutionary Architectures*, 2nd ed. (Ford,
    Parsons, Kua, Sadalage): 9 concepts. See
    [architecture/evolutionary-architectures/README.md](architecture/evolutionary-architectures/README.md).
  - **System Design Interview** - *System Design Interview*, Vol. 1 (Xu): 15 concepts. See
    [architecture/system-design-interview/README.md](architecture/system-design-interview/README.md).
- **`software-engineering/` domain** grouping the book-subjects that teach how to write
  maintainable, evolvable software - see
  [software-engineering/README.md](software-engineering/README.md). Scaffolded with nine
  subject `README.md` indexes (dependency-ordered concept lists, all `drafted`) and empty
  `lessons/` and `discussions/` folders; lesson bodies are not yet authored:
  - **The Pragmatic Programmer** (Hunt & Thomas): 15 concepts.
  - **Code Complete** (McConnell): 14 concepts.
  - **Clean Architecture** (Martin): 13 concepts.
  - **Clean Code** (Martin): 12 concepts.
  - **Refactoring** (Fowler): 12 concepts.
  - **A Philosophy of Software Design** (Ousterhout): 11 concepts.
  - **Working Effectively with Legacy Code** (Feathers): 12 concepts.
  - **Patterns of Enterprise Application Architecture** (Fowler): 14 concepts.
  - **Design Patterns** (Gang of Four): 11 concepts.
- **`domain-modeling/` domain** (modeling business complexity with Domain-Driven Design) -
  see [domain-modeling/README.md](domain-modeling/README.md). Scaffolded with four subject
  indexes (dependency-ordered concept lists, all `drafted`, per-lesson seniority) and empty
  `lessons/`/`discussions/` folders; lesson bodies not yet authored: **DDD** (Evans) 16,
  **Implementing DDD** (Vernon) 15, **Learning DDD** (Khononov) 14, **DDD Distilled**
  (Vernon) 9.
- **`data-engineering/` domain** (choosing, designing, and understanding storage systems;
  DDIA cross-referenced from `architecture/`) - see
  [data-engineering/README.md](data-engineering/README.md). Scaffolded: **Database
  Internals** (Petrov) 16, **SQL Performance Explained** (Winand) 10, **Seven Databases in
  Seven Weeks** (Perkins, Redmond, Wilson) 9.
- **`cs-fundamentals/` domain** (algorithms, data structures, concurrency) - see
  [cs-fundamentals/README.md](cs-fundamentals/README.md). Scaffolded: **Introduction to
  Algorithms** (CLRS) 20, **Algorithms** (Sedgewick & Wayne) 14, **Algorithm Design**
  (Kleinberg & Tardos) 12, **Java Concurrency in Practice** (Goetz et al.) 15, **The Art of
  Multiprocessor Programming** (Herlihy & Shavit) 13.
- **`software-quality/` domain** (testing and reliability) - see
  [software-quality/README.md](software-quality/README.md). Scaffolded: **GOOS** (Freeman &
  Pryce) 12, **Unit Testing** (Khorikov) 13, **xUnit Test Patterns** (Meszaros) 12.
- **`devops-reliability/` domain** (operating software in production) - see
  [devops-reliability/README.md](devops-reliability/README.md). Scaffolded: **The Phoenix
  Project** (Kim, Behr, Spafford) 10, **The DevOps Handbook** (Kim, Humble, Debois, Willis)
  16, **Site Reliability Engineering** (Beyer, Jones, Petoff, Murphy) 16, **Seeking SRE**
  (Blank-Edelman, ed.) 12.
- **`technical-leadership/` domain** (growing beyond coding) - see
  [technical-leadership/README.md](technical-leadership/README.md). Scaffolded: **Staff
  Engineer** (Larson) 12, **The Staff Engineer's Path** (Reilly) 14, **An Elegant Puzzle**
  (Larson) 13, **The Manager's Path** (Fournier) 13, **Accelerate** (Forsgren, Humble, Kim)
  12, **Thinking, Fast and Slow** (Kahneman) 14, **How to Measure Anything** (Hubbard) 11.
- **Local static website** for browsing lessons in a browser instead of reading raw
  Markdown. Added `website/build.py`, `website/serve.py`, `website/requirements.txt`,
  templates under `website/templates/`, and `website/static/style.css`; documented in
  [agent-docs/website.md](agent-docs/website.md) and the root [README.md](README.md).

### Changed

- **Every existing subject `README.md`** (the four authored architecture subjects and all
  scaffolded subjects) gained a **Seniority** column and a seniority-baseline line as part
  of introducing the seniority model.
- **`architecture/` domain index** and the cross-domain root [SUMMARY.md](SUMMARY.md)
  updated to list the six new architecture subjects, the new `software-engineering/` domain,
  and the six further new domains (domain modeling, data engineering, CS fundamentals,
  software quality, DevOps/reliability, technical leadership), and to note DDIA's
  cross-reference to the Data Engineering domain.
- **Root [README.md](README.md)** subjects section expanded to all eight domains, with a
  seniority explanation and a link to [SENIORITY.md](SENIORITY.md).

### Deepened

- **Microservices Patterns** subject - authored all 12 lesson bodies (was scaffolded):
  `microservices-patterns/01` through `microservices-patterns/12`. See
  [architecture/microservices-patterns/README.md](architecture/microservices-patterns/README.md).
- **Designing Distributed Systems** subject - authored all 12 lesson bodies (was
  scaffolded): `designing-distributed-systems/01` through
  `designing-distributed-systems/12`. See
  [architecture/designing-distributed-systems/README.md](architecture/designing-distributed-systems/README.md).


## [0.1.0] - 2026-06-30

Initial public release of the library: the **architecture** domain with four subjects and
75 lessons, the agent operating manual, the lesson/discussion templates, and the
repository tooling.

### Added

- **`architecture/` domain** grouping the book-subjects that teach how to design software
  systems - see [architecture/README.md](architecture/README.md).
- **DDIA** subject - *Designing Data-Intensive Applications* (Kleppmann): 16 lessons on
  reliability/scalability, data models and query languages, storage engines (OLTP/OLAP,
  column storage), encoding and schema evolution, replication, partitioning, transactions,
  distributed-systems failure modes, consistency/consensus, and batch/stream processing.
  See [architecture/ddia/README.md](architecture/ddia/README.md).
- **System Design** subject - *System Design Guide for Software Professionals* (Sinha &
  Chopra): 20 lessons applying DDIA theory to real systems - fundamentals, distributed
  attributes, CAP/PACELC/consensus, consistent hashing, probabilistic data structures,
  DNS/load balancing, gateways/proxies, databases/storage, replication/sharding,
  distributed caching, pub/sub and queues, API design, security/auth, rate limiting and
  resilience, observability, a design method, and case studies (URL shortener, news feed,
  real-time collaboration, video streaming, proximity service). Cross-linked to DDIA. See
  [architecture/system-design/README.md](architecture/system-design/README.md).
- **The Hard Parts** subject - *Software Architecture: The Hard Parts* (Ford, Richards,
  Sadalage, Dehghani): 17 lessons on distributed trade-off analysis - coupling and the
  architecture quantum, architectural modularity and decomposition, component-based
  decomposition patterns, service and data granularity, reuse patterns, data ownership,
  distributed transactions and eventual consistency, distributed data access, orchestration
  vs choreography, the eight saga patterns, strict vs loose contracts, and analytical data
  (warehouse, lake, mesh). Cross-linked to DDIA and System Design. See
  [architecture/hard-parts/README.md](architecture/hard-parts/README.md).
- **Fundamentals** subject - *Fundamentals of Software Architecture* (Richards & Ford): 22
  lessons consolidating the architecture vocabulary - architectural thinking and the
  architect role, characteristics (discover/measure/govern), modularity and architecture
  quanta, monolithic vs distributed topology and the fallacies of distributed computing,
  the core architecture styles (layered, modular monolith, pipeline, microkernel,
  service-based, event-driven, space-based, SOA, microservices), choosing styles, ADRs,
  risk analysis, communication, and architect leadership. Cross-linked to DDIA, System
  Design, and The Hard Parts. See
  [architecture/fundamentals/README.md](architecture/fundamentals/README.md).
- **Agent operating manual** ([AGENTS.md](AGENTS.md)) and its load-on-demand detail docs:
  [repository-model.md](agent-docs/repository-model.md),
  [learning-workflows.md](agent-docs/learning-workflows.md), and
  [git-policy.md](agent-docs/git-policy.md), plus the Claude Code symlink (`CLAUDE.md`).
- **Templates** for authoring: [lesson-template.md](templates/lesson-template.md) and
  [discussion-template.md](templates/discussion-template.md).
- **Indexes and summaries**: per-subject `README.md` progress tables and `SUMMARY.md`
  recaps, plus the cross-domain root [SUMMARY.md](SUMMARY.md).
- **Repository tooling**: public [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md),
  GitHub issue forms for requesting a new domain/subject/lesson
  ([.github/ISSUE_TEMPLATE/](.github/ISSUE_TEMPLATE/)), GitHub Sponsors funding
  ([.github/FUNDING.yml](.github/FUNDING.yml)), and the
  [CC BY-SA 4.0 license](LICENSE).

[Unreleased]: https://github.com/iarechaga/oh-my-learning/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/iarechaga/oh-my-learning/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/iarechaga/oh-my-learning/releases/tag/v0.1.0
