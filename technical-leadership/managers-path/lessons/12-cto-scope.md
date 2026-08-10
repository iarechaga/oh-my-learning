---
id: managers-path/12
subject: managers-path
title: 'CTO scope: technology vision and company strategy'
slug: cto-scope
status: drafted
mastery:
seniority: principal
source: The Manager's Path (Camille Fournier), Chapter 8 - Executive Leadership
prerequisites: [managers-path/11]
created: 2026-08-10
updated: 2026-08-10
---

# CTO scope: technology vision and company strategy

## TL;DR
The CTO role is the most variable in the ladder - it can mean anything from a hands-on technical co-founder to a pure external-facing figurehead to an internally-focused VP-of-Engineering-plus-strategy - but its common thread is owning technology's role in company strategy: what bets to make, what risks to take, and how technology serves the business's long-term direction, not just this quarter's delivery.

## The idea
Fournier is explicit that "CTO" is not one job - unlike engineering manager, tech lead, or even VP of Engineering, which have reasonably consistent day-to-day content across companies, the CTO title covers wildly different actual responsibilities depending on company stage and history. At an early-stage startup, the CTO is often still the most senior hands-on engineer and de facto architect. At a larger company, the CTO might be primarily an external-facing role - representing the company's technology story to investors, customers, and the press - while a VP of Engineering (`managers-path/11`) runs internal execution. At another company, the CTO might absorb the VP of Engineering's execution responsibilities entirely, with no separate VP role. Because of this variability, evaluating "what does a CTO do" requires first asking "at this company, given its stage and other leaders, what does this company actually need from its CTO?" rather than assuming a fixed job description.

Despite the variability, Fournier identifies a common core: the CTO is the person ultimately responsible for the company's technology *strategy* - the multi-year bets on platform, buy-versus-build, technical risk tolerance, and how technology capability constrains or enables the company's business strategy - as distinct from the VP of Engineering's more execution-focused ownership of delivering the current roadmap well.

## How it works

### Diagnose which "flavor" of CTO the company actually needs
Before doing the job well, a CTO (or someone considering the role) needs an honest read on the company's actual gap: does this company need someone who can still architect and prototype hands-on (common pre-product-market-fit), someone who can credibly represent technology to external stakeholders (common when raising funding or selling to technically sophisticated enterprise customers), or someone who can run engineering execution at scale alongside strategy (common when there's no separate VP of Engineering)? A mismatch - hiring or promoting a hands-on-architect-style CTO into a company that actually needs an external-facing evangelist, or vice versa - is a common and costly failure mode Fournier flags directly.

### Own multi-year technology bets, not just this quarter's roadmap
Where a VP of Engineering (`managers-path/11`) is judged substantially on whether the current roadmap ships predictably, a CTO is judged more on whether the company placed the right long-horizon technology bets: build a data platform in-house or buy one; invest early in a scalable architecture before it's strictly needed, accepting slower initial feature velocity, or ship fast now and accept a costly rewrite later; which emerging technology is worth real investment versus which is hype the company should ignore. Concrete example: a CTO deciding whether to build a custom recommendation engine in-house versus licensing a third-party solution needs to weigh not just this quarter's engineering cost, but multi-year differentiation value, the cost of being locked into a vendor's roadmap, and whether the company has (or can build) the specialized talent to sustain a custom system - a strategic trade-off with a much longer time horizon than typical execution decisions.

### Manage technical risk at the company level
A CTO is often the person who has to say, credibly, "this is an acceptable technical risk to take" or "this risk is not acceptable, even though it would let us move faster" - security posture, infrastructure resilience, technical debt that could threaten the company's ability to operate, compliance/regulatory technology requirements. This requires judgment calibrated to company-level consequences (a security breach or major outage can be existential, not just embarrassing) rather than team-level consequences, and often requires pushing back against short-term business pressure to accept a risk the CTO judges unacceptable.

### Represent technology in the company's overall strategy conversation
At the executive/board level, a CTO's job includes making sure technology capability and constraint are genuinely part of company strategy discussions - not brought in after a business decision is already made to simply "figure out how to build it." Fournier notes this requires the CTO to have real influence in strategic conversations, which is itself built over time through credibility (the VP of Engineering-style delivery credibility from `managers-path/11`, extended to a longer strategic horizon) rather than being automatically granted by the title.

## Pros
- Aligns technology investment with genuine long-term company strategy, avoiding both under-investment (a company that never modernizes and gets outpaced) and over-investment (gold-plating infrastructure the business doesn't yet need).
- Gives technology a real seat at the company strategy table, so business decisions account for technical feasibility, risk, and opportunity rather than treating engineering as a pure execution function.
- At its best, provides company-wide technical risk judgment (security, resilience, compliance) that no lower-level role has the scope or mandate to own.

## Cons
- The role's high variability across companies makes it genuinely hard to hire for, be evaluated in, or transition into from a lower level - success in one company's CTO role doesn't predict success in another's very different version of the same title.
- Multi-year strategic bets are judged on multi-year timescales, meaning a CTO can be wrong for a long time before the consequences of a bad bet (or the benefits of a good one) become clear - much slower feedback than execution-level work.
- Risk of drifting into a purely figurehead or purely execution role that doesn't actually match what Fournier considers the CTO's real strategic core, especially in companies that create the title without a clear mandate for it.

## Alternatives
- **Chief Architect (separate from CTO)** - some larger companies split hands-on technical architecture leadership into a distinct role from the business-strategy-facing CTO, allowing each to specialize; adds a coordination seam between the two roles.
- **VP of Engineering absorbing CTO-style strategy work** - smaller companies sometimes skip a distinct CTO title entirely, with the VP of Engineering (or even a strong director) carrying both execution and strategic technology responsibility; works at smaller scale, gets strained as company complexity grows.
- **Technical advisory board / fractional CTO** - very early-stage companies sometimes use part-time or advisory technical leadership instead of a full-time CTO, trading depth of ownership for lower cost and flexibility before the company can justify a full executive hire.

## When to use it
When a company has reached a point where multi-year technology strategy, company-level technical risk decisions, and/or credible external technical representation are a distinct, ongoing need separate from (or in addition to) day-to-day engineering execution.

## When NOT to use it
Don't assume "CTO" means the same job across companies, or transplant a playbook wholesale from one company's CTO role to another's - always diagnose which flavor of the role (hands-on architect, external evangelist, execution-plus-strategy) a specific company actually needs first. And don't create the title as a reward or a retention lever without a genuine strategic mandate behind it - a CTO without real influence on company strategy conversations is set up to fail regardless of their individual competence.

## Key takeaways / mental model
"CTO" names a strategic function - owning technology's role in company strategy and long-horizon risk - more than a fixed job description; diagnose what flavor a given company actually needs before assuming the role looks like any other company's CTO.

## Self-check questions
1. Why does Fournier argue that "CTO" is a less consistent job description than "engineering manager" or "VP of Engineering" across companies?
2. Describe the difference between how a VP of Engineering and a CTO would each evaluate a proposal to rewrite a core system from scratch. What time horizon and criteria would each bring?
3. A startup is hiring its first CTO. What questions would you want answered about the company's stage and needs before deciding what "flavor" of CTO to hire?
4. Give an example of a company-level technical risk decision (something with existential, not just team-level, consequences) that would appropriately land on a CTO's desk rather than a director's or VP's.

## References
- The Manager's Path (Camille Fournier), Chapter 8: "Executive Leadership".
