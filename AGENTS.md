# AGENTS.md — Oh My Learning Operating Manual

This repository is a personal learning workspace. The human reads self-authored
lessons on a concept, then asks the agent to **discuss** that concept to test and
deepen their understanding. This file tells the agent **how to operate** that
workflow. Follow it on every learning task. It overrides nothing the human says in
the moment, but in the absence of a contrary instruction, these rules are binding.

The agent is the author of lessons, the Socratic examiner during discussions, and
the maintainer of all progress records. The human is the learner.

---

## Core loop

1. The human picks a **subject** (e.g. "system design") and usually points to a
   reference book. The agent decides the concept breakdown.
2. The agent writes one **lesson** per **concept** as a Markdown file.
3. The human reads the lesson on their own.
4. When the human asks to open/start a lesson, the agent first shows the available
   topics and progress so the learner can choose deliberately - see `Workflow C0`.
5. The human says something like *"discuss `system-design/03`"* (see Concept IDs).
6. The agent runs a **discussion**: Socratic questioning, not lecturing — see
   `Workflow C`.
7. The agent writes a **discussion record** (summary, weak spots, verdict) and
   updates every dependent summary so nothing drifts.

---

## Repository layout

Subjects are grouped by **domain** (a broad theme, e.g. `architecture`). One domain
holds one or more subjects; one subject holds one lesson per concept. Create exactly
this structure. Slugs are lowercase-kebab-case.

```
<domain-slug>/                          e.g. architecture/
  README.md                             domain index: lists the subjects in this domain
  <subject-slug>/                       e.g. ddia/, system-design/
    README.md                           subject overview + concept index/progress table
    lessons/
      <NN>-<concept-slug>.md            e.g. 01-load-balancing.md   (NN is zero-padded)
    discussions/
      <NN>-<concept-slug>/              one folder per concept
        <YYYY-MM-DD>-<SS>.md            one record per session (SS = session # that day, e.g. 01)
    SUMMARY.md                          comprehensive recap of THIS subject
SUMMARY.md                              root: cross-domain comprehensive summary
templates/
  lesson-template.md                    copy this to author a lesson
  discussion-template.md                copy this to write a discussion record
AGENTS.md                               this file
```

Current domains: `architecture/` (holds `ddia`, `system-design`). Create a new domain
folder only when a subject does not fit an existing one (e.g. later `clean-code/`,
`engineering-practices/`). Do not invent additional top-level files unless the human
asks. Keep everything for a subject inside that subject's folder, and each subject
inside its domain folder.

---

## Concept IDs

Every concept has a stable ID: **`<subject-slug>/<NN>`** (e.g. `system-design/03`).
`NN` is the zero-padded lesson number within the subject and never changes once
assigned. The lesson filename embeds the same number. The ID is **subject-scoped, not
path-scoped**: the domain folder (e.g. `architecture/`) organizes files on disk but is
NOT part of the ID. Subject slugs are unique across the whole repo, so `ddia/07` is
unambiguous regardless of which domain holds `ddia`.

When the human refers to a concept to discuss, resolve it in this order:
1. A full ID like `system-design/03`.
2. A bare number (`03` / `3`) when a single subject is clearly in context.
3. A concept name or slug (e.g. "load balancing") — match against lesson titles/slugs.

If the reference is ambiguous (matches two concepts, or no subject in context), ask
one short clarifying question before proceeding. Never guess which concept to
discuss.

---

## Status & mastery vocabulary

Track two independent fields per concept.

**Status** (lifecycle of the lesson):
- `drafted` — lesson written, not yet discussed.
- `discussed` — at least one discussion has happened.

