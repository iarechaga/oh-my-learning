# Oh My Learning - Lessons + Socratic Discussion

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/iarechaga)

If this learning library is useful to you, consider [sponsoring its
upkeep](https://github.com/sponsors/iarechaga). Thank you!

A learning repository with an unusual workflow. An AI coding agent writes a deep,
self-contained **lesson** for each concept; you read it on your own; then you ask the
agent to **discuss** that concept with you. The discussion is Socratic - the agent
asks questions instead of lecturing, finds the gaps in your understanding, guides you
to the right conclusions, and records where you are solid versus shaky.

This is not a code project. There is nothing to build or run. The "program" is the
loop of *read a lesson, then get grilled on it until you actually understand it.*

> Driven by an AI agent. The discussions, lesson authoring, and progress tracking are
> all performed by an AI coding agent (such as [OpenCode](https://opencode.ai) or
> Claude Code) that reads [`AGENTS.md`](AGENTS.md). Without an agent you can still read
> the lessons as standalone notes, but the interactive part needs one.

---

## The loop

1. The agent authors one lesson per concept - a complete deep reading, written so you
   do **not** need the source book.
2. You read the lesson.
3. You tell the agent: *"discuss `ddia/07`"* (see Concept IDs below).
4. The agent runs a Socratic session: one question at a time, hints instead of
   answers, at least one applied scenario, scaling difficulty to how you do.
5. The agent writes a **discussion record** (what you got, your weak spots, a mastery
   verdict) and updates the progress tables and summaries.

---

## Layout

Subjects (one per book) are grouped by **domain** - a broad theme such as
`architecture`. New domains (e.g. `clean-code`, `engineering-practices`) get added
beside it as the library grows.

```
AGENTS.md                   the operating manual the agent follows (authoritative)
templates/                  lesson + discussion templates
SUMMARY.md                  cross-domain summary + aggregated focus areas
<domain>/                   e.g. architecture/
  README.md                 domain index: the subjects in this domain
  <subject>/                e.g. ddia/, system-design/
    README.md               concept index + progress table for that subject
    lessons/<NN>-<slug>.md   one lesson per concept
    discussions/            one folder per concept, holding session records
    SUMMARY.md              comprehensive recap of the subject
```

**Concept IDs** are `<subject>/<NN>`, e.g. `ddia/07` or `system-design/03` - they are
subject-scoped, so the domain folder does not appear in the ID. Refer to a concept by
its full ID, by its number when the subject is obvious, or by name.

**Status** is `drafted` or `discussed`. **Mastery** (from your latest discussion) is
`solid` / `partial` / `shaky` / `not-yet`. **Seniority** (per lesson, with a subject
baseline) is `junior` / `mid` / `senior` / `staff` / `principal` - it measures whose job
a concept anchors and calibrates how deeply a discussion probes; see
[SENIORITY.md](SENIORITY.md).

---

## Subjects

**[architecture/](architecture/README.md)** - designing scalable, maintainable,
distributed systems. All ten subjects are fully authored:

| Subject | What it is | Lessons | Start here |
| --- | --- | --- | --- |
| **DDIA** | *Designing Data-Intensive Applications* - the theory of data systems (replication, partitioning, transactions, consistency, batch/stream). | 16 | [architecture/ddia/README.md](architecture/ddia/README.md) |
| **System Design** | *System Design Guide for Software Professionals* - applying that theory to real systems (load balancing, caching, sharding, queues, APIs, plus end-to-end case studies). Cross-linked to DDIA. | 20 | [architecture/system-design/README.md](architecture/system-design/README.md) |
| **The Hard Parts** | *Software Architecture: The Hard Parts* - advanced distributed trade-off analysis around decomposition, service/data granularity, ownership, sagas, contracts, and analytical data. | 17 | [architecture/hard-parts/README.md](architecture/hard-parts/README.md) |
| **Fundamentals** | *Fundamentals of Software Architecture* - architectural vocabulary, characteristics, modularity, styles, decisions, risk, communication, and architect leadership. | 22 | [architecture/fundamentals/README.md](architecture/fundamentals/README.md) |
| **Building Microservices** | *Building Microservices*, 2nd ed. (Newman) - service boundaries, communication, per-service data, delivery, testing, observability, resilience, teams. | 17 | [architecture/building-microservices/README.md](architecture/building-microservices/README.md) |
| **Microservices Patterns** | *Microservices Patterns* (Richardson) - decomposition, IPC, sagas, event sourcing, CQRS, API gateway, testing, production concerns. | 12 | [architecture/microservices-patterns/README.md](architecture/microservices-patterns/README.md) |
| **Designing Distributed Systems** | *Designing Distributed Systems* (Burns) - reusable container/orchestration patterns (sidecar, ambassador, sharding, scatter/gather) and batch patterns. | 12 | [architecture/designing-distributed-systems/README.md](architecture/designing-distributed-systems/README.md) |
| **Distributed Systems** | *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum) - the formal principles: coordination, consistency/replication, fault tolerance, consensus, security. | 12 | [architecture/distributed-systems/README.md](architecture/distributed-systems/README.md) |
| **Evolutionary Architectures** | *Building Evolutionary Architectures*, 2nd ed. - fitness functions, incremental change, appropriate coupling, governance. | 9 | [architecture/evolutionary-architectures/README.md](architecture/evolutionary-architectures/README.md) |
| **System Design Interview** | *System Design Interview*, Vol. 1 (Xu) - an interview framework, estimation, and worked end-to-end designs. | 15 | [architecture/system-design-interview/README.md](architecture/system-design-interview/README.md) |

**[software-engineering/](software-engineering/README.md)** - writing maintainable,
evolvable software. All nine subjects are fully authored:

| Subject | What it is | Lessons | Start here |
| --- | --- | --- | --- |
| **The Pragmatic Programmer** | *The Pragmatic Programmer* (Hunt & Thomas) - the pragmatic philosophy and everyday habits: DRY, orthogonality, tracer bullets, decoupling. | 15 | [software-engineering/pragmatic-programmer/README.md](software-engineering/pragmatic-programmer/README.md) |
| **Code Complete** | *Code Complete*, 2nd ed. (McConnell) - construction craftsmanship: defensive programming, variables, routines, class design. | 14 | [software-engineering/code-complete/README.md](software-engineering/code-complete/README.md) |
| **Clean Architecture** | *Clean Architecture* (Martin) - SOLID, component principles, and the dependency rule. | 13 | [software-engineering/clean-architecture/README.md](software-engineering/clean-architecture/README.md) |
| **Clean Code** | *Clean Code* (Martin) - readable code in the small: naming, functions, comments, smells. | 12 | [software-engineering/clean-code/README.md](software-engineering/clean-code/README.md) |
| **Refactoring** | *Refactoring*, 2nd ed. (Fowler) - code smells and a catalog of named refactorings, backed by tests. | 12 | [software-engineering/refactoring/README.md](software-engineering/refactoring/README.md) |
| **A Philosophy of Software Design** | *A Philosophy of Software Design* (Ousterhout) - complexity, deep modules, information hiding. | 11 | [software-engineering/philosophy-of-software-design/README.md](software-engineering/philosophy-of-software-design/README.md) |
| **Working Effectively with Legacy Code** | *Working Effectively with Legacy Code* (Feathers) - seams, dependency-breaking, characterization tests. | 12 | [software-engineering/legacy-code/README.md](software-engineering/legacy-code/README.md) |
| **Enterprise Application Patterns** | *Patterns of Enterprise Application Architecture* (Fowler) - domain logic, O/R mapping, concurrency, sessions, distribution. | 14 | [software-engineering/enterprise-patterns/README.md](software-engineering/enterprise-patterns/README.md) |
| **Design Patterns** | *Design Patterns* (Gang of Four) - the classic 23 OO patterns: creational, structural, behavioral. | 11 | [software-engineering/design-patterns/README.md](software-engineering/design-patterns/README.md) |

More domains (e.g. domain modeling, data engineering, software quality, DevOps/
reliability) will sit beside these as the library grows. *(scaffold)* subjects have
their concept list and index in place; the deep lesson bodies are authored next.

**[domain-modeling/](domain-modeling/README.md)** - modeling business complexity with
Domain-Driven Design. All four subjects are fully authored:

| Subject | What it is | Lessons | Start here |
| --- | --- | --- | --- |
| **DDD (Evans)** | *Domain-Driven Design* (Evans, the "blue book") - ubiquitous language, aggregates, bounded contexts, strategic design. | 16 | [domain-modeling/ddd-evans/README.md](domain-modeling/ddd-evans/README.md) |
| **Implementing DDD** | *Implementing Domain-Driven Design* (Vernon, the "red book") - aggregates, domain events, context integration in depth. | 15 | [domain-modeling/implementing-ddd/README.md](domain-modeling/implementing-ddd/README.md) |
| **Learning DDD** | *Learning Domain-Driven Design* (Khononov) - a modern, strategic-design-first path. | 14 | [domain-modeling/learning-ddd/README.md](domain-modeling/learning-ddd/README.md) |
| **DDD Distilled** | *Domain-Driven Design Distilled* (Vernon) - a concise primer of the core ideas. | 9 | [domain-modeling/ddd-distilled/README.md](domain-modeling/ddd-distilled/README.md) |

**[data-engineering/](data-engineering/README.md)** - choosing, designing, and
understanding storage systems (DDIA is the theory, cross-referenced from `architecture/`).
All scaffolded:

| Subject | What it is | Lessons | Start here |
| --- | --- | --- | --- |
| **Database Internals** | *Database Internals* (Petrov) - storage engines (B-Trees, LSM) through replication, partitioning, and consensus. | 16 *(scaffold)* | [data-engineering/database-internals/README.md](data-engineering/database-internals/README.md) |
| **SQL Performance Explained** | *SQL Performance Explained* (Winand) - indexing and query-shape reasoning for predictable SQL performance. | 10 | [data-engineering/sql-performance-explained/README.md](data-engineering/sql-performance-explained/README.md) |
| **Seven Databases in Seven Weeks** | *Seven Databases in Seven Weeks* (Perkins et al.) - a comparative tour of relational, document, wide-column, graph, and key-value stores. | 9 | [data-engineering/seven-databases/README.md](data-engineering/seven-databases/README.md) |

**[cs-fundamentals/](cs-fundamentals/README.md)** - core CS: algorithms, data structures,
and concurrency. All five subjects are fully authored:

| Subject | What it is | Lessons | Start here |
| --- | --- | --- | --- |
| **Introduction to Algorithms (CLRS)** | *Introduction to Algorithms* (CLRS) - the comprehensive algorithms reference. | 20 | [cs-fundamentals/clrs/README.md](cs-fundamentals/clrs/README.md) |
| **Algorithms (Sedgewick & Wayne)** | *Algorithms* (Sedgewick & Wayne) - practical, implementation-focused algorithms and data structures. | 14 | [cs-fundamentals/algorithms-sedgewick/README.md](cs-fundamentals/algorithms-sedgewick/README.md) |
| **Algorithm Design** | *Algorithm Design* (Kleinberg & Tardos) - design techniques: greedy, D&C, DP, network flow, NP-completeness. | 12 | [cs-fundamentals/algorithm-design/README.md](cs-fundamentals/algorithm-design/README.md) |
| **Java Concurrency in Practice** | *Java Concurrency in Practice* (Goetz et al.) - JVM thread safety, the memory model, concurrent components. | 15 | [cs-fundamentals/java-concurrency/README.md](cs-fundamentals/java-concurrency/README.md) |
| **The Art of Multiprocessor Programming** | *The Art of Multiprocessor Programming* (Herlihy & Shavit) - concurrent algorithms, linearizability, lock-free structures. | 13 | [cs-fundamentals/multiprocessor-programming/README.md](cs-fundamentals/multiprocessor-programming/README.md) |

**[software-quality/](software-quality/README.md)** - testing and reliability through
better test design. All scaffolded:

| Subject | What it is | Lessons | Start here |
| --- | --- | --- | --- |
| **GOOS** | *Growing Object-Oriented Software, Guided by Tests* (Freeman & Pryce) - outside-in TDD, walking skeleton, mock objects. | 12 | [software-quality/goos/README.md](software-quality/goos/README.md) |
| **Unit Testing** | *Unit Testing* (Khorikov) - valuable vs brittle tests, the four pillars, doubles, integration strategy. | 13 | [software-quality/unit-testing/README.md](software-quality/unit-testing/README.md) |
| **xUnit Test Patterns** | *xUnit Test Patterns* (Meszaros) - the catalog of test smells, patterns, and test-code refactorings. | 12 | [software-quality/xunit-test-patterns/README.md](software-quality/xunit-test-patterns/README.md) |

**[devops-reliability/](devops-reliability/README.md)** - operating software in
production: flow, feedback, and reliability engineering. All scaffolded:

| Subject | What it is | Lessons | Start here |
| --- | --- | --- | --- |
| **The Phoenix Project** | *The Phoenix Project* (Kim et al.) - a novel teaching the Three Ways, flow, WIP, and constraints. | 10 *(scaffold)* | [devops-reliability/phoenix-project/README.md](devops-reliability/phoenix-project/README.md) |
| **The DevOps Handbook** | *The DevOps Handbook* (Kim et al.) - the practical implementation of flow, feedback, and continual learning. | 16 *(scaffold)* | [devops-reliability/devops-handbook/README.md](devops-reliability/devops-handbook/README.md) |
| **Site Reliability Engineering** | *Site Reliability Engineering* (Beyer et al.) - SLIs/SLOs, error budgets, toil, on-call, incidents. | 16 *(scaffold)* | [devops-reliability/sre/README.md](devops-reliability/sre/README.md) |
| **Seeking SRE** | *Seeking SRE* (Blank-Edelman, ed.) - applying and evolving SRE: culture, human factors, strategy. | 12 *(scaffold)* | [devops-reliability/seeking-sre/README.md](devops-reliability/seeking-sre/README.md) |

**[technical-leadership/](technical-leadership/README.md)** - growing beyond coding:
staff-plus IC leadership, management, delivery science, and decision-making. All seven
subjects are fully authored:

| Subject | What it is | Lessons | Start here |
| --- | --- | --- | --- |
| **Staff Engineer** | *Staff Engineer* (Larson) - staff-plus roles, archetypes, and operating with broad influence. | 12 | [technical-leadership/staff-engineer/README.md](technical-leadership/staff-engineer/README.md) |
| **The Staff Engineer's Path** | *The Staff Engineer's Path* (Reilly) - big-picture thinking, execution, leveling up others. | 14 | [technical-leadership/staff-engineers-path/README.md](technical-leadership/staff-engineers-path/README.md) |
| **An Elegant Puzzle** | *An Elegant Puzzle* (Larson) - engineering management as systems: org design, team topology. | 13 | [technical-leadership/elegant-puzzle/README.md](technical-leadership/elegant-puzzle/README.md) |
| **The Manager's Path** | *The Manager's Path* (Fournier) - the management ladder from tech lead to CTO. | 13 | [technical-leadership/managers-path/README.md](technical-leadership/managers-path/README.md) |
| **Accelerate** | *Accelerate* (Forsgren, Humble, Kim) - the DORA metrics and what predicts delivery performance. | 12 | [technical-leadership/accelerate/README.md](technical-leadership/accelerate/README.md) |
| **Thinking, Fast and Slow** | *Thinking, Fast and Slow* (Kahneman) - biases, heuristics, and decision-making under uncertainty. | 14 | [technical-leadership/thinking-fast-and-slow/README.md](technical-leadership/thinking-fast-and-slow/README.md) |
| **How to Measure Anything** | *How to Measure Anything* (Hubbard) - calibrated estimation and the value of information. | 11 | [technical-leadership/how-to-measure-anything/README.md](technical-leadership/how-to-measure-anything/README.md) |

---

## How to use it

1. **Open the repo with an AI coding agent** that reads `AGENTS.md`.
2. **The agent puts you on your own branch, not `main`.** `main` is the shared, public
   library of lessons; your learning is personal - discussion records, mastery updates,
   and summary edits are *your* progress, not everyone's. You don't have to run any git
   commands: on your first session the agent creates and switches you to a `learn/<name>`
   branch itself and keeps your personal notes off `main`. (Prefer to work in a fork?
   Fork the repo and open it there instead.) This is the deliberate split: the canonical
   lessons live on `main`; the *execution* of the lessons (your discussions and progress)
   lives on your branch.
3. **On your first session, the agent gets to know you.** Before proposing what to
   study, it asks your name and how you'd like to be addressed, your seniority level
   (offering to briefly assess it if you're unsure), and what you want to learn and why -
   then proposes a learning path. It writes these notes to a personal `LEARNER.md`
   (gitignored, never on `main`), reads it at the start of every session so you never
   repeat yourself, and updates it whenever you ask to change your level or how you're
   treated.
4. **Read a lesson**, then ask the agent to discuss it: *"discuss `system-design/03`"*.
5. The agent records the session under `<domain>/<subject>/discussions/` and updates
   your progress tables on your branch. Pull new lessons from `main` whenever you like.

If you are not sure what to read next, ask the agent to open the lesson catalog, for
example: *"show architecture lessons"* or *"what should I study next?"* The agent will
summarize available topics, which ones are started or not started, progress per subject,
and a recommended next concept. After a discussion, it will also suggest related topics
from the same or another book that deepen what you just studied.

You do not need the source books. Each lesson teaches its concept from first
principles, with worked examples, trade-offs, and self-check questions. The cited book
is only an optional "go deeper".

---

## Local website

If you prefer browsing in a browser instead of reading raw Markdown, there is a
self-contained static site generator under `website/`. It discovers lessons from the
same `<domain>/<subject>/lessons/<NN>-<slug>.md` files used by the agent and renders
them as HTML pages with navigation, seniority badges, and completion status.

Install dependencies once:

```bash
pip3 install -r website/requirements.txt
```

Build and serve:

```bash
python3 website/build.py
python3 website/serve.py
```

Then open `http://localhost:8000`. New lessons are picked up automatically when you
rebuild; the agent is responsible for rebuilding after it authors a lesson or records a
discussion. See [`agent-docs/website.md`](agent-docs/website.md) for the agent
maintenance rules.

---

## How to contribute

Contributions are new domains, new subjects, new or deeper lessons, and corrections.
The step-by-step guide is in [`CONTRIBUTING.md`](CONTRIBUTING.md); the agent's
authoritative rules are in [`AGENTS.md`](AGENTS.md). Don't want to author it yourself?
Open a structured request from **Issues -> New issue** (new domain / new subject / new
lesson). The essentials:

- **One concept per lesson.** Copy [`templates/lesson-template.md`](templates/lesson-template.md)
  and fill **every** section with real content - no placeholders.
- **Lessons are deep, self-sufficient readings.** Assume the reader does not have the
  book: teach from first principles, with multiple concrete worked examples, edge
  cases, and small ASCII diagrams or tables where they help.
- **Front matter is required and stable.** Fill `id`, `subject`, `title`, `slug`,
  `status`, `mastery`, `source`, `prerequisites`, `created`, `updated`. Never change an
  `id` once assigned.
- **Order by dependency** and cross-link prerequisites, including across subjects
  (e.g. a System Design lesson listing `ddia/07`).
- **Keep the indexes in sync.** Update the subject `README.md` table and regenerate the
  subject `SUMMARY.md` and the root `SUMMARY.md` when you add or restructure lessons.
- **Style:** clear, learner-focused prose, ASCII by default, concrete over abstract.
- **Adding a whole domain, subject, or single lesson?** See the matching section in
  [`CONTRIBUTING.md`](CONTRIBUTING.md) (it maps to `AGENTS.md` Workflows A and B).
- **Note your change in [`CHANGELOG.md`](CHANGELOG.md).** Add a bullet under `[Unreleased]`
  for any content or agent-rule change; the rules live in
  [`agent-docs/release-policy.md`](agent-docs/release-policy.md). Personal progress is
  never listed.

### Pull requests

- Open PRs against `main` for **lesson and subject content** only.
- Do **not** put personal learning artifacts in `main` - your `discussions/` records,
  mastery/status edits, and progress-table changes belong on personal learning
  branches or forks, never in a content PR.
- Generated/agent artifacts are gitignored (`.omo/`, `.code-review-graph/`); don't
  commit them.

---

## The agent's contract

The agent's behavior - the lesson template, the Socratic discussion protocol, the
verification steps, and the rule that summaries must never drift - is defined in
[`AGENTS.md`](AGENTS.md). Read it if you want to understand exactly how lessons are
written and how discussions are run and recorded.

---

## License & attribution

The lessons in this repository are **original explanations written from first
principles**. Each lesson cites the source book it draws its concepts from, but the
prose, structure, worked examples, and diagrams are the author's own - the books are a
source and an optional "go deeper", never reproduced here.

This work is licensed under the **Creative Commons Attribution-ShareAlike 4.0
International License** ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/));
the full text is in [`LICENSE`](LICENSE). In short: you may share and adapt the material,
even commercially, as long as you **give appropriate credit** and **license your
derivatives under the same terms**.

Cited book titles and author names (Kleppmann; Sinha & Chopra; Ford, Richards, Sadalage
& Dehghani; Richards & Ford) are referenced for attribution only and remain the property
of their respective rights holders; they are not covered by this license.
