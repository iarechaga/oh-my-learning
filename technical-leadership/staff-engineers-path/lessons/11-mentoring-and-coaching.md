---
id: staff-engineers-path/11
subject: staff-engineers-path
title: Mentoring and coaching for durable capability growth
slug: mentoring-and-coaching
status: drafted
mastery:
seniority: staff
source: The Staff Engineer's Path (Tanya Reilly), Chapter 6 - "Good Influence" (mentoring, coaching, teaching)
prerequisites: [staff-engineers-path/01]
created: 2026-08-10
updated: 2026-08-10
---

# Mentoring and coaching for durable capability growth

## TL;DR
Mentoring transfers your knowledge and experience directly ("here's what I'd do and why"); coaching draws out the other person's own thinking through questions rather than answers ("what have you considered?"). Both grow someone's durable capability, but they're different tools for different situations, and defaulting to only one — usually mentoring, because it's faster and feels more helpful — leaves real growth on the table.

## The idea
The fastest way to help someone stuck on a problem is often to just tell them the answer. It's also frequently the *worst* way to help them grow, because it solves today's problem without building the muscle to solve tomorrow's version of it themselves. Reilly frames mentoring and coaching as two ends of a spectrum, both legitimate, both necessary at different moments — the skill is knowing which one a given situation calls for, not defaulting reflexively to whichever one is more comfortable for you.

- **Mentoring** is knowledge transfer: sharing your own experience, giving direct advice, showing someone how you'd approach something. It's efficient when the mentee lacks information or experience they genuinely don't have yet, and there's no way to "discover" it themselves faster than being told.
- **Coaching** is drawing out the other person's own reasoning through questions, reflection, and structured problem-solving support — without supplying the answer. It's slower per-instance but builds the mentee's own judgment, which transfers to future problems the original conversation never covered.

## How it works

### Recognizing which mode a moment calls for
**Worked example — mentoring is right.** A junior engineer is stuck because they don't know their company's deployment process has an undocumented manual approval step for a specific class of changes. There's no reasoning path that gets them to that fact — it's tribal knowledge. Telling them directly ("for database migrations, you also need sign-off from the DBA team — here's the process") is the correct move; there's nothing to "discover" here, only information to transfer.

**Worked example — coaching is right.** A mid-level engineer brings you a design for a new service and asks "does this look right?" They actually have the skill and context to evaluate their own design — they're just not yet in the habit of interrogating it critically themselves. Instead of reviewing it and handing back a list of fixes (mentoring), you ask: "What's the failure mode you're most worried about in this design? What would you do if this service needed to handle 10x the load next year?" These questions push them to find the gaps themselves. It takes longer in the moment, but next time they design something, they'll ask themselves those questions unprompted — the coaching habit transfers, whereas a handed-over fix list would only have fixed this one design.

### Why coaching-when-appropriate is worth the extra time
Mentoring produces a *fixed* answer to *this* problem. Coaching produces a *transferable* skill the mentee applies to problems you'll never even see. The extra time coaching costs in the moment is an investment that pays off across every future problem the mentee's newly-built judgment now handles without your involvement — this is the mechanism by which "leveling up others" (`staff-engineers-path/01`) compounds rather than just helping once.

### Reading the room: don't coach when someone needs mentoring, or vice versa
A common mistake is applying coaching-style questions when someone genuinely lacks the underlying knowledge to answer them — repeatedly asking "well, what do you think?" to someone who has no information to reason from isn't Socratic, it's just withholding help, and it reads (correctly) as unhelpful or even a little cruel. Equally, mentoring someone who already has the skill and just needs confidence or practice deprives them of the chance to build that confidence themselves. Calibrating which mode fits requires actually assessing what the person in front of you currently has (knowledge/experience) versus what they're missing (judgment/confidence/practice) before responding.

### Group-scale versions: teaching and documentation
Mentoring and coaching are inherently one-on-one and don't scale past a handful of relationships at a time. Their group-scale analogs are teaching (a workshop, a brown-bag session, a structured onboarding curriculum — knowledge transfer at scale, mentoring's group form) and well-designed self-service documentation/exercises that let someone coach themselves through structured reflection prompts. A staff engineer balances direct 1:1 mentoring/coaching relationships against these lower-touch, higher-reach mechanisms, since 1:1 time is the scarcest resource.

## Pros
- Coaching, done well, produces capability that compounds without further involvement from you — the highest-leverage form of "leveling up others."
- Mentoring is fast and effective for pure information gaps, avoiding wasted time forcing someone to rediscover tribal knowledge through questions alone.
- Deliberately practicing both modes makes you a more effective manager-adjacent leader even without formal reports, since both skills transfer directly to leading through influence.

## Cons
- Coaching takes real, often uncomfortable patience — sitting with someone's incomplete answer instead of just fixing it yourself is a genuine skill, and under time pressure the temptation to "just tell them" is strong and sometimes justified.
- Misapplying coaching to a pure knowledge gap wastes time and frustrates the person being "coached," who correctly senses they're being asked to guess at information they were never given.
- Both modes require an ongoing relationship and real time investment; they don't scale to an entire org the way a written standard (`staff-engineers-path/09`) does — hence the group-scale alternatives below.

## Alternatives
- **Teaching (structured, group-scale knowledge transfer)** — a workshop or onboarding curriculum; efficient for spreading commonly-needed information widely, but loses the personalization that makes 1:1 mentoring/coaching effective for a specific person's specific gap.
- **Documentation and self-service resources** — written guides, runbooks, worked examples; scales infinitely and costs no ongoing time, but can't adapt to an individual's specific confusion the way a live conversation can, and works best for well-understood, stable knowledge rather than judgment-building.
- **Formal management/1:1 structures** — a direct manager's regular 1:1s are a natural, expected venue for both mentoring and coaching; a staff engineer's version is informal and elective, which is more flexible but also easier to let slide under time pressure since nobody's tracking whether it happens.

## When to use it
Use mentoring when the gap is genuinely informational — the person cannot reason their way to the answer because they lack a fact or experience only you (or someone) can supply. Use coaching when the person already has the raw material (skill, context) to reach a good answer and what they need is practice interrogating their own thinking, or confidence that their own judgment is trustworthy.

## When NOT to use it
Don't coach when someone is missing information entirely — repeated open questions to someone with nothing to reason from is not helpful and erodes trust. Don't mentor (hand over the answer) when someone is capable of reaching it themselves with a nudge — doing so repeatedly creates learned dependency, where the person defers to you by habit rather than building their own judgment.

## Key takeaways / mental model
Ask yourself, before responding to someone stuck: do they lack information (mentor — tell them), or do they lack practice/confidence exercising judgment they already have (coach — ask them)? Misreading this in either direction wastes time or stunts growth; reading it correctly is most of the actual skill in both mentoring and coaching.

## Self-check questions
1. Recall a recent moment you helped a colleague. Was it mentoring or coaching? Would the other mode have served them better, and why?
2. Describe a scenario where coaching (asking questions instead of giving answers) would actively frustrate someone rather than help them. What made it the wrong mode for that moment?
3. Why does coaching, despite costing more time per instance, sometimes produce more total value than mentoring across a mentee's career?
4. What group-scale (non-1:1) mechanisms could substitute for some mentoring/coaching relationships, and what do they lose relative to a 1:1 conversation?

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 6: "Good Influence" (mentoring, coaching, teaching).
