# 80-Repository Calibration Brief

This is a launch-ready summary of rrdoctor's current public calibration corpus.
It is meant for blog posts, community discussions, and Artifact Evaluation
conversations. It should not be read as a ranking of the scanned projects.

## Short Summary

We ran rrdoctor's static scan across 80 public research and scientific software
repositories and manually reviewed every corpus entry for focused false-positive
or false-negative risks. The latest maintainer gate scanned all 80 repositories,
reported 0 clone or scan errors, and had 0 expected-absent regressions in
first-run trust cases such as nanoGPT-style root entrypoints and notebook secret
noise.

The strongest pattern was not "bad code." It was missing release evidence:
data availability notes, reproducibility instructions, dependency/runtime
metadata, notebook hygiene, and test-runner discoverability were the most common
actionable gaps.

## Method

- Corpus size: 80 public repositories.
- Scan date: 2026-07-09 maintainer snapshot.
- Runner: `scripts/scan_corpus.py`.
- Scan mode: static only.
- Dynamic behavior: no dependency installation, imports, builds, notebooks, or
  target repository scripts were executed.
- Review evidence: 80 focused manual review notes under `evaluation/reviews/`.
- Regression gate: `--fail-on-expected-absent` for known first-run trust cases.

Reproduce the maintainer gate:

```bash
python scripts/scan_corpus.py --limit 80 --timeout 120 --max-mb 500 --progress --fail-on-expected-absent
```

## Snapshot Numbers

| Metric | Value |
| --- | ---: |
| Repositories listed | 80 |
| Scanned successfully | 80 |
| Clone or scan errors | 0 |
| Expected-absent regressions | 0 |
| Focused manual review notes | 80 |
| Repositories awaiting focused review | 0 |
| Average static score | 67.5 |

Readiness distribution:

| Readiness | Repositories | Share |
| --- | ---: | ---: |
| Available | 56 | 70.0% |
| Functional | 22 | 27.5% |
| Needs preparation | 2 | 2.5% |

## Most Common Actionable Gaps

| Rule | Meaning | Repositories | Share |
| --- | --- | ---: | ---: |
| RRD040 | Data availability documentation missing | 56 | 70.0% |
| RRD004 | README lacks reproducibility section | 50 | 62.5% |
| RRD034 | Imported package not in dependency manifest | 43 | 53.8% |
| RRD060 | Notebook files detected with large outputs | 39 | 48.8% |
| RRD071 | No test runner/configuration detected | 36 | 45.0% |
| RRD002 | README lacks installation/setup section | 32 | 40.0% |
| RRD091 | `.gitignore` missing common research artifacts | 30 | 37.5% |
| RRD110 | Python project metadata incomplete | 26 | 32.5% |
| RRD043 | Potential local absolute data path detected | 23 | 28.8% |
| RRD030 | No dependency manifest found | 22 | 27.5% |

## What This Means

The corpus suggests that deadline-time reproducibility work is often less about
rewriting algorithms and more about making the release inspectable:

- Can a reviewer find the setup and run path in the first minute?
- Is the data source, DOI, or retrieval step explicit?
- Are runtime dependencies declared where tooling can see them?
- Are notebook outputs clean enough to review without stale state?
- Is there a lightweight test or smoke command a maintainer can trust?

That is why rrdoctor is positioned as an Artifact Evaluation preparation tool
rather than a general code-quality score. The scan is useful when it turns those
release blockers into a small, deterministic checklist before submission.

## What Changed Because Of The Corpus

The corpus is not just marketing evidence. It has already driven rule changes:

- Root-level `train.py`, `main.py`, `run.py`, README commands, notebook-first
  demo artifacts, and model-release scripts are recognized as entrypoints.
- Mature library/framework repositories are not forced to look like paper
  artifact repositories.
- Notebook and repository secret checks now use conservative context, token
  boundaries, and entropy filtering to avoid noisy public-output findings.
- Placeholder paths, vendored dependency paths, CI/devcontainer paths, and URL
  path segments are filtered without suppressing concrete source-code paths.
- R, Julia, Bazel, Conda, editable pip, and grouped CI evidence are recognized
  where the repository already exposes it.

## Limits

- This is a static scan. It cannot prove scientific claims or reproduce paper
  results by itself.
- The corpus is a calibration set, not a representative sample of all research
  software.
- Counts are useful for prioritizing rule quality, not for naming and shaming
  individual maintainers.
- Dynamic `rrdoctor verify --run` is the right next step for repositories you
  trust when you need to know whether the documented quickstart actually runs.

## Copy-Ready Public Framing

We scanned 80 public research repositories with a deterministic, static
Artifact Evaluation preparation tool. The recurring blockers were mundane but
painful: 70% lacked clear data availability docs, 62.5% lacked a reproducibility
section, 53.8% imported packages not declared in dependency manifests, and
48.8% had large notebook outputs. The point is not to rank projects. The point
is that most release-readiness work is a checklist authors can fix before an AE
deadline, and a local-first tool can make that checklist objective.

See also:

- [Evaluation corpus](evaluation-corpus.md)
- [nanoGPT first-run case study](case-studies/nanogpt.md)
- [Artifact Evaluation deadline workflow](ae-deadline-workflow.md)
