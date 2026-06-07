# GitHub Action

The action lets another repository run Research Repo Doctor in pull requests and pushes.

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
      - uses: Tom409114/research-repo-doctor@v0.2.0
        with:
          profile: standard
          fail-on: warning
          output: rrdoctor-report.md
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `path` | `.` | Repository path to scan. |
| `config` | empty | Optional config path. |
| `profile` | `standard` | `minimal`, `standard`, `strict`, or `ml`. |
| `format` | `markdown` | `markdown`, `json`, `sarif`, or `agent`. |
| `output` | `rrdoctor-report.md` | Report output path. |
| `fail-on` | `error` | `none`, `error`, or `warning`. |
| `baseline` | empty | Baseline JSON report to compare against. |
| `fail-on-new` | empty | With `baseline`, fail only on new findings. |
| `plan` | `false` | Also generate an agent-ready `rrdoctor-plan.md`. |
| `comment-pr` | `false` | Post or update a sticky PR comment with the report. |
| `step-summary` | `true` | Write the report to the job summary. |
| `upload-artifacts` | `true` | Upload the report (and plan) as artifacts. |
| `extra-args` | empty | Additional CLI args. |

The action does not require API keys and does not make network calls as part of
scanning. PR comments use the built-in `GITHUB_TOKEN`.

## Pull request comments and gating

To post a sticky comment and gate only on newly introduced findings, see
[pull request automation](pull-request-automation.md). The comment step needs:

```yaml
permissions:
  contents: read
  pull-requests: write
```

The action edits a single marker-tagged comment on each run rather than posting a
new one, so the PR thread stays clean.
