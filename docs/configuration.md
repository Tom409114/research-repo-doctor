# Configuration

Commands that accept a repository path automatically load
`<repository>/.rrdoctor.yml`, even when rrdoctor is launched from another
working directory. Pass `--config path/to/config.yml` to use a different file;
an explicit path always takes precedence over repository discovery.

Configuration precedence is deterministic:

1. Explicit CLI options such as `--profile`, `--format`, `--output`, and
   `--fail-on`.
2. Values in the selected `.rrdoctor.yml`.
3. Built-in defaults.

With no configuration file, `rrdoctor scan` keeps its normal behavior: the
`standard` profile, Markdown on stdout, and the `error` failure threshold. A
configured relative `report.output` is resolved from the repository root.

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

The configured profile is used by `scan`, `fix`, `plan`, `badge`, `verify`, and
MCP scans when no profile is passed explicitly. `prepare` and `appendix` retain
their purpose-specific `acm` default unless `--profile` is supplied.

## Paths

- `include`: files or directories to scan, relative to the repository root;
  `.` includes the complete repository.
- `exclude`: files, directories, or glob patterns to omit after includes are
  applied.

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

## Scan defaults

- `fail_on`: default scan exit threshold (`none`, `error`, or `warning`).
- `report.format`: default scan format (`markdown`, `json`, `sarif`, or
  `agent`).
- `report.output`: optional report path. Relative paths are written under the
  repository root. Remove this key to print the report to stdout by default.
  rrdoctor excludes its own output file from the current scan so repeated runs
  cannot turn report contents into findings.
