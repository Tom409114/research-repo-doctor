# Research Repo Doctor Report

- Repository path: `C:/Users/thuah/Documents/Codex/2026-06-03/files-mentioned-by-the-user-txt/research-repo-doctor/tests/fixtures/missing-basics-repo`
- Generated: `2026-06-03T07:02:59.240656+00:00`
- Profile: `standard`
- Overall score: **12/100**
- Rules evaluated: `30`

> Heuristic note: Research Repo Doctor uses deterministic heuristics. The score is a guide, not a substitute for peer review or maintainer judgment.

## Summary by category

| Category | Score | Errors | Warnings | Info |
| --- | ---: | ---: | ---: | ---: |
| ci | 92 | 0 | 1 | 0 |
| citation | 92 | 0 | 1 | 0 |
| data | 80 | 1 | 0 | 0 |
| documentation | 80 | 1 | 0 | 0 |
| environment | 80 | 1 | 0 | 0 |
| experiments | 80 | 1 | 0 | 0 |
| governance | 80 | 1 | 0 | 0 |
| release | 84 | 0 | 2 | 0 |
| security | 92 | 0 | 1 | 0 |
| testing | 84 | 0 | 2 | 0 |

## How to fix first

- **RRD040** Data availability documentation missing: Add DATA.md, docs/data.md, data/README.md, or a README data availability section.
- **RRD001** README missing: Add a README with project scope, setup, usage, and reproducibility instructions.
- **RRD030** No dependency manifest found: Add pyproject.toml, requirements.txt, environment.yml, or another supported manifest.
- **RRD050** No experiment entrypoint found: Add scripts/reproduce.sh, scripts/run*.sh, a Makefile, or documented train/eval scripts.
- **RRD010** LICENSE missing: Add an OSI-approved license such as MIT, BSD-3-Clause, or Apache-2.0.
- **RRD080** No CI workflow detected: Add a GitHub Actions workflow or another CI configuration that runs tests/linting.
- **RRD020** Citation instructions missing: Add CITATION.cff or a clear citation section in the README.
- **RRD100** CHANGELOG missing: Add CHANGELOG.md with at least an initial v0.1.0 entry.

## Findings

### error / data

#### RRD040: Data availability documentation missing

No data availability documentation was found.

Recommendation: Add DATA.md, docs/data.md, data/README.md, or a README data availability section.

### error / documentation

#### RRD001: README missing

No README file was found at the repository root.

Recommendation: Add a README with project scope, setup, usage, and reproducibility instructions.

### error / environment

#### RRD030: No dependency manifest found

No supported dependency manifest was found.

Recommendation: Add pyproject.toml, requirements.txt, environment.yml, or another supported manifest.

### error / experiments

#### RRD050: No experiment entrypoint found

No experiment or reproduction entrypoint was detected.

Recommendation: Add scripts/reproduce.sh, scripts/run*.sh, a Makefile, or documented train/eval scripts.

### error / governance

#### RRD010: LICENSE missing

No LICENSE file was found.

Recommendation: Add an OSI-approved license such as MIT, BSD-3-Clause, or Apache-2.0.

### warning / ci

#### RRD080: No CI workflow detected

No CI configuration was detected.

Recommendation: Add a GitHub Actions workflow or another CI configuration that runs tests/linting.

### warning / citation

#### RRD020: Citation instructions missing

No CITATION.cff or citation guidance was found.

Recommendation: Add CITATION.cff or a clear citation section in the README.

### warning / release

#### RRD100: CHANGELOG missing

No CHANGELOG file was found.

Recommendation: Add CHANGELOG.md with at least an initial v0.1.0 entry.

#### RRD101: No version metadata found

No version metadata was detected.

Recommendation: Add package version metadata, VERSION file, or release tags.

### warning / security

#### RRD091: .gitignore missing common research artifacts

.gitignore is missing.

Recommendation: Add entries for .env, caches, raw data, checkpoints, wandb, and mlruns.

### warning / testing

#### RRD070: No tests directory or test files found

No tests directory or test files were detected.

Recommendation: Add tests/ or at least one test_*.py / *_test.py file.

#### RRD071: No test runner/configuration detected

No obvious test runner or test command configuration was detected.

Recommendation: Document or configure a test runner such as pytest, tox, nox, or package scripts.

Evidence:
- Searched pyproject, tox/nox, package scripts, and workflows.

## Suggested GitHub issues

- [error] Fix RRD040: Data availability documentation missing
- [error] Fix RRD001: README missing
- [error] Fix RRD030: No dependency manifest found
- [error] Fix RRD050: No experiment entrypoint found
- [error] Fix RRD010: LICENSE missing
- [warning] Fix RRD080: No CI workflow detected
- [warning] Fix RRD020: Citation instructions missing
- [warning] Fix RRD100: CHANGELOG missing
- [warning] Fix RRD101: No version metadata found
- [warning] Fix RRD091: .gitignore missing common research artifacts

## Reproducibility checklist

- [ ] README explains setup, usage, and result reproduction.
- [ ] Dependencies and runtime versions are documented.
- [ ] Data availability and provenance are documented.
- [ ] Experiment entrypoints and configuration are discoverable.
- [ ] Notebooks are clean, ordered, and free of secrets.
- [ ] Tests and CI provide a basic quality gate.
- [ ] Citation, license, changelog, and release metadata are present.
