#!/usr/bin/env python3
"""Zero-dependency static checks for TeWei02/iq-analysis-bot (pure PWA site).

Checks
  1. Required repository files exist (HTML, manifest, service worker, icons).
  2. Every local href/src target in every HTML file resolves (broken-link check).
  3. manifest.json is valid JSON with the required PWA fields, and every icon
     it references exists on disk.
  4. Service-worker precache list resolves to real files.
  5. No obvious secret material is committed.

Errors fail the build (exit 1). Warnings are reported but never fail.
"""

from __future__ import annotations

import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "index.html",
    "manifest.json",
    "sw.js",
    "README.md",
    "README.en.md",
    "LICENSE",
    "icons/favicon.svg",
    "icons/favicon-32.png",
    "icons/apple-touch-icon.png",
    "icons/icon-192.png",
    "icons/icon-512.png",
]

SKIP_DIRS = {".git", ".github", "node_modules", "dist", "build"}

STRUCTURAL_TAGS = {
    "div", "section", "main", "header", "footer", "nav", "article", "aside",
    "table", "thead", "tbody", "tr", "td", "th", "ul", "ol", "li", "form",
    "select", "textarea", "button", "a", "span", "p", "h1", "h2", "h3", "h4",
    "h5", "h6", "strong", "em", "code", "pre", "blockquote", "script", "style",
    "html", "head", "body", "title", "label",
}
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}

SKIP_PREFIXES = (
    "http://", "https://", "//", "mailto:", "tel:", "javascript:", "data:", "#",
)

REQUIRED_MANIFEST_FIELDS = ("name", "short_name", "start_url", "display", "icons")

SECRET_PATTERNS = [
    ("error", "private key block", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("error", "AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("error", "GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("error", "Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("error", "Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("error", "OpenAI key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    (
        "warning",
        "hardcoded credential assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|apikey|secret|token|password|passwd)\b"
            r"\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']"
        ),
    ),
]
PLACEHOLDER_HINTS = (
    "your", "xxx", "example", "placeholder", "changeme", "dummy", "todo",
    "null", "undefined", "redacted", "<", "$",
)

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def walk_files(suffixes: tuple[str, ...] | None = None):
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if suffixes and path.suffix.lower() not in suffixes:
            continue
        yield path


class RefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, int]] = []
        self.stack: list[tuple[str, int]] = []

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.refs.append((value.strip(), line))
        if tag in VOID_TAGS:
            return
        if tag in STRUCTURAL_TAGS:
            self.stack.append((tag, line))

    def handle_startendtag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.refs.append((value.strip(), self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag not in STRUCTURAL_TAGS:
            return
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return


def check_required_files() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            err(f"missing required file: {rel}")


def resolve_local(base_dir: Path, ref: str) -> Path | None:
    if not ref or ref.lower().startswith(SKIP_PREFIXES):
        return None
    target = ref.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    target = unquote(target)
    if target.startswith("/"):
        return ROOT / target.lstrip("/")
    return (base_dir / target).resolve()


def check_links() -> None:
    html_files = list(walk_files((".html",)))
    if not html_files:
        warn("no HTML files found")
    for html_path in html_files:
        rel_html = html_path.relative_to(ROOT)
        parser = RefCollector()
        try:
            parser.feed(html_path.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:  # noqa: BLE001
            err(f"{rel_html}: cannot parse HTML ({exc})")
            continue
        for ref, line in parser.refs:
            target = resolve_local(html_path.parent, ref)
            if target is None or target.exists():
                continue
            shown = ref.split("#", 1)[0].split("?", 1)[0]
            err(f"{rel_html}:{line}: broken local link '{shown}'")
        for tag, line in parser.stack:
            warn(f"{rel_html}:{line}: <{tag}> appears unclosed")


def check_manifest() -> None:
    path = ROOT / "manifest.json"
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        err(f"manifest.json: invalid JSON ({exc})")
        return
    if not isinstance(data, dict):
        err("manifest.json: root must be a JSON object")
        return
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in data:
            err(f"manifest.json: missing field '{field}'")
    for icon in data.get("icons", []) or []:
        src = icon.get("src") if isinstance(icon, dict) else None
        if not src:
            err("manifest.json: icon entry without 'src'")
            continue
        target = resolve_local(ROOT, src)
        if target is not None and not target.exists():
            err(f"manifest.json: icon '{src}' does not exist")


def check_service_worker() -> None:
    path = ROOT / "sw.js"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"PRECACHE\s*=\s*\[(.*?)\]", text, re.S)
    if not match:
        warn("sw.js: no PRECACHE array found, skipped precache check")
        return
    entries = re.findall(r"['\"]([^'\"]+)['\"]", match.group(1))
    if not entries:
        warn("sw.js: PRECACHE array is empty")
    for entry in entries:
        target = resolve_local(ROOT, entry)
        if target is None:
            continue
        if entry in ("./", "."):
            target = ROOT / "index.html"
        if not target.exists():
            err(f"sw.js: precached asset '{entry}' does not exist")


def check_secrets() -> None:
    for path in walk_files():
        rel = path.relative_to(ROOT)
        if rel.name in {"LICENSE", "check_static.py"}:
            continue
        if path.stat().st_size > 2 * 1024 * 1024:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if len(line) > 2000:
                continue
            for severity, label, pattern in SECRET_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                if severity == "warning":
                    value = match.group(0).lower()
                    if any(hint in value for hint in PLACEHOLDER_HINTS):
                        continue
                message = f"{rel}:{line_no}: possible {label}"
                if severity == "error":
                    err(message)
                else:
                    warn(message)

CONFLICT_MARKERS = re.compile(r"^(?:<{7}|>{7})(?:\s|$)")


def check_conflict_markers() -> None:
    for path in walk_files():
        rel = path.relative_to(ROOT)
        if rel.name == "LICENSE" or path.stat().st_size > 1024 * 1024:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if CONFLICT_MARKERS.match(line):
                err(f"{rel}:{line_no}: leftover merge conflict marker")


def main() -> int:
    check_required_files()
    check_links()
    check_manifest()
    check_service_worker()
    check_secrets()
    check_conflict_markers()

    print(f"check_static: {len(errors)} error(s), {len(warnings)} warning(s)")
    for message in errors:
        print(f"ERROR   {message}")
    for message in warnings:
        print(f"WARNING {message}")

    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if target:
        lines = [
            "# Static checks — iq-analysis-bot",
            "",
            f"- errors: **{len(errors)}**",
            f"- warnings: **{len(warnings)}**",
            "",
        ]
        lines += [f"- ERROR: {m}" for m in errors[:50]]
        lines += [f"- WARNING: {m}" for m in warnings[:50]]
        try:
            Path(target).write_text("\n".join(lines) + "\n", encoding="utf-8")
        except OSError:
            pass

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