**Mastery** (set from the most recent discussion's verdict; empty until first discussion):
- `solid` — understood thoroughly, including trade-offs and when-not-to-use.
- `partial` — core idea understood, gaps in trade-offs/alternatives/edge cases.
- `shaky` — significant misconceptions or unable to apply it to a scenario.
- `not-yet` — did not reach the expected understanding this session.

Both fields live in the lesson's front matter and in the subject `README.md` table.

---

## Workflow A — Plan a subject

Trigger: the human names a subject and/or provides a book.

1. Read whatever source material the human points to. If it is a book, identify the
   concepts worth isolating; **the agent decides coverage and ordering** — order by
   dependency (foundational concepts first).
2. Propose a numbered concept list (ID, title, one-line scope each) and confirm
   scope with the human before mass-authoring, unless they explicitly said "write
   them all."
3. Scaffold the subject: choose its **domain** (reuse an existing `<domain-slug>/` or
   create a new one with a domain `README.md` index), then create
   `<domain-slug>/<subject-slug>/`, an initial subject `README.md` (using the
   index-table format below), and the `lessons/` and `discussions/` folders. Add the
   new subject's row to the domain `README.md`.
4. Author lessons per `Workflow B`, either the agreed batch or on demand.
5. When the subject is complete (all agreed lessons authored and verified, indexes in
   sync), **commit and push it automatically** — creating a new book is the one case
   where you do not wait to be asked. Follow the **Git** policy below for where to push
   (maintainer → `main`; contributor → a new branch + pull request).

---

## Workflow B — Author a lesson

Trigger: a concept needs its lesson written.

1. Copy `templates/lesson-template.md` to `<subject-slug>/lessons/<NN>-<slug>.md`.
2. Fill **every** required section with real, concrete content — no placeholders, no
   "TODO". One concept only; if it sprawls into two ideas, split it into two lessons.

Required sections (the template enforces these):
- Front matter: `id`, `subject`, `title`, `slug`, `status`, `mastery`, `source`,
  `prerequisites`, `created`, `updated`.
- **TL;DR** — 1-3 sentences.
- **The idea** — the problem it solves and the intuition behind it.
- **How it works** — the mechanism/approach in depth, with multiple concrete worked
  examples.
- **Pros**.
- **Cons**.
- **Alternatives** — name them and state how each differs.
- **When to use it**.
- **When NOT to use it**.
- **Key takeaways / mental model**.
- **Self-check questions** — a few prompts the learner should be able to answer
  (these seed the discussion).
- **References** — book chapter and any links.

**Depth and self-sufficiency (assume the learner does NOT have the book).** Each
lesson is the complete learning material for its concept: a deep reading, not a
summary. Teach every idea needed from first principles; never assume the reader has
read or owns the source. "How it works" carries the weight - break it into labelled
subsections, give multiple concrete worked examples (with numbers and step-by-step
reasoning), cover the important edge cases, and explain the *why* behind each
mechanism and trade-off. Use small ASCII diagrams or comparison tables where they aid
understanding. Prioritise completeness and clarity over brevity (most lessons run well
beyond a page); never pad with filler. The cited book is a source and an optional
"go deeper", never required reading.

3. Set front matter: `status: drafted`, `mastery:` empty, fill `source` and
   `prerequisites` (other concept IDs, if any).
4. Add or update the concept's row in the subject `README.md` index.

**Verify a lesson before declaring done:**
- Every required section is present and non-empty.
- Front matter is complete and `id` matches the filename number.
- The `README.md` index contains an accurate row for this concept.
- Internal links (to prerequisites, references) resolve.

---

## Workflow C0 — Open a lesson / show topic progress

Trigger: *"open a lesson"*, *"start learning"*, *"show lessons"*, *"what should I
study next?"*, *"let's cover architecture"*, or any request to begin choosing a lesson
rather than discussing a specific concept immediately.

Before pointing the learner at a lesson, present a compact topic catalog:

1. Read the relevant domain `README.md`, subject `README.md` files, and root
   `SUMMARY.md` as needed. If no domain or subject is specified, show the top-level
   subject catalog first.
2. For each relevant subject, compute progress from its concept table:
   - total lessons;
   - drafted/not yet discussed count;
   - discussed count;
   - mastery counts (`solid`, `partial`, `shaky`, `not-yet`, and not-yet-rated);
   - suggested next undiscussed concept, respecting prerequisite/order.
3. Present available topics grouped by subject. Mark each concept as:
   - **not started** — `drafted` and no discussion record;
   - **started** — at least one discussion record exists or status is `discussed`;
   - **needs revisit** — latest mastery is `partial`, `shaky`, or `not-yet`;
   - **solid** — latest mastery is `solid`.
4. Keep the catalog short by default: show subject-level progress plus the next few
   candidate topics. Offer to expand a subject instead of dumping every lesson when the
   catalog is large.
5. Ask the learner to pick a concept, or recommend one specific next concept with a
   one-sentence reason. Never start quizzing until the learner has selected or accepted
   a concept.

When a specific concept is already named (e.g. *"discuss `ddia/07`"*), do not show the
full catalog first. Resolve the concept, read the lesson, and proceed with `Workflow C`.
You may still mention one line of current progress for that subject before the first
question.

---

## Workflow C — Run a discussion

Trigger: *"discuss `<ID>`"*, *"let's go over X"*, or similar.

This is the heart of the repo. The goal is to find out what the learner actually
understands and to guide them to the correct conclusions **themselves**.

**Before starting:** read the full lesson file for that concept. Also inspect the
lesson front matter `prerequisites`, the subject `README.md`, and any nearby
cross-subject references so you know what related concepts exist. Never quiz on
anything not covered by the lesson. Confirm which concept and, if helpful, ask the
learner how confident they already feel.

**During the discussion — rules:**
- **Socratic, not a lecture.** Ask one focused question at a time, then wait for the
  answer. Do not stack multiple questions or pre-empt with the explanation.
- **Progress through the concept** roughly in this order, adapting to their answers:
  1. The problem it solves / the intuition.
  2. How it works.
  3. Trade-offs (pros and cons).
  4. Alternatives and how they compare.
  5. The hard part: **when NOT to use it**, plus an applied scenario.
- **When the learner is vague or wrong, do not hand over the answer.** Nudge with a
  hint or a narrower leading question. Give the direct answer only after ~2 failed
  attempts, then re-test the same idea from a fresh angle to confirm it landed.
- **Test transfer, not recall.** Include at least one applied scenario — *"Given a
  system with constraint Y, would you reach for this? Why or why not?"* — to check
  they can use the idea, not just recite it.
- **Scale difficulty** to their performance: go deeper when they are solid, slow
  down and rebuild from fundamentals when they struggle.
- **Track weak spots and misconceptions as they surface** — you will record them.
- **End** when the core sub-areas have been probed and the learner has either shown
  solid understanding or hit a clear ceiling for this session.
- **Close with related next topics.** After the verdict, recommend 1-3 concrete related
  concepts to study next. Prefer prerequisites that were weak, direct follow-ons in the
  same subject, and cross-subject lessons that cover the same idea from another angle
  (for example, a Fundamentals style lesson may point to System Design components or
  Hard Parts trade-off lessons). Explain each recommendation in one short sentence.

**After the discussion — record + propagate:**
1. Write the discussion record (copy `templates/discussion-template.md`) to
   `<subject-slug>/discussions/<NN>-<slug>/<YYYY-MM-DD>-<SS>.md`. It must contain:
   - Header: concept ID, title, date, session number.
   - **Scope covered** — which sub-areas were probed.
   - **Strengths** — what the learner clearly understood.
   - **Weak spots / misconceptions** — specific, each paired with the corrected
     understanding.
   - **Verdict** — a `mastery` rating (`solid`/`partial`/`shaky`/`not-yet`) with a
     one-line justification.
   - **Reached expected understanding?** — Yes / Partially / No.
   - **Recommended follow-up** — sections to re-read, prerequisites to shore up,
     whether to re-discuss and roughly when.
   - **Related next topics** — 1-3 concept IDs with one-line reasons, or `None` if no
     useful follow-up exists.
2. Update the lesson front matter: `status: discussed`, `mastery: <verdict>`,
   bump `updated`.
3. Update the subject `README.md` row: status, mastery, last-discussed date, and a
   link to the new record.
4. Regenerate the subject `SUMMARY.md` and the root `SUMMARY.md` (see below) so they
   reflect this session.

**Verify after a discussion before declaring done:**
- The record file exists with all sections filled.
- Lesson front matter updated (status, mastery, updated).
- `README.md` row updated (status, mastery, date, record link).
- Subject `SUMMARY.md` and root `SUMMARY.md` reflect the latest verdict and weak
  spots.
- The record captures related next topics and the learner was told those recommendations
  before the session ended.

---

## Summaries (keep in sync, never let them drift)

### Subject `README.md` — index + progress

Short "about this subject" line + the source book, then a table:

```
| ID  | Concept | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Load balancing | discussed | solid | 2026-06-30 | [lesson](lessons/01-load-balancing.md) | [01](discussions/01-load-balancing/) |
```

### Subject `SUMMARY.md` — comprehensive recap of one subject

A per-concept recap of the whole subject. Give **more detail where the learner
struggled** (concepts rated `shaky`/`not-yet`, and recorded misconceptions) and on
high-importance concepts; keep solidly-understood basics brief. Cross-link to
lessons and records.

### Root `SUMMARY.md` — cross-subject comprehensive summary

One section per subject summarizing the concepts covered and overall mastery, plus a
top-level **"Focus areas"** callout that aggregates the open weak spots across every
subject. "Greater detail where needed" means: expand on concepts rated
`shaky`/`not-yet` or flagged important; compress the rest.

Regenerate the subject `SUMMARY.md` and root `SUMMARY.md` after every discussion and
whenever lessons are added or restructured.

---

## Conventions & constraints

- Write lessons and discussion prose in clear, plain language aimed at a learner —
  concrete examples over abstraction.
- ASCII by default; introduce other characters only when a concept genuinely needs
  them.
- During a discussion, **do not pre-load the answer** into your questions and do not
  rush to correct — give the learner room to reason first.
- Never fabricate progress: a concept is `discussed` only after a real discussion;
  mastery reflects the actual session, not optimism.
- Keep IDs and filenames stable once assigned; if a concept is renamed, keep the
  number and update the slug everywhere it is referenced.
- Commit and push follow the **Git: branches, commits, and pushes** policy below.

---

## Git: branches, commits, and pushes

Your identity decides what you may do. Determine it from the repository's git author
email (`git config user.email`):

- **Maintainer — `iarechaga`.** The configured author email belongs to the `iarechaga`
  GitHub account. You may commit and push **directly to `main`**.
- **Contributor — anyone else.** Any other author email. You must **never** commit or
  push to `main`. Always start by creating a new branch (e.g. `book/<subject-slug>` or
  `learn/<name>`) and do all work there, then open a pull request against `main`. Only
  the maintainer merges to `main`.

When to commit and push:

- **Creating a new subject (book):** when the subject is complete per Workflow A (all
  agreed lessons authored and verified, indexes in sync), **commit and push it
  automatically** — this is the one case where you do not wait to be asked. The
  maintainer pushes to `main`; a contributor pushes the branch and opens a pull request.
- **Anything else** — single lessons, discussion records, edits, refactors — commit and
  push **only when the human asks**.
- Personal learning artifacts (discussion records, `status`/`mastery` edits,
  progress-table changes) are never committed to `main` directly; they live on a branch
  or fork, even for the maintainer's own sessions.

Use the repo's commit-message style, and never fabricate progress in a message.

---

## Templates

- Author a lesson → copy `templates/lesson-template.md`.
- Record a discussion → copy `templates/discussion-template.md`.
