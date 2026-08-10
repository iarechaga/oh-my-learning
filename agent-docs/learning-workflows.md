# Learning Workflows

Load this file before planning a subject, authoring lessons, opening/showing the lesson
catalog, running a discussion, writing discussion records, or updating learning
progress.

## Workflow A - Plan a subject

Trigger: the human names a subject and/or provides a book.

1. Read whatever source material the human points to. If it is a book, identify the
   concepts worth isolating; **the agent decides coverage and ordering** - order by
   dependency (foundational concepts first).
2. Propose a numbered concept list (ID, title, one-line scope each) and confirm scope
   with the human before mass-authoring, unless they explicitly said "write them all."
3. Scaffold the subject: choose its **domain** (reuse an existing `<domain-slug>/` or
   create a new one with a domain `README.md` index), then create
   `<domain-slug>/<subject-slug>/`, an initial subject `README.md` (using the index-table
   format in [repository-model.md](repository-model.md)), and the `lessons/` and
   `discussions/` folders. Add the new subject's row to the domain `README.md`.
4. Author lessons per `Workflow B`, either the agreed batch or on demand.
5. When the subject is complete (all agreed lessons authored and verified, indexes in
   sync), regenerate the root catalog: `python3 scripts/generate_catalog.py` (see
   [repository-model.md](repository-model.md)), and update the domain's row in the root
   `README.md`'s condensed domain table (subject/lesson counts). Then **commit and push
   it automatically** - creating a new book is the one case where you do not wait to be
   asked. Follow [git-policy.md](git-policy.md) for where to push (maintainer ->
   `main`; contributor -> a new branch + pull request).

## Workflow B - Author a lesson

Trigger: a concept needs its lesson written.

1. Copy `templates/lesson-template.md` to `<subject-slug>/lessons/<NN>-<slug>.md`.
2. Fill **every** required section with real, concrete content - no placeholders, no
   "TODO". One concept only; if it sprawls into two ideas, split it into two lessons.

Required sections (the template enforces these):
- Front matter: `id`, `subject`, `title`, `slug`, `status`, `mastery`, `source`,
  `prerequisites`, `created`, `updated`.
- **TL;DR** - 1-3 sentences.
- **The idea** - the problem it solves and the intuition behind it.
- **How it works** - the mechanism/approach in depth, with multiple concrete worked
  examples.
- **Pros**.
- **Cons**.
- **Alternatives** - name them and state how each differs.
- **When to use it**.
- **When NOT to use it**.
- **Key takeaways / mental model**.
- **Self-check questions** - a few prompts the learner should be able to answer (these
  seed the discussion).
- **References** - book chapter and any links.

**Depth and self-sufficiency (assume the learner does NOT have the book).** Each lesson
is the complete learning material for its concept: a deep reading, not a summary. Teach
every idea needed from first principles; never assume the reader has read or owns the
source. "How it works" carries the weight - break it into labelled subsections, give
multiple concrete worked examples (with numbers and step-by-step reasoning), cover the
important edge cases, and explain the *why* behind each mechanism and trade-off. Use
small ASCII diagrams or comparison tables where they aid understanding. Prioritise
completeness and clarity over brevity (most lessons run well beyond a page); never pad
with filler. The cited book is a source and an optional "go deeper", never required
reading.

3. Set front matter: `status: drafted`, `mastery:` empty, fill `source` and
   `prerequisites` (other concept IDs, if any). Assign `seniority` (one of
   `junior`/`mid`/`senior`/`staff`/`principal`) using the rubric in
   [seniority-model.md](seniority-model.md) - tag by whose job the concept anchors, and
   prefer the lower band on a tie.
4. Add or update the concept's row in the subject `README.md` index, including the
   **Seniority** column, and keep the subject's seniority baseline line accurate.
5. Regenerate `CATALOG.md` (`python3 scripts/generate_catalog.py`) so the public catalog
   picks up the new lesson - see [repository-model.md](repository-model.md).

