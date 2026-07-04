"""Deterministic, idempotent auto-fixers for common reproducibility gaps.

Fixers create or extend small scaffolding files (governance docs, citation
metadata, data and results provenance notes, changelog, and ignore entries).
They never overwrite existing content, never make network calls, and never run
code from the scanned repository. Anything that requires human judgement (for
example, the actual content of a README reproducibility section) is intentionally
left to the agent fix plan instead.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

from rrdoctor.models import FixResult
from rrdoctor.rules.base import read_text
from rrdoctor.rules.security import COMMON_GITIGNORE_TERMS

DATA_HINT_DIR_NAMES = {
    "data",
    "datasets",
    "dataset",
    "inputs",
    "input",
    "raw",
    "processed",
}
DATA_SCRIPT_TERMS = (
    "download",
    "fetch",
    "prepare",
    "preprocess",
    "dataset",
    "data",
)
DATA_HINT_TEXT_RE = re.compile(
    r"(?i)\b(data availability|dataset|datasets|download|preprocess|zenodo|doi|kaggle)\b"
)
Metadata = dict[str, str | tuple[str, ...]]


@dataclass(frozen=True)
class FixContext:
    """Inputs that parameterise generated scaffolding."""

    root: Path
    project_name: str
    author: str
    year: int
    contact: str = "the maintainers (see repository profile)"
    repository_url: str | None = None
    version: str | None = None
    date_released: str | None = None
    authors: tuple[str, ...] = ()


def _write_if_missing(path: Path, content: str, rule_id: str, rel: str) -> FixResult:
    if path.exists():
        return FixResult(rule_id, rel, "skipped", f"{rel} already exists.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return FixResult(rule_id, rel, "created", f"Created {rel}.")


def infer_fix_context(
    root: Path,
    *,
    project_name: str | None = None,
    author: str | None = None,
    year: int | None = None,
) -> FixContext:
    """Infer useful scaffold metadata from local repository files."""

    metadata = _read_pyproject_metadata(root)
    inferred_name = project_name or _metadata_str(metadata, "name") or root.name
    metadata_authors = _metadata_authors(metadata)
    if author:
        inferred_authors = (author,)
        inferred_author = author
    elif metadata_authors:
        inferred_authors = metadata_authors
        inferred_author = ", ".join(metadata_authors)
    else:
        inferred_author = _metadata_str(metadata, "author") or f"{inferred_name} maintainers"
        inferred_authors = (inferred_author,)
    return FixContext(
        root=root,
        project_name=inferred_name,
        author=inferred_author,
        year=year or datetime.now(timezone.utc).year,
        repository_url=_metadata_str(metadata, "repository_url") or _read_git_origin_url(root),
        version=_metadata_str(metadata, "version"),
        date_released=datetime.now(timezone.utc).date().isoformat(),
        authors=inferred_authors,
    )


def _metadata_str(metadata: Metadata, key: str) -> str | None:
    value = metadata.get(key)
    return value if isinstance(value, str) else None


def _metadata_authors(metadata: Metadata) -> tuple[str, ...]:
    value = metadata.get("authors")
    return value if isinstance(value, tuple) else ()


def _read_pyproject_metadata(root: Path) -> Metadata:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return {}
    text = read_text(pyproject)
    try:
        parsed = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        pass
    else:
        metadata = _metadata_from_toml(parsed)
        if metadata:
            return metadata
    return _read_pyproject_metadata_fallback(text)


def _read_pyproject_metadata_fallback(text: str) -> Metadata:
    metadata: Metadata = {}
    for key in ("name", "version"):
        match = re.search(rf"(?m)^{key}\s*=\s*['\"]([^'\"]+)['\"]", text)
        if match:
            metadata[key] = match.group(1)
    author = re.search(r"(?s)authors\s*=\s*\[\s*\{\s*name\s*=\s*['\"]([^'\"]+)['\"]", text)
    if author:
        cleaned = _clean_author_name(author.group(1))
        if cleaned:
            metadata["author"] = cleaned
            metadata["authors"] = (cleaned,)
    urls = re.search(r"(?ms)^\[project\.urls\](.*?)(?:^\[|\Z)", text)
    if urls:
        for key in ("Repository", "Homepage"):
            match = re.search(rf"(?m)^{key}\s*=\s*['\"]([^'\"]+)['\"]", urls.group(1))
            if match:
                metadata["repository_url"] = _normalize_git_url(match.group(1))
                break
    return metadata


def _metadata_from_toml(data: dict[str, Any]) -> Metadata:
    metadata: Metadata = {}
    project = _as_mapping(data.get("project"))
    if project:
        _set_if_str(metadata, "name", project.get("name"))
        _set_if_str(metadata, "version", project.get("version"))
        authors = _author_names_from_entries(project.get("authors"))
        if authors:
            metadata["authors"] = authors
            metadata["author"] = ", ".join(authors)
        url = _url_from_mapping(project.get("urls"))
        if url:
            metadata["repository_url"] = url

    poetry = _as_mapping(_as_mapping(data.get("tool")).get("poetry")) if data.get("tool") else {}
    if poetry:
        if "name" not in metadata:
            _set_if_str(metadata, "name", poetry.get("name"))
        if "version" not in metadata:
            _set_if_str(metadata, "version", poetry.get("version"))
        if not _metadata_authors(metadata):
            authors = _author_names_from_entries(poetry.get("authors"))
            if authors:
                metadata["authors"] = authors
                metadata["author"] = ", ".join(authors)
        if "repository_url" not in metadata:
            url = _url_from_poetry(poetry)
            if url:
                metadata["repository_url"] = url

    return {key: value for key, value in metadata.items() if value}


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _set_if_str(metadata: Metadata, key: str, value: Any) -> None:
    cleaned = _clean_optional_str(value)
    if cleaned:
        metadata[key] = cleaned


def _clean_optional_str(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _author_names_from_entries(entries: Any) -> tuple[str, ...]:
    if not isinstance(entries, list):
        return ()
    names: list[str] = []
    for entry in entries:
        name: str | None = None
        if isinstance(entry, dict):
            name = _clean_optional_str(entry.get("name"))
        elif isinstance(entry, str):
            name = _clean_optional_str(entry)
        cleaned = _clean_author_name(name or "")
        if cleaned and cleaned not in names:
            names.append(cleaned)
    return tuple(names)


def _clean_author_name(name: str) -> str:
    return re.sub(r"\s*<[^>]+>\s*$", "", name).strip()


def _url_from_mapping(value: Any) -> str | None:
    urls = _as_mapping(value)
    normalized_keys = {str(key).lower(): val for key, val in urls.items()}
    for key in ("repository", "source", "code", "homepage"):
        url = _clean_optional_str(normalized_keys.get(key))
        if url:
            return _normalize_git_url(url)
    return None


def _url_from_poetry(poetry: dict[str, Any]) -> str | None:
    for key in ("repository", "homepage", "documentation"):
        url = _clean_optional_str(poetry.get(key))
        if url:
            return _normalize_git_url(url)
    return None


def _read_git_origin_url(root: Path) -> str | None:
    config = _git_config_path(root)
    if not config.exists():
        return None
    text = read_text(config)
    origin = re.search(r'(?ms)^\[remote "origin"\](.*?)(?:^\[|\Z)', text)
    if not origin:
        return None
    url = re.search(r"(?m)^\s*url\s*=\s*(\S+)\s*$", origin.group(1))
    if not url:
        return None
    return _normalize_git_url(url.group(1))


def _git_config_path(root: Path) -> Path:
    git_path = root / ".git"
    if git_path.is_dir():
        return git_path / "config"
    if git_path.is_file():
        match = re.search(r"(?im)^gitdir:\s*(.+?)\s*$", read_text(git_path))
        if match:
            git_dir = Path(match.group(1))
            if not git_dir.is_absolute():
                git_dir = (root / git_dir).resolve()
            return git_dir / "config"
    return git_path / "config"


def _normalize_git_url(url: str) -> str:
    ssh = re.match(r"git@([^:]+):(.+?)(?:\.git)?$", url)
    if ssh:
        return f"https://{ssh.group(1)}/{ssh.group(2)}"
    ssh_url = re.match(r"ssh://git@([^/]+)/(.+?)(?:\.git)?$", url)
    if ssh_url:
        return f"https://{ssh_url.group(1)}/{ssh_url.group(2)}"
    return url.removesuffix(".git")


# --- Templates ---------------------------------------------------------------


def _license_mit(ctx: FixContext) -> str:
    return (
        f"MIT License\n\n"
        f"Copyright (c) {ctx.year} {ctx.author}\n\n"
        "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
        'of this software and associated documentation files (the "Software"), to deal\n'
        "in the Software without restriction, including without limitation the rights\n"
        "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
        "copies of the Software, and to permit persons to whom the Software is\n"
        "furnished to do so, subject to the following conditions:\n\n"
        "The above copyright notice and this permission notice shall be included in all\n"
        "copies or substantial portions of the Software.\n\n"
        'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n'
        "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
        "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
        "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
        "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
        "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
        "SOFTWARE.\n"
    )


def _contributing(ctx: FixContext) -> str:
    return (
        f"# Contributing to {ctx.project_name}\n\n"
        "Thank you for helping make this research code easier to reproduce and reuse.\n\n"
        "## Development setup\n\n"
        "```bash\n"
        'python -m pip install -e ".[dev]"\n'
        "```\n\n"
        "## Before opening a pull request\n\n"
        "- Run the test suite and linters.\n"
        "- Keep changes focused and described in the pull request body.\n"
        "- Update documentation and the changelog when behaviour changes.\n\n"
        "## Reproducibility expectations\n\n"
        "- Document any new data, configuration, or environment requirements.\n"
        "- Prefer relative paths and configurable inputs over machine-specific paths.\n"
        "- Set and document random seeds for any new stochastic steps.\n"
    )


def _security(ctx: FixContext) -> str:
    return (
        "# Security Policy\n\n"
        "## Reporting a vulnerability\n\n"
        "Please do not open a public issue for suspected credential exposure or\n"
        "security vulnerabilities. Instead, contact "
        f"{ctx.contact} privately so the issue can be triaged and fixed.\n\n"
        "## Credentials\n\n"
        "Never commit API keys, tokens, or passwords. If a secret is exposed,\n"
        "rotate it immediately and remove it from history.\n"
    )


def _code_of_conduct(ctx: FixContext) -> str:
    return (
        "# Code of Conduct\n\n"
        "## Our pledge\n\n"
        "We pledge to make participation in this project a harassment-free experience\n"
        "for everyone, regardless of background or identity.\n\n"
        "## Our standards\n\n"
        "Examples of behaviour that contributes to a positive environment include using\n"
        "welcoming language, respecting differing viewpoints, and accepting constructive\n"
        "feedback gracefully.\n\n"
        "## Enforcement\n\n"
        f"Report unacceptable behaviour to {ctx.contact}. This Code of Conduct is\n"
        "adapted from the Contributor Covenant (https://www.contributor-covenant.org).\n"
    )


def _agents(ctx: FixContext) -> str:
    return (
        "# AGENTS.md\n\n"
        f"Guidance for coding agents and human contributors working on {ctx.project_name}.\n\n"
        "## Setup\n\n"
        "```bash\n"
        'python -m pip install -e ".[dev]"\n'
        "```\n\n"
        "## Test and lint commands\n\n"
        "```bash\n"
        "pytest\n"
        "ruff check .\n"
        "```\n\n"
        "## Conventions\n\n"
        "- Keep changes small, documented, and covered by tests.\n"
        "- Prefer relative paths and configurable inputs.\n"
        "- Document data sources, environment versions, and random seeds.\n\n"
        "## Verification\n\n"
        "Reproducibility regressions are caught by running the project's reproducibility\n"
        "audit. Re-run it after changes and confirm previously reported issues are gone.\n"
    )


def _citation(ctx: FixContext) -> str:
    lines = [
        "cff-version: 1.2.0\n"
        f'title: "{_yaml_double_quoted(ctx.project_name)}"\n'
        'message: "If you use this software, please cite it as below."\n'
        "type: software\n"
        "authors:\n"
    ]
    for author in ctx.authors or (ctx.author,):
        lines.append(f'  - name: "{_yaml_double_quoted(author)}"\n')
    lines.extend([f'date-released: "{ctx.date_released or f"{ctx.year}-01-01"}"\n'])
    if ctx.version:
        lines.append(f'version: "{_yaml_double_quoted(ctx.version)}"\n')
    if ctx.repository_url:
        lines.append(f'repository-code: "{_yaml_double_quoted(ctx.repository_url)}"\n')
    lines.append(
        "# TODO: Add a DOI and verify individual author names before release, if available.\n"
    )
    return "".join(lines)


def _yaml_double_quoted(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _detected_data_hints(ctx: FixContext) -> list[str]:
    hints: list[str] = []
    for path in _top_level_data_dirs(ctx.root):
        hints.append(f"- Local data-related directory: `{path}`")
    for path in _data_related_scripts(ctx.root):
        hints.append(f"- Possible data retrieval/preprocessing script: `{path}`")
    readme = ctx.root / "README.md"
    if readme.exists() and DATA_HINT_TEXT_RE.search(read_text(readme)):
        hints.append("- README mentions data, datasets, downloads, DOI, or preprocessing.")
    return hints


def _top_level_data_dirs(root: Path) -> list[str]:
    paths: list[str] = []
    for path in sorted(root.iterdir()):
        if path.is_dir() and path.name.lower() in DATA_HINT_DIR_NAMES:
            paths.append(_rel_posix(path, root) + "/")
    return paths[:12]


def _data_related_scripts(root: Path) -> list[str]:
    scripts: list[str] = []
    for path in sorted(root.rglob("*")):
        if len(scripts) >= 12:
            break
        if not path.is_file() or _is_ignored_hint_path(path, root):
            continue
        lowered = path.name.lower()
        if path.suffix.lower() not in {".py", ".r", ".jl", ".sh", ".R"}:
            continue
        if any(term in lowered for term in DATA_SCRIPT_TERMS):
            scripts.append(_rel_posix(path, root))
    return scripts


def _is_ignored_hint_path(path: Path, root: Path) -> bool:
    ignored = {".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".ruff_cache"}
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in ignored for part in rel_parts)


def _rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _data_dir_children(ctx: FixContext) -> list[str]:
    data_dir = ctx.root / "data"
    if not data_dir.exists() or not data_dir.is_dir():
        return []
    children: list[str] = []
    for child in sorted(data_dir.iterdir()):
        suffix = "/" if child.is_dir() else ""
        children.append(_rel_posix(child, ctx.root) + suffix)
    return children[:20]


def _data_md(ctx: FixContext) -> str:
    lines = [
        "# Data Availability\n\n",
        f"Project: {ctx.project_name}\n",
    ]
    if ctx.repository_url:
        lines.append(f"Repository: {ctx.repository_url}\n")
    lines.extend(
        [
            "\n",
            "This file was scaffolded from local repository evidence. Replace the prompts\n",
            "below with confirmed dataset names, access terms, versions, and retrieval\n",
            "steps before a release or Artifact Evaluation submission.\n\n",
            "## Detected local hints\n\n",
        ]
    )
    hints = _detected_data_hints(ctx)
    if hints:
        lines.extend(f"{hint}\n" for hint in hints)
    else:
        lines.append("- No obvious local data directories or retrieval scripts were detected.\n")
    lines.extend(
        [
            "\n",
            "## Sources\n\n",
            "- Dataset name and version:\n",
            "- Original source or archive URL/DOI:\n",
            "- License, terms of use, or access restrictions:\n\n",
            "## Retrieval\n\n",
            "- Command or script to obtain the data:\n",
            "- Expected download size and runtime:\n",
            "- Required credentials or manual approval, if any:\n\n",
            "## Preprocessing\n\n",
            "- Command or script to preprocess raw data:\n",
            "- Inputs and outputs:\n",
            "- Random seed or deterministic ordering assumptions:\n\n",
            "## Storage\n\n",
            "- Files committed to this repository:\n",
            "- Files intentionally excluded from git:\n",
            "- Checksum or archive snapshot, if available:\n",
        ]
    )
    return "".join(lines)


def _data_dir_readme(ctx: FixContext) -> str:
    lines = [
        "# Data directory\n\n",
        "This directory holds project data or data pointers. Large, restricted, or\n",
        "regenerable artifacts should usually stay outside git and be documented here.\n\n",
    ]
    children = _data_dir_children(ctx)
    if children:
        lines.extend(["## Current contents\n\n"])
        lines.extend(f"- `{child}`\n" for child in children)
        lines.append("\n")
    lines.extend(
        [
            "## Document before release\n\n",
            "- Expected files and formats.\n",
            "- Source archive, DOI, or access procedure for raw data.\n",
            "- Preprocessing commands and generated outputs.\n",
            "- Checksums or version identifiers for externally stored artifacts.\n",
        ]
    )
    return "".join(lines)


def _results_readme(ctx: FixContext) -> str:
    return (
        "# Results provenance\n\n"
        "For each stored result, record:\n\n"
        "- The command used to produce it.\n"
        "- The commit hash of the code.\n"
        "- The data version or snapshot.\n"
        "- The environment (dependency versions, hardware, random seed).\n"
    )


def _seed_helper(ctx: FixContext) -> str:
    return (
        '"""Deterministic seed helper scaffolded by rrdoctor.\n'
        "\n"
        "TODO: Import and call set_global_seed(seed) at the start of your CLI,\n"
        "training, evaluation, or notebook entrypoint before creating datasets,\n"
        "models, data loaders, train/test splits, or any random samples.\n"
        '"""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "import os\n"
        "import random\n"
        "\n"
        "\n"
        "def set_global_seed(seed: int) -> None:\n"
        '    """Seed common Python and ML randomness sources."""\n'
        "\n"
        '    os.environ["PYTHONHASHSEED"] = str(seed)\n'
        "    random.seed(seed)\n"
        "\n"
        "    try:\n"
        "        import numpy as np\n"
        "    except ImportError:\n"
        "        np = None\n"
        "    if np is not None:\n"
        "        np.random.seed(seed)\n"
        "\n"
        "    try:\n"
        "        import torch\n"
        "    except ImportError:\n"
        "        torch = None\n"
        "    if torch is not None:\n"
        "        torch.manual_seed(seed)\n"
        '        if hasattr(torch, "cuda"):\n'
        "            torch.cuda.manual_seed_all(seed)\n"
        '        if hasattr(torch, "backends") and hasattr(torch.backends, "cudnn"):\n'
        "            torch.backends.cudnn.deterministic = True\n"
        "            torch.backends.cudnn.benchmark = False\n"
        "\n"
        "    try:\n"
        "        import tensorflow as tf\n"
        "    except ImportError:\n"
        "        tf = None\n"
        "    if tf is not None:\n"
        "        tf.random.set_seed(seed)\n"
    )


