---
id: pragmatic-programmer/08
subject: pragmatic-programmer
title: Debugging and Rubber Ducking
slug: debugging
status: drafted
mastery:
seniority: junior
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 3
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Debugging and Rubber Ducking

## TL;DR
Debug scientifically: form a hypothesis about the cause, design the smallest test that would prove or disprove it, and never fix a symptom without understanding the underlying mechanism — or you'll ship a fix that doesn't actually fix it. "Rubber ducking" (explaining the problem out loud, even to an inanimate object) forces the same rigor by making you articulate assumptions you'd otherwise skip past silently.

## The idea
The book's central reframing: debugging is not "poke at the code until it seems to work," it's applying the scientific method to a system that's behaving unexpectedly. You have an observation (the bug), you form a hypothesis (what you think is causing it), you design an experiment (a test, a log line, a breakpoint) that would distinguish "hypothesis true" from "hypothesis false," and you run it before touching the fix. Skipping straight to "let me just try changing this" is what produces bugs that seem fixed, ship, and come back a week later under slightly different conditions — because the actual cause was never confirmed, only guessed at.

"Rubber ducking" is the social/psychological trick that makes this rigor easier: explaining a problem out loud, step by step, in enough detail that a rubber duck (or a colleague, or a chat window) could follow it, frequently surfaces the bug *before* you finish the explanation — because verbalizing forces you to make explicit every assumption you'd silently skip while just staring at the code.

## How it works

### "Select Isn't Broken" — start by trusting the platform, but verify, don't assume
The chapter's ironic title (referencing how often people blame a language's `select` statement or a well-tested library before considering their own code) captures a real bias: it's tempting to suspect the framework, the compiler, or a library before your own code, because blaming your own logic feels worse. The pragmatic discipline: **don't assume, verify** — check the actual behavior with a minimal, isolated test before concluding "the library is broken," because in the overwhelming majority of real cases, it isn't. But this cuts both ways: don't blindly assume the library is *correct* either if you haven't actually checked — verify, in both directions, rather than assuming based on which explanation is more comfortable.

### The core debugging loop
1. **Reproduce reliably.** An intermittent bug you can't reproduce on demand is nearly unfixable — invest first in making it reproducible (same input, same environment, same sequence of steps), even if that means adding logging or a script that triggers it repeatedly.
2. **Form a specific hypothesis.** Not "something's wrong with the auth flow" — instead, "I believe the token refresh happens *after* the expiry check runs, causing a false 401." A vague hypothesis can't be disproven, which means it can't actually guide you.
3. **Design the smallest test that discriminates.** What's the cheapest experiment (a log statement, a debugger breakpoint, a unit test with a crafted input) that would come back differently depending on whether the hypothesis is true or false? If your planned test would look the same either way, it's not testing the hypothesis — redesign it.
4. **Run it, and believe the result — even if it's not what you expected.** This is where discipline usually breaks down: people run the test, see a result that contradicts their favorite theory, and rationalize it away instead of updating the hypothesis. Trust the data over your intuition.
5. **Fix the cause, not the symptom.** Once the actual mechanism is confirmed, fix *that* — and specifically resist the tempting shortcut of a patch that makes the immediate symptom go away (e.g., catching and swallowing an exception) without addressing why it occurred, because the underlying condition will resurface elsewhere.

### Worked example
Bug report: "Users occasionally see someone else's profile picture flash for a second before their own loads." 

