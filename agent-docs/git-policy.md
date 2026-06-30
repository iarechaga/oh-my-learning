# Git Policy

Load this file before committing, pushing, creating branches, opening pull requests, or
deciding whether work belongs on `main`.

## Identity and permissions

Your identity decides what you may do. Determine it from the repository's git author
email (`git config user.email`):

- **Maintainer - `iarechaga`.** The configured author email belongs to the `iarechaga`
  GitHub account. You may commit and push **directly to `main`**.
- **Contributor - anyone else.** Any other author email. You must **never** commit or
  push to `main`. Always start by creating a new branch (e.g. `book/<subject-slug>` or
  `learn/<name>`) and do all work there, then open a pull request against `main`. Only
  the maintainer merges to `main`.

## When to commit and push

- **Creating a new subject (book):** when the subject is complete per Workflow A (all
  agreed lessons authored and verified, indexes in sync), **commit and push it
  automatically** - this is the one case where you do not wait to be asked. The
  maintainer pushes to `main`; a contributor pushes the branch and opens a pull request.
- **Anything else** - single lessons, discussion records, edits, refactors - commit and
  push **only when the human asks**.
- Personal learning artifacts (discussion records, `status`/`mastery` edits,
  progress-table changes) are never committed to `main` directly; they live on a branch
  or fork, even for the maintainer's own sessions.
- **Tagging and releases** - cutting a versioned release, writing the `CHANGELOG.md`
  entry, and creating a `vX.Y.Z` tag or GitHub Release follow
  [release-policy.md](release-policy.md). Only the maintainer tags/releases, and only when
  the human explicitly asks; contributors never tag or publish releases.

Use the repo's commit-message style, and never fabricate progress in a message.

## Safety rules

- Inspect `git status`, `git diff`, and recent `git log` before committing.
- Stage only intended files.
- Never use destructive git commands unless the human explicitly requested them.
- Never amend or force-push unless the human explicitly requested that exact operation.
- Do not commit generated runtime artifacts such as `.omo/` or `.code-review-graph/`.