def _changelog(ctx: FixContext) -> str:
    today = datetime.now(timezone.utc).date().isoformat()
    return (
        "# Changelog\n\n"
        "All notable changes to this project are documented in this file.\n\n"
        f"## Unreleased\n\n"
        "- Initial changelog created.\n\n"
        f"## 0.1.0 - {today}\n\n"
        "- First documented release.\n"
    )


# --- Fixers that operate conditionally on the repository state ---------------


def _fix_gitignore(ctx: FixContext) -> FixResult:
    rule_id = "RRD091"
    path = ctx.root / ".gitignore"
    header = "# Added by rrdoctor: common research artifacts\n"
    block = header + "\n".join(COMMON_GITIGNORE_TERMS) + "\n"
    if not path.exists():
        path.write_text(block, encoding="utf-8")
        return FixResult(
            rule_id, ".gitignore", "created", "Created .gitignore with research artifacts."
        )
    text = read_text(path)
    missing = [term for term in COMMON_GITIGNORE_TERMS if term not in text]
    if not missing:
        return FixResult(
            rule_id, ".gitignore", "skipped", ".gitignore already covers research artifacts."
        )
    suffix = ("" if text.endswith("\n") else "\n") + "\n" + header + "\n".join(missing) + "\n"
    path.write_text(text + suffix, encoding="utf-8")
    return FixResult(
        rule_id, ".gitignore", "updated", f"Appended {len(missing)} research artifact entries."
    )


