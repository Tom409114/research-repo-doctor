"""Environment and dependency rules."""

from __future__ import annotations

import re

from rrdoctor.models import Category, Evidence, ScanContext, Severity
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

    def check(self, context: ScanContext):
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

    def check(self, context: ScanContext):
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

    def check(self, context: ScanContext):
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
    ContainerMissingStrictRule(),
]
