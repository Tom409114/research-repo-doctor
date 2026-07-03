# Research Repo Doctor v0.2.0

v0.2.0 turns Research Repo Doctor from an auditor into a full audit → fix → verify loop. The
core stays deterministic, local-first, and API-key-free; the new pieces let you act on the
output and gate it in CI.

## Highlights

- **`rrdoctor fix`** — deterministic, idempotent auto-fix. Scaffolds LICENSE, CONTRIBUTING,
  SECURITY, CODE_OF_CONDUCT, AGENTS.md, CITATION.cff, DATA.md, data/README.md,
  results/README.md, CHANGELOG.md, and `.gitignore` entries. Existing files are never
  overwritten and no repository code is executed. Preview by default; apply with `--write`.
- **`rrdoctor plan`** and the `agent` format — a tool-agnostic fix plan. Every task names the
  files to change and the deterministic check that verifies it, so any coding agent (or a
  human) can execute it and `rrdoctor scan` confirms the result.
- **Baseline gating** — `rrdoctor scan --baseline report.json --fail-on-new error` reports new
  and resolved findings and fails only on newly introduced ones. Large repositories can adopt
  the audit without fixing everything first.
- **`rrdoctor badge`** — a Shields.io endpoint document or self-contained SVG badge.
- **Pull request automation** — the GitHub Action posts a sticky PR comment, writes the report
  to the job summary, can attach an agent-ready fix plan, supports baseline gating, and uploads
  artifacts. It uses only the built-in `GITHUB_TOKEN`.
- **New rules** — RRD014 (AGENTS.md task guide), RRD033 (unpinned dependencies), RRD065
  (committed notebook checkpoints), RRD082 (pre-commit configuration).

## Upgrade notes

- The GitHub Action reference moves to `Tom409114/research-repo-doctor@v0.2.0`.
- `--format agent` is a new scan format; `markdown`, `json`, and `sarif` are unchanged.
- Reports gain `autofix_available` on each finding; existing JSON consumers are unaffected.

## Install from source

```bash
git clone https://github.com/Tom409114/research-repo-doctor.git
cd research-repo-doctor
python -m pip install -e ".[dev]"
```

## The loop

```bash
rrdoctor scan . --format json --output baseline.json --fail-on none
rrdoctor fix . --write
rrdoctor plan . --output fix-plan.md      # hand to any coding agent
rrdoctor scan . --baseline baseline.json --fail-on-new error
```

## Known limitations

- SARIF output remains experimental.
- The score is heuristic and does not replace human review.
- Generated fixes are starting points with placeholders to complete before release.
- The scanner does not verify external DOI, package, or archive URLs over the network.
