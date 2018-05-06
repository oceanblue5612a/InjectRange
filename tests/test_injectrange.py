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
        self.assertFalse(classes.is_known("tool_coercian"))


class CorpusTest(unittest.TestCase):
    def test_load_and_shape(self):
        c = corpus_mod.load(CORPUS_PATH)
        self.assertEqual(c.version, "1.0.0")
        self.assertEqual(len(c.patterns), 24)
        counts = corpus_mod.counts_by_class(c)
        for key in classes.CLASS_KEYS:
            self.assertEqual(counts[key], 4)

    def test_digest_is_stable(self):
        a = corpus_mod.load(CORPUS_PATH)
        b = corpus_mod.load(CORPUS_PATH)
        self.assertEqual(a.digest, b.digest)
        self.assertEqual(a.digest, cli.PINNED_DIGEST)

    def test_digest_matches_pin(self):
        c = corpus_mod.load(CORPUS_PATH)
        self.assertTrue(corpus_mod.verify(c, cli.PINNED_DIGEST))
        self.assertFalse(corpus_mod.verify(c, "0" * 64))

    def test_digest_independent_of_pattern_order(self):
        c = corpus_mod.load(CORPUS_PATH)
        shuffled = list(reversed(c.patterns))
        self.assertEqual(
            corpus_mod.compute_digest(c.version, c.patterns),
            corpus_mod.compute_digest(c.version, shuffled),
        )

    def test_rejects_unknown_class(self):
        path = os.path.join(HERE, "_bad_corpus.json")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write('{"corpus_version":"x","patterns":[{"id":"a","cls":"ghost","text":"t"}]}')
        try:
            with self.assertRaises(corpus_mod.CorpusError):
                corpus_mod.load(path)
        finally:
            os.remove(path)

    def test_rejects_duplicate_id(self):
        path = os.path.join(HERE, "_dup_corpus.json")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write('{"corpus_version":"x","patterns":['
                         '{"id":"a","cls":"role_confusion","text":"t"},'
                         '{"id":"a","cls":"role_confusion","text":"u"}]}')
        try:
            with self.assertRaises(corpus_mod.CorpusError):
                corpus_mod.load(path)
        finally:
            os.remove(path)


class GuardTest(unittest.TestCase):
    def test_blocks_is_case_insensitive(self):
        g = guard_mod.from_config({"name": "t", "rules": ["you are now"]})
        self.assertTrue(g.blocks("YOU ARE NOW something"))
        self.assertFalse(g.blocks("harmless text"))

    def test_matching_rule(self):
        g = guard_mod.from_config({"name": "t", "rules": ["shell tool"]})
        self.assertEqual(g.matching_rule("call the shell tool"), "shell tool")
        self.assertEqual(g.matching_rule("nothing here"), "")

    def test_load_samples(self):
        perm = guard_mod.load(PERMISSIVE)
        strict = guard_mod.load(STRICT)
        self.assertEqual(perm.name, "permissive")
        self.assertEqual(strict.name, "strict")
        self.assertGreater(len(strict.rules), len(perm.rules))

    def test_rejects_bad_config(self):
        with self.assertRaises(guard_mod.GuardError):
            guard_mod.from_config({"name": "", "rules": []})
        with self.assertRaises(guard_mod.GuardError):
            guard_mod.from_config({"name": "t", "rules": "not a list"})


class HarnessTest(unittest.TestCase):
    def setUp(self):
        self.corpus = corpus_mod.load(CORPUS_PATH)

    def test_permissive_breaches_all(self):
        g = guard_mod.load(PERMISSIVE)
        result = harness.run(self.corpus, g)
        self.assertTrue(result.any_breach)
        self.assertEqual(len(result.breached_classes), 6)

    def test_strict_leaves_one_class(self):
        g = guard_mod.load(STRICT)
        result = harness.run(self.corpus, g)
        self.assertTrue(result.any_breach)
        self.assertEqual(result.breached_classes, ["delimiter_escape"])

    def test_outcomes_ordered_by_taxonomy(self):
        g = guard_mod.load(STRICT)
        result = harness.run(self.corpus, g)
        self.assertEqual([o.cls for o in result.outcomes], classes.CLASS_KEYS)

    def test_totals_and_blocked_add_up(self):
        g = guard_mod.load(STRICT)