def _fix_data_dir_readme(ctx: FixContext) -> FixResult:
    rule_id = "RRD041"
    data_dir = ctx.root / "data"
    if not data_dir.exists():
        return FixResult(rule_id, "data/README.md", "skipped", "No data/ directory present.")
    return _write_if_missing(
        data_dir / "README.md", _data_dir_readme(ctx), rule_id, "data/README.md"
    )


def _fix_results_readme(ctx: FixContext) -> FixResult:
    rule_id = "RRD053"
    results_dir = ctx.root / "results"
    if not results_dir.exists():
        return FixResult(rule_id, "results/README.md", "skipped", "No results/ directory present.")
    return _write_if_missing(
        results_dir / "README.md", _results_readme(ctx), rule_id, "results/README.md"
    )


def _fix_seed_helper(ctx: FixContext) -> FixResult:
    rule_id = "RRD052"
    path = _seed_helper_path(ctx)
    rel = _rel_posix(path, ctx.root)
    return _write_if_missing(path, _seed_helper(ctx), rule_id, rel)


def _seed_helper_path(ctx: FixContext) -> Path:
    package_dir = _preferred_python_package_dir(ctx)
    if package_dir is not None:
        return package_dir / "_repro_seed.py"
    return ctx.root / "repro_seed.py"


