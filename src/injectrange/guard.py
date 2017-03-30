"""A configurable reference guard built from rules the user declares.

The guard is deliberately simple and fully local: it holds a list of rules, and
each rule is a lowercase substring that, if present in a probe, blocks that
probe. This is not a production filter. It is a reference target so a regression
range has something concrete and reproducible to evaluate. Because the guard is
declared in a config file the user controls, the corpus tests the guard, not any
model.

A probe is judged blocked if any rule substring occurs in its lowercased text.
A breach class breaches when at least one probe in that class is not blocked.
"""

from __future__ import annotations

import json
from typing import List, NamedTuple

from . import classes


class GuardError(Exception):
    """Raised when a guard config is malformed."""


class Guard(NamedTuple):
    """A named guard with a case-insensitive list of blocking substrings."""

    name: str
    rules: List[str]

    def blocks(self, text: str) -> bool:
        """Report whether the guard blocks a probe text."""
        lowered = text.lower()
        return any(rule in lowered for rule in self.rules)

    def matching_rule(self, text: str) -> str:
        """Return the first rule that blocks the text, or an empty string."""
        lowered = text.lower()
        for rule in self.rules:
            if rule in lowered:
                return rule
        return ""


