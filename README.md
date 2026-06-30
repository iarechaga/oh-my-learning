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
`solid` / `partial` / `shaky` / `not-yet`.

---

## Subjects

**[architecture/](architecture/README.md)** - the current domain:

| Subject | What it is | Lessons | Start here |
| --- | --- | --- | --- |
| **DDIA** | *Designing Data-Intensive Applications* - the theory of data systems (replication, partitioning, transactions, consistency, batch/stream). | 16 | [architecture/ddia/README.md](architecture/ddia/README.md) |
| **System Design** | *System Design Guide for Software Professionals* - applying that theory to real systems (load balancing, caching, sharding, queues, APIs, plus end-to-end case studies). Cross-linked to DDIA. | 20 | [architecture/system-design/README.md](architecture/system-design/README.md) |
| **The Hard Parts** | *Software Architecture: The Hard Parts* - advanced distributed trade-off analysis around decomposition, service/data granularity, ownership, sagas, contracts, and analytical data. | 17 | [architecture/hard-parts/README.md](architecture/hard-parts/README.md) |
| **Fundamentals** | *Fundamentals of Software Architecture* - architectural vocabulary, characteristics, modularity, styles, decisions, risk, communication, and architect leadership. | 22 | [architecture/fundamentals/README.md](architecture/fundamentals/README.md) |

Future domains (e.g. `clean-code`, `engineering-practices`) will sit beside
`architecture/` as the library grows.

---

## How to use it

1. **Open the repo with an AI coding agent** that reads `AGENTS.md`.
2. **Work on your own branch, not `main`.** `main` is the shared, public library of
   lessons. Your learning is personal - discussion records, mastery updates, and
   summary edits are *your* progress, not everyone's. Keep `main` clean by doing your
   sessions on a branch or a fork:
   ```bash
   git checkout -b learn/your-name   # or fork the repo
   ```
   This is the deliberate split: the canonical lessons live on `main`; the *execution*
   of the lessons (your discussions and progress) lives on your branch.
3. **Read a lesson**, then ask the agent to discuss it: *"discuss `system-design/03`"*.
4. The agent records the session under `<domain>/<subject>/discussions/` and updates
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
