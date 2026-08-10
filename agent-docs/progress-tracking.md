# Progress Tracking

Load this file before answering any progress question ("what's next", "how am I
doing", "where should I focus", "put more focus on X"), before writing `PROGRESS.md`
for the first time (Workflow O, Step 4), or before updating it after a discussion
(Workflow C).

`PROGRESS.md` lives at the repository root, next to `LEARNER.md`. It is the
learner's personal **structured track** - an ordered study plan plus a derived,
LLM-optimized index of progress - kept up to date across sessions so progress
questions never require walking the whole repo.

---

## Source of truth vs. derived index

Per-lesson `status` and `mastery` in each lesson's front matter (see
[repository-model.md](repository-model.md)) remain the **single source of truth**.
`PROGRESS.md` is a **derived, regenerable cache** scoped to the learner's track: it
exists purely so progress questions are fast and repo-wide scans are unnecessary. If
`PROGRESS.md` and a lesson's front matter ever disagree, the front matter wins -
regenerate the disagreeing row from it.

Two things in `PROGRESS.md` are *not* derivable from front matter and must be
maintained by the agent directly, not regenerated from a scan:
- **Track membership and order** - which concepts are on the track, in what
  sequence, and why (the one-line reason per step). This reflects the learner's
  stated goal (see `LEARNER.md` Goals and concerns) and the agent's judgment, not
  something the repo encodes anywhere else.
- **Track status** (`queued` / `current` / `done` / `skipped`) - the learner's
  position on the track. `done` normally lines up with lesson `status: discussed`,
  but `skipped` (deprioritized without discussing) and `current` (in progress) have
  no front-matter equivalent.

Everything else in the file - lesson status, mastery, seniority, last-discussed
date, the Stats and Focus areas rollups, Recent sessions - is a straight readout of
front matter for the concepts on the track and can always be safely regenerated.

---

## File schema

`PROGRESS.md` is optimized to be read and edited by an agent: stable section
headers, one markdown table per concern, short fields, no prose that has to be
re-parsed. It does not need to look polished - the agent renders it into a friendly
summary in conversation when the learner asks.

```markdown
# Progress

<!-- Derived index. Source of truth = lesson front matter (status/mastery) in each
     subject's lessons/. Track membership, order, and status are agent-maintained,
     not derived. Regenerate Stats/Focus areas/Recent sessions from front matter;
     never fabricate a status or mastery value not backed by a lesson or session. -->

**Learner:** <name from LEARNER.md>
**Track goal:** <one-line objective, from LEARNER.md Goals and concerns>
**Last updated:** YYYY-MM-DD

## Next up
1. <subject/NN> - <title> - <one-line reason it's next>
2. <subject/NN> - <title> - <reason>
3. <subject/NN> - <title> - <reason>

## Track
| # | ID | Concept | Seniority | Track status | Lesson status | Mastery | Last discussed | Reason |
| - | -- | ------- | --------- | ------------ | -------------- | ------- | --------------- | ------ |
| 1 | system-design/01 | ... | mid | done | discussed | solid | 2026-07-14 | foundation for everything else |
| 2 | system-design/02 | ... | mid | current | discussed | partial | 2026-07-20 | builds directly on #1 |
| 3 | ddia/03 | ... | senior | queued | drafted | | | needed before sharding topics |
| 4 | hard-parts/02 | ... | senior | skipped | drafted | | | deprioritized: not interview-relevant |

## Focus areas
- **Shaky:** <ID> - <concept> - <one-line note on the gap>
- **Not-yet:** <ID> - <concept> - <one-line note>
(omit a bullet list entirely if empty; do not print "none" noise)

## Stats
### By subject
| Subject | On track | Done | Solid | Partial | Shaky | Not-yet |
| ------- | -------- | ---- | ----- | ------- | ----- | ------- |
| system-design | 8 | 3 | 2 | 1 | 0 | 0 |

### By seniority band
| Band | On track | Done | Solid | Partial | Shaky | Not-yet |
| ---- | -------- | ---- | ----- | ------- | ----- | ------- |
| mid | 5 | 3 | 2 | 1 | 0 | 0 |
| senior | 3 | 0 | 0 | 0 | 0 | 0 |

## Recent sessions
<!-- newest last, one line per discussion -->
- 2026-07-14 - system-design/01 - solid - clean on trade-offs, minor gap on failure modes
- 2026-07-20 - system-design/02 - partial - needs a re-pass on consensus
```

