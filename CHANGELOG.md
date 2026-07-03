# Changelog

## Unreleased

- Added Artifact Evaluation-style readiness levels (`Available`, `Functional`,
  `Reproduced-ready`) to scan reports, JSON output, CLI summaries, fix plans, and badges.
- Changed `rrdoctor badge` to publish the readiness label instead of a bare numeric score.
- Reframed the README first screen around Artifact Evaluation deadline preparation.
- Added a public-repository evaluation corpus manifest and static scan runner for
  evidence-driven false-positive and false-negative review.
- Added corpus review-stub generation so maintainers can scale manual
  false-positive and false-negative review without inflating reviewed counts.
- Added a corpus regression gate for `expected_absent` rules, so reviewed
  first-run trust cases such as nanoGPT can fail before release if known
  false-positive or false-negative regressions return.
- Updated PyPI publishing documentation to match the active Trusted Publishing
  workflow and current `rrdoctor` package release.
- Polished public documentation, release notes, and project hygiene evidence.
- Replaced the broken README demo placeholder with a generated demo GIF and kept
  the unavailable live demo link out of the first screen.
- Fixed `RRD050` so common research entrypoints such as root-level `train.py`, `main.py`,
  `run.py`, eval scripts, Snakemake, Nextflow, and documented README commands count as
  experiment entrypoints.
- Tightened `RRD063` and `RRD090` secret heuristics so notebook output needs a
  high-confidence credential-like value before triggering a security error.
- Improved `rrdoctor fix` metadata inference for generated citation scaffolds.
- Improved `rrdoctor fix` data-provenance scaffolds so generated `DATA.md` and
  `data/README.md` include local evidence such as data directories, retrieval
  scripts, README data mentions, and current `data/` contents.
- Reduced `RRD091` noise on real research repositories by checking `.gitignore`
  coverage groups instead of requiring every optional research-tool ignore
  entry.
- Changed `RRD100` (missing changelog) from warning to info in standard scans so
  release history remains visible without penalizing core artifact
  reproducibility.
- Updated corpus summaries to rank top actionable error/warning rules while
  still preserving all rule frequencies in JSON.
- Improved `RRD101` version metadata detection so local git tags count as
  version evidence without requiring network access.
- Made `RRD101` informational in standard/ML scans while keeping it a warning in
  strict and submission profiles.
- Improved `RRD020` citation detection so README Citing sections, "please cite"
  text, BibTeX entries, DOI fields, and DOI links count as citation guidance.

## v0.2.3 - 2026-06-30

- Repositioned around conference Artifact Evaluation: README leads with an
  "AE-ready before you submit" wedge and zero-clone `uvx`/`pipx` install commands.
- Added `rrdoctor appendix`: generates an ACM-style Artifact Appendix skeleton and maps findings
  to ACM badge tiers (Available / Functional / Reproduced) and the NeurIPS reproducibility checklist.
- Added `rrdoctor verify`: an L1 (static) / L2 (environment build) / L3 (entrypoint run)
  reproducibility ladder. With `--run` it actually resolves dependencies (`uv`/`pip`/`conda`/`Rscript`)
  and executes a declared entrypoint under a `--timeout`. Static by default. Only `--run` trusted repos.
- Added `rrdoctor mcp`: an MCP server exposing `scan`/`verify`/`appendix` as tools for coding
  agents (optional extra: `pip install 'rrdoctor[mcp]'`).
- Added submission profiles `ml-paper`, `neurips`, `icml`, `acm`, `fair4rs`, and `joss` with
  tag-based inheritance from the base profiles.
- Added rule `RRD034` (deptry-style import-vs-manifest cross-check) and `RRD054` (hardcoded
  GPU/CUDA assumption without a documented requirement).
- Broadened environment checks to R (`DESCRIPTION`, `install.R`) and Julia (`Project.toml`)
  manifests and runtime-version hints.
- The GitHub Action profile input now accepts the submission profiles.
- Added release, publishing, and outreach documentation without requiring users to manage API keys.

## v0.2.0 - 2026-06-08

- Added `rrdoctor fix`: deterministic, idempotent auto-fix that scaffolds common gaps
  (LICENSE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, AGENTS.md, CITATION.cff, DATA.md,
  data/README.md, results/README.md, CHANGELOG.md, and .gitignore entries). Existing files
  are never overwritten and no code from the scanned repository is executed.
- Added `rrdoctor plan` and the `agent` report format: a tool-agnostic fix plan where each
  task names the deterministic check that verifies it.
- Added baseline comparison to `rrdoctor scan` via `--baseline` and `--fail-on-new`, so CI
  can gate only on newly introduced findings.
- Added `rrdoctor badge`: a Shields.io endpoint document or a self-contained SVG badge.
- Enhanced the GitHub Action with sticky pull request comments, job summaries, an optional
  fix-plan artifact, baseline gating, and artifact upload, all using the built-in token.
- Added rules: RRD014 (AGENTS.md task guide), RRD033 (unpinned dependencies), RRD065
  (committed notebook checkpoints), and RRD082 (pre-commit configuration).
- Added the `autofix_available` flag and a stable finding fingerprint to the report model.
- Expanded documentation, examples, and tests; refreshed the self-scan report and badge.

## v0.1.0 - 2026-06-03

- Initial public-release-ready repository structure.
- Added `rrdoctor scan`, `init`, `list-rules`, `explain`, and `doctor` commands.
- Added deterministic rule engine with research reproducibility checks across documentation, data, environments, experiments, notebooks, citation, governance, testing, CI, security, release, and metadata.
- Added Markdown, JSON, and experimental SARIF-compatible reports.
- Added GitHub Action metadata and example workflows.
- Added tests, fixtures, docs, issue templates, PR template, roadmap, security policy, citation metadata, and maintainer workflow notes.
- Added example reports, including a self-scan report for release review.
- Completed v0.1.0 release-readiness pass covering YAML validity, package metadata, docs consistency, local Markdown links, and refreshed self-scan output.
