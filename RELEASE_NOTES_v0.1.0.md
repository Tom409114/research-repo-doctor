# Research Repo Doctor v0.1.0

Research Repo Doctor is a deterministic, local-first CLI and GitHub Action for auditing research code repositories for reproducibility, reviewability, citation readiness, security hygiene, and release readiness.

## Highlights

- Adds the `rrdoctor` Python package and CLI.
- Provides `rrdoctor scan`, `init`, `list-rules`, `explain`, and `doctor`.
- Includes deterministic checks for README quality, licensing, citation metadata, dependency manifests, data documentation, experiment entrypoints, notebooks, tests, CI, security hygiene, changelog, release metadata, and project metadata.
- Emits Markdown, JSON, and experimental SARIF-compatible reports.
- Includes GitHub Action metadata for use as `Tom409114/research-repo-doctor@v0.1.0`.
- Includes fixtures, tests, documentation, issue templates, a contribution guide, security policy, roadmap, citation metadata, and Codex for OSS application notes.

## Install from source

```bash
git clone https://github.com/Tom409114/research-repo-doctor.git
cd research-repo-doctor
python -m pip install -e ".[dev]"
```

## CLI usage

```bash
rrdoctor scan .
rrdoctor scan . --profile strict --fail-on warning --output rrdoctor-report.md
rrdoctor list-rules
rrdoctor explain RRD001
```

## GitHub Action usage

```yaml
- uses: Tom409114/research-repo-doctor@v0.1.0
  with:
    profile: standard
    fail-on: warning
    output: rrdoctor-report.md
```

## Rule coverage

v0.1.0 includes rules across documentation, governance, citation, environment, data, experiments, reproducibility, notebooks, testing, CI, security, release, and metadata categories.

## Known limitations

- SARIF output is experimental.
- The score is heuristic and should not replace human review.
- The scanner is deterministic and local-first; it does not verify external DOI, package, or archive URLs over the network.
- PyPI publication is deferred until Trusted Publishing is configured.

## Codex for OSS application notes

See `docs/codex-for-oss-application.md` and `APPLICATION_READY.md`.

## Roadmap issues

Initial issue drafts are available in `docs/initial-issues.md`. Once the public GitHub repository is available, maintainers can create the roadmap issues from those drafts.
