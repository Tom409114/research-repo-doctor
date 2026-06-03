# Initial GitHub Issue Drafts

These drafts are ready to copy into GitHub issues after the public repository is created. Replace labels or priorities to match the final project board.

## 1. Add R project environment detection

**Title:** Add R project environment detection

**Type label suggestion:** `rule-request`, `environment`, `good first issue`

**Priority:** Medium

**Background:** Research Repo Doctor currently detects common Python, Conda, Node, and R `renv.lock` dependency signals, but R research repositories often use several additional conventions. Supporting these conventions would make the tool more useful for statistics, social science, ecology, bioinformatics, and reproducible analysis projects.

**Proposed implementation:**

- Extend environment detection to recognize `DESCRIPTION`, `renv.lock`, `.Rprofile`, `install.R`, `requirements.R`, and `packages.R`.
- Detect R version hints in `renv.lock`, `DESCRIPTION`, `.Rprofile`, and README setup sections.
- Add remediation text that recommends `renv`, documented R version, and setup commands.
- Add fixtures for a healthy R project and an R project missing version hints.
- Update `docs/checks.md` and `docs/configuration.md` if behavior changes.

**Acceptance criteria:**

- R projects with `renv.lock` or `DESCRIPTION` are treated as having dependency metadata.
- R projects without an R version hint can trigger the existing environment version warning.
- Tests cover both positive and non-finding cases.
- Reports give R-specific remediation without weakening Python behavior.

**Good first issue suitability:** Good first issue if scoped to detection and tests only. It is deterministic and does not require changing report formats.

**Related rules if applicable:** `RRD030`, `RRD031`

## 2. Add Julia project environment detection

**Title:** Add Julia project environment detection

**Type label suggestion:** `rule-request`, `environment`, `good first issue`

**Priority:** Medium

**Background:** Julia is common in numerical computing and research software. Julia projects usually describe dependencies through `Project.toml` and `Manifest.toml`, which should be recognized as environment metadata.

**Proposed implementation:**

- Treat `Project.toml` and `Manifest.toml` as dependency manifests.
- Detect Julia version hints from `Manifest.toml`, README setup docs, or `.julia-version` if present.
- Add Julia-specific remediation recommending `julia --project=.` and checked-in environment files.
- Add minimal Julia fixtures for healthy and missing-version cases.

**Acceptance criteria:**

- A repository with `Project.toml` is not flagged by `RRD030`.
- A repository with Julia dependencies but no version hint can be flagged by `RRD031`.
- Tests verify detection without network calls.
- Documentation lists Julia environment support.

**Good first issue suitability:** Good first issue. The implementation is mostly manifest recognition, parsing heuristics, and fixtures.

**Related rules if applicable:** `RRD030`, `RRD031`

## 3. Add Snakemake and Nextflow workflow detection

**Title:** Add Snakemake and Nextflow workflow detection

**Type label suggestion:** `rule-request`, `experiments`, `workflow`

**Priority:** High

**Background:** Many computational biology, data processing, and large-scale analysis repositories use Snakemake or Nextflow as their reproducibility entrypoint. Research Repo Doctor should recognize these workflows as experiment entrypoints and configuration evidence.

**Proposed implementation:**

- Recognize `Snakefile`, `*.smk`, `workflow/Snakefile`, `nextflow.config`, and `main.nf`.
- Treat these files as valid experiment entrypoints for `RRD050`.
- Treat `config.yaml`, `config.yml`, `nextflow.config`, and workflow config directories as configuration evidence where appropriate.
- Add fixtures for Snakemake and Nextflow repositories.
- Add docs explaining supported workflow entrypoints.

**Acceptance criteria:**

- Snakemake and Nextflow fixture repos do not trigger `RRD050` when entrypoints exist.
- Missing workflow config can still be flagged where relevant.
- Tests cover both workflow systems.
- Existing script and Makefile entrypoint detection remains unchanged.

**Good first issue suitability:** Moderate. Good for contributors familiar with workflow engines, but requires careful fixture design.

**Related rules if applicable:** `RRD050`, `RRD051`

## 4. Improve CITATION.cff validation

**Title:** Improve CITATION.cff validation

**Type label suggestion:** `citation`, `rule-improvement`

**Priority:** Medium

**Background:** The current citation check detects whether citation guidance exists. It does not validate whether `CITATION.cff` has the key fields needed for citation tools and GitHub rendering.

**Proposed implementation:**

- Parse `CITATION.cff` with PyYAML.
- Check for key fields such as `cff-version`, `message`, `title`, `authors`, and either `version`, `date-released`, `doi`, or repository metadata.
- Emit a warning for malformed YAML or missing recommended fields.
- Avoid strict schema validation in v0.1.x unless an optional dependency is introduced.
- Add fixtures for valid, missing-field, and malformed citation files.

