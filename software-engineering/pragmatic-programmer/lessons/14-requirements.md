---
id: pragmatic-programmer/14
subject: pragmatic-programmer
title: Requirements and the Requirements Pit
slug: requirements
status: drafted
mastery:
seniority: senior
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 8
prerequisites: [pragmatic-programmer/01]
created: 2026-08-10
updated: 2026-08-10
---

# Requirements and the Requirements Pit

## TL;DR
Requirements are not "out there" waiting to be discovered by asking users what they want — users describe symptoms and habits, not underlying needs, so requirements must be actively dug out through examples, policy documents, and probing "why," and then documented as concrete usage scenarios rather than abstract, ambiguous prose. Treat requirements gathering as an ongoing conversation, not a one-time upfront phase.

## The idea
A common and costly mistake: treating a requirements-gathering session as an information *retrieval* task — as if the user already has a clear, correct, complete specification in their head and your job is just to transcribe it accurately. In reality, users are experts in their *problem domain*, not in specifying software — they describe how they currently work around the problem (habits, workarounds, existing paper forms), not the underlying need those habits exist to serve. Taking their described process literally and automating it precisely often just digitizes the workaround, missing the actual opportunity and sometimes cementing an inefficiency that only existed because of some other, since-removed constraint.

The book calls the resulting cycle of continuous clarification the "requirements pit" — not because requirements are a hole you fall into and escape once, but because genuinely understanding what's needed is an iterative digging process that continues throughout a project, not a phase that completes before "real" work begins.

## How it works

### Requirements are policy, not process — dig for the "why" behind the "what"
The book's key move: when a user describes a process ("the clerk checks if the customer's account is more than 90 days overdue, and if so, refers it to collections"), don't just encode that exact process — ask *why* that specific rule exists. Usually the process encodes an underlying **business policy** ("we don't want to write off accounts that are still likely to pay, but we do want to escalate ones that probably won't") that could be served by a different, better mechanism once you understand it as policy rather than as a fixed sequence of steps.

**Worked example.** A user says: "when an order comes in, print it, walk it to the warehouse, and have someone manually check if we have stock before confirming it." Taking this literally, you'd build a system that... generates a printout. The actual underlying need, once you ask "why do you check stock this way, specifically" is: "because our inventory system isn't real-time, so we can't trust the on-screen count." The real requirement isn't "support printing and manual walking" — it's "provide a trustworthy, real-time stock count," which the printing-and-walking process was only ever a workaround for. Automating the walk-to-the-warehouse process would have been a costly, literal-minded mistake; fixing the actual underlying gap (real-time inventory) removes the need for the workaround entirely.

### Work with a user to think like a user — concrete scenarios over abstract prose
Abstract requirements ("the system shall be user-friendly," "search shall be fast") are unfalsifiable and useless for design or testing — nobody can point at code and say definitively whether "user-friendly" is satisfied. The book's fix: extract **concrete usage scenarios/examples** instead — specific, walkthrough-able stories of a particular user doing a particular thing with particular data, because concrete examples surface ambiguity that abstract statements hide.

"Search shall be fast" tells you nothing actionable. "When a support agent searches for a customer by phone number during an active call, results must appear within 1 second, because the caller is waiting on the line and every extra second increases call-abandonment risk" tells you the actual constraint, its magnitude, *and* the reason behind it — which lets you make an informed trade-off later if 1 second turns out to be technically expensive to guarantee (maybe 1.5s is fine if it's not literally a live call).

### Requirements documentation should record the *why*, in the user's own words where possible
The book recommends documenting requirements as a living glossary of concrete scenarios and rules, each ideally traceable back to a business reason — not as a static, one-time signed-off spec. This matters specifically because requirements *will* change (markets shift, regulations change, users discover new needs once they see the first version) — a document that only records the "what" with no "why" leaves future changes to guesswork about whether a rule is still load-bearing or was only ever incidental.

### It's a pit, not a phase — requirements gathering doesn't stop at kickoff
Because you can't fully anticipate what a user actually needs until they interact with something real, the book pushes toward continuous requirements refinement alongside iterative delivery (echoing tracer bullets, Lesson 05): build something concrete early, show it, and let the user's reaction ("oh, actually, I also need to filter by region") surface requirements that no amount of upfront interviewing would have extracted, because the user themselves didn't know to mention it until they saw something tangible.

## Pros
- Digging for underlying policy rather than literal process avoids automating workarounds and can reveal much better solutions to the actual problem.
- Concrete scenarios are testable, reviewable, and expose ambiguity far earlier than abstract prose requirements do.
- Continuous requirements refinement, paired with iterative delivery, catches misunderstandings while they're still cheap to fix.

## Cons
- Digging past the literal ask for the underlying "why" takes real interviewing skill and stakeholder patience — some stakeholders find "why do you do it that way" repeatedly frustrating or feel second-guessed.
- Concrete-scenario-based requirements can miss genuinely general rules if too much energy goes into specific examples without generalizing the pattern behind them.
- Treating requirements as perpetually open ("it's a pit, not a phase") can be misused to justify scope creep or an endlessly moving target if not paired with real delivery discipline and change control.

## Alternatives
- **Formal requirements specification (e.g., IEEE 830-style SRS documents)** — comprehensive, signed-off upfront documentation, more appropriate for regulated or contractually fixed-scope projects (aerospace, medical devices) where requirements genuinely must be frozen and traceable for compliance, at the cost of flexibility.
- **User story mapping / Jobs-to-be-Done** — Agile-flavored techniques that similarly push past "what feature do you want" toward "what job is the user actually trying to accomplish," largely converging on the same underlying insight from a different framework.
- **A/B testing / shipping and measuring** — for some product requirements, skip trying to fully specify what users want upfront and instead ship a hypothesis, measure real behavior, and let the data reveal the actual requirement — appropriate when the cost of a wrong guess is low and measurable quickly.

## When to use it
Apply "dig for the policy behind the process" whenever a stakeholder describes a specific workflow as if it were the requirement itself — especially workflows that involve manual workarounds, paper, or "because that's how we've always done it." Push for concrete scenarios whenever a requirement is stated in unfalsifiable, abstract terms.

## When NOT to use it
Don't relitigate the "why" behind every stated requirement if the underlying policy is already well-understood and well-documented (e.g., a clear, known regulatory rule) — that's wasted stakeholder patience for no informational gain. In regulated/contractual contexts requiring a frozen, traceable spec, don't treat requirements as an open-ended pit without an explicit, agreed change-control process layered on top.

## Key takeaways / mental model
When someone describes a process, hear it as evidence of a policy, not as the requirement itself — ask "why do you do it that way" until you reach the actual business reason, then design for that reason, which may look nothing like the described process. And always translate abstract requirement language into a concrete, walkthrough-able scenario before treating it as understood.

## Self-check questions
1. Using the warehouse/stock example, explain the difference between "the requirement" as literally described and "the requirement" once you dig for the underlying policy.
2. Rewrite "the dashboard should load quickly" as a concrete, falsifiable scenario with a specific user, action, and threshold.
3. Why does the book insist that requirements gathering doesn't stop after an initial interview phase? What replaces the traditional "sign-off and move on" model?
4. Describe a situation where digging too aggressively for "the real why" would be counterproductive, and explain when to stop digging.

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 8: "Before the Project" (The Requirements Pit section).
