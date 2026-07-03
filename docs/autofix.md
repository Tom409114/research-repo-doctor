# Auto-fix

`rrdoctor fix` applies deterministic, idempotent scaffolding for the most common
reproducibility gaps. It never overwrites existing files, never makes network
calls, and never executes code from the scanned repository.

## Preview, then apply

The default invocation is a dry-run that shows what would change:

```bash
rrdoctor fix .
```

Apply the changes with `--write`:

```bash
rrdoctor fix . --write --author "Your Lab" --project-name "my-project"
```

If `--author` or `--project-name` is omitted, `rrdoctor` tries to infer sensible
values from `pyproject.toml` and the local git remote. Generated citation
metadata can include the project name, version, release date, author, and
repository URL when those are already available locally.

Re-run the scan to confirm the score improved, then review the diff before
committing. Because fixers are idempotent, running them again is safe.

## What can be auto-fixed

| Rule | Scaffold created |
| --- | --- |
| RRD010 | `LICENSE` (MIT template) |
| RRD011 | `CONTRIBUTING.md` |
| RRD012 | `SECURITY.md` |
| RRD013 | `CODE_OF_CONDUCT.md` |
| RRD014 | `AGENTS.md` |
| RRD020 | `CITATION.cff` |
| RRD040 | `DATA.md` |
| RRD041 | `data/README.md` (only when `data/` exists) |
| RRD053 | `results/README.md` (only when `results/` exists) |
| RRD091 | `.gitignore` (creates or appends research artifacts) |
| RRD100 | `CHANGELOG.md` |

Generated files are starting points. They contain placeholders (for example, the
DOI in `CITATION.cff`) that you should complete before a release.

## What is intentionally not auto-fixed

Anything that requires judgement - the actual content of a README reproducibility
section, removing a committed secret, pinning a specific dependency version - is
left to a human or a coding agent. Use `rrdoctor plan` to get a tool-agnostic work
order for those tasks. See [agent workflows](agent-workflows.md).

## Scope a fix run

Restrict to specific rules with `--only`:

```bash
rrdoctor fix . --write --only RRD012,RRD100
```
