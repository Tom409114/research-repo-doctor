"""Artifact Appendix and submission-checklist mapping.

Turns a deterministic scan into the artifacts a researcher actually needs at a
submission deadline: an ACM-style Artifact Appendix skeleton and a table that
maps rrdoctor findings to the ACM badge tiers and the NeurIPS reproducibility
checklist. This is the "bind to the painful moment" layer.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from rrdoctor.models import ScanReport
from rrdoctor.rules.base import read_text
from rrdoctor.verification import _entrypoint_command

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

# Rule IDs whose *failure* blocks a given ACM Artifact Evaluation badge tier.
# Badges are cumulative: Functional implies Available, Reproduced implies Functional.
ACM_BADGE_RULES: dict[str, tuple[str, ...]] = {
    "Artifact Available": ("RRD010", "RRD020", "RRD021", "RRD100", "RRD101"),
    "Artifact Functional": ("RRD001", "RRD002", "RRD030", "RRD031", "RRD034", "RRD050"),
    "Results Reproduced": ("RRD004", "RRD040", "RRD051", "RRD052", "RRD053", "RRD054"),
}

# NeurIPS-style reproducibility checklist items mapped to the rule IDs that
# provide evidence for them.
NEURIPS_CHECKLIST: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Code is provided with instructions to reproduce the main results", ("RRD002", "RRD050")),
    ("All training/eval details and dependencies are specified", ("RRD030", "RRD031", "RRD034")),
    ("Random seeds and sources of randomness are reported", ("RRD052",)),
    ("Compute resources (GPU/CUDA) are described", ("RRD054",)),
    ("Data is documented and access is described", ("RRD040", "RRD041")),
    ("Results provenance is recorded", ("RRD053",)),
    ("A license is included", ("RRD010",)),
)

DEPENDENCY_MANIFESTS = (
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "environment.yml",
    "conda.yml",
    "Pipfile",
    "poetry.lock",
    "uv.lock",
    "renv.lock",
    "DESCRIPTION",
    "Project.toml",
    "Manifest.toml",
    "package.json",
    "Dockerfile",
    ".devcontainer/devcontainer.json",
)
DATA_DOCS = ("DATA.md", "docs/data.md", "data/README.md")
RESULTS_DOCS = ("results/README.md", "RESULTS.md", "docs/results.md")
CONFIG_SUFFIXES = {".yaml", ".yml", ".json", ".toml"}


@dataclass(frozen=True)
class TierStatus:
    """Readiness of a single badge tier."""

    name: str
    blocking_rule_ids: list[str]

    @property
    def ready(self) -> bool:
        return not self.blocking_rule_ids


@dataclass(frozen=True)
class AppendixEvidence:
    """Local static evidence used to pre-fill the artifact appendix."""

    repo_name: str
    description: str | None = None
    repository_url: str | None = None
    release_doi: str | None = None
    entrypoint: str | None = None
    dependency_manifests: tuple[str, ...] = ()
    data_docs: tuple[str, ...] = ()
    results_docs: tuple[str, ...] = ()
    config_files: tuple[str, ...] = ()
    runtime_hint: str | None = None


def _failed_rule_ids(report: ScanReport) -> set[str]:
    """Rule IDs that produced an error or warning finding."""

    return {f.rule_id for f in report.findings if f.severity.value in ("error", "warning")}


def badge_status(report: ScanReport) -> list[TierStatus]:
    """Compute per-tier readiness from a scan report."""

    failed = _failed_rule_ids(report)
    tiers: list[TierStatus] = []
    for name, rule_ids in ACM_BADGE_RULES.items():
        blocking = [rid for rid in rule_ids if rid in failed]
        tiers.append(TierStatus(name=name, blocking_rule_ids=blocking))
    return tiers


def render_checklist(report: ScanReport) -> str:
    """Render the ACM/NeurIPS mapping table as Markdown."""

    failed = _failed_rule_ids(report)
    repo_name = PurePosixPath(report.repository_path.replace("\\", "/").rstrip("/")).name
    lines = [
        "# Submission readiness - checklist mapping",
        "",
        f"- Repository: `{repo_name or report.repository_path}`",
        f"- Profile: `{report.profile}`",
        f"- Artifact readiness: **{report.readiness.level}**",
        f"- Heuristic score: **{report.score}/100**",
        "",
        "## ACM Artifact Evaluation badges",
        "",
        "| Badge | Status | Blocking checks |",
        "| --- | --- | --- |",
    ]
    for tier in badge_status(report):
        status = "ready" if tier.ready else "action needed"
        blocking = ", ".join(tier.blocking_rule_ids) if tier.blocking_rule_ids else "-"
        lines.append(f"| {tier.name} | {status} | {blocking} |")

    lines.extend(
        [
            "",
            "## NeurIPS reproducibility checklist",
            "",
            "| Item | Status | Evidence checks |",
            "| --- | --- | --- |",
        ]
    )
    for item, rule_ids in NEURIPS_CHECKLIST:
        blocking_ids = [rid for rid in rule_ids if rid in failed]
        status = "OK" if not blocking_ids else "TODO"
        evidence = ", ".join(rule_ids)
        lines.append(f"| {item} | {status} | {evidence} |")

    lines.extend(
        [
            "",
            "> Mapping is heuristic. An OK means rrdoctor found no blocking issue for that "
            "item; it does not certify the artifact. Reviewers make the final call.",
            "",
        ]
    )
    return "\n".join(lines)


def _badge_summary(report: ScanReport) -> str:
    ready = [t.name for t in badge_status(report) if t.ready]
    if not ready:
        return "No tier is clear yet - see the blocking checks below."
    return "On track for: " + ", ".join(ready) + "."


def _appendix_evidence(report: ScanReport) -> AppendixEvidence:
    repo_name = PurePosixPath(report.repository_path.replace("\\", "/").rstrip("/")).name
    root = Path(report.repository_path)
    if not root.exists():
        return AppendixEvidence(repo_name=repo_name)

    metadata = _read_project_metadata(root)
    citation = _read_citation_metadata(root)
    entrypoint = _entrypoint_command(root)[1] or None
    return AppendixEvidence(
        repo_name=repo_name,
        description=metadata.get("description") or _readme_summary(root),
        repository_url=metadata.get("repository_url") or citation.get("repository_url"),
        release_doi=citation.get("doi"),
        entrypoint=entrypoint,
        dependency_manifests=_existing_paths(root, DEPENDENCY_MANIFESTS),
        data_docs=_existing_paths(root, DATA_DOCS),
        results_docs=_existing_paths(root, RESULTS_DOCS),
        config_files=_config_files(root),
        runtime_hint=metadata.get("requires_python"),
    )


def _read_project_metadata(root: Path) -> dict[str, str]:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return {}
    try:
        parsed = tomllib.loads(read_text(pyproject))
    except tomllib.TOMLDecodeError:
        return {}
    project = _as_mapping(parsed.get("project"))
    metadata: dict[str, str] = {}
    for key, target in (
        ("description", "description"),
        ("requires-python", "requires_python"),
    ):
        value = project.get(key)
        if isinstance(value, str) and value.strip():
            metadata[target] = value.strip()
    urls = _as_mapping(project.get("urls"))
    normalized_urls = {str(key).lower(): value for key, value in urls.items()}
    for key in ("repository", "source", "code", "homepage"):
        value = normalized_urls.get(key)
        if isinstance(value, str) and value.strip():
            metadata["repository_url"] = value.strip()
            break
    return metadata


def _read_citation_metadata(root: Path) -> dict[str, str]:
    citation = root / "CITATION.cff"
    if not citation.exists():
        return {}
    text = read_text(citation)
    metadata: dict[str, str] = {}
    doi = re.search(r"(?im)^doi:\s*[\"']?(?P<value>10\.\S+?)[\"']?\s*$", text)
    if doi:
        metadata["doi"] = doi.group("value").rstrip(".,;")
    repository = re.search(
        r"(?im)^repository-code:\s*[\"']?(?P<value>https?://\S+?)[\"']?\s*$", text
    )
    if repository:
        metadata["repository_url"] = repository.group("value").rstrip(".,;")
    return metadata


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _readme_summary(root: Path) -> str | None:
    readme = root / "README.md"
    if not readme.exists():
        return None
    lines = read_text(readme).splitlines()
    paragraphs: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith("#") or stripped.startswith("![") or not stripped:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs[0] if paragraphs else None


def _existing_paths(root: Path, candidates: tuple[str, ...]) -> tuple[str, ...]:
    paths = [candidate for candidate in candidates if (root / candidate).exists()]
    return tuple(paths)


def _config_files(root: Path) -> tuple[str, ...]:
    candidates: list[str] = []
    for directory in ("config", "configs"):
        base = root / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in CONFIG_SUFFIXES:
                candidates.append(path.relative_to(root).as_posix())
            if len(candidates) >= 8:
                return tuple(candidates)
    return tuple(candidates)


def _format_paths(paths: tuple[str, ...]) -> str:
    return ", ".join(f"`{path}`" for path in paths)


def _abstract(evidence: AppendixEvidence) -> str:
    if evidence.description:
        return (
            f"This artifact package contains `{evidence.repo_name}`, described locally as: "
            f"{evidence.description} TODO: connect this package to the specific paper claims "
            "it supports."
        )
    return (
        f"This artifact package contains `{evidence.repo_name}`. TODO: add one paragraph "
        "describing which paper claims it supports."
    )


def _program_summary(evidence: AppendixEvidence) -> str:
    if evidence.entrypoint:
        return f"`{evidence.repo_name}`; primary run command detected as `{evidence.entrypoint}`."
    return f"`{evidence.repo_name}`; TODO: name the primary executable or notebook."


def _environment_summary(evidence: AppendixEvidence, fallback: str) -> str:
    parts: list[str] = []
    if evidence.runtime_hint:
        parts.append(f"runtime `{evidence.runtime_hint}`")
    if evidence.dependency_manifests:
        parts.append(f"manifests {_format_paths(evidence.dependency_manifests)}")
    if parts:
        return "Declared " + "; ".join(parts) + "."
    return fallback


def _docs_summary(paths: tuple[str, ...], satisfied: str, missing: str) -> str:
    if paths:
        return f"See {_format_paths(paths)}."
    return satisfied if satisfied.startswith("TODO:") else satisfied or f"TODO: {missing}"


def render_appendix(report: ScanReport) -> str:
    """Render an ACM-style Artifact Appendix skeleton, pre-filled where possible.

    Sections rrdoctor cannot infer are left as explicit TODOs so the author fills
    them in rather than shipping blanks.
    """

    failed = _failed_rule_ids(report)
    evidence = _appendix_evidence(report)

    def todo_if(rule_id: str, satisfied: str, missing: str) -> str:
        return satisfied if rule_id not in failed else f"TODO: {missing}"

    lines = [
        "# Artifact Appendix",
        "",
        "<!-- Generated by rrdoctor. Edit before submitting; TODOs mark gaps the",
        "     scanner could not fill automatically. -->",
        "",
        "## Abstract",
        "",
        _abstract(evidence),
        "",
        "## Artifact check-list (meta-information)",
        "",
        "- **Algorithm:** "
        + (
            evidence.description
            if evidence.description
            else "TODO: name the algorithm, model, analysis, or workflow."
        ),
        "- **Program:** " + _program_summary(evidence),
        "- **Data set:** "
        + (
            f"See {_format_paths(evidence.data_docs)}."
            if evidence.data_docs
            else todo_if(
                "RRD040", "See documented data availability.", "describe datasets and access."
            )
        ),
        "- **Run-time environment:** "
        + _environment_summary(
            evidence,
            todo_if(
                "RRD030", "Declared dependency manifest is present.", "list OS and dependencies."
            ),
        ),
        "- **Hardware:** "
        + todo_if(
            "RRD054",
            "No hardcoded GPU/CUDA blocker detected; confirm CPU/GPU requirements.",
            "state required GPU/CUDA, if any.",
        ),
        "- **Metrics:** "
        + (
            f"See {_format_paths(evidence.results_docs)}."
            if evidence.results_docs
            else "TODO: list the metrics, figures, tables, or checksums to compare."
        ),
        "- **Output:** "
        + (
            f"See {_format_paths(evidence.results_docs)}."
            if evidence.results_docs
            else todo_if("RRD053", "Results provenance is recorded.", "describe expected outputs.")
        ),
        "- **Experiments:** "
        + (
            f"`{evidence.entrypoint}`"
            if evidence.entrypoint
            else todo_if(
                "RRD050", "Experiment entrypoint is present.", "name the reproduction entrypoint."
            )
        ),
        "- **How much disk space required (approximately)?:** TODO",
        "- **How much time is needed to prepare workflow (approximately)?:** TODO",
        "- **How much time is needed to complete experiments (approximately)?:** TODO",
        "- **Publicly available?:** "
        + todo_if("RRD010", "Yes - license included.", "add a license before archiving."),
        "- **Archived (provide DOI)?:** "
        + (
            f"`{evidence.release_doi}`"
            if evidence.release_doi
            else "TODO: deposit on Zenodo/Figshare/Dryad and add the DOI."
        ),
        "",
        "## Description",
        "",
        "### How to access",
        "",
        (
            f"Repository URL: <{evidence.repository_url}>."
            if evidence.repository_url
            else todo_if(
                "RRD101",
                "Tagged release / version metadata is available.",
                "tag a release and archive it for a citable DOI.",
            )
        ),
        "",
        "### Hardware dependencies",
        "",
        todo_if("RRD054", "Documented in the README.", "state CPU/GPU/CUDA requirements."),
        "",
        "### Software dependencies",
        "",
        _environment_summary(
            evidence,
            todo_if(
                "RRD031",
                "Runtime version and dependency manifest are documented.",
                "pin a runtime version and list dependencies.",
            ),
        ),
        "",
        "### Data sets",
        "",
        _docs_summary(
            evidence.data_docs,
            todo_if(
                "RRD040",
                "Data availability is documented.",
                "document datasets and how to obtain them.",
            ),
            "document datasets and how to obtain them.",
        ),
        "",
        "### Models",
        "",
        "TODO: Describe any pretrained models/weights and where to obtain them.",
        "",
        "## Installation",
        "",
        (
            "See `README.md`"
            + (
                f" and dependency manifest(s) {_format_paths(evidence.dependency_manifests)}."
                if evidence.dependency_manifests
                else "."
            )
            if "RRD002" not in failed
            else todo_if(
                "RRD002",
                "See the README setup section.",
                "add setup/installation steps to the README.",
            )
        ),
        "",
        "## Experiment workflow",
        "",
        (
            f"Run `{evidence.entrypoint}`."
            if evidence.entrypoint
            else todo_if(
                "RRD050",
                "Run the documented experiment entrypoint.",
                "document how to run experiments.",
            )
        ),
        (
            "Configuration files detected: " + _format_paths(evidence.config_files) + "."
            if evidence.config_files
            else ""
        ),
        "",
        "## Evaluation and expected results",
        "",
        (
            f"See {_format_paths(evidence.results_docs)} for result provenance."
            if evidence.results_docs
            else todo_if(
                "RRD004",
                "See the README reproducibility section for expected results.",
                "describe the key results to reproduce and tolerances.",
            )
        ),
        "",
        "## Notes",
        "",
        f"_{_badge_summary(report)}_",
        "",
    ]
    return "\n".join(lines)