Field notes:
- **Track status** vocabulary is exactly `queued` / `current` / `done` / `skipped` -
  never invent other values. Exactly one row is normally `current` at a time (the
  concept the learner is actively working toward); it is fine to have zero if the
  learner just finished one and hasn't been told what's next yet (fix this
  immediately by promoting the next `queued` row).
- **Lesson status** / **Mastery** mirror the lesson's front matter verbatim - do not
  restate them differently.
- The track is **goal-scoped, not repo-wide**: only concepts relevant to the
  learner's stated objective belong on it. It is expected to cover a subset of the
  repo's 8 domains / hundreds of lessons, and it is expandable later (Workflow P
  handles adding concepts when the goal shifts or the learner asks for more).
- Keep table rows sorted by track order (the sequence the learner should tackle
  them), not alphabetically or by ID.

---

## Regeneration rule

Whenever a lesson's `status`/`mastery` changes (i.e. after every discussion, per
Workflow C), regenerate the affected parts of `PROGRESS.md` **from the front matter
of the concepts currently on the track** - not from a full-repo scan, and not by
hand-guessing values:

1. Update that concept's row: `Lesson status`, `Mastery`, `Last discussed`.
2. Flip its `Track status` from `current` to `done` (unless the learner explicitly
   wants to revisit it later - keep it `current` in that case and say so).
3. Promote the next `queued` row to `current` and rewrite **Next up** from the first
   few `queued`/newly-`current` rows.
4. Recompute **Stats** (by subject and by seniority band) by counting the Track
   table rows - a simple tally, not a repo walk.
5. Recompute **Focus areas** by listing every track row whose `Mastery` is `shaky`
   or `not-yet`.
6. Append one line to **Recent sessions**.
7. Bump **Last updated**.

A full rebuild of the Track table from scratch (re-deriving membership and order,
not just status) only happens when: `PROGRESS.md` doesn't exist yet (Workflow O,
Step 4), the learner's goal changed enough to warrant re-planning, or the file is
found to have drifted from front matter in a way a targeted update can't fix.
Otherwise, edit the existing table in place - don't regenerate wholesale on every
small change; that discards the reasons and ordering the learner already agreed to.

---

## Workflow P - Answer a progress question

Trigger: *"what's next"*, *"how am I doing"*, *"where should I focus"*, *"give me
more X"*, *"how's my system-design going"*, or any question about status, progress,
or study focus that is not a request to discuss a specific concept.

1. **Read only `PROGRESS.md`.** Do not open lesson files, subject `README.md`
   tables, or `SUMMARY.md` for this - that defeats the point of keeping the index.
   The only exception: the learner asks for the *detail* of one specific concept
   (e.g. "remind me what `ddia/03` covers" or "why did I struggle with `system-design/02`?")
   - then, and only then, open that concept's lesson and/or discussion record.
2. Answer directly from the file's structured sections:
   - *"what's next"* -> render **Next up**.
   - *"how am I doing"* / general status -> render **Stats** plus a one-line summary
     (e.g. "5/12 on track, 3 solid, 1 shaky").
   - *"where should I improve"* / *"what's shaky"* -> render **Focus areas**.
   - *"how did last session go"* -> render the last line(s) of **Recent sessions**.
3. Always render the answer **friendly and conversational** - `PROGRESS.md`'s
   markdown tables are for the agent to parse, not to paste verbatim into chat.
   Summarize in prose, use a short list, or a small ad-hoc table if it helps; never
   dump the raw file.
4. **"More focus on X"** (a subject, a concept, a theme) is a track-editing request:
   - Re-order the **Track** table so `queued` rows related to X move earlier
     (respecting prerequisite order - never reorder a concept ahead of an
     unresolved prerequisite).
   - If X isn't on the track yet, add it: read the relevant subject `README.md` to
     find matching concepts, insert rows in dependency order, mark them `queued`.
     This is the one case Workflow P *does* read beyond `PROGRESS.md`, because the
     track is genuinely expanding.
   - Rewrite **Next up** to reflect the new order and set `Last updated`.
   - Tell the learner what changed in one or two sentences; do not silently
     rewrite their track.

## Non-negotiables

- Never fabricate a `Mastery` or `Lesson status` value in `PROGRESS.md` that isn't
  backed by a real lesson or discussion - same rule as the front matter itself (see
  [AGENTS.md](../AGENTS.md) non-negotiables).
- Keep `PROGRESS.md` and the underlying lesson front matter consistent; front matter
  wins on any conflict.
- `PROGRESS.md` is committed on the learner's branch/fork, never on `main` - see
  [git-policy.md](git-policy.md).