def _preferred_python_package_dir(ctx: FixContext) -> Path | None:
    normalized = _normalize_package_name(ctx.project_name)
    candidates: list[Path] = []
    src = ctx.root / "src"
    if src.exists() and src.is_dir():
        exact = src / normalized
        if _is_python_package_dir(exact):
            return exact
        candidates.extend(_package_dirs(src))
    exact_root = ctx.root / normalized
    if _is_python_package_dir(exact_root):
        return exact_root
    candidates.extend(_package_dirs(ctx.root))
    return candidates[0] if len(candidates) == 1 else None


def _normalize_package_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name).strip("_").lower()


def _package_dirs(root: Path) -> list[Path]:
    ignored = {".git", ".venv", "venv", "__pycache__", "tests", "docs", "examples"}
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and path.name not in ignored and _is_python_package_dir(path)
    )


def _is_python_package_dir(path: Path) -> bool:
    return path.exists() and path.is_dir() and (path / "__init__.py").exists()


def _simple_file(
    name: str, render: Callable[[FixContext], str], rule_id: str
) -> Callable[[FixContext], FixResult]:
    def fixer(ctx: FixContext) -> FixResult:
        return _write_if_missing(ctx.root / name, render(ctx), rule_id, name)

    return fixer


# --- Registry ----------------------------------------------------------------

