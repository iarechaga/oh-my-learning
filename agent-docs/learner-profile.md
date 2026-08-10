# Learner Profile and Onboarding

Load this file before the **first interaction of a learning relationship**, at the
**start of every session**, and whenever the learner asks to change their name, how they
are addressed, their seniority, their goals, or how the agent should behave.

This is the authoritative workflow for getting to know the learner and keeping durable,
personal notes about them across many sessions. The notes live in **`LEARNER.md`** at the
repository root. `LEARNER.md` is **gitignored**: it is personal to one learner and must
**never** be committed to `main` (same rule as discussion records and progress - see
[git-policy.md](git-policy.md)). The copyable structure is
[templates/learner-profile-template.md](../templates/learner-profile-template.md).

The point: a learning track is personal. Before proposing what someone should study, the
agent must know **who they are**, **how they want to be treated**, **what level they
operate at**, and **what they actually want to learn** - and must remember all of it
between sessions so the learner never has to repeat themselves.

---

## Start of every session - read the profile first

At the very start of any session, before doing learning work:

1. **Make sure you are on a learner branch, not `main`.** If the current branch is `main`
   (or any shared branch), create and switch to a `learn/<slug>` branch yourself before
   anything else - the learner never has to run git commands. See the learner-branch rule
   in [git-policy.md](git-policy.md). (`LEARNER.md` is gitignored, but discussion records
   and progress edits must not land on `main`, so the branch comes first.)
2. Check whether `LEARNER.md` exists at the repo root.
   - **It exists** -> read it fully. Greet the learner by their preferred name, honor
     their stated tone/address and behavior preferences, and use their seniority (global
     band plus any per-subject override) to calibrate everything. Do **not** re-ask
     onboarding questions you already have answers to.
   - **It does not exist** -> this is a new learning relationship. Run **Workflow O -
     Onboarding** below before proposing or starting any learning path.
3. If the learner immediately asks to discuss a specific concept and no profile exists,
   you may run a lightweight onboarding first (at least name, how to be addressed, and
   seniority) rather than the full path proposal - but still create `LEARNER.md`. Never
   skip onboarding entirely just because the learner jumped straight in.

Reading the profile at session start is not optional; it is what makes the agent
consistent across sessions.

---

## Workflow O - Onboarding (first contact)

Trigger: the first interaction with a learner, or any session where `LEARNER.md` is
missing. Ask **one thing at a time** (same Socratic discipline as discussions - never
dump all questions at once), and write answers into `LEARNER.md` as you go.

Copy [templates/learner-profile-template.md](../templates/learner-profile-template.md) to
`LEARNER.md` first, then fill it through these steps.

### Step 0 - Set up the learner branch (before asking anything)
If the session is on `main` (or any shared branch), the agent **creates and switches to a
`learn/<slug>` branch itself** - the learner never runs git commands and onboarding never
happens on `main`. See the learner-branch rule in [git-policy.md](git-policy.md). Until you
know the learner's name, a placeholder like `learn/session` is fine; once they give their
preferred name in Step 1, you may rename the branch to `learn/<their-name>` (e.g.
`git branch -m learn/alex`) or simply keep the placeholder - either is acceptable. This is
a non-destructive setup step; do it automatically without asking.

### Step 1 - Name and how to be treated (personalization)
Ask the learner:
- their **name**, and **what they would like to be called** (name or nickname);
- **how they would like to be treated** - tone and formality (e.g. casual and direct,
  or formal), and any communication preference (terseness, language, hint style).

Record these in the **Identity and address** and **Behavior preferences** sections. From
this point on, address and treat the learner exactly as recorded, in every session.

### Step 2 - Seniority level
Ask the learner for their **seniority level**, framed by whose job a concept anchors
rather than years alone. Offer the five bands so the answer is concrete:
`junior` / `mid` / `senior` / `staff` / `principal` (see
[seniority-model.md](seniority-model.md) for what each band means).

- **If the learner states a clear band** -> record it as the **global self-rated band**
  and mark it `self-reported`.
- **If the learner is unsure** -> run **Step 2a - Brief seniority assessment** to
  estimate it. Do not force a number on them and do not skip it: a proposed path needs a
  clear-enough level.

Also capture, if it comes up, that the learner is a **different level in different
areas** (e.g. senior at backend, junior at distributed systems). Record those as
**per-subject / per-domain overrides**; the global band is the default and overrides
apply where stated.

### Step 2a - Brief seniority assessment (only if the learner is unsure)
Keep it short and respectful - this is a calibration, not an exam. Ask **2-4** targeted
questions and infer the band from the *kind* of answer, using the rubric in
[seniority-model.md](seniority-model.md):

1. Ask about a topic in (or near) the area they want to learn. Start mid-level and adjust.
2. Judge by decision-type, not vocabulary:
   - explains *what a thing is and how to apply it*, one clear right answer -> `junior`;
   - *chooses between known options* and reasons about first-order trade-offs -> `mid`;
   - *owns non-obvious trade-offs, failure modes, and when-NOT-to* -> `senior`;
   - reasons about *cross-system/cross-team, second-order, and evolution-over-time*
     effects -> `staff`;
   - reasons about *strategy, org leverage, and measuring value* under deep ambiguity
     -> `principal`.
