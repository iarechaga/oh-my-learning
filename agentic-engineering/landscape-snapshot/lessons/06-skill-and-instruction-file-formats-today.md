---
id: landscape-snapshot/06
subject: landscape-snapshot
title: Skill and Instruction File Formats Today
slug: skill-and-instruction-file-formats-today
status: drafted
mastery:
seniority: mid
source: "Anthropic, Skill authoring best practices documentation (accessed August 2026, platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); Anthropic, Agent Skills overview documentation (accessed August 2026); agents.md, the AGENTS.md open specification (accessed August 2026, agents.md); MorphLLM, AGENTS.md Spec 2026: Recommended Sections + AGENTS.md vs CLAUDE.md vs .cursorrules (2026); this repository's own CLAUDE.md and AGENTS.md as inspectable, currently-in-use examples of the conventions described"
durability: perishable
next_review: 2026-11
prerequisites: [instruction-and-context-design/08]
created: 2026-08-10
updated: 2026-08-10
---

# Skill and Instruction File Formats Today

## TL;DR
As of August 2026, two file-format conventions dominate how agentic coding tools consume standing instructions: `SKILL.md` (Anthropic's format for triggerable, on-demand skills, with a strict two-field YAML frontmatter and a 500-line body guideline) and `AGENTS.md` (a Linux Foundation-stewarded, frontmatter-free plain-Markdown convention for always-loaded repository context, adopted by 25+ coding agents including this repository's own use of `CLAUDE.md`/`AGENTS.md`). `instruction-and-context-design/08` teaches the durable four-step process for authoring good instructions in either shape; this lesson supplies the exact current syntax those instructions get written in.

> **Snapshot date: August 2026.** This lesson is tagged `durability: perishable` and reviewed quarterly (`next_review: 2026-11`) - treat every specific field name, limit, and syntax example below as accurate as of the date above, not as a permanent fact. See `agent-docs/fast-moving-domain-policy.md`.

## The idea
`instruction-and-context-design/08` is deliberately silent on file syntax - it teaches scoping, trigger-writing, body structure, and the inline-vs-file split as decisions that apply regardless of what the resulting file is literally named or how its frontmatter is formatted, because those decisions would otherwise date the moment a vendor changed a field name. That silence has a cost: a learner who has internalized the four-step process still needs to know, concretely, what a `SKILL.md` file's YAML frontmatter is allowed to contain today, or what `AGENTS.md` expects, before they can ship anything. This lesson exists to pay that cost in one place, dated, instead of scattering perishable syntax details across an otherwise-durable subject.

The two formats solve different problems, which is why both exist rather than one superseding the other. `SKILL.md` is for *on-demand* material: something loaded only when a specific, describable task triggers it, which is why its two required frontmatter fields (`name` and `description`) exist purely to support cheap, always-resident trigger matching before the expensive body ever loads - the exact tier-2-loading mechanism `instruction-and-context-design` covers elsewhere in that subject. `AGENTS.md` is for *always-loaded* material: build commands, code-style rules, and repository-wide conventions that every task needs regardless of what it is, which is why it carries no frontmatter or trigger mechanism at all - there is nothing to decide whether to load, because it is always loaded.

## How it works

### SKILL.md: exact current frontmatter and structure
As documented by Anthropic (accessed August 2026), the `SKILL.md` frontmatter requires exactly two fields, each with hard validation rules:

```yaml
---
name: processing-pdfs
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---
```

- **`name`**: maximum 64 characters; lowercase letters, numbers, and hyphens only; no XML tags; cannot contain the reserved words "anthropic" or "claude". Current naming guidance favors gerund form (`processing-pdfs`, `analyzing-spreadsheets`) over vague nouns (`helper`, `utils`).
- **`description`**: must be non-empty, maximum 1,024 characters, no XML tags, must be written in third person (not "I can help you..." or "You can use this to...") because the description text is injected directly into the system prompt alongside every other skill's description, and inconsistent point-of-view degrades the model's ability to select the right skill from a large pool.

Beyond the two required fields, the body is unrestricted Markdown, with one hard operational guideline: **keep the `SKILL.md` body under 500 lines**; content beyond that budget should be split into separate reference files that the body links to and the agent loads only on demand. The full directory shape looks like:

```text
pdf/
  SKILL.md              # Main instructions (loaded when triggered)
  FORMS.md              # Form-filling guide (loaded as needed)
  reference.md          # API reference (loaded as needed)
  examples.md           # Usage examples (loaded as needed)
  scripts/
    analyze_form.py     # Utility script (executed, not loaded)
    fill_form.py
    validate.py
```

