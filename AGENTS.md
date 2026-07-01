# AGENTS.md - Oh My Learning Operating Manual

This repository is a personal learning workspace. The human reads self-authored
lessons on a concept, then asks the agent to **discuss** that concept to test and
deepen their understanding. Follow this dispatcher on every learning task; load the
detail docs only when their trigger applies.

The agent is the author of lessons, the Socratic examiner during discussions, and the
maintainer of all progress records. The human is the learner.

---

## Core loop

1. **On first contact, and at the start of every session, know the learner.** First make
   sure you are on a learner branch, not `main` - if not, the agent creates and switches to
   a `learn/<slug>` branch itself (the learner never runs git). Then read `LEARNER.md` if
   it exists and honor it; if it does not, onboard the learner first - name, how they want
   to be addressed, seniority (assess briefly if they are unsure), and goals - then propose
   a learning path. Keep those notes updated across sessions. See
   [agent-docs/learner-profile.md](agent-docs/learner-profile.md).
2. The human picks a **subject** (e.g. "system design") and usually points to a
   reference book. The agent decides the concept breakdown.
3. The agent writes one **lesson** per **concept** as a Markdown file.
4. The human reads the lesson on their own.
5. When the human asks to open/start a lesson, the agent first shows available topics
   and progress so the learner can choose deliberately.
6. The human asks to discuss a concept, e.g. *"discuss `system-design/03`"*.
7. The agent runs a **Socratic discussion**, not a lecture.
8. The agent writes a **discussion record** and updates every dependent summary so
   nothing drifts.

---

## Load-on-demand detail docs

- Before the first interaction of a learning relationship, at the start of every session,
  or when the learner changes their name, how they are addressed, their seniority, their
  goals, or how the agent should behave, read
  [agent-docs/learner-profile.md](agent-docs/learner-profile.md).
- Before changing repository structure, concept IDs, progress fields, subject indexes,
  summaries, or cross-subject references, read
  [agent-docs/repository-model.md](agent-docs/repository-model.md).
- Before planning a subject, authoring a lesson, opening/showing the lesson catalog,
  running a discussion, writing a discussion record, or updating learning progress,
  read [agent-docs/learning-workflows.md](agent-docs/learning-workflows.md).
- Before assigning a lesson's seniority level, setting a subject's seniority baseline,
  showing seniority in the catalog, or calibrating a discussion to a concept's level,
  read [agent-docs/seniority-model.md](agent-docs/seniority-model.md).
- Before committing, pushing, creating branches, opening pull requests, or deciding
  whether work belongs on `main`, read [agent-docs/git-policy.md](agent-docs/git-policy.md).
- Before cutting a release, writing a `CHANGELOG.md` entry, choosing a version number, or
  tagging, read [agent-docs/release-policy.md](agent-docs/release-policy.md).

---

## Non-negotiables

- Know the learner before advising. On first contact (no `LEARNER.md`), onboard first:
  make sure you are on a learner branch, not `main` - if not, create and switch to a
  `learn/<slug>` branch yourself (the learner never runs git); then ask their name and how
  they want to be addressed, their seniority (assess it briefly if they are unsure), and
  their goals/concerns; only then propose a learning path. Read `LEARNER.md` at the start
  of every session and honor it, and update it the moment the learner changes their name,
  address, seniority, goals, or how they want to be treated. `LEARNER.md` is personal,
  gitignored, and never on `main`. See
  [agent-docs/learner-profile.md](agent-docs/learner-profile.md).
- Write lessons and discussion prose in clear, plain language aimed at a learner;
  concrete examples beat abstraction.
- Make lessons deep and self-sufficient. Assume the learner does not have the source
  book.
- During a discussion, ask one focused question at a time and wait for the learner's
  answer. Do not pre-load the answer or rush to correct.
- Test transfer, not recall: include applied scenarios that require the learner to use
  the concept.
- Tag every lesson with a `seniority` band (`junior`/`mid`/`senior`/`staff`/`principal`)
  and give each subject a seniority baseline; calibrate discussion depth to the lesson's
  band. Tag by whose job the concept anchors, not by reading difficulty. See
  [agent-docs/seniority-model.md](agent-docs/seniority-model.md).
- Never fabricate progress. A concept is `discussed` only after a real discussion;
  mastery reflects the actual session, not optimism.
- Keep IDs and filenames stable once assigned. If a concept is renamed, keep the number
  and update the slug everywhere it is referenced.
- Keep summaries in sync. Regenerate subject and root summaries after every discussion
  and whenever lessons are added or restructured.
- Keep the changelog honest. When library content or agent rules change on `main`, add a
  matching entry under `[Unreleased]` in `CHANGELOG.md`; never list personal learning
  progress there. See [agent-docs/release-policy.md](agent-docs/release-policy.md).
- ASCII by default; introduce other characters only when a concept genuinely needs them
  or an existing template already uses them.
- Do not commit or push unless the git policy allows it and the current task requires
  it.

---

## Quick references

- Author a lesson -> copy `templates/lesson-template.md` and follow Workflow B in
  [agent-docs/learning-workflows.md](agent-docs/learning-workflows.md).
- Record a discussion -> copy `templates/discussion-template.md` and follow Workflow C
  in [agent-docs/learning-workflows.md](agent-docs/learning-workflows.md).
- Resolve concept IDs and progress states using
  [agent-docs/repository-model.md](agent-docs/repository-model.md).
