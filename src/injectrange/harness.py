"""Run the corpus against a guard and collect outcomes.

The harness evaluates every corpus probe against a guard and records, per breach
class, how many probes were blocked and how many leaked. A class breaches when
at least one probe in it leaks past the guard. The result is a plain data
structure so report.py can render it and diff.py can compare two of them.
"""
