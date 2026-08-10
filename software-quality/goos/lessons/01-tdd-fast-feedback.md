---
id: goos/01
subject: goos
title: TDD as Fast Feedback for Behavior
slug: tdd-fast-feedback
status: drafted
mastery:
seniority: mid
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part I/Chapter 1
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# TDD as Fast Feedback for Behavior

## TL;DR
Test-driven development (TDD) is not primarily a testing technique — it is a way of designing software in small, verifiable steps, where a failing test is a precise, immediate statement of "what should happen next" and a passing test is proof the system does it. The value Freeman & Pryce emphasize is the *tightness of the feedback loop*: you learn whether your last five minutes of thinking was correct within seconds, not days.

## The idea
Before TDD became common, the typical loop was: write code based on your understanding of the requirements, integrate it with the rest of the system, and find out much later — via manual QA, a staging environment, or production — whether your understanding was right. The gap between "I wrote this" and "I found out if it works" could be hours, days, or weeks. Bugs discovered that late are expensive: you've forgotten the context you had when you wrote the code, other work has piled on top of it, and diagnosing the failure means reconstructing a mental model you've since lost.

TDD collapses that gap to seconds. You write a small test that describes one increment of behavior you don't have yet, watch it fail (because the behavior genuinely doesn't exist), write the minimum code to make it pass, and confirm it does. The feedback — "did my last change do what I intended?" — arrives almost instantly, while the context is still fresh in your head. Freeman & Pryce frame this as the central benefit: TDD is a discipline for *keeping the system, and your understanding of it, always in a known, working state*, advancing that state in small, checked steps rather than large, unchecked leaps.

This reframes what a "test" is for. A test in TDD isn't primarily there to catch regressions after the fact (though it does that too, permanently) — it's there, first, as a *design tool*: writing the test forces you to state, precisely and from the outside, what the code needs to do before you write it. Because you write the test first, you're forced to think about the code's interface — how it will be called, what it needs, what it returns — from the perspective of a caller, not an implementer. That perspective shift is itself a design pressure, independent of the safety-net benefit.

## How it works

### The Red-Green-Refactor cycle, and why the order matters
The mechanics: (1) **Red** — write a small test for behavior that doesn't exist yet, run it, and watch it fail. (2) **Green** — write the smallest amount of code that makes the test pass, even if it's ugly. (3) **Refactor** — clean up the code (and the test) now that it's covered by a passing test, without changing behavior.

The order is deliberate. Writing the test *first* (red before green) is what forces the design pressure described above — if you write the code first and the test after, the test tends to just describe what the code already does, adding confirmation but no design feedback. Watching the test fail before making it pass is also not ceremony: it's a check that the test is actually exercising the behavior you think it is. A test that passes immediately, without you writing any new production code, is telling you either that the behavior already existed or that the test isn't testing what you think — both are important to catch immediately, not discover three months later when the test silently stops meaning anything.

**Worked example.** Suppose you're building the core of an "auction sniper" — a program that watches an online auction and places a last-moment bid on the user's behalf (the running example Freeman & Pryce use throughout the book). The very first behavior worth testing might be: "when the sniper hears that the auction is closed, it should record that it lost, if it never placed a winning bid." You write:

```
@Test
public void reportsLostWhenAuctionClosesImmediately() {
    sniper.auctionClosed();
    assertEquals(SniperState.LOST, sniper.getState());
}
```

This fails immediately (red) — there's no `auctionClosed()` method yet, or it doesn't set the state. You add just enough code to make `getState()` return `LOST` after `auctionClosed()` is called (green). Only then do you look at whether the resulting code is well-structured (refactor) — perhaps introducing a `SniperState` enum instead of a raw string, now that you have a passing test guaranteeing you won't break the behavior while you clean it up.

### Fast feedback compounds — it isn't just about individual bugs
A single fast test doesn't feel dramatically different from a single slow one. The value shows up as a *system property* over the life of a codebase: hundreds of tests running in seconds mean every developer, on every change, gets an almost-instant answer to "did I break anything?" This changes behavior. Freeman & Pryce note that teams with a fast, trustworthy test suite make bolder changes, because the cost of being wrong is a few seconds of red, not a multi-day bug hunt. Teams without one become conservative, because every change is a gamble against a slow, uncertain feedback signal — which, ironically, makes the codebase degrade faster, since nobody dares clean it up.

