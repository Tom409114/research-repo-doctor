"""README and documentation rules."""

from __future__ import annotations

from rrdoctor.models import Category, Evidence, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, has_any_heading, read_text


def readme_path(context: ScanContext):
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

    def check(self, context: ScanContext):
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

    def check(self, context: ScanContext):
        path = readme_path(context)
        if path is None:
            return []
        text = read_text(path)
        if not has_any_heading(text, ("install", "installation", "setup", "environment")):
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

    def check(self, context: ScanContext):
        path = readme_path(context)
        if path is None:
            return []
        text = read_text(path)
        if not has_any_heading(text, ("quickstart", "usage", "example", "run")):
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

    def check(self, context: ScanContext):
        path = readme_path(context)
        if path is None:
            return []
        text = read_text(path)
        if not has_any_heading(text, ("reproduc", "results", "replicate")):
            return [
                self.finding(
                    context,
                    message="README does not describe how to reproduce key results.",
                    evidence=[
                        Evidence(
                            "README headings do not mention reproducibility.", context.rel(path)
                        )
                    ],
                    file=context.rel(path),
                )
            ]
        return []


RULES = [ReadmeMissingRule(), ReadmeSetupRule(), ReadmeUsageRule(), ReadmeReproduceRule()]
