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

## Corpus review

Rule quality should be checked against public research repositories as well as
small fixtures. Use the evaluation corpus workflow before changing broad
heuristics such as entrypoint, data, notebook, or secret detection:

```bash
python scripts/scan_corpus.py --limit 3 --progress
```

Review `evaluation/reports/corpus-summary.md` manually. Treat expected-absent
violations as regression candidates, then add a fixture before changing rule
logic. See [evaluation corpus](evaluation-corpus.md).

## Pull requests

Rule PRs are reviewed for deterministic behavior, evidence quality, secret masking, tests, docs, profile fit, and config compatibility. Maintainers should verify that reports remain actionable and do not expose secrets.

## Releases

Before a release, maintainers run tests, linting, self-scan, changelog review, and action smoke tests. Release notes are based on `CHANGELOG.md`, and public release artifacts should link to the self-scan report when useful.

Release checklist:

- `python scripts/check.py`
- GitHub Action smoke test
- Changelog entry and tag notes
- Security policy and issue templates still current

## Public readiness gate

Before a launch post, JOSS submission, or outreach to Artifact Evaluation chairs,
run:

```bash
python scripts/check_public_readiness.py
```

This local gate checks the first-time evaluator signals that are easy to
regress: the README live demo and GIF, package metadata URLs, issue templates,
self-scan badge/report consistency, corpus scan evidence, and absence of
out-of-scope working files or local workspace paths. It does not
call external services; maintainers still need to manually confirm that GitHub
issues are enabled, the Streamlit demo is awake, and any external post drafts
match the current release.
