---
id: managers-path/03
subject: managers-path
title: 'Becoming an engineering manager: role reset and priorities'
slug: becoming-an-engineering-manager
status: drafted
mastery:
seniority: staff
source: The Manager's Path (Camille Fournier), Chapter 4 - Managing People
prerequisites: [managers-path/02]
created: 2026-08-10
updated: 2026-08-10
---

# Becoming an engineering manager: role reset and priorities

## TL;DR
Becoming a manager is a job change, not a promotion in the usual sense: your primary output stops being your own code and becomes your team's effectiveness, which requires a genuine identity shift away from measuring your day by what you personally shipped.

## The idea
The most common failure of new managers is measuring themselves by the wrong scoreboard: they still feel productive only when they've written code, so they squeeze management duties into the margins of a day still organized around individual output, and the actual management work - 1:1s, unblocking people, thinking about team structure, giving feedback - gets treated as overhead rather than the job itself. Fournier calls this out directly: if you keep evaluating your day by "did I ship code," you will chronically under-invest in the things that make you effective as a manager, because those things don't produce a visible commit.

The deeper reason this transition is hard is that engineers are trained, rewarded, and hired for individual technical excellence, and management asks for a different kind of excellence: judgment about people and priorities, patience with ambiguity, and comfort with your success being measured by other people's output. Camille Fournier frames the first months of management as "losing your former job" - you have to consciously let go of being the go-to technical expert on every question, or you'll never create the space (and give your reports the credit and growth opportunity) for anyone else to become that expert instead.

## How it works

### The job changes from "solve problems" to "make sure problems get solved by the right people"
A new manager sees their team stuck on a design problem and instinctively wants to just solve it - old habits from IC and tech-lead days. The manager mindset instead asks: who on my team should own this, do they have what they need to solve it, and if they're stuck, is that a skill gap I should coach through or a resourcing/priority problem I should fix? Concrete example: a report is behind on a project because they're avoiding a difficult architecture decision. The IC instinct is to just make the call for them. The manager instinct is to ask what's making the decision hard, and coach them through making it - slower in the moment, but it's how the report grows and how the manager avoids becoming the bottleneck for every hard call on the team.

### Redefine what "a good day" looks like
Early managers often feel like they "didn't get anything done" on a day full of 1:1s, because nothing shipped that they can point to. Fournier's reframe: a good management day is one where your team is unblocked, informed, and growing - that is real output, it's just output you can't `git log`. A useful practical habit: at the end of the day, write down what you did to help your team be more effective (removed a blocker for X, gave Y feedback that will change how they approach code review, made a staffing call for the next project) instead of only counting lines of code or PRs merged.

### Give up being the top individual technical contributor - on purpose
A manager who continues to grab the hardest, most interesting technical problems for themselves (the tech-lead trap from `managers-path/02`, now with real authority behind it) starves their team of growth opportunities and signals, intentionally or not, that management is a part-time job layered on top of still being the best engineer. Concrete example: a critical, gnarly bug appears. The new-manager instinct is to dive in and fix it personally, because it's satisfying and fast. The better move, most of the time, is to pair with the report best positioned to grow from owning it, even though the manager could probably fix it faster alone - the short-term speed loss buys long-term team capability.

### Expect a real emotional adjustment period
Fournier is candid that new managers often go through a period that feels like loss - loss of flow-state coding time, loss of being universally seen as technically excellent, loss of the clear, bounded sense of "done" that a merged PR gives you. This is normal and expected, not a sign the person made the wrong choice; it typically resolves once the manager finds a new sense of "done" rooted in team outcomes rather than personal output.

## Pros
- Multiplies impact: a manager who builds a genuinely effective team can influence far more outcome than any one person coding alone, once the mindset shift actually happens.
- Develops a skill set (people judgment, prioritization, influence, organizational navigation) that compounds into director/VP-level scope later (see `managers-path/10`-`managers-path/12`).
- Creates the structural role needed for `managers-path/04` (1:1s) and `managers-path/05` (feedback) to actually happen with real authority and accountability behind them.

## Cons
- Loses the fast, clear feedback loop of writing and shipping code personally; the feedback loop for "am I doing this well" is slower and noisier (team outcomes over months, not a merged PR today).
- Genuinely different skill set - technical excellence does not automatically transfer, and some excellent engineers are, honestly, poor managers without deliberate training and practice.
- Reversible in principle but costly in practice - stepping back from management to IC work is possible but often carries real career and perception friction, so the transition deserves a deliberate decision, not a default "next step."

## Alternatives
- **Staff/Principal engineer track** - stay a deep technical IC, gaining scope and influence through technical leverage (architecture, mentoring at scale, cross-team technical initiatives) rather than through formal people management; a legitimate and equally senior alternative path, not a consolation prize.
- **Tech lead without becoming a manager** (`managers-path/02`) - keep the hybrid coordination role without taking on people-management authority and accountability; a smaller step than full management.
- **Manager-plus-hands-on (playing coach)** - some organizations, especially small ones, keep managers coding part-time; workable at small scale but breaks down as team size and management load grow (see `managers-path/06` on team health at scale).

## When to use it
When someone has shown real aptitude and interest in the mentoring (`managers-path/01`) and tech-lead (`managers-path/02`) precursors, genuinely wants their success to be measured by team outcomes rather than personal output, and the organization can give them real authority (hiring input, performance review responsibility, resourcing decisions) to match the new accountability.

## When NOT to use it
Don't promote someone into management as the *only* available path to more compensation or seniority when they have shown no interest in or aptitude for people work - this produces reluctant managers who under-invest in the job and often damages the team more than an explicit IC-track promotion would have. Also don't move into management expecting to keep doing 80% of your previous IC workload "on the side" - that's the identity-shift failure mode this lesson exists to name.

## Key takeaways / mental model
The new job's scoreboard is your team's effectiveness, not your own output - measure your days by what you unblocked, coached, or decided for others, not by what you personally shipped, and expect a real adjustment period before that feels like enough.

## Self-check questions
1. Describe a specific day that would "feel unproductive" to a new manager still measuring themselves by IC habits, but was actually a highly effective management day. What made it effective?
2. Why does Fournier warn against a new manager grabbing the hardest technical problems for themselves, even if they can genuinely solve them fastest?
3. What is the difference between staying technically strong as a manager and staying the team's top individual technical contributor? Why does the second one become a problem?
4. If you were coaching a friend through their first three months as a manager, what's one habit you'd tell them to build to avoid the "measuring myself by code shipped" trap?

## References
- The Manager's Path (Camille Fournier), Chapter 4: "Managing People".
