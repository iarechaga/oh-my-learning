---
id: seeking-sre/06
subject: seeking-sre
title: Reliability Communication with Executives and Stakeholders
slug: reliability-stakeholder-communication
status: drafted
mastery:
seniority: staff
source: Seeking SRE (David Blank-Edelman, ed.), essay on translating error budgets and reliability trade-offs for non-technical leadership
prerequisites: [seeking-sre/01, sre/04]
created: 2026-08-10
updated: 2026-08-10
---

# Reliability Communication with Executives and Stakeholders

## TL;DR
Executives don't need to understand SLOs or error budgets as engineering mechanisms — they need reliability trade-offs translated into the vocabulary they already reason in (revenue, risk, customer trust, opportunity cost), and the specific skill of doing that translation well, repeatedly, is what turns error budgets from an engineering tool into an org-wide decision-making tool.

## The idea
`sre/04` establishes error budgets as a release-governance mechanism: a service has a target reliability (say, 99.9% uptime), the gap between that and 100% is a "budget" of acceptable unreliability, and once it's spent, feature releases pause in favor of reliability work. That mechanism only actually governs anything if the people who decide whether to ship a risky feature anyway — often product leadership, sometimes the CEO — understand and respect it. An error budget that engineering tracks internally but that gets overridden by executive fiat every time it matters ("ship it anyway, this launch is too important") isn't governing release decisions; it's decorative.

The book's framing: this is fundamentally a **translation problem**, not an education problem. The goal isn't teaching executives to compute SLIs — it's finding the vocabulary in which a reliability trade-off is obviously a business trade-off to them, so they make the same call they'd make with full context, without needing the underlying engineering literacy.

## How it works

### Translate budget state into terms executives already use
Instead of reporting "we're at 40% error budget remaining for the checkout service, SLO is 99.9%," translate to: "if checkout has the same bad week it had in March, we'll have an unplanned outage before the next release window — and last time that cost us an estimated $180K in abandoned carts over 6 hours." The second framing requires no engineering literacy to act on; it states risk in money and precedent, which is the currency executives already reason in.

A reusable translation table, built once per critical service and reused in every stakeholder conversation:
| Engineering term | Executive translation |
| --- | --- |
| SLO breach | "We fall below the reliability level we promised customers/contracts" |
| Error budget exhausted | "We're out of room for more risk this cycle without real customer impact" |
| Error budget healthy | "We have room to ship faster/riskier this cycle" |
| Toil | "Engineer time spent on repetitive manual work instead of product/reliability improvements" |
| Postmortem action item overdue | "A known risk we identified and haven't yet fixed" |

### Worked example: the launch-day override conversation
A product VP wants to ship a major feature on a specific date for a marketing tie-in, but the payments service's error budget is already exhausted from an unrelated incident two weeks earlier. The engineering-native pitch ("we're past our SLO threshold, per policy we should hold non-critical releases") is easy for a VP under deadline pressure to simply overrule, because it sounds like process for process's sake. The translated pitch: "shipping this now means our next payments hiccup — which historically happens about once every three weeks at our current reliability trend — will land during the highest-traffic days of this launch, and payments outages during a high-traffic launch have historically cost us roughly 3x normal incident cost in lost revenue and support load. We can ship one week later once the budget resets, or ship now with a documented, executive-approved risk acceptance." This doesn't guarantee the VP defers — but it makes the trade-off visible and puts the decision, explicitly, in the VP's hands with real stakes named, rather than leaving it as an invisible engineering-only judgment call that gets silently overridden.

### The recurring reliability review, not just incident-driven updates
A common mistake: executives only hear about reliability during or after a bad incident, which trains them to associate "reliability conversation" with "bad news, probably my fault for pushing too hard." The fix is a short, recurring (monthly or quarterly) reliability review, framed neutrally, covering: current error-budget state per critical service, trend over the period, and any risk-acceptance decisions made. This does two things: it normalizes reliability as an ongoing input to planning rather than a crisis-only topic, and it creates a paper trail of risk-acceptance decisions so that when a deferred fix eventually causes an incident, it's visibly a decision the org made with eyes open, not a surprise.

