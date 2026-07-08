.PHONY: install test lint type-check format-check self-scan check

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

lint:
	ruff check .

type-check:
	python -m mypy

format-check:
	ruff format --check .

self-scan:
	python -m rrdoctor scan . --profile standard --format markdown --output examples/reports/self-scan-report.md --fail-on none

check:
	python scripts/check.py
