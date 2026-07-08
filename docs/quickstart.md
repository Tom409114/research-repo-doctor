# Quickstart

## Install

Run from PyPI without adding it to the project:

```bash
uvx rrdoctor scan .
```

Alternatives:

```bash
pipx run rrdoctor scan .
python -m pip install rrdoctor
rrdoctor scan .
```

For development:

```bash
git clone https://github.com/Tom409114/research-repo-doctor.git
cd research-repo-doctor
python -m pip install -e ".[dev]"
```

## Scan

```bash
rrdoctor scan .
```

The default report is Markdown. Use JSON for automation:

```bash
rrdoctor scan . --format json --quiet
```

## Interpret the result

The report leads with an Artifact Evaluation-style readiness level: `Available`,
`Functional`, or `Reproduced-ready`. The numeric score remains as a secondary
triage signal, not proof that a repository is reproducible.

Fix errors first, then warnings that affect setup, data access, experiment entrypoints, notebooks, tests, and CI.

## Fix the easy ones automatically

```bash
rrdoctor fix .            # preview
rrdoctor fix . --write    # apply safe scaffolding
```

See [auto-fix](autofix.md).

## Get a plan for the rest

```bash
rrdoctor plan . --output fix-plan.md
```

The plan is tool-agnostic: hand it to any coding agent or work through it by hand,
then re-run `rrdoctor scan` to verify. See [agent workflows](agent-workflows.md).

## Before a submission deadline

```bash
# One local packet: report, fix plan, appendix, and verification ladder:
rrdoctor prepare . --profile acm --out-dir rrdoctor-prep

# ACM Artifact Appendix skeleton + ACM badge / NeurIPS checklist mapping:
rrdoctor appendix . --profile acm --output ARTIFACT_APPENDIX.md

# Verification ladder. Static by default; --run actually resolves deps and runs the entrypoint:
rrdoctor verify . --profile neurips
rrdoctor verify . --run --timeout 600        # only on repositories you trust
rrdoctor verify . --command "python train.py config/default.py" --run --timeout 600
```

Submission profiles: `acm`, `neurips`, `icml`, `ml-paper`, `fair4rs`, `joss`. Dependency and
runtime checks also understand R (`DESCRIPTION`, `renv.lock`) and Julia (`Project.toml`).

For a fuller deadline-oriented sequence, see the
[Artifact Evaluation deadline workflow](ae-deadline-workflow.md).

## Use from a coding agent (MCP)

```bash
pip install 'rrdoctor[mcp]'
rrdoctor mcp        # exposes scan/verify/appendix as MCP tools over stdio
```

The MCP `verify` tool accepts `command` and `timeout` arguments, so a coding
agent can use the same trusted run-path gate as the CLI. For stdio client
configuration, smoke tests, and safety notes, see [MCP integration](mcp.md).

## Add the GitHub Action

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.15
  with:
    profile: standard
    fail-on: warning
    output: rrdoctor-report.md
```

For PR comments, job summaries, and new-finding gating, see
[pull request automation](pull-request-automation.md).