FIXERS: dict[str, Callable[[FixContext], FixResult]] = {
    "RRD010": _simple_file("LICENSE", _license_mit, "RRD010"),
    "RRD011": _simple_file("CONTRIBUTING.md", _contributing, "RRD011"),
    "RRD012": _simple_file("SECURITY.md", _security, "RRD012"),
    "RRD013": _simple_file("CODE_OF_CONDUCT.md", _code_of_conduct, "RRD013"),
    "RRD014": _simple_file("AGENTS.md", _agents, "RRD014"),
    "RRD020": _simple_file("CITATION.cff", _citation, "RRD020"),
    "RRD040": _simple_file("DATA.md", _data_md, "RRD040"),
    "RRD041": _fix_data_dir_readme,
    "RRD052": _fix_seed_helper,
    "RRD053": _fix_results_readme,
    "RRD091": _fix_gitignore,
    "RRD100": _simple_file("CHANGELOG.md", _changelog, "RRD100"),
}


def fixable_rule_ids() -> frozenset[str]:
    """Return the set of rule IDs that have a deterministic fixer."""

    return frozenset(FIXERS)


def apply_fix(rule_id: str, ctx: FixContext) -> FixResult | None:
    """Apply the fixer for a rule, or return None when no fixer exists."""

    fixer = FIXERS.get(rule_id.upper())
    if fixer is None:
        return None
    return fixer(ctx)
