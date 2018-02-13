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