**Verify a lesson before declaring done:**
- Every required section is present and non-empty.
- Front matter is complete, `id` matches the filename number, and `seniority` is one of
  the five bands.
- The `README.md` index contains an accurate row for this concept (Seniority column
  filled), and the subject baseline still reflects the lessons.
- Internal links (to prerequisites, references) resolve.
- `CATALOG.md` is regenerated (`python3 scripts/generate_catalog.py --check` passes).

## Workflow C0 - Open a lesson / show topic progress

Trigger: *"open a lesson"*, *"start learning"*, *"show lessons"*, *"what should I study
next?"*, *"let's cover architecture"*, or any request to begin choosing a lesson rather
than discussing a specific concept immediately.

Before pointing the learner at a lesson, present a compact topic catalog:

1. Read the relevant domain `README.md`, subject `README.md` files, and root
   `SUMMARY.md` as needed. If no domain or subject is specified, show the top-level
   subject catalog first.
2. For each relevant subject, compute progress from its concept table:
   - total lessons;
   - drafted/not yet discussed count;
   - discussed count;
   - mastery counts (`solid`, `partial`, `shaky`, `not-yet`, and not-yet-rated);
   - the subject's **seniority baseline** and, where useful, the band spread across
     lessons (e.g. "ranges junior->staff");
   - suggested next undiscussed concept, respecting prerequisite/order.
3. Present available topics grouped by subject. Show each concept's **seniority** band
   alongside its state, and mark each concept as:
   - **not started** - `drafted` and no discussion record;
   - **started** - at least one discussion record exists or status is `discussed`;
   - **needs revisit** - latest mastery is `partial`, `shaky`, or `not-yet`;
   - **solid** - latest mastery is `solid`.
4. Keep the catalog short by default: show subject-level progress plus the next few
   candidate topics. Offer to expand a subject instead of dumping every lesson when the
   catalog is large.
5. Ask the learner to pick a concept, or recommend one specific next concept with a
   one-sentence reason (you may factor in seniority - e.g. suggest a lower-band concept to
   build confidence or a higher-band one to stretch). Never start quizzing until the
   learner has selected or accepted a concept.

When a specific concept is already named (e.g. *"discuss `ddia/07`"*), do not show the
full catalog first. Resolve the concept, read the lesson, and proceed with `Workflow C`.
You may still mention one line of current progress for that subject before the first
question.

## Workflow C - Run a discussion

Trigger: *"discuss `<ID>`"*, *"let's go over X"*, or similar.

This is the heart of the repo. The goal is to find out what the learner actually
understands and to guide them to the correct conclusions **themselves**.

**Before starting:** read the full lesson file for that concept. Also inspect the lesson
front matter `prerequisites` and `seniority`, the subject `README.md`, and any nearby
cross-subject references so you know what related concepts exist and at what level to pitch
the session. Never quiz on anything not covered by the lesson. Confirm which concept and,
if helpful, ask the learner how confident they already feel.

**During the discussion - rules:**
- **Socratic, not a lecture.** Ask one focused question at a time, then wait for the
  answer. Do not stack multiple questions or pre-empt with the explanation.
- **Progress through the concept** roughly in this order, adapting to their answers:
  1. The problem it solves / the intuition.
  2. How it works.
  3. Trade-offs (pros and cons).
  4. Alternatives and how they compare.
  5. The hard part: **when NOT to use it**, plus an applied scenario.
- **When the learner is vague or wrong, do not hand over the answer.** Nudge with a hint
  or a narrower leading question. Give the direct answer only after ~2 failed attempts,
  then re-test the same idea from a fresh angle to confirm it landed.
- **Test transfer, not recall.** Include at least one applied scenario - *"Given a
  system with constraint Y, would you reach for this? Why or why not?"* - to check they
  can use the idea, not just recite it.
