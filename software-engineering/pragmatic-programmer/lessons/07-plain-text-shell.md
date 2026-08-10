---
id: pragmatic-programmer/07
subject: pragmatic-programmer
title: The Power of Plain Text and the Shell
slug: plain-text-shell
status: drafted
mastery:
seniority: junior
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 3
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# The Power of Plain Text and the Shell

## TL;DR
Plain text — human-readable, not tied to a specific tool or binary format — is the most durable, composable, and future-proof way to store information a program will need to read, write, or be debugged from. Mastering the command-line shell (and scripting it) multiplies your leverage over plain-text data and over repetitive tasks that GUIs make slow and unrepeatable.

## The idea
Binary and proprietary formats optimize for one thing efficiently (compactness, a specific tool's convenience) at the cost of everything else: you need that specific tool (or a compatible one) to read the data at all, decades from now you may not have it, and you can't easily diff, grep, version-control, or script against it. Plain text pays a small storage/parsing cost in exchange for near-unlimited flexibility: any tool, any language, any future person can read it, and the entire Unix toolchain (grep, sed, awk, diff, version control) works on it for free.

The shell is the natural companion to this idea: it's the fastest way to compose small, plain-text-oriented tools into a pipeline that does something none of the individual tools were built to do — and, crucially, whatever you type interactively can usually be saved as a script and run again, turning one-off investigation into a repeatable, shareable tool.

## How it works

### Why plain text wins over the long run
- **Tool independence**: a CSV file can be opened by Excel, a Python script, `grep`, a text editor, or a future tool that doesn't exist yet. A proprietary binary export from a specific app version might not even open in next year's version of the same app.
- **Diffability and version control**: `git diff` on a JSON config file shows exactly what changed, line by line. `git diff` on a binary `.xlsx` shows "binary files differ" — useless for review, useless for blame, useless for understanding history.
- **Composability**: plain text output from one tool can be piped as plain text input to another, with no format-conversion step, because the interchange format is universal rather than tool-specific.
- **Debuggability under pressure**: when production is down and you need to inspect data by hand at 3 a.m., plain text (a log file, a JSON payload) can be read with `cat`/`less`/`grep` on any machine with a terminal. A proprietary format needs its specific tool installed, licensed, and working — an extra failure mode exactly when you can least afford one.

### Worked example: config file format choice
A team is choosing how to store application configuration. Option A: a proprietary binary format from a config-management vendor, edited only through the vendor's GUI. Option B: a YAML file in the repo.
- With Option B, a config change is a normal pull request: reviewable diff, blame history showing who changed a value and when, rollback via `git revert`, and any engineer can `grep -r "max_connections"` across the whole config history in seconds.
- With Option A, a config change requires the specific GUI tool, produces no reviewable diff, and if the vendor's tool has a bug or the license lapses, the config becomes partly inaccessible — a real, not hypothetical, risk the book explicitly warns about.

### The shell as a force multiplier over plain text
Because so much of a system's data and logs end up as plain text, shell fluency directly multiplies how fast you can investigate, transform, or automate against it. A few illustrative patterns:
- **Investigation**: `grep -c "ERROR" access.log.*` across a week of rotated logs answers "how many errors per day" in one line, without writing a program.
- **Transformation**: `cut -d',' -f2 report.csv | sort | uniq -c | sort -rn` turns a CSV column into a frequency-ranked summary — a rough "GROUP BY COUNT ORDER BY DESC" without touching a database.
- **Automation of the investigation itself**: once a one-off pipeline like the above proves useful, save it as a `.sh` script with a name and a couple of parameters — the next time the same question comes up (and it will), it's a five-second command instead of a from-scratch investigation.

### The book's caution: know when the shell isn't the right tool anymore
This isn't "do everything as shell one-liners forever." Once a script grows real logic (branching, error handling, structured data beyond flat text/CSV, anything another person needs to maintain), the pragmatic move is to graduate it into a real scripting language (Python, Ruby) with proper structure, tests, and readability — the shell's job is fast composition and glue, not to become an unmaintainable pile of chained pipes nobody can safely modify.

## Pros
- Plain text data outlives specific tools, vendors, and even programming-language ecosystems.
- The Unix toolchain (grep/sed/awk/diff/sort/uniq/version control) works on plain text "for free," multiplying leverage without writing new code.
- Shell scripts turn one-off manual investigations into fast, repeatable, shareable tools.

## Cons
- Plain text is less space- and parse-efficient than binary formats — a real cost at genuine scale (e.g., high-throughput binary protocols, large numeric datasets).
- Shell scripting has a real ceiling: past a certain complexity, shell scripts become unreadable, hard to test, and dangerous to modify (quoting bugs, silent failures) compared to a proper language.
- "Plain text everywhere" without schemas or validation can trade format lock-in for a different problem: silently malformed or ambiguously-structured data with no enforced contract.

## Alternatives
- **Structured binary formats (Protocol Buffers, Avro)** — chosen deliberately for high-throughput or schema-strict systems where plain text's overhead and lack of a strict schema are actual liabilities, not merely theoretical.
- **GUI-only proprietary tools** — sometimes genuinely the right choice for domain experts who aren't engineers and need visual, guided editing more than they need diffability or scriptability.
- **A real programming language instead of shell** for anything with meaningful logic, once the "one-liner" stage is clearly outgrown — trading the shell's terseness for testability and readability.

## When to use it
Default to plain text for configuration, logs, interchange formats, and anything a human might need to read, diff, or debug directly — unless you have a measured, specific reason (throughput, strict schema enforcement) to reach for a binary format instead. Reach for the shell for quick investigation, data wrangling, and automating a repeated manual task.

## When NOT to use it
Don't use plain text for genuinely high-volume, high-throughput binary data (video frames, dense numeric telemetry at scale) where the parsing/size overhead is a real, measured cost. Don't keep extending a shell script once it needs real control flow, structured data handling, or shared maintenance by people who aren't shell experts — move it to a proper language before it becomes unmaintainable.

## Key takeaways / mental model
Ask, before choosing a storage or interchange format: "in five years, with none of today's specific tools guaranteed to still exist, can someone still read this?" Plain text almost always answers yes. And treat every useful one-off shell command as a draft of a reusable script — save it before the insight is lost.

## Self-check questions
1. Give a concrete example where choosing a proprietary/binary format over plain text caused a real accessibility or maintainability problem.
2. Why does `git diff` behave so differently on a JSON file versus an `.xlsx` file, and why does that difference matter operationally?
3. Describe a shell one-liner you've used more than once that you should have saved as a script — what would that script look like?
4. At what point should a shell script "graduate" into a real programming language? Give the signal that tells you it's time.

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 3: "Basic Tools" (Plain Text's Power and Shell sections).
