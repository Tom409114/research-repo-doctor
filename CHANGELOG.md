# Changelog

## Unreleased

- Made the `RRD014` `AGENTS.md` scaffold include the rrdoctor
  scan/plan/baseline verification loop and trusted-only `verify --run` guidance
  for coding agents.
- Made the `RRD053` results-provenance scaffold include local project context,
  repository URL, readable git commit, existing `results/` contents, and a
  structured result-inventory table.
- Expanded the first-party Action smoke test to assert that trusted dynamic
  verification failures are reported and block the composite action when
  `verify-run` and `verify-fail-on: error` are enabled.

## v0.2.12 - 2026-07-06

- Added `verify-fail-on` to the GitHub Action so trusted `verify-run` jobs can
  block CI on dynamic verification failures while still uploading the generated
  verification report.
- Added repository-level GitHub Copilot instructions plus copyable Agent Skill
  and Cursor rule templates for using rrdoctor as a deterministic coding-agent
  verification loop.
- Tightened public corpus and JOSS draft wording so focused review notes are not
  overstated as full manual repository audits.

## v0.2.11 - 2026-07-05

- Added a CI smoke test for the optional MCP extra and documented how to verify
  that the MCP server builds before wiring it into a coding agent.
- Reduced first-run false positives by recognizing README install/usage commands
  even when legacy research repositories do not use modern setup/quickstart
  headings.
- Reduced `RRD052` false positives by treating `random.Random(seed)` as a
  deterministic local RNG seed application.
- Reduced `RRD052` false positives by ignoring PyTorch parameter-initialization
  wrappers such as `nn.Parameter(torch.randn(...))` when no other randomness is
  present.
- Reduced secret-scanning false positives by treating canonical UUID values as
  public identifiers rather than generic `token`/`secret` credentials.
- Made `rrdoctor verify --run` a real automation gate: with the default
  `--fail-on error`, dynamic L2/L3 failures or blocked run steps now return a
  nonzero exit code instead of only appearing in the Markdown report.
- Added focused corpus review notes for BERT, CLIP, and improved-diffusion,
  including expected-absent coverage for CLIP model parameter initialization.

## v0.2.10 - 2026-07-05

- Clarified evaluation corpus review accounting so generated summaries
  distinguish completed focused review notes from repositories that still need
  manual review.
- Improved `rrdoctor doctor` optional dependency checks so it reports an MCP
  integration as available only when the MCP package and its import-time
  dependencies actually load.
- Updated first-party workflows, the composite action, and documentation
  examples to current Node 24-compatible GitHub Actions releases.
- Made the evaluation corpus runner fall back to GitHub archives when
  `git clone` times out, not only when clone exits with an error.

## v0.2.9 - 2026-07-04

- Added `rrdoctor --version` for quick CLI/package version checks.
- Made bare `rrdoctor` print the root help page and exit successfully, improving
  the first-run CLI experience.

## v0.2.8 - 2026-07-04

- Improved README entrypoint detection and verification so documented
  `python -m package.train ...` commands count as experiment entrypoints when
  they point at local repository modules.
- Improved `rrdoctor verify` support for module-runner commands such as
  `python -m torch.distributed.run train.py ...` when the command includes a
  file-backed local Python entrypoint.

## v0.2.7 - 2026-07-04

- Improved `rrdoctor fix --write` citation scaffolds so `CITATION.cff` can use
  structured PEP 621 or Poetry metadata, preserve multiple authors, normalize
  SSH git remotes, and read git worktree origin URLs without executing target
  repository code.
- Improved `RRD034` dependency parsing for PEP 621 environment markers and
  Poetry dependency groups, reducing undeclared-import false positives.

## v0.2.6 - 2026-07-04

- Reduced `RRD090` security false positives on R/pkgdown repositories by
  ignoring Rcpp `Generator token` provenance markers and public pkgdown
  `docsearch.api_key` search configuration while keeping generic API key
  detection active.
- Added a GitHub archive fallback to the evaluation corpus runner so static
  corpus scans can continue when `git clone` transport is unavailable or flaky.
- Expanded focused corpus review notes from 4 to 17 repositories, covering
  Snakemake/Nextflow entrypoint regression cases and R/Rcpp secret-heuristic
  false positives.
- Refreshed the public corpus snapshot: 60 listed repositories, 60 successful
  static scans, 0 expected-absent regressions, and 17 focused review notes loaded
  in that snapshot.
- Added tests for package version consistency across `pyproject.toml`,
  `rrdoctor.__version__`, `CITATION.cff`, and demo dependencies.

## v0.2.5 - 2026-07-04

- Improved `RRD050` first-run trust on real ML/research repositories by
  recognizing ML-style `tools/train.py`, `tools/test.py`, documented
  `python scripts/*.py` or `python tools/*.py` commands, and pyproject-declared
  console scripts shown in the README.
- Added focused corpus review notes and `expected_absent` regression gates for
  `segment-anything`, `whisper`, and `mmdetection` entrypoint detection.
- Added `RRD052` auto-fix scaffolding: `rrdoctor fix --write` can create a
  non-destructive `set_global_seed(seed)` helper for Python/NumPy/PyTorch/
  TensorFlow projects while leaving integration with the training entrypoint as
  an explicit TODO.
- Updated auto-fix documentation to clarify that some scaffolds are starting
  points and clear findings only after maintainers wire them into the project.
- Refreshed the public evaluation-corpus snapshot and self-scan report.

## v0.2.4 - 2026-07-04

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
- Improved `RRD004` reproducibility README detection so concrete training,
  evaluation, benchmark, workflow, or reproduction commands count as a documented
  path to reproduce results.

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
