---
id: staff-engineer/10
subject: staff-engineer
title: Partnering effectively with engineering managers and peers
slug: partnering-with-managers
status: drafted
mastery:
seniority: staff
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 6 and material on staff/EM partnership
prerequisites: [staff-engineer/07, staff-engineer/08]
created: 2026-08-10
updated: 2026-08-10
---

# Partnering effectively with engineering managers and peers

## TL;DR
A staff engineer and an engineering manager cover complementary halves of the same team or domain (technical direction versus people, process, and delivery), and the partnership only works if both sides actively divide responsibility, communicate constantly, and avoid either duplicating or leaving gaps in the other's territory — an unclear staff/EM boundary is one of the most common sources of team dysfunction at this level.

## The idea
The Tech Lead archetype (`staff-engineer/02`) is explicitly paired with an engineering manager by design: the EM owns people management, performance, hiring, process, and delivery commitments; the staff engineer owns technical direction, architecture, and unblocking hard technical problems. This division exists because both halves require real, different expertise, and the same person doing both well, at scale, is rare and difficult to sustain — which is exactly why companies split senior IC and management into separate ladders in the first place.

But splitting responsibility on paper doesn't automatically make the partnership work in practice. If the boundary is unclear, both territory gaps (neither person owns a decision, so it doesn't get made) and territory overlaps (both people weigh in inconsistently, confusing the team about who to listen to) are common failure modes — and they're more damaging than either problem alone, because they erode the team's trust in the leadership structure itself.

## How it works

### Dividing responsibility explicitly
Larson's practical recommendation is to make the division explicit rather than assuming it's obvious — a short, direct conversation ("here's what I see as my lane, here's what I see as yours, does that match your read?") between a new staff/EM pairing avoids months of quiet friction. A reasonable default split:
- **EM owns:** performance management, hiring and team composition, career growth conversations, sprint/delivery process, cross-team commitments about *when* things will ship.
- **Staff engineer owns:** architecture and technical direction, technical risk assessment, code quality standards, *how* things get built and in what technical sequence.
- **Shared, requiring active coordination:** prioritization (the EM knows delivery pressure and team capacity; the staff engineer knows technical risk and sequencing — a good prioritization call needs both), and anything involving a team member's technical growth (career growth is the EM's territory, but the staff engineer often has the clearest picture of that engineer's technical trajectory and should feed it in, not decide it unilaterally).

### Communicating constantly, not just at scheduled syncs
Because the two roles' decisions constantly affect each other — a technical risk the staff engineer identifies changes what the EM can safely commit to; a delivery deadline the EM negotiates changes what technical shortcuts the staff engineer needs to plan for — a good staff/EM partnership typically involves frequent informal communication (a standing weekly sync at minimum, plus ad hoc check-ins), not just occasional coordination when a conflict forces it. Pairs that only talk when there's already a problem tend to discover misalignment after it's already visible to the team, which is more costly to repair than catching it privately first.

### Presenting a unified front to the team
Even when a staff engineer and EM privately disagree (which is healthy and expected — different expertise should sometimes produce different initial opinions), surfacing that disagreement unresolved in front of the team creates confusion about who the team should actually listen to, and can let team members implicitly "shop" for whichever answer they prefer. The practice Larson recommends: hash out disagreements privately first, and if a decision needs to go to the team while genuine disagreement remains, present it as an open question with both perspectives named explicitly, rather than each leader informally undermining the other's position in separate conversations with different team members.

**Worked example.** An EM wants to commit to a customer deadline that the staff engineer believes requires cutting a testing corner they consider risky. Poor handling: the EM commits to the deadline in a leadership meeting without checking with the staff engineer first; the staff engineer, blindsided, tells the team afterward that the deadline "isn't realistic if we want to do this safely" — now the team has two contradictory signals from its two leaders and doesn't know which to trust. Better handling: the EM checks with the staff engineer before committing; they agree between themselves either that the risk is acceptable given the business context (and the staff engineer commits to that framing when talking to the team) or that the deadline needs to move (and the EM takes that back to leadership) — the team hears one aligned message either way, even though the underlying negotiation involved real disagreement.

