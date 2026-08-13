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

- **`multi-agent-orchestration` subject fully authored (7/7 lessons)** - when
  splitting work across multiple agents actually helps (vs. adding cost and
  coordination overhead for nothing), subagents as a delegation boundary with context
  isolation, orchestration patterns (deterministic workflows vs. autonomous
  delegation), coordination mechanisms, the three durable orchestration architecture
  patterns (graph-based, role-based, deterministic-script), documented multi-agent
  failure modes (coordination overhead, emergent behavior, 41-87% production failure
  rates per a validated 2026 taxonomy), and authorization propagation across
  delegation chains. Named frameworks (LangGraph, CrewAI) stay boxed illustrative
  examples throughout. New
  `agentic-engineering/multi-agent-orchestration/SUMMARY.md`; root
  `README.md`/`SUMMARY.md` and `CATALOG.md` updated (652 lessons, 50 subjects, 9
  domains). Authored on `feat/agentic-engineering-domain`.
- **`model-context-protocol` subject fully authored (7/7 lessons)** - why MCP exists
  (the M x N integration problem, with a worked count), MCP architecture (host/client/
  server), MCP primitives (tools/resources/prompts), building an MCP server well
  (granularity, context cost, recoverable errors), authorization and the 2026
  stateless-protocol-core shift, discovering and trusting third-party servers (tool
  poisoning, registry verification vs. behavioral trust), and MCP as a shared tooling
  layer across multiple agents. This subject is this domain's one explicit exception to
  "no product is the concept": MCP-the-protocol itself is treated as durable (Linux
  Foundation governance, cross-vendor adoption - cited with real 2026 figures), while
  every *other* named product stays a swappable boxed example. New
  `agentic-engineering/model-context-protocol/SUMMARY.md`; root `README.md`/`SUMMARY.md`
  and `CATALOG.md` updated (645 lessons, 49 subjects, 9 domains). Authored on
  `feat/agentic-engineering-domain`.
- **`instruction-and-context-design` subject fully authored (11/11 lessons)** - the
  domain's most differentiated subject: the full set of surfaces an agent reads
  instructions from, structured metadata as cheap signal, the always-loaded-vs-on-demand
  decision, designing trigger descriptions (how an agent decides what to load) and
  their failure modes (over-triggering, under-triggering, ambiguity), writing
  instructions that survive out-of-order loading, what a skill is and authoring one end
  to end, evaluating whether a skill actually works, hooks/commands as deterministic
  alternatives to model-judged triggers, and a (deliberately incomplete) capstone on
  choosing the right primitive. Uses this repository's own `AGENTS.md`/`agent-docs/`
  dispatcher as one worked example among several, never the lesson's subject. New
  `agentic-engineering/instruction-and-context-design/SUMMARY.md`; root
  `README.md`/`SUMMARY.md` and `CATALOG.md` updated (638 lessons, 48 subjects, 9
  domains). Authored on `feat/agentic-engineering-domain`.
- **`tool-use-agentic-loop` subject fully authored (8/8 lessons)** - the second
  authored subject in the `agentic-engineering` domain: function-calling mechanics,
  designing tool schemas, the plan-act-observe agentic loop, parallel vs sequential
  tool calls, the harness-vs-scaffolding distinction, stateless vs stateful tool
  execution, designing for recoverable failure (idempotency, retry budgets), and
  termination-condition design for runaway-loop prevention. Every lesson is tagged
  `durability: durable` and follows the domain's rule that named products appear only
  as dated, swappable examples. New
  `agentic-engineering/tool-use-agentic-loop/SUMMARY.md`; root `README.md`/`SUMMARY.md`
  and `CATALOG.md` updated (627 lessons, 47 subjects, 9 domains). Authored on
  `feat/agentic-engineering-domain`.
- **`prompting-context-engineering` subject fully authored (10/10 lessons)** - the
  first authored subject in the `agentic-engineering` domain: what LLMs actually do
  (tokens, autoregression, statelessness), prompt anatomy, core prompting techniques,
  chain-of-thought and reasoning effort (including the 2025-2026 research on when CoT
  helps vs. is theater and its faithfulness limits), structured output/constrained
  decoding, the limits of prompting, and context engineering as a discipline (the
  budget framing, named failure modes, retrieval/memory, and compaction/handoff for
  long-horizon tasks). Every lesson is tagged `durability: durable` per
  [`agent-docs/fast-moving-domain-policy.md`](agent-docs/fast-moving-domain-policy.md) -
  named products appear only as dated, swappable examples in blockquotes, never as a
  concept's defining identity. New `agentic-engineering/prompting-context-engineering/SUMMARY.md`;
  root `README.md`/`SUMMARY.md` and `CATALOG.md` updated to match (619 lessons, 46
  subjects, 9 domains). Authored on `feat/agentic-engineering-domain`; the other eight
  subjects in the domain remain scaffolded.
- **Website published on GitHub Pages** - the reading site now auto-deploys to
  <https://iarechaga.github.io/oh-my-learning/> via
  `.github/workflows/deploy-pages.yml` on every push to `main` (and on manual
  `workflow_dispatch`); no manual build/publish step is required. `website/build.py`
  gained a `--base-path` option so generated links and static assets work correctly
  under a GitHub Pages project-site subpath (`/oh-my-learning/`) instead of only at
  the domain root; the `website/templates/` were updated to use it. Also fixed: 44
  lessons' in-prose relative links to sibling/cross-subject lessons
  (`[01-fundamentals.md](01-fundamentals.md)`-style) resolved to `.md` files that don't
  exist in the generated site (only `.html` pages do) - `website/build.py` now rewrites
  those to the correct rendered page during the build instead of leaving them as dead
  links; verified zero broken internal links across all 663 generated pages. Documented
  in [`agent-docs/website.md`](agent-docs/website.md). `README.md` links to the
  published site and the repository's GitHub "homepage" URL now points to it.
