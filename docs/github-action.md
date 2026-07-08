# GitHub Action

The action lets another repository run Research Repo Doctor in pull requests and
pushes. It can publish the reproducibility report, an agent-ready fix plan, an
Artifact Evaluation appendix, a verification ladder report, and a complete
Artifact Evaluation prep packet from the same run.

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
      - uses: Tom409114/research-repo-doctor@v0.2.17
        with:
          profile: standard
          fail-on: warning
          output: rrdoctor-report.md
          plan: "true"
          appendix: "true"
          prepare: "true"
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
| `prepare` | `false` | Also generate a full Artifact Evaluation prep packet directory. |
| `prepare-output` | `rrdoctor-prep` | Artifact Evaluation prep packet output directory. |
| `verify` | `false` | Also generate an L1/L2/L3 verification ladder report. |
| `verify-run` | `false` | Run dynamic verification steps. Executes target repository code; only use on trusted repositories. |
| `verify-fail-on` | `none` | `none`, `error`, or `warning`; set to `error` to make failed dynamic verification block the workflow. |
| `verify-output` | `rrdoctor-verify.md` | Verification report output path. |
| `verify-timeout` | `300` | Per-step timeout in seconds for dynamic verification. |
| `verify-command` | empty | Optional L3 quickstart command for `verify` and `prepare`. |
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
| `verify-exit-code` | rrdoctor verify exit code before the final enforcement step. |
| `prepare-exit-code` | rrdoctor prepare exit code before the final enforcement step. |
| `report-path` | Path to the generated report. |
| `plan-path` | Path to `rrdoctor-plan.md` when `plan` is `true`. |
| `appendix-path` | Path to the appendix file when `appendix` is `true`. |
| `prepare-path` | Path to the prep packet directory when `prepare` is `true`. |
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
      - uses: Tom409114/research-repo-doctor@v0.2.17
        with:
          profile: acm
          fail-on: none
          appendix: "true"
          appendix-output: ARTIFACT_APPENDIX.md
```

The appendix is uploaded as an artifact and included in the job summary when
`step-summary` is enabled. It is pre-filled from local README text, project
metadata, dependency manifests, data/results docs, config files, and detected
entrypoint commands when those exist. Treat it as a scaffold: fill in
venue-specific hardware, runtime, data access, and expected-results details
before submission.

## Artifact Evaluation Prep Packet

Set `prepare: "true"` to generate the same local packet as
`rrdoctor prepare`: `README.md`, `rrdoctor-report.md`, `rrdoctor-plan.md`,
`ARTIFACT_APPENDIX.md`, and `rrdoctor-verify.md` in one uploaded directory.

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.17
        with:
          profile: acm
          fail-on: none
          prepare: "true"
          prepare-output: rrdoctor-prep
```

For trusted repositories, `prepare` also honors `verify-run`, `verify-command`,
`verify-timeout`, and `verify-fail-on`, so the packet can include the dynamic
run-path evidence reviewers should inspect. Without `verify-run`, the packet is
static and does not execute target repository code.

## Verification Ladder

Set `verify: "true"` to emit a static L1/L2/L3 verification report:

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.17
        with:
          profile: acm
          fail-on: none
          verify: "true"
```

By default this does not execute target repository code and does not fail the
workflow. For repositories you trust, add `verify-run: "true"` to resolve
dependencies and execute the detected entrypoint under `verify-timeout`.
Set `verify-command` when the artifact has a specific quickstart command that
should be used as the L3 gate. The generated report includes the gate outcome,
failure threshold, timeout, L3 command source, trust boundary, per-step details,
and a copyable rerun command.

To make dynamic verification a real release gate, also set
`verify-fail-on: error`:

```yaml
      - uses: Tom409114/research-repo-doctor@v0.2.17
        with:
          profile: acm
          fail-on: none
          verify: "true"
          verify-run: "true"
          verify-command: "python train.py config/default.py"
          verify-fail-on: error
          verify-timeout: "600"
```

The action still writes the verification report to the job summary and uploads it
before enforcing the final verification exit code.
