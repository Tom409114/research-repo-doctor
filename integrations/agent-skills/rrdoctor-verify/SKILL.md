---
name: rrdoctor-verify
description: Use rrdoctor as the deterministic, offline definition of done for preparing a research repository for Artifact Evaluation or public release.
---

# rrdoctor Verify Loop

Use this skill when a repository contains research code, notebooks, datasets,
model artifacts, or an Artifact Evaluation / reproducibility checklist.

rrdoctor is the grader. The coding agent is the editor. Do not weaken rrdoctor
checks to make the task pass.

## Baseline

Run a deterministic baseline scan:

```bash
uvx rrdoctor scan . --format json --output baseline.json
```

If `uvx` is unavailable but `rrdoctor` is installed, use:

```bash
rrdoctor scan . --format json --output baseline.json
```

## Plan

Generate a work order:

```bash
uvx rrdoctor plan . --output plan.md
```

Read `plan.md` and fix the highest-impact items first: missing run paths,
dependency metadata, local-only data paths, stale notebooks, citation/provenance
gaps, and randomness/seed issues.

Use `rrdoctor fix --write` only for safe scaffolding fixes. Generated files may
contain TODO placeholders that need human or agent completion.

## Definition Of Done

After editing, run:

```bash
uvx rrdoctor scan . --baseline baseline.json --fail-on-new error
```

Stop only when this command passes. If it reports a new error, keep working from
the finding and re-run the gate.

## Trusted Dynamic Gate

The default scan is static: it does not install, import, build, or execute target
repository code.

Only when the repository is trusted and the user wants dynamic evidence, run:

```bash
uvx rrdoctor verify . --run --timeout 600 --fail-on error
```

Treat this like running the repository yourself. Do not use it on arbitrary
untrusted repositories.

## Reporting Back

Summarize:

- the original readiness label and top findings,
- the files changed,
- the final baseline-gate result, and
- any remaining TODOs that require human judgment.
