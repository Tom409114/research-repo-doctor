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
- Scanned successfully: 51 of 60
- Clone or scan errors: 9
- Average score across scanned repositories: 56.9
- Expected-absent regressions: 0
- Manually reviewed repositories: 4 focused reviews

Top actionable rule frequencies in that snapshot:

| Rule | Error/warning findings |
| --- | ---: |
| RRD071 | 38 |
| RRD040 | 34 |
| RRD002 | 33 |
| RRD004 | 30 |
| RRD003 | 25 |
| RRD070 | 25 |
| RRD091 | 25 |
| RRD030 | 23 |
| RRD081 | 22 |
| RRD043 | 21 |

This is not a benchmark and should not be read as a ranking of projects. The
snapshot is a maintainer calibration tool: high-frequency rules are candidates
for manual review, better evidence collection, or more conservative heuristics.
The clone/scan errors in this snapshot came from local checkout constraints
such as Windows path length limits or transient GitHub connectivity, not from
executing target repositories.

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
by git. Before publishing aggregate results, manually review the findings for
false positives and false negatives. Do not rank or shame individual maintainers.
