# GitHub Action

The action lets another repository run Research Repo Doctor in pull requests and
pushes. It can publish the reproducibility report, an agent-ready fix plan, an
Artifact Evaluation appendix, and a verification ladder report from the same run.

```yaml
name: Research Repo Doctor

on:
  pull_request:
  push:
    branches: [main]

jobs:
  rrdoctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: Tom409114/research-repo-doctor@v0.2.11
        with:
          profile: standard
          fail-on: warning
          output: rrdoctor-report.md
          plan: "true"
          appendix: "true"
          verify: "true"
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `path` | `.` | Repository path to scan. |
| `config` | empty | Optional config path. |
| `profile` | `standard` | `minimal`, `standard`, `strict`, `ml`, `ml-paper`, `neurips`, `icml`, `acm`, `fair4rs`, or `joss`. |
| `format` | `markdown` | `markdown`, `json`, `sarif`, or `agent`. |
| `output` | `rrdoctor-report.md` | Report output path. |
| `fail-on` | `error` | `none`, `error`, or `warning`. |
| `baseline` | empty | Baseline JSON report to compare against. |
| `fail-on-new` | empty | With `baseline`, fail only on new findings. |
| `plan` | `false` | Also generate an agent-ready `rrdoctor-plan.md`. |
| `appendix` | `false` | Also generate an Artifact Evaluation appendix/checklist. |
| `appendix-output` | `ARTIFACT_APPENDIX.md` | Artifact appendix output path. |
| `verify` | `false` | Also generate an L1/L2/L3 verification ladder report. |
| `verify-run` | `false` | Run dynamic verification steps. Executes target repository code; only use on trusted repositories. |
| `verify-output` | `rrdoctor-verify.md` | Verification report output path. |
| `verify-timeout` | `300` | Per-step timeout in seconds for dynamic verification. |
| `comment-pr` | `false` | Post or update a sticky PR comment with the report. |
| `step-summary` | `true` | Write the report to the job summary. |
| `upload-artifacts` | `true` | Upload the report (and plan) as artifacts. |
| `extra-args` | empty | Additional CLI args. |

The action does not require API keys and does not make network calls as part of
scanning. PR comments use the built-in `GITHUB_TOKEN`.

## Outputs

| Output | Description |
| --- | --- |
| `exit-code` | rrdoctor scan exit code before the final enforcement step. |
| `report-path` | Path to the generated report. |
| `plan-path` | Path to `rrdoctor-plan.md` when `plan` is `true`. |
| `appendix-path` | Path to the appendix file when `appendix` is `true`. |
| `verify-path` | Path to the verification report when `verify` is `true`. |

## Pull request comments and gating

To post a sticky comment and gate only on newly introduced findings, see
[pull request automation](pull-request-automation.md). The comment step needs:

```yaml
permissions:
  contents: read
  pull-requests: write
```

The action edits a single marker-tagged comment on each run rather than posting a
new one, so the PR thread stays clean.

## Artifact Appendix

Set `appendix: "true"` to generate `ARTIFACT_APPENDIX.md` with an ACM-style
artifact appendix and ACM/NeurIPS checklist mapping:

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.11
        with:
          profile: acm
          fail-on: none
          appendix: "true"
          appendix-output: ARTIFACT_APPENDIX.md
```

The appendix is uploaded as an artifact and included in the job summary when
`step-summary` is enabled. Treat it as a scaffold: fill in venue-specific
hardware, runtime, data access, and expected-results details before submission.

## Verification Ladder

Set `verify: "true"` to emit a static L1/L2/L3 verification report:

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.11
        with:
          profile: acm
          fail-on: none
          verify: "true"
```

By default this does not execute target repository code. For repositories you
trust, add `verify-run: "true"` to resolve dependencies and execute the detected
entrypoint under `verify-timeout`:

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.11
        with:
          profile: acm
          fail-on: none
          verify: "true"
          verify-run: "true"
          verify-timeout: "600"
```
