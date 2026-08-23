# Release Policy

Load this file before cutting a release, writing a CHANGELOG entry, choosing a version
number, or tagging. It defines how this repository versions its **library content and
agent rules**, and how to keep [`CHANGELOG.md`](../CHANGELOG.md) consistent across
releases.

This repo is a library of lessons, not a software product, so versioning tracks what
actually changes here: domains, subjects, lessons, the agent's own rules (AGENTS.md,
templates, workflows), and repository tooling. It does **not** track personal learning
progress.

---

## What a release is

A release is a labelled snapshot of the **canonical library on `main`** at a point in
time, summarised by a versioned section in `CHANGELOG.md` and (optionally) a git tag plus
a GitHub Release. Releases let a reader see what was added, deepened, or restructured
since they last pulled.

Only content that lives on `main` is ever part of a release. Personal learning artifacts
(discussion records, `status`/`mastery` edits, progress-table changes) never reach `main`
(see [git-policy.md](git-policy.md)), so they are **never** in a changelog.

---

## Versioning (content-adapted SemVer)

Use `MAJOR.MINOR.PATCH`, reinterpreted for a learning library. Decide the bump from the
**most significant** change in the release.

- **MAJOR** (`X.0.0`) - a breaking reorganization that invalidates existing references:
  - renaming or renumbering a concept **ID** or **subject slug**;
  - moving a subject between domains in a way that changes documented paths;
  - removing or merging subjects/lessons;
  - restructuring the repository layout, the front-matter schema, or the status/mastery
    vocabulary;
  - any change that would break a learner's existing links, bookmarks, or cross-subject
    prerequisites.
- **MINOR** (`x.Y.0`) - additive, backward-compatible growth:
  - a new **domain**;
  - a new **subject** (book);
  - one or more **new lessons** in an existing subject;
  - substantial **deepening** of existing lessons that adds real new material;
  - new agent capabilities or workflows (e.g. a new `agent-docs/` doc) that do not break
    existing structure.
- **PATCH** (`x.y.Z`) - small fixes that change no structure:
  - corrections, clarifications, or typo fixes inside existing lessons;
  - link/diagram/table fixes;
  - index/summary regeneration with no new concepts;
  - tooling and meta changes (license, CONTRIBUTING, issue templates, README wording).

**Rules of thumb:**
- IDs/slugs/structure change -> MAJOR. New stuff added -> MINOR. Existing stuff fixed ->
  PATCH.
- Stay on `0.y.z` until the library is declared stable; pre-1.0, prefer MINOR for new
  subjects/lessons and PATCH for fixes, and reserve a future `1.0.0` for the first
  "stable, structure-frozen" milestone.
- One release can contain many changes; the version reflects the single most significant
  one (a release that adds a subject **and** fixes typos is a MINOR).

---

## Renaming, splitting, or merging a lesson

Load this section before renaming a lesson file, splitting one lesson into several, or
merging several into one - this is where MAJOR-vs-MINOR is easiest to get wrong, because
two different identifiers are involved and only one of them is this repo's stable
contract.

**ID vs. URL - they are not the same guarantee.**
- The concept **ID** (`<subject-slug>/<NN>`) is the stable, canonical identifier.
  `prerequisites`, in-prose cross-references, and `CATALOG.md` all resolve by ID. Keeping
  the ID unchanged during a rename/split keeps all of that working - this is why ID
  stability is a repo-wide non-negotiable (see `AGENTS.md`).
- The lesson's **filename/`slug`** is a *different*, weaker identifier, and the
  published website URL is derived from it, not from the ID (`website/build.py` builds
  `<domain>/<subject>/<NN>-<slug>.html`). **Changing the filename changes the public URL
  even when the ID is untouched.** Preserving the ID does not save a bookmark to the old
  page - this is the exact gap that broke `prompting-context-engineering/09`'s URL in
  `v1.2.0` despite its ID staying `09` throughout the split.
- Consequence for versioning: a rename/split that keeps the ID stable is **not
  automatically MINOR**. It is MINOR for the repo's own internal-reference contract, but
  it is a breaking change for anyone who bookmarked or linked the old published URL. Both
  facts have to be evaluated, not just the first one.

