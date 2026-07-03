# Evaluation Corpus

rrdoctor's rule quality should be judged against real research repositories, not
only hand-made fixtures. The evaluation corpus is a maintainer workflow for that
work.

The seed manifest lives at [`evaluation/corpus.yml`](../evaluation/corpus.yml).
It stores public repository URLs, ecosystems, review focus areas, and any
expected-absent regression checks. It does not copy third-party code into this
repository.

## Run a Smoke Scan

```bash
python scripts/scan_corpus.py --limit 1
```

This shallow-clones the first corpus repository into a temporary directory, runs
the static rrdoctor scanner, and writes:

- `evaluation/reports/corpus-scan.json`
- `evaluation/reports/corpus-aggregate.json`
- `evaluation/reports/corpus-summary.md`

The scan JSON stays one object per repository. The aggregate JSON and Markdown
summary include data-post-ready counts for readiness levels, ecosystems,
severity totals, top rule IDs, and expected-absent violations.

The runner never installs target dependencies, imports target modules, builds
the target project, or executes target repository scripts.

## Manual Review

Every corpus scan needs human review before its results are used in a public
post or release decision.

For each repository:

- Check whether high-severity findings are actionable for that repository shape.
- Mark false positives with the rule ID and the evidence that was misleading.
- Mark false negatives with the missing reproducibility risk and the file or
  README section that should have been recognized.
- Add or update a small fixture before changing rule logic.
- Keep aggregate posts about ecosystem patterns; do not shame individual
  maintainers.

Use `corpus-aggregate.json` for public charts only after this manual review. The
raw counts are triage evidence, not final claims about individual projects.

## Expansion Target

The seed corpus now starts at 50+ recent or high-impact repositories across:

- ML paper code releases.
- Computational biology workflows.
- R and Julia research software.
- Snakemake and Nextflow pipelines.
- Notebook-heavy analysis repositories.

The goal is not to prove rrdoctor is perfect. The goal is to make false
positives and false negatives visible enough that rule changes become
evidence-driven. Keep expanding toward 100 repositories before publishing an
aggregate data post, and record manual review notes separately from the manifest
so the public corpus remains a compact list of URLs and review focus areas.
