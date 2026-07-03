# Quickstart

## Install

Zero-clone (needs `uv` or `pipx`):

```bash
uvx --from git+https://github.com/Tom409114/research-repo-doctor rrdoctor scan .
```

After PyPI publishing:

```bash
uvx rrdoctor scan .        # or: pipx run rrdoctor scan .  /  pip install rrdoctor
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

The score starts at 100 and subtracts deterministic penalties for errors and warnings. Treat it as a triage signal, not as proof that a repository is reproducible.

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
# ACM Artifact Appendix skeleton + ACM badge / NeurIPS checklist mapping:
rrdoctor appendix . --profile acm --output ARTIFACT_APPENDIX.md

# Verification ladder. Static by default; --run actually resolves deps and runs the entrypoint:
rrdoctor verify . --profile neurips
rrdoctor verify . --run --timeout 600        # only on repositories you trust
```

Submission profiles: `acm`, `neurips`, `icml`, `ml-paper`, `fair4rs`, `joss`. Dependency and
runtime checks also understand R (`DESCRIPTION`, `renv.lock`) and Julia (`Project.toml`).

## Use from a coding agent (MCP)

```bash
pip install 'rrdoctor[mcp]'
rrdoctor mcp        # exposes scan/verify/appendix as MCP tools over stdio
```

## Add the GitHub Action

```yaml
- uses: Tom409114/research-repo-doctor@v0.2.3
  with:
    profile: standard
    fail-on: warning
    output: rrdoctor-report.md
```

For PR comments, job summaries, and new-finding gating, see
[pull request automation](pull-request-automation.md).
