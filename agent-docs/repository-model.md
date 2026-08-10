# Repository Model

Load this file before changing repository layout, concept IDs, progress fields,
subject indexes, summaries, or cross-subject references.

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
  progress-template.md                  copy this to seed PROGRESS.md
AGENTS.md                               short dispatcher for agents
CLAUDE.md                               symlink to AGENTS.md for Claude Code
agent-docs/                             detailed agent instructions loaded on demand
PROGRESS.md                             per-learner: structured track + derived progress index
LEARNER.md                              per-learner: profile (gitignored, never on main)
```

`PROGRESS.md` is a **derived index**, not a new source of truth: the front matter
`status`/`mastery` fields described below remain authoritative, and `PROGRESS.md` is a
regenerable cache scoped to one learner's track, kept for fast progress answers. See
[progress-tracking.md](progress-tracking.md) for its schema, the regeneration rule, and
Workflow P (answering progress questions). Unlike `LEARNER.md`, `PROGRESS.md` **is**
committed - but only on the learner's own branch/fork, never `main`; see
[git-policy.md](git-policy.md).

Current domains: `architecture/` (holds `ddia`, `system-design`, `hard-parts`, and
`fundamentals`). Create a new domain folder only when a subject does not fit an
existing one (e.g. later `clean-code/`, `engineering-practices/`). Do not invent
additional top-level files unless the human asks. Keep everything for a subject inside
that subject's folder, and each subject inside its domain folder.

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
3. A concept name or slug (e.g. "load balancing") - match against lesson titles/slugs.

If the reference is ambiguous (matches two concepts, or no subject in context), ask
one short clarifying question before proceeding. Never guess which concept to discuss.

## Status and mastery vocabulary

Track two independent fields per concept.

**Status** (lifecycle of the lesson):
- `drafted` - lesson written, not yet discussed.
- `discussed` - at least one discussion has happened.

**Mastery** (set from the most recent discussion's verdict; empty until first discussion):
- `solid` - understood thoroughly, including trade-offs and when-not-to-use.
- `partial` - core idea understood, gaps in trade-offs/alternatives/edge cases.
- `shaky` - significant misconceptions or unable to apply it to a scenario.
- `not-yet` - did not reach the expected understanding this session.

Both fields live in the lesson's front matter and in the subject `README.md` table.

## Seniority

Every authored lesson also carries a **`seniority`** band in its front matter, from a
fixed five-value vocabulary: `junior` < `mid` < `senior` < `staff` < `principal`. It
measures whose job the concept anchors, not how hard the lesson reads. Each subject also
declares a **seniority baseline** (its typical band) in its `README.md`. The full rubric,
the discussion-depth calibration, and worked examples live in
[seniority-model.md](seniority-model.md); load that file before assigning or showing
seniority. While a subject is only scaffolded, per-lesson bands are provisional and the
subject baseline is the reliable signal.

## Subject README index

Short "about this subject" line + the source book + a **seniority baseline** line, then a
table:

```
| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Load balancing | mid | discussed | solid | 2026-06-30 | [lesson](lessons/01-load-balancing.md) | [01](discussions/01-load-balancing/) |
```

The **Seniority** column sits between `Concept` and `Status` and uses the five bands.

## Subject SUMMARY.md

Maintain a per-concept recap of the whole subject. Give **more detail where the
learner struggled** (concepts rated `shaky`/`not-yet`, and recorded misconceptions) and
on high-importance concepts; keep solidly-understood basics brief. Cross-link to
lessons and records.

## Root SUMMARY.md

Maintain one section per subject summarizing the concepts covered and overall mastery,
plus a top-level **"Focus areas"** callout that aggregates the open weak spots across
every subject. "Greater detail where needed" means: expand on concepts rated `shaky` or
`not-yet` or flagged important; compress the rest.

Regenerate the subject `SUMMARY.md` and root `SUMMARY.md` after every discussion and
whenever lessons are added or restructured.

## Root README.md and CATALOG.md - always update together

These two are a matched pair and **always change together, in the same commit**,
whenever a lesson, subject, or domain is added, renumbered, or removed - this is a
standing rule for every future addition to the library, not a one-time cleanup:

1. **Root `README.md`** is public-facing and keeps only a **condensed domain-level
   table** (domain, one-line theme, subject count, lesson count) plus a link to
   [`CATALOG.md`](../CATALOG.md) for the full subject/lesson detail - it does not
   enumerate subjects itself. Update the affected domain's row (subject count, lesson
   count; add a new row for a brand-new domain).
2. **Root `CATALOG.md`** is the full public catalog - every domain, subject, and lesson,
   with seniority and a direct link - and is **generated, never hand-edited**. Run:
   ```
   python3 scripts/generate_catalog.py
   ```
   (stdlib only, no install needed - it reads lesson front matter directly, so it is
   always consistent with the source of truth). Run
   `python3 scripts/generate_catalog.py --check` to confirm it is current before
   declaring the work done; it exits non-zero if stale.

This is a separate step from updating `SUMMARY.md` (previous section) - all three
(`README.md`'s domain table, `CATALOG.md`, and the summaries) must be kept current
together, and none of them substitutes for another.
