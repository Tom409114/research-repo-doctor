# GitHub Copilot Instructions

Use rrdoctor as the deterministic, key-free grader for reproducibility work in
this research repository. Copilot can edit files, but rrdoctor defines whether
the work is done. Do not weaken rrdoctor checks, remove evidence, or hide files
only to make a scan pass.

Start by capturing the baseline:

```bash
uvx rrdoctor scan . --format json --output baseline.json --fail-on none
uvx rrdoctor plan . --output plan.md
```

Work through `plan.md` in small, reviewable changes. Prioritize high-signal
Artifact Evaluation blockers:

- missing setup, run, or verification commands;
- missing dependency/runtime metadata;
- local-only data paths or unclear data availability;
- missing citation, license, results, or data provenance;
- stale notebook outputs or notebook outputs with high-confidence secrets;
- random seed flags that do not actually seed randomness;
- missing tests, CI, or smoke commands.

The definition of done is:

```bash
uvx rrdoctor scan . --baseline baseline.json --fail-on-new error
```

If the final command reports a new error, keep fixing and re-run it. Explain any
remaining findings that require human judgement.

Static rrdoctor scans are safe for untrusted repositories: they do not install
dependencies, import target modules, build the project, execute notebooks, or
run repository scripts.

For repositories you trust, add the dynamic run-path gate:

```bash
uvx rrdoctor verify . --run --timeout 600 --fail-on error
```

If the artifact has an official quickstart command, pin it explicitly:

```bash
uvx rrdoctor verify . --command "python train.py config/default.py" --run --timeout 600 --fail-on error
```

Never run dynamic verification on untrusted code.
