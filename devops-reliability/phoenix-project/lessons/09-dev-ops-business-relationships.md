---
id: phoenix-project/09
subject: phoenix-project
title: Changing Relationships Between Development, Ops, and Business
slug: dev-ops-business-relationships
status: drafted
mastery:
seniority: staff
source: The Phoenix Project (Kim, Behr, Spafford), Part 3
prerequisites: [phoenix-project/05, phoenix-project/06, phoenix-project/07]
created: 2026-08-10
updated: 2026-08-10
---

# Changing Relationships Between Development, Ops, and Business

## TL;DR
Parts Unlimited's crisis is sustained by a structural, adversarial split: Development is measured on shipping features fast, Operations is measured on stability and uptime, and the business treats both as interchangeable cost centers that should simply execute whatever is requested. These misaligned incentives mean each group's locally rational behavior actively works against the others' goals and against the company's actual outcome. The book's resolution isn't a new org chart — it's a shared goal, shared metrics, and structural changes (embedding, shared on-call, joint planning) that make Dev, Ops, and the business genuinely accountable to the same outcome instead of to conflicting local scorecards.

## The idea
At the start of the novel, Development wants to ship the Phoenix Project fast to satisfy business deadlines; Operations wants to slow down and stabilize changes to avoid outages; the business (Steve, the CEO, and the board) wants both — fast delivery and stability — without understanding that these teams' incentive structures actively fight each other to produce those outcomes. Each side has a coherent, locally rational story: Development is right that shipping late has real costs; Ops is right that unstable changes cause real outages; the business is right that it needs both speed and reliability to compete. The tragedy is structural, not personal — nobody in this triangle is wrong about their own local goal, but the three goals as currently measured and organized are in direct tension, and the resulting behavior (Dev pushes risky changes to hit dates, Ops resists and slows everything down to protect stability, the business escalates pressure on both) makes the underlying problem worse, not better.

This lesson names the pattern and the fix the book arrives at: the Three Ways (`phoenix-project/05`, `06`, `07`) only work at scale if the organizational structure and incentives actually support them — fast flow requires Ops and Dev to be pulling in the same direction, fast feedback requires the business to trust and act on signal from engineering rather than just applying pressure, and continual learning requires all three groups to see incidents as shared, not "their" fault versus "our" fault.

## How it works

### The classic Dev-vs-Ops incentive conflict
Development is traditionally measured on throughput: features shipped, deadlines hit, velocity. Operations is traditionally measured on stability: uptime, incident count, change-failure rate. These metrics are in direct tension by construction — the fastest way to hit a Dev deadline is often to skip testing or push a risky change; the surest way to protect Ops's stability metric is to slow down or block changes entirely. When each group is rewarded for optimizing its own metric in isolation, the natural equilibrium is exactly what Parts Unlimited exhibits: Dev pushes hard to ship, Ops erects gates and slows everything down defensively, and the resulting friction (missed deadlines *and* outages, the worst of both) gets blamed on "the other team" rather than on the incentive structure that produced it.

**Worked example.** A mid-size company measures its Dev team purely on sprint velocity and its Ops team purely on incident count. Dev, under deadline pressure, ships a database migration without coordinating a maintenance window, causing a brief outage; Ops's response is to institute a strict two-week change-freeze policy requiring director-level sign-off for any production database change, to protect their incident metric. Six months later: Dev's velocity has dropped (every DB-touching feature now takes weeks longer to ship due to the approval gate), and Ops's incident count hasn't meaningfully improved (the pressure just shifted to non-database changes, and the freeze period saw a spike of batched changes right when it lifted). Both teams are optimizing their assigned metric rationally; the *system* is worse off than before, because the metrics themselves are in conflict rather than aligned to a shared outcome.

### Aligning around a shared goal and shared metrics
The structural fix isn't asking either team to care more or try harder — it's changing what's measured so that Dev's and Ops's local incentives point the same direction. A shared metric like **change-failure rate combined with lead time** (both teams jointly accountable for shipping fast *and* safely) removes the zero-sum framing, because neither team can improve their score by making the other team's job harder. This is a direct organizational analogue of `phoenix-project/05`'s First Way (end-to-end lead time, not per-stage speed) applied to incentive design rather than just process design.

**Worked example.** The same company redesigns its metrics: both Dev and Ops are now jointly measured on (a) deployment frequency, (b) change-failure rate, and (c) mean time to recovery — the DORA-style metrics later formalized in `devops-handbook/16`. Now, Dev shipping a risky, untested change that causes an outage hurts *Dev's own* score (change-failure rate), not just Ops's — and Ops blocking changes indiscriminately hurts *Ops's own* score (deployment frequency) if it's not actually reducing failures. Both teams are now incentivized to solve the same problem together (safe, fast delivery) rather than defend against each other.

### Structural integration: embedding, shared on-call, and joint planning
Beyond metrics, the book depicts concrete structural changes that reduce the Dev-Ops divide: embedding Ops expertise directly into feature teams earlier in the design process (rather than Ops finding out about a risky architecture decision only at deployment time), shared or rotating on-call responsibilities so Dev engineers directly experience the operational consequences of what they ship, and joint planning sessions where deployment and operational readiness are discussed alongside feature scope, not bolted on afterward. These structural changes make the Second Way's feedback loop (`phoenix-project/06`) shorter and more direct between Dev and Ops specifically — an Ops concern raised during design, when it's cheap to address, versus the same concern surfacing as a production incident weeks later, when it's expensive.

