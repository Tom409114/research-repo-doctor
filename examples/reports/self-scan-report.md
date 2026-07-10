# Research Repo Doctor Report

- Repository: `research-repo-doctor`
- Generated: `2026-07-10T14:52:12.538276+00:00`
- Profile: `standard`
- Artifact readiness: **Reproduced-ready**
- Heuristic score: **100/100**
- Rules evaluated: `33`

> Readiness note: Static checks found no blocking findings. Run `rrdoctor verify --run` on a trusted machine for dynamic evidence.

> Heuristic note: Research Repo Doctor uses deterministic heuristics. The score is a guide, not a substitute for peer review or maintainer judgment.

## Summary by category

| Category | Score | Errors | Warnings | Info |
| --- | ---: | ---: | ---: | ---: |
| all | 100 | 0 | 0 | 0 |

## How to fix first

- No findings. Keep the repository documentation and automation current.

## Artifact Evaluation next steps

Use the static report to fix packaging gaps, then collect reviewer-facing
evidence with the appendix and verification ladder:

```bash
rrdoctor plan . --profile standard --output rrdoctor-plan.md
rrdoctor appendix . --profile standard --output ARTIFACT_APPENDIX.md
rrdoctor verify . --profile standard --fail-on none
```

For repositories you trust, add a dynamic run-path check under a timeout:

```bash
rrdoctor verify . --profile standard --run --timeout 600 --fail-on error
```

Do not run dynamic verification on untrusted code.

## Findings

No findings were detected.

## Suggested GitHub issues

- No issue suggestions from this scan.

## Reproducibility checklist

- [ ] README explains setup, usage, and result reproduction.
- [ ] Dependencies and runtime versions are documented.
- [ ] Data availability and provenance are documented.
- [ ] Experiment entrypoints and configuration are discoverable.
- [ ] Notebooks are clean, ordered, and free of secrets.
- [ ] Tests and CI provide a basic quality gate.
- [ ] Citation, license, changelog, and release metadata are present.
