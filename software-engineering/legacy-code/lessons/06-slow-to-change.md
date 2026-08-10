---
id: legacy-code/06
subject: legacy-code
title: It Takes Forever to Make a Change
slug: slow-to-change
status: drafted
mastery:
seniority: senior
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 2
prerequisites: [legacy-code/01, philosophy-of-software-design/01]
created: 2026-08-10
updated: 2026-08-10
---

# It Takes Forever to Make a Change

## TL;DR
When a codebase has slowed to the point that every change takes disproportionately long, Feathers' diagnosis is usually one of a small number of specific, recognizable causes — most commonly, a lack of understanding of the code's actual structure and behavior, not raw code volume. The fix is targeted comprehension-building (informed by `legacy-code/03`'s characterization technique) at exactly the point of the needed change, not a wholesale rewrite or an attempt to understand the entire system first.

## The idea
"It takes forever to make even a small change here" is one of the most common complaints about legacy codebases, and it's tempting to attribute it vaguely to "the code is just bad" or "there's just too much of it." Feathers pushes for a more precise diagnosis, directly connecting to `philosophy-of-software-design/01`'s specific symptom vocabulary: the slowness is usually **change amplification** (a change requires touching many places) or **cognitive load / unknown unknowns** (you don't yet understand what needs to change, or what else might be affected) — and each has a different, targeted remedy, rather than a single, generic "the code needs a rewrite" response.

## How it works

### Diagnosing which specific problem is causing the slowness
Before applying any fix, identify which of these is actually happening for the specific change you're trying to make:
- **You don't understand the code well enough to know what to change.** This is a comprehension problem — the actual code, once identified, might be a small, contained edit, but *finding* the right place and understanding its current behavior is what's consuming the time.
- **The change genuinely requires touching many scattered places** (echoing `refactoring/04`'s Shotgun Surgery smell and `philosophy-of-software-design/01`'s change amplification). This is a structural problem — even with perfect understanding, the change is inherently large because the relevant logic/data is duplicated or scattered.
- **You're afraid to make the change because you can't verify it won't break something** (`legacy-code/01`'s change dilemma). This is a safety-net problem — the change itself might be simple and well-understood, but the *verification* cost (manual testing, careful review, anxiety) is what's actually consuming the time.

Misdiagnosing which of these three is actually happening leads to the wrong fix: attempting to build tests (safety-net fix) when the real problem is comprehension gains you little; attempting to understand the code more deeply (comprehension fix) when the real problem is genuinely scattered logic doesn't reduce the number of places you still have to touch.

### The comprehension-building technique: sketch, don't fully document
When the diagnosis is a comprehension problem, Feathers recommends lightweight, throwaway sketches specifically scoped to the area you're about to change — a quick diagram of the classes and their relationships relevant to your task, a rough sequence diagram of the specific call flow you need to modify — deliberately *not* attempting to fully document or understand the entire system. This directly mirrors `pragmatic-programmer/06`'s prototyping discipline (learn one specific thing, cheaply, then discard the artifact) applied to comprehension rather than technical feasibility: the sketch's job is to answer "what do I need to know for *this* specific change," not to become permanent system documentation.

**Worked example.** Before modifying a discount-calculation function buried in a large, unfamiliar order-processing module, spend fifteen minutes sketching (on paper, in a scratch file, in a whiteboard tool) just the call chain leading to and from that function — what calls it, what it calls, what data flows in and out — rather than attempting to understand the entire order-processing module's full architecture. This targeted sketch, built specifically for the task at hand and then discarded once the change is made, is dramatically cheaper than either fully understanding the whole system or proceeding to change code you don't understand at all.

### When the real problem is structural (change amplification), sketching doesn't help — refactor instead
If comprehension is already adequate and the diagnosis is genuinely "this change requires touching many scattered places," the fix is a refactoring (`refactoring/06`'s Move Function/Extract Class, `refactoring/04`'s smell-driven catalog) that consolidates the scattered logic — but critically, per `refactoring/02`'s guidance, this refactoring is justified specifically *because* it makes the current change easier, not as an abstract, separately-justified cleanup effort.

