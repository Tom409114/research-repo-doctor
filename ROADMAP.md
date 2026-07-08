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
- Badge endpoint (`rrdoctor badge`).
- Pull request automation: sticky comments, job summaries, fix-plan artifacts.
- New rules: AGENTS.md, unpinned dependencies, notebook checkpoints, pre-commit.

## v0.2.3

- Artifact Evaluation profiles and appendix generation.
- Verification ladder (`rrdoctor verify`) with static, environment, and entrypoint tiers.
- Coding-agent verifier loop and optional MCP integration.
- R and Julia environment metadata detection.
- Root-level ML entrypoint detection plus Snakemake and Nextflow workflow detection.
- Reproducible randomness checks for unseeded Python/ML code.

## v0.2.4

- First-run trust fixes driven by the public repository evaluation corpus.
- More conservative notebook and repository secret heuristics.
- Lower-noise README reproducibility and citation guidance detection.
- Git-tag-based release metadata detection without network access.
- Public corpus calibration snapshot and refreshed 100/100 self-scan evidence.

## v0.3.0

- More robust SARIF output and code-scanning docs.
- Additional language ecosystem checks for MATLAB and JavaScript research repos.
- More fixers (Dockerfile/devcontainer stubs, CI workflow scaffolding) with strict safety.
- Better report diffing and richer PR comment summaries (score deltas, fixed/new tables).
- Broader workflow detection for CWL, DVC, and other research pipelines.
- Zenodo, DOI, and arXiv metadata detection improvements.

## Good first issues

- Add MATLAB runtime environment detection.
- Add JavaScript/Node research environment refinements.
- Add a fixer for a minimal CI workflow.
- Improve notebook path detection fixtures.
- Improve Zenodo, DOI, and arXiv metadata detection.
- Add support for another workflow marker such as CWL or DVC.
- Add a docs website deployment.
