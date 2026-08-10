#!/usr/bin/env python3
"""Build a static website from the Oh My Learning Markdown lessons.

The generator scans the repository for lesson files, reads their YAML front matter,
and emits a self-contained site under website/dist/. New lessons are discovered
automatically as long as they follow the established layout:

    <domain>/<subject>/lessons/<NN>-<slug>.md

Run with:
    python website/build.py
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pygments.formatters import HtmlFormatter

REPO_ROOT = Path(__file__).resolve().parent.parent
WEBSITE_ROOT = REPO_ROOT / "website"
TEMPLATE_DIR = WEBSITE_ROOT / "templates"
STATIC_DIR = WEBSITE_ROOT / "static"
DIST_DIR = WEBSITE_ROOT / "dist"

# Site-root path all generated links are prefixed with. Always starts and ends with "/".
# Defaults to "/" for local serving; a GitHub Pages *project* site (served from
# https://<user>.github.io/<repo>/, not a custom domain or a <user>.github.io user site)
# needs this set to "/<repo>/" via --base-path, since every internal link and static
# asset reference is otherwise root-relative and would 404 under the repo subpath.
BASE_PATH = "/"

# Top-level directories that are not learning domains.
NON_DOMAIN_DIRS = {
    ".git",
    ".github",
    ".omo",
    ".opencode",
    "agent-docs",
    "templates",
    "website",
}

SENIORITY_ORDER = ["junior", "mid", "senior", "staff", "principal"]
MASTERY_ORDER = ["solid", "partial", "shaky", "not-yet"]


def slugify(name: str) -> str:
    """Turn a directory or title into a URL-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def format_label(name: str) -> str:
    """Turn a kebab directory name into a readable label."""
    return " ".join(part.capitalize() for part in name.replace("_", "-").split("-"))


def read_first_heading(file_path: Path) -> str | None:
    """Return the text of the first Markdown H1 in a file, if any."""
    if not file_path.is_file():
        return None
    text = file_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Split YAML front matter from the Markdown body."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                meta = {}
            return meta, parts[2].strip()
    return {}, text


@dataclass
class Lesson:
    path: Path
    domain_slug: str
    subject_slug: str
    number: int
    slug: str
    id: str = ""
    subject: str = ""
    title: str = ""
    status: str = "drafted"
    mastery: str = ""
    seniority: str = ""
    source: str = ""
    prerequisites: list[str] = field(default_factory=list)
    created: str = ""
    updated: str = ""
    body_html: str = ""
    toc_html: str = ""
    reading_minutes: int = 0
    prev: "Lesson | None" = None
    next: "Lesson | None" = None

    @property
    def url(self) -> str:
        return f"{BASE_PATH}{self.domain_slug}/{self.subject_slug}/{self.number:02d}-{self.slug}.html"

    @property
    def is_discussed(self) -> bool:
        return self.status.lower() == "discussed"

    @property
    def display_status(self) -> str:
        if self.is_discussed and self.mastery:
            return f"discussed · {self.mastery}"
        return "drafted" if self.status else "drafted"

    @property
    def completion_badge(self) -> str:
        if self.is_discussed:
            return self.mastery or "discussed"
        return "not started"

    @property
    def sort_key(self) -> tuple[int, str]:
        return (self.number, self.slug)


@dataclass
class Subject:
    path: Path
    domain_slug: str
    slug: str
    lessons: list[Lesson] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"{BASE_PATH}{self.domain_slug}/{self.slug}/index.html"

    @property
    def title(self) -> str:
        return read_first_heading(self.path / "README.md") or format_label(self.slug)

    @property
    def seniority_baseline(self) -> str:
        """Best-guess baseline from the most common seniority among lessons."""
        counts: dict[str, int] = {}
        for lesson in self.lessons:
            if lesson.seniority:
                counts[lesson.seniority] = counts.get(lesson.seniority, 0) + 1
        if not counts:
            return ""
        return max(counts, key=lambda k: (counts[k], SENIORITY_ORDER.index(k) if k in SENIORITY_ORDER else 0))

    @property
    def progress(self) -> tuple[int, int]:
        total = len(self.lessons)
        done = sum(1 for lesson in self.lessons if lesson.is_discussed)
        return done, total

    @property
    def percent(self) -> int:
        done, total = self.progress
        return round(100 * done / total) if total else 0


