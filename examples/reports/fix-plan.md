# Reproducibility Fix Plan

- Repository: `/path/to/missing-basics-repo`
- Profile: `standard`
- Current score: **12/100**
- Tasks: `12` (5 auto-fixable)

## How to use this plan

This plan is tool-agnostic: hand it to any coding agent or work through it by hand. Each task names the deterministic check that verifies it. The audit is the source of truth, so apply a change and then re-run the check.

1. Apply the mechanical fixes first: `rrdoctor fix --write`.
2. Work the remaining tasks below, smallest blast radius first.
3. Verify with `rrdoctor scan <path> --fail-on none` and aim to raise the score.

## Tasks

### 1. RRD040 Data availability documentation missing [error] (auto-fixable: `rrdoctor fix`)

- Category: data
- Files: (repository root)
- Do: Add DATA.md, docs/data.md, data/README.md, or a README data availability section.
- Verify: Re-run `rrdoctor scan` and confirm RRD040 no longer reports a finding.

### 2. RRD001 README missing [error]

- Category: documentation
- Files: (repository root)
- Do: Add a README with project scope, setup, usage, and reproducibility instructions.
- Verify: Re-run `rrdoctor scan` and confirm RRD001 no longer reports a finding.

### 3. RRD030 No dependency manifest found [error]

- Category: environment
- Files: (repository root)
- Do: Add pyproject.toml, requirements.txt, environment.yml, or another supported manifest.
- Verify: Re-run `rrdoctor scan` and confirm RRD030 no longer reports a finding.

### 4. RRD050 No experiment entrypoint found [error]

- Category: experiments
- Files: (repository root)
- Do: Add scripts/reproduce.sh, scripts/run*.sh, a Makefile, or documented train/eval scripts.
- Verify: Re-run `rrdoctor scan` and confirm RRD050 no longer reports a finding.

### 5. RRD010 LICENSE missing [error] (auto-fixable: `rrdoctor fix`)

- Category: governance
- Files: (repository root)
- Do: Add an OSI-approved license such as MIT, BSD-3-Clause, or Apache-2.0.
- Verify: Re-run `rrdoctor scan` and confirm RRD010 no longer reports a finding.

### 6. RRD080 No CI workflow detected [warning]

- Category: ci
- Files: (repository root)
- Do: Add a GitHub Actions workflow or another CI configuration that runs tests/linting.
- Verify: Re-run `rrdoctor scan` and confirm RRD080 no longer reports a finding.

### 7. RRD020 Citation instructions missing [warning] (auto-fixable: `rrdoctor fix`)

- Category: citation
- Files: (repository root)
- Do: Add CITATION.cff or a clear citation section in the README.
- Verify: Re-run `rrdoctor scan` and confirm RRD020 no longer reports a finding.

### 8. RRD100 CHANGELOG missing [warning] (auto-fixable: `rrdoctor fix`)

- Category: release
- Files: (repository root)
- Do: Add CHANGELOG.md with at least an initial v0.1.0 entry.
- Verify: Re-run `rrdoctor scan` and confirm RRD100 no longer reports a finding.

### 9. RRD101 No version metadata found [warning]

- Category: release
- Files: (repository root)
- Do: Add package version metadata, VERSION file, or release tags.
- Verify: Re-run `rrdoctor scan` and confirm RRD101 no longer reports a finding.

### 10. RRD091 .gitignore missing common research artifacts [warning] (auto-fixable: `rrdoctor fix`)

- Category: security
- Files: (repository root)
- Do: Add entries for .env, caches, raw data, checkpoints, wandb, and mlruns.
- Verify: Re-run `rrdoctor scan` and confirm RRD091 no longer reports a finding.

### 11. RRD070 No tests directory or test files found [warning]

- Category: testing
- Files: (repository root)
- Do: Add tests/ or at least one test_*.py / *_test.py file.
- Verify: Re-run `rrdoctor scan` and confirm RRD070 no longer reports a finding.

### 12. RRD071 No test runner/configuration detected [warning]

- Category: testing
- Files: (repository root)
- Do: Document or configure a test runner such as pytest, tox, nox, or package scripts.
- Verify: Re-run `rrdoctor scan` and confirm RRD071 no longer reports a finding.

## Acceptance

When the plan is complete, re-run the audit. The resolved tasks should no longer appear and the overall score should increase. Use a baseline to gate regressions in CI:

```bash
rrdoctor scan . --format json --output rrdoctor-baseline.json --fail-on none
# ...apply changes...
rrdoctor scan . --baseline rrdoctor-baseline.json --fail-on-new error
```
