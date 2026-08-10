---
id: devops-handbook/07
subject: devops-handbook
title: Trunk-Based Development and Release Cadence
slug: trunk-based-release-cadence
status: drafted
mastery:
seniority: senior
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part III
prerequisites: [devops-handbook/04, devops-handbook/06]
created: 2026-08-10
updated: 2026-08-10
---

# Trunk-Based Development and Release Cadence

## TL;DR
Trunk-based development means every developer integrates into a single shared branch at least daily, keeping branches (if used at all) short-lived and small, instead of maintaining long-lived feature branches that diverge for weeks — because branch divergence is exactly the accumulated integration debt that turns merging into a painful, risky event.

## The idea
Long-lived feature branches feel safe in the moment — "I'll work in isolation until my feature is done, then merge it in" — but they quietly accumulate a debt: every day a branch stays unmerged, it drifts further from trunk, and every other change landing on trunk in the meantime is a change your branch doesn't know about yet. The debt comes due all at once at merge time, as conflicts and integration bugs that are hardest to diagnose precisely because they've been building invisibly for weeks. Trunk-based development's core argument, consistent with `devops-handbook/03`'s small-batch principle, is that this debt should never be allowed to accumulate in the first place — pay it continuously, in tiny daily installments, rather than in one large, unpredictable payment at the end.

## How it works

### The mechanism: short-lived branches, feature flags, and daily integration
Trunk-based development doesn't mean "never branch" — it means branches, when used, live for hours to a day or two at most, and merge back to trunk before diverging significantly. The technique that makes this compatible with building large, multi-week features is decoupling "code merged" from "feature complete": incomplete functionality is merged into trunk continuously, hidden behind a feature flag (introduced in `devops-handbook/06`) or simply not yet wired into the UI, so trunk always builds and passes tests even while a feature is only half-built.

**Worked example — building a multi-week feature on trunk.** A team is building a new checkout flow that will take three weeks. Under a long-lived-branch approach, all three weeks of work stays on a `feature/new-checkout` branch, diverging further from trunk daily, and merges back in one large, risky event at the end. Under trunk-based development, the same three weeks of work merges to trunk in small daily increments — day 1 adds a new (currently unused) database table behind a migration; day 3 adds a new API endpoint gated by a feature flag that's off in production; day 8 adds the new UI component, also flag-gated and invisible to real users; day 15 the flag flips on for internal testers only; day 21 it ramps to 100% of users. Every one of those merges is small, individually low-risk, and continuously validated by CI (`devops-handbook/05`) against everyone else's concurrent changes — there is no single "merge day" where three weeks of divergence collides at once.

### Why long-lived branches specifically damage the First and Second Ways
This connects directly to `devops-handbook/01`'s framing. Long-lived branches violate the First Way (flow) because work sitting unmerged on a branch is work-in-progress that isn't actually flowing toward the customer — it's stalled, exactly the kind of invisible WIP `devops-handbook/03` warns about. They also damage the Second Way (feedback) because a bug introduced on day 2 of a three-week branch isn't caught by CI running against trunk until the merge on day 21 — the feedback loop that should close in minutes instead takes weeks, by which point the engineer has lost the context needed to debug it quickly.

### Release cadence: decoupling deploy frequency from release-to-user frequency
Trunk-based development, combined with feature flags, lets an organization set its *internal* deployment cadence (how often code moves from trunk to production, potentially many times a day) completely independently from its *external* release cadence (how often new functionality becomes visible to users, which might still be weekly, aligned with marketing or a mobile app store review cycle). This is a genuinely useful, often-missed distinction: an organization doesn't have to choose between "we deploy constantly" and "we control the pace of user-facing change carefully" — trunk-based development plus flags gives you both simultaneously.

