"""CI rules."""

from __future__ import annotations

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, read_text
from rrdoctor.rules.paths import find_files


class CiMissingRule(Rule):
    definition = definition(
        "RRD080",
        "No CI workflow detected",
        Category.CI,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks for GitHub Actions or other CI configuration.",
        "CI catches broken setup and reproduction commands before release.",
        "Add a GitHub Actions workflow or another CI configuration that runs tests/linting.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not find_files(
            context,
            [
                ".github/workflows/*.yml",
                ".github/workflows/*.yaml",
                ".gitlab-ci.yml",
                "azure-pipelines.yml",
            ],
        ):
            return [self.finding(context, message="No CI configuration was detected.")]
        return []


class CiNoTestsRule(Rule):
    definition = definition(
        "RRD081",
        "CI lacks obvious test or lint step",
        Category.CI,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks CI workflows for test or lint commands.",
        "CI should do more than build; it should exercise reproducibility checks.",
        "Add test, lint, or rrdoctor scan steps to CI.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        workflows = find_files(
            context, [".github/workflows/*.yml", ".github/workflows/*.yaml", ".gitlab-ci.yml"]
        )
        if not workflows:
            return []
        combined = "\n".join(read_text(path).lower() for path in workflows)
        if not any(
            term in combined for term in ("pytest", "ruff", "tox", "nox", "npm test", "rrdoctor")
        ):
            return [
                self.finding(
                    context,
                    message="CI exists but no obvious test/lint step was found.",
                    evidence=[
                        Evidence(
                            "Workflow text lacks pytest, ruff, tox, nox, npm test, or rrdoctor."
                        )
                    ],
                )
            ]
        return []


RULES = [CiMissingRule(), CiNoTestsRule()]
