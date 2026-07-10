# nanoGPT First-Run Case Study

This case study records a focused regression check against
[karpathy/nanoGPT](https://github.com/karpathy/nanoGPT). It is not a ranking of
nanoGPT. The goal is narrower: make sure rrdoctor no longer reports the two
high-noise findings that originally damaged first-run trust on a well-known ML
research repository.

## Scan Context

- Target repository: `https://github.com/karpathy/nanoGPT`
- Target commit scanned: `3adf61e154c3fe3fca428ad6bc3818b27a3b8291`
- rrdoctor package: PyPI `rrdoctor==0.2.23`
- Scan date: 2026-07-10
- Mode: static scan only; no dependency installation and no target code
  execution

Reproduction command:

```bash
git clone --depth 1 https://github.com/karpathy/nanoGPT.git
uvx --refresh --from rrdoctor==0.2.23 rrdoctor scan nanoGPT \
  --profile standard \
  --format json \
  --output nanogpt-rrdoctor.json \
  --fail-on none
```

## Observed Result

| Metric | Result |
| --- | --- |
| Readiness | `Functional` |
| Score | 76/100 |
| Errors | 0 |
| Warnings | 6 |
| Info | 2 |

Observed rule IDs:

| Rule | Severity | Interpretation |
| --- | --- | --- |
| RRD020 | warning | Citation instructions are not explicit enough for rrdoctor. |
| RRD030 | warning | README install instructions exist, but no supported dependency manifest was detected. |
| RRD041 | warning | `data/` exists without a `data/README.md`. |
| RRD070 | warning | No test directory or test files were detected. |
| RRD071 | warning | No obvious test runner configuration was detected. |
| RRD080 | warning | No CI configuration was detected. |
| RRD100 | info | No changelog file was found. |
| RRD101 | info | No version metadata was detected. |

## Regression Points

Two original first-run trust failures are absent in the v0.2.23 scan:

| Rule | Current result | Why it matters |
| --- | --- | --- |
| RRD050 | absent | nanoGPT's root-level `train.py` and README training commands count as experiment entrypoint evidence. |
| RRD063 | absent | Public notebook output is not treated as a credential leak unless it contains a high-confidence secret-like value. |

This is the desired behavior. The remaining findings are release-hardening
tasks, not blockers for recognizing nanoGPT's main run path.

## Maintainer Guard

The corpus manifest keeps nanoGPT as a regression seed:

- [`evaluation/corpus.yml`](../../evaluation/corpus.yml) lists `RRD050` and
  `RRD063` under `expected_absent`.
- [`evaluation/reviews/nanogpt.yml`](../../evaluation/reviews/nanogpt.yml)
  records the focused review status and last verified scan result.

Run the focused gate before changing entrypoint or notebook-secret rules:

```bash
python scripts/scan_corpus.py --only nanoGPT --fail-on-scan-error --fail-on-expected-absent
```
