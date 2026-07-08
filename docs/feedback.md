# Feedback and Calibration

rrdoctor is most useful when its rules are calibrated against real research
repositories. False positives and false negatives are welcome, especially from
artifact evaluation, ML, data science, and computational science repositories.

## Quick Feedback Loop

Run a static scan without executing target code:

```bash
uvx rrdoctor scan . --format json --output rrdoctor-report.json --fail-on none
uvx rrdoctor scan . --output rrdoctor-report.md --fail-on none
```

Then open the issue template that matches what you saw:

- [False positive](https://github.com/Tom409114/research-repo-doctor/issues/new?template=false_positive.yml):
  a rule flagged acceptable repository content.
- [False negative](https://github.com/Tom409114/research-repo-doctor/issues/new?template=false_negative.yml):
  rrdoctor missed a reproducibility risk.
- [Research repository scan case](https://github.com/Tom409114/research-repo-doctor/issues/new?template=scan_case.yml):
  a public repo gives a useful calibration case.
- [New rule request](https://github.com/Tom409114/research-repo-doctor/issues/new?template=rule_request.yml):
  a deterministic check would catch a repeated review blocker.

## What To Include

Please include:

- The rrdoctor version: `rrdoctor --version` or `uvx rrdoctor --version`.
- The command you ran.
- The rule ID, such as `RRD050` or `RRD063`.
- A minimal repository tree, public repository URL, or sanitized fixture.
- Why the finding is wrong, missing, too severe, or too vague.
- Any reviewer-facing context that a static scanner cannot know.

Do not paste real secrets, private data, unpublished paper text, confidential
paths, private dataset locations, or credentials. If a finding involves a
secret-like value, replace the value with a fake value that preserves the shape
of the example.

For suspected credential exposure, secret masking bypasses, unsafe dynamic
verification behavior, or report-generation leaks, do not open a public issue.
Use the private process in [SECURITY.md](../SECURITY.md).

## What Makes A Good Rule Change

A strong calibration report usually answers three questions:

1. What evidence should a deterministic local scanner use?
2. What common false-positive case should it avoid?
3. What remediation would help a tired researcher fix the repository before a
   deadline?

For rule implementation details, see [rule authoring](rule-authoring.md).
