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

- Date: 2026-07-09
- Command: `python scripts/scan_corpus.py --limit 60 --timeout 120 --max-mb 500 --progress --fail-on-expected-absent`
- Corpus slice: all 60 public repositories currently listed in `evaluation/corpus.yml`
- Scanned successfully: 60 of 60
- Clone or scan errors: 0
- Average score across scanned repositories: 65.1
- Expected-absent regressions: 0
- Focused manual review notes: 33
- Not yet manually reviewed: 27

Top actionable rule frequencies in that snapshot:

| Rule | Error/warning findings |
| --- | ---: |
| RRD040 | 41 |
| RRD004 | 37 |
| RRD071 | 32 |
| RRD002 | 30 |
| RRD091 | 26 |
| RRD034 | 24 |
| RRD043 | 24 |
| RRD030 | 23 |
| RRD070 | 19 |
| RRD060 | 18 |

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

Focused review coverage in the current snapshot:

- Focused manual review notes loaded: 33
- Repositories still awaiting focused manual review: 27
- Includes BERT, CLIP, improved-diffusion, MAE, AlphaFold, DETR, YOLOv5,
  DynamicalSystems.jl, Scanpy, scikit-learn, Astropy, scvi-tools, DINOv2,
  t5x, GraphCast, and SciPy reviews for README evidence, experiment-entrypoint
  recognition, path-noise handling, Julia test/CI recognition, dependency
  signal quality, notebook-first artifacts, and randomness-seed signal quality.
- Confirmed that BERT's local `random.Random(seed)` usage, CLIP model parameter
  initialization, MAE-style root `main_*.py` scripts, and AlphaFold
  `random_seed=` plumbing are not reported as noisy findings.
- Confirmed that Julia `test/runtests.jl` and `Project.toml` test targets are
  recognized as test evidence, `julia-actions/julia-runtest` is recognized as a
  CI test runner, and regex-escaped warning filters do not look like Windows
  absolute paths.
- Confirmed that package-level research binaries such as `t5x/train.py`,
  documented `python3 ${T5X_DIR}/t5x/train.py` commands, and clearly named
  demo notebooks such as `graphcast_demo.ipynb` count as experiment entrypoint
  evidence.
- Confirmed that SciPy's `LICENSE.txt`, CI/devcontainer environment paths, and
  placeholder examples such as `/home/...` and Windows `<user>` cache paths do
  not trigger noisy `RRD010` or `RRD043` findings.

First-run trust spot check refreshed on 2026-07-09:

- Command: `uvx --refresh --from rrdoctor==0.2.19 rrdoctor scan <nanoGPT> --profile standard --format json --fail-on none`
- Result: `Functional`, 76/100, 0 errors, 6 warnings, 2 info
- Regression checks: `RRD050` and `RRD063` were absent

## Reproduce The Smoke Scan

Run a small smoke scan:

```bash
python scripts/scan_corpus.py --limit 1 --output evaluation/reports/corpus-scan.json
```

Run the current maintainer gate:

```bash
python scripts/scan_corpus.py --limit 60 --timeout 120 --max-mb 500 --progress --fail-on-expected-absent
```

The generated reports are written under `evaluation/reports/`, which is ignored
by git. The runner shallow-clones each repository and falls back to GitHub
archives when clone transport fails. Before publishing aggregate results,
manually review the findings for false positives and false negatives. Do not
rank or shame individual maintainers.
