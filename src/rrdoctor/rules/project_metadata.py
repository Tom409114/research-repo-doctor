"""Project metadata rules."""

from __future__ import annotations

import re

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, read_text
from rrdoctor.rules.readme import readme_path


class PyprojectMetadataRule(Rule):
    definition = definition(
        "RRD110",
        "Python project metadata incomplete",
        Category.METADATA,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks Python project metadata when pyproject.toml exists.",
        "Complete package metadata helps reuse, citation, and packaging.",
        "Fill project name, version, description, license, authors, and requires-python.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        pyproject = context.root / "pyproject.toml"
        if not pyproject.exists():
            return []
        text = read_text(pyproject)
        required = ("name", "version", "description", "requires-python")
        missing = [key for key in required if not re.search(rf"(?m)^\s*{re.escape(key)}\s*=", text)]
        if "license" not in text.lower():
            missing.append("license")
        if missing:
            return [
                self.finding(
                    context,
                    message="pyproject.toml is missing useful project metadata.",
                    evidence=[Evidence("Missing keys: " + ", ".join(missing), "pyproject.toml")],
                    file="pyproject.toml",
                )
            ]
        return []


class ReadmeTopicsRule(Rule):
    definition = definition(
        "RRD111",
        "Repository lacks topic/keyword guidance in README",
        Category.METADATA,
        Severity.INFO,
        ("standard", "strict", "ml"),
        "Checks README for domain keywords or topic guidance.",
        "Keywords help readers understand scope and discover related work.",
        "Add a sentence naming the research area, methods, datasets, and intended users.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        path = readme_path(context)
        if path is None:
            return []
        text = read_text(path).lower()
        if not any(
            term in text for term in ("keywords", "topics", "research area", "dataset", "method")
        ):
            return [
                self.finding(
                    context,
                    message="README does not include explicit topic or keyword guidance.",
                    file=context.rel(path),
                )
            ]
        return []


RULES = [PyprojectMetadataRule(), ReadmeTopicsRule()]
