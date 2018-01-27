"""Command line interface for injectrange.

Subcommands:
  run      evaluate a guard config against the pinned corpus, print the matrix
  corpus   print the corpus summary and verify its pinned digest
  diff     compare two guard configs against the corpus, print what changed
  version  print the version

Exit codes:
  0  clean, no class breached
  1  findings present, at least one class breached
  2  usage or input error
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from . import __version__
from . import corpus as corpus_mod
from . import guard as guard_mod
from . import harness, report

# The corpus is pinned to this canonical sha256 digest. A run refuses to
# proceed if the loaded corpus does not match, unless the pin is overridden on
# the command line. Recompute with: injectrange corpus --show-digest
PINNED_DIGEST = "236cbebaab82a1a00f5ab0643dce0db33dd8ef5c08f2a77e8bf69ea467a0a470"

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2


def _default_corpus_path() -> str:
    """Return the packaged sample corpus path, used when none is given."""
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
