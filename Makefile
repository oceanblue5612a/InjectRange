PY ?= python

.PHONY: test lint smoke

test:
	$(PY) -m pytest -q
