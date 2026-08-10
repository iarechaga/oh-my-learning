# Contributing to Oh My Learning

This repository is a library of deep, self-contained **lessons** plus a Socratic
**discussion** loop run by an AI coding agent. Contributions extend that library: a new
**domain**, a new **subject** (one book), a new or deeper **lesson**, or corrections.

The single source of truth for *how the agent works* is [`AGENTS.md`](AGENTS.md) and its
detail docs under [`agent-docs/`](agent-docs/). This guide is the human-facing summary of
**how to add content** and **how it gets merged**. When the two ever disagree, `AGENTS.md`
wins - fix this file to match it.

> Most contributions are made *through the agent*: you open the repo with an AI coding
> agent (OpenCode or Claude Code) that reads `AGENTS.md`, or you file an issue (see
> [Requesting content](#requesting-content-issues)) and let the agent do the authoring.
> You can also hand-write content yourself as long as it follows the rules below.

---

## Table of contents

- [The two kinds of content (read this first)](#the-two-kinds-of-content-read-this-first)
- [Repository model in one screen](#repository-model-in-one-screen)
- [Requesting content (issues)](#requesting-content-issues)
- [Adding a new domain](#adding-a-new-domain)
- [Adding a new subject (a book)](#adding-a-new-subject-a-book)
- [Adding a single lesson](#adding-a-single-lesson)
- [Lesson quality bar](#lesson-quality-bar)
- [Keeping indexes and summaries in sync](#keeping-indexes-and-summaries-in-sync)
- [Branches, commits, and pull requests](#branches-commits-and-pull-requests)
- [Style rules](#style-rules)
- [Pre-submit checklist](#pre-submit-checklist)

---

## The two kinds of content (read this first)

This repo deliberately separates two things, and they go to **different places**:

| Kind | What it is | Where it lives | Goes to `main`? |
| --- | --- | --- | --- |
| **Library content** | Lessons, subjects, domains, indexes, summaries | The shared, canonical library | **Yes** - via PR (contributors) or directly (maintainer) |
| **Personal learning** | Discussion records, `status`/`mastery` edits, progress-table changes | *Your* execution of the lessons | **No** - personal branch or fork only |

A content contribution **must not** include personal learning artifacts. Do not commit
`discussions/` records or flip a lesson's `status`/`mastery` in a content PR - those are
the learner's personal progress, captured during a real discussion, and they never belong
on `main`. See [git-policy.md](agent-docs/git-policy.md).

---

## Repository model in one screen

Subjects (one per book) are grouped by **domain** (a broad theme such as `architecture`).
Each subject holds one lesson per concept. Slugs are `lowercase-kebab-case`.

```
<domain-slug>/                          e.g. architecture/
  README.md                             domain index: the subjects in this domain
  <subject-slug>/                       e.g. ddia/, system-design/
    README.md                           subject overview + concept index/progress table
    lessons/
      <NN>-<concept-slug>.md            e.g. 01-load-balancing.md  (NN is zero-padded)
    discussions/
      <NN>-<concept-slug>/              one folder per concept (personal; not in content PRs)
        <YYYY-MM-DD>-<SS>.md            one record per session
    SUMMARY.md                          comprehensive recap of THIS subject
SUMMARY.md                              root: cross-domain comprehensive summary
templates/                              lesson-template.md + discussion-template.md
AGENTS.md                               the operating manual (authoritative)
agent-docs/                             detailed agent instructions, loaded on demand
```

**Concept IDs** are `<subject-slug>/<NN>` (e.g. `system-design/03`). `NN` is the
zero-padded lesson number within the subject and **never changes once assigned**. The ID
is **subject-scoped, not path-scoped**: the domain folder organizes files on disk but is
NOT part of the ID. Subject slugs are unique across the whole repo, so `ddia/07` is
unambiguous regardless of which domain holds `ddia`.

**Status** (lesson lifecycle): `drafted` (written, not yet discussed) -> `discussed`.
**Mastery** (from the latest discussion; empty until first discussed): `solid` /
`partial` / `shaky` / `not-yet`.

The full model is in [agent-docs/repository-model.md](agent-docs/repository-model.md).

---

## Requesting content (issues)

If you do not want to author content yourself, **open an issue** and the maintainer (or an
agent) will pick it up. Use the structured forms - they collect exactly what an agent needs
to actually build the thing without a round-trip:

- **Request a new domain** - propose a new top-level theme and the subjects it would hold.
- **Request a new subject (book)** - propose one book, its source, and a concept list.
- **Request a single lesson** - propose one concept inside an existing subject.

Open one from the repository's **Issues -> New issue** menu. Blank issues are disabled so
the right fields are always captured; the templates live in
[`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/). The more precise your concept
list/scope, the closer the first draft will be.

---

## Adding a new domain

A domain is a broad theme that groups subjects (e.g. `architecture`, later `clean-code` or
`engineering-practices`). **Create a new domain only when a subject genuinely does not fit
an existing one** - do not spin up a domain for a single loosely-related book.

1. Create `<domain-slug>/` at the repo root (`lowercase-kebab-case`).
2. Add a domain `README.md` index: a short "what this domain is" paragraph, a note that
   concept IDs are subject-scoped, and a **Subjects** table with the same columns the
   existing [`architecture/README.md`](architecture/README.md) uses:

   ```
   | Subject | What it is | Lessons | Index |
   | --- | --- | --- | --- |
   | **Name** | *Book Title* (Author) - one-line scope. | <N> | [slug/README.md](slug/README.md) |
   ```
3. Add a section for the domain to the root [`SUMMARY.md`](SUMMARY.md), and remove it from
   the "Other domains: none yet" note once it has real content.
4. Add a row for the domain to the condensed domain table in the root
   [`README.md`](README.md#domains-at-a-glance) (theme, subject count, lesson count).
5. Place the first subject inside it via [Adding a new subject](#adding-a-new-subject-a-book).
6. Regenerate `CATALOG.md`: `python3 scripts/generate_catalog.py` (see
   [agent-docs/repository-model.md](agent-docs/repository-model.md)).

A domain with no subjects yet is fine as a scaffold, but prefer to land it together with
its first subject so the indexes are never empty.

---

## Adding a new subject (a book)

This follows **Workflow A** in
[agent-docs/learning-workflows.md](agent-docs/learning-workflows.md). The agent decides the
concept breakdown and ordering (foundational concepts first); a human contributor confirms
scope before mass-authoring.

1. **Pick the source and the concepts.** Identify the concepts worth isolating from the
   book and **order them by dependency**. Propose a numbered concept list - `ID`, `title`,
   one-line scope each - and confirm scope before authoring everything (unless the request
   explicitly says "write them all").
2. **Choose the domain.** Reuse an existing `<domain-slug>/` or create a new one (see
   [Adding a new domain](#adding-a-new-domain)).
3. **Scaffold the subject** under `<domain-slug>/<subject-slug>/`:
   - `README.md` - subject overview using the index-table format below.
   - `lessons/` - empty, to be filled.
   - `discussions/` - empty (records are created later, during discussions, and stay off
     `main`).
4. **Add the subject's row** to the domain `README.md` table and the root `SUMMARY.md`;
   update the domain's subject/lesson counts in the root `README.md`'s condensed domain
   table.
5. **Author the lessons** per [Adding a single lesson](#adding-a-single-lesson), either the
   agreed batch or on demand.
6. **Verify and ship.** When all agreed lessons are authored and verified and every index
   is in sync, regenerate `CATALOG.md` (`python3 scripts/generate_catalog.py`) - the
   subject is then complete. Creating a new book is the one case where the agent commits
   and pushes **automatically** (maintainer -> `main`; contributor -> a branch + pull
   request). See [Branches, commits, and pull requests](#branches-commits-and-pull-requests).

**Subject `README.md` shape** (mirror an existing one such as
[`architecture/system-design/README.md`](architecture/system-design/README.md)):

```
# <Subject Name> (<one-line positioning>)

<2-4 sentence "about this subject" intro.>

**Source book:** *<Book Title>* - <Author(s)> (<Publisher, Year>).

**How to use this subject:** read a lesson, then ask to *discuss `<subject-slug>/<NN>`*.
Ordered by dependency: <one line on the ordering>.

## Concepts

| ID  | Concept | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | <Concept> | drafted | — | — | [lesson](lessons/01-<slug>.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
```

New, undiscussed rows always use `drafted`, `—` mastery, `—` last-discussed, and `—`
records.

---

## Adding a single lesson

This follows **Workflow B** in
[agent-docs/learning-workflows.md](agent-docs/learning-workflows.md). **One concept per
lesson** - if it sprawls into two ideas, split it into two lessons.

1. **Copy the template** [`templates/lesson-template.md`](templates/lesson-template.md) to
   `<domain-slug>/<subject-slug>/lessons/<NN>-<concept-slug>.md`. Use the next free
   zero-padded `NN` in that subject; the filename number must equal the front-matter `id`
   number.
2. **Fill every required section with real content** - no placeholders, no "TODO". See the
   [quality bar](#lesson-quality-bar) below.
3. **Set the front matter** completely:
   - `id: <subject-slug>/<NN>` (stable, never changes)
   - `subject: <subject-slug>`
   - `title`, `slug` (matches the filename slug)
   - `status: drafted`
   - `mastery:` (leave empty until the first discussion)
   - `source: <Book Title, Chapter/Section>`
   - `prerequisites: []` - other concept IDs, **including cross-subject** ones (e.g.
     `[system-design/01, ddia/07]`)
   - `created` / `updated` (`YYYY-MM-DD`)
4. **Order by dependency and cross-link.** List prerequisites in the front matter and also
   name them in prose where they are used, including across subjects (e.g. a System Design
   lesson that builds on `ddia/07`).
5. **Add the row** to the subject `README.md` concepts table.
6. **Update summaries** - regenerate the subject `SUMMARY.md` and the root `SUMMARY.md`
   (see [Keeping indexes and summaries in sync](#keeping-indexes-and-summaries-in-sync)).
7. **Regenerate `CATALOG.md`** - `python3 scripts/generate_catalog.py`.

---

## Lesson quality bar

A lesson is the **complete learning material** for its concept - a deep reading, not a
summary. Assume the reader does **not** own the source book.

**Required sections** (the template enforces them):

- Front matter (all fields above).
- **TL;DR** - 1-3 sentences.
- **The idea** - the problem it solves and the intuition behind it.
- **How it works** - the mechanism in depth. This carries the weight: break it into
  labelled subsections, give **multiple concrete worked examples** (with numbers and
  step-by-step reasoning), cover the important edge cases, and explain the *why* behind
  each mechanism and trade-off. Small ASCII diagrams or comparison tables where they help.
- **Pros**.
- **Cons**.
- **Alternatives** - name them and state how each differs / when it is preferable.
- **When to use it**.
- **When NOT to use it** - and what to reach for instead.
- **Key takeaways / mental model**.
- **Self-check questions** - a few prompts the learner should be able to answer; these
  seed the discussion.
- **References** - book chapter and any links.

Prioritise completeness and clarity over brevity (most lessons run well beyond a page), but
never pad with filler. The cited book is a source and an optional "go deeper", never
required reading.

---

## Keeping indexes and summaries in sync

Drift is the main failure mode. After adding or restructuring lessons, update **all** of:

- The subject **`README.md`** concepts table (one row per lesson, accurate links).
- The subject **`SUMMARY.md`** - a per-concept recap of the whole subject. Give more detail
  where the learner struggled (`shaky`/`not-yet`, recorded misconceptions) and on
  high-importance concepts; keep solid basics brief. Cross-link to lessons and records.
- The root **`SUMMARY.md`** - one section per subject plus the top-level **"Focus areas"**
  callout that aggregates open weak spots across every subject.
- The domain **`README.md`** table, and the root **`README.md`**'s condensed domain
  table, when a subject's lesson count or a domain/subject set changes.
- **`CATALOG.md`** - regenerate with `python3 scripts/generate_catalog.py` (never
  hand-edit; it is derived from lesson front matter). Run
  `python3 scripts/generate_catalog.py --check` to confirm it's current.
- **`CHANGELOG.md`** - add a bullet under `[Unreleased]` for the content or agent-rule
  change, in the right category. The full versioning and category rules are in
  [agent-docs/release-policy.md](agent-docs/release-policy.md). Never list personal
  progress.

Regenerate the subject `SUMMARY.md` and root `SUMMARY.md` after every discussion **and**
whenever lessons are added or restructured.

---

## Branches, commits, and pull requests

The full rules are in [agent-docs/git-policy.md](agent-docs/git-policy.md). The essentials:

**Your identity decides what you may do** (determined from `git config user.email`):

- **Maintainer** (`iarechaga`): may commit and push **directly to `main`**.
- **Contributor** (anyone else): **never** commit or push to `main`. Create a branch
  (e.g. `book/<subject-slug>` or `lesson/<subject-slug>-<NN>`), do all work there, and open
  a **pull request** against `main`. Only the maintainer merges.

**When to commit/push:**

- **A new subject (book):** when it is complete and in sync, it is committed and pushed
  **automatically** - the one case you do not wait to be asked. Maintainer pushes to
  `main`; a contributor pushes the branch and opens a PR.
- **Anything else** (single lessons, edits, refactors): commit and push **only when asked**.
- **Personal learning artifacts never go to `main`** - not even for the maintainer's own
  sessions.

**Pull request rules:**

- PRs against `main` are for **lesson and subject content only**.
- Do **not** include `discussions/` records, `status`/`mastery` flips, or progress-table
  changes - those are personal and belong on a learning branch or fork.
- Do **not** commit generated/agent artifacts; `.omo/` and `.code-review-graph/` are
  gitignored - keep them out.
- Inspect `git status`, `git diff`, and recent `git log`, and **stage only intended
  files**, before committing. Use the repo's commit-message style (short, imperative
  subject, e.g. `Add <Subject> lessons on <topic>`). Never fabricate progress in a message.
- Never use destructive git commands, amend, or force-push unless explicitly requested.

---

## Style rules

- **Clear, learner-focused prose.** Concrete examples beat abstraction.
- **Self-sufficient lessons.** Teach from first principles; never assume the reader has the
  book.
- **One focused idea per lesson.** Split if it sprawls.
- **ASCII by default.** Introduce other characters only when a concept genuinely needs them
  or an existing template already uses them.
- **Stable IDs and filenames.** Never change an `id` once assigned. If a concept is renamed,
  keep the number and update the slug everywhere it is referenced.
- **Never fabricate progress.** A concept is `discussed` only after a real discussion;
  mastery reflects the actual session, not optimism.

---

## Licensing of contributions

This repository is licensed under **Creative Commons Attribution-ShareAlike 4.0
International** ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); see
[`LICENSE`](LICENSE)). By submitting a contribution (a PR or content authored on your
behalf), you agree that:

- Your contribution is **your own original work** - lessons re-explain concepts from first
  principles in your own words; do **not** copy passages, figures, or distinctive
  examples from the source books, and do not paste text from other copyrighted or
  incompatibly-licensed material.
- Each lesson **cites its source** (book + chapter) for attribution, but the prose,
  structure, and examples are original.
- Your contribution is licensed to the project and the public under **CC BY-SA 4.0**, the
  same terms as the rest of the repository.

If you are unsure whether something is original enough, paraphrase further or ask in the
PR before merging.

---

## Pre-submit checklist

Before opening a PR (or before the maintainer pushes), confirm:

- [ ] Every required lesson section is present and **non-empty** (no placeholders/TODOs).
- [ ] Front matter is complete and the `id` number matches the filename number.
- [ ] `status: drafted` and `mastery:` empty for new, undiscussed lessons.
- [ ] Prerequisites are listed (front matter + prose), including cross-subject IDs, and all
      internal links resolve.
- [ ] The subject `README.md` table has an accurate row for each new lesson.
- [ ] Subject `SUMMARY.md` and root `SUMMARY.md` are regenerated and consistent.
- [ ] Domain `README.md` / root `README.md` condensed domain table updated if a domain or
      subject set changed.
- [ ] `CATALOG.md` regenerated (`python3 scripts/generate_catalog.py --check` passes).
- [ ] `CHANGELOG.md` `[Unreleased]` has a bullet for this change, under the right category
      (Added / Deepened / Changed / Restructured / Fixed / Removed) - see
      [agent-docs/release-policy.md](agent-docs/release-policy.md). Personal progress is
      never listed.
- [ ] No personal learning artifacts in the diff (no `discussions/` records, no
      `status`/`mastery` flips, no progress-table edits).
- [ ] No generated artifacts staged (`.omo/`, `.code-review-graph/`).
- [ ] Contributors only: work is on a branch, not `main`, and targets a PR against `main`.
