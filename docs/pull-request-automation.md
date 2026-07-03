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
      - uses: actions/checkout@v4
      - uses: Tom409114/research-repo-doctor@v0.2.3
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
      - uses: Tom409114/research-repo-doctor@v0.2.3
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

## Score badge

Publish a live reproducibility badge by committing an endpoint file and pointing
Shields.io at it:

```bash
rrdoctor badge . --output .rrdoctor-badge.json
```

```markdown
![rrdoctor](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OWNER/REPO/main/.rrdoctor-badge.json)
```
