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
      - uses: Tom409114/research-repo-doctor@v0.1.0
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
| `format` | `markdown` | `markdown`, `json`, or `sarif`. |
| `output` | `rrdoctor-report.md` | Report output path. |
| `fail-on` | `error` | `none`, `error`, or `warning`. |
| `extra-args` | empty | Additional CLI args. |

The action does not require API keys and does not make network calls as part of scanning.
