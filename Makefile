.PHONY: setup check test lint fmt

# Run tools through the interpreter that has the package installed, not whatever
# `pytest` or `ruff` happens to be first on PATH.
PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e ".[dev,mcp]"

check: lint test

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

fmt:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .

test:
	$(PYTHON) -m pytest -q
