.PHONY: setup check test lint fmt

setup:
	pip install -e ".[dev,mcp]"

check: lint test

lint:
	ruff check .
	ruff format --check .

fmt:
	ruff format .
	ruff check --fix .

test:
	pytest -q