**Worked example.** A consumer app deploys to production 15 times a day (bug fixes, backend changes, infrastructure updates, and flag-gated feature code), but its product team only flips user-visible feature flags on a deliberate weekly cadence tied to a release-notes and support-readiness process. Engineering's deployment frequency (a DORA metric, `devops-handbook/16`) and the product's release cadence are two different numbers, measured and optimized separately.

### The discipline this requires
Trunk-based development is not free — it requires strong CI (`devops-handbook/05`) because a broken trunk blocks everyone, a team culture willing to write code that's safely incomplete-but-mergeable (behind flags, behind unused code paths), and enough test coverage that a daily merge doesn't require lengthy manual verification. Teams that adopt the trunk-based branching model without those supports typically end up with a chronically broken or barely-tested trunk, which is worse than a disciplined long-lived-branch workflow.

## Pros
- Eliminates the large, unpredictable "merge day" integration event by paying integration cost continuously in small increments.
- Keeps every engineer's work within a day of what everyone else is doing, dramatically shrinking the surface area of any single merge conflict or integration bug.
- Enables deployment frequency and user-facing release cadence to be controlled independently, giving both engineering speed and product control simultaneously.

## Cons
- Requires disciplined use of feature flags and incremental design (building features as a sequence of safely-mergeable increments), which is a real design skill some teams lack initially.
- A weak or slow CI pipeline makes trunk-based development actively worse than branching, because a broken trunk now blocks the entire team's daily integration, not just one branch.
- Feature-flag proliferation, if not actively managed (removing flags once a feature is fully rolled out), becomes its own form of technical debt and code complexity.

## Alternatives
- **GitFlow / long-lived feature and release branches** — the direct alternative this lesson argues against for most contexts; can make sense for shipping cadences genuinely tied to infrequent, hard release boundaries (e.g., embedded firmware with expensive physical distribution), but reintroduces integration risk proportional to branch lifetime for anything with a faster feedback loop available.
- **Short-lived feature branches with mandatory same-day merge** — a middle ground some teams use: still branch per change, but with a hard cultural/tooling rule that branches merge back within 24 hours, capturing most of trunk-based development's benefit while keeping a lightweight PR-review checkpoint.
- **Release branches cut from trunk at release time** — trunk stays the continuous integration point; a short-lived release branch is cut only at the moment of an actual release for final stabilization, combining trunk-based daily development with a controlled release-cut process.

## When to use it
Default to trunk-based development whenever your CI pipeline (`devops-handbook/05`) is fast and trustworthy and your team can invest in feature-flag discipline — this covers the large majority of modern web/service software.

## When NOT to use it
Don't adopt trunk-based development without first having a trustworthy, fast CI pipeline — you'll just turn "merge conflicts on a stale branch" into "a permanently broken shared trunk that blocks everyone," which is strictly worse. In contexts with a genuinely expensive, infrequent, and hard-to-reverse release mechanism (unavoidable in some embedded/regulated domains), a more structured release-branch model may still be the pragmatic choice.

## Key takeaways / mental model
Integration debt behaves like compound interest: the longer a branch diverges from trunk, the more expensive (and less predictable) the eventual merge becomes. Trunk-based development pays that debt in small daily installments instead of one large, risky lump sum — and feature flags are the tool that makes "merge incomplete work safely" possible.

## Self-check questions
1. Using the three-week checkout-flow example, explain specifically what makes each daily merge low-risk even though the overall feature isn't done yet.
2. Why does the lesson argue that a long-lived branch damages both the First Way (flow) and the Second Way (feedback), not just one of them?
3. Explain how trunk-based development plus feature flags lets an organization decouple deployment frequency from user-facing release cadence. Why is that distinction useful?
4. A team wants to adopt trunk-based development but their CI pipeline takes 45 minutes and fails intermittently about 15% of the time. What would you tell them to fix first, and what specifically goes wrong if they adopt trunk-based development anyway?

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part III: "The First Way: Technical Practices of Flow."
- See also: `devops-handbook/04` (version control everything), `devops-handbook/06` (deployment pipeline design, including feature-flag mechanics).
