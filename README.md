# Research Repo Doctor

[![CI](https://github.com/research-repo-doctor/research-repo-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/research-repo-doctor/research-repo-doctor/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/badge/PyPI-after%20v0.1.0-blue)](https://pypi.org/project/rrdoctor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Research Repo Doctor (`rrdoctor`) is research reproducibility infrastructure: a local-first CLI and GitHub Action for auditing whether a research code repository is reproducible, reviewable, citable, and ready for public release.

It is not a generic repository health checker. It focuses on the practical things that often decide whether research code can be reused: environment files, data documentation, experiment entrypoints, notebooks, citation metadata, README quality, tests, CI, security hygiene, and release readiness.

The scanner is deterministic and works without an AI API key, network access, or hosted service. Maintainers may use Codex or API credits for project maintenance workflows, but the user-facing CLI does not require OpenAI.

Keywords: research software, reproducibility, GitHub Action, repository audit, notebooks, data availability, citation metadata.

## Why this matters

Research code often lands on GitHub under deadline pressure. A reviewer or future lab member may find a promising repository, then lose time because the environment is underspecified, data paths are local, notebooks contain stale outputs, or the paper citation is unclear.

Research Repo Doctor turns those recurring release blockers into deterministic checks with concrete remediation. It is meant to sit in the ordinary maintenance path for research software: run locally while preparing a release, then run automatically in pull requests through GitHub Actions.

## Installation and setup

Install from source for the initial release:

```bash
git clone https://github.com/research-repo-doctor/research-repo-doctor.git
cd research-repo-doctor
python -m pip install -e ".[dev]"
rrdoctor scan .
```

After the PyPI release:

```bash
python -m pip install rrdoctor
rrdoctor scan .
```

Create a config file:

```bash
rrdoctor init --profile standard
```

Scan with a stricter gate:

```bash
rrdoctor scan . --profile strict --fail-on warning --output rrdoctor-report.md
```

Machine-readable output:

```bash
rrdoctor scan . --format json --quiet
rrdoctor scan . --format sarif --output rrdoctor.sarif --fail-on none
```

## Reproducibility stance

Research Repo Doctor does not claim to prove a paper is reproducible. It checks release hygiene that makes reproduction possible to attempt: documented setup, dependency metadata, data availability, experiment entrypoints, notebook state, citation metadata, CI, tests, and security hygiene. Reports are heuristic and should be reviewed by maintainers.

## Example output excerpt

```text
Research Repo Doctor Summary
Profile: standard
Score: 76/100
Errors: 1
Warnings: 5
Rules evaluated: 25

How to fix first:
- RRD030 No dependency manifest found: Add pyproject.toml, requirements.txt, environment.yml, or another supported manifest.
- RRD040 Data availability documentation missing: Add DATA.md, docs/data.md, data/README.md, or a README data availability section.
```

## GitHub Action

GitHub Action integration is the main adoption path. A lab can add one workflow to many repositories and get consistent reproducibility reports on pull requests and pushes.

Use the action in another repository:

```yaml
name: Research Repo Doctor

on:
  pull_request:
  push:
    branches: [main]

jobs:
  rrdoctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: research-repo-doctor/research-repo-doctor@v0.1.0
        with:
          profile: standard
          fail-on: warning
          output: rrdoctor-report.md
```

The action does not require an API key. It installs the package from the checked-out action repository and runs `rrdoctor scan`.

## For maintainers

Research Repo Doctor is designed to be maintainable as an OSS rule project:

- Rules are deterministic, documented, and fixture-tested.
- False positives and false negatives have dedicated issue templates.
- New rules require a clear reproducibility risk, evidence model, remediation text, and tests.
- Releases are expected to run tests, linting, action smoke tests, and a self-scan report.
- Security hygiene is part of the product: reports mask secret-like evidence and the scanner avoids network calls.

## Rule categories

- Documentation: README setup, usage, and reproduction guidance.
- Environment: dependency manifests, runtime versions, optional containers.
- Data: data availability, large files, local absolute paths.
- Experiments: entrypoints, configs, seeds, results provenance.
- Notebooks: large outputs, execution order, paths, secrets, paired scripts.
- Citation: CITATION.cff and paper metadata.
- Governance: contribution, security, and conduct policies.
- Testing and CI: test files, test runners, and workflow quality gates.
- Security: conservative secret detection and research artifact ignores.
- Release and metadata: changelog, version metadata, package metadata, topic guidance.

## Configuration

```yaml
version: 1
profile: standard
paths:
  include:
    - "."
  exclude:
    - ".git"
    - ".venv"
    - "node_modules"
    - "__pycache__"
thresholds:
  large_file_mb: 50
  large_notebook_output_kb: 1024
rules:
  RRD032:
    enabled: false
  RRD042:
    severity: warning
fail_on: error
report:
  format: markdown
  output: rrdoctor-report.md
```

Rules can be enabled or disabled, severities can be overridden, and thresholds can be tuned for a repository's domain.

## Philosophy

Research Repo Doctor is deterministic first. The scanner should be understandable, testable, and useful on an airplane with no network access. AI-assisted workflows are optional and maintainer-facing: triaging false positives, drafting tests, reviewing rule changes, summarizing release notes, and analyzing failure cases. The core scanner will not add network calls, require an OpenAI API key, or fabricate adoption metrics.

## Roadmap

See [ROADMAP.md](ROADMAP.md). The first release focuses on stable deterministic checks and GitHub Action support. Future work includes stronger SARIF support, more language ecosystems, richer rule authoring docs, and carefully reviewed optional maintainer automations.

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), open a rule request or false positive report, and include a minimal fixture when possible.

## Security

Do not report suspected credential exposure in a public issue. See [SECURITY.md](SECURITY.md).

## Citation

Use the included [CITATION.cff](CITATION.cff). Citation metadata will be updated after v0.1.0 is released.

## License

MIT. See [LICENSE](LICENSE).
