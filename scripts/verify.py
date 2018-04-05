#!/usr/bin/env python3
"""Quality gate for injectrange.

Runnable as `python scripts/verify.py` from the project root. Standard library
only. Exits 0 when every check passes and 1 when any check fails, printing one
line per check and a final summary line.

The checks encode the lessons in _standards/LESSONS.md that can be verified
mechanically: SVG assets must parse and stay free of banned filters and illegal
comment sequences, no tracked text file may carry an em dash in any of its three
forms, README.md must avoid pandoc image attribute blocks and banned marketing
terms, every asset must be a labelled information graphic, and no two SVG text
labels sharing a baseline may overlap.
"""

from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT, "docs", "assets")
README = os.path.join(ROOT, "README.md")

SVG_NS = "{http://www.w3.org/2000/svg}"

# Filter primitives that betray a decorative, non-informational asset.
BANNED_SVG_FILTERS = ("feGaussianBlur", "feDropShadow", "feTurbulence")

# The em dash in every form it has slipped through before.
EM_DASH_FORMS = ("\u2014", "&#8212;", "&mdash;")

# Marketing terms a factual README should not need.
BANNED_MARKETING = (
    "blazing", "blazingly", "seamless", "seamlessly", "effortless",
    "effortlessly", "cutting-edge", "state-of-the-art", "revolutionary",
    "game-changing", "world-class", "next-generation", "next-gen",
    "supercharge", "unleash", "unlock the power", "powerful",
    "robust", "leverage", "synergy", "best-in-class", "turnkey",
    "one-stop", "delight", "magical", "magic",
)

# Text file extensions that are searched for the em dash forms.
TEXT_EXTENSIONS = (
    ".py", ".md", ".txt", ".json", ".toml", ".cfg", ".ini", ".yml",
    ".yaml", ".svg", ".cff", ".editorconfig", ".gitattributes",
    ".gitignore", "",
)

# Directories that never carry tracked, human-authored text.
SKIP_DIRS = {
    "__pycache__", ".git", ".venv", "venv", "build", "dist",
    ".eggs", ".pytest_cache",
}

# Rough per-character advance widths in em units, from LESSONS.md rule 4.
EM_PER_CHAR_SANS = 0.58
EM_PER_CHAR_MONO = 0.60


def _iter_svgs() -> List[str]:
    result = []
    if not os.path.isdir(ASSETS_DIR):
        return result
    for name in sorted(os.listdir(ASSETS_DIR)):
        if name.lower().endswith(".svg"):
            result.append(os.path.join(ASSETS_DIR, name))
    return result


def _iter_text_files() -> List[str]:
    result = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            base = name.lower()
            if ext in TEXT_EXTENSIONS or base in (
                ".editorconfig", ".gitattributes", ".gitignore",
            ):
                result.append(os.path.join(dirpath, name))
    return sorted(result)


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def check_svg_parses() -> Tuple[bool, str]:
    """Every .svg under docs/assets/ parses as XML."""
    failures = []
    for path in _iter_svgs():
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            failures.append("%s (%s)" % (_rel(path), exc))
    if failures:
        return False, "svg parses as XML: " + "; ".join(failures)
    return True, "svg parses as XML: all clean"


def check_no_banned_filters() -> Tuple[bool, str]:
    """No .svg contains feGaussianBlur, feDropShadow, or feTurbulence."""
    failures = []
    for path in _iter_svgs():
        text = _read(path)
        for banned in BANNED_SVG_FILTERS:
            if banned in text:
                failures.append("%s has %s" % (_rel(path), banned))
    if failures:
        return False, "no banned svg filters: " + "; ".join(failures)
    return True, "no banned svg filters: all clean"


def check_no_illegal_comment() -> Tuple[bool, str]:
    """No XML comment in any .svg contains the illegal -- sequence."""
    failures = []
    comment = re.compile(r"<!--(.*?)-->", re.DOTALL)
    for path in _iter_svgs():
        text = _read(path)
        for body in comment.findall(text):
            if "--" in body:
                failures.append(_rel(path))
                break
    if failures:
        return False, "no illegal -- in svg comments: " + "; ".join(failures)
    return True, "no illegal -- in svg comments: all clean"


def check_no_em_dash() -> Tuple[bool, str]:
    """No tracked text file contains U+2014, &#8212;, or &mdash;."""
    failures = []
    for path in _iter_text_files():
        try:
            text = _read(path)
        except (OSError, UnicodeDecodeError):
            continue
        for form in EM_DASH_FORMS:
            if form in text:
                failures.append("%s has %r" % (_rel(path), form))
    if failures:
        return False, "no em dash in any form: " + "; ".join(failures)
    return True, "no em dash in any form: all clean"


def check_readme_no_pandoc_attr() -> Tuple[bool, str]:
    """README.md has no pandoc image attribute block like ){width=...}."""
    if not os.path.isfile(README):
        return True, "no pandoc image attributes: README.md absent"
    text = _read(README)
    pattern = re.compile(r"\)\{[^}]*(?:width|height)[^}]*\}")
    if pattern.search(text):
        return False, "no pandoc image attributes: README.md has one"
    return True, "no pandoc image attributes: README.md clean"


def check_readme_no_marketing() -> Tuple[bool, str]:
    """README.md contains none of the banned marketing terms."""
    if not os.path.isfile(README):
        return True, "no marketing terms: README.md absent"
    text = _read(README).lower()
    hits = []
    for term in BANNED_MARKETING:
        if re.search(r"\b" + re.escape(term) + r"\b", text):
            hits.append(term)
    if hits:
        return False, "no marketing terms: README.md has " + ", ".join(hits)
    return True, "no marketing terms: README.md clean"


def _find_labels(path: str):
    """Return every <title>, <desc>, viewBox, role for one SVG root."""
    tree = ET.parse(path)
    root = tree.getroot()
    view_box = root.get("viewBox")
    role = root.get("role")
    titles = root.findall(".//%stitle" % SVG_NS)
    descs = root.findall(".//%sdesc" % SVG_NS)
    return view_box, role, titles, descs


def check_svg_accessible() -> Tuple[bool, str]:
    """Every .svg carries viewBox, role="img", a <title>, and a <desc>."""
    failures = []
    for path in _iter_svgs():
        view_box, role, titles, descs = _find_labels(path)
        missing = []
        if not view_box:
            missing.append("viewBox")
        if role != "img":
            missing.append('role="img"')
        if not titles:
            missing.append("<title>")
        if not descs:
            missing.append("<desc>")
        if missing:
            failures.append("%s missing %s" % (_rel(path), ", ".join(missing)))
