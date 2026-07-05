# Report Formats

## Markdown

Markdown is the default human-readable format. It includes repository name, timestamp,
profile, Artifact Evaluation-style readiness level, heuristic score, category summary,
prioritized fixes, grouped findings, suggested GitHub issue titles, and a reproducibility
checklist. It also includes Artifact Evaluation next-step commands for
`rrdoctor plan`, `rrdoctor appendix`, and `rrdoctor verify`.

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
- `readiness`
- `score`
- `category_scores`
- `findings`
- `rules_evaluated`
- `summary`

## SARIF-compatible JSON

SARIF output is experimental. It is valid JSON shaped for future code-scanning integration, but it does not yet claim full SARIF coverage.

```bash
rrdoctor scan . --format sarif --output rrdoctor.sarif --fail-on none
```

## Agent fix plan

The `agent` format renders a tool-agnostic fix plan: an ordered, verifiable work
order that any coding agent or human can execute. The same output is available via
the `plan` command. The Markdown plan ends with baseline gating plus appendix and
verification commands for Artifact Evaluation packages.

```bash
rrdoctor scan . --format agent --output fix-plan.md
rrdoctor plan . --format json --output fix-plan.json
```

See [agent workflows](agent-workflows.md).

## Readiness badge

`rrdoctor badge` emits a Shields.io endpoint document or a self-contained SVG using
the AE-style readiness label (`Available`, `Functional`, or `Reproduced-ready`).

```bash
rrdoctor badge . --output .rrdoctor-badge.json
rrdoctor badge . --format svg --output rrdoctor-badge.svg
```

## Baseline comparison

Any JSON report can act as a baseline. `--baseline` reports new and resolved
findings, and `--fail-on-new` gates only on newly introduced ones.

```bash
rrdoctor scan . --format json --output baseline.json --fail-on none
rrdoctor scan . --baseline baseline.json --fail-on-new error
```
