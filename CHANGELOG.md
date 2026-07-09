# Changelog

## Unreleased

- Hardened the release sequence so the Streamlit demo can remain pinned to the
  last published package until the new PyPI version is publicly installable,
  avoiding a deployment race during Trusted Publishing propagation.
- Added an offline integration test that installs a declared local wheel into
  the temporary verification environment and requires L3 to import it.
- Moved a minimal copyable GitHub Action workflow near the top of the README and
  added a public-readiness regression check so the main adoption path stays
  visible to first-time and Marketplace visitors.
- Added a low-friction 10-minute trial issue form that separates useful findings,
  false-positive or false-negative feedback, and real deadline fit; the web demo
  now links to that form after each completed scan.
- Added versioned official MCP Registry metadata and the PyPI ownership marker,
  while keeping the MCP SDK outside the core scanner dependency set.

## v0.2.22 - 2026-07-10

- Upgraded Python `verify --run` from dependency resolution-only checks to a
  real temporary isolated environment: declared dependencies are installed and
  L3 executes with the isolated interpreter/PATH. Reports disclose build-hook
  execution risk, redact temporary paths, and clean the environment afterward.
- Corrected stale Zenodo citation metadata, documented the stable concept DOI,
  validated the archived `v0.2.21` record, and added an optional post-release
  Zenodo metadata check.
- Refreshed the nanoGPT first-run case study and focused corpus review note
  against PyPI `rrdoctor==0.2.21`, confirming `Functional` readiness, 76/100,
  0 errors, and no `RRD050` or `RRD063` regression.

## v0.2.21 - 2026-07-09

- Strengthened the JOSS draft manuscript with an explicit evaluation and
  calibration section covering the reviewed 80-repository static corpus,
  expected-absent regression gate, and limits of the evidence.
- Added a copyable GitHub Copilot instructions template so the rrdoctor
  baseline -> plan -> verify loop can be installed in target research
  repositories alongside the existing Agent Skill and Cursor templates.
- Added an 80-repository calibration data brief that turns the reviewed corpus
  snapshot into a public, caveated launch artifact with reproducible commands
  and copy-ready framing for community posts.
- Reduced `RRD063` and `RRD090` secret false positives by adding a conservative
  entropy threshold for generic `api_key`/`token`/`secret`/`password`
  assignments, while keeping provider-shaped keys such as standalone AWS access
  key IDs blocking.
- Reduced `RRD050` first-run noise for model-release repositories by treating
  root, `scripts/`, and `tools/` `demo.py`, `inference.py`, `predict.py`,
  `sample.py`, and `generate.py` files plus README-documented commands as
  experiment entrypoints; `verify` now detects the same entrypoint family for
  the L3 run-path ladder.
- Reduced `RRD043` local-path noise for vendored dependency trees such as
  `dependencies/`, `third_party/`, and `vendor/`, after the instant-ngp corpus
  review exposed a vendored TinyEXR Windows test path as non-actionable noise.
- Reduced `RRD052` seed-rule noise by recognizing
  `pytorch_lightning.seed_everything(...)` and
  `lightning.pytorch.seed_everything(...)` as valid seed applications.
- Reduced first-run noise for legacy/Bazel scientific projects by recognizing
  `setup.py`/`setup.cfg` as Python dependency manifests, `python_requires` as a
  runtime version hint, Bazel `*_test(...)` targets as test runner evidence, CI
  test scripts such as `run_github_tests.sh`, and URL path segments in notebook
  markdown cells.
- Added focused corpus review notes and `expected_absent` regression gates for
  detectron2, DINO, StyleGAN2-ADA PyTorch, instant-ngp, Big Vision,
  latent-diffusion, taming-transformers, generative-models,
  pytorch-image-models, Brax, ArviZ, PyMC, Pyro, TensorFlow Probability,
  statsmodels, Optax, long-range-arena, OpenSpiel, yt, SunPy, Nilearn,
  MNE-Python, Nipype, clusterProfiler, DifferentialEquations.jl, Turing.jl,
  Flux.jl, Distributions.jl, and Images.jl. The 80-repository corpus now has 80
  focused review notes and 0 repositories still awaiting focused manual review.

## v0.2.20 - 2026-07-09

- Refreshed the nanoGPT first-run case study and corpus review notes against
  PyPI `rrdoctor==0.2.19`, confirming that `RRD050` and `RRD063` remain absent.
- Reduced mature scientific-package noise by recognizing common license
  filenames such as `LICENSE.txt` and ignoring CI/devcontainer plus placeholder
  absolute paths, URL path segments, and common example-user paths in `RRD043`.
  Added SciPy, torchvision, MDAnalysis, QuTiP, and ESM as focused corpus review
  cases and regression gates for `RRD010`, `RRD030`, `RRD043`, and `RRD050`.
- Reduced `RRD090` and `RRD050` first-run noise found while expanding the corpus:
  public URL query `token=` values, local function-call or method-call token
  variables, generic test-helper tokens, and `AKIA...` substrings embedded in
  longer biological/test sequences are no longer treated as committed secrets;
  mature library/framework projects, including nested `package/` layouts, are
  not forced to expose paper experiment entrypoints.
- Expanded the public calibration corpus from 60 to 80 repositories, adding
  probabilistic ML, JAX ecosystem, scientific Python, legacy RL, scientific
  package, neural-rendering, protein-model, and similarity-search projects. The
  80-repository gate passes with 0 expected-absent regressions and 48 focused
  review notes loaded.
