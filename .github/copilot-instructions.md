# GitHub Copilot Instructions

Research Repo Doctor (`rrdoctor`) is deterministic, local-first research
reproducibility infrastructure. Keep the core scanner offline and key-free.

Use rrdoctor itself as the objective definition of done for agent changes:

```bash
python -m rrdoctor scan . --format json --output baseline.json
python -m rrdoctor plan . --output plan.md
# Work through plan.md without weakening checks.
python -m rrdoctor scan . --baseline baseline.json --fail-on-new error
```

For implementation work, keep changes aligned with the existing architecture:

- Rules live under `src/rrdoctor/rules/` and must be deterministic.
- Every rule needs an RRD id, severity, message, evidence, remediation text, tests,
  and a `docs/checks.md` entry.
- Auto-fixes must be idempotent, non-destructive, and must never overwrite
  existing files.
- Do not add network calls, hosted-service requirements, or API keys to the core
  scan path.
- Mask secret-like values in all reported evidence.
- Prefer small, conservative heuristics over broad claims that create noisy
  first-run findings.

Before proposing a PR, run:

```bash
ruff format --check .
ruff check .
pytest
python -m mypy
python -m rrdoctor scan . --profile standard --fail-on none --quiet
```

If a change touches trusted dynamic verification, also test the relevant
`rrdoctor verify --run --fail-on error` behavior on a controlled fixture. Never
run untrusted external repository code as part of normal scan behavior.
