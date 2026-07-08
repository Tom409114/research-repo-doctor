# Contributing

Thanks for helping improve Research Repo Doctor. The project is early, so small, well-tested contributions are especially valuable.

## Setup

```bash
python -m pip install -e ".[dev]"
python scripts/check.py
```

`make check` is also available on systems with `make`; it delegates to the same
script. If you need to run the gates manually:

```bash
ruff format --check .
ruff check .
python -m mypy
python -m pytest -q
python -m rrdoctor scan . --profile standard --fail-on none
```

## Good first contributions

Good first contributions should be deterministic, local-first, and small enough
to cover with fixtures. Current starter-sized areas:

- Add MATLAB runtime environment detection.
- Add JavaScript/Node research environment refinements.
- Improve notebook path detection fixtures.
- Improve Zenodo, DOI, and arXiv metadata detection.
- Add a fixer for a minimal CI workflow.
- Add docs website deployment.
- Add support for another workflow marker such as CWL or DVC.

If no public issue exists yet, open a rule request or feature request first so
the expected evidence, severity, and false-positive cases are clear.

## Rule contribution contract

Rules must be deterministic, local-first, and explainable. A rule should emit concise evidence, avoid scanning binary content except for size checks, respect configured excludes, and never print full secrets.

## Reporting rule quality issues

False-positive and false-negative reports are high-value contributions. Run
`uvx rrdoctor scan . --format json --output rrdoctor-report.json --fail-on none`,
then open the matching GitHub issue template with the rule ID, rrdoctor version,
command, and a sanitized minimal repository shape. See
[docs/feedback.md](docs/feedback.md) for the full checklist.

## Rule contribution process

1. Open or link a rule request describing the reproducibility risk.
2. Propose deterministic evidence and likely false-positive cases.
3. Add rule metadata and implementation in `src/rrdoctor/rules/`.
4. Add a focused fixture or unit test.
5. Update `docs/checks.md` and `docs/rule-authoring.md` when behavior changes.
6. Run `python scripts/check.py` or the equivalent direct commands from the setup section.

Every new rule should include rule metadata, tests, docs, and remediation text that a researcher can act on.

## Review expectations

Pull requests should keep the scanner understandable. Avoid broad rewrites unless they reduce real maintenance cost. If a rule is heuristic, say so in the rule description and tests.
