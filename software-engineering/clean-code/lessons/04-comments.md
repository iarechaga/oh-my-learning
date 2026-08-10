---
id: clean-code/04
subject: clean-code
title: "Comments: Good, Bad, and Unnecessary"
slug: comments
status: drafted
mastery:
seniority: junior
source: Clean Code (Robert C. Martin), Chapter 4
prerequisites: [clean-code/02, clean-code/03]
created: 2026-08-10
updated: 2026-08-10
---

# Comments: Good, Bad, and Unnecessary

## TL;DR
A comment is an admission that the code itself failed to express intent — sometimes justified, often not. Prefer making the code say what a comment would say (better names, extracted functions) over writing a comment to compensate, because comments can silently drift out of sync with the code they describe while the code itself never can.

## The idea
This chapter's provocative framing: every comment is, in a sense, a failure — an admission that we couldn't figure out how to express ourselves clearly enough in code alone, so we added English (or another natural language) as a crutch. That doesn't mean comments are always wrong; some information genuinely cannot be expressed in code (the reason a workaround exists, a legal notice, a warning about a non-obvious consequence). But it does mean a comment should be held to a real justification bar, not written reflexively — and that bar is: *would improving the code itself (a name, a function extraction) make this comment unnecessary?* If yes, do that instead. If no, the comment earns its place.

The deeper risk the chapter emphasizes: **comments rot.** Code is executed, tested, and reviewed continuously — if it's wrong, something eventually breaks and someone notices. A comment is inert; nothing forces it to stay accurate as the code around it changes, and developers reliably forget to update comments when they change the code nearby. A stale comment doesn't just fail to help — it actively misleads, and a reader has no built-in way to know whether a given comment is still true or has been stale for two years.

## How it works

### Good comments — the kinds that earn their place
- **Legal comments** — license headers, copyright notices, required by policy or law, not aimed at explaining the code.
- **Informative comments explaining intent that genuinely can't be captured in code** — e.g., explaining *why* a regex pattern matches what it matches, when the pattern itself is dense and non-obvious even to an experienced reader.
- **Warning of consequences** — `// this test is slow (loads full DB), run only in the nightly suite` tells a reader something the code's structure alone wouldn't convey.
- **TODO comments** — acceptable when they're specific, attributed, and tracked (see `pragmatic-programmer/02`'s "board it up" — this is the same discipline), not vague, permanent, unowned markers nobody revisits.
- **Amplification** — emphasizing that something apparently minor is actually critical, e.g., `// the trim() here is essential — trailing whitespace breaks the downstream parser`, where the *reason* something matters isn't visible just from reading the line.

### Bad comments — the kinds that should be deleted or fixed at the source
- **Redundant comments that just restate the code**: `i++; // increment i` adds zero information and adds visual noise a reader has to read and discard.
- **Misleading comments**: a comment describing behavior slightly different from what the code actually does — worse than no comment, because a reader trusts it and is actively misled.
- **Mandated/boilerplate comments** (e.g., a policy requiring a Javadoc block on every method, even trivial getters) — produce comments with no real content, purely to satisfy a checklist, diluting the signal of the comments that do matter.
- **Journal comments** — a changelog embedded at the top of a file (`// 2019-03-01, Alice: fixed bug`, `// 2020-11-12, Bob: added validation`) — this is what version control is *for*; a file-embedded journal duplicates and inevitably falls behind what `git log`/`git blame` already track accurately.
- **Commented-out code** — dead code left "just in case," which the book treats as actively harmful: nobody dares delete it because they don't know if it's still needed, and it accumulates indefinitely because nobody has the confidence version control (which actually preserves history reliably) gives them to just remove it.
- **Noise comments and comments that don't correspond to the code below them**, often left behind after refactoring moved the code the comment was originally about.

