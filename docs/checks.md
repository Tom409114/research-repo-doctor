# Checks

Rules are deterministic and local-first. Severity can be overridden in `.rrdoctor.yml`.
Rules marked auto-fix can be scaffolded with `rrdoctor fix --write`; the rest are
covered by the agent fix plan (`rrdoctor plan`).

| ID | Name | Category | Severity | Profiles | Auto-fix |
| --- | --- | --- | --- | --- | --- |
| RRD001 | README missing | documentation | error | minimal, standard, strict, ml |  |
| RRD002 | README lacks installation/setup section | documentation | warning | minimal, standard, strict, ml |  |
| RRD003 | README lacks quickstart or usage section | documentation | warning | minimal, standard, strict, ml |  |
| RRD004 | README lacks reproducibility section | reproducibility | warning | minimal, standard, strict, ml |  |
| RRD010 | LICENSE missing | governance | error | minimal, standard, strict, ml | yes |
| RRD011 | CONTRIBUTING guide missing | governance | warning | strict | yes |
| RRD012 | SECURITY policy missing | governance | warning | strict | yes |
| RRD013 | CODE_OF_CONDUCT missing | governance | info | strict | yes |
| RRD014 | Agent/contributor task guide (AGENTS.md) missing | governance | info | strict | yes |
| RRD020 | Citation instructions missing | citation | warning | standard, strict, ml | yes |
| RRD021 | Paper metadata not documented | citation | warning | standard, strict, ml |  |
| RRD030 | No dependency manifest found | environment | error | minimal, standard, strict, ml |  |
| RRD031 | Dependency manifest lacks version hint | environment | warning | minimal, standard, strict, ml |  |
| RRD032 | Dockerfile or devcontainer missing | environment | info | strict |  |
| RRD033 | Unpinned dependencies in requirements file | environment | warning | standard, strict, ml |  |
| RRD034 | Imported package not in dependency manifest | environment | warning | standard, strict, ml |  |
| RRD040 | Data availability documentation missing | data | error | minimal, standard, strict, ml | yes |
| RRD041 | data directory lacks README | data | warning | standard, strict, ml | yes |
| RRD042 | Large data files detected | data | warning | standard, strict, ml |  |
| RRD043 | Potential local absolute data path detected | data | warning | standard, strict, ml |  |
| RRD050 | No experiment entrypoint found | experiments | error | minimal, standard, strict, ml |  |
| RRD051 | No configuration files found | experiments | warning | ml |  |
| RRD052 | Unseeded randomness in Python code | reproducibility | warning | standard, strict, ml | yes |
| RRD053 | Results provenance documentation missing | experiments | warning | standard, strict, ml | yes |
| RRD054 | Hardcoded GPU/CUDA assumption without a documented requirement | reproducibility | warning | ml |  |
| RRD060 | Notebook files detected with large outputs | notebooks | warning | standard, strict, ml |  |
| RRD061 | Notebook execution counts appear out of order | notebooks | warning | standard, strict, ml |  |
| RRD062 | Notebook contains absolute local paths | notebooks | warning | standard, strict, ml |  |
| RRD063 | Notebook contains possible secret-like output | security | error | standard, strict, ml |  |
| RRD064 | Notebook has no paired script or execution instructions | notebooks | info | strict |  |
| RRD065 | Jupyter checkpoint artifacts committed | notebooks | warning | standard, strict, ml |  |
| RRD070 | No tests directory or test files found | testing | warning | standard, strict, ml |  |
| RRD071 | No test runner/configuration detected | testing | warning | standard, strict, ml |  |
| RRD080 | No CI workflow detected | ci | warning | standard, strict, ml |  |
| RRD081 | CI lacks obvious test or lint step | ci | warning | standard, strict, ml |  |
| RRD082 | No pre-commit configuration found | ci | info | strict |  |
| RRD090 | Potential committed secret detected | security | error | standard, strict, ml |  |
| RRD091 | .gitignore missing common research artifacts | security | warning | standard, strict, ml | yes |
| RRD100 | CHANGELOG missing | release | info | standard, strict, ml | yes |
| RRD101 | No version metadata found | release | info/warning | standard, strict, ml |  |
| RRD102 | No release or packaging workflow found | release | info | strict |  |
| RRD110 | Python project metadata incomplete | metadata | warning | standard, strict, ml |  |
| RRD111 | Repository lacks topic/keyword guidance in README | metadata | info | standard, strict, ml |  |

