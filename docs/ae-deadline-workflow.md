# Artifact Evaluation Deadline Workflow

This workflow is for maintainers preparing a research artifact for ACM-style
Artifact Evaluation, NeurIPS/ICML reproducibility checks, or a lab handoff where
someone else must rerun the repository quickly.

rrdoctor does not prove the scientific claim. It checks whether another person
can understand, cite, install, and attempt to run the artifact without guessing.

## 1. Capture the Starting Point

Run a static scan before editing so later work has an objective baseline.

```bash
rrdoctor scan . --profile acm --format json --output rrdoctor-baseline.json --fail-on none
rrdoctor scan . --profile acm --output rrdoctor-report.md --fail-on none
```

Read the readiness label first:

- `Needs preparation`: basics are missing before a reviewer can use the artifact.
- `Available`: release metadata and access information are mostly present.
- `Functional`: the repository exposes a credible environment and run path.
- `Reproduced-ready`: static checks found no blocking release-readiness gaps.

Treat the numeric score as triage, not as proof of reproducibility.

## 2. Scaffold the Mechanical Fixes

Preview the safe fixes:

```bash
rrdoctor fix .
```

Apply them when the preview looks right:

```bash
rrdoctor fix . --write
```

Fixes are deterministic and idempotent. They create starter files such as
governance docs, citation metadata, data/results notes, seed helpers, changelog
entries, and research-oriented ignore rules. They never overwrite existing
files. Review any generated starter text before submission.

## 3. Turn the Remaining Work into a Plan

```bash
rrdoctor plan . --output rrdoctor-plan.md
```

Use the plan as a work order for a maintainer or coding agent. Each item points
back to the rule that will verify the change. A good loop is:

```bash
rrdoctor scan . --format json --output rrdoctor-baseline.json --fail-on none
rrdoctor plan . --output rrdoctor-plan.md
# Work through rrdoctor-plan.md.
rrdoctor scan . --baseline rrdoctor-baseline.json --fail-on-new error
```

The final command is a regression gate: it allows incremental adoption and fails
only when new error-level findings appear.

## 4. Generate the Artifact Appendix

```bash
rrdoctor appendix . --profile acm --output ARTIFACT_APPENDIX.md
```

The appendix output is a scaffold for the submission package. It maps findings
to ACM Artifact Evaluation badge tiers and the NeurIPS-style reproducibility
checklist. Fill in the human parts that rrdoctor cannot know, such as hardware
expectations, expected runtime, dataset access restrictions, and result
interpretation.

For another venue, switch profiles:

```bash
rrdoctor appendix . --profile neurips --output REPRODUCIBILITY_CHECKLIST.md
rrdoctor scan . --profile icml
rrdoctor scan . --profile joss
```

## 5. Verify the Run Path

Start with the static verification ladder:

```bash
rrdoctor verify . --profile acm --output rrdoctor-verify.md --fail-on none
```

This reports L1 static readiness and explains what would block L2 environment
setup or L3 entrypoint execution.

L3 prefers documented README run commands when they are conservative and
file-backed, then falls back to common research entrypoints such as
`scripts/reproduce.sh`, Make targets, root-level `train.py`/`main.py`/`run.py`,
matching scripts under `scripts/`, and executable notebooks via `papermill` when
available.

For repositories you trust, run the dynamic check under a timeout:

```bash
rrdoctor verify . --profile acm --run --timeout 600 --output rrdoctor-verify-run.md --fail-on none
```

Only use `--run` on trusted repositories. Static scans do not execute target
code. Dynamic verification resolves dependencies and runs the declared
entrypoint, so it should be treated like running the repository yourself.

## 6. Add the Pull Request Gate

For a repository preparing a public artifact, add the GitHub Action after the
first local pass:

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
      - uses: actions/checkout@v4
      - uses: Tom409114/research-repo-doctor@v0.2.6
        with:
          profile: acm
          fail-on: none
          comment-pr: "true"
          step-summary: "true"
          plan: "true"
```

Start with `fail-on: none` while fixing old findings. Raise the gate later, for
example to `fail-on: warning`, once the repository is ready for stricter review.

## Submission-Day Checklist

- The README contains a minimal setup command and a minimal run command.
- Dependencies, runtime versions, and required hardware are documented.
- Data access, preprocessing, and licensing are documented.
- Random seeds or randomness controls are documented and actually used.
- Notebooks are clean, ordered, and free of local-only outputs.
- Results directories explain how their artifacts were produced.
- License, citation metadata, changelog, and security contact are present.
- `rrdoctor appendix` has produced a filled artifact appendix.
- `rrdoctor verify` passes static checks.
- `rrdoctor verify --run` has been attempted on a trusted clean environment when feasible.