### "Fast" means fast in wall-clock time, not just fast in principle
This is a practical, easy-to-miss point: a test suite that is logically correct but takes 20 minutes to run does not deliver the feedback-loop benefit TDD is built on, because developers stop running it on every change — they batch changes, run it occasionally, and the loop widens back toward the old integrate-then-discover pattern. Freeman & Pryce treat test speed as a first-class design constraint: tests that hit real databases, real networks, or sleep for real time are to be minimized and isolated (a concern this subject returns to directly in `goos/08` on asynchronous testing and `goos/06` on ports and adapters, which push slow, external things to the edges of the system precisely so the fast unit-level feedback loop can stay fast).

## Pros
- Feedback on correctness arrives in seconds, while the context of the change is still in short-term memory, making bugs dramatically cheaper to fix than when found later.
- Forces an outside-in, caller's-eye view of an interface before it's implemented, which tends to produce simpler, more usable APIs.
- A growing suite of fast tests becomes a permanent regression safety net that makes later changes (including refactoring) safer and less feared.

## Cons
- The discipline has real overhead per increment — writing a test first, for every small step, is slower in the moment than writing code freehand, even though it's usually faster in aggregate.
- Badly written tests (tightly coupled to implementation details) can slow the loop down over time rather than speed it up, turning "fast feedback" into "constant false alarms" — a failure mode this subject covers in `goos/10`.
- TDD alone doesn't guarantee good design; it creates design pressure, but a developer can still write a well-tested, badly structured system if they ignore what the tests are telling them (see `goos/09` on listening to tests).

## Alternatives
- **Test-after development** — write the code first, then tests to verify it works and guard against regressions. Faster to get first-draft code out, but loses the design-pressure benefit and tends to produce tests that mirror the implementation rather than the intended behavior.
- **Manual/exploratory testing only** — relies on a human clicking through the system. Catches things automated tests might miss (real usability issues) but the feedback loop is measured in minutes-to-hours per check, not seconds, and doesn't scale as a regression net.
- **Formal upfront specification with separate QA verification** — a heavier-weight process (common in some regulated or safety-critical domains) that front-loads correctness thinking into a specification phase, verified later by a separate team; slower feedback but sometimes required for compliance reasons TDD doesn't address on its own.

## When to use it
Use TDD whenever you're actively developing behavior you're not yet certain how to implement, or in a codebase whose correctness genuinely matters and will be maintained over time. It shines especially where requirements are still being discovered (the loop of writing a test, watching it fail, and making it pass is also a loop of clarifying what "done" means).

## When NOT to use it
Don't force TDD onto pure exploration/spike code you intend to throw away — the design-pressure benefit is wasted on code you won't keep, and the overhead just slows down learning. Also be wary of TDD-ing against a design you already know is wrong just because "the process says test first" — the practice serves good design, not the other way around; sometimes the right move is to stop, think, sketch a design on paper, and only then resume writing tests against it.

## Key takeaways / mental model
Think of each red-green-refactor cycle as a single, checked step forward — not "write tests" as a separate activity bolted onto "writing code," but a fused single activity where each step is verified before you take the next one. The tightness of the loop (both in the sequence of steps and in wall-clock test speed) is the entire point; anything that widens the loop back toward "discover problems later" erodes the technique's core value.

## Self-check questions
1. A colleague says "I write my tests right after I write the function, so it's basically the same as TDD." What specific benefit of test-first development do they lose by writing the test second, even if the resulting test suite ends up covering the same lines of code?
2. Your team's test suite takes 25 minutes to run, so developers only run it before pushing at the end of the day. Using the ideas in this lesson, explain what feedback-loop property has been lost, and what effect you'd predict on the team's willingness to refactor.
3. Give an example (not from this lesson) of a situation where skipping TDD in favor of a quick spike is the right call, and explain what would change once that spike needed to become production code.

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part I, Chapter 1: "What Is the Point of Test-Driven Development?"
