"""Load and hash-pin the injection corpus, and verify its integrity.

The corpus is a JSON file of short synthetic pattern skeletons. Each pattern is
tagged with one breach class. The corpus is pinned by hashing a canonical byte
encoding of its patterns, so a run refuses to proceed if the file drifts from
the pinned digest. The digest is stable across platforms because it hashes a
canonical form rather than the raw file bytes.
"""

from __future__ import annotations

import hashlib
import json
from typing import Dict, List, NamedTuple

from . import classes


class Pattern(NamedTuple):
    """One corpus entry: an id, a breach class key, and the probe text."""

    id: str
    cls: str
    text: str


class Corpus(NamedTuple):
    """A loaded corpus with its version and computed digest."""

    version: str
    patterns: List[Pattern]
    digest: str


class CorpusError(Exception):
    """Raised when the corpus is malformed or fails integrity checks."""


def _canonical_bytes(version: str, patterns: List[Pattern]) -> bytes:
    """Build the canonical byte form that the digest is computed over.

    The form is deterministic: patterns are sorted by id and serialized with
    sorted keys and no incidental whitespace, so formatting of the source file
