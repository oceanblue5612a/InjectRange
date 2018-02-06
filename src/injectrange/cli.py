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
    return os.path.join(root, "samples", "corpus.json")


def _emit(lines: List[str]) -> None:
    for line in lines:
        sys.stdout.write(line + "\n")


def _load_corpus(path: str, pin: str, allow_unpinned: bool) -> corpus_mod.Corpus:
    corpus = corpus_mod.load(path)
    if not allow_unpinned and not corpus_mod.verify(corpus, pin):
        raise corpus_mod.CorpusError(
            "corpus digest %s does not match pin %s" % (corpus.digest, pin))
    return corpus


def _cmd_run(args: argparse.Namespace) -> int:
    try:
        corpus = _load_corpus(args.corpus, args.pin, args.allow_unpinned)
        guard = guard_mod.load(args.guard)
    except (corpus_mod.CorpusError, guard_mod.GuardError) as exc:
        sys.stderr.write("error: %s\n" % exc)
        return EXIT_USAGE
    result = harness.run(corpus, guard)
    _emit(report.render_matrix(result))
    return EXIT_FINDINGS if result.any_breach else EXIT_CLEAN


def _cmd_corpus(args: argparse.Namespace) -> int:
    try:
        corpus = corpus_mod.load(args.corpus)
    except corpus_mod.CorpusError as exc:
        sys.stderr.write("error: %s\n" % exc)
        return EXIT_USAGE
    if args.show_digest:
        sys.stdout.write(corpus.digest + "\n")
        return EXIT_CLEAN
    counts = corpus_mod.counts_by_class(corpus)
    _emit(report.render_corpus_summary(corpus.version, corpus.digest, counts))
    if not args.allow_unpinned and not corpus_mod.verify(corpus, args.pin):
        sys.stderr.write(
            "error: corpus digest does not match pin %s\n" % args.pin)
        return EXIT_USAGE
    return EXIT_CLEAN


def _cmd_diff(args: argparse.Namespace) -> int:
    try:
        corpus = _load_corpus(args.corpus, args.pin, args.allow_unpinned)
        base = guard_mod.load(args.base)
        head = guard_mod.load(args.head)
    except (corpus_mod.CorpusError, guard_mod.GuardError) as exc:
        sys.stderr.write("error: %s\n" % exc)
        return EXIT_USAGE
    base_result = harness.run(corpus, base)
    head_result = harness.run(corpus, head)
    _emit(report.render_diff(base_result, head_result))
    return EXIT_FINDINGS if head_result.any_breach else EXIT_CLEAN


def _cmd_version(_args: argparse.Namespace) -> int:
    sys.stdout.write("injectrange %s\n" % __version__)
    return EXIT_CLEAN


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="injectrange",
        description="Deterministic regression range for prompt-injection defences.",
    )
    sub = parser.add_subparsers(dest="command")

    default_corpus = _default_corpus_path()

    p_run = sub.add_parser("run", help="evaluate a guard against the corpus")
    p_run.add_argument("guard", help="path to a guard config JSON file")
    p_run.add_argument("--corpus", default=default_corpus,
                       help="path to the corpus JSON file")
    p_run.add_argument("--pin", default=PINNED_DIGEST,
                       help="expected corpus digest")
    p_run.add_argument("--allow-unpinned", action="store_true",
                       help="skip the corpus digest check")
    p_run.set_defaults(func=_cmd_run)
