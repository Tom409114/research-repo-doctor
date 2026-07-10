"""Release readiness rules."""

from __future__ import annotations

import re
from pathlib import Path

from rrdoctor.models import Category, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, read_text
from rrdoctor.rules.paths import find_files, has_file


class ChangelogMissingRule(Rule):
    definition = definition(
        "RRD100",
        "CHANGELOG missing",
        Category.RELEASE,
        Severity.INFO,
        ("standard", "strict", "ml"),
        "Checks for release history documentation.",
        "A changelog helps users understand changes between research code releases.",
        "Add CHANGELOG.md with at least an initial v0.1.0 entry.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not has_file(context.root, ["CHANGELOG.md", "HISTORY.md"]):
            return [self.finding(context, message="No CHANGELOG file was found.")]
        return []


class VersionMetadataMissingRule(Rule):
    definition = definition(
        "RRD101",
        "No version metadata found",
        Category.RELEASE,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks for version metadata in common project files.",
        "Versioned releases are easier to cite and reproduce.",
        "Add package version metadata, VERSION file, or release tags.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        candidates = [
            context.root / "pyproject.toml",
            context.root / "Cargo.toml",
            context.root / "package.json",
            context.root / "VERSION",
        ]
        combined = "\n".join(read_text(path) for path in candidates if path.exists())
        if (
            not re.search(r"(?im)^(version|__version__)\s*=", combined)
            and not (context.root / "VERSION").exists()
            and not _has_git_tag(context.root)
        ):
            return [
                self.finding(
                    context,
                    message="No version metadata was detected.",
                    severity=_version_metadata_severity(context),
                )
            ]
        return []


class ReleaseWorkflowMissingRule(Rule):
    definition = definition(
        "RRD102",
        "No release or packaging workflow found",
        Category.RELEASE,
        Severity.INFO,
        ("strict",),
        "Checks strict-profile repositories for release automation.",
        "Release workflows make public artifacts more consistent and auditable.",
        "Add a release workflow, packaging workflow, or documented manual release checklist.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        workflows = find_files(context, [".github/workflows/*.yml", ".github/workflows/*.yaml"])
        text = "\n".join(read_text(path).lower() for path in workflows)
        if not any(
            term in text
            for term in ("release", "pypa/gh-action-pypi-publish", "actions/upload-artifact")
        ):
            return [self.finding(context, message="No release or packaging workflow was detected.")]
        return []


def _has_git_tag(root: Path) -> bool:
    git_dir = root / ".git"
    if not git_dir.exists():
        return False
    if git_dir.is_file():
        gitdir_line = read_text(git_dir).strip()
        if gitdir_line.lower().startswith("gitdir:"):
            git_dir = (root / gitdir_line.split(":", 1)[1].strip()).resolve()
    tags_dir = git_dir / "refs" / "tags"
    if tags_dir.exists() and any(path.is_file() for path in tags_dir.rglob("*")):
        return True
    packed_refs = git_dir / "packed-refs"
    if packed_refs.exists():
        for line in read_text(packed_refs).splitlines():
            if line and not line.startswith("#") and " refs/tags/" in line:
                return True
    return False


def _version_metadata_severity(context: ScanContext) -> Severity:
    profile = str(context.config.get("profile", "standard"))
    strict_profiles = {"strict", "ml-paper", "neurips", "icml", "acm", "fair4rs", "joss"}
    return Severity.WARNING if profile in strict_profiles else Severity.INFO


RULES = [ChangelogMissingRule(), VersionMetadataMissingRule(), ReleaseWorkflowMissingRule()]
