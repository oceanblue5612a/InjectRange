"""Render run results as line-oriented text.

Two renderers live here: a per-class matrix for a single run, and a diff between
two runs that names each class whose breach state or leak count changed. Output
is line-oriented and deterministic so it diffs cleanly in git.
"""

from __future__ import annotations

from typing import Dict, List

