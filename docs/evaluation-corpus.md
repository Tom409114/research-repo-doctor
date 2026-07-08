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

This shallow-clones the first corpus repository into a temporary directory, falls
back to a GitHub archive download if clone transport fails, runs the static
rrdoctor scanner, and writes:

- `evaluation/reports/corpus-scan.json`
- `evaluation/reports/corpus-aggregate.json`
- `evaluation/reports/corpus-summary.md`

The scan JSON stays one object per repository. The aggregate JSON and Markdown
summary include data-post-ready counts for readiness levels, ecosystems,
severity totals, top actionable rule IDs, and expected-absent violations. The
aggregate JSON keeps all rule frequencies under `rules` and error/warning-only
frequencies under `actionable_rules`; the Markdown summary uses the actionable
view so informational maintenance hints do not dominate public data posts.
Manual review notes from `evaluation/reviews/` are loaded automatically and add
reviewed-repository, false-positive, and false-negative counts to the aggregate.

The runner never installs target dependencies, imports target modules, builds
the target project, or executes target repository scripts.

For longer local runs, add `--progress` to print one line per repository to
stderr while preserving the JSON and Markdown report formats.

To create YAML starters for manual review, add a stub directory:

```bash
python scripts/scan_corpus.py --limit 10 --progress --review-stub-dir evaluation/reviews/todo
```

Review stubs are marked `needs-review`, so they do not count as manually
reviewed repositories until a maintainer edits them and changes `status` to
`reviewed`.

To turn manually reviewed first-run trust cases into a regression gate, run:

```bash
python scripts/scan_corpus.py --only nanoGPT --fail-on-expected-absent
```

Each corpus entry can list rule IDs under `expected_absent`. The gate exits
nonzero if one of those rules appears again. Use this for cases such as
root-level `train.py` detection and notebook secret false-positive regressions,
where a single noisy finding can undermine confidence in a first scan.

## Current Maintainer Snapshot

Latest local maintainer smoke run, generated on 2026-07-09:

```bash
python scripts/scan_corpus.py --limit 60 --timeout 120 --max-mb 500 --progress --fail-on-expected-absent
```

- Repositories listed: 60
- Scanned successfully: 60
- Clone or scan errors: 0
- Expected-absent regressions: 0
- Focused manual review notes: 30
- Not yet manually reviewed: 30
- Average score across scanned repositories: 62.1

Readiness distribution:

| Readiness | Repositories |
| --- | ---: |
| Available | 39 |
| Functional | 11 |
| Needs preparation | 10 |

Top actionable rule frequencies:

| Rule | Error/warning findings |
| --- | ---: |
| RRD040 | 41 |
| RRD004 | 37 |
| RRD071 | 32 |
| RRD002 | 30 |
| RRD091 | 26 |
| RRD043 | 25 |
| RRD034 | 24 |
| RRD030 | 23 |
| RRD070 | 19 |
| RRD060 | 18 |

This snapshot is calibration evidence, not a benchmark or ranking of the scanned
projects. The scanner does not install dependencies, import target modules,
build target projects, or execute target repository code. It uses a GitHub
archive fallback only as a static transport mechanism when `git clone` is
unavailable or flaky.

Manual review flags captured in this snapshot:

| Type | Rule | Count |
| --- | --- | ---: |
| False positive | RRD090 | 4 |

Focused reviews currently cover BERT, CLIP, improved-diffusion, MAE,
AlphaFold, DETR, YOLOv5, DynamicalSystems.jl, Scanpy, scikit-learn, Astropy,
scvi-tools, and DINOv2. The repository contains 30 reviewed notes and 30
repositories still awaiting focused manual review. Those additions confirm that
BERT local RNG seeding via
`random.Random(FLAGS.random_seed)`, CLIP model parameter initialization via
`nn.Parameter(torch.randn(...))`, MAE-style root `main_*.py` entrypoints,
AlphaFold `random_seed=` plumbing, Julia `test/runtests.jl` test evidence,
Julia CI runners, regex-escaped warning filters, and comments/docstrings that
look like import statements no longer trigger noisy findings. The dependency
gap check also focuses on runtime-like Python files instead of docs, tests,
benchmarks, vendored code, or maintainer tooling.

The v0.2.18 PyPI package was also spot-checked against nanoGPT, the original
first-run trust regression case. The static scan reported `Functional`, 76/100,
0 errors, 6 warnings, and 2 info findings; `RRD050` and `RRD063` were absent.
See the [nanoGPT first-run case study](case-studies/nanogpt.md) for the exact
command, target commit, and interpretation.

## Manual Review

Every corpus scan needs human review before its results are used in a public
post or release decision.

For each repository:

- Check whether high-severity findings are actionable for that repository shape.
- Mark false positives with the rule ID and the evidence that was misleading.
- Mark false negatives with the missing reproducibility risk and the file or
  README section that should have been recognized.
- Add or update a small fixture before changing rule logic.
- Start from generated stubs when available, but remove irrelevant
  `candidate_findings` before committing a final review note.
- Keep aggregate posts about ecosystem patterns; do not shame individual
  maintainers.

Use `corpus-aggregate.json` for public charts only after this manual review. The
raw counts are triage evidence, not final claims about individual projects.
Record those reviews in `evaluation/reviews/` so corpus studies can distinguish
raw scanner output from maintainer-confirmed false positives and false negatives.

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