Two syntax rules current guidance treats as load-bearing, not stylistic: use forward slashes in every file path even on Windows (`scripts/helper.py`, never `scripts\helper.py`), and keep reference-file links **one level deep from SKILL.md** - a file `SKILL.md` links to should not itself link to a third file, because when Claude encounters a reference nested two hops deep it may only partially read it (using something like `head -100`), producing incomplete information the author never intended.

### AGENTS.md: exact current conventions
`AGENTS.md` is a plain Markdown file at a repository's root with **no required frontmatter, no YAML, no special syntax at all** - "just standard Markdown," per the specification. There is no `name`/`description` trigger mechanism because there is nothing to trigger: any coding agent that supports the convention reads the file at the start of every task in that repository. Recommended (not required) sections, per the specification, include:

```markdown
# Project overview
<what this repo is, in a sentence or two>

## Build and test commands
<exact commands, not paraphrased instructions>

## Code style guidelines
<conventions specific to this repo>

## Security considerations
<anything an agent must never do here>
```

As of August 2026, `AGENTS.md` is stewarded by the Agentic AI Foundation under the Linux Foundation, having been formalized as an open specification in August 2025 through collaborative work led by OpenAI with Google, Cursor, and Factory as early participants, and donated to the Linux Foundation in December 2025. It is now reported in use across 60,000+ open-source repositories and supported by 25+ coding agents, including Claude Code, OpenAI Codex, Cursor, and VS Code.

**A live example, one directory away.** This repository's own root `CLAUDE.md` (Claude Code's file-discovery convention, functionally the same always-loaded-context role as `AGENTS.md`) is exactly this pattern in practice: no frontmatter, headed sections ("Core loop," "Non-negotiables," "Quick references"), and load-on-demand pointers to `agent-docs/*.md` files for anything that would otherwise bloat the always-loaded body - the same progressive-disclosure principle `SKILL.md`'s file-splitting guidance applies, expressed without any frontmatter mechanism at all because the whole file is meant to be always-loaded, not conditionally triggered.

### CLAUDE.md and vendor-specific always-loaded conventions
Several coding-agent products maintain their own always-loaded convention file name in parallel with (or as a precursor to) `AGENTS.md` - `CLAUDE.md` for Claude Code being the example this repository itself uses, and `.cursorrules` historically serving a similar role for Cursor before that tool added `AGENTS.md` support. Current practitioner guidance (2026) generally recommends treating `AGENTS.md` as the primary, tool-agnostic file when targeting multiple agents, with a short pointer file (or a symlink) for any tool that still looks for its own vendor-specific filename first - avoiding maintaining the same content twice under different names.

### A comparison at a glance

| | `SKILL.md` | `AGENTS.md` / `CLAUDE.md` |
| --- | --- | --- |
| Loaded | On-demand, when the `description` matches the current task | Always, at the start of every task in the repo |
| Frontmatter | Required: `name` (<=64 chars), `description` (<=1,024 chars) | None |
| Body limit | ~500 lines guideline before splitting into reference files | No fixed limit; same progressive-disclosure instinct applies in practice |
| Governance | Anthropic-specific format | Linux Foundation / Agentic AI Foundation open specification |
| Analogous to | A skill in `instruction-and-context-design`'s tier-2 (loaded only when triggered) | Always-loaded system context, tier-1 |

## Pros
- Both formats are genuinely simple to hand-author - `SKILL.md`'s frontmatter is two fields with clear validation rules, and `AGENTS.md` has no required syntax at all, so the barrier to adopting either is authoring discipline (`instruction-and-context-design/08`'s four steps), not tooling.
- `AGENTS.md`'s Linux Foundation stewardship and 25+-tool adoption as of August 2026 makes it a comparatively durable choice among file-format conventions in this fast-moving domain - a repository investing in one `AGENTS.md` file is reasonably betting it will be read by tools that don't exist yet, more so than most conventions in this subject.
- `SKILL.md`'s hard character limits and third-person-description rule are concrete, checkable rules a linter or reviewer can enforce mechanically, unlike the softer craft judgment `instruction-and-context-design/08` teaches for what goes inside the body.