- **Bad approach**: immediately add a loading spinner to hide the flash. This "fixes" the visible symptom but leaves the actual bug (a shared cache being read before the current user's data overwrites it) live — it'll resurface as a data-leak bug report eventually, possibly a serious one, once someone notices the wrong picture *persists* under different timing.
- **Scientific approach**: 
  1. Reproduce: find that it happens specifically on fast navigation between two users' profiles on a slow network — a timing-dependent bug, so the reproduction needs throttled network conditions, not just "click around."
  2. Hypothesis: "the profile-picture component reads from a shared, keyed-by-nothing cache slot that the previous profile view populated, and briefly renders it before the new fetch resolves and overwrites the slot."
  3. Discriminating test: add a temporary log line that prints the cache key being read at render time versus the currently-active user ID. If they mismatch during the flash window, hypothesis confirmed; if they always match, hypothesis wrong and something else is happening.
  4. Result: keys mismatch during the flash window — hypothesis confirmed.
  5. Real fix: key the cache by user ID (not a single global slot) so a stale read simply can't return another user's data, regardless of timing. This fixes the actual mechanism — the *class* of bug (transient wrong-user render) becomes structurally impossible, not just less visible.

### Rubber ducking as forced articulation
Before escalating a hard bug to a colleague, the practice: explain the problem out loud from the top — what you expected, what actually happened, what you've already ruled out and how — as if to someone with zero context. Many bugs are found mid-explanation, at the exact sentence where you have to say something you'd normally think past too fast to notice ("...and then the callback fires, which — wait, why would it fire twice here?"). This works because writing/speaking is slower and more linear than thinking, and it forces you to notice gaps your brain was silently filling in.

## Pros
- Produces fixes that actually eliminate the root cause, preventing the bug (and its relatives) from resurfacing under different conditions.
- Converts "I have no idea why this is happening" into a structured, time-bounded investigation instead of open-ended despair.
- Rubber ducking is free, requires no tooling, and frequently resolves the bug before you even need a second person.

## Cons
- Rigorous hypothesis-driven debugging takes real discipline under deadline pressure, when "just try something" feels faster (and sometimes is, for genuinely trivial bugs).
- Reproducing intermittent, environment-dependent, or timing-dependent bugs can itself be a substantial and frustrating investment before the "real" debugging even starts.
- Explaining a problem to a person (versus a literal rubber duck) costs someone else's time and attention, which is a real cost to weigh against just-in-time self-debugging.

## Alternatives
- **Trial-and-error / shotgun debugging** — try plausible fixes without confirming the mechanism first. Occasionally faster for genuinely trivial, obvious bugs, but risks shipping a fix that doesn't address the real cause (see the profile-picture example above).
- **Bisection (e.g., `git bisect`)** — narrow down *when* a regression was introduced by binary-searching commit history, complementary to hypothesis-driven debugging rather than a replacement: bisection finds *which change* caused it, but you still need to understand *why* that change caused it.
- **Static analysis / linters** — catch a class of bugs before they're ever observed at runtime, sidestepping live debugging entirely for the bugs they can detect (null derefs, type mismatches) — but they don't help with logic or timing bugs the tools can't statically reason about.

## When to use it
Apply the full hypothesis-driven loop for any bug whose cause isn't immediately, unambiguously obvious — especially intermittent, production-only, or "worked on my machine" bugs where guessing is expensive. Reach for rubber ducking whenever you're stuck for more than a few minutes, before escalating to interrupt a colleague.

## When NOT to use it
Don't over-formalize trivial, obvious bugs (a typo'd variable name causing an immediate, deterministic crash) with a full scientific-method write-up — just fix it. The rigor should scale with the bug's actual ambiguity and cost, not be applied uniformly to everything.

## Key takeaways / mental model
Before touching code to "fix" a bug, be able to state: "I believe X is happening because Y, and here's the smallest experiment that would prove or disprove that." If you can't fill in that sentence, you're not ready to fix it yet — you're about to guess.

## Self-check questions
1. Describe a bug you fixed by treating the symptom rather than the cause, and what happened later as a result.
2. What makes a hypothesis "not specific enough" to be useful for debugging? Give a vague hypothesis and a specific rewrite of it.
3. Why does the book warn against reflexively blaming the library/framework/compiler, and separately, against reflexively trusting it? What's the actual discipline being asked for?
4. Walk through how you would make an intermittent, "only happens in production under load" bug reliably reproducible enough to debug.

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 3: "Basic Tools" (Debugging section).
