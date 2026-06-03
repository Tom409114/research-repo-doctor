# Contributing

Thanks for helping improve Research Repo Doctor. The project is early, so small, well-tested contributions are especially valuable.

## Setup

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
```

## Good first contributions

- Add R language environment detection.
- Add Julia environment detection.
- Improve notebook path detection.
- Add Zenodo/DOI detection.
- Add Snakemake/Nextflow workflow detection.
- Add docs website deployment.

## Rule contribution contract

Rules must be deterministic, local-first, and explainable. A rule should emit concise evidence, avoid scanning binary content except for size checks, respect configured excludes, and never print full secrets.

## Rule contribution process

1. Open or link a rule request describing the reproducibility risk.
2. Propose deterministic evidence and likely false-positive cases.
3. Add rule metadata and implementation in `src/rrdoctor/rules/`.
4. Add a focused fixture or unit test.
5. Update `docs/checks.md` and `docs/rule-authoring.md` when behavior changes.
6. Run `pytest`, `ruff check .`, and `ruff format --check .`.

Every new rule should include rule metadata, tests, docs, and remediation text that a researcher can act on.

## Review expectations

Pull requests should keep the scanner understandable. Avoid broad rewrites unless they reduce real maintenance cost. If a rule is heuristic, say so in the rule description and tests.