This table is verified against the rule registry by the test suite, so it stays in
sync with the code.

`RRD020` accepts `CITATION.cff`, `CITATION.md`, or README citation evidence such
as Citing sections, "please cite" text, BibTeX entries, DOI fields, or DOI links.

`RRD004` accepts explicit Reproducibility/Results/Replicate sections as well as
concrete training, evaluation, benchmark, workflow, or reproduction commands such
as `python train.py`, `python eval.py`, `make reproduce`, `snakemake`, or
`nextflow run ...`.

`RRD050` recognizes common research entrypoints including root-level `train.py`,
`main.py`, `run.py`, `demo.py`, `inference.py`, `sample.py`, `generate.py`,
`predict.py`, `main_*.py`/`main-*.py`, `scripts/`, and ML-style
`tools/train.py` or `tools/test.py` entrypoints, README-documented
`python scripts/*.py` or `python tools/*.py` commands, README-documented
`python -m package.train` commands, pyproject-declared console scripts shown in
the README, explicit artifact verify/smoke scripts, `cargo run/test/bench`,
eval/reproduce/demo/inference scripts, Make targets,
Snakemake/Nextflow workflow files, and README commands such as
`python train.py ...`. Reusable library or framework projects with
standard package metadata, docs/tests/examples structure, and library-oriented
README language are not treated as missing a paper experiment entrypoint. Common
monorepo-style library layouts with package metadata under `package/` are also
recognized.

`RRD030` treats a lockable dependency manifest as the strongest evidence. It
recognizes Python, JavaScript, R, Julia, and Rust manifests, plus CMake, Meson,
Conan, vcpkg, Docker, and Nix environment definitions. If no manifest exists but
the README contains concrete install commands, the finding is downgraded to a
warning rather than an error. Root manifests and common nested package manifests
such as `package/pyproject.toml` are both recognized.

`RRD031` also reads dedicated runtime pins such as `.python-version`, `.nvmrc`,
and `rust-toolchain.toml`. A container base tagged `latest` is not treated as a
runtime version pin.

`RRD034` uses Python AST import statements rather than regex text matching, so
comments, docstrings, notebooks, and prose examples are not treated as imports.
It focuses on runtime-like source paths and skips conventional docs, tests,
benchmarks, test configuration, vendored code, and build/tooling folders. Local
sibling modules and package modules are treated as repository code, not missing
third-party distributions. It is still a conservative static dependency-gap
check: optional imports may need maintainer review before being considered
actionable for a specific project.

`RRD040` accepts dedicated data docs and README-based evidence, including common
dataset sections and documented `python data/.../prepare.py` style preparation
commands.

`RRD043` and notebook path rule `RRD062` ignore obvious documentation
placeholders such as `/home/user/absolute_path_to_the_output_dir`, URL path
segments that merely contain `/home/`, CI/devcontainer paths, test fixtures, and
common example-user paths such as `/Users/Me/...` or `/home/joe/...`, system
install locations such as `C:\Program Files\...`, and escaped Windows path
examples such as `C:\\folder1\\folder2`. Raw notebook output JSON is skipped by
RRD043 so traceback paths do not look like data locations; notebook source
cells remain covered by `RRD062`. The rule still flags machine-specific
personal home-directory paths in source or docs.

`RRD063` and `RRD090` are intentionally conservative. Generic `token`,
`api_key`, `secret`, or `password` text must be paired with a credential-like
random value with enough character diversity and entropy before it is reported;
canonical UUID values are treated as public identifiers, public URL query
`token=` values, low-entropy placeholder strings, local function-call or
method-call token variables, and generic fake tokens in test/fixture paths are
ignored.
Provider-like keys still need a token boundary, so an `AKIA...` substring inside
a longer biological/test sequence is not treated as a standalone AWS key, while
known standalone provider key prefixes are still flagged.

`RRD091` is likewise conservative: an existing `.gitignore` only needs basic
coverage across generated outputs, credential files, notebook checkpoints, or
language caches. It does not require every project to ignore optional tool
folders such as `wandb` or `mlruns`.

`RRD100` is informational in the standard profiles. Changelogs help package
users and release maintainers, but a missing changelog is not treated as a core
research-artifact reproducibility blocker.

`RRD101` accepts package version fields, a `VERSION` file, or local git tags as
version evidence. The scan stays network-free and does not query GitHub
releases. It is informational in standard/ML scans and a warning in strict or
submission profiles.