## Cons
- The two formats are not interchangeable, and conflating them is a common authoring mistake: putting always-needed repo context inside a `SKILL.md` (where it only loads when triggered) or putting narrow, task-specific procedure inside `AGENTS.md` (where it loads on every single task, wasting the always-loaded budget lesson 03 of `instruction-and-context-design` warns against) both defeat the point of choosing one format over the other.
- Field-level limits are exact and unforgiving (a `name` over 64 characters or a `description` over 1,024 characters is a hard validation failure, not a soft warning) - authoring against memory rather than checking the current limit risks a skill that silently fails to register.
- Multiple vendor-specific filenames (`CLAUDE.md`, `.cursorrules`, and others) coexisting alongside `AGENTS.md` creates real duplication risk for teams targeting more than one coding agent, and the "point one file at another" mitigation is a workaround for fragmentation, not a solved problem.

## Alternatives
- **A single monolithic always-loaded instructions file, no skill/trigger split at all** - simpler to author, but reintroduces the always-loaded-budget problem `instruction-and-context-design`'s lesson 03 exists to avoid; reasonable only for a very small project where the total instruction volume never approaches a budget concern.
- **MCP-served instructions or tools instead of a static file** - covered in `model-context-protocol`; trades static, human-editable files for a live server that can serve dynamic or parameterized guidance, at the cost of running and maintaining that server.
- **IDE- or tool-native configuration formats** (e.g., editor-specific rule files predating `AGENTS.md`) - still in use where a team has standardized on a single tool and has no cross-tool portability need; the trade-off `AGENTS.md`'s open-specification adoption is specifically trying to make unnecessary going forward.

## When to use it
Reach for `SKILL.md` for any instruction that only some tasks need - the exact bar `instruction-and-context-design/07` sets for when something is skill-shaped. Reach for `AGENTS.md` (or this repository's `CLAUDE.md`) for anything every task in the repository needs regardless of what it is: build commands, non-negotiable rules, and repo-wide conventions. When targeting more than one coding agent, author the content once in `AGENTS.md` and add a thin pointer for any tool that insists on its own vendor filename, per current practitioner guidance.

## When NOT to use it
Do not put narrow, occasionally-needed procedure into an always-loaded `AGENTS.md`/`CLAUDE.md` file just because it is convenient to write once - that is exactly the always-loaded-budget mistake `instruction-and-context-design` warns against, made worse because `AGENTS.md` has no mechanism to load it conditionally at all. Do not treat the specific character limits or field names in this lesson as permanent - verify against the current Anthropic and agents.md documentation (see References) before shipping a skill that depends on an exact limit, since this entire lesson is scoped `perishable` for exactly this reason.

## Key takeaways / mental model
Two shapes, two jobs: `SKILL.md` is triggerable, tier-2, on-demand material with a strict two-field frontmatter contract; `AGENTS.md`/`CLAUDE.md` is always-loaded, tier-1, frontmatter-free repository context. The choice between them is the same tier-1-vs-tier-2 decision `instruction-and-context-design` teaches durably; the field names, character limits, and governance status in this lesson are the current, dated syntax that decision gets expressed in - re-verify them against the primary sources in References past this lesson's `next_review` date.

## Self-check questions
1. State, from memory, the two required `SKILL.md` frontmatter fields and their exact character limits, then check your answer against the "How it works" section - which limit is easier to forget?
2. A teammate wants to add a rule that says "never commit directly to main" to a project. Should it go in a `SKILL.md` or in `AGENTS.md`/`CLAUDE.md`? Justify the answer using this lesson's table, not just intuition.
3. Explain why `SKILL.md`'s description field must be written in third person, tying your answer to how the field is actually used at runtime (not just "because the docs say so").
4. This repository already has a root `CLAUDE.md` that points to `agent-docs/*.md` files for detail. Which `SKILL.md` guideline in this lesson does that pattern mirror, and why does the same instinct apply to both formats despite one having frontmatter and the other not?
5. Why is `AGENTS.md`'s Linux Foundation stewardship (donated December 2025) relevant to how much you should trust its syntax staying stable, compared to a single vendor's proprietary format?

## References
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (accessed August 2026)
- [Anthropic, Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) (accessed August 2026)
- [agents.md, the AGENTS.md open specification](https://agents.md/) (accessed August 2026)
- [MorphLLM, AGENTS.md Spec 2026: Recommended Sections + AGENTS.md vs CLAUDE.md vs .cursorrules](https://www.morphllm.com/agents-md-guide) (2026)
- This repository's own root `CLAUDE.md` and `AGENTS.md`, as an inspectable, currently-in-use example of the always-loaded-file convention described in this lesson.
