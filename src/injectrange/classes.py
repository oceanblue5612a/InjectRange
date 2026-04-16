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
        description="Attempts to break out of a quoting or fencing boundary.",
    ),
    BreachClass(
        key="encoding_smuggling",
        title="Encoding smuggling",
        description="Attempts to hide directives behind an encoding or transform.",
    ),
    BreachClass(
        key="tool_coercion",
        title="Tool coercion",
        description="Attempts to force an unrequested tool or command invocation.",
    ),
    BreachClass(
        key="exfiltration_framing",
        title="Exfiltration framing",
        description="Attempts to frame a request as a reason to reveal held secrets.",
    ),
]

CLASS_KEYS: List[str] = [c.key for c in BREACH_CLASSES]

_BY_KEY: Dict[str, BreachClass] = {c.key: c for c in BREACH_CLASSES}


def get_class(key: str) -> BreachClass:
    """Return the breach class for a key, or raise KeyError with a clear message."""
    try:
        return _BY_KEY[key]
    except KeyError:
        known = ", ".join(CLASS_KEYS)
        raise KeyError("unknown breach class %r; known classes: %s" % (key, known))


def is_known(key: str) -> bool:
    """Report whether a key names a known breach class."""
    return key in _BY_KEY
