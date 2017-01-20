"""Breach class taxonomy.

A breach class names one family of prompt-injection technique that a guard is
expected to reject. The corpus tags every pattern with exactly one class, and
the harness reports a per-class result so a regression shows up as a named class
opening rather than a single opaque score change.
"""

from __future__ import annotations

from typing import Dict, List, NamedTuple


class BreachClass(NamedTuple):
    """One family of injection technique."""

    key: str
    title: str
    description: str


# Ordered so reports and matrices are stable across runs.
BREACH_CLASSES: List[BreachClass] = [
    BreachClass(
        key="instruction_override",
        title="Instruction override",
        description="Attempts to cancel or replace the standing instructions.",
    ),
    BreachClass(
        key="role_confusion",
        title="Role confusion",
        description="Attempts to reassign the assistant to a new persona or role.",
    ),
    BreachClass(
        key="delimiter_escape",
        title="Delimiter escape",
