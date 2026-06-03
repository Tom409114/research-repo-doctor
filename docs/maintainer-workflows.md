# Maintainer Workflows

## Issue triage

Maintainers classify incoming reports as bugs, false positives, false negatives, rule requests, research repository scan cases, or docs improvements. Each issue should be labeled with the affected rule ID when known, the repository ecosystem, and whether it needs a fixture.

Initial triage target:

- Confirm the report is reproducible from public or sanitized inputs.
- Ask for a minimal fixture when repository content cannot be shared.
- Decide whether the fix is rule logic, docs, config guidance, or a new rule.
- Link related issues so repeated patterns become roadmap items.

## False positive handling

False positives should include the rule ID, a minimal repository shape, expected behavior, and why the current finding is misleading. A fix should add or update a fixture before changing rule logic. Maintainers should prefer narrowing evidence over disabling useful checks globally.

## False negative handling

False negatives should include the missed reproducibility risk, expected finding, relevant files, and a sanitized example. If the risk is common and deterministic, it can become a rule request. If it is too context-specific, docs or config guidance may be a better response.

## Rule requests

A rule request should describe the reproducibility risk, the deterministic evidence, expected remediation, and likely false-positive cases. Accepted rule requests become fixture-driven pull requests.

## Pull requests

Rule PRs are reviewed for deterministic behavior, evidence quality, secret masking, tests, docs, profile fit, and config compatibility. Maintainers should verify that reports remain actionable and do not expose secrets.

## Releases

Before a release, maintainers run tests, linting, self-scan, changelog review, and action smoke tests. Release notes are based on `CHANGELOG.md`, and public release artifacts should link to the self-scan report when useful.

Release checklist:

- `pytest`
- `ruff check .`
- `ruff format --check .`
- `rrdoctor scan . --profile standard --format markdown --output examples/reports/self-scan-report.md --fail-on none`
- GitHub Action smoke test
- Changelog entry and tag notes
- Security policy and issue templates still current

## Responsible Codex/API credit use

Codex or API credits may help maintainers analyze false-positive reports, draft minimal test fixtures, review rule PRs, summarize failing cases, draft release notes, and improve docs. The core CLI remains local-first and does not require OpenAI. Maintainers must not paste real secrets, private datasets, or confidential repository content into AI tools. AI suggestions require human review and deterministic tests before merge.
