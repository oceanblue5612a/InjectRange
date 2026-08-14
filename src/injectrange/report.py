"""Render run results as line-oriented text.

Two renderers live here: a per-class matrix for a single run, and a diff between
two runs that names each class whose breach state or leak count changed. Output
is line-oriented and deterministic so it diffs cleanly in git.
"""

from __future__ import annotations

from typing import Dict, List

from . import classes
from .harness import RunResult


def _status(breached: bool) -> str:
    return "BREACH" if breached else "closed"


def render_matrix(result: RunResult) -> List[str]:
    """Return the per-class matrix for one run as a list of lines."""
    lines: List[str] = []
    lines.append("guard: %s" % result.guard_name)
    lines.append("corpus: %s" % result.corpus_version)
    lines.append("digest: %s" % result.corpus_digest)
    lines.append("")
    header = "%-22s %6s %7s %7s  %s" % (
        "class", "total", "blocked", "leaked", "status")
    lines.append(header)
    lines.append("-" * len(header))
    for outcome in result.outcomes:
        title = classes.get_class(outcome.cls).title
        lines.append("%-22s %6d %7d %7d  %s" % (
            title,
            outcome.total,
            outcome.blocked,
            outcome.leaked,
            _status(outcome.breached),
        ))
    lines.append("-" * len(header))
    breached = result.breached_classes
    lines.append("breached classes: %d of %d" % (
        len(breached), len(result.outcomes)))
    return lines


def _by_class(result: RunResult) -> Dict[str, "object"]:
    return {o.cls: o for o in result.outcomes}


def render_diff(base: RunResult, head: RunResult) -> List[str]:
    """Return a diff between two runs as a list of lines.

    Reports each class whose leak count changed, marking classes that opened
    (regression) and classes that closed (improvement).
    """
    lines: List[str] = []
    lines.append("diff")
    lines.append("base guard: %s" % base.guard_name)
    lines.append("head guard: %s" % head.guard_name)
    if base.corpus_digest != head.corpus_digest:
        lines.append("warning: corpus digests differ, comparison is not like for like")
    lines.append("")

    base_map = _by_class(base)
    head_map = _by_class(head)

    header = "%-22s %12s %12s  %s" % ("class", "base leaked", "head leaked", "change")
    lines.append(header)
    lines.append("-" * len(header))

    opened = 0
    closed = 0
    for key in classes.CLASS_KEYS:
        b = base_map[key]
        h = head_map[key]
        title = classes.get_class(key).title
        if h.leaked > b.leaked:
            change = "opened"
            opened += 1
        elif h.leaked < b.leaked:
            change = "closed"
            closed += 1
        else:
            change = "same"
        lines.append("%-22s %12d %12d  %s" % (title, b.leaked, h.leaked, change))
    lines.append("-" * len(header))
    lines.append("classes opened: %d" % opened)
    lines.append("classes closed: %d" % closed)
    return lines


def render_corpus_summary(version: str, digest: str, counts: Dict[str, int]) -> List[str]:
    """Return a summary of corpus contents as a list of lines."""
    lines: List[str] = []
    lines.append("corpus: %s" % version)
    lines.append("digest: %s" % digest)
    lines.append("")
    header = "%-22s %6s" % ("class", "count")
    lines.append(header)
    lines.append("-" * len(header))
    total = 0
    for key in classes.CLASS_KEYS:
        title = classes.get_class(key).title
        count = counts.get(key, 0)
        total += count
        lines.append("%-22s %6d" % (title, count))
    lines.append("-" * len(header))
    lines.append("%-22s %6d" % ("total", total))
    return lines
