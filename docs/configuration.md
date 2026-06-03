# Configuration

Create a config file:

```bash
rrdoctor init --profile standard
```

Default structure:

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
    - ".mypy_cache"
    - ".pytest_cache"
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

## Profiles

- `minimal`: README, license, environment, data docs, experiment entrypoint.
- `standard`: minimal plus citation, notebooks, tests, CI, security, changelog.
- `strict`: standard plus container hints, governance, release workflow, paired notebooks.
- `ml`: standard plus ML-oriented configuration, seed, data, and provenance checks.

## Rule overrides

```yaml
rules:
  RRD042:
    severity: info
  RRD064:
    enabled: true
```

## Thresholds

- `large_file_mb`: large committed file warning threshold.
- `large_notebook_output_kb`: notebook output payload threshold.
