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


def from_config(raw: dict) -> Guard:
    """Build a guard from a parsed config object.

    Expected shape:

        {"name": "strict", "rules": ["ignore all previous", "you are now", ...]}

    Raises GuardError on any structural problem. Rules are lowercased so the
    guard is case-insensitive and its behaviour is deterministic.
    """
    if not isinstance(raw, dict):
        raise GuardError("guard config must be an object")
    name = raw.get("name")
    if not isinstance(name, str) or not name:
        raise GuardError("guard name must be a non-empty string")
    rules = raw.get("rules")
    if not isinstance(rules, list):
        raise GuardError("guard rules must be a list")
    cleaned: List[str] = []
    for index, rule in enumerate(rules):
        if not isinstance(rule, str) or not rule:
            raise GuardError("rule %d must be a non-empty string" % index)
        cleaned.append(rule.lower())
    return Guard(name=name, rules=cleaned)


def load(path: str) -> Guard:
    """Load and build a guard from a JSON config file."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, ValueError) as exc:
        raise GuardError("could not read guard config %r: %s" % (path, exc))
    return from_config(raw)


def known_class_keys() -> List[str]:
    """Expose the taxonomy order for callers that report per class."""
