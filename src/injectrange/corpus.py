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
    does not change the digest.
    """
    ordered = sorted(patterns, key=lambda p: p.id)
    payload = {
        "corpus_version": version,
        "patterns": [
            {"id": p.id, "cls": p.cls, "text": p.text} for p in ordered
        ],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_digest(version: str, patterns: List[Pattern]) -> str:
    """Return the sha256 hex digest of the canonical corpus form."""
    return hashlib.sha256(_canonical_bytes(version, patterns)).hexdigest()


def load(path: str) -> Corpus:
    """Load a corpus file, validate its structure, and compute its digest.

    Raises CorpusError on any structural problem, including an unknown breach
    class or a duplicate pattern id.
    """
    try:
