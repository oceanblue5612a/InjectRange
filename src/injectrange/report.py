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
