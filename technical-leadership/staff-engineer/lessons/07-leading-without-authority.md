---
id: staff-engineer/07
subject: staff-engineer
title: Leading without authority through influence networks
slug: leading-without-authority
status: drafted
mastery:
seniority: staff
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 5 ("Influence without authority")
prerequisites: [staff-engineer/01]
created: 2026-08-10
updated: 2026-08-10
---

# Leading without authority through influence networks

## TL;DR
Staff-plus engineers almost never have formal authority (a reporting line) over the people they need to align — their tool is influence, built through a network of trust relationships, well-reasoned written arguments, and consistent follow-through, not through positional power. Influence has to be earned continuously and can be spent down by a single bad call, unlike formal authority, which persists regardless of recent track record.

## The idea
A manager can, in the last resort, simply tell a direct report what to do. A staff engineer almost never can — the engineers whose work needs to change, the teams whose roadmap needs to shift, the executive whose plan has a technical flaw, none of them report to a staff engineer. And yet staff-plus impact (per `staff-engineer/01` and `staff-engineer/03`) *requires* changing what other people do, at a scale beyond what the staff engineer can personally execute. This is the central mechanical puzzle of the role: real influence over outcomes, with no formal lever to pull.

The resolution is that influence is a real, learnable substitute for authority — but it works on different rules. Authority is granted once (by title) and persists until formally revoked. Influence is earned continuously through a track record of good judgment, and it degrades the moment that track record includes a visible bad call. This means staff-plus engineers have to actively build and maintain their influence, rather than assuming a title alone will make people listen.

## How it works

### The three components of influence
1. **Track record.** People extend trust to judgment that has previously been right. Every well-reasoned recommendation that turns out correct, every honest "I don't know, let's find out" instead of overconfident guessing, every incident where you were the person who correctly diagnosed the real problem — these accumulate into a reputation that precedes you into rooms you're not yet in.
2. **Relationships.** Influence rarely travels through a single big meeting; it travels through a network of people who already trust your judgment from prior interactions, and who will vouch for or push back on an idea based partly on who's presenting it. Building this network is not a side activity to "real work" — deliberately investing time in 1:1s with engineers and managers on teams you don't work with directly is how the network gets built before you need it.
3. **Legible reasoning.** Especially with people who don't know you well, a clearly written argument that shows your reasoning (not just your conclusion) lets someone evaluate the idea on its merits even without pre-existing trust in you personally — this is part of why writing (see `staff-engineer/06`) is such a load-bearing skill for staff-plus work.