@dataclass
class Domain:
    path: Path
    slug: str
    subjects: list[Subject] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"{BASE_PATH}{self.slug}/index.html"

    @property
    def title(self) -> str:
        return read_first_heading(self.path / "README.md") or format_label(self.slug)

    @property
    def progress(self) -> tuple[int, int]:
        done = sum(d for subject in self.subjects for d, _ in [subject.progress])
        total = sum(t for subject in self.subjects for _, t in [subject.progress])
        return done, total

    @property
    def percent(self) -> int:
        done, total = self.progress
        return round(100 * done / total) if total else 0

    @property
    def lesson_count(self) -> int:
        return sum(len(subject.lessons) for subject in self.subjects)


def discover_domains() -> list[Domain]:
    """Walk the repo and build the domain/subject/lesson tree."""
    domains: list[Domain] = []
    for domain_path in sorted(REPO_ROOT.iterdir()):
        if not domain_path.is_dir():
            continue
        if domain_path.name in NON_DOMAIN_DIRS or domain_path.name.startswith("."):
            continue

        domain = Domain(path=domain_path, slug=slugify(domain_path.name))
        for subject_path in sorted(domain_path.iterdir()):
            if not subject_path.is_dir() or subject_path.name.startswith("."):
                continue
            lessons_dir = subject_path / "lessons"
            if not lessons_dir.is_dir():
                continue

            subject = Subject(
                path=subject_path,
                domain_slug=domain.slug,
                slug=slugify(subject_path.name),
            )
            for lesson_file in sorted(lessons_dir.glob("*.md")):
                lesson = parse_lesson(lesson_file, domain.slug, subject.slug)
                if lesson:
                    subject.lessons.append(lesson)

            if subject.lessons:
                subject.lessons.sort(key=lambda lesson: lesson.sort_key)
                domain.subjects.append(subject)

        if domain.subjects:
            domain.subjects.sort(key=lambda subject: subject.slug)
            domains.append(domain)

    domains.sort(key=lambda domain: domain.slug)
    return domains


def parse_lesson(file_path: Path, domain_slug: str, subject_slug: str) -> Lesson | None:
    """Parse a single lesson Markdown file into a Lesson object."""
    match = re.match(r"^(\d+)-(.+)\.md$", file_path.name)
    if not match:
        return None

    number = int(match.group(1))
    slug = match.group(2)
    text = file_path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)

    md = markdown.Markdown(
        extensions=[
            "toc",
            "tables",
            "fenced_code",
            "codehilite",
            "md_in_html",
        ],
        extension_configs={
            "codehilite": {"css_class": "highlight", "use_pygments": True},
            "toc": {"permalink": "#", "toc_depth": "2-3"},
        },
    )
    body_html = md.convert(body)
    toc_html = getattr(md, "toc", "") or ""
    word_count = len(re.findall(r"\w+", body))
    reading_minutes = max(1, round(word_count / 200))

    return Lesson(
        path=file_path,
        domain_slug=domain_slug,
        subject_slug=subject_slug,
        number=number,
        slug=slug,
        id=meta.get("id", f"{subject_slug}/{number:02d}"),
        subject=meta.get("subject", subject_slug),
        title=meta.get("title") or format_label(slug),
        status=str(meta.get("status", "drafted")),
        mastery=str(meta.get("mastery", "")),
        seniority=str(meta.get("seniority", "")),
        source=str(meta.get("source", "")),
        prerequisites=list(meta.get("prerequisites") or []),
        created=str(meta.get("created", "")),
        updated=str(meta.get("updated", "")),
        body_html=body_html,
        toc_html=toc_html,
        reading_minutes=reading_minutes,
    )


def write_highlight_css(dest: Path) -> None:
    """Generate theme-aware Pygments styles for code blocks.

    Light rules apply by default; a dark palette takes over when the dark
    theme is active, either through the OS preference or the explicit toggle.
    """
    light = HtmlFormatter(style="default").get_style_defs(".highlight")
    dark_toggle = HtmlFormatter(style="monokai").get_style_defs(
        'html[data-theme="dark"] .highlight'
    )
    dark_auto = HtmlFormatter(style="monokai").get_style_defs(
        'html:not([data-theme="light"]) .highlight'
    )
    css = (
        "/* Generated by build.py — do not edit. */\n"
        f"{light}\n\n"
        f"{dark_toggle}\n\n"
        "@media (prefers-color-scheme: dark) {\n"
        f"{dark_auto}\n"
        "}\n"
    )
    dest.write_text(css, encoding="utf-8")


