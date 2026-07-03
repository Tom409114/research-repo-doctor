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
- Command: `python scripts/scan_corpus.py --limit 10 --timeout 120 --max-mb 500 --fail-on-expected-absent`
- Corpus slice: first 10 public repositories in `evaluation/corpus.yml`
- Scanned successfully: 10 of 10
- Clone or scan errors: 0
- Average score across scanned repositories: 68.0
- Expected-absent regressions: 0
- Manually reviewed repositories: 4 focused reviews

Top actionable rule frequencies in that snapshot:

| Rule | Error/warning findings |
| --- | ---: |
| RRD004 | 6 |
| RRD060 | 6 |
| RRD071 | 6 |
| RRD003 | 5 |
| RRD034 | 5 |
| RRD080 | 5 |
| RRD002 | 4 |
| RRD030 | 4 |
| RRD040 | 4 |
| RRD070 | 4 |

This is not a benchmark and should not be read as a ranking of projects. The
snapshot is a maintainer calibration tool: high-frequency rules are candidates
for manual review, better evidence collection, or more conservative heuristics.

## Reproduce The Smoke Scan

Run a small smoke scan:

```bash
python scripts/scan_corpus.py --limit 1 --output evaluation/reports/corpus-scan.json
```

Run the current maintainer gate:

```bash
python scripts/scan_corpus.py --limit 10 --timeout 120 --max-mb 500 --fail-on-expected-absent
```

The generated reports are written under `evaluation/reports/`, which is ignored
by git. Before publishing aggregate results, manually review the findings for
false positives and false negatives. Do not rank or shame individual maintainers.
