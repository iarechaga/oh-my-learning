---
id: devops-handbook/03
subject: devops-handbook
title: Small Batch Sizes and Limiting Work in Process
slug: small-batches-wip-limits
status: drafted
mastery:
seniority: mid
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part II
prerequisites: [devops-handbook/02, phoenix-project/04]
created: 2026-08-10
updated: 2026-08-10
---

# Small Batch Sizes and Limiting Work in Process

## TL;DR
Shipping work in small batches (a handful of commits, not months of accumulated changes) and capping how much work is in progress at once (WIP limits) both reduce lead time and reduce risk per change, because small batches are easier to test, easier to review, easier to roll back, and don't sit queued behind unrelated work.

## The idea
`phoenix-project/04` dramatized the cost of multitasking and unbounded WIP: Brent becomes a bottleneck partly because too many projects are "in flight" at once, each one stealing his attention from the others and none of them finishing. This lesson gives the same insight a delivery-pipeline lens: batch size is a lever most teams don't realize they're pulling. A "batch" is the unit of work that moves through the pipeline together — a single commit, a week's worth of changes, or (in the worst case) an entire quarter's release bundled into one deploy. Batch size and WIP are related but distinct: batch size is how much work moves together through one pass of the pipeline; WIP is how many separate units of work are open simultaneously across the team.

## How it works

### Why big batches slow everything down, not just make it riskier
Large-batch, infrequent releases feel efficient — "let's bundle everything and deploy once" seems like it saves overhead. In practice it does the opposite, for reasons lean manufacturing identified long before software: as batch size grows, queue time grows non-linearly (queuing theory: wait time increases sharply as utilization approaches capacity, and big batches keep resources busy longer per unit, pushing utilization up), and the cost of finding and fixing a defect grows because there are more changes to search through when something breaks.

**Worked example.** Compare two teams shipping the same total amount of code over a month.
- Team A batches into one release at month-end: 200 commits go out together. When production breaks, the failure could be caused by any of 200 changes from many different engineers — triage takes hours because there's no small, recent, reviewable diff to suspect first.
- Team B ships continuously, ~10 commits/day. When production breaks, the on-call engineer checks what deployed in the last 20 minutes — usually 1-3 commits — and has a strong first suspect immediately. Team B's mean time to resolution is minutes, not hours, purely because of batch size, with no difference in code quality between the teams.

### Why unbounded WIP silently destroys throughput
This is the multitasking cost from `phoenix-project/04` made quantitative. Classic result: an engineer working on 1 task at a time might spend 100% of their effective time on that task; splitting attention across 2 simultaneous tasks (context-switching overhead) can cost 20-40% of total capacity to the switching itself, not to either task; by 5 simultaneous tasks, more time can go to switching than to any actual work. WIP limits (a Kanban board with an explicit "max 3 items in progress" column cap) force the team to *finish* before *starting more*, which sounds obviously right but is routinely violated because starting new work feels more productive in the moment than finishing existing work.

**Worked example.** A platform team has 8 engineers and 12 projects nominally "in progress." Nothing finishes for months because everyone is spread across 3-4 projects each. Imposing a WIP limit of "no more than 1.5 projects per engineer, cap total in-progress projects at 5" forces 7 projects to sit explicitly in a backlog instead of silently stalling in progress. Counter-intuitively, throughput (projects actually completed per quarter) goes *up*, because the 5 in-progress projects now get focused attention and finish, rather than 12 projects each inching forward and none finishing.

### Applying small batches to the deployment pipeline specifically
Concretely, small-batch delivery means: commit and integrate frequently (feeding into `devops-handbook/04` and `devops-handbook/05`), deploy on a cadence measured in hours/days rather than weeks/months, and use feature flags to decouple "merged to trunk" from "visible to users" so a small code batch can ship even when the *feature* it's part of isn't done yet (this connects directly to `devops-handbook/07`'s trunk-based development).

### The trade-off: batch size floor
Batch size can't shrink to zero — there's real per-deployment overhead (spinning up a deploy, running a full test suite, a canary observation window) that doesn't scale down with batch size. The Handbook's answer isn't "always minimize batch size" but "shrink batch size until the fixed per-batch overhead, not the batch content, is the limiting cost" — and then invest in reducing that fixed overhead (faster pipelines, cheaper deploys) so batch size can shrink further.

## Pros
- Smaller batches mean smaller, more reviewable diffs, faster root-cause triage when something breaks, and cheaper rollback.
- WIP limits convert invisible multitasking cost into a visible, deliberately-managed queue, which increases actual throughput even though it feels like doing less.
- Both practices shorten feedback loops (Second Way, `devops-handbook/01`) — smaller batches surface problems closer to the change that caused them.

## Cons
- Requires pipeline investment (fast automated tests, fast deploys) to make small, frequent batches practical — without that investment, small batches just mean more manual overhead more often.
- WIP limits can feel like an artificial constraint to stakeholders used to "just start everything now, we'll get to it," and enforcing them requires organizational buy-in to say no to new work starting.
- Batch size can be shrunk past the point of diminishing returns if per-deployment fixed costs aren't also addressed — ultra-small batches on a slow pipeline just means paying the fixed cost more often for less benefit each time.

## Alternatives
- **Large, scheduled release trains** — appropriate in some regulated or hardware-coupled contexts where the deployment mechanism itself is expensive or infrequent by necessity (e.g., firmware shipped to physical devices); the direct alternative this lesson argues against for typical software delivery.
- **Kanban's explicit WIP-limited board** — the concrete team-process mechanism for enforcing WIP limits day-to-day; this lesson covers *why* WIP limits matter, Kanban is one *how*.
- **Scrum sprint-boxing** — bounds WIP indirectly via sprint capacity and story-point commitment rather than an explicit column limit; can achieve similar effect but is easier to game by overcommitting a sprint.

## When to use it
Default to small batches and explicit WIP limits whenever your pipeline can support frequent integration and deployment (see `devops-handbook/05`, `devops-handbook/06`) — which is the large majority of modern software delivery contexts.

## When NOT to use it
Don't force artificially tiny batches where the fixed cost per deployment is still high and unaddressed (a 4-hour manual regression suite makes daily micro-deploys worse, not better, until that cost is automated away) — fix the fixed cost first, or accept a larger interim batch size. Also don't impose WIP limits without giving the team the authority to actually say no to new incoming work — a WIP limit that's routinely overridden by management pressure isn't a real constraint, just decoration.

## Key takeaways / mental model
Batch size and WIP are levers, not fixed facts about how software must be delivered. Shrinking batch size shortens the blast radius and diagnosis time of every failure; capping WIP converts invisible context-switching cost into visible throughput gains. Both trade a feeling of "doing more at once" for actually finishing more.

## Self-check questions
1. Using the queuing-theory intuition from this lesson, explain why doubling batch size more than doubles expected lead time, rather than just doubling it.
2. A team wants to cut deploy batch size from weekly to daily but their manual QA process takes 6 hours per release. What has to happen first, and why would skipping that step make daily deploys worse rather than better?
3. Your manager asks you to also "just quickly start" a new urgent project on top of your team's already-full WIP limit. Using this lesson's reasoning, what's the actual throughput cost of agreeing, even though it "feels" reasonable to just add one more thing?
4. How does small-batch delivery specifically support the Second Way (fast feedback, `devops-handbook/01`) beyond just being "faster" in a generic sense?

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part II: "Where to Start."
- See also: `phoenix-project/04` (WIP limits and multitasking damage) and `devops-handbook/02` (value stream mapping, for identifying where batch size is inflating lead time).