### Handling the "just make it 100% reliable" instinct
Non-technical stakeholders sometimes respond to a reliability conversation by asking for the simplest-sounding fix: "why can't we just make it never go down?" The translation move here is cost-of-additional-nines framing: "going from 99.9% to 99.99% roughly means engineering time currently split 80/20 between features and reliability work shifts closer to 50/50 for the next two quarters, and even then some classes of failure (a cloud provider region outage) aren't fully preventable at any reasonable cost." Concrete, comparable numbers (percentage of roadmap capacity, not abstract engineering effort) let a non-technical stakeholder make an informed trade-off between more reliability and more features, rather than treating "more reliable" as a free lunch.

## Pros
- Makes error budgets an actual governance mechanism instead of an internal engineering artifact that gets silently overridden under pressure.
- Builds a track record (via the recurring review) of transparent, jointly-made risk decisions, which protects engineering credibility when a deferred risk eventually surfaces.
- Gives non-technical stakeholders a genuine, informed choice instead of either blind trust in engineering or blind override of engineering's recommendation.

## Cons
- Requires an engineering leader with both the technical grounding and the communication skill to do the translation well and repeatedly — a rare, specific skill combination.
- Executives can still override a well-communicated risk, and doing this well doesn't guarantee better outcomes, only better-informed ones — the value is in shared accountability, not veto power.
- Overuse of dollar-figure framing on incidents where the cost estimate is shaky can itself erode credibility if the numbers turn out to be wrong or clearly padded to win an argument.

## Alternatives
- **Hard technical enforcement (freeze deploys automatically when budget is exhausted)** — removes the negotiation entirely by making the override technically impossible without an explicit, logged executive unlock; more reliable at actually stopping risky ships but requires significant trust and tooling investment, and can itself become a political flashpoint if it blocks a genuinely important launch.
- **Reliability as a purely engineering-owned decision with no stakeholder visibility** — the default in many companies by omission; avoids the communication overhead of this lesson entirely but leaves engineering without air cover when a deferred risk causes a costly incident and leadership asks "why didn't we know."
- **A dedicated reliability/risk officer role that sits between engineering and executive leadership** — professionalizes the translation function as its own job rather than a skill individual engineering leaders must build; viable at larger scale, less so for smaller companies who can't dedicate headcount to it.

## When to use it
Build the translation habit (vocabulary table, recurring review, cost-of-additional-nines framing) as soon as error budgets are meant to actually influence release decisions that executives care about — which is essentially always, since any release decision significant enough to need an SLO trade-off is usually significant enough to attract executive attention eventually.

## When NOT to use it
Don't build an elaborate stakeholder-communication apparatus for reliability decisions that never actually reach executive attention (a low-visibility internal tool with no revenue link) — the overhead isn't justified there, and a lighter internal-only error-budget process suffices. Don't use dollar-figure framing as a scare tactic to win an argument when the underlying estimate is genuinely uncertain; overclaiming certainty damages the trust the whole practice depends on.

## Key takeaways / mental model
An error budget only governs behavior if the person who can override it understands the trade-off in their own vocabulary. Build a standing translation table (engineering term to business term), report proactively on a recurring cadence rather than only during incidents, and frame "more reliability" as a genuine trade-off against roadmap capacity with comparable numbers, not a free lunch.

## Self-check questions
1. A product VP wants to override an exhausted error budget for a launch. Rewrite the engineering-native objection ("we're past our SLO threshold") into the business-vocabulary version this lesson recommends, using a scenario of your own choosing.
2. Why does the lesson recommend a recurring, neutral-framed reliability review instead of only communicating reliability status during incidents?
3. An executive asks "why can't we just make this service 100% reliable?" What's the translation move this lesson recommends, and why does it work better than explaining nines and asymptotic cost curves directly?
4. What's the risk of relying on dollar-figure framing for every reliability conversation, and how would you mitigate it?

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on translating error budgets and reliability trade-offs for non-technical leadership.
- See also `sre/04` (error budgets as a release-governance mechanism) for the underlying engineering machinery this lesson translates, and `seeking-sre/09` for how these conversations feed into product roadmap prioritization.
