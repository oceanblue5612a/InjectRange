"""Load and hash-pin the injection corpus, and verify its integrity.

The corpus is a JSON file of short synthetic pattern skeletons. Each pattern is
tagged with one breach class. The corpus is pinned by hashing a canonical byte
encoding of its patterns, so a run refuses to proceed if the file drifts from
the pinned digest. The digest is stable across platforms because it hashes a
canonical form rather than the raw file bytes.
"""

from __future__ import annotations

