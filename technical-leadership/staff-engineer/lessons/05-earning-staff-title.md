---
id: staff-engineer/05
subject: staff-engineer
title: "Earning the staff title: promotion packets, sponsors, and timing"
slug: earning-staff-title
status: drafted
mastery:
seniority: senior
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 3 ("Getting the title")
prerequisites: [staff-engineer/01, staff-engineer/02]
created: 2026-08-10
updated: 2026-08-10
---

# Earning the staff title: promotion packets, sponsors, and timing

## TL;DR
Getting promoted to staff is not simply "do enough good work and someone notices" — it requires deliberately doing staff-shaped work before the title, finding a sponsor senior enough to advocate for you in rooms you're not in, and assembling a legible case (usually a written packet) that a promotion committee unfamiliar with your day-to-day can actually evaluate. Timing and framing matter as much as the underlying work.

## The idea
Below staff, promotion is often close to mechanical: hit the criteria on the ladder, get a good review, get promoted. Above senior, this stops working for a structural reason — staff promotions are decided, in most companies, by a committee of people who are *not* your manager and have never seen your work directly. They know you only through what's written down and what a sponsor says about you in a room you're not in. This means a genuinely excellent staff-level engineer who does the work but never makes it legible to that committee can be passed over indefinitely, while a slightly less exceptional engineer who tells a clear, well-evidenced story gets promoted faster. This isn't fair in a moral sense, but it is predictable, which means it's manageable if you understand the mechanism.

## How it works

### Do the work before the title
The single most reliable predictor of a successful staff promotion is already operating at staff scope (`staff-engineer/03`) before asking for the title — leading cross-team work, writing documents other teams use, being the person other teams' engineers go to for judgment calls. Promotion committees are much more comfortable ratifying a role someone is already visibly performing than gambling on a title change that's supposed to *cause* someone to start performing it. Asking for the title first and hoping the scope follows is a much harder, slower path.

### Find and cultivate a sponsor
A sponsor is someone senior enough to advocate for you in the calibration or committee meeting where your promotion is actually decided — a room you are, by design, not in. A sponsor is different from a mentor: a mentor gives you advice; a sponsor spends their own political capital vouching for you when you can't speak for yourself. Sponsorship isn't requested directly and bluntly ("will you sponsor my promotion?") so much as earned by consistently doing visible, valuable work that a senior leader personally benefits from and remembers — then that leader naturally becomes willing to advocate when the moment comes. Building this relationship takes months to years, which is why waiting until the promotion cycle to start looking for a sponsor is usually too late.

### Assemble a legible packet
Most companies use some form of written promotion packet: a document laying out your key projects, their scope and impact, and how they demonstrate staff-level judgment, usually alongside peer and cross-functional feedback. The packet's job is translation — converting the messy, distributed reality of staff-plus work (documents, meetings, influence, decisions that prevented bad outcomes) into a narrative a committee member with five minutes and no prior context can follow and believe.

**What makes a packet weak, concretely:**
- Listing projects by activity ("I led the migration") instead of impact ("the migration eliminated $400K/year in redundant infrastructure spend and unblocked three teams' roadmaps").
- Describing only technical execution, omitting the organizational and influence work (getting buy-in, resolving a cross-team disagreement, mentoring another engineer through the hard parts) that is usually the actual staff-level signal.
- No independent corroboration — a packet that's entirely self-reported reads as unverifiable; peer and cross-functional quotes matter because they come from people with nothing to gain by inflating your case.

**Worked example — turning raw work into a packet-ready story.** Raw fact: "I wrote a shared retry library used by eight teams" (see the worked example in `staff-engineer/03`). Packet version: "Identified a recurring pattern across three post-incident reviews where uncoordinated retry logic amplified outages; proposed and built a standard solution with buy-in from three team leads; the library is now used by eight teams, and retry-storm incidents have dropped from roughly one per month to zero in the two quarters since rollout. [Tech lead of Team X]: 'this fundamentally changed how we think about failure handling across the org.'" The second version shows scope, judgment, delivered impact, and independent validation — everything the first version leaves for the reader to infer.

