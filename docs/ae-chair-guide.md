# Guide for Artifact Evaluation Chairs

This page is for Artifact Evaluation chairs, program committee members, lab
maintainers, and course staff who want to recommend rrdoctor as an optional
pre-submission check for research artifacts.

rrdoctor is not a reviewer and does not decide whether a scientific claim is
correct. It is a deterministic, local-first checklist runner that helps authors
find practical packaging blockers before a human reviewer spends time on the
artifact.

## Where It Fits

Use rrdoctor as a preflight check before the artifact deadline:

```bash
uvx rrdoctor scan . --profile acm
uvx rrdoctor appendix . --profile acm --output ARTIFACT_APPENDIX.md
uvx rrdoctor verify . --profile acm --fail-on none
```

For trusted artifacts, authors can also attempt a dynamic run-path check:

```bash
uvx rrdoctor verify . --profile acm --run --timeout 600 --fail-on error
```

The default scan is static. It does not install dependencies, import target
code, build the project, execute scripts, or send repository contents to a
hosted service.

## Suggested Call-for-Artifacts Wording

You may adapt this wording:

```text
Optional artifact preflight: authors may run Research Repo Doctor before
submission to catch common packaging issues such as missing dependency metadata,
unclear run paths, local-only data references, stale notebook outputs, missing
citation metadata, and unapplied random seeds.

Run:
uvx rrdoctor scan . --profile acm
uvx rrdoctor appendix . --profile acm --output ARTIFACT_APPENDIX.md

This tool is optional and advisory. Passing it is not required for acceptance,
and failing it does not imply that the artifact is invalid. Its purpose is to
help authors make the artifact easier for reviewers to install, inspect, cite,
and attempt to run.
```

## Suggested Repository Gate

Authors who want a pull request gate can start permissively:

```yaml
name: Reproducibility audit

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  pull-requests: write

jobs:
  rrdoctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: Tom409114/research-repo-doctor@v0.2.24
        with:
          profile: acm
          fail-on: none
          comment-pr: "true"
          step-summary: "true"
          appendix: "true"
          prepare: "true"
          verify: "true"
```

Use `fail-on: none` while preparing an artifact. Raise the gate later only if
the project wants a stricter release policy.
`prepare: "true"` uploads a single packet containing the report, repair plan,
Artifact Appendix, and verification ladder for the authors or reviewers to
download.

## What rrdoctor Checks

The ACM-style profile focuses on reviewability:

- README setup and run instructions
- dependency and runtime metadata
- experiment entrypoints and documented commands
- data availability and local-only paths
- notebook output hygiene
- seed and randomness plumbing
- citation, license, changelog, and release metadata
- tests and CI signals
- artifact appendix scaffolding

Reports lead with an Artifact Evaluation-style readiness level:

- `Needs preparation`
- `Available`
- `Functional`
- `Reproduced-ready`

The numeric score is only triage. It is not a scientific reproducibility
judgment.

## Safety and Limits

- Static scans are safe for untrusted repositories.
- `verify --run` may install dependencies, execute project build hooks, and run
  repository code. It should be used only for artifacts the author or reviewer
  already trusts. Supported Python repositories use a temporary isolated venv.
- Chairs can ask authors to run `rrdoctor verify --command "..." --run` with the
  artifact's official quickstart command, making the dynamic gate explicit.
- Generated fixes are starter scaffolds and require human review.
- rrdoctor cannot verify dataset licensing, hardware availability, private
  credentials, expected runtime, or whether the paper's claims are correct.
- rrdoctor output should support human review, not replace it.

## Feedback From Chairs and Reviewers

False positives and false negatives are useful calibration data. Please report
them with the matching issue template:

- [False positive](https://github.com/Tom409114/research-repo-doctor/issues/new?template=false_positive.yml)
- [False negative](https://github.com/Tom409114/research-repo-doctor/issues/new?template=false_negative.yml)
- [Research repository scan case](https://github.com/Tom409114/research-repo-doctor/issues/new?template=scan_case.yml)

Include the rule ID, rrdoctor version, command, and a sanitized minimal
repository shape. See [feedback and calibration](feedback.md).
