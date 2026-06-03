# PyPI Publishing Preparation

PyPI publication is intentionally deferred for v0.1.0 unless the maintainer explicitly requests it and Trusted Publishing is configured.

## Recommended Trusted Publishing setup

1. Create or claim the `rrdoctor` project on PyPI.
2. In PyPI project settings, add a trusted publisher for:
   - Owner: `research-repo-doctor`
   - Repository: `research-repo-doctor`
   - Workflow: `.github/workflows/release.yml`
   - Environment: leave empty unless the workflow later uses one.
3. Verify the GitHub release workflow has `id-token: write`.
4. Uncomment the `pypa/gh-action-pypi-publish` step in `.github/workflows/release.yml`.
5. Publish only from a reviewed GitHub tag/release workflow.

## Local build check

```bash
python -m pip install build
python -m build
```

If `twine` is available:

```bash
twine check dist/*
```

Do not use long-lived PyPI API tokens unless Trusted Publishing is not available and the maintainer explicitly accepts that tradeoff.