### Timing
Staff promotions are rarely decided the moment the packet is submitted — they're usually decided over a longer arc where the sponsor has been building the case in conversations well before any formal cycle, and the packet documents a case that's already largely believed rather than making it from scratch. Submitting a packet for work that's only just started, or timing a request right after a single big win with no sustained track record before it, is a common and avoidable mistake — committees look for a pattern across multiple projects and multiple quarters, not one impressive quarter in isolation.

### What to do with a "not yet"
A denied or deferred promotion should come with specific, written feedback about the gap — if it doesn't, ask directly for it. The most common gaps are: insufficient scope (still mostly team-bound, not yet organizational per `staff-engineer/03`), insufficient evidence (the work happened but wasn't documented or made visible to people outside the immediate team), or insufficient sponsorship (the work was real but nobody senior enough was in the room advocating for it). Each has a different, concrete fix, which is why getting the specific reason matters more than the raw "not yet."

## Pros
- Understanding the mechanism turns an opaque, anxiety-inducing process into a set of concrete, controllable actions (do staff-scoped work, build sponsor relationships, write a legible packet) rather than a mysterious judgment from on high.
- Rewards exactly the behaviors — cross-team impact, clear communication, relationship-building — that make someone effective in the staff role itself, so the promotion process and the job it's promoting into are well aligned.
- A well-built packet is genuinely useful beyond the promotion itself: it's a forcing function to reflect on and articulate your own impact clearly.

## Cons
- Politically and emotionally taxing — sponsorship-dependent processes can feel (and sometimes are) unfair to engineers who are excellent but poorly networked, quieter, or in less visible parts of the organization.
- Creates a real incentive to over-invest in visibility and narrative relative to the underlying work, which can tip into self-promotion that damages trust with peers if taken too far.
- The "not yet" outcome, without specific feedback, is genuinely hard to act on — many companies do this process poorly, leaving engineers to guess at the gap.

## Alternatives
- **Purely criteria-based, committee-free promotion** (some smaller companies or flatter orgs) — a manager alone decides based on a fixed rubric, with no separate calibration committee; removes the sponsorship dependency but concentrates the decision (and its biases) in a single person instead of distributing them across a committee.
- **External hiring at the staff level** rather than internal promotion — skips the packet/sponsor process entirely by having a company that already operates at staff scope validate the level via its own interview loop; trades the internal-politics problem for interview-loop variance and loss of company-specific context.
- **Title-blind leveling based purely on compensation bands** — a few companies decouple "staff" as a title from a formal promotion ceremony, adjusting compensation and scope more continuously; reduces the high-stakes, single-moment nature of promotion but is uncommon and requires unusual organizational discipline to keep calibrated.

## When to use it
Start acting on this the moment you're doing staff-shaped work (`staff-engineer/03`) and want the title to catch up — track impact as you go (don't reconstruct a quarter's worth of impact from memory the week before packet deadline), invest in relationships with senior leaders who see your work, and ask your manager directly what specifically your committee looks for.

## When NOT to use it
Don't chase the packet-and-sponsor machinery before you're actually doing staff-scoped work — a polished narrative describing senior-engineer-level work dressed up in staff-level language will not survive committee scrutiny, and over-indexing on packaging before substance reads (correctly) as premature.

## Key takeaways / mental model
Think of the promotion committee as a jury that never watched the trial — your job is to be a good witness for your own case, corroborated by other witnesses (peers, sponsors) who have nothing to gain by lying for you. The verdict depends on evidence made legible in advance, not on the underlying work being self-evidently good; undocumented excellence is, to that jury, indistinguishable from mediocrity.

## Self-check questions
1. Pick a piece of your own work from the last six months. Write both the "raw fact" version and the "packet version" (impact-framed, with independent corroboration) as in this lesson's worked example. What does the exercise reveal was missing from how you'd normally describe it?
2. Explain the difference between a mentor and a sponsor. Who, concretely, in your organization could plausibly be a sponsor for you, and what would you need to do to earn that?
3. Why does Larson emphasize that promotion decisions are usually substantially settled *before* the formal packet is submitted? What does that imply about when you should start building your case?
4. If you received a "not yet" with no specific reason given, what would you concretely do next, according to this lesson?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 3: "Getting the title."
