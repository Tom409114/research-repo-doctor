# Pre-commit hook

Use a local pre-commit hook when you want `rrdoctor` to catch reproducibility issues before changes leave your machine.

Install `pre-commit` and make sure `rrdoctor` is available in the same environment:

```bash
python -m pip install pre-commit rrdoctor
```

Add this `.pre-commit-config.yaml` to the repository you want to scan:

```yaml
repos:
  - repo: local
    hooks:
      - id: rrdoctor
        name: Research Repo Doctor
        entry: rrdoctor scan . --fail-on error
        language: system
        pass_filenames: false
```

For a softer local check that never blocks commits, use `--fail-on none` instead:

```yaml
entry: rrdoctor scan . --fail-on none
```

Run the hook manually:

```bash
pre-commit run rrdoctor --all-files
```

The hook uses local commands only. It does not require API keys, network access, or a hosted service.

Large repositories, notebook-heavy projects, or repositories with generated artifacts can make full scans too slow for every commit. In those cases, keep `--fail-on none` locally for visibility and run a stricter `--fail-on error` or `--fail-on warning` scan in CI.
