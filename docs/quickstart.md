# Quickstart

## Install

For the initial source release:

```bash
git clone https://github.com/research-repo-doctor/research-repo-doctor.git
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

## Add the GitHub Action

```yaml
- uses: research-repo-doctor/research-repo-doctor@v0.1.0
  with:
    profile: standard
    fail-on: warning
    output: rrdoctor-report.md
```
