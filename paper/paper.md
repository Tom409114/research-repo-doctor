---
title: "Research Repo Doctor: deterministic artifact-readiness checks for research repositories"
tags:
  - Python
  - reproducible research
  - artifact evaluation
  - research software
  - continuous integration
authors:
  - name: Research Repo Doctor Maintainers
    affiliation: 1
affiliations:
  - name: Independent open-source maintainers
    index: 1
date: 6 July 2026
bibliography: paper.bib
---

# Summary

Research Repo Doctor (`rrdoctor`) is a Python command line tool and GitHub Action
for preparing research code repositories for public release, Artifact Evaluation,
and reproducibility review. It performs deterministic, local-first checks for
common release blockers: missing dependency metadata, local-only data paths,
undocumented experiment entrypoints, unreproducible randomness, stale notebook
outputs, missing citation metadata, weak release hygiene, and absent continuous
integration. The tool reports an Artifact Evaluation-style readiness level,
generates an actionable fix plan, scaffolds safe non-destructive starter files,
and can produce an ACM-style Artifact Appendix skeleton.

The core scanner is static and network-free. It does not install, import, build,
or execute a target repository. For trusted repositories, a separate
`rrdoctor verify --run` mode adds dynamic evidence by resolving dependencies and
running a declared entrypoint under a timeout. This split lets maintainers use
the default audit on untrusted code while still supporting the higher-value
question researchers face before submission: whether the documented run path can
actually be exercised.

# Statement of need

Research artifacts often reach GitHub under deadline pressure. Reviewers and
future users then discover that setup commands are incomplete, dependencies are
unpinned, data instructions refer to private locations, notebooks contain hidden
state, or the paper does not clearly describe how to cite and rerun the code.
These are not always scientific errors, but they are practical blockers for
artifact review and reuse.

Existing community standards describe what good artifacts should contain.
The FAIR principles emphasize findability, accessibility, interoperability, and
reuse for data and related digital objects [@wilkinson2016fair]. ACM artifact
badging defines availability, functionality, and reusability expectations for
research artifacts [@acm_artifact_badging]. Machine learning venues have also
introduced reproducibility programs and checklists to improve reporting quality
[@pineau2021reproducibility]. These standards are useful, but authors still need
a concrete, repeatable way to check a repository before a deadline.

`rrdoctor` fills that operational gap. It converts reproducibility expectations
into deterministic repository checks, safe starter fixes, a machine-readable
report, a maintainer plan, and CI gates. The intended users are research software
maintainers, students preparing artifact submissions, lab engineers helping
others package code, and reviewers who want a fast triage report before deeper
manual inspection.

# State of the field

Several tools and practices address neighboring parts of this problem. JOSS
itself provides a public review process for research software quality and credit
[@smith2018joss]. Tools such as `howfairis` check FAIR software indicators for
repositories [@howfairis]. Artifact Evaluation policies and venue checklists
define the target expectations [@acm_artifact_badging; @pineau2021reproducibility].

`rrdoctor` differs by treating Artifact Evaluation readiness as a maintainer
workflow rather than only a metadata checklist. It combines rule-based static
analysis, profile-specific expectations, non-destructive autofix scaffolds,
baseline-aware regression gating, an agent-ready fix plan, an appendix generator,
and an optional verification ladder. The project is intentionally conservative:
when evidence is ambiguous, rules are expected to avoid high-severity findings
until a fixture or corpus case supports the behavior.

# Software design

The scanner is organized around stable rule identifiers, categories, severities,
messages, and remediation text. Rules operate on repository files and return
findings without relying on network services or hosted APIs. Profiles select
different expectations for general research repositories, machine learning paper
code, FAIR-for-research-software checks, JOSS readiness, and ACM/NeurIPS-style
artifact preparation.

Reports can be emitted as Markdown, JSON, SARIF-like JSON, a Shields.io badge
endpoint, or an agent-oriented plan. The same findings feed the command line,
GitHub Action summaries, sticky pull request comments, the artifact appendix,
and MCP tooling for coding agents. This design keeps the scanner deterministic
while allowing different consumers to use the same evidence.

Autofixes follow a non-destructive contract. They may create missing starter
files, but they do not overwrite existing files. Generated content is explicitly
a scaffold: maintainers must fill in real data provenance, citation details, and
experiment context. Dynamic verification is similarly separated from static
scanning. `rrdoctor verify` can summarize the L1/L2/L3 ladder without execution,
while `rrdoctor verify --run` is reserved for trusted repositories because it
resolves dependencies and runs target code.

# Research impact statement

`rrdoctor` is designed to improve the handoff quality of research code before
artifact review, public archival, or lab-to-lab reuse. The current release
provides a tested Python package, a GitHub Action, rule documentation, example
reports, an evaluation corpus workflow for public repositories, agent-integration
templates for deterministic coding-agent review loops, and a Zenodo archive DOI.
The project does not claim external adoption in this draft. Its
near-term significance is that it provides a concrete, repeatable artifact
readiness gate that can be used by individual maintainers and evaluated against
public research repositories.

The broader research value is measurement. Because reports are deterministic
and machine-readable, `rrdoctor` can support corpus studies of repository
readiness patterns across fields, venues, or time. Those studies can identify
which release blockers are common enough to warrant better tooling, reviewer
guidance, or venue policy.

# AI usage disclosure

Generative AI tools have been used during development and documentation drafting
for this project. Maintainer-facing changes are reviewed through source control,
tests, linting, self-scans, and manual inspection before release. The released
scanner itself does not call AI services, require an API key, or send target
repository contents to a hosted model. Its user-facing findings are produced by
deterministic local rules.

# Acknowledgements

This draft acknowledges the open reproducible research, Artifact Evaluation, and
research software review communities whose policies and checklists shaped the
project's scope. No external funding is claimed in this draft.

# References
