# Seniority Bands

Every lesson in this library is tagged with a **seniority band**, and every subject
declares a **seniority baseline**. This page explains what the bands mean and how to use
them to plan what to study. The authoritative rules the agent follows live in
[agent-docs/seniority-model.md](agent-docs/seniority-model.md).

## Why seniority is tagged

The same topic matters differently at different career stages. A junior engineer needs to
*use* a load balancer correctly; a staff engineer needs to reason about what a
service-boundary decision does to three teams over two years. Learning "system design" as
one undifferentiated pile hides that. The seniority tag tells you, for each concept, *whose
job it most naturally anchors* - so you can aim your study, not just wander a reading list.

Crucially, the band is **not reading difficulty**. A junior can read a staff-level lesson
and follow every word. The band answers a different question: at what level does this
concept become a load-bearing part of your day-to-day judgement?

## The five bands

| Band | Anchors the work of | The concept is mostly about |
| --- | --- | --- |
| **junior** | Early-career IC (~0-2y) | Using and understanding a thing correctly - what it is, how it works, applying it in the small. Usually a clear right answer. |
| **mid** | Solid IC (~2-5y) | Choosing between known options and applying them well across a feature or service; first-order trade-offs. |
| **senior** | Senior IC (~5y+) | Owning the non-obvious trade-offs: failure modes, when NOT to use it, designing a component end-to-end. |
| **staff** | Staff IC / tech lead | Cross-system and cross-team consequences, second-order effects, migration and evolution, org-shaped technical decisions. |
| **principal** | Principal / distinguished / eng leadership | Strategy, org-wide leverage, measuring value, and judgement under deep uncertainty. Payoff measured in outcomes, not code. |

They are ordered: `junior < mid < senior < staff < principal`.

## How to use the bands

- **Find your level, then stretch one up.** Study comfortably at your band to consolidate,
  and reach one band higher to grow. The discussion (below) is where the stretch happens.
- **A subject's baseline is a quick filter**, but read the per-lesson column: most books
  span several bands. *Clean Code* is mostly `junior`/`mid` but has `senior` chapters;
  *The Hard Parts* is mostly `senior`/`staff` but opens with accessible foundations.
- **Ask the agent to filter by band**: *"show me the senior-level system-design topics"* or
  *"what staff-level lessons haven't I discussed?"*

## The band changes the discussion, not just the label

When you discuss a lesson, the agent scales its Socratic questioning to the lesson's band:

- **junior** - it checks you can explain the mechanism and apply it correctly.
- **mid** - it makes you choose between named alternatives and justify first-order
  trade-offs.
- **senior** - it pushes on failure modes and *when not to*; the applied scenario has no
  clean answer.
- **staff** - it asks what breaks across teams and over time, and throws in conflicting
  constraints.
- **principal** - it interrogates strategy, leverage, and how you'd *measure* that a call
  was right, sitting with the ambiguity instead of resolving it.

Your mastery rating is judged against the lesson's own band: `solid` on a `junior` lesson
means solid junior-level command. When you reach beyond (or fall short of) the band, the
discussion record says so.

## Where you see it

- **Subject `README.md`** - a *Seniority* column per concept, plus a baseline line under
  the source book.
- **Lesson front matter** - a `seniority:` field.
- **The catalog** - when you ask what to study, bands are shown next to each topic.

While a subject is only *scaffolded* (its concept list exists but the deep lesson bodies
are not written yet), the per-lesson bands are provisional estimates and the subject
baseline is the reliable signal; each lesson's band is finalized when its body is authored.