def build_site(base_path: str = "/") -> None:
    """Generate the complete static website.

    base_path is the site-root prefix for every internal link and static asset
    (see BASE_PATH above) - "/" for local serving, "/<repo>/" for a GitHub Pages
    project site.
    """
    global BASE_PATH
    base_path = base_path.strip()
    if not base_path.startswith("/"):
        base_path = "/" + base_path
    if not base_path.endswith("/"):
        base_path += "/"
    BASE_PATH = base_path

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, DIST_DIR / "static", dirs_exist_ok=True)

    write_highlight_css(DIST_DIR / "static" / "highlight.css")

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["format_label"] = format_label
    env.globals["base"] = BASE_PATH

    domains = discover_domains()

    # Global manifest for client-side search or debugging.
    manifest = [
        {
            "domain": domain.slug,
            "domain_title": domain.title,
            "subjects": [
                {
                    "subject": subject.slug,
                    "subject_title": subject.title,
                    "lessons": [
                        {
                            "id": lesson.id,
                            "title": lesson.title,
                            "url": lesson.url,
                            "status": lesson.status,
                            "mastery": lesson.mastery,
                            "seniority": lesson.seniority,
                        }
                        for lesson in subject.lessons
                    ],
                }
                for subject in domain.subjects
            ],
        }
        for domain in domains
    ]
    (DIST_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Home page.
    template = env.get_template("index.html")
    (DIST_DIR / "index.html").write_text(
        template.render(domains=domains, title="Oh My Learning"),
        encoding="utf-8",
    )

    # Domain and subject index pages.
    domain_template = env.get_template("domain.html")
    subject_template = env.get_template("subject.html")
    for domain in domains:
        domain_dir = DIST_DIR / domain.slug
        domain_dir.mkdir(parents=True)
        (domain_dir / "index.html").write_text(
            domain_template.render(domain=domain, domains=domains, title=f"{domain.title} | Oh My Learning"),
            encoding="utf-8",
        )

        for subject in domain.subjects:
            subject_dir = domain_dir / subject.slug
            subject_dir.mkdir(parents=True)
            (subject_dir / "index.html").write_text(
                subject_template.render(
                    subject=subject,
                    domain=domain,
                    domains=domains,
                    title=f"{subject.title} | {domain.title} | Oh My Learning",
                ),
                encoding="utf-8",
            )

    # Lesson pages.
    lesson_template = env.get_template("lesson.html")
    for domain in domains:
        for subject in domain.subjects:
            for i, lesson in enumerate(subject.lessons):
                lesson.prev = subject.lessons[i - 1] if i > 0 else None
                lesson.next = (
                    subject.lessons[i + 1] if i < len(subject.lessons) - 1 else None
                )
            for lesson in subject.lessons:
                lesson_file = DIST_DIR / domain.slug / subject.slug / f"{lesson.number:02d}-{lesson.slug}.html"
                lesson_file.write_text(
                    lesson_template.render(
                        lesson=lesson,
                        subject=subject,
                        domain=domain,
                        domains=domains,
                        title=f"{lesson.title} | {subject.title} | Oh My Learning",
                    ),
                    encoding="utf-8",
                )

    print(f"Built site with {sum(len(d.subjects) for d in domains)} subjects and "
          f"{sum(len(s.lessons) for d in domains for s in d.subjects)} lessons.")
    print(f"Output: {DIST_DIR}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Oh My Learning website.")
    parser.add_argument("--watch", action="store_true", help="Rebuild when source files change")
    parser.add_argument(
        "--base-path",
        default="/",
        help="Site-root prefix for links and assets, e.g. /oh-my-learning/ for a "
        "GitHub Pages project site. Defaults to / for local serving.",
    )
    args = parser.parse_args()

    build_site(args.base_path)

    if args.watch:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            print("--watch requires watchdog: pip install watchdog", file=sys.stderr)
            return 1

        class Rebuilder(FileSystemEventHandler):
            def on_any_event(self, event):
                if event.is_directory or event.event_type == "deleted":
                    return
                if "website/dist" in event.src_path or event.src_path.endswith(".html") and "dist" in event.src_path:
                    return
                print(f"Change detected: {event.src_path}")
                build_site(args.base_path)

        observer = Observer()
        observer.schedule(Rebuilder(), str(REPO_ROOT), recursive=True)
        observer.start()
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    return 0


if __name__ == "__main__":
    sys.exit(main())
