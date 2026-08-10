---
id: staff-engineer/11
subject: staff-engineer
title: Multiplying impact by developing successors and technical leaders
slug: developing-successors
status: drafted
mastery:
seniority: principal
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapters 5 and 8
prerequisites: [staff-engineer/02, staff-engineer/03, staff-engineer/09]
created: 2026-08-10
updated: 2026-08-10
---

# Multiplying impact by developing successors and technical leaders

## TL;DR
The highest-leverage activity available to an experienced staff-plus engineer is deliberately growing other engineers into staff-plus-capable technical leaders, because it's the only form of impact that keeps compounding after you personally stop being involved in a given problem — a single staff engineer's direct capacity is a hard ceiling, but the capacity of the technical leaders they've developed is not.

## The idea
Every mechanism covered so far in this subject — expanding scope (`staff-engineer/03`), writing strategy (`staff-engineer/06`), running initiatives (`staff-engineer/09`) — still routes impact through one person's personal time and attention. That's a real ceiling: even an extremely effective staff engineer can only personally review so many designs, unblock so many teams, sit in so many rooms. Developing successors breaks through that ceiling by a different mechanism entirely: instead of you doing more high-leverage work, other people become capable of doing high-leverage work themselves, and that capability persists and keeps producing impact whether or not you're personally involved in any given instance of it.

This is also, practically, what makes it possible for an experienced staff-plus engineer to keep taking on new, larger problems rather than becoming permanently stuck maintaining everything they've ever built (the trap flagged in `staff-engineer/03` and expanded on in `staff-engineer/12`) — if nobody else can pick up what you've been carrying, you can never fully hand it off and move to the next problem.

## How it works

### Identifying who's ready to grow
Not identical to identifying who's technically strongest — the signal to look for is an engineer who's already informally doing pieces of staff-plus-shaped work without the title: the one other engineers already go to with hard technical questions, the one who writes the clearest design docs on the team, the one who's started noticing cross-team problems on their own initiative (even in a small way) rather than only executing assigned tickets. These are the people for whom deliberate development compounds fastest, because the raw instinct is already there and just needs scope and support.

### Deliberately transferring scope, not just advice
Advice ("you should think about cross-team impact more") is far weaker than actually handing someone real scope and staying close enough to support them through it. The mechanism that works: give a developing engineer a real piece of ambiguous, cross-cutting work — something you would otherwise have done yourself — and be genuinely available to unblock and coach them through it, without taking the scope back the first time they struggle. Taking scope back at the first sign of difficulty teaches the wrong lesson (that ambiguous work gets reassigned to someone more senior the moment it gets hard) and trains people to stay in their comfort zone rather than grow into it.

**Worked example.** A staff engineer notices a senior engineer on an adjacent team consistently writing the clearest, most-referenced design docs in their org, and independently flagging cross-team inconsistencies in code review (without being asked to). Instead of quietly absorbing the next cross-team seam problem personally, the staff engineer brings this senior engineer in as a co-owner on it: drafts the initial framing together, but has the senior engineer own writing the actual proposal document and running the socialization conversations with affected teams (`staff-engineer/07`), while staying available to review drafts and coach through the harder stakeholder conversations rather than taking them over. The senior engineer's first attempt at the cross-team socialization goes roughly, hitting pushback they didn't anticipate — the staff engineer resists the urge to step in and handle it personally, instead debriefing afterward on what the pushback revealed and how to approach the next conversation differently. Six months later, that engineer is running similar cross-team work independently, and the original staff engineer has genuinely freed up capacity for a new problem area.

### Sponsorship as part of development
Growing someone technically is necessary but not sufficient — per `staff-engineer/05`, staff promotion also requires visibility to people who aren't the engineer's manager. An experienced staff-plus engineer developing a successor should also actively sponsor them: mentioning their work in rooms they're not in, connecting them with senior stakeholders on the cross-team work they're now doing, and being a vocal advocate at calibration time. Technical development without sponsorship can produce someone who's genuinely ready for staff scope but stays invisible to the people who'd promote them; the combination of both is what actually multiplies impact into a title change and durable career growth for the person being developed.

