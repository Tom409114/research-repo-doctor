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
python scripts/scan_corpus.py --limit 80 --timeout 120 --max-mb 500 --progress --fail-on-expected-absent
```

- Repositories listed: 80
- Scanned successfully: 80
- Clone or scan errors: 0
- Expected-absent regressions: 0
- Focused manual review notes: 51
- Not yet manually reviewed: 29
- Average score across scanned repositories: 67.5

Readiness distribution:

| Readiness | Repositories |
| --- | ---: |
| Available | 56 |
| Functional | 22 |
| Needs preparation | 2 |

Top actionable rule frequencies:

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

This snapshot is calibration evidence, not a benchmark or ranking of the scanned
projects. The scanner does not install dependencies, import target modules,
build target projects, or execute target repository code. It uses a GitHub
archive fallback only as a static transport mechanism when `git clone` is
unavailable or flaky.

Manual review flags captured in this snapshot:

| Type | Rule | Count |
| --- | --- | ---: |
| False positive | RRD090 | 4 |

Focused reviews currently cover BERT, CLIP, guided-diffusion,
improved-diffusion, vision-transformer, MAE, AlphaFold, DETR, YOLOv5,
DynamicalSystems.jl, Scanpy, scikit-learn, Astropy, scvi-tools, DINOv2, t5x,
GraphCast, SciPy, scikit-image, JAX, NetworkX, Keras, openai-baselines,
Transformers, PyTorch Lightning, Biopython, torchvision, xarray, MDAnalysis,
QuTiP, ESM, stable-diffusion, nerfstudio, and FAISS. The repository contains
51 reviewed notes and 29 repositories still awaiting focused manual review.
Those additions
confirm that BERT local RNG seeding via
`random.Random(FLAGS.random_seed)`, CLIP model parameter initialization via
`nn.Parameter(torch.randn(...))`, MAE-style root `main_*.py` entrypoints,
AlphaFold `random_seed=` plumbing, Julia `test/runtests.jl` test evidence,
Julia CI runners, regex-escaped warning filters, and comments/docstrings that
look like import statements no longer trigger noisy findings. The t5x review
also confirms that package-level research binaries such as `t5x/train.py` and
documented `python3 ${T5X_DIR}/t5x/train.py` commands count as experiment
entrypoints. The GraphCast review confirms that clearly named demo notebooks
such as `graphcast_demo.ipynb` count as notebook-first experiment entrypoints.
The SciPy review confirms that `LICENSE.txt`, CI/devcontainer environment paths,
and placeholder examples such as `/home/...` or Windows `<user>` cache paths do
not create high-noise license or local-path findings.
The torchvision, MDAnalysis, and QuTiP reviews confirm that URL path segments
containing `/home/`, common documentation examples such as `/home/joe/...` and
`/Users/Me/...`, nested `package/` dependency manifests, and reusable
library-shaped layouts no longer create high-noise `RRD043`, `RRD030`, or
`RRD050` findings. The FAISS review keeps a specific hardcoded benchmark
dataset path as actionable rather than suppressing it.
The guided-diffusion, vision-transformer, and openai-baselines reviews confirm
that README-documented script, module, and config-driven training commands are
recognized as experiment entrypoint evidence rather than noisy `RRD050`
findings.
The ESM and nerfstudio reviews confirm that notebook output tracebacks and
installation-doc placeholder paths are filtered without suppressing notebook
source-cell checks or concrete hardcoded source-code paths.
The stable-diffusion review confirms that Conda `environment.yaml` manifests,
editable pip `#egg=` entries, and documented seed plumbing through
`pytorch_lightning.seed_everything(...)` are recognized.
The scikit-image and JAX reviews confirm that public URL query `token=` values
and internal compiler/runtime variables named `token` no longer create
high-noise secret findings. The NetworkX and Keras reviews confirm that mature
library/framework repositories are not treated as missing paper experiment
entrypoints.
The dependency gap check also focuses on runtime-like Python files instead of
docs, tests, benchmarks, vendored code, or maintainer tooling.

The 80-repository manifest currently has 51 focused manual review notes and 29
repositories still awaiting focused review.

The v0.2.19 PyPI package was also spot-checked against nanoGPT, the original
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