### When the real problem is the safety net, build one before proceeding
If the diagnosis is genuinely "I don't trust that I can verify this change is safe," the fix is exactly `legacy-code/03`'s characterization-testing technique — building a targeted safety net for the specific area about to change, rather than either proceeding without verification (risky) or attempting to comprehensively test the entire surrounding system first (disproportionate and often impractical).

### Combining diagnoses — often more than one is present simultaneously
In practice, a slow-to-change area of legacy code often exhibits more than one of these problems at once — poor comprehension *and* scattered logic *and* no safety net, compounding each other. The practical sequence Feathers implies: build minimal comprehension first (a targeted sketch), then a targeted safety net (characterization tests, enabled by whatever seams — `legacy-code/02` — are available or creatable), and only then attempt the structural fix (refactoring) if the change amplification problem remains after the first two are addressed.

## Pros
- Precisely diagnosing which of the three causes (comprehension, structure, safety net) is actually slowing you down avoids wasted effort applying the wrong fix.
- Lightweight, task-scoped sketches provide just enough comprehension to proceed safely, without the impractical cost of fully understanding an entire unfamiliar legacy system first.
- The sequenced approach (comprehend, then safety-net, then refactor if still needed) tackles the cheapest, most likely-to-help interventions first, before committing to more expensive structural changes.

## Cons
- Correctly diagnosing which cause is actually dominant requires some experience and honest self-assessment — it's easy to misattribute slowness to "the code is just bad" without pinpointing the actual, specific, addressable cause.
- Task-scoped sketches, by design, don't build durable, reusable documentation — the same comprehension cost may need to be paid again for a future, different change to a nearby but distinct area.
- For codebases with severe, longstanding structural problems, even a well-diagnosed, well-sequenced approach may reveal that a change genuinely requires substantial, unavoidable effort — the diagnosis clarifies the problem but doesn't always make it small.

## Alternatives
- **Full system documentation effort before any change** — trades a large, upfront, hard-to-justify time investment for potentially reusable, durable comprehension — rarely proportionate for a single, specific pending change, though it may be justified for a codebase about to see sustained, ongoing work.
- **Proceeding with the change despite poor comprehension, relying on code review to catch problems** (`code-complete/12`) — riskier, and shifts the comprehension burden onto reviewers who may have even less context than the original author, though it can work for genuinely small, low-consequence changes.
- **A full rewrite of the slow-to-change area** — appropriate specifically when the structural problem is severe and pervasive enough that incremental refactoring (even once comprehension and a safety net are in place) isn't a realistic path — see `refactoring/01`'s rewrite-versus-refactor distinction.

## When to use it
Apply this diagnostic framework whenever a specific change is taking disproportionately long, before assuming a rewrite or extensive redesign is the only answer — identify whether the actual bottleneck is comprehension, structure, or safety-net confidence, and apply the correspondingly targeted fix.

## When NOT to use it
Don't invest in a full sketch/documentation effort for a change so trivial that the comprehension cost is already negligible. Don't skip the diagnosis step and jump straight to a large refactoring or rewrite without confirming that structure (not comprehension or safety-net confidence) is actually the dominant cause of the slowness.

## Key takeaways / mental model
When a change is taking too long, stop and ask specifically: "is it because I don't understand this code, because the change is genuinely scattered across many places, or because I don't trust that I can verify I haven't broken anything?" Each answer points to a different, specific, proportionate fix — comprehension sketching, targeted refactoring, or characterization testing, respectively.

## Self-check questions
1. Describe a recent change that took longer than expected, and diagnose, using this lesson's framework, which of the three causes (comprehension, structure, safety net) was actually dominant.
2. Why does the book recommend a lightweight, task-scoped sketch rather than comprehensive documentation for building comprehension? What's the trade-off being made?
3. In what order does this lesson suggest addressing comprehension, safety net, and structural problems when more than one is present, and why that order?
4. Describe a case where the real problem was structural (change amplification) but a team mistakenly tried to fix it by writing more tests or building more documentation instead. What would the correct fix have been?

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 2: "Working with Feedback" and Chapter 3: "Sensing and Separation" (diagnostic framing drawn from the book's broader treatment of legacy-code change difficulty).