### Tactics for exercising influence without authority
- **Lead with the other person's incentives, not your own reasoning.** A team will adopt your shared library faster if you can show it saves *them* time and risk, not merely because it's architecturally cleaner from your point of view. Frame proposals in terms of what the audience cares about.
- **Use data and a written document to depersonalize disagreement.** A design doc with clear evidence lets people argue with the argument instead of with you personally, which lowers the emotional stakes of pushing back or being pushed back on, and makes it more likely disagreement resolves on the merits.
- **Pick your battles — spend influence on what matters.** Influence is not infinite; disagreeing loudly over every small decision burns trust that's needed for the decisions that actually matter. Staff-plus engineers who are known for picking a small number of well-chosen fights are listened to more carefully on those fights than engineers who object to everything.
- **Build coalitions before the decisive meeting.** Walking into a room to propose something contested, cold, is a weak position. Having already talked individually to the two or three people whose opinion will carry the room — hearing their objections in private, adjusting the proposal, and securing at least tacit agreement beforehand — means the decisive meeting ratifies a decision that's substantially already made, rather than litigating it from scratch in public.
- **Demonstrate rather than merely argue, when possible.** A working prototype of the shared retry library (see `staff-engineer/03`'s worked example) is more persuasive than a design doc alone, because it removes the "will this actually work" uncertainty that a purely written proposal leaves open.

### Worked example
A staff engineer believes three teams should consolidate onto one message queue technology instead of each running a different one, but has no authority over any of the three teams. Ineffective approach: write a single company-wide email announcing the consolidation and asking everyone to comply. This has no track record behind it for two of the three teams, no relationships to draw on, and reads as an order from someone with no standing to give one — predictable resistance follows.

Effective approach: the engineer first has individual conversations with each team's tech lead, framed around what that specific team is currently struggling with (one team's pain is operational — three different on-call runbooks for effectively the same tool; another team's pain is cost — running three separate managed-queue services). The engineer tailors the framing to each team's actual incentive, not a single generic pitch. After hearing objections (one team has a hard dependency on a queue feature the proposed consolidated choice doesn't support), the engineer adjusts the proposal to accommodate it before it ever becomes a public disagreement. Only after this groundwork does the engineer write a short document and bring it to a joint meeting — where the outcome is close to already settled, because the real negotiation happened in the individual conversations beforehand.

### Influence degrades — protect it
A staff engineer who pushes a recommendation that turns out badly wrong, especially if pushed with high confidence, pays for it in future influence — people extend less benefit of the doubt next time. This is why calibrated confidence (being honest about uncertainty rather than always projecting certainty) is itself an influence-preserving habit, not a weakness: overclaiming confidence that later proves wrong costs more trust than an honest "I think X, but I'm not fully sure, here's what would change my mind."

## Pros
- Scales impact far beyond a staff engineer's personal formal authority, which is exactly the leverage `staff-engineer/01` describes as the point of the role.
- Builds durable organizational relationships and trust that outlast any single project, compounding in value over a career.
- Tends to produce more durable buy-in than authority-driven compliance, because people who were genuinely persuaded (rather than told) are more likely to maintain and defend the decision later.

## Cons
- Slow — building a track record and a relationship network takes months to years, and there's no shortcut for a staff engineer new to an organization who needs influence quickly.
- Fragile compared to formal authority — a manager's authority survives one bad call; a staff engineer's influence can take a real, lasting hit from a single visible misjudgment.
- Requires emotional labor and social skill (reading incentives, managing disagreement, building coalitions) that not every technically excellent engineer has developed or enjoys exercising.

## Alternatives
- **Escalate to a manager or executive with formal authority** — when influence genuinely isn't working and the stakes are high enough, asking a manager to make a call using their actual authority is a legitimate move; overusing it, though, signals an inability to lead peers and can itself cost influence over time.
- **Formal RFC / decision-record processes with a defined decision-maker** — some organizations institutionalize cross-team technical decisions with a documented process and a named decision owner, reducing reliance on any one person's personal influence network; this scales better organizationally but requires the company to have built that process in the first place.
- **Building the relationship network passively over time, without deliberate tactics** — simply doing good work for years and letting reputation accumulate organically; slower and less reliable than the deliberate tactics in this lesson, especially for engineers newer to an organization or moving into a new domain.

## When to use it
Use these tactics any time you need people outside your reporting line to change what they're doing — cross-team technical alignment, proposing a standard, resolving a disagreement between two teams — which is to say, most staff-plus work per `staff-engineer/03`.

## When NOT to use it
Don't reach for informal-influence tactics (coalition-building, incentive-framing) as a way to route around a decision that genuinely needs formal authority to resolve fairly — some disagreements (e.g., involving conflicting team OKRs that only a shared manager can actually trade off) are legitimately a management decision, and trying to influence your way to a "win" there can look like manipulation rather than leadership.

## Key takeaways / mental model
Influence is a bank account, not a title: it's funded by track record and relationships, spent by every recommendation you make, and it can go negative fast on one bad, overconfident call. Before every attempt to change what another team does, ask "have I built enough of a balance with these specific people, on this specific topic, to spend it here?"

## Self-check questions
1. Describe a time you (or someone you observed) tried to get a team outside your reporting line to change direction. Which of this lesson's tactics (incentive-framing, coalition-building before the meeting, demonstrating rather than arguing) were used, and which were missing?
2. Why does Larson argue that influence is fundamentally more fragile than formal authority? What's the mechanism by which a single bad call costs more than a manager's single bad call would?
3. Rewrite a generic, un-tailored pitch ("we should all use library X because it's cleaner") into three different incentive-framed pitches for three different hypothetical teams with different pain points.
4. When is escalating to a manager's formal authority the right move instead of continuing to build informal influence? What's the cost of escalating too often?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 5: "Influence without authority" and related material on staff-plus relationship-building.
