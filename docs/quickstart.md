# Quickstart

## Install

For the initial source release:

```bash
git clone https://github.com/Tom409114/research-repo-doctor.git
cd research-repo-doctor
python -m pip install -e ".[dev]"
```

After PyPI publishing:

```bash
python -m pip install rrdoctor
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

## Add the GitHub Action

```yaml
- uses: Tom409114/research-repo-doctor@v0.2.0
  with:
    profile: standard
    fail-on: warning
    output: rrdoctor-report.md
```

For PR comments, job summaries, and new-finding gating, see
[pull request automation](pull-request-automation.md).
