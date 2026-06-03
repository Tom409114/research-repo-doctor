# Report Formats

## Markdown

Markdown is the default human-readable format. It includes repository path, timestamp, profile, score, category summary, prioritized fixes, grouped findings, suggested GitHub issue titles, and a reproducibility checklist.

```bash
rrdoctor scan . --format markdown --output rrdoctor-report.md
```

## JSON

JSON mirrors the `ScanReport` model and is suitable for automation.

```bash
rrdoctor scan . --format json --quiet
```

Top-level fields include:

- `repository_path`
- `generated_at`
- `profile`
- `score`
- `category_scores`
- `findings`
- `rules_evaluated`
- `summary`

## SARIF-compatible JSON

SARIF output is experimental. It is valid JSON shaped for future code-scanning integration, but v0.1.0 does not claim full SARIF coverage.

```bash
rrdoctor scan . --format sarif --output rrdoctor.sarif --fail-on none
```