**Acceptance criteria:**

- Valid `CITATION.cff` files do not produce citation validation warnings.
- Malformed or incomplete files produce actionable findings.
- The scanner never crashes on invalid YAML.
- Evidence does not print excessive file content.

**Good first issue suitability:** Moderate. Good for contributors comfortable with YAML parsing and edge cases.

**Related rules if applicable:** `RRD020`, `RRD021`

## 5. Add Zenodo DOI and archive metadata checks

**Title:** Add Zenodo DOI and archive metadata checks

**Type label suggestion:** `rule-request`, `citation`, `release`

**Priority:** Medium

**Background:** Research software is easier to cite and reproduce when releases are archived through Zenodo or another DOI-backed archive. The tool should check for documented archive metadata without making network calls.

**Proposed implementation:**

- Detect DOI-like strings in README, `CITATION.cff`, `.zenodo.json`, and docs.
- Recognize `.zenodo.json` as archive metadata.
- Add a warning when a release-ready research project has no archive or DOI guidance.
- Keep the check deterministic and offline; do not verify DOI existence over the network.
- Add docs clarifying that DOI detection is heuristic.

**Acceptance criteria:**

- Repositories with `.zenodo.json` or DOI guidance are recognized.
- Repositories with release metadata but no archive guidance can receive a warning.
- Tests include DOI, Zenodo metadata, and no-DOI fixtures.
- Documentation avoids implying that rrdoctor validates DOI registration.

**Good first issue suitability:** Moderate. The detection itself is approachable, but severity and profile behavior need maintainer review.

**Related rules if applicable:** `RRD020`, `RRD021`, `RRD100`, `RRD101`

## 6. Add support for repo-level reproducibility badges

**Title:** Add support for repo-level reproducibility badges

**Type label suggestion:** `documentation`, `rule-request`, `good first issue`

**Priority:** Low

**Background:** Some research repositories use README badges to show CI, package status, DOI, archival status, or reproducibility services. Research Repo Doctor should detect useful badges as supporting evidence, while avoiding badge-driven scoring that can be gamed.

**Proposed implementation:**

- Detect badges in README Markdown image/link syntax.
- Recognize common badge categories: CI, DOI/Zenodo, license, PyPI/package, docs, reproducibility services.
- Use badges as positive evidence in reports or as context for existing checks.
- Do not allow badges alone to satisfy substantive checks such as data availability or experiment entrypoints.

**Acceptance criteria:**

- README badge detection is tested with common Markdown badge formats.
- Badge evidence can appear in reports or future debug output.
- Documentation explains that badges are supporting signals, not proof of reproducibility.
- No network calls are made to badge providers.

**Good first issue suitability:** Good first issue. It is a bounded Markdown parsing and documentation task.

**Related rules if applicable:** `RRD002`, `RRD003`, `RRD020`, `RRD080`, `RRD111`

## 7. Add false-positive regression fixture format

**Title:** Add false-positive regression fixture format

**Type label suggestion:** `testing`, `maintainer-workflow`

**Priority:** High

**Background:** As more users report false positives, maintainers need a stable way to add regression fixtures that document the repository shape, expected quiet rules, and the issue that motivated the case.

**Proposed implementation:**

- Create a fixture metadata format such as `rrdoctor-fixture.yml` under fixture directories.
- Include fields for issue link, description, expected findings, expected quiet rules, profile, and notes.
- Add a test helper that can load fixture metadata and assert expected behavior.
- Document how maintainers turn a false positive issue into a regression fixture.

**Acceptance criteria:**

- At least one existing fixture uses the metadata format.
- A reusable pytest helper validates expected findings or expected quiet rules.
- `docs/maintainer-workflows.md` explains the process.
- The format avoids requiring private repository content.

**Good first issue suitability:** Moderate. It is a testing infrastructure task and should be reviewed carefully.

**Related rules if applicable:** All rules

## 8. Add Markdown table report for category scores

**Title:** Add Markdown table report for category scores

**Type label suggestion:** `reporting`, `good first issue`

**Priority:** Low

**Background:** The Markdown report already contains a category summary table. It would be useful to expose a compact table-only mode or reusable section that maintainers can paste into pull request comments.

**Proposed implementation:**

- Add an internal helper that renders only the category score table.
- Consider a CLI option such as `--summary-only` or a future report mode after maintainer discussion.
- Ensure category table output is stable enough for snapshot-like tests.
- Document intended use in PR comments and lightweight status reports.

**Acceptance criteria:**

- Category score table rendering is covered by tests.
- The existing full Markdown report remains unchanged unless intentionally updated.
- The table includes category, score, errors, warnings, and info counts.
- Documentation includes an example.

