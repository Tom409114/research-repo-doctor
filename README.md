# Research Repo Doctor

Get your research artifact ready for Artifact Evaluation before the deadline:
scan the repo, scaffold the easy fixes, verify the run path, and generate the appendix.

[![CI](https://github.com/Tom409114/research-repo-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/Tom409114/research-repo-doctor/actions/workflows/ci.yml)
[![rrdoctor readiness](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Tom409114/research-repo-doctor/main/.rrdoctor-badge.json)](https://github.com/Tom409114/research-repo-doctor)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

`rrdoctor` is a local CLI and GitHub Action for research artifact preparation. It audits
whether a repo is reviewable, citable, and close to runnable; scaffolds safe mechanical
fixes; maps findings to an AE-style readiness level; and turns the rest into a checklist
any coding agent or human can finish.

## AE deadline loop

```bash
uvx rrdoctor scan . --profile acm
uvx rrdoctor fix . --write
uvx rrdoctor appendix . --profile acm --output ARTIFACT_APPENDIX.md
uvx rrdoctor verify . --profile acm
```

For trusted repositories, `rrdoctor verify --run` can go beyond static checks and actually
resolve dependencies and execute the declared entrypoint under a timeout.

## What it catches

- **"Your `--seed` flag does nothing."** `RRD052` spots code that declares a seed option but
  never calls `random.seed`, `np.random.seed`, `torch.manual_seed`, `tf.random.set_seed`, or
  `random_state=seed`.
- **"This worked on my laptop."** Local-only data paths, missing data provenance, and
  undocumented retrieval steps.
- **"The environment silently changed."** Unpinned dependencies, missing runtime versions,
  undeclared imports, and absent dependency manifests.
- **"The notebook lies."** Stale outputs, out-of-order execution, checkpoint artifacts, and
  secret-like notebook output.
- **"Reviewers cannot tell how to cite or rerun this."** Missing license, citation, CI,
  tests, changelog, results provenance, or experiment entrypoint.

## Install

Run once, without installing:

```bash
uvx rrdoctor scan .
```

Alternatives:

```bash
pipx run rrdoctor scan .
pip install rrdoctor
rrdoctor scan .
```

Developer install from source:

```bash
git clone https://github.com/Tom409114/research-repo-doctor.git
cd research-repo-doctor
python -m pip install -e ".[dev]"
rrdoctor scan .
```

## Fix the easy gaps

Let `rrdoctor` create the safe scaffolding for you. It is deterministic, idempotent, and
never overwrites existing files.

```bash
rrdoctor fix . --write
```

It can scaffold missing governance docs, citation metadata, data/results provenance notes,
changelog entries, and common research `.gitignore` entries. The hard parts become a
reviewable plan:

```bash
rrdoctor plan . --output plan.md
```

## Use with your coding agent

Paste this into Claude Code, Cursor, GitHub Copilot, or any other coding agent:

```text
Use rrdoctor as the deterministic, offline, no-API-key grader for this research repo.

Run:
rrdoctor scan . --format json --output baseline.json
rrdoctor plan . --output plan.md

Work through plan.md without weakening rrdoctor checks.

Definition of done:
rrdoctor scan . --baseline baseline.json --fail-on-new error
```

The final command is the objective gate: it verifies the agent's work against the starting
baseline and fails only on newly introduced errors.

Keywords: research software, reproducibility, artifact evaluation, repository audit, auto-fix,
coding agents, AGENTS.md, GitHub Action, notebooks, data availability, citation metadata.

## Why this matters

Research code often lands on GitHub under deadline pressure. A reviewer or future lab
member finds a promising repository and then loses hours because the environment is
underspecified, data paths are local, notebooks contain stale outputs, dependencies are
unpinned, or the citation is unclear.

Research Repo Doctor turns those recurring release blockers into deterministic checks with
concrete remediation - and, where it is safe to do so, fixes them for you. It is built to
sit in the ordinary maintenance path: run locally while preparing a release, then run
automatically on pull requests through GitHub Actions.

The audit runs without an AI API key, network access, or hosted service. That same
determinism makes it an honest grader: it can verify fixes made by a person or a coding
agent.

```text
audit -> fix -> plan -> (your coding agent / you) -> verify -> PR
  |       |       |                                  |
  |       |       rrdoctor plan                      rrdoctor scan --baseline
  |       rrdoctor fix --write                       --fail-on-new error
  rrdoctor scan
```

## What's new in 0.2.3

- **`rrdoctor appendix`** generates an ACM-style Artifact Appendix skeleton and maps findings
  to ACM badge tiers and the NeurIPS reproducibility checklist, so you can fill the artifact
  paperwork before a deadline.
- **`rrdoctor verify`** adds an L1 (static) / L2 (environment build) / L3 (entrypoint run)
  reproducibility ladder. With `--run` it actually resolves dependencies (`uv`/`pip`/`conda`/`Rscript`)
  and executes a declared entrypoint under a timeout. Only use `--run` on repositories you trust.
- **Submission profiles** include `acm`, `neurips`, `icml`, `ml-paper`, `fair4rs`, and `joss`,
  with tag-based inheritance from the base tiers.
- **Deeper static checks** include `RRD034` import/manifest cross-checks (deptry-style) and
  `RRD054` hardcoded GPU/CUDA assumptions without a documented requirement.
- **More ecosystems**: dependency/runtime checks now understand R (`DESCRIPTION`, `renv.lock`)
  and Julia (`Project.toml`) in addition to Python and JavaScript.
- **`rrdoctor mcp`** exposes `scan`/`verify`/`appendix` as tools for coding agents
  (`pip install 'rrdoctor[mcp]'`).

## What's new in 0.2.0

- **`rrdoctor fix`** provides deterministic, idempotent auto-fix for common gaps (governance
  docs, citation metadata, data/results provenance, changelog, ignore entries). Never overwrites.
- **`rrdoctor plan`** emits a tool-agnostic fix plan you can hand to any coding agent; every
  task names the deterministic check that verifies it.
- **Baseline gating**: `rrdoctor scan --baseline report.json --fail-on-new error` fails only
  on newly introduced findings, so large repos can adopt the audit incrementally.
- **`rrdoctor badge`** emits a Shields.io endpoint or SVG artifact-readiness badge.
- **Artifact readiness labels** map findings to an AE-style level: `Available`,
  `Functional`, or `Reproduced-ready`. The numeric score remains as a secondary
  triage signal.
- **First-class PR automation**: the Action posts a sticky PR comment, writes a job summary,
  and can attach the fix plan, using only the built-in `GITHUB_TOKEN`.
- **New rules** include unpinned dependencies, committed notebook checkpoints, pre-commit
  config, and an AGENTS.md task guide for agent and human contributors.

## Quickstart

```bash
rrdoctor scan .                   # deterministic audit (Markdown report)
rrdoctor fix . --write            # apply safe scaffolding for easy gaps
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

## The audit -> fix -> verify loop

A deterministic checker is reproducible and trustworthy but cannot write prose or judge
intent. A coding agent edits well but needs a precise specification and an objective
definition of done. Research Repo Doctor gives you both:

1. **Audit**: `rrdoctor scan` produces deterministic findings.
2. **Fix the easy ones**: `rrdoctor fix --write` scaffolds governance docs, citation metadata,
   provenance notes, a changelog, and ignore entries (idempotent, never overwriting).
3. **Plan the rest**: `rrdoctor plan` emits a tool-agnostic work order. Paste it into the
   coding agent of your choice, attach it to an issue, or work it by hand.
4. **Verify**: re-run the audit against a baseline. Because verification is deterministic
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
      - uses: Tom409114/research-repo-doctor@v0.2.3
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
Readiness: Functional
Score: 64/100
Errors: 0
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
| `rrdoctor badge` | Emit an artifact-readiness badge (Shields.io endpoint or SVG). |
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
fabricate adoption metrics. AI is something you bring to act on the output - never a
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

Use the included [CITATION.cff](CITATION.cff) or cite the archived release DOI:
[10.5281/zenodo.21045373](https://doi.org/10.5281/zenodo.21045373).

```bibtex
@software{research_repo_doctor_2026,
  title = {Research Repo Doctor},
  author = {{Research Repo Doctor Maintainers}},
  version = {0.2.3},
  year = {2026},
  doi = {10.5281/zenodo.21045373},
  url = {https://github.com/Tom409114/research-repo-doctor}
}
```

## License

MIT. See [LICENSE](LICENSE).