**Check whether the project has real external usage before deciding the bump.**
Do not guess. Run:
```
gh repo view iarechaga/oh-my-learning --json stargazerCount,forkCount \
  -q '.stargazerCount, .forkCount'
```
- If stars and forks are effectively zero (the maintainer's own activity aside) and there
  is no other evidence of external readers (no issues/PRs from other accounts, no
  reported broken links), a URL-breaking rename **may still ship as MINOR**, exactly as
  decided for `v1.2.0` - state that reasoning explicitly in the CHANGELOG entry (see
  below) so it's an auditable decision, not a silent one.
- The moment that check shows real external usage - nonzero forks from accounts other
  than `iarechaga`, a meaningful star count, inbound links, or any report of a broken
  page - **this exception is gone.** From that point on, a published-URL-breaking rename
  requires either a MAJOR bump or a mandatory redirect (see procedure below) before it
  ships; do not fall back on "nobody probably has this bookmarked" once there is evidence
  someone might.
- This check has no fixed threshold to hit forever - re-run it every time this situation
  comes up, don't rely on a past answer.

**Procedure for a rename/split/merge that changes a lesson's filename:**
1. **Warn the human before renaming, not after.** State plainly that the published URL
   will change, what the old and new URLs are, and run the traction check above so they
   decide with real information - do not rename first and disclose the URL break in the
   report.
2. **Preserve the concept ID** whenever the concept is continuous with what existed
   before (a split of one lesson into several keeps the ID on the piece that's the
   closest continuation; a genuinely new concept gets a new, appended ID instead - see
   `repository-model.md`'s ID-stability rule).
3. **Add a redirect from the old URL to the new one.** See `LEGACY_URL_REDIRECTS` in
   `website/build.py` for the current (manual, one-entry-per-rename) mechanism - add an
   entry there before the release ships, every time, not only when usage numbers look
   high enough to bother.
4. **Document it under `Restructured`** in `CHANGELOG.md` with the path/URL change called
   out explicitly, even when the ID itself didn't change - see the
   [CHANGELOG.md format](#changelogmd-format) rule below that already requires this for
   ID/slug/path changes.

**Prevention: prefer a new lesson over renaming an existing one.**
When a new lesson would serve just as well as renaming/splitting an existing one -
e.g. the old content stays valid and a genuinely new angle is what's actually being
added - add the new lesson under the next available ID instead of touching the existing
file. This sidesteps the whole MAJOR/MINOR/redirect question, keeps every existing URL
alive, and costs nothing but one more ID. Reach for a rename/split only when the old
content is actually wrong, thin, or in the wrong place - not merely to make the index
read better.

---

## CHANGELOG.md format

Follow **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)** conventions, with
categories adapted to this repo. The file lives at the repo root.

**Structure (top to bottom):**

1. Title + a one-line description and links to Keep a Changelog and SemVer.
2. An **`## [Unreleased]`** section that always sits at the top and accumulates changes as
   they land (see [Workflow](#workflow-how-to-cut-a-release)).
3. One `## [X.Y.Z] - YYYY-MM-DD` section per release, newest first.

**Categories** - use these headings (in this order) under a version; include only the
ones that apply:

- **Added** - new domains, new subjects, new lessons, new agent docs/workflows, new
  tooling.
- **Deepened** - existing lessons expanded with substantial new material (this repo's
  analogue of "Changed" for content quality).
- **Changed** - reworded/reorganized content or agent rules that are **not** breaking.
- **Restructured** - moves/renames/renumbering and layout or schema changes. **Call out
  anything that changes a concept ID, slug, or path explicitly**, because it is a
  breaking change for readers.
- **Fixed** - corrections of factual errors, broken links, typos.
- **Removed** - deleted or merged lessons/subjects/domains.

Do **not** use software-only categories like "Security" or "Deprecated" unless they
genuinely apply (they normally will not).

**Entry style:**

- One change per bullet, in plain past-tense ("Added the *Refactoring* subject (18
  lessons).").
- Reference subjects by name and lessons by **concept ID** where useful
  (`system-design/21`), and link to the lesson or subject README when it helps.
- Group lesson additions by subject rather than listing 20 near-identical bullets; give a
  count and link the subject index, then call out individually only the notable ones.
- Be specific about scope: a reader should be able to tell whether to re-read something.
- Never list personal progress (no "discussed X", no mastery changes).

**Example skeleton:**

```
## [Unreleased]

## [0.2.0] - 2026-07-15
### Added
- *Refactoring* subject under a new `engineering-practices/` domain (18 lessons) -
  see `engineering-practices/refactoring/README.md`.
- `system-design/21` - Backpressure in streaming systems.
### Deepened
- Expanded `ddia/07` (replication) with two worked examples and a failure-mode table.
### Fixed
- Corrected the offset/cursor pagination trade-off in `system-design/12`.

## [0.1.0] - 2026-06-30
...
```

---

## Workflow (how to cut a release)

The maintainer (`iarechaga`) cuts releases on `main`; contributors never tag or publish
releases (see [git-policy.md](git-policy.md)).

**1. Keep `[Unreleased]` current as work lands.**
Whenever you add, deepen, restructure, fix, or remove **library content or agent rules**
on `main`, add a matching bullet under the right category in the `[Unreleased]` section in
the same change. This is the cheapest way to keep the changelog from drifting - do not
reconstruct it from `git log` at release time if you can avoid it.

**2. When the human asks to cut a release `X.Y.Z`:**
1. **Pick the version** using the [rules above](#versioning-content-adapted-semver),
   driven by the most significant change since the last release. Confirm the number with
   the human if it is ambiguous (especially MAJOR vs MINOR).
2. **Reconcile `[Unreleased]`** against what actually changed. Cross-check with
   `git log <last-tag>..HEAD` (or the full history for `0.1.0`) so nothing is missing and
   nothing personal slipped in. Edit, group, and order the bullets to read well.
3. **Check for an overdue `agentic-engineering/landscape-snapshot` review.** If that
   domain exists, scan `agentic-engineering/landscape-snapshot/README.md`'s concept
   table for any `Next review` date in the past and flag it to the human before
   finalizing - see
   [fast-moving-domain-policy.md](fast-moving-domain-policy.md). This does not block
   the release; it is a heads-up, not a gate.
4. **Promote the section:** rename `## [Unreleased]` to `## [X.Y.Z] - YYYY-MM-DD` (today's
   date, real date - never fabricate), and add a fresh empty `## [Unreleased]` above it.
5. **Verify** per the [checklist](#verification).
6. **Commit** the changelog with a message like `Release X.Y.Z` (or fold it into the final
   content commit). Per git-policy, the maintainer pushes to `main`.
7. **Tag and publish only when the human explicitly asks.** Do not create the git tag or
   GitHub Release as part of routine work. When asked:
   - tag the release commit: `git tag -a vX.Y.Z -m "Release X.Y.Z"` and push the tag
     (`git push origin vX.Y.Z`);
   - optionally create a GitHub Release from that tag, using the changelog section as the
     body.

Seeding the very first release (`0.1.0`) is the one case where you summarise the whole
existing library from history rather than from an accumulated `[Unreleased]` section.

---

## What counts (include) vs what never appears (exclude)

**Include** (these are releasable):
- New/changed **domains, subjects, lessons**.
- **Deepening** or correcting lesson content.
- **Restructuring**: ID/slug/path/layout/schema changes (flag as breaking).
- **Agent rules**: changes to `AGENTS.md`, `templates/`, or `agent-docs/`.
- **Tooling/meta**: `LICENSE`, `CONTRIBUTING.md`, `.github/` templates, README, this
  policy.

**Exclude** (never in a changelog):
- Discussion records under any `discussions/` folder.
- `status` / `mastery` edits and progress-table changes (personal learning).
- Generated/runtime artifacts (`.omo/`, `.code-review-graph/`).
- Routine summary regeneration when it carries no new or changed concept (it rides along
  silently; only mention summaries if their restructuring is itself notable).

---

## Verification

Before declaring a release done:

- The new version section uses a real date (`YYYY-MM-DD`) and the correct, justified
  version number.
- Categories used are from the approved list and ordered correctly; only applicable ones
  appear.
- Every breaking change (ID/slug/path/schema) is under **Restructured** (or **Removed**)
  and explicitly described as breaking.
- No personal learning artifacts and no generated artifacts are listed.
- Bullets are specific, past-tense, and grouped sensibly; links and concept IDs resolve.
- A fresh empty `## [Unreleased]` sits at the top.
- The changelog matches what actually changed on `main` since the previous release
  (spot-check against `git log`).