**Good first issue suitability:** Good first issue. It is a contained reporting change with straightforward tests.

**Related rules if applicable:** Not rule-specific

## 9. Add pre-commit hook example

**Title:** Add pre-commit hook example

**Type label suggestion:** `documentation`, `developer-experience`, `good first issue`

**Priority:** Low

**Background:** Some maintainers may want to run `rrdoctor` before committing changes to research repositories. A documented pre-commit example would make local adoption easier.

**Proposed implementation:**

- Add an example `.pre-commit-config.yaml` snippet to docs.
- Consider an `examples/pre-commit-config.yaml` file.
- Document recommended `--fail-on none` or `--fail-on error` behavior for local use.
- Explain that large scans may be better suited for CI than every commit.

**Acceptance criteria:**

- Docs include a copy-ready pre-commit example.
- The example uses local commands and does not require API keys.
- The guidance explains tradeoffs for repository size.
- No package behavior changes are required.

**Good first issue suitability:** Good first issue. This is documentation-focused and low risk.

**Related rules if applicable:** Not rule-specific

## 10. Add docs website deployment workflow

**Title:** Add docs website deployment workflow

**Type label suggestion:** `docs`, `ci`, `good first issue`

**Priority:** Medium

**Background:** The project has Markdown documentation under `docs/`, but no public documentation website deployment. A lightweight docs workflow would improve discoverability and make the project look more maintainable to users and evaluators.

**Proposed implementation:**

- Choose a lightweight docs tool such as MkDocs.
- Add minimal `mkdocs.yml` navigation.
- Add a GitHub Actions workflow to build docs on pull requests.
- Optionally deploy to GitHub Pages on `main`.
- Document the release and deployment process.

**Acceptance criteria:**

- Docs build passes in CI.
- Navigation includes quickstart, checks, configuration, GitHub Action, report formats, rule authoring, and maintainer workflows.
- Deployment instructions do not require secrets beyond standard GitHub Pages permissions.
- README links to the docs site once deployment is enabled.

**Good first issue suitability:** Good first issue if limited to MkDocs setup and CI build. Deployment settings may need maintainer follow-up.

**Related rules if applicable:** Not rule-specific

## 11. Add machine learning checkpoint hygiene checks

**Title:** Add machine learning checkpoint hygiene checks

**Type label suggestion:** `rule-request`, `ml`, `security`

**Priority:** Medium

**Background:** ML research repositories often generate large model checkpoints, experiment outputs, and tracking directories. These artifacts can bloat repositories, leak data, or make releases hard to review.

**Proposed implementation:**

- Add ML-profile checks for common checkpoint files and directories: `*.pt`, `*.pth`, `*.ckpt`, `*.h5`, `checkpoints/`, `outputs/`, `wandb/`, and `mlruns/`.
- Reuse large-file thresholds where possible.
- Check `.gitignore` coverage for checkpoint and tracking directories.
- Provide remediation recommending external artifact storage, Git LFS where appropriate, and documented retrieval instructions.
- Add ML fixtures with ignored and committed checkpoint-like files.

**Acceptance criteria:**

- ML profile can flag committed checkpoint-like artifacts.
- `.gitignore` recommendations remain actionable and do not duplicate existing findings excessively.
- Evidence includes file paths and sizes where useful, without reading binary content.
- Tests cover common checkpoint extensions and directories.

**Good first issue suitability:** Moderate. It is deterministic, but needs careful severity and duplicate-finding handling.

**Related rules if applicable:** `RRD042`, `RRD091`, potential new ML-specific rule

## 12. Add anonymized scan corpus for rule evaluation

**Title:** Add anonymized scan corpus for rule evaluation

**Type label suggestion:** `testing`, `research-repo`, `maintainer-workflow`

**Priority:** High

**Background:** Rule quality will improve if maintainers can evaluate changes against a small corpus of anonymized or public research repository shapes. This should not include private data, real secrets, or copied proprietary repository contents.

**Proposed implementation:**

- Define a corpus directory structure under `tests/fixtures/corpus/` or a separate documented location.
- Include metadata for repository domain, languages, expected findings, and source/permission notes.
- Start with synthetic or heavily anonymized cases.
- Add a test mode or helper that runs selected profiles against the corpus.
- Document privacy and permission requirements for contributed cases.

**Acceptance criteria:**

- Corpus format is documented.
- At least two synthetic corpus cases are included.
- Tests can run the corpus without network access.
- Contribution guidance clearly forbids real secrets, private data, and unpermitted code copies.

**Good first issue suitability:** Moderate to advanced. Good for contributors interested in testing infrastructure and research software diversity.

**Related rules if applicable:** All rules
