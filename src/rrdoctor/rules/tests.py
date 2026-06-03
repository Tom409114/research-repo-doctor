"""Testing rules."""

from __future__ import annotations

from rrdoctor.models import Category, Evidence, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, read_text
from rrdoctor.rules.paths import find_files


class TestsMissingRule(Rule):
    definition = definition(
        "RRD070",
        "No tests directory or test files found",
        Category.TESTING,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks for tests or test files.",
        "Even small smoke tests help reviewers catch broken reproduction steps.",
        "Add tests/ or at least one test_*.py / *_test.py file.",
    )

    def check(self, context: ScanContext):
        if not find_files(context, ["tests/**", "test_*.py", "**/test_*.py", "**/*_test.py"]):
            return [
                self.finding(context, message="No tests directory or test files were detected.")
            ]
        return []


class TestRunnerMissingRule(Rule):
    definition = definition(
        "RRD071",
        "No test runner/configuration detected",
        Category.TESTING,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks for pytest/tox/nox/package scripts or CI test invocation.",
        "Tests are most useful when maintainers know how to run them consistently.",
        "Document or configure a test runner such as pytest, tox, nox, or package scripts.",
    )

    def check(self, context: ScanContext):
        markers = []
        for name in ("pyproject.toml", "tox.ini", "noxfile.py", "package.json"):
            path = context.root / name
            if path.exists():
                markers.append(read_text(path).lower())
        for workflow in find_files(
            context, [".github/workflows/*.yml", ".github/workflows/*.yaml"]
        ):
            markers.append(read_text(workflow).lower())
        combined = "\n".join(markers)
        if not any(term in combined for term in ("pytest", "tox", "nox", "npm test", "ruff check")):
            return [
                self.finding(
                    context,
                    message="No obvious test runner or test command configuration was detected.",
                    evidence=[
                        Evidence("Searched pyproject, tox/nox, package scripts, and workflows.")
                    ],
                )
            ]
        return []


RULES = [TestsMissingRule(), TestRunnerMissingRule()]