3. Prefer the **lower band on a genuine tie** (same rule as lesson tagging).
4. Tell the learner your estimate, briefly say why, and let them correct it - their
   correction wins.

Record the outcome as the global band, mark it `agent-assessed on <date>`, and write the
evidence into **Assessment notes** so a later session does not re-guess.

### Step 3 - Goals and concerns
Ask what they **want to learn about and why** - the concern that brought them here (a
role they are preparing for, a weak area, a book they want to work through). Capture:
- their goal in their own words;
- target subjects/domains, if they know them;
- any constraints (time, deadline, job context);
- anything they explicitly do **not** want to focus on right now.

Record in **Goals and concerns**. A learning path cannot be proposed without this.

### Step 4 - Propose a learning path (gated)
Only propose a path once **both** are true:
- the **seniority level is clear enough** (self-reported or assessed), and
- the learner's **goals/concerns are known**.

If either is missing, go back and get it first - do not guess a path.

When both are known:
1. Use the catalog (see [learning-workflows.md](learning-workflows.md), Workflow C0) to
   find subjects/concepts that match the learner's goals, pitched to their band (a lower
   band may start with foundational lessons to build confidence; a higher band may skip
   ahead to trade-off-heavy concepts). Concretely: read each candidate subject's
   `README.md` concept table (not the lessons themselves yet) for `seniority` and
   `prerequisites`, and keep only concepts that (a) match the learner's stated goal/target
   subjects, (b) fall within the learner's band ±1 (a `senior` learner may reasonably start
   at `mid` or reach into `staff`), and (c) respect prerequisite order (a concept cannot
   precede an unresolved prerequisite on the list). The track is scoped to the goal, not
   the whole repo - it is normal for it to cover a handful of subjects out of the many
   available, and it can be expanded later (see Workflow P in
   [progress-tracking.md](progress-tracking.md)).
2. Propose an **ordered path** with a one-line reason per step, respecting prerequisites
   and dependency order.
3. Present it and **let the learner accept or adjust** - do not start quizzing until they
   agree on a starting point.
4. Record the path and its status (`proposed` / `accepted` / `revised`, with dates) in
   **Proposed learning path**.
5. Once accepted, write the same ordered list as a **structured track** in `PROGRESS.md`
   at the repo root: copy [templates/progress-template.md](../templates/progress-template.md)
   if the file does not exist yet, fill **Track goal** and the **Track** table (one row per
   accepted step, `Track status: queued`, first row `current`, one-line **Reason** per row
   from step 2 above), and render **Next up** from the first few rows. See
   [progress-tracking.md](progress-tracking.md) for the full schema and the regeneration
   rule - load that file before writing or updating `PROGRESS.md`. `PROGRESS.md` follows
   the same branch/commit rules as `LEARNER.md` (never on `main`; see
   [git-policy.md](git-policy.md)), except it **is** committed on the learner's own
   branch/fork (unlike `LEARNER.md`, which stays gitignored).

### Step 5 - Confirm and save
Briefly reflect back what you recorded (name, how they will be addressed, level, goals,
proposed path) so the learner can correct anything, then save `LEARNER.md`. Add a
one-line entry to **Session history**.

---

## Keeping the profile current (updates)

The profile is a **living document**. Update `LEARNER.md` immediately - in the same
session, the moment it happens - whenever:

- The learner asks to **change how they are addressed or treated** (name, nickname, tone,
  formality, hint style, pacing, language). Update **Identity and address** /
  **Behavior preferences**, and log the change with its date in the profile's
  **Change log**. From then on, behave the new way consistently, every session.
- The learner's **seniority changes** - they revise their self-rating, ask to be treated
  as a different level, or their performance across sessions clearly warrants it. Update
  the global band or the relevant per-subject override, note why (and the evidence if you
  raised/lowered it from observed performance), and log it in the **Change log**.
- Their **goals or concerns shift** - update **Goals and concerns** and, if needed,
  re-propose the path (Step 4) and record the revision.
- A **session happens** - add a one-line **Session history** entry (what was covered,
  mastery outcome, or what changed) so the next session has continuity.

When a behavior or seniority change is requested, treat it as authoritative: the learner's
current preference always overrides an older note. Never keep treating a learner the old
way after they have asked for a change.

---

## Non-negotiables

- **Onboard before advising.** Never propose or start a learning path for a new learner
  before capturing name, how they want to be addressed, seniority (clear enough), and
  goals. If the learner is unsure of their level, briefly assess it - do not skip it.
- **Read `LEARNER.md` at the start of every session** and act on it - address and treat
  the learner as recorded, and calibrate to their band. Do not make them repeat
  themselves.
- **One question at a time** during onboarding and assessment, exactly as in a discussion.
- **Write it down and keep it consistent.** Every relevant fact and preference goes into
  `LEARNER.md`; behave the same way across all sessions until the learner changes it.
- **Update on change, immediately.** When the learner changes their name, address, tone,
  behavior preference, seniority, or goals, update the profile in the same session and log
  it; then honor the change from that point on.
- **The profile is personal.** `LEARNER.md` stays gitignored and never lands on `main`
  (see [git-policy.md](git-policy.md)); it is never listed in `CHANGELOG.md`.
- **Never fabricate.** Record only what the learner told you or what a stated assessment
  concluded; leave unknowns as `unknown` rather than guessing.
