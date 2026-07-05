"""README and documentation rules."""

from __future__ import annotations

import re
from pathlib import Path

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, has_any_heading, read_text

INSTALL_COMMAND_RE = re.compile(
    r"(?im)(^|\n)\s*(?:\$|>)?\s*"
    r"(?:(?:python\s+-m\s+)?pip|pipx|uv|uvx|conda|mamba|poetry|pdm)\s+"
    r"(?:install|add|sync|run|create|env)\b"
)
USAGE_COMMAND_RE = re.compile(
    r"(?im)(^|\n)\s*(?:\$|>)?\s*"
    r"(?:(?:uv|poetry|pipenv)\s+run\s+)?"
    r"(?:python(?:\s+-m)?|Rscript|julia|bash|sh|make|snakemake|nextflow(?:\s+run)?)\b"
)
GET_STARTED_TEXT_RE = re.compile(r"(?i)\b(get started|getting started|quick start)\b")
REPRODUCE_COMMAND_RE = re.compile(
    r"(?im)(^|\n)\s*(?:\$|>)?\s*"
    r"(?:(?:uv|poetry|pipenv)\s+run\s+)?"
    r"(?:"
    r"python(?:\s+-m)?|Rscript|julia|bash|sh|make|snakemake|nextflow(?:\s+run)?"
    r")\b[^\n]*\b("
    r"train|training|eval|evaluate|test|predict|infer|inference|sample|benchmark|"
    r"reproduc|replicate|experiment|main|run|Snakefile|workflow"
    r")\b"
)
REPRODUCE_TEXT_RE = re.compile(
    r"(?is)\b(reproduce|replicate)\b.{0,80}\b(results?|experiments?|paper|figures?)\b"
)


def readme_path(context: ScanContext) -> Path | None:
    """Return README path if present."""

    for name in ("README.md", "README.rst", "README.txt", "readme.md"):
        path = context.root / name
        if path.exists():
            return path
    return None


class ReadmeMissingRule(Rule):
    definition = definition(
        "RRD001",
        "README missing",
        Category.DOCUMENTATION,
        Severity.ERROR,
        ("minimal", "standard", "strict", "ml"),
        "Checks that the repository has a README.",
        "A README is the entry point for reviewers and future users.",
        "Add a README with project scope, setup, usage, and reproducibility instructions.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if readme_path(context) is None:
            return [
                self.finding(context, message="No README file was found at the repository root.")
            ]
        return []


class ReadmeSetupRule(Rule):
    definition = definition(
        "RRD002",
        "README lacks installation/setup section",
        Category.DOCUMENTATION,
        Severity.WARNING,
        ("minimal", "standard", "strict", "ml"),
        "Checks README for setup or installation guidance.",
        "Reproducibility begins with a working environment.",
        "Add an Installation or Setup section with exact commands.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        path = readme_path(context)
        if path is None:
            return []
        text = read_text(path)
        has_setup_evidence = has_any_heading(
            text, ("install", "installation", "setup", "environment")
        ) or INSTALL_COMMAND_RE.search(text)
        if not has_setup_evidence:
            return [
                self.finding(
                    context,
                    message="README exists but does not include an installation/setup section.",
                    evidence=[
                        Evidence(
                            "README headings do not mention installation or setup.",
                            context.rel(path),
                        )
                    ],
                    file=context.rel(path),
                )
            ]
        return []


class ReadmeUsageRule(Rule):
    definition = definition(
        "RRD003",
        "README lacks quickstart or usage section",
        Category.DOCUMENTATION,
        Severity.WARNING,
        ("minimal", "standard", "strict", "ml"),
        "Checks README for quickstart or usage guidance.",
        "Reviewers need a short path from clone to first meaningful run.",
        "Add a Quickstart or Usage section with a minimal command.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        path = readme_path(context)
        if path is None:
            return []
        text = read_text(path)
        has_usage_evidence = (
            has_any_heading(text, ("quickstart", "usage", "example", "run"))
            or GET_STARTED_TEXT_RE.search(text)
            or USAGE_COMMAND_RE.search(text)
        )
        if not has_usage_evidence:
            return [
                self.finding(
                    context,
                    message="README exists but does not include quickstart or usage guidance.",
                    evidence=[
                        Evidence(
                            "README headings do not mention quickstart or usage.", context.rel(path)
                        )
                    ],
                    file=context.rel(path),
                )
            ]
        return []


class ReadmeReproduceRule(Rule):
    definition = definition(
        "RRD004",
        "README lacks reproducibility section",
        Category.REPRODUCIBILITY,
        Severity.WARNING,
        ("minimal", "standard", "strict", "ml"),
        "Checks README for how to reproduce results.",
        "Research repositories should document the path from code to reported results.",
        "Add a Reproducibility or How to reproduce results section.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        path = readme_path(context)
        if path is None:
            return []
        text = read_text(path)
        has_reproducibility_evidence = (
            has_any_heading(text, ("reproduc", "results", "replicate"))
            or REPRODUCE_TEXT_RE.search(text)
            or REPRODUCE_COMMAND_RE.search(text)
        )
        if not has_reproducibility_evidence:
            return [
                self.finding(
                    context,
                    message="README does not describe how to reproduce key results.",
                    evidence=[
                        Evidence(
                            "README does not include a reproducibility/results section or a "
                            "training/evaluation/reproduction command.",
                            context.rel(path),
                        )
                    ],
                    file=context.rel(path),
                )
            ]
        return []


RULES = [ReadmeMissingRule(), ReadmeSetupRule(), ReadmeUsageRule(), ReadmeReproduceRule()]
