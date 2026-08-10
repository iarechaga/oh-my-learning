---
id: pragmatic-programmer/02
subject: pragmatic-programmer
title: Software Entropy and the Broken-Windows Theory
slug: software-entropy
status: drafted
mastery:
seniority: junior
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 1
prerequisites: [pragmatic-programmer/01]
created: 2026-08-10
updated: 2026-08-10
---

# Software Entropy and the Broken-Windows Theory

## TL;DR
Codebases decay the same way neighborhoods do: one unaddressed "broken window" (a hack, a failing test left ignored, bad naming) signals that nobody cares, which invites more of the same, and quality collapses faster than the sum of the individual problems would suggest. Fix small problems immediately, or at minimum contain them, to stop the spiral.

## The idea
"Software entropy" borrows the physics idea that closed systems drift toward disorder unless energy is spent maintaining order. Code doesn't get messier because messiness is inevitable — it gets messier because nobody actively resists the drift, and the drift is self-reinforcing.

The mechanism behind that reinforcement is the **broken-windows theory**, borrowed from criminology (Wilson & Kelling's research on urban decay): a building with one broken window that stays unrepaired soon has more broken windows, then graffiti, then squatters — not because the building got structurally weaker, but because the visible neglect changed what looked acceptable to everyone around it. Nobody decided to trash the building; the absence of care removed the social cost of doing so.

The same happens in code. A developer who finds an already-messy function feels no guilt adding one more `if` branch to the pile — the mess gives implicit permission. A developer looking at pristine, well-tested code feels real friction about being the one to introduce the first hack. The state of the code itself is a signal that shapes future behavior, independent of any written standard.

## How it works

### The decay loop
```
One shortcut lands unnoticed/unfixed
        |
        v
Code "looks" lower quality  ---->  Next developer's bar for care drops
        ^                                        |
        |                                        v
More shortcuts land, faster  <----  Norm becomes "this is just how it is"
```
Each pass through the loop is cheap individually — one more untyped parameter, one more copy-pasted block, one more `// TODO: fix later` that's never revisited — but the loop compounds. This is why codebases often feel like they degrade in a step function ("it was fine, then suddenly it was unmanageable") rather than smoothly: the loop has a tipping point where the norm flips from "we keep this clean" to "nobody keeps this clean," and after that flip, deterioration accelerates.

### Two responses: fix it, or visibly contain it
The pragmatic response to a broken window is not always "stop and fix it fully right now" — sometimes that's disproportionate. The book offers two valid responses:
1. **Fix it.** If it's small (rename a variable, delete dead code, add the missing test), just do it as part of your current change. This is the cheapest point in the codebase's life to fix it — it only gets more expensive.
2. **Board it up.** If it's too large to fix right now, make the damage visible and contained rather than silently living with it: a `// TODO(name, ticket-id): this violates X, tracked in JIRA-123` comment, a tracked tech-debt ticket, or a loud test marked `@skip("flaky — see INFRA-42")` instead of just deleted. The goal is to prevent the *appearance* of "this is fine and intentional" — an unmarked problem reads as acceptable; a marked one reads as known and tracked.

**Worked example.** You're fixing a bug in a function and notice it has a parameter named `data` that's actually always a `UserSession`, plus a commented-out block of old logic from three refactors ago.
- Small, in scope, cheap: rename `data` to `session`, delete the dead block. Do it now, in the same commit — this is "fix it."
- If instead the function is 400 lines mixing three responsibilities and untangling it is a half-day job unrelated to your bug fix: don't silently ignore it either. Leave `// TODO(alice, TECH-88): split validation/persistence/notification concerns, see TECH-88` and file the ticket. That's "board it up" — it stops the next reader from assuming this is intentional design.

### Why "nobody will notice one more" is exactly the wrong intuition
The individually-rational move ("this one hack won't matter") is what makes the theory dangerous: it's true in isolation and false in aggregate. Every contributor to a decayed codebase, if asked, will usually say their own contribution was minor. The decay is never one person's fault and always everyone's fault a little — which is precisely why it needs an explicit norm ("we don't add broken windows, and we don't tolerate existing ones silently") rather than relying on individual judgment case by case.

### Applies beyond code
The same pattern governs test suites (one ignored flaky test invites more `@skip`s), CI health (one long-tolerated red build invites people to stop watching CI), and documentation (one stale doc invites nobody trusting docs, so nobody updates any of them). The lesson generalizes: **any signal of neglect lowers the bar for everyone who sees it next.**

## Pros
- Cheap early intervention prevents expensive late-stage rescue projects ("rewrite the whole module").
- Creates a self-reinforcing *positive* loop when applied consistently: clean code invites care, care keeps code clean.
- Gives a concrete, actionable heuristic ("would I let this window stay broken?") instead of a vague "write good code" directive.

## Cons
- Can tip into unproductive perfectionism or scope creep — "fixing" every window can turn a one-line bug fix into an unrelated refactor that blows up the PR and the review.
- Requires a team-wide norm to work; a single disciplined engineer surrounded by five who don't care cannot single-handedly stop the decay loop, and may burn out trying.
- "Boarding it up" only works if the tracked debt is actually revisited — an ignored TODO is functionally the same as an unmarked broken window, just with better paperwork.

## Alternatives
- **Scheduled "cleanup sprints"** — batch quality fixes into a dedicated period instead of continuously. Tends to fail in practice: entropy compounds between sprints faster than a periodic sprint can undo, and cleanup sprints are the first thing cut under deadline pressure.
- **Strict linting/formatting gates only** — enforce mechanical rules via CI. Useful and complementary, but catches only what's mechanically checkable (formatting, some smells); it does nothing for the deeper decay of bad abstractions, mixed responsibilities, or untracked complexity.
- **Code ownership with a strong owner** — assign a single accountable owner per module who has final say and personally maintains its quality bar. Effective but doesn't scale past the owner's bandwidth and creates a bus-factor risk.

## When to use it
Every single time you touch code and notice something wrong nearby, even if it's not what you came to fix. Also apply it proactively when reviewing PRs: treat "this introduces a new broken window" as a valid review comment on its own, independent of whether the PR's stated goal is achieved.

## When NOT to use it
Don't let "no broken windows" justify unbounded scope creep in a single change — a bug-fix PR that balloons into a drive-by refactor of unrelated code is harder to review and riskier to ship. When the fix is too large to do "now," the correct move is explicitly to board it up (ticket + comment), not to silently expand the current PR.

## Key takeaways / mental model
Ask, every time you notice a problem: *fix it now, or make the damage visible and tracked* — never the silent third option of leaving it unmarked. The state of the code is a message to the next person; make sure the message you're sending is "this is cared for," not "abandon hope."

## Self-check questions
1. Give an example of a "broken window" you've personally seen normalize further decay in a codebase you've worked in.
2. When is "board it up" the right call instead of "fix it now"? Give the deciding factor.
3. Why does the theory claim decay is a step function rather than gradual, and what practical implication does that have for when to intervene?
4. A teammate says "it's just one extra `any` type, it doesn't matter." Using this lesson, explain what's wrong with that reasoning even if they're individually correct that one `any` won't break anything.

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 1: "Software Entropy".
- James Q. Wilson & George L. Kelling, "Broken Windows," The Atlantic Monthly, 1982 (the original criminological theory).
