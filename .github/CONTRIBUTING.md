# Contributing to InjectRange

Thanks for considering a contribution. InjectRange is an offline harness: it
runs a pinned probe corpus against a guard and never talks to a live model.

## Development setup

- Python 3.11+. The package uses the standard library only.

```bash
python -m compileall -q src
python -m pytest -q
PYTHONPATH=src python -m injectrange --help
```

## Before you open a pull request

1. Compile and the full test suite must pass.
2. Every new class needs sample probes, a test and a paragraph in the README
   explaining what a breach means.
3. Keep the package dependency-free.
