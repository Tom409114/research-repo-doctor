# PyPI Publishing

Research Repo Doctor publishes the `rrdoctor` package to PyPI from GitHub
Releases using PyPI Trusted Publishing. Maintainers do not need long-lived PyPI
API tokens.

## Current Package

- PyPI project: `rrdoctor`
- Current package version: `0.2.15`
- Release workflow: [`.github/workflows/release.yml`](../.github/workflows/release.yml)
- PyPI environment name: `pypi`

Install from PyPI:

```bash
uvx rrdoctor scan .
pipx run rrdoctor scan .
python -m pip install rrdoctor
```

## Trusted Publishing Setup

The GitHub workflow is configured to publish on GitHub Release publication:

- trigger: `release` / `published`
- build frontend: `python -m build`
- publisher: `pypa/gh-action-pypi-publish@release/v1`
- OIDC permission: `id-token: write`
- GitHub environment: `pypi`

PyPI should have a matching trusted publisher entry:

- PyPI project: `rrdoctor`
- Owner: `Tom409114`
- Repository: `research-repo-doctor`
- Workflow: `release.yml`
- Environment: `pypi`

Do not add a PyPI password or API token secret to this repository unless Trusted
Publishing becomes unavailable and the maintainer explicitly accepts that
tradeoff.

## Local Release Checks

Before publishing a GitHub Release:

```bash
python -m pip install --upgrade build twine
python -m build
twine check dist/*
python -m pytest
ruff check .
ruff format --check .
python -m rrdoctor scan . --profile standard --fail-on none --quiet
```

Confirm the version is consistent in:

- [`pyproject.toml`](../pyproject.toml)
- [`src/rrdoctor/__init__.py`](../src/rrdoctor/__init__.py)
- [`CITATION.cff`](../CITATION.cff)
- [`CHANGELOG.md`](../CHANGELOG.md)

## Publishing Flow

1. Merge the release-preparation pull request.
2. Ensure the working tree is clean and tests are green.
3. Create and push a signed or annotated version tag when possible.
4. Publish a GitHub Release for that tag.
5. Watch the `Publish to PyPI` workflow.
6. Verify the package after the workflow succeeds:

```bash
python -m pip index versions rrdoctor
uvx rrdoctor --help
```
