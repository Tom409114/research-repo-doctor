# AGENTS.md

## Mission

Research Repo Doctor helps researchers and lab teams audit whether public research code is reproducible, reviewable, citable, and release-ready. The CLI must stay deterministic, local-first, and useful without any AI API key.

## Setup

```bash
python -m pip install -e ".[dev]"
```

## Test commands

```bash
pytest
python -m rrdoctor scan tests/fixtures/missing-basics-repo --format markdown --fail-on none
python -m rrdoctor plan tests/fixtures/missing-basics-repo
python -m rrdoctor fix tests/fixtures/missing-basics-repo   # dry-run; add --write to apply
```

## Lint commands

```bash
ruff check .
ruff format --check .
mypy src/rrdoctor
```

## Architecture

- `src/rrdoctor/models.py`: typed report, rule, and fix-plan models.
- `src/rrdoctor/config.py`: `.rrdoctor.yml` defaults and overrides.
- `src/rrdoctor/scanner.py`: path traversal, exclude handling, rule execution.
- `src/rrdoctor/rules/`: deterministic rule modules.
- `src/rrdoctor/fixers.py`: deterministic, idempotent auto-fixers (scaffolding only).
- `src/rrdoctor/baseline.py`: diff a scan against a stored baseline report.
- `src/rrdoctor/reporting/`: Markdown, JSON, SARIF, agent-plan, and badge renderers.
- `src/rrdoctor/cli.py`: Typer CLI (`scan`, `fix`, `plan`, `badge`, `init`, ...).

## Rule authoring rules

- Rules must be deterministic and not require network access.
- Emit actionable findings with concise evidence and remediation.
- Respect path excludes through the scan context.
- Mask possible secrets in all evidence.
- Add tests or fixtures for every new rule.
- Update docs and rule tables.

## Fixer authoring rules

- Fixers must be deterministic and idempotent.
- Never overwrite or delete existing files; create or safely append only.
- Never execute code from the scanned repository and never make network calls.
- Generated content may contain clearly marked placeholders for human review.
- Anything requiring judgement belongs in the agent fix plan, not a fixer.

## Style

- Python 3.10 minimum.
- Keep heuristics simple and readable.
- Prefer small rule modules over hidden global behavior.
- Add comments only when they clarify non-obvious logic.

## Do not do

- Do not add network calls to the core scanner.
- Do not require a hosted-service API key.
- Do not expose secrets in reports.
- Do not fabricate adoption metrics.
- Do not add vague automation features without deterministic fallback.
