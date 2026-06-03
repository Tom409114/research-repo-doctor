.PHONY: install test lint format-check self-scan

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

format-check:
	ruff format --check .

self-scan:
	rrdoctor scan . --profile standard --format markdown --output examples/reports/self-scan-report.md --fail-on none
