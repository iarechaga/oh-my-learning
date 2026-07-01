<!--
LEARNER PROFILE - personal, per-learner notes the agent keeps across sessions.

This file is the agent's memory of WHO the learner is and HOW to work with them.
Copy it to LEARNER.md at the repo root on first contact, then keep it updated.
LEARNER.md is gitignored: it is personal and must never be committed to `main`.
Fill every [bracketed] field from what the learner tells you (or from a brief
assessment). Never invent facts; leave a field as `unknown` until you truly know it.
See agent-docs/learner-profile.md for the workflow that maintains this file.
-->

# Learner Profile

**Last updated:** [YYYY-MM-DD]

## Identity and address
- **Name:** [what the learner gave]
- **Prefers to be called:** [name / nickname they chose]
- **How to address them:** [tone + form they asked for, e.g. "casual, first name, direct" / "formal, no nicknames"]
- **Language / notes on communication:** [any stated preference, e.g. "explain in Spanish sometimes", "keep it terse", or `unknown`]

## Seniority
- **Global self-rated band:** [junior | mid | senior | staff | principal | unknown]
- **How this was set:** [self-reported | agent-assessed on YYYY-MM-DD | unknown]
- **Per-subject / per-domain overrides** (only where it differs from the global band):
  - [subject-or-domain]: [band] - [one-line reason, e.g. "strong backend, new to distributed systems"]
  - [subject-or-domain]: [band] - [reason]
- **Assessment notes** (if the band was estimated, capture the evidence so it is not re-guessed next time):
  - [what was asked, how they answered, what it implied about the band]

## Goals and concerns
- **What they want to learn / why:** [their stated concern, in their words]
- **Target subjects/domains:** [e.g. "system design for an upcoming role", "DDD fundamentals"]
- **Constraints / context:** [time, deadline, job context, or `unknown`]
- **Explicitly NOT interested in (for now):** [topics to deprioritize, or `none`]

## Proposed learning path
<!-- Only fill this once seniority is clear enough AND goals are known. Ordered, with reasons. -->
- **Status:** [not yet proposed | proposed on YYYY-MM-DD | accepted on YYYY-MM-DD | revised on YYYY-MM-DD]
- **Path:**
  1. [subject/NN or subject] - [why this, at this point, for this learner]
  2. [subject/NN or subject] - [why]
  3. [subject/NN or subject] - [why]

## Behavior preferences (how the agent should act with this learner)
<!-- Durable instructions for the agent. Update the moment the learner asks to change any of these. -->
- **Discussion pacing:** [e.g. "one question at a time, slow" / "push hard, stack follow-ups"]
- **Hint style:** [e.g. "let me struggle, minimal hints" / "give hints quickly"]
- **Depth vs breadth:** [e.g. "go deep on fewer topics" / "broad coverage first"]
- **Other standing preferences:** [anything else they asked for, or `none`]

## Session history (brief)
<!-- One line per session touchpoint so future sessions have continuity. Newest last. -->
- [YYYY-MM-DD] - [what happened: onboarding done / discussed subject/NN -> mastery / path revised / preference changed]

## Change log for this profile
<!-- Record every change the learner requests to seniority, address, or behavior, with the date. -->
- [YYYY-MM-DD] - [what changed and why, e.g. "learner asked to be addressed formally", "raised global band mid -> senior after strong sessions"]
