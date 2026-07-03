# Corpus Review Notes

This directory stores manual review notes for public corpus scans. The files do
not copy third-party source code or notebook contents. They only record rule IDs,
review outcomes, and short evidence summaries that help maintainers decide
whether a finding is a false positive, a false negative, or an expected absence.

Use one YAML file per corpus entry:

```yaml
version: 1
repository: nanoGPT
status: reviewed
reviewed_at: 2026-07-03
reviewer: Research Repo Doctor maintainers
confirmed_absent:
  - rule_id: RRD050
    evidence: Root-level train.py and README commands are recognized.
false_positives: []
false_negatives: []
notes: Keep notes short and aggregate-friendly.
```

When `scripts/scan_corpus.py` runs, it loads this directory by default and
includes review counts in `evaluation/reports/corpus-aggregate.json` and the
Markdown summary. Public posts should use aggregate patterns after manual review,
not rankings of individual maintainers.
