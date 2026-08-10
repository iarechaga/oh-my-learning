#!/usr/bin/env python3
"""Regenerate CATALOG.md from lesson front matter.

CATALOG.md is a derived, public-facing index of every lesson in the repo (domain ->
subject -> concept), used as the "see the full depth" link from the root README. It is
generated, not hand-maintained: run this script after adding, renumbering, or removing
lessons/subjects/domains, and commit the result alongside the content change.

No third-party dependencies (stdlib only), so contributors can run it without installing
website/requirements.txt.

Usage:
    python3 scripts/generate_catalog.py            # write CATALOG.md
    python3 scripts/generate_catalog.py --check     # exit 1 if CATALOG.md is stale
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "CATALOG.md"

# Top-level directories that are not content domains.
NON_DOMAIN_DIRS = {
    "templates",
    "agent-docs",
    "website",
    "scripts",
    ".git",
    ".github",
    ".claude",
    ".opencode",
}

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class Lesson:
    id: str
    number: str
    title: str
    seniority: str
    status: str
    path: Path


@dataclass
class Subject:
    slug: str
    domain_slug: str
    title: str
    readme_path: Path
    lessons: list[Lesson] = field(default_factory=list)

    @property
    def path(self) -> str:
        return f"{self.domain_slug}/{self.slug}"


@dataclass
class Domain:
    slug: str
    title: str
    subjects: list[Subject] = field(default_factory=list)

    @property
    def lesson_count(self) -> int:
        return sum(len(s.lessons) for s in self.subjects)


def parse_front_matter_field(text: str, field_name: str) -> str:
    """Grab a single scalar front-matter field without a full YAML parser.

    Front matter here is flat `key: value` per line; values are never multi-line for
    the fields this script reads (id, title, seniority, status). Strips surrounding
    quotes so `title: "Foo: Bar"` and `title: Foo: Bar` both come back as `Foo: Bar`.
    """
    m = re.search(rf"^{field_name}:\s*(.*)$", text, re.MULTILINE)
    if not m:
        return ""
    value = m.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def read_h1(readme: Path) -> str:
    for line in readme.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return readme.parent.name


def load_lesson(path: Path) -> Lesson | None:
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None
    fm = m.group(1)
    lesson_id = parse_front_matter_field(fm, "id")
    if not lesson_id or "/" not in lesson_id:
        return None
    number = lesson_id.split("/", 1)[1]
    return Lesson(
        id=lesson_id,
        number=number,
        title=parse_front_matter_field(fm, "title"),
        seniority=parse_front_matter_field(fm, "seniority"),
        status=parse_front_matter_field(fm, "status") or "drafted",
        path=path,
    )


def discover() -> list[Domain]:
    domains: list[Domain] = []
    for domain_dir in sorted(ROOT.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name in NON_DOMAIN_DIRS:
            continue
        if domain_dir.name.startswith("."):
            continue
        domain_readme = domain_dir / "README.md"
        if not domain_readme.exists():
            continue

        subjects: list[Subject] = []
        for subject_dir in sorted(domain_dir.iterdir()):
            lessons_dir = subject_dir / "lessons"
            subject_readme = subject_dir / "README.md"
            if not lessons_dir.is_dir() or not subject_readme.exists():
                continue

            lessons = []
            for lesson_path in sorted(lessons_dir.glob("*.md")):
                lesson = load_lesson(lesson_path)
                if lesson:
                    lessons.append(lesson)
            if not lessons:
                continue
            lessons.sort(key=lambda l: l.number)

            subjects.append(
                Subject(
                    slug=subject_dir.name,
                    domain_slug=domain_dir.name,
                    title=read_h1(subject_readme),
                    readme_path=subject_readme,
                    lessons=lessons,
                )
            )

        if subjects:
            domains.append(
                Domain(slug=domain_dir.name, title=read_h1(domain_readme), subjects=subjects)
            )

    return domains


def render(domains: list[Domain]) -> str:
    total_lessons = sum(d.lesson_count for d in domains)
    total_subjects = sum(len(d.subjects) for d in domains)

    lines: list[str] = []
    lines.append("# Full Lesson Catalog")
    lines.append("")
    lines.append(
        "Generated from lesson front matter by `scripts/generate_catalog.py` - do "
        "**not** hand-edit. Regenerate with `python3 scripts/generate_catalog.py` "
        "after adding, renumbering, or removing lessons, subjects, or domains, and "
        "commit the result in the same change. See "
        "[agent-docs/repository-model.md](agent-docs/repository-model.md)."
    )
    lines.append("")
    lines.append(
        f"**{total_lessons} lessons across {len(domains)} domains, {total_subjects} "
        "subjects.** Every row links straight to the lesson; `status`/`mastery` are "
        "personal (per learner branch/fork), so this catalog only shows what exists, "
        "not who has studied it."
    )
    lines.append("")
    lines.append("## Contents")
    lines.append("")
    for domain in domains:
        lines.append(
            f"- [{domain.title}](#{domain.slug}) - {len(domain.subjects)} subjects, "
            f"{domain.lesson_count} lessons"
        )
        for subject in domain.subjects:
            lines.append(
                f"  - [{subject.title}](#{subject.slug}) - {len(subject.lessons)} lessons"
            )
    lines.append("")
    lines.append("---")
    lines.append("")

    for domain in domains:
        lines.append(f'<a id="{domain.slug}"></a>')
        lines.append(f"## {domain.title}")
        lines.append("")
        for subject in domain.subjects:
            lines.append(f'<a id="{subject.slug}"></a>')
            lines.append(f"### {subject.title}")
            lines.append("")
            lines.append(
                f"{len(subject.lessons)} lessons - "
                f"[subject index]({subject.domain_slug}/{subject.slug}/README.md)"
            )
            lines.append("")
            lines.append("| # | Concept | Seniority | Lesson |")
            lines.append("| - | ------- | --------- | ------ |")
            for lesson in subject.lessons:
                rel_path = lesson.path.relative_to(ROOT).as_posix()
                seniority = lesson.seniority or "-"
                lines.append(
                    f"| {lesson.number} | {lesson.title} | {seniority} | [lesson]({rel_path}) |"
                )
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(
        "Back to [README.md](README.md#dominios-de-un-vistazo) for the condensed "
        "domain overview and how to get started."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if CATALOG.md is out of date instead of writing it",
    )
    args = parser.parse_args()

    domains = discover()
    content = render(domains)

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != content:
            print("CATALOG.md is stale - run: python3 scripts/generate_catalog.py", file=sys.stderr)
            return 1
        print("CATALOG.md is up to date.")
        return 0

    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({sum(d.lesson_count for d in domains)} lessons).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