- **Calibrate to the lesson's `seniority` band.** Pitch the questioning to the band and
  adapt if the learner clearly over- or under-performs it (see
  [seniority-model.md](seniority-model.md) for the per-band script):
  - `junior` - correctness and mechanism; one applied scenario with a mostly-clear answer.
  - `mid` - option-selection and first-order trade-offs; compare named alternatives.
  - `senior` - trade-offs, failure modes, and when NOT to; the applied scenario has no
    clean answer.
  - `staff` - cross-system/cross-team effects, second-order consequences, evolution over
    time; introduce conflicting constraints.
  - `principal` - strategy, leverage, and measurement; interrogate ambiguity rather than
    resolving it.
- **Scale difficulty** to their performance within the band: go deeper when they are
  solid, slow down and rebuild from fundamentals when they struggle. Judge the mastery
  verdict against the concept's own band.
- **Track weak spots and misconceptions as they surface** - you will record them.
- **End** when the core sub-areas have been probed and the learner has either shown
  solid understanding or hit a clear ceiling for this session.
- **Close with related next topics.** After the verdict, recommend 1-3 concrete related
  concepts to study next. Prefer prerequisites that were weak, direct follow-ons in the
  same subject, and cross-subject lessons that cover the same idea from another angle
  (for example, a Fundamentals style lesson may point to System Design components or
  Hard Parts trade-off lessons). Explain each recommendation in one short sentence.

**After the discussion - record + propagate:**
1. Write the discussion record (copy `templates/discussion-template.md`) to
   `<subject-slug>/discussions/<NN>-<slug>/<YYYY-MM-DD>-<SS>.md`. It must contain:
   - Header: concept ID, title, date, session number.
   - **Scope covered** - which sub-areas were probed.
   - **Strengths** - what the learner clearly understood.
   - **Weak spots / misconceptions** - specific, each paired with the corrected
     understanding.
   - **Verdict** - a `mastery` rating (`solid`/`partial`/`shaky`/`not-yet`) with a
     one-line justification.
   - **Reached expected understanding?** - Yes / Partially / No.
   - **Recommended follow-up** - sections to re-read, prerequisites to shore up, whether
     to re-discuss and roughly when.
   - **Related next topics** - 1-3 concept IDs with one-line reasons, or `None` if no
     useful follow-up exists.
2. Update the lesson front matter: `status: discussed`, `mastery: <verdict>`, bump
   `updated`.
3. Update the subject `README.md` row: status, mastery, last-discussed date, and a link
   to the new record.
4. Regenerate the subject `SUMMARY.md` and the root `SUMMARY.md` so they reflect this
   session.
5. If `PROGRESS.md` exists at the repo root, update it too - see
   [progress-tracking.md](progress-tracking.md) for the full schema and regeneration rule.
   In short: update this concept's row (`Lesson status`, `Mastery`, `Last discussed`),
   flip its `Track status` from `current` to `done`, promote the next `queued` row to
   `current` and rewrite **Next up**, recompute **Stats** and **Focus areas** by tallying
   the Track table, and append one line to **Recent sessions**. If `PROGRESS.md` does not
   exist yet (no structured track was set up during onboarding), skip this step - do not
   create one mid-discussion.

**Verify after a discussion before declaring done:**
- The record file exists with all sections filled.
- Lesson front matter updated (status, mastery, updated).
- `README.md` row updated (status, mastery, date, record link).
- Subject `SUMMARY.md` and root `SUMMARY.md` reflect the latest verdict and weak spots.
- The record captures related next topics and the learner was told those recommendations
  before the session ended.
- If `PROGRESS.md` exists: its row for this concept, **Next up**, **Stats**, **Focus
  areas**, and **Recent sessions** all reflect this session's outcome.

## Templates

- Author a lesson -> copy `templates/lesson-template.md`.
- Record a discussion -> copy `templates/discussion-template.md`.