**Worked example.** A feature team redesigns its process so that an Ops-background engineer participates in design review for any change touching shared infrastructure, and Dev engineers rotate onto the on-call schedule for services they build. Within two quarters, the team reports catching several would-be operational issues during design review that previously would only have surfaced in production (a proposed caching strategy that would have caused a cache-stampede under real traffic patterns, flagged before implementation began), and Dev engineers report writing measurably more defensive, operationally-aware code once they're the ones paged at 2am for their own bugs.

### The business's role: trust, visibility, and not treating IT as a black box
The third leg of the triangle — the business itself — has its own structural fix, directly extending `phoenix-project/01`'s "IT is a black box" problem: business leadership needs real visibility into IT's actual capacity and constraints (via the flow metrics of `phoenix-project/02`) to make honest trade-off decisions, rather than simply escalating pressure when deadlines slip without understanding why. Steve's arc in the book is learning to ask "what would you need to be true to hit this date safely?" instead of "why haven't you hit this date," and to treat IT's constraint data (a la `phoenix-project/03`) as real input to business planning rather than an excuse to be overridden. This reframes IT from an order-taking cost center into a genuine planning partner — the direct precursor to `phoenix-project/10`'s "IT as competitive advantage."

## Pros
- Removes the structural incentive for Dev and Ops to work against each other, replacing a zero-sum local-metric conflict with shared accountability for a shared outcome.
- Structural integration (embedded expertise, shared on-call, joint planning) shortens the Second Way's feedback loop specifically at the highest-friction boundary in the organization.
- Gives business leadership honest, structural visibility into IT capacity and constraints, enabling better trade-off decisions instead of blind pressure that makes the underlying problem worse.

## Cons
- Changing incentive structures and reporting lines is a genuine organizational change effort, often requiring executive sponsorship, and is slower and more politically sensitive than a purely technical fix.
- Shared metrics can be gamed or diluted if not carefully designed — a poorly chosen "shared" metric can end up rewarding neither genuine speed nor genuine safety if it doesn't actually capture both dimensions honestly.
- Structural integration (rotating on-call, embedded Ops-in-Dev) requires real skill investment and can create short-term friction or confusion about ownership and escalation paths while the new structure beds in.

## Alternatives
- **Strict separation with formal handoff contracts (SLAs between Dev and Ops)** — keep teams separate but govern their interaction through formal service-level agreements and change-request processes; can reduce ambiguity but tends to formalize and entrench the adversarial dynamic rather than resolve it, since each side still optimizes its own side of the contract.
- **Full merge into a single "you build it, you run it" team (per Team Topologies-style stream-aligned teams)** — eliminate the Dev/Ops split entirely by making each team own their service end-to-end, including on-call; a more radical structural fix that this lesson's "shared on-call" worked example gestures toward, explored further in `devops-handbook/14`.
- **Platform team as an intermediary** — rather than fully merging Dev and Ops, build a dedicated platform/enablement team that provides self-service infrastructure and guardrails, reducing the need for constant Dev-Ops negotiation on every change; a scalable middle path covered in `devops-handbook/14` and `devops-handbook/15`.

## When to use it
Diagnose and fix Dev-Ops-business misalignment whenever you observe the classic symptom pattern: Dev and Ops each blame the other for missed deadlines or outages, both have locally rational arguments, and neither team's individual effort improvement seems to fix the systemic friction. It's also the right lens whenever business leadership repeatedly escalates on deadlines without engaging with IT's actual capacity constraints — that's a visibility and trust problem, not a motivation problem.

## When NOT to use it
Don't reach for large structural reorganization (merging teams, changing reporting lines) as a first response to a single, isolated conflict between one Dev and one Ops engineer — that may just be a normal interpersonal or process disagreement, not evidence of a systemic incentive conflict. Full "you build it, you run it" merging is also not universally appropriate — some organizations and domains (highly regulated environments, deeply specialized infrastructure) have good reasons to maintain some separation of duties, provided the shared-metric and feedback-loop fixes above are still applied to prevent adversarial dynamics.

## Key takeaways / mental model
When two teams are structurally rewarded for opposing outcomes, expect them to behave adversarially no matter how well-intentioned the individuals are — the fix is changing what's measured and how closely feedback loops connect them, not asking either side to try harder. Ask: are Dev and Ops (and the business) accountable to the same outcome, or to competing local scorecards that make the other side's success look like their own failure?

## Self-check questions
1. Using the change-failure-rate worked example, explain why a shared metric removes the incentive for Ops to block changes indiscriminately, in a way that a purely Ops-owned "incident count" metric does not.
2. A company merges Dev and Ops metrics but keeps the teams organizationally separate with no shared on-call or joint planning. Would you expect this alone to resolve the adversarial dynamic? Why or why not, referencing the Second Way (`phoenix-project/06`)?
3. Describe the difference between the business "escalating pressure on a missed deadline" and the business "asking what would need to be true to hit the deadline safely." What structural precondition (per `phoenix-project/02`) does the second approach require that the first doesn't?
4. When would strict Dev/Ops separation with formal handoff contracts be the *right* choice over merging into "you build it, you run it" teams? Give a concrete scenario.

## References
- The Phoenix Project (Kim, Behr, Spafford), Part 3 (Steve's arc toward trusting and partnering with IT; the book's resolution of the Dev-Ops-business triangle).
- See also `phoenix-project/01` (IT as a black box to the business), `phoenix-project/02` (flow visibility as the basis for honest trade-off conversations), and `devops-handbook/14` (enabling team topologies and platform capabilities), which operationalizes structural integration further.
