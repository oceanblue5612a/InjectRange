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
