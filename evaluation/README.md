# Evaluation Corpus

This directory stores the public-repository corpus used to check rrdoctor's rule
signal quality. It stores URLs and review notes only; no third-party repository
content is copied into this project.

The corpus exists to keep first-run trust honest. When a respected research repo
is flagged incorrectly, maintainers should fix the rule, add review evidence, or
document why the finding is intentionally conservative. The goal is to reduce
false positives and false negatives before using rrdoctor in Artifact Evaluation
or release-preparation workflows.

## Current Maintainer Snapshot

Latest local maintainer smoke run:

- Date: 2026-07-04
- Command: `python scripts/scan_corpus.py --limit 60 --timeout 120 --max-mb 500 --fail-on-expected-absent`
- Corpus slice: all 60 public repositories currently listed in `evaluation/corpus.yml`
- Scanned successfully: 60 of 60
- Clone or scan errors: 0
- Average score across scanned repositories: 57.9
- Expected-absent regressions: 0
- Manually reviewed repositories: 17 focused reviews

Top actionable rule frequencies in that snapshot:

| Rule | Error/warning findings |
| --- | ---: |
| RRD040 | 41 |
| RRD002 | 39 |
| RRD071 | 38 |
| RRD004 | 37 |
| RRD003 | 34 |
| RRD043 | 28 |
| RRD091 | 28 |
| RRD070 | 25 |
| RRD034 | 24 |
| RRD030 | 23 |

This is not a benchmark and should not be read as a ranking of projects. The
snapshot is a maintainer calibration tool: high-frequency rules are candidates
for manual review, better evidence collection, or more conservative heuristics.
The runner shallow-clones each repository and falls back to a GitHub archive
download when clone transport fails; both paths are static and never execute
target repository code.

Manual review flags captured in this snapshot:

| Type | Rule | Count |
| --- | --- | ---: |
| False positive | RRD090 | 4 |

## Reproduce The Smoke Scan

Run a small smoke scan:

```bash
python scripts/scan_corpus.py --limit 1 --output evaluation/reports/corpus-scan.json
```

Run the current maintainer gate:

```bash
python scripts/scan_corpus.py --limit 60 --timeout 120 --max-mb 500 --fail-on-expected-absent
```

The generated reports are written under `evaluation/reports/`, which is ignored
by git. The runner shallow-clones each repository and falls back to GitHub
archives when clone transport fails. Before publishing aggregate results,
manually review the findings for false positives and false negatives. Do not
rank or shame individual maintainers.
