"""Check public trust signals before a release, submission, or launch post.

The gate is intentionally local and deterministic. It does not call GitHub,
Streamlit, PyPI, Zenodo, or any third-party repository; it only checks that the
tracked public repository still contains the evidence a first-time evaluator
expects to see.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]

LIVE_DEMO_URL = "https://research-repo-doctor-bckncrcwwmg6jrbsrd6btj.streamlit.app/"
MIN_DEMO_GIF_BYTES = 100_000
MIN_CORPUS_REPOSITORIES = 50
MIN_REVIEWED_CORPUS_REPOSITORIES = 20

REQUIRED_ISSUE_TEMPLATES = {
    "bug_report.yml",
    "false_negative.yml",
    "false_positive.yml",
    "rule_request.yml",
    "scan_case.yml",
}
REQUIRED_PROJECT_URLS = {"Homepage", "Repository", "Issues", "Changelog", "Live Demo"}
REQUIRED_DOC_INDEX_LINKS = {
    "Artifact Evaluation deadline workflow": "ae-deadline-workflow.md",
    "Guide for Artifact Evaluation chairs": "ae-chair-guide.md",
    "Evaluation corpus": "evaluation-corpus.md",
    "Feedback and calibration": "feedback.md",
    "Maintainer workflows": "maintainer-workflows.md",
}
FORBIDDEN_TRACKED_PATH_PARTS = (
    "codex-for-oss" + "-application",
    "initial" + "-issues",
    "launch" + "-checklist",
    "CONTRIB" + "_awesome_entry",
    "MAKING" + "_THE_GIF",
)
FORBIDDEN_PUBLIC_TEXT = (
    "C:" + "\\" + "Users" + "\\" + "thuah",
    "files-mentioned-by-the-user" + "-txt",
    ".codex" + "/" + "attachments",
    "codex-for-oss" + "-application",
    "docs" + "/" + "starter-issues.md",
    "docs" + "/" + "release-checklist.md",
    "CONTRIB" + "_awesome_entry.md",
    "once the public repo" + " is launched",
    "@" + "OWNER",
    "<PASTE" + "_DEMO_URL>",
)
TEXT_SUFFIXES = {
    ".cff",
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def check_public_readiness(root: Path = ROOT) -> list[str]:
    """Return public-readiness failures for a repository checkout."""

    failures: list[str] = []
    tracked_files = _tracked_files(root)

    _check_internal_materials(root, tracked_files, failures)
    _check_readme_and_demo(root, failures)
    _check_package_metadata(root, failures)
    _check_release_metadata(root, failures)
    _check_issue_templates(root, failures)
    _check_self_scan_badge(root, failures)
    _check_corpus_evidence(root, failures)
    _check_docs_index(root, failures)

    return failures


def _check_internal_materials(root: Path, tracked_files: list[str], failures: list[str]) -> None:
    leaked_paths = [
        path
        for path in tracked_files
        if any(part.lower() in path.lower() for part in FORBIDDEN_TRACKED_PATH_PARTS)
    ]
    if leaked_paths:
        failures.append("internal launch/application files are tracked: " + ", ".join(leaked_paths))

    leaks: list[str] = []
    for tracked_path in tracked_files:
        path = root / tracked_path
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for forbidden in FORBIDDEN_PUBLIC_TEXT:
            if forbidden in text:
                leaks.append(f"{tracked_path}: {forbidden}")
    if leaks:
        failures.append("public text leaks internal or placeholder material: " + "; ".join(leaks))


def _check_readme_and_demo(root: Path, failures: list[str]) -> None:
    readme = _read_required_text(root / "README.md", failures)
    if not readme:
        return

    if LIVE_DEMO_URL not in readme:
        failures.append("README.md does not link the live zero-install demo near the top.")
    if "![rrdoctor demo](docs/demo.gif)" not in readme:
        failures.append("README.md does not embed docs/demo.gif.")

    demo = root / "docs" / "demo.gif"
    if not demo.exists():
        failures.append("docs/demo.gif is missing.")
        return
    if demo.stat().st_size < MIN_DEMO_GIF_BYTES:
        failures.append(f"docs/demo.gif is smaller than {MIN_DEMO_GIF_BYTES} bytes.")
    if demo.read_bytes()[:6] not in {b"GIF87a", b"GIF89a"}:
        failures.append("docs/demo.gif is not a GIF file.")


def _check_package_metadata(root: Path, failures: list[str]) -> None:
    pyproject = _load_toml(root / "pyproject.toml", failures)
    if not pyproject:
        return

    project = pyproject.get("project", {})
    urls = project.get("urls", {})
    missing_urls = sorted(REQUIRED_PROJECT_URLS - set(urls))
    if missing_urls:
        failures.append("pyproject.toml is missing project URLs: " + ", ".join(missing_urls))
    if urls.get("Live Demo") != LIVE_DEMO_URL:
        failures.append("pyproject.toml Live Demo URL is missing or stale.")

    version = project.get("version")
    latest_changelog = _latest_changelog_version(root / "CHANGELOG.md")
    if latest_changelog and version != latest_changelog:
        failures.append(
            f"pyproject.toml version {version!r} does not match latest CHANGELOG release "
            f"{latest_changelog!r}."
        )


def _check_release_metadata(root: Path, failures: list[str]) -> None:
    for required in ("LICENSE", "CITATION.cff", "CHANGELOG.md", "SECURITY.md"):
        if not (root / required).exists():
            failures.append(f"{required} is missing.")


def _check_issue_templates(root: Path, failures: list[str]) -> None:
    template_dir = root / ".github" / "ISSUE_TEMPLATE"
    if not template_dir.exists():
        failures.append(".github/ISSUE_TEMPLATE is missing.")
        return

    present = {path.name for path in template_dir.glob("*.yml")}
    missing = sorted(REQUIRED_ISSUE_TEMPLATES - present)
    if missing:
        failures.append("required issue templates are missing: " + ", ".join(missing))

    config_path = template_dir / "config.yml"
    if not config_path.exists():
        failures.append(".github/ISSUE_TEMPLATE/config.yml is missing.")
        return
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if config.get("blank_issues_enabled") is not True:
        failures.append("blank GitHub issues are disabled in issue-template config.")


def _check_self_scan_badge(root: Path, failures: list[str]) -> None:
    badge_path = root / ".rrdoctor-badge.json"
    report_path = root / "examples" / "reports" / "self-scan-report.md"
    if not badge_path.exists():
        failures.append(".rrdoctor-badge.json is missing.")
        return
    if not report_path.exists():
        failures.append("examples/reports/self-scan-report.md is missing.")
        return

    badge = json.loads(badge_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    readiness = _markdown_field(report, "Artifact readiness")
    score = _markdown_field(report, "Heuristic score")

    if badge.get("message") != readiness:
        failures.append(
            f"readiness badge message {badge.get('message')!r} does not match self-scan "
            f"readiness {readiness!r}."
        )
    if readiness != "Reproduced-ready":
        failures.append(f"self-scan readiness is {readiness!r}, expected 'Reproduced-ready'.")
    if score != "100/100":
        failures.append(f"self-scan score is {score!r}, expected '100/100'.")


def _check_corpus_evidence(root: Path, failures: list[str]) -> None:
    aggregate_path = root / "evaluation" / "reports" / "corpus-aggregate.json"
    summary_path = root / "evaluation" / "reports" / "corpus-summary.md"
    if not aggregate_path.exists():
        failures.append("evaluation/reports/corpus-aggregate.json is missing.")
        return
    if not summary_path.exists():
        failures.append("evaluation/reports/corpus-summary.md is missing.")

    aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
    scanned = int(aggregate.get("scanned_repositories", 0))
    reviewed = int(aggregate.get("reviewed_repositories", 0))
    errors = int(aggregate.get("error_repositories", 0))
    expected_absent = aggregate.get("expected_absent_violations", [])

    if scanned < MIN_CORPUS_REPOSITORIES:
        failures.append(
            f"evaluation corpus has {scanned} scanned repositories; expected at least "
            f"{MIN_CORPUS_REPOSITORIES}."
        )
    if reviewed < MIN_REVIEWED_CORPUS_REPOSITORIES:
        failures.append(
            f"evaluation corpus has {reviewed} reviewed repositories; expected at least "
            f"{MIN_REVIEWED_CORPUS_REPOSITORIES}."
        )
    if errors != 0:
        failures.append(f"evaluation corpus has {errors} clone or scan errors.")
    if expected_absent:
        failures.append("evaluation corpus has expected-absent regressions.")


def _check_docs_index(root: Path, failures: list[str]) -> None:
    index = _read_required_text(root / "docs" / "index.md", failures)
    if not index:
        return
    for label, href in REQUIRED_DOC_INDEX_LINKS.items():
        if f"[{label}]({href})" not in index:
            failures.append(f"docs/index.md does not link {label}.")


def _tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def _read_required_text(path: Path, failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"{path.name} is missing.")
        return ""
    return path.read_text(encoding="utf-8")


def _load_toml(path: Path, failures: list[str]) -> dict[str, Any]:
    if not path.exists():
        failures.append(f"{path.name} is missing.")
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _latest_changelog_version(path: Path) -> str | None:
    if not path.exists():
        return None
    match = re.search(
        r"^## v(?P<version>\d+\.\d+\.\d+) - \d{4}-\d{2}-\d{2}$",
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        return None
    return match.group("version")


def _markdown_field(markdown: str, field: str) -> str | None:
    match = re.search(rf"^- {re.escape(field)}: \*\*(?P<value>[^*]+)\*\*$", markdown, re.MULTILINE)
    return match.group("value") if match else None


def main() -> int:
    failures = check_public_readiness()
    if not failures:
        print("Public readiness checks passed.")
        return 0

    print("Public readiness checks failed:", file=sys.stderr)
    for failure in failures:
        print(f"- {failure}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
