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