### Multiplying technical leadership more broadly
Beyond one-on-one successor development, staff-plus engineers multiply technical leadership organization-wide through things like: writing documentation and standards that let engineers who've never met you make better decisions (a form of "successor development" at scale, distinct from developing one specific person), running or contributing to internal training on the technical judgment skills covered in this subject, and deliberately building processes (like the design-review rhythm in `staff-engineer/08`) that create structured opportunities for less-experienced engineers to practice cross-team technical judgment in a lower-stakes setting than being fully on their own.

### Recognizing the trade-off honestly
Developing a successor on a piece of work is almost always slower and rockier in the short term than doing the work yourself — the senior engineer in the worked example above made choices the staff engineer wouldn't have made, hit pushback the staff engineer might have avoided, and took longer to reach the same outcome. This short-term cost is real and needs to be weighed honestly against the long-term multiplier; development work is not free, and treating it as costless leads to under-investing the actual time and patience it requires.

## Pros
- The only mechanism in this subject whose impact compounds and persists independent of the developer's own continued personal involvement.
- Frees the developer to take on new, larger problems instead of becoming a permanent bottleneck on everything they've ever touched.
- Strengthens the organization's overall technical-leadership bench, which is valuable to the company independent of any single individual's career.

## Cons
- Genuinely slower and higher-risk in the short term than doing the work yourself — the developing engineer will make mistakes a more experienced person might have avoided, and those mistakes have real cost.
- Requires real patience and restraint (not stepping back in at the first sign of struggle) that's psychologically hard, especially under delivery pressure where the "safe" move is to just do it yourself.
- Not every strong technical engineer wants this kind of growth, or wants it on the developer's timeline — pushing someone toward staff-plus-shaped scope they don't want is not development, it's imposition.

## Alternatives
- **Hiring externally for staff-plus roles instead of developing internally** — faster in the short term when there's an urgent gap, and brings in outside perspective, but forgoes the compounding, trust-building benefit of growing someone who already has deep organizational context; most healthy organizations do some mix of both rather than relying on either exclusively.
- **Formal mentorship/training programs decoupled from real project scope** — structured, scalable, and lower-risk than handing someone live ambiguous work, but Larson's own emphasis (and general leadership-development consensus) is that real scope with real stakes develops judgment faster and more durably than simulated exercises alone.
- **Not investing in successor development at all, staying the sole owner of your scope** — maximizes short-term personal output and avoids the real short-term cost described above, but caps long-term impact at one person's capacity and creates a single point of failure — the trap this lesson exists to counter.

## When to use it
Invest deliberately in successor development once you have real staff-plus scope of your own to hand off pieces of, and once you've identified someone showing early signs of staff-plus instinct — don't wait until you're personally burned out or overloaded to start; by then there's no slack left to invest the necessary coaching time.

## When NOT to use it
Don't hand off ambiguous, high-stakes scope to someone who hasn't shown any of the readiness signals yet (an engineer with excellent narrow execution but no track record of independently noticing cross-team problems or writing clear proposals) — that's not development, it's setting someone up to fail without the scaffolding to succeed, and it can damage both the initiative and the engineer's confidence.

## Key takeaways / mental model
Picture your own impact as a pipe with a fixed diameter — no matter how skilled you get, only so much can flow through it personally. Developing successors is the only way to add more pipes rather than trying to force more through the one you have; it costs real throughput in the short term (training a new pipe is slower than using the one that already works) but is the only investment that keeps paying off after you've moved on to the next problem.

## Self-check questions
1. Name someone at your own organization (or a hypothetical profile) showing the "readiness signals" this lesson describes — informally doing staff-shaped work without the title. What specific piece of your own scope could you hand to them, and what would you need to do to support rather than take over when they struggle?
2. Why does the lesson argue that taking scope back at the first sign of difficulty teaches the wrong lesson? What should happen instead, per the worked example?
3. Explain why technical development alone (without sponsorship) can fail to actually multiply impact into a promoted, visible technical leader. What's missing?
4. Describe the short-term cost versus long-term benefit trade-off of developing a successor on a real project. Under what circumstances would it be reasonable to decide the short-term cost isn't worth paying right now?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 5 ("Influence without authority") and Chapter 8 material on staff-plus career trajectories and organizational leverage.