- **`agentic-engineering` domain scaffolded (9 subjects, 71 concepts, 0 lessons
  authored yet)** - working effectively with LLMs at an advanced level and building
  the agent capabilities that exist today: `prompting-context-engineering` (10),
  `tool-use-agentic-loop` (8), `instruction-and-context-design` (11),
  `model-context-protocol` (7), `multi-agent-orchestration` (7),
  `agentic-software-engineering` (6), `agent-evaluation` (7),
  `agent-security-and-operations` (8), and `landscape-snapshot` (7). This domain has
  no canonical book to anchor to - the field moves faster than the rest of the
  repository's subject matter - so it introduces a new, domain-scoped
  durable-vs-perishable content split: eight subjects teach durable capability, and
  one (`landscape-snapshot`) is an explicitly dated survey of today's concrete
  products, reviewed on a fixed quarterly cadence rather than opportunistically. New
  `durability`/`next_review` front-matter fields (used only in this domain) and the
  full policy - what's durable vs perishable, the review cadence, and what it implies
  for versioning - are documented in new
  [`agent-docs/fast-moving-domain-policy.md`](agent-docs/fast-moving-domain-policy.md);
  `AGENTS.md`, `agent-docs/repository-model.md`, and `agent-docs/release-policy.md`
  wired to reference it. Scaffolded on `feat/agentic-engineering-domain`; lesson
  bodies not yet authored.

## [1.0.0] - 2026-08-10

First stable release: the full library is authored (609 lessons, 45 subjects, 8
domains), concept IDs and repository structure are frozen, and the agent's operating
system (onboarding, discussions, progress tracking, public catalog) is complete and
self-consistent. No renames, renumbering, or layout changes shipped in this release -
see [agent-docs/release-policy.md](agent-docs/release-policy.md) for what a `1.0.0`
commits to.

### Added

- **Architecture domain completed (10/10 subjects, 152 lessons)** - authored the four
  subjects that were index-only scaffolds at `0.2.0`: System Design Interview (15),
  Distributed Systems (12), Evolutionary Architectures (9), Building Microservices (17).
  See [architecture/README.md](architecture/README.md).
- **Computer Science Fundamentals domain authored (5/5 subjects, 74 lessons)** -
  Introduction to Algorithms/CLRS (20), Algorithms - Sedgewick & Wayne (14), Algorithm
  Design (12), Java Concurrency in Practice (15), The Art of Multiprocessor Programming
  (13). See [cs-fundamentals/README.md](cs-fundamentals/README.md).
- **Data Engineering & Databases domain authored (3/3 subjects, 35 lessons)** - Database
  Internals (16), SQL Performance Explained (10), Seven Databases in Seven Weeks (9).
  See [data-engineering/README.md](data-engineering/README.md).
- **DevOps, Cloud & Reliability domain authored (4/4 subjects, 54 lessons)** - The
  Phoenix Project (10), The DevOps Handbook (16), Site Reliability Engineering (16),
  Seeking SRE (12). See [devops-reliability/README.md](devops-reliability/README.md).
- **Domain Modeling domain authored (4/4 subjects, 54 lessons)** - Domain-Driven Design
  / Evans (16), Implementing Domain-Driven Design (15), Learning Domain-Driven Design
  (14), Domain-Driven Design Distilled (9). See
  [domain-modeling/README.md](domain-modeling/README.md).
- **Software Engineering domain authored (9/9 subjects, 114 lessons)** - The Pragmatic
  Programmer (15), Code Complete (14), Clean Architecture (13), Clean Code (12),
  Refactoring (12), A Philosophy of Software Design (11), Working Effectively with
  Legacy Code (12), Patterns of Enterprise Application Architecture (14), Design
  Patterns (11). See
  [software-engineering/README.md](software-engineering/README.md).
- **Software Quality domain authored (3/3 subjects, 37 lessons)** - Growing
  Object-Oriented Software, Guided by Tests (12), Unit Testing (13), xUnit Test Patterns
  (12). See [software-quality/README.md](software-quality/README.md).
- **Technical Leadership domain authored (7/7 subjects, 89 lessons)** - Staff Engineer
  (12), The Staff Engineer's Path (14), An Elegant Puzzle (13), The Manager's Path (13),
  Accelerate (12), Thinking, Fast and Slow (14), How to Measure Anything (11). See
  [technical-leadership/README.md](technical-leadership/README.md).
- **Generated `CATALOG.md`** - a full public catalog of all 609 lessons
  (domain -> subject -> concept, with seniority and a direct link to each lesson),
  produced programmatically by the new `scripts/generate_catalog.py` (stdlib only) from
  lesson front matter, so it can never drift by hand. `--check` mode verifies it is
  current. `AGENTS.md`, `agent-docs/repository-model.md`, and
  `agent-docs/learning-workflows.md` now require regenerating it - together with the
  root README's domain table, in the same commit - whenever a lesson, subject, or
  domain is added, renumbered, or removed; `CONTRIBUTING.md`'s workflows and pre-submit
  checklist updated to match.
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
- **Root `README.md` restructured as a public landing page** - user-facing "how to get
  started in 2 minutes" now leads (fork/branch, agent onboarding, first discussion, and
  the `PROGRESS.md` track/Next-up/Focus-areas loop), followed by a condensed 8-row
  domain table and the new `CATALOG.md` link. Internals (full repository model,
  contribution steps, the agent's contract) were trimmed out of the root README in favor
  of linking to `CONTRIBUTING.md` and `AGENTS.md`, which already carried that detail, to
  keep the landing page readable in one pass.

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
