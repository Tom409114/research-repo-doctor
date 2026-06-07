# Roadmap

## v0.1.0

- Deterministic CLI scans.
- Markdown, JSON, and experimental SARIF-compatible reports.
- GitHub Action integration.
- Public docs and contribution workflow.
- Issue templates and a published self-scan report.

## v0.2.0

- Deterministic auto-fix (`rrdoctor fix`) for common reproducibility gaps.
- Tool-agnostic agent fix plan (`rrdoctor plan` / `agent` format).
- Baseline comparison and new-finding gating for incremental adoption.
- Score badge (`rrdoctor badge`).
- Pull request automation: sticky comments, job summaries, fix-plan artifacts.
- New rules: AGENTS.md, unpinned dependencies, notebook checkpoints, pre-commit.

## v0.3.0

- More robust SARIF output and code-scanning docs.
- Additional language ecosystem checks for R, Julia, MATLAB, and JavaScript research repos.
- More fixers (Dockerfile/devcontainer stubs, CI workflow scaffolding) with strict safety.
- Better report diffing and richer PR comment summaries (score deltas, fixed/new tables).
- Workflow detection for Snakemake, Nextflow, and other research pipelines.
- Zenodo, DOI, and arXiv metadata detection improvements.

## Good first issues

- Add R and Julia environment detection.
- Add Snakemake/Nextflow workflow detection.
- Add a fixer for a minimal CI workflow.
- Improve notebook path detection.
- Add Zenodo/DOI detection.
- Add a docs website deployment.
