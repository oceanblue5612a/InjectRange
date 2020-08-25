"""Run the corpus against a guard and collect outcomes.

The harness evaluates every corpus probe against a guard and records, per breach
class, how many probes were blocked and how many leaked. A class breaches when
at least one probe in it leaks past the guard. The result is a plain data
structure so report.py can render it and diff.py can compare two of them.
"""

from __future__ import annotations

from typing import Dict, List, NamedTuple

from . import classes
from .corpus import Corpus
from .guard import Guard


class ClassOutcome(NamedTuple):
    """Per-class tally: total probes, how many leaked, whether it breached."""

    cls: str
    total: int
    leaked: int

    @property
    def blocked(self) -> int:
        return self.total - self.leaked

    @property
    def breached(self) -> bool:
        return self.leaked > 0


class RunResult(NamedTuple):
    """A full run: which guard, which corpus, and the per-class outcomes."""

    guard_name: str
    corpus_version: str
    corpus_digest: str
    outcomes: List[ClassOutcome]

    @property
    def breached_classes(self) -> List[str]:
        return [o.cls for o in self.outcomes if o.breached]

    @property
    def any_breach(self) -> bool:
        return any(o.breached for o in self.outcomes)


def run(corpus: Corpus, guard: Guard) -> RunResult:
    """Evaluate the corpus against the guard and return per-class outcomes.

    Outcomes are ordered by the fixed taxonomy so two runs diff cleanly.
    """
    totals: Dict[str, int] = {key: 0 for key in classes.CLASS_KEYS}
    leaked: Dict[str, int] = {key: 0 for key in classes.CLASS_KEYS}

    for pattern in corpus.patterns:
        totals[pattern.cls] += 1
        if not guard.blocks(pattern.text):
            leaked[pattern.cls] += 1

    outcomes = [
        ClassOutcome(cls=key, total=totals[key], leaked=leaked[key])
        for key in classes.CLASS_KEYS
    ]
    return RunResult(
        guard_name=guard.name,
        corpus_version=corpus.version,
        corpus_digest=corpus.digest,
        outcomes=outcomes,
