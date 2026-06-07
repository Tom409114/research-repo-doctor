"""Environment and dependency rules."""

from __future__ import annotations

import re

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, read_text
from rrdoctor.rules.paths import has_file

DEPENDENCY_FILES = [
    "pyproject.toml",
    "requirements.txt",
    "environment.yml",
    "conda.yml",
    "Pipfile",
    "poetry.lock",
    "uv.lock",
    "package.json",
    "renv.lock",
]


class DependencyManifestMissingRule(Rule):
    definition = definition(
        "RRD030",
        "No dependency manifest found",
        Category.ENVIRONMENT,
        Severity.ERROR,
        ("minimal", "standard", "strict", "ml"),
        "Checks for dependency manifests.",
        "A repository without dependency metadata is hard to reproduce.",
        "Add pyproject.toml, requirements.txt, environment.yml, or another supported manifest.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not has_file(context.root, DEPENDENCY_FILES):
            return [self.finding(context, message="No supported dependency manifest was found.")]
        return []


class PythonVersionHintMissingRule(Rule):
    definition = definition(
        "RRD031",
        "Dependency manifest lacks version hint",
        Category.ENVIRONMENT,
        Severity.WARNING,
        ("minimal", "standard", "strict", "ml"),
        "Checks dependency manifests for Python or environment version hints.",
        "Language/runtime versions are part of the experimental environment.",
        "Add requires-python, python=, runtime.txt, or a documented environment version.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        existing = [
            context.root / name for name in DEPENDENCY_FILES if (context.root / name).exists()
        ]
        if not existing:
            return []
        combined = "\n".join(read_text(path) for path in existing)
        if not re.search(
            r"(?i)(requires-python|python\s*[<>=~!]|python=|runtime|node\s*[:=])", combined
        ):
            evidence = [
                Evidence(
                    "Manifest exists but no runtime version hint was detected.",
                    context.rel(existing[0]),
                )
            ]
            return [
                self.finding(
                    context,
                    message="Dependency manifest lacks a Python/environment version hint.",
                    evidence=evidence,
                    file=context.rel(existing[0]),
                )
            ]
        return []


def _unpinned_requirements(text: str) -> list[str]:
    """Return requirement names that declare no version at all."""

    unpinned: list[str] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        # Drop environment markers and inline options.
        spec = line.split(";", 1)[0].strip()
        if not spec or spec[0] in "<>=~!@" or not spec[0].isascii() or not spec[0].isalnum():
            continue
        name = re.split(r"[\[<>=~!@ ]", spec, maxsplit=1)[0]
        if not any(op in spec for op in ("==", ">=", "<=", "~=", "!=", "<", ">", "@")):
            unpinned.append(name)
    return unpinned


class UnpinnedDependenciesRule(Rule):
    definition = definition(
        "RRD033",
        "Unpinned dependencies in requirements file",
        Category.ENVIRONMENT,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks requirements.txt files for dependencies declared without any version.",
        "Unpinned dependencies can resolve to different versions over time, which "
        "silently changes results and breaks reproduction.",
        "Pin versions (prefer ==) or document a tested version range and a lockfile.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        for name in ("requirements.txt", "requirements/base.txt", "requirements/main.txt"):
            path = context.root / name
            if not path.exists():
                continue
            unpinned = _unpinned_requirements(read_text(path))
            if unpinned:
                rel = context.rel(path)
                preview = ", ".join(unpinned[:6])
                return [
                    self.finding(
                        context,
                        message=f"{len(unpinned)} dependency line(s) declare no version.",
                        evidence=[Evidence(f"Unpinned: {preview}", rel)],
                        file=rel,
                    )
                ]
        return []


class ContainerMissingStrictRule(Rule):
    definition = definition(
        "RRD032",
        "Dockerfile or devcontainer missing",
        Category.ENVIRONMENT,
        Severity.INFO,
        ("strict",),
        "Checks strict-profile repositories for containerized environment docs.",
        "Containers are not required, but help reviewers rebuild complex environments.",
        "Add a Dockerfile, .devcontainer/devcontainer.json, or document why one is not needed.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not has_file(context.root, ["Dockerfile", ".devcontainer/devcontainer.json"]):
            return [
                self.finding(
                    context, message="Strict profile expects a Dockerfile or devcontainer."
                )
            ]
        return []


RULES = [
    DependencyManifestMissingRule(),
    PythonVersionHintMissingRule(),
    UnpinnedDependenciesRule(),
    ContainerMissingStrictRule(),
]
