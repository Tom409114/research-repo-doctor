# Research Repo Doctor

[![CI](https://github.com/Tom409114/research-repo-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/Tom409114/research-repo-doctor/actions/workflows/ci.yml)
[![rrdoctor score](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Tom409114/research-repo-doctor/main/.rrdoctor-badge.json)](https://github.com/Tom409114/research-repo-doctor)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

**Get your research artifact reviewer-ready before you submit.**

Research Repo Doctor (`rrdoctor`) is reproducibility infrastructure for research code: a
local-first CLI and GitHub Action that **audits** whether a repository is reproducible,
reviewable, citable, and release-ready, **fixes** the mechanical gaps, hands the rest to any
coding agent as a verifiable plan, and maps the result to the artifact checklists that have a
deadline attached — ACM Artifact Evaluation (Available / Functional / Reproduced) and the
NeurIPS reproducibility checklist.

The audit is deterministic and runs without an AI API key, network access, or hosted
service. That same determinism makes it an honest grader: it can verify fixes made by a
person *or* a coding agent.

```text
audit ──▶ fix ──▶ plan ──▶ (your coding agent / you) ──▶ verify ──▶ PR
  │         │        │                                      │
  └ rrdoctor scan    └ rrdoctor fix --write                 └ rrdoctor scan --baseline
            └ rrdoctor plan (tool-agnostic work order)        --fail-on-new error
```

```bash
# Zero-clone (needs uv or pipx):
uvx --from git+https://github.com/Tom409114/research-repo-doctor rrdoctor scan .
# Before a deadline: draft the Artifact Appendix + ACM/NeurIPS checklist mapping
uvx --from git+https://github.com/Tom409114/research-repo-doctor rrdoctor appendix . --profile acm
```

Keywords: research software, reproducibility, artifact evaluation, repository audit, auto-fix,
coding agents, AGENTS.md, GitHub Action, notebooks, data availability, citation metadata.

## Why this matters

Research code often lands on GitHub under deadline pressure. A reviewer or future lab
member finds a promising repository and then loses hours because the environment is
underspecified, data paths are local, notebooks contain stale outputs, dependencies are
unpinned, or the citation is unclear.

Research Repo Doctor turns those recurring release blockers into deterministic checks with
concrete remediation — and, where it is safe to do so, fixes them for you. It is built to
sit in the ordinary maintenance path: run locally while preparing a release, then run
automatically on pull requests through GitHub Actions.

## What's new in 0.3.0

- **`rrdoctor appendix`** — generates an ACM-style Artifact Appendix skeleton and maps findings
  to ACM badge tiers and the NeurIPS reproducibility checklist, so you can fill the artifact
  paperwork before a deadline.
- **`rrdoctor verify`** — an L1 (static) / L2 (environment build) / L3 (entrypoint run)
  reproducibility ladder. With `--run` it actually resolves dependencies (`uv`/`pip`/`conda`/`Rscript`)
  and executes a declared entrypoint under a timeout. Only use `--run` on repositories you trust.
- **Submission profiles** — `acm`, `neurips`, `icml`, `ml-paper`, `fair4rs`, `joss`, with
  tag-based inheritance from the base tiers.
- **Deeper static checks** — `RRD034` cross-checks imports against the dependency manifest
  (deptry-style); `RRD054` flags hardcoded GPU/CUDA assumptions without a documented requirement.
- **More ecosystems** — dependency/runtime checks now understand R (`DESCRIPTION`, `renv.lock`)
  and Julia (`Project.toml`) in addition to Python and JavaScript.
- **`rrdoctor mcp`** — an MCP server exposing `scan`/`verify`/`appendix` as tools for coding
  agents (`pip install 'rrdoctor[mcp]'`).

## What's new in 0.2.0

- **`rrdoctor fix`** — deterministic, idempotent auto-fix for common gaps (governance docs,
  citation metadata, data/results provenance, changelog, ignore entries). Never overwrites.
- **`rrdoctor plan`** — a tool-agnostic fix plan you can hand to any coding agent; every task
  names the deterministic check that verifies it.
- **Baseline gating** — `rrdoctor scan --baseline report.json --fail-on-new error` fails only
  on *newly introduced* findings, so large repos can adopt the audit incrementally.
- **`rrdoctor badge`** — a Shields.io endpoint or SVG reproducibility-score badge.
- **First-class PR automation** — the Action posts a sticky PR comment, writes a job summary,
  and can attach the fix plan, using only the built-in `GITHUB_TOKEN`.
- **New rules** — unpinned dependencies, committed notebook checkpoints, pre-commit config,
  and an AGENTS.md task guide for agent and human contributors.

## Install

Zero-clone (needs `uv` or `pipx`):

```bash
uvx --from git+https://github.com/Tom409114/research-repo-doctor rrdoctor scan .
```

After PyPI publishing this becomes:

```bash
uvx rrdoctor scan .        # or: pipx run rrdoctor scan .  /  pip install rrdoctor
```

From source (for development):

```bash
git clone https://github.com/Tom409114/research-repo-doctor.git
cd research-repo-doctor
python -m pip install -e ".[dev]"
rrdoctor scan .
```

## Quickstart

```bash
rrdoctor scan .                 # deterministic audit (Markdown report)
rrdoctor fix . --write          # apply safe scaffolding for the easy gaps
rrdoctor plan . --output plan.md  # tool-agnostic work order for the rest
rrdoctor scan . --format json --output baseline.json --fail-on none
rrdoctor scan . --baseline baseline.json --fail-on-new error  # gate regressions
```

Stricter gate and report file:

```bash
rrdoctor scan . --profile strict --fail-on warning --output rrdoctor-report.md
```

Machine-readable and agent output:

```bash
rrdoctor scan . --format sarif --output rrdoctor.sarif --fail-on none
rrdoctor scan . --format agent --output fix-plan.md
```

Before a submission deadline:

```bash
rrdoctor appendix . --profile acm --output ARTIFACT_APPENDIX.md   # appendix + checklist mapping
rrdoctor verify . --profile neurips                               # L1/L2/L3 ladder (static)
rrdoctor verify . --run --timeout 600                             # actually build + run (trusted repos)
```

Submission profiles: `acm`, `neurips`, `icml`, `ml-paper`, `fair4rs`, `joss` (alongside the
general `minimal`/`standard`/`strict`/`ml` tiers). Dependency and runtime checks also understand
R (`DESCRIPTION`, `renv.lock`) and Julia (`Project.toml`), not just Python and JavaScript.

## The audit → fix → verify loop

A deterministic checker is reproducible and trustworthy but cannot write prose or judge
intent. A coding agent edits well but needs a precise specification and an objective
definition of done. Research Repo Doctor gives you both:

1. **Audit** — `rrdoctor scan` produces deterministic findings.
2. **Fix the easy ones** — `rrdoctor fix --write` scaffolds governance docs, citation
   metadata, provenance notes, a changelog, and ignore entries (idempotent, never
   overwriting).
3. **Plan the rest** — `rrdoctor plan` emits a tool-agnostic work order. Paste it into the
   coding agent of your choice, attach it to an issue, or work it by hand.
4. **Verify** — re-run the audit against a baseline. Because verification is deterministic
   and key-free, it works as an honest grader for changes from any source.

See [docs/agent-workflows.md](docs/agent-workflows.md) and [docs/autofix.md](docs/autofix.md).

## GitHub Action

Add one workflow to many repositories and get consistent reproducibility reports on pull
requests and pushes. The Action requires no API key.

```yaml
name: Reproducibility audit

on:
  pull_request:

permissions:
  contents: read
  pull-requests: write

jobs:
  rrdoctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Tom409114/research-repo-doctor@v0.2.0
        with:
          profile: standard
          fail-on: none
          comment-pr: "true"     # sticky PR comment with the report
          step-summary: "true"   # report in the job summary
          plan: "true"           # attach an agent-ready fix plan
```

For new-finding gating and a committed baseline, see
[docs/pull-request-automation.md](docs/pull-request-automation.md).

## Example output

```text
Research Repo Doctor Summary
Profile: standard
Score: 76/100
Errors: 1
Warnings: 5
Rules evaluated: 32

How to fix first:
- RRD030 No dependency manifest found: Add pyproject.toml, requirements.txt, or another manifest.
- RRD040 Data availability documentation missing: Add DATA.md, docs/data.md, or a README section.
```

Worked examples live in [examples/reports/](examples/reports/), including a
[fix plan](examples/reports/fix-plan.md) and a [self-scan report](examples/reports/self-scan-report.md).

## Commands

| Command | Purpose |
| --- | --- |
| `rrdoctor scan` | Run the deterministic audit; supports `--baseline` and `--fail-on-new`. |
| `rrdoctor fix` | Apply safe, idempotent scaffolding for common gaps (`--write` to apply). |
| `rrdoctor plan` | Emit a tool-agnostic fix plan (Markdown or JSON). |
| `rrdoctor verify` | Reproducibility ladder L1/L2/L3; `--run` actually builds and executes. |
| `rrdoctor appendix` | Generate an ACM Artifact Appendix + ACM/NeurIPS checklist mapping. |
| `rrdoctor badge` | Emit a reproducibility-score badge (Shields.io endpoint or SVG). |
| `rrdoctor mcp` | Run the MCP server (`scan`/`verify`/`appendix` as agent tools). |
| `rrdoctor init` | Write a documented `.rrdoctor.yml`. |
| `rrdoctor list-rules` | List all registered rules. |
| `rrdoctor explain RRD0xx` | Explain a rule and how to remediate it. |
| `rrdoctor doctor` | Self-diagnostics. |

## Rule categories

Documentation, environment, data, experiments, notebooks, citation, governance, testing,
CI, security, release, and metadata. The full table is in [docs/checks.md](docs/checks.md);
auto-fixable rules are marked there.

## Reproducibility stance

Research Repo Doctor does not claim to prove a paper is reproducible. It checks release
hygiene that makes reproduction possible to attempt. Reports are heuristic and should be
reviewed by maintainers. Generated fixes are starting points and contain placeholders to
complete before release.

## Philosophy

Deterministic first. The scanner is understandable, testable, and useful with no network
access. The core scanner will not add network calls, require a hosted-service API key, or
fabricate adoption metrics. AI is something you bring to *act on* the output — never a
dependency of the audit itself, and never tied to a single tool.

## Configuration

```yaml
version: 1
profile: standard
paths:
  exclude: [".git", ".venv", "node_modules", "__pycache__"]
thresholds:
  large_file_mb: 50
  large_notebook_output_kb: 1024
rules:
  RRD032:
    enabled: false
  RRD042:
    severity: warning
fail_on: error
```

See [docs/configuration.md](docs/configuration.md).

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md),
open a rule request or false-positive report, and include a minimal fixture when possible.

## Security

Do not report suspected credential exposure in a public issue. See [SECURITY.md](SECURITY.md).

## Citation

Use the included [CITATION.cff](CITATION.cff).

## License

MIT. See [LICENSE](LICENSE).