- Added stable-diffusion as a focused review case and expected-absent gate for
  `RRD030` and `RRD052`; Conda `environment.yaml`/`conda.yaml` manifests and
  editable pip entries with `#egg=` are now recognized by dependency checks.
- Improved auto-fix scaffolds for legacy Python research repositories:
  `rrdoctor fix --write` can now read simple literal `setup.py` metadata
  statically, without executing repository code, before generating
  `CITATION.cff`, data, and results provenance notes.
- Improved Artifact Appendix scaffolds for legacy Python research repositories:
  repository URL and version fields can now be pre-filled from the same static
  local metadata inference used by auto-fix scaffolds.
- Improved L2 dynamic verification coverage for common research repository
  layouts: `verify --run` now recognizes nested Python requirement files such
  as `requirements/base.txt` and `requirements/main.txt`, plus `.yaml` Conda
  environment files.
- Reduced `RRD063` notebook-output false positives by sharing the `RRD090`
  test/fixture generic fake-token suppression, while still flagging standalone
  provider-style keys.

## v0.2.19 - 2026-07-09

- Reduced `RRD050` first-run entrypoint false positives for large research
  frameworks by recognizing package-level research binaries such as
  `t5x/train.py` and README commands that invoke `python3` with environment
  variable path prefixes.
- Reduced `RRD050` notebook-first false positives by recognizing clearly named
  demo/example/reproduce notebooks such as `graphcast_demo.ipynb` as experiment
  entrypoints.
- Added focused corpus review notes and `expected_absent` regression gates for
  t5x and GraphCast; the 60-repository corpus scan remains at 0 expected-absent
  regressions with 32 focused review notes loaded.

## v0.2.18 - 2026-07-09

- Changed `RRD034` dependency-gap detection to parse Python AST import
  statements instead of regex-matching source text, reducing false positives
  from comments, docstrings, prose examples, tests, docs, benchmarks, and
  vendored/tooling paths in real corpus repositories; local sibling modules and
  test configuration files are no longer treated as undeclared third-party
  packages.

## v0.2.17 - 2026-07-09

- Refined public release notes and README wording so the latest package metadata
  focuses on reviewer-facing functionality and release consistency.
- Kept v0.2.16's Julia test/CI recognition, path-noise reduction, and
  public-readiness checks as the current installable package behavior.

## v0.2.16 - 2026-07-09

- Published a small alignment release so the GitHub tag, source tree, and PyPI
  package all point at the same current source state.
- Recognized Julia `test/runtests.jl`, Julia `Project.toml` test targets, and
  `julia-actions/julia-runtest` as valid testing and CI evidence.
- Tightened Windows absolute-path detection so regex-escaped warning filters do
  not look like local machine paths.
- Kept the public-readiness guard focused on tracked source and release
  metadata.

## v0.2.15 - 2026-07-09

- Added an explicit `timeout` parameter to the MCP `verify` tool so coding
  agents can run the same bounded L1/L2/L3 verification gate as the CLI.
- Enabled GitHub private vulnerability reporting and updated security guidance
  for secret-masking, report-generation, and dynamic-verification concerns.
- Replaced the placeholder CODEOWNERS entry and tightened the pull request
  checklist around tests, type checks, self-scan, and trusted dynamic verification.
- Refreshed good-first-contribution guidance so it points to current starter
  work instead of rule families that are already implemented.
- Added a cross-platform `python scripts/check.py` maintainer gate, wired
  `make check` to it, and exposed the live demo in package metadata.
- Added a public-readiness gate for release/JOSS/Artifact Evaluation outreach
  checks covering demo assets, package metadata, issue templates, self-scan
  evidence, corpus evidence, and source-tree hygiene.
- Improved the `DATA.md` auto-fix scaffold so it carries over candidate dataset
  URLs, DOIs, README data commands, and local data scripts for maintainer review.
- Pre-filled the Artifact Appendix with local README/project metadata,
  dependency manifests, data/results docs, config files, and detected entrypoint
  commands where available.
- Improved verification reports with a top-level evidence summary, explicit
  gate outcome, failure threshold, timeout, trust boundary, per-step details,
  and a copyable rerun command.
- Made verification reports show the L3 command source, distinguishing explicit
  `--command`, README-documented commands, and conservative fallback entrypoints.

## v0.2.14 - 2026-07-06

- Added a public-hygiene regression test that prevents out-of-scope working
  files, local workspace paths, and the README demo GIF regression from
  re-entering the tracked repository.
- Recognized root-level `main_*.py` and `main-*.py` paper scripts as experiment
  entrypoints and verification fallbacks, based on MAE corpus review.
- Reduced unset-seed and local-path noise by ignoring test-file randomness,
  recognizing `random_seed=` passed to seeded operations, and skipping obvious
  placeholder absolute paths, based on AlphaFold corpus review.
- Added a `rrdoctor verify --command "..."` override, plus GitHub Action and
  MCP support, so maintainers can pin an official quickstart command as the L3
  dynamic verification gate.
- Added `rrdoctor prepare`, a one-command local Artifact Evaluation prep packet
  that writes the static report, agent fix plan, artifact appendix, and
  verification ladder into a single directory.
- Added GitHub Action `prepare` / `prepare-output` inputs so CI can upload the
  same Artifact Evaluation prep packet, and aligned `verify` / `prepare`
  `--fail-on warning` behavior with the documented Action input.

## v0.2.13 - 2026-07-06

- Added Artifact Evaluation next-step commands to Markdown scan reports and
  agent fix plans, including appendix generation, static verification, and
  trusted-only dynamic `verify --run` guidance.
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