**Worked example — a comment that should be a rename instead:**
```
# Before
x = x - 1  # decrement retry counter

# After — the comment becomes unnecessary
retries_remaining -= 1
```
The "before" comment exists purely because `x` is a bad name (see `clean-code/02`); fixing the name at the source removes the need for the comment entirely, and unlike the comment, the improved name can never drift out of sync — it's read and relied upon by every caller, not passively sitting beside code nobody re-checks it against.

**Worked example — a comment that genuinely earns its place:**
```
# We intentionally retry with jitter here (not fixed backoff) to avoid a
# thundering-herd effect when many clients reconnect after the same outage.
time.sleep(random.uniform(0, backoff_seconds))
```
This comment explains a *design decision's reasoning* — information that isn't recoverable just by reading the `random.uniform` call, no matter how well-named the surrounding code is. Removing this comment would genuinely lose information a future maintainer needs (they might "simplify" the jitter away, not understanding why it was there).

### The real discipline: try the code fix first
Before writing a comment to explain something, the book's implied workflow is: ask whether a better name, an extracted function, or a small refactor would make the comment unnecessary. Reach for a comment only once you've confirmed the information genuinely can't live in the code itself — a design rationale, a non-obvious consequence, a legal requirement — not as the default first response to "this is confusing."

## Pros
- Removing unnecessary comments in favor of clearer code produces information that can't silently rot, because it's exercised by every reader and every test, not passively sitting nearby.
- The remaining, genuinely-necessary comments carry more signal once the redundant/noise comments around them are gone — a reader can trust that a comment they encounter is there for a real reason.
- Deleting commented-out code and journal comments removes clutter and defers to version control, which does that job more reliably.

## Cons
- A "comments are a code smell" stance taken too literally can lead to under-commenting genuinely non-obvious design rationale, leaving future readers to reconstruct "why" from git history or guesswork.
- Some domains (regulated industries, safety-critical code, complex algorithms translated from a paper) genuinely benefit from more explanatory comments than typical application code, and a blanket "minimize comments" policy can hurt there.
- Team habits around comments (a policy mandating documentation comments on public APIs, for instance) may conflict with this chapter's preferences for legitimate external reasons (generated API docs, IDE tooltips) that aren't really about "comments are bad."

## Alternatives
- **Self-documenting code as the sole strategy, with essentially no comments** — the purest application of this lesson; works well for straightforward logic, strains when the "why" behind a decision genuinely has no code-shaped home.
- **External design documents / ADRs** (see `architecture/fundamentals`) — capture the "why" behind larger decisions outside the code entirely, avoiding in-code comment rot at the cost of the reader needing to know the doc exists and go find it.
- **Doc-comment tooling (Javadoc, docstrings, TSDoc)** — generate structured, tool-consumed documentation from comments; a different category from inline explanatory comments, since these serve external API consumers rather than explaining internal logic to code readers.

## When to use it
Write a comment when you've genuinely exhausted the "can the code say this itself" options and the remaining information is about *why* (a design decision, a non-obvious trade-off, a warning) rather than *what* or *how* — the latter two should almost always be expressible through naming and function extraction instead.

## When NOT to use it
Don't write a comment to compensate for a bad name or an overly complex function — fix the name or extract the function instead (see `clean-code/02` and `clean-code/03`). Don't leave commented-out code, journal-style changelogs, or comments that just restate the line below them — delete all three; version control already does that job.

## Key takeaways / mental model
Before writing a comment, ask: "could a better name or a small refactor make this comment unnecessary?" If yes, do that instead — it can't rot. If no, write the comment, because you've found genuine information (a "why," a warning, a legal requirement) that code structure alone can't carry.

## Self-check questions
1. Find a comment in code you've written that just restates what the line already says. Rewrite the code so the comment becomes unnecessary.
2. Give an example of a comment that genuinely earns its place because it explains "why," not "what," and couldn't be replaced by a better name.
3. Why does the book treat commented-out code as actively harmful rather than merely unnecessary?
4. Why can a stale, misleading comment be worse than no comment at all? Give a concrete failure scenario.

## References
- Clean Code: A Handbook of Agile Software Craftsmanship (Robert C. Martin), Chapter 4: "Comments".
