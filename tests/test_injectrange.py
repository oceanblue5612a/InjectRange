"""Tests for injectrange, stdlib unittest only."""

import io
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from injectrange import classes, corpus as corpus_mod, guard as guard_mod
from injectrange import harness, report, cli

SAMPLES = os.path.join(ROOT, "samples")
CORPUS_PATH = os.path.join(SAMPLES, "corpus.json")
PERMISSIVE = os.path.join(SAMPLES, "guard-permissive.json")
STRICT = os.path.join(SAMPLES, "guard-strict.json")

