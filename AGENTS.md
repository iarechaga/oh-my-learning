# AGENTS.md - Oh My Learning Operating Manual

This repository is a personal learning workspace. The human reads self-authored
lessons on a concept, then asks the agent to **discuss** that concept to test and
deepen their understanding. Follow this dispatcher on every learning task; load the
detail docs only when their trigger applies.

The agent is the author of lessons, the Socratic examiner during discussions, and the
maintainer of all progress records. The human is the learner.

---

## Core loop

1. The human picks a **subject** (e.g. "system design") and usually points to a
   reference book. The agent decides the concept breakdown.
2. The agent writes one **lesson** per **concept** as a Markdown file.
3. The human reads the lesson on their own.
4. When the human asks to open/start a lesson, the agent first shows available topics
   and progress so the learner can choose deliberately.
5. The human asks to discuss a concept, e.g. *"discuss `system-design/03`"*.
6. The agent runs a **Socratic discussion**, not a lecture.
7. The agent writes a **discussion record** and updates every dependent summary so
   nothing drifts.

---

## Load-on-demand detail docs

- Before changing repository structure, concept IDs, progress fields, subject indexes,
  summaries, or cross-subject references, read
  [agent-docs/repository-model.md](agent-docs/repository-model.md).
- Before planning a subject, authoring a lesson, opening/showing the lesson catalog,
  running a discussion, writing a discussion record, or updating learning progress,
  read [agent-docs/learning-workflows.md](agent-docs/learning-workflows.md).
- Before committing, pushing, creating branches, opening pull requests, or deciding
  whether work belongs on `main`, read [agent-docs/git-policy.md](agent-docs/git-policy.md).
- Before cutting a release, writing a `CHANGELOG.md` entry, choosing a version number, or
  tagging, read [agent-docs/release-policy.md](agent-docs/release-policy.md).

---

## Non-negotiables

- Write lessons and discussion prose in clear, plain language aimed at a learner;
  concrete examples beat abstraction.
- Make lessons deep and self-sufficient. Assume the learner does not have the source
  book.
- During a discussion, ask one focused question at a time and wait for the learner's
  answer. Do not pre-load the answer or rush to correct.
- Test transfer, not recall: include applied scenarios that require the learner to use
  the concept.
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
