PY ?= python

.PHONY: test lint smoke

test:
	$(PY) -m pytest -q

lint:
	$(PY) -m compileall -q src

smoke:
	PYTHONPATH=src $(PY) -m injectrange --help

<!-- draft note 1621 -->
