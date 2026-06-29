"""Deterministic, idempotent auto-fixers for common reproducibility gaps.

Fixers create or extend small scaffolding files (governance docs, citation
metadata, seed helpers, data and results provenance notes, changelog, and ignore entries).
They never overwrite existing content, never make network calls, and never run
code from the scanned repository. Anything that requires human judgement (for
example, the actual content of a README reproducibility section) is intentionally
left to the agent fix plan instead.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from rrdoctor.models import FixResult
from rrdoctor.rules.base import read_text
from rrdoctor.rules.security import COMMON_GITIGNORE_TERMS


@dataclass(frozen=True)
class FixContext:
    """Inputs that parameterise generated scaffolding."""

    root: Path
    project_name: str
    author: str
    year: int
    contact: str = "the maintainers (see repository profile)"


def _write_if_missing(path: Path, content: str, rule_id: str, rel: str) -> FixResult:
    if path.exists():
        return FixResult(rule_id, rel, "skipped", f"{rel} already exists.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return FixResult(rule_id, rel, "created", f"Created {rel}.")


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
    return (
        "cff-version: 1.2.0\n"
        f'title: "{ctx.project_name}"\n'
        'message: "If you use this software, please cite it as below."\n'
        "type: software\n"
        "authors:\n"
        f'  - name: "{ctx.author}"\n'
        f'date-released: "{ctx.year}-01-01"\n'
        "# Add a DOI, repository-code URL, version, and individual authors before release.\n"
    )


def _data_md(ctx: FixContext) -> str:
    return (
        "# Data Availability\n\n"
        "## Sources\n\n"
        "Describe each dataset used: where it comes from, license or access terms, and\n"
        "how to obtain it.\n\n"
        "## Retrieval\n\n"
        "Document the exact steps or scripts used to download or generate the data.\n\n"
        "## Preprocessing\n\n"
        "Describe preprocessing steps and where intermediate artifacts are stored.\n"
    )


def _data_dir_readme(ctx: FixContext) -> str:
    return (
        "# Data directory\n\n"
        "This directory holds project data. Document the following:\n\n"
        "- Expected contents and file formats.\n"
        "- How to obtain raw data (large or restricted data should not be committed).\n"
        "- Any preprocessing required before use.\n"
    )


def _results_readme(ctx: FixContext) -> str:
    return (
        "# Results provenance\n\n"
        "For each stored result, record:\n\n"
        "- The command used to produce it.\n"
        "- The commit hash of the code.\n"
        "- The data version or snapshot.\n"
        "- The environment (dependency versions, hardware, random seed).\n"
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


def _repro_seed_module(ctx: FixContext) -> str:
    return (
        '"""Project-level random seed helper for reproducible local runs.\n'
        "\n"
        "TODO: Call set_global_seed(...) from the main training or analysis\n"
        "entrypoint before data splitting, random sampling, or model initialization.\n"
        '"""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "import importlib\n"
        "import importlib.util\n"
        "import random\n"
        "\n"
        "\n"
        "def _optional_module(name: str):\n"
        '    """Import an optional dependency only when it is installed."""\n'
        "\n"
        "    if importlib.util.find_spec(name) is None:\n"
        "        return None\n"
        "    return importlib.import_module(name)\n"
        "\n"
        "\n"
        "def set_global_seed(seed: int) -> None:\n"
        '    """Seed common pseudo-random number generators used in research code."""\n'
        "\n"
        "    random.seed(seed)\n"
        "\n"
        '    numpy = _optional_module("numpy")\n'
        "    if numpy is not None:\n"
        "        numpy.random.seed(seed)\n"
        "\n"
        '    torch = _optional_module("torch")\n'
        "    if torch is not None:\n"
        "        torch.manual_seed(seed)\n"
        "        if torch.cuda.is_available():\n"
        "            torch.cuda.manual_seed_all(seed)\n"
        "\n"
        '    tensorflow = _optional_module("tensorflow")\n'
        "    if tensorflow is not None:\n"
        "        tensorflow.random.set_seed(seed)\n"
    )


def _repro_seed_note(ctx: FixContext) -> str:
    return (
        "# Reproducible randomness seed scaffold\n\n"
        "This project uses randomness. Add a deterministic seed call before data\n"
        "splitting, random sampling, or model initialization.\n\n"
        "TODO: Move this helper into the package or script that owns the main\n"
        "training/analysis entrypoint, then call `set_global_seed(...)` there.\n\n"
        "```python\n"
        f"{_repro_seed_module(ctx)}"
        "```\n"
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


def _is_package_dir(path: Path) -> bool:
    return path.is_dir() and path.name.isidentifier() and (path / "__init__.py").exists()


def _single_python_package(root: Path) -> Path | None:
    src_dir = root / "src"
    if src_dir.is_dir():
        src_packages = sorted(
            (path for path in src_dir.iterdir() if _is_package_dir(path)),
            key=lambda path: path.name,
        )
        if len(src_packages) == 1:
            return src_packages[0]

    ignored = {"docs", "notebooks", "scripts", "tests"}
    root_packages = sorted(
        (
            path
            for path in root.iterdir()
            if path.name not in ignored and not path.name.startswith(".") and _is_package_dir(path)
        ),
        key=lambda path: path.name,
    )
    if len(root_packages) == 1:
        return root_packages[0]
    return None


def _fix_repro_seed_helper(ctx: FixContext) -> FixResult:
    rule_id = "RRD052"
    package_dir = _single_python_package(ctx.root)
    if package_dir is not None:
        rel = (package_dir.relative_to(ctx.root) / "_repro_seed.py").as_posix()
        return _write_if_missing(
            package_dir / "_repro_seed.py", _repro_seed_module(ctx), rule_id, rel
        )
    return _write_if_missing(
        ctx.root / "docs" / "reproducibility-seed.md",
        _repro_seed_note(ctx),
        rule_id,
        "docs/reproducibility-seed.md",
    )


def _fix_results_readme(ctx: FixContext) -> FixResult:
    rule_id = "RRD053"
    results_dir = ctx.root / "results"
    if not results_dir.exists():
        return FixResult(rule_id, "results/README.md", "skipped", "No results/ directory present.")
    return _write_if_missing(
        results_dir / "README.md", _results_readme(ctx), rule_id, "results/README.md"
    )


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
    "RRD052": _fix_repro_seed_helper,
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
