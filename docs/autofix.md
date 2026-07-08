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
metadata can include the project name, version, release date, multiple authors,
and repository URL when those are already available locally. PEP 621
`[project]` metadata and Poetry `[tool.poetry]` metadata are both supported, and
git worktree remotes are recognized without running repository code.

Generated data-provenance notes also include local evidence when it exists:
top-level data directories, likely data download or preprocessing scripts, and
README data/access mentions. When the README already contains likely dataset
URLs, DOIs, or data/download commands, those are copied into the scaffold as
candidate source and retrieval entries for review. rrdoctor does not infer the
actual dataset license or access terms; it gives maintainers a better starting
point to verify.

Generated results-provenance notes include the project name, repository URL,
current git commit when it can be read locally, existing `results/` contents,
and a table for commands, data snapshots, code commits, and validation notes.

Generated `AGENTS.md` files include the rrdoctor agent repair loop:
`scan --format json --output baseline.json`, `plan --output plan.md`, and the
final `scan --baseline baseline.json --fail-on-new error` gate. They also call
out that `verify --run` is optional and only for trusted repositories.

When unseeded randomness is detected, rrdoctor can scaffold a small
`set_global_seed(seed: int)` helper. It does not edit your training script; the
generated file includes a TODO showing where to import and call the helper.

Review the diff before committing, then re-run the scan after wiring any starter
code into the project. Some scaffolds, such as the seed helper, are intentionally
only starting points and clear the finding only after you import and call them.
Because fixers are idempotent, running them again is safe.

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
| RRD052 | `src/<package>/_repro_seed.py` or `repro_seed.py` |
| RRD053 | `results/README.md` (only when `results/` exists) |
| RRD091 | `.gitignore` (creates or appends research artifacts) |
| RRD100 | `CHANGELOG.md` |

Generated files are starting points. They contain placeholders (for example, a
DOI in `CITATION.cff` when one is not already documented) that you should
complete before a release.

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
