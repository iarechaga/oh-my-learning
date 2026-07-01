# Seniority Model

Load this file before assigning a lesson's seniority level, setting a subject's seniority
baseline, showing seniority in the lesson catalog, or calibrating a discussion to a
concept's level. This is the authoritative definition of the seniority track; the
learner-facing summary lives in the root [SENIORITY.md](../SENIORITY.md).

Seniority is a **controlled vocabulary**, exactly like `mastery`. Never invent bands
outside the five defined here, and never leave a lesson's `seniority` empty once its body
is authored.

## The five bands

Seniority measures *the level of engineer for whom a concept is a natural, load-bearing
part of the job* - not how hard the lesson is to read. A junior can read a staff-level
lesson; the band says whose day-to-day judgement the concept anchors.

| Band | Who it anchors | What the concept is for at this level |
| --- | --- | --- |
| `junior` | Early-career IC (0-2y) | Correctly using and understanding a thing: what it is, how it works, how to apply it in the small. Right-vs-wrong has a mostly clear answer. |
| `mid` | Solid IC (2-5y) | Choosing between known options and applying them well across a feature/service; understanding first-order trade-offs. |
| `senior` | Senior IC (5y+) | Owning non-obvious trade-offs within a system; knowing when-NOT-to and the failure modes; designing a component end-to-end. |
| `staff` | Staff IC / lead | Cross-system and cross-team consequences; ambiguity with no clean answer; second-order effects, migration/evolution, org-shaped technical decisions. |
| `principal` | Principal / distinguished / eng leadership | Strategy, org-wide leverage, measurement of value, and judgement under deep uncertainty; concepts whose payoff is measured in company outcomes, not code. |

Bands are ordered: `junior < mid < senior < staff < principal`.

## Assigning a lesson's seniority (per-lesson primary tag)

Each lesson carries exactly **one** `seniority` band in its front matter - its *center of
gravity*: the level at which this concept first becomes load-bearing. Assign it with this
rubric, in order:

1. **Who first *needs* this to do their job well?** Not who *can* learn it. Consistent
   hashing is learnable by a junior, but a mid/senior engineer is who actually reaches for
   it - tag by the latter.
2. **What kind of decision does the concept govern?**
   - Apply-it-correctly, one right answer -> `junior`.
   - Pick-the-right-known-option -> `mid`.
   - Own-the-trade-off / when-NOT-to / failure modes -> `senior`.
   - Cross-system, cross-team, second-order, evolution-over-time -> `staff`.
   - Org strategy, leverage, value measurement, deep ambiguity -> `principal`.
3. **Prefer the lower band on a genuine tie.** If a concept sits between two bands, tag the
   lower one and let the *discussion depth* (below) stretch upward. This keeps tags honest
   and avoids band inflation.
4. **Tag the concept, not the book's reputation.** A famous "senior" book still has
   junior-friendly foundational chapters; tag each lesson on its own merits.

Worked examples (illustrative, not binding):
- `clean-code/02` Meaningful names -> `junior` (apply-it-correctly craft).
- `system-design/06` DNS and load balancing -> `mid` (choose and apply known components).
- `hard-parts/11` The eight saga patterns -> `senior` (own distributed trade-offs).
- `building-microservices/17` Conway's law and teams -> `staff` (org-shaped technical
  decision).
- `technical-leadership/*` An Elegant Puzzle, Accelerate -> `staff`/`principal`
  (org leverage and measurement).

## Subject baseline

Each subject `README.md` states a **seniority baseline** - the *typical* band for the
subject as a whole (usually the median of its lessons, sometimes expressed as a short span
like `mid-senior` in prose only). The baseline is a navigation aid; the per-lesson tag is
the source of truth. When lessons span several bands, say so in one line ("ranges
junior->staff; baseline senior").

Where the baseline appears:
- Subject `README.md`: one line under the source book, e.g.
  `**Seniority baseline:** senior (lessons range mid->staff).`
- Domain `README.md` subjects table and the root docs may show the baseline per subject.

## Per-lesson seniority column in the subject index

The subject `README.md` concept table gains a **Seniority** column between `Concept` and
`Status`:

```
| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Meaningful names | junior | drafted | — | — | [lesson](lessons/01-...) | — |
```

While a subject is only *scaffolded* (concept list exists, lesson bodies not yet
authored), the per-lesson band is a **provisional estimate** and the column may read the
subject baseline or a best-guess band; finalize each lesson's band when its body is
authored. Always keep the subject baseline filled even in a scaffold.

## Calibrating the discussion to the band

Seniority is **functional**: it changes how the agent runs Workflow C. Scale the Socratic
questioning to the lesson's band (and adapt within a session if the learner clearly
over- or under-performs the band):

- `junior` - Probe correctness and mechanism. "What is it, how does it work, walk me
  through applying it here." One applied scenario with a mostly-clear right answer. Rebuild
  from fundamentals when they stumble.
- `mid` - Probe option-selection and first-order trade-offs. "Given these two approaches,
  which and why?" Expect them to compare named alternatives.
- `senior` - Probe trade-offs, failure modes, and **when NOT to**. Push on edge cases and
  operational consequences. The applied scenario should have no clean answer; make them
  defend a judgement call.
- `staff` - Probe cross-system and cross-team effects, second-order consequences, and
  evolution/migration. "What breaks in the org, not just the code? What does this look like
  in two years?" Challenge assumptions; introduce conflicting constraints.
- `principal` - Probe strategy, leverage, and measurement. "How would you know this was the
  right call? What's the company-level bet?" Accept and interrogate ambiguity rather than
  resolving to one answer.

The mastery verdict is still judged against the concept's own band: `solid` at `junior`
means solid junior-level command, not staff-level. Note in the discussion record when a
learner reaches beyond (or falls short of) the lesson's band.

## Non-negotiables

- Use only the five bands. Never leave `seniority` empty on an authored lesson.
- Tag by *whose job the concept anchors*, not by reading difficulty or book fame.
- Prefer the lower band on ties; let discussion depth stretch upward.
- Keep the subject baseline and the per-lesson tags consistent; when they drift, the
  per-lesson tags win and the baseline is re-derived.
- Seniority never fabricates progress: it describes the concept, independent of the
  learner's `mastery`.