### Partnering with peer staff engineers, not just EMs
The same dynamics — explicit division of territory, frequent communication, unified front where it matters — apply to relationships with peer staff-plus engineers on adjacent teams or domains, especially where scope overlaps (two staff engineers whose domains touch at a shared service boundary). The specific failure modes differ slightly: peer staff engineers are more prone to duplicated, uncoordinated effort (see the seams discussion in `staff-engineer/03`) than to the people-vs-technical-territory confusion specific to staff/EM pairs, but the underlying fix — an explicit conversation about who owns what, and a standing communication rhythm — is the same.

### When the partnership breaks down
The most common breakdown pattern is an EM and staff engineer who simply don't talk enough, so misalignment silently accumulates until it surfaces as a visible, embarrassing disagreement in front of the team or leadership. The fix is rarely a personality issue requiring a personnel change — usually it's a structural fix: schedule the standing sync that wasn't happening, and have the explicit territory conversation that was assumed rather than actually had.

## Pros
- Lets both technical direction and people/delivery management get real, dedicated expertise instead of being handled adequately-but-not-excellently by one overloaded person.
- A well-functioning staff/EM pair gives the team a clear, consistent signal about both what to build and how the team operates, rather than ambiguity about who's in charge of what.
- Builds exactly the kind of cross-functional trust and communication habit that scales into the broader influence network described in `staff-engineer/07`.

## Cons
- Requires real, ongoing communication investment from both sides — a pairing that's technically well-divided on paper but doesn't talk enough in practice degrades quietly.
- Ego and territoriality can undermine the division even when both people intellectually agree with it — a staff engineer who quietly resents not having formal authority over people decisions, or an EM who second-guesses technical calls without the depth to fully evaluate them, both erode the partnership.
- A strong staff engineer paired with a weak EM (or vice versa) creates real strain, because the weaker half's gaps don't get automatically covered — the team feels the gap directly.

## Alternatives
- **A single tech-lead-manager (TLM) role combining both functions** — some smaller teams or earlier-stage companies use one person for both people and technical leadership; works at small scale, but is widely considered hard to sustain well past a certain team size, which is exactly why Larson's staff-plus track exists as an alternative to forcing everyone senior into a hybrid TLM role.
- **Fully independent, uncoordinated staff and EM roles** — the anti-pattern this lesson is warning against; included here only as the "what not to do" default when no explicit coordination effort is made.
- **A rotating or matrixed technical-lead role** (different engineers take technical lead responsibility for different projects, without one fixed staff/EM pairing) — can work for a team without a dedicated staff engineer, but loses the continuity and deep context a fixed pairing builds over time.

## When to use it
Apply deliberate territory-division and communication practices any time you're in a fixed pairing with an EM (most commonly in the Tech Lead archetype) or with a peer staff engineer whose scope regularly overlaps yours — set the explicit conversation up early in the relationship, not after the first visible conflict.

## When NOT to use it
Don't over-formalize the division for a very small team or a short-lived collaboration where the overhead of explicit territory-mapping exceeds the coordination risk it's meant to prevent — a two-person effort lasting three weeks probably just needs a quick conversation, not a documented RACI.

## Key takeaways / mental model
Picture the staff/EM pair as two hands on one steering wheel: each hand needs to know which turns it's responsible for, they need to talk to each other constantly (not just when the car is already swerving), and the passengers (the team) need to see one coordinated set of hands on the wheel, not two hands fighting each other in front of them.

## Self-check questions
1. If you're in (or can observe) a staff/EM pairing, can you state clearly which decisions are the EM's, which are the staff engineer's, and which are genuinely shared? If you can't state it clearly, what does that suggest about the pairing's health?
2. In the worked deadline-versus-testing-risk example, what specifically made the "poor handling" version damaging to the team, beyond the underlying disagreement itself being reasonable on both sides?
3. Why does Larson recommend hashing out disagreements privately before presenting a decision to the team, rather than modeling open disagreement transparently in front of the team? What's the trade-off being made there?
4. How does the staff/EM territory-division problem differ from the peer-staff-engineer territory-division problem? What's the shared underlying fix for both?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 6 and the discussion of Tech Lead / engineering-manager partnership throughout the book.
