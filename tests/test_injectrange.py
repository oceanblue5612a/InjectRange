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


class ClassesTest(unittest.TestCase):
    def test_six_classes_in_fixed_order(self):
        self.assertEqual(len(classes.BREACH_CLASSES), 6)
        self.assertEqual(classes.CLASS_KEYS[0], "instruction_override")
        self.assertEqual(classes.CLASS_KEYS[-1], "exfiltration_framing")

    def test_get_class_known_and_unknown(self):
        self.assertEqual(classes.get_class("role_confusion").title, "Role confusion")
        with self.assertRaises(KeyError):
            classes.get_class("nope")

    def test_is_known(self):
        self.assertTrue(classes.is_known("tool_coercion"))
