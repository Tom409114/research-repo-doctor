# Pre-commit Hook Integration

Research Repo Doctor can run as a pre-commit hook so you catch reproducibility issues before committing changes to a research repository.

## Example configuration

Add a `.pre-commit-config.yaml` file to your repository:

```yaml
repos:
  - repo: local
    hooks:
      - id: rrdoctor
        name: Research Repo Doctor
        entry: rrdoctor scan .
        language: system
        pass_filenames: false
        args: [--fail-on, error]
```

## Choosing a `--fail-on` level

| Value     | Behavior                                      | Recommended for         |
|-----------|-----------------------------------------------|-------------------------|
| `none`    | Always passes, shows report only              | Local exploration       |
| `error`   | Fails only on errors                          | Pre-commit (recommended)|
| `warning` | Fails on warnings and errors                  | CI pipelines            |

For pre-commit use, `--fail-on error` is recommended. Using `--fail-on warning` on every commit may create friction for active development.

## Large repositories

For repositories with many files, a full `rrdoctor scan` on every commit may feel slow. In that case, consider running rrdoctor only in CI rather than as a pre-commit hook. See [GitHub Action integration](github-action.md) for details.

## Prerequisites

- `rrdoctor` must be installed in the environment where pre-commit runs: `pip install rrdoctor`
- Install pre-commit itself: `pip install pre-commit`
- Activate the hooks: `pre-commit install`
