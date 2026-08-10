---
id: philosophy-of-software-design/09
subject: philosophy-of-software-design
title: Comments Describe Things the Code Cannot
slug: comments
status: drafted
mastery:
seniority: mid
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapters 12-13
prerequisites: [clean-code/04, philosophy-of-software-design/04]
created: 2026-08-10
updated: 2026-08-10
---

# Comments Describe Things the Code Cannot

## TL;DR
Ousterhout takes a notably more comment-friendly stance than Clean Code: comments should capture the "abstraction" of a piece of code — precisely the information hidden by information hiding (`philosophy-of-software-design/04`) that a reader has no other way to recover. Rather than "minimize comments," his test is "write the comment that describes what the interface promises and why the implementation does what it does, at a level of detail the code itself structurally cannot express."

## The idea
`clean-code/04` argued a comment is often an admission that the code failed to express itself, and pushed toward removing comments in favor of better names and extraction wherever possible. Ousterhout's framing, while not contradicting that a bad comment is worse than no comment, starts from a different premise: **good code hides information (per `philosophy-of-software-design/04`) precisely so callers don't need to know it — but "not needing to know it to use the module" and "having no way to learn it at all" are different things**, and comments are the mechanism for making hidden design rationale discoverable to the specific readers who *do* need it (someone modifying the module's internals, someone debugging a subtle interaction) without forcing every casual caller to learn it just to use the interface.

This reframes comments not as a fallback for bad naming, but as a **first-class, deliberate complement to abstraction**: the interface's job is to let callers *not need* certain information; the comment's job is to make that same information available to the smaller set of readers who genuinely do need it (implementers, debuggers, future modifiers).

## How it works

### Two distinct kinds of comments, serving different readers
- **Interface comments** — describe what a caller needs to know to use a module/method correctly, without needing to read its implementation: what it does, its parameters' meaning and constraints, what it returns, what side effects or exceptions to expect. These serve the "I just want to use this deep module without reading its internals" reader — directly supporting `philosophy-of-software-design/03`'s deep-module ideal, since a genuinely deep module's whole value proposition depends on a caller being able to trust its documented interface without reading the implementation.
- **Implementation comments** — describe *why* the code inside a method does what it does: non-obvious algorithmic choices, the reasoning behind a specific approach, a workaround for a specific bug or constraint. These serve the "I need to modify or debug this module's internals" reader — a different audience than the interface comment's, with different needs.

**Worked example — an interface comment earning its place, precisely because it captures information hiding is deliberately hiding:**
```
def get_verified_email(user_id: int) -> str | None:
    """Returns the user's verified email address, or None if the user
    has no email on file, or has an email that has not completed the
    verification flow. Does NOT distinguish between these two cases —
    callers needing that distinction should query User.email_status directly."""
```
Nothing about the function's *name* or *signature* alone tells a caller that "no email" and "unverified email" are deliberately conflated into the same `None` return — that's a genuine design decision (information hiding, per `philosophy-of-software-design/04`: the function deliberately hides the distinction from most callers who don't need it) that a caller *does* need to know about, specifically to avoid wrongly assuming `None` means "definitely has no email at all." A better name alone (per Clean Code's usual first-resort fix) can't carry this nuance — this is exactly the kind of information a comment, not a rename, is the right tool for.

### The comment should be written at a different level of detail than the code
A comment that merely restates the code in English (`clean-code/04`'s "redundant comment" antipattern) fails Ousterhout's test just as much as Clean Code's: `# increment retries` above `retries += 1` adds nothing, because it's at the *same* level of detail as the code, just in a different language. A comment earns its place specifically when it operates at a genuinely *different* level — either more abstract (summarizing the overall purpose/effect of a block, so a reader can skip the details if the summary is all they need) or containing information the code's syntax structurally cannot express at all (why this specific approach was chosen over an alternative, what invariant this section is maintaining, what edge case a seemingly-unnecessary line is actually guarding against).

### Write comments as you write the code, not as an afterthought
A practical discipline the book stresses: writing the interface comment *before or during* implementation (not after, as cleanup) tends to clarify your own thinking about the abstraction you're actually building — if you struggle to write a clean, precise interface comment, that's often a signal the interface itself isn't yet well-designed, not just that the documentation is hard to write. This mirrors `code-complete/12`'s "write the try/catch skeleton first" discipline: writing the comment early is a design tool, not merely a documentation task performed after the design is already settled.

### Comments and Deep Modules — a mutually reinforcing relationship
This chapter connects directly back to `philosophy-of-software-design/03`: a deep module's whole value depends on callers being able to trust a simple interface without reading the implementation — and that trust has to come from *somewhere*, since callers can't verify the implementation's behavior by inspection every time. A precise, well-written interface comment is what makes that trust possible without inspection; a deep module with no interface documentation forces every caller back into reading the implementation anyway, which quietly defeats much of the depth the module's structure was trying to provide in the first place.

## Pros
- Interface comments let callers genuinely benefit from a deep module's simple interface without needing to read its implementation, which is the entire point of designing a deep module in the first place.
- Implementation comments capture design rationale that would otherwise be lost, forcing future maintainers to either guess or painstakingly reverse-engineer the original reasoning.
- Writing comments during design (not after) surfaces interface weaknesses early, when they're still cheap to fix.

## Cons
- Comments still carry the "rot" risk `clean-code/04` raises — nothing forces an interface or implementation comment to stay accurate as code changes around it, and Ousterhout's more comment-friendly stance doesn't eliminate that risk, it just accepts it as a worthwhile trade for the information comments uniquely carry.
- Writing genuinely good interface comments (capturing exactly what's hidden and why, without merely restating the signature) is a real skill that takes deliberate practice, and it's easy to produce comments that look thorough but don't actually add the specific missing information a deep module's comment should.
- A team without a shared discipline for maintaining comments as code evolves can end up with the worst of both worlds — comments that were once genuinely valuable but have since drifted stale, actively misleading readers who trust them.

## Alternatives
- **Clean Code's minimize-comments stance** (`clean-code/04`) — the more skeptical default, favoring naming/extraction fixes over comments wherever possible; the two books' positions genuinely disagree here, and holding both in tension (per this subject's own framing) is more useful than picking one as simply "correct."
- **Executable documentation (doctest-style examples, type annotations as partial documentation)** — captures some interface information in a form that's automatically checked against the actual code, reducing (though not eliminating) the staleness risk plain-text comments carry.
- **Architecture Decision Records** (see `architecture/fundamentals`) — for larger design rationale that doesn't fit naturally at the level of a single module's comment, capturing the same "why," but at a coarser architectural grain and in an external document rather than inline.

## When to use it
Write an interface comment for any module whose interface deliberately hides information a *some* callers genuinely need to know (an edge-case behavior, a conflated special case, a non-obvious constraint) — even though the interface's whole point is that *most* callers don't need to know it. Write implementation comments for non-obvious design or algorithmic choices that a future maintainer would otherwise have to reconstruct from scratch.

## When NOT to use it
Don't write a comment that merely restates the code at the same level of detail — that's `clean-code/04`'s legitimate "redundant comment" critique, which this chapter doesn't dispute. Don't treat a thorough-looking comment as a substitute for actually designing a clean interface — if the comment needs to explain away a confusing or poorly-designed interface, fixing the interface (as Clean Code would argue) is usually the better investment than documenting around it.

## Key takeaways / mental model
Ask, before writing (or skipping) a comment: "is there information here that a caller or maintainer genuinely needs, that the code's structure cannot express on its own?" If yes, that's exactly the kind of comment this chapter argues for — write it at a different level of detail than the code, and treat writing it as part of the design process, not cleanup afterward.

## Self-check questions
1. Using the `get_verified_email` example, explain precisely what information the comment carries that no amount of renaming could have captured instead.
2. What's the difference between an interface comment and an implementation comment, and who is each one's intended reader?
3. Why does the book argue writing comments early (during design) can improve the design itself, not just document it?
4. Where do Ousterhout's and Clean Code's views on comments genuinely conflict, and where do they actually agree once you look closely?

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 12: "Comments Should Describe Things that Aren't Obvious from the Code" and Chapter 13: "Comments: Choosing Names and Writing Them at the Right Time".
- See also: `clean-code/04` (Comments: Good, Bad, and Unnecessary) for the deliberately contrasting stance this lesson engages with directly.
