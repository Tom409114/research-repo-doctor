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
- Command: `python scripts/scan_corpus.py --limit 80 --timeout 120 --max-mb 500 --progress --fail-on-expected-absent`
- Corpus slice: all 80 public repositories currently listed in `evaluation/corpus.yml`
- Scanned successfully: 80 of 80
- Clone or scan errors: 0
- Average score across scanned repositories: 67.5
- Expected-absent regressions: 0
- Focused manual review notes: 61
- Not yet manually reviewed: 19

Top actionable rule frequencies in that snapshot:

| Rule | Error/warning findings |
| --- | ---: |
| RRD040 | 56 |
| RRD004 | 50 |
| RRD034 | 43 |
| RRD060 | 39 |
| RRD071 | 36 |
| RRD002 | 32 |
| RRD091 | 30 |
| RRD110 | 26 |
| RRD043 | 23 |
| RRD030 | 22 |

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

- Focused manual review notes loaded: 61
- Repositories still awaiting focused manual review: 19
- Includes BERT, CLIP, guided-diffusion, improved-diffusion,
  vision-transformer, MAE, AlphaFold, DETR, YOLOv5, DynamicalSystems.jl,
  Scanpy, scikit-learn, Astropy, scvi-tools, DINO, DINOv2, t5x, GraphCast,
  SciPy, scikit-image, JAX, NetworkX, Keras, openai-baselines, Transformers,
  PyTorch Lightning, Biopython, torchvision, xarray, MDAnalysis, QuTiP, ESM,
  stable-diffusion, nerfstudio, FAISS, detectron2, StyleGAN2-ADA PyTorch, and
  instant-ngp, Big Vision, latent-diffusion, taming-transformers,
  generative-models, pytorch-image-models, and Brax reviews for
  README evidence, experiment-entrypoint recognition, path-noise handling,
  secret-heuristic noise, library-shaped package handling, Julia test/CI
  recognition, dependency signal quality, Conda `.yaml` manifest handling,
  editable pip dependency parsing, notebook-first artifacts, and
  randomness-seed signal quality.
- The 80-repository manifest now has focused review notes for all repositories
  added in the latest expansion except the remaining older unreviewed entries.
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
- Confirmed that README-documented script, module, and config-driven training
  commands in guided-diffusion, vision-transformer, and openai-baselines count
  as experiment entrypoint evidence.
- Confirmed that detectron2, DINO, StyleGAN2-ADA PyTorch, and instant-ngp do
  not produce noisy `RRD050` entrypoint findings, and that vendored dependency
  trees no longer produce noisy `RRD043` local-path findings.
- Confirmed that Big Vision, latent-diffusion, taming-transformers,
  generative-models, pytorch-image-models, and Brax do not produce noisy
  `RRD050` entrypoint findings, and that Lightning/PyTorch seed plumbing in the
  diffusion and PyTorch vision reviews does not produce noisy `RRD052`
  findings.
- Confirmed that SciPy's `LICENSE.txt`, CI/devcontainer environment paths, and
  placeholder examples such as `/home/...` and Windows `<user>` cache paths do
  not trigger noisy `RRD010` or `RRD043` findings.
- Confirmed that public asset URL query `token=` values and internal compiler
  variables named `token` do not trigger noisy `RRD090` findings, and that
  mature library/framework projects such as NetworkX and Keras are not treated
  as missing paper experiment entrypoints.
- Confirmed that URL path segments containing `/home/`, common documentation
  examples such as `/home/joe/...` and `/Users/Me/...`, nested `package/`
  dependency manifests, and reusable library-shaped layouts no longer create
  high-noise `RRD043`, `RRD030`, or `RRD050` findings. The FAISS review keeps a
  specific hardcoded benchmark dataset path as actionable rather than
  suppressing it.
- Confirmed that notebook output tracebacks with local source paths no longer
  create `RRD043` data-path findings; notebook source cells remain covered by
  `RRD062`, and large/stale notebook outputs remain covered by `RRD060` and
  `RRD061`.

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
python scripts/scan_corpus.py --limit 80 --timeout 120 --max-mb 500 --progress --fail-on-expected-absent
```

The generated reports are written under `evaluation/reports/`, which is ignored
by git. The runner shallow-clones each repository and falls back to GitHub
archives when clone transport fails. Before publishing aggregate results,
manually review the findings for false positives and false negatives. Do not
rank or shame individual maintainers.
