---
id: managers-path/01
subject: managers-path
title: Mentoring as the first leadership responsibility
slug: mentoring-as-first-leadership
status: drafted
mastery:
seniority: senior
source: The Manager's Path (Camille Fournier), Chapter 1 - Management 101
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Mentoring as the first leadership responsibility

## TL;DR
Mentoring - helping a specific, usually more junior, engineer grow - is the first leadership skill nearly everyone practices, often years before any title changes. It is a low-stakes, high-leverage training ground for the empathy, communication, and patience that all later management work depends on.

## The idea
Most engineers are never "suddenly" made a manager with zero prior leadership experience - they mentor first. A senior engineer pairs with a new hire, answers questions in Slack, reviews a junior's pull requests with real teaching intent instead of just a stamp of approval, or shows someone how to debug a production incident calmly. None of this shows up on an org chart, and none of it is optional once you're the most experienced person in the room - someone always ends up leaning on you, whether or not "mentor" is in your job title.

Camille Fournier frames mentoring as management's on-ramp because it isolates the core skill management is actually built from: helping someone else be effective, rather than being effective yourself. That is a genuinely different skill from writing good code. A brilliant senior engineer can be a poor mentor if they explain by doing instead of by teaching, if they can't tolerate watching someone struggle productively, or if they give answers instead of asking questions that lead to answers. Mentoring is where you first practice these muscles, at low stakes: no one's compensation or career trajectory formally depends on how well you mentor, so mistakes are cheap and recoverable, unlike mistakes made as a people manager with real authority over someone's career.

## How it works

### Mentoring is not teaching by doing
The most common mentoring failure mode is the mentor solving the problem themselves while narrating it, or simply fixing the mentee's code directly instead of pointing at what's wrong. This feels efficient in the moment - the bug gets fixed faster - but it transfers zero durable skill. A concrete example: a junior engineer's pull request has a subtle race condition. The unhelpful mentor rewrites the function and adds a one-line comment. The effective mentor instead asks, "Walk me through what happens if two requests hit this function at the same time" - a question that makes the mentee find the race condition themselves, and that they will now recognize the *pattern* of the next time they see it, in code the mentor will never review.

### Match the mentoring style to what the mentee actually needs
Not every mentee needs the same thing. Some need technical skill-building (how do I write a good test, how do I read a stack trace). Some need organizational navigation (who do I ask about this system, how do promotions actually work here). Some need confidence-building more than skill-building - a mentee who is technically strong but afraid to speak up in design reviews needs a mentor who creates space and explicitly invites their opinion, not more code review. Fournier's point: figure out which of these a given mentee needs *right now*, because applying the wrong kind of help (drilling someone on syntax when their real blocker is confidence) wastes both people's time.

### Mentoring scales your impact without giving you authority
This is the leverage insight that makes mentoring the gateway to management: a senior engineer who mentors three junior engineers well multiplies their impact on the team's output without writing any more code themselves. That is precisely the shape of a manager's job - impact through other people's work rather than your own - except practiced with none of the formal authority (no performance reviews, no hiring/firing power, no obligation) that makes management higher-stakes. If you find you dislike this multiplying-through-others work when practiced as low-stakes mentoring, that is a strong, cheap signal about whether formal management is a good fit for you at all.

### A worked mentoring interaction
A new engineer, Priya, is stuck for two hours on a failing integration test. A poor mentor response: "Oh yeah that test is flaky, just rerun it" (solves the symptom, teaches nothing, and is possibly wrong). A good mentor response: sit with her for ten minutes, ask "What have you tried so far? What did each attempt tell you?", and guide her toward checking whether the test depends on execution order - teaching a debugging *heuristic* ("look for shared state between tests") she can reapply independently next time, not just this test's fix.

## Pros
- Builds the core management skill (helping others be effective) at low stakes, before any formal authority or accountability is on the line.
- Strengthens the mentor's own understanding - explaining a concept clearly to someone else routinely surfaces gaps in the mentor's own model.
- Compounds team-wide: a strong mentoring culture reduces onboarding time and turnover far more cheaply than hiring more people.

## Cons
- Time cost is real and often invisible in performance metrics that reward shipped code over other people's growth, creating a disincentive for engineers who are evaluated narrowly.
- Informal mentoring (no assigned pairing, no structure) can be inconsistent - some junior engineers get excellent mentors by luck of who sits near them, others get none.
- A mentor without any people-management training can default to doing-the-work-for-them, which feels helpful but actively slows the mentee's growth.

## Alternatives
- **Formal mentorship programs** - the organization assigns mentor/mentee pairs deliberately, rather than relying on organic pairing; more consistent but can feel forced if the pairing lacks real rapport.
- **Sponsorship** - distinct from mentoring: a sponsor advocates for someone's advancement in rooms they're not in (promotion committees, project staffing), rather than teaching skills directly. Complementary to mentoring, not a substitute - see how this differs from tech lead scope in `managers-path/02`.
- **Coaching** - a more structured, often external, relationship focused on unlocking someone's own answers through questions rather than transferring the coach's specific expertise; useful when the mentor lacks direct domain expertise in the mentee's growth area.

## When to use it
Any time you are the more experienced person in an interaction with a colleague who is stuck, ramping up, or navigating something new - pairing sessions, code review, onboarding, incident retrospectives. It scales from an ad hoc five-minute Slack exchange to a standing weekly pairing session with a specific junior engineer.

## When NOT to use it
Don't let mentoring substitute for a mentee's manager doing their job - a mentor is not accountable for the mentee's performance review, career trajectory, or compensation, and confusing the two roles (e.g., a mentor privately promising a promotion) creates false expectations and undermines the actual manager. Also don't mentor by osmosis alone (assuming someone will pick things up just by sitting near you) when a mentee has explicitly asked for structured help - that requires actual time investment, not passive availability.

## Key takeaways / mental model
Mentoring is management's practice mode: same core skill (multiplying your impact by helping someone else succeed), none of the formal authority or stakes. If you can't enjoy watching someone else get the credit for a problem you helped them solve, formal management will be a harder fit than it looks from the outside.

## Self-check questions
1. Describe a time you (or someone mentoring you) solved a problem "for" the mentee instead of teaching a reusable approach. What would the teaching version of that interaction have looked like?
2. A mentee is technically capable but never speaks up in design reviews. What kind of mentoring do they need, and how does it differ from mentoring someone who is technically behind?
3. Why does Fournier treat mentoring as a signal for whether someone might enjoy formal management, rather than treating strong individual contribution as that signal?
4. What is the difference between a mentor and a sponsor, and why might someone need both?

## References
- The Manager's Path (Camille Fournier), Chapter 1: "Management 101".
