# Pull request automation

The GitHub Action can post a reproducibility report on every pull request, write a
job summary, and gate merges on newly introduced findings only. This lets a lab
adopt the audit on a large existing repository without having to fix everything up
front.

## Sticky PR comment and job summary

```yaml
name: Reproducibility audit

on:
  pull_request:

permissions:
  contents: read
  pull-requests: write

jobs:
  rrdoctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: Tom409114/research-repo-doctor@v0.2.13
        with:
          profile: standard
          fail-on: none
          comment-pr: "true"
          step-summary: "true"
```

The action writes the Markdown report to the job summary and updates a single
sticky comment on the pull request (it edits the same comment on each run rather
than posting a new one). It uses the built-in `GITHUB_TOKEN`; no API key is
required.

## Gate on new findings only

Commit a baseline once, then fail only when a pull request introduces new
findings:

```bash
rrdoctor scan . --format json --output .rrdoctor-baseline.json --fail-on none
git add .rrdoctor-baseline.json && git commit -m "Add rrdoctor baseline"
```

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.13
        with:
          profile: standard
          baseline: .rrdoctor-baseline.json
          fail-on-new: error
          comment-pr: "true"
```

Refresh the baseline whenever you intentionally accept the current state.

## Emit the fix plan as an artifact

Set `plan: "true"` to also produce `rrdoctor-plan.md`, which the action uploads as
a build artifact and includes in the job summary. Contributors (or a coding agent)
can use it to resolve the findings. See [agent workflows](agent-workflows.md).

## Emit the Artifact Appendix

Set `appendix: "true"` before a submission deadline to produce
`ARTIFACT_APPENDIX.md` from the same scan:

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.13
        with:
          profile: acm
          fail-on: none
          appendix: "true"
```

The appendix is uploaded with the other action artifacts and included in the job
summary when `step-summary` is enabled.

## Emit the Verification Ladder

Set `verify: "true"` to include a static L1/L2/L3 verification report in the job
summary and uploaded artifacts:

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.13
        with:
          profile: acm
          fail-on: none
          verify: "true"
```

The default is static and report-only. Add `verify-run: "true"` only for
repositories you trust, because dynamic verification resolves dependencies and
executes the detected entrypoint. Add `verify-command` when you want the L3 gate
to use the artifact's official quickstart command. Add `verify-fail-on: error`
when you want that dynamic step to block the workflow:

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.13
        with:
          profile: acm
          fail-on: none
          verify: "true"
          verify-run: "true"
          verify-command: "python train.py config/default.py"
          verify-fail-on: error
          verify-timeout: "600"
```

## Readiness badge

Publish a live artifact-readiness badge by committing an endpoint file and pointing
Shields.io at it. The badge shows the AE-style readiness level; the full report
still includes the numeric score:

```bash
rrdoctor badge . --output .rrdoctor-badge.json
```

```markdown
![rrdoctor](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Tom409114/research-repo-doctor/main/.rrdoctor-badge.json)
```

For another repository, replace the GitHub owner, repository name, branch, and
endpoint-file path in the raw URL.
