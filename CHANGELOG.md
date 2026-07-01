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

- **Seniority model** - every lesson now carries a `seniority` band
  (`junior`/`mid`/`senior`/`staff`/`principal`) and every subject declares a seniority
  baseline. The band measures whose job a concept anchors, not reading difficulty, and it
  calibrates how deeply the agent runs a Socratic discussion. New authoritative agent doc
  [agent-docs/seniority-model.md](agent-docs/seniority-model.md) (wired into
  [AGENTS.md](AGENTS.md)) and learner-facing [SENIORITY.md](SENIORITY.md); the lesson
  template, [repository-model.md](agent-docs/repository-model.md), and
  [learning-workflows.md](agent-docs/learning-workflows.md) updated accordingly. Every
  existing subject `README.md` gained a **Seniority** column and a baseline line.

### Changed

- **Every existing subject `README.md`** (the four authored architecture subjects and all
  scaffolded subjects) gained a **Seniority** column and a seniority-baseline line as part
  of introducing the seniority model.


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

[Unreleased]: https://github.com/iarechaga/oh-my-learning/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/iarechaga/oh-my-learning/releases/tag/v0.1.0
