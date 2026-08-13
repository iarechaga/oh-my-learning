# Oh My Learning - Lessons + Socratic Discussion

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/iarechaga)

If this learning library is useful to you, consider [sponsoring its
upkeep](https://github.com/sponsors/iarechaga). Thank you!

An AI coding agent writes a deep, self-contained **lesson** for each concept; you read
it on your own; then you ask the agent to **discuss** it with you. The discussion is
Socratic - questions instead of lectures - and finds the gaps in your understanding
before you find them in an interview or a production incident.

**638 lessons, 48 subjects, 9 domains**, from architecture and distributed systems to
DDD, testing, DevOps/SRE, technical leadership, and agentic engineering. This is not a
code project - there is nothing to build or run. The "program" is the loop of *read,
then get grilled on it until you actually understand it.*

> Driven by an AI agent. Lesson authoring, discussions, and progress tracking are all
> performed by an AI coding agent (such as [OpenCode](https://opencode.ai) or Claude
> Code) that reads [`AGENTS.md`](AGENTS.md). Without an agent you can still read the
> lessons as standalone notes, but the interactive part needs one.

---

## Getting started (2 minutes)

1. **Fork or clone the repo**, and open it with a coding agent that reads `AGENTS.md`
   (OpenCode, Claude Code, or similar).
2. **Tell it you want to start learning.** The agent puts you on your own branch, not
   `main` (`main` is the shared library; your learning is personal - your progress, your
   notes). You don't need to run any git commands: on your first session the agent
   creates and switches you to a `learn/<your-name>` branch itself.
3. **The agent gets to know you first.** It asks your name, your seniority level (it
   helps estimate it if you're not sure), and what you want to learn and why. With that,
   it proposes an **ordered study track**: a concrete list of concepts, in the right
   order, with a reason for each - not a random lesson.
4. **Read a lesson**, then ask the agent to discuss it with you: *"discuss
   `system-design/03`"*. One question at a time, hints instead of answers, at least one
   applied scenario, and a mastery verdict (`solid` / `partial` / `shaky` / `not-yet`) at
   the end.
5. **The agent tracks your progress for you**, in `PROGRESS.md` at the root of your
   branch: what's next (*Next up*), where you're shaky (*Focus areas*), and stats per
   domain and seniority. Ask it anytime *"what's next"*, *"how am I doing"*, or *"I want
   more focus on databases"* - it answers instantly, without re-reading the whole repo,
   and adjusts the track if you ask it to.

You don't need the source books: each lesson teaches its concept from scratch, with
worked examples, trade-offs, and self-check questions. The cited book is only an
optional "go deeper".

---

## Domains at a glance

| Domain | What it's about | Subjects | Lessons |
| --- | --- | --- | --- |
| **[Architecture](architecture/README.md)** | Designing scalable, maintainable, distributed systems - from theory (DDIA) to practice (System Design, microservices, evolutionary architectures). | 10 | 152 |
| **[Software Engineering](software-engineering/README.md)** | Writing maintainable, evolvable code: pragmatism, Clean Code/Architecture, refactoring, patterns. | 9 | 114 |
| **[Technical Leadership](technical-leadership/README.md)** | Growing beyond coding: staff-plus IC leadership, management, delivery science, decision-making. | 7 | 89 |
| **[CS Fundamentals](cs-fundamentals/README.md)** | Algorithms, data structures, and concurrency - the formal foundation. | 5 | 74 |
| **[DevOps, Cloud & Reliability](devops-reliability/README.md)** | Operating software in production: flow, feedback, and SRE (SLOs, error budgets, incidents). | 4 | 54 |
| **[Domain Modeling](domain-modeling/README.md)** | Modeling business complexity with Domain-Driven Design. | 4 | 54 |
| **[Data Engineering & Databases](data-engineering/README.md)** | Choosing, designing, and understanding storage systems. | 3 | 35 |
| **[Software Quality](software-quality/README.md)** | Testing and reliability through better test design. | 3 | 37 |
| **[Agentic Engineering](agentic-engineering/README.md)** | Working effectively with LLMs and building/operating today's agent capabilities: prompting, context and instruction design, tool use, MCP, orchestration, evaluation, and security/cost/operations. | 9 | 71 *(29 authored, rest scaffold)* |

**-> [See all 638 lessons: CATALOG.md](CATALOG.md)** - the full catalog,
domain -> subject -> lesson, with seniority and a direct link to each one. It's
generated programmatically from lesson front matter (see
[scripts/generate_catalog.py](scripts/generate_catalog.py)), so it never drifts out of
sync by hand.

---

## Other ways to read

Besides reading the Markdown directly on GitHub or in your editor, there's a static
website with navigation, seniority badges, and reading status.

**-> [Browse it online](https://iarechaga.github.io/oh-my-learning/)** - published via
GitHub Pages and rebuilt automatically on every push to `main`.

Or run it locally:

```bash
pip3 install -r website/requirements.txt
python3 website/build.py
python3 website/serve.py
```

Open `http://localhost:8000`. It rebuilds from the same lesson files; see
[`agent-docs/website.md`](agent-docs/website.md) for details.

---

## For contributors, or to understand the internals

The repository model in short: **subjects** (one book each) are grouped by **domain**;
each subject has one lesson per concept, identified by a stable ID `<subject>/<NN>`
(e.g. `ddia/07`). Each lesson carries `status` (`drafted` -> `discussed`), `mastery`
(`solid`/`partial`/`shaky`/`not-yet`, personal and per-branch), and `seniority`
(`junior`/`mid`/`senior`/`staff`/`principal`, whose job the concept anchors - see
[SENIORITY.md](SENIORITY.md)).

- **The full repository model**, with the folder tree and ID rules, is in
  [`CONTRIBUTING.md`](CONTRIBUTING.md#repository-model-in-one-screen).
- **How to contribute** (a new lesson, subject, or domain; or request one via Issues) is
  in [`CONTRIBUTING.md`](CONTRIBUTING.md).
- **The agent's contract** - the lesson template, the Socratic discussion protocol, the
  progress-tracking system (`PROGRESS.md`), and all the verification rules - lives in
  [`AGENTS.md`](AGENTS.md) and its detail docs in `agent-docs/`.

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

Cited book titles and author names are referenced for attribution only and remain the
property of their respective rights holders; they are not covered by this license.
