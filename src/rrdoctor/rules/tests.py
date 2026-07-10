"""Testing rules."""

from __future__ import annotations

import re

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, has_any_heading, read_text
from rrdoctor.rules.paths import find_files

TEST_FILE_PATTERNS = [
    "tests/**",
    "test/**",
    "test_*.py",
    "**/test_*.py",
    "**/*_test.py",
    "runtests.jl",
    "**/runtests.jl",
    "verify*.sh",
    "smoke*.sh",
    "scripts/verify*.sh",
    "scripts/smoke*.sh",
]

TEST_RUNNER_TERMS = (
    "pytest",
    "tox",
    "nox",
    "npm test",
    "ruff check",
    "cargo test",
    "cargo nextest",
    "julia-actions/julia-runtest",
    "julia-runtest",
    "pkg.test",
    "runtests.jl",
    "bazel test",
    "bazelisk test",
    "run_tests.sh",
    "run_github_tests.sh",
    "testthat",
    "test_check(",
    "r cmd check",
    "rcmdcheck",
    "bioccheck",
    "devtools::test",
)

BAZEL_TEST_TARGET_RE = re.compile(
    r"\b(?:py|sh|cc|java|go|multi_substrate_py)_test\s*\(|\btest_suite\s*\("
)
ARTIFACT_ANALYSIS_COMMAND_RE = re.compile(
    r"(?im)(^|\n)\s*(?:\$|>)?\s*(?:\./)?(?:scripts/)?analyze_all\.sh(?:\s|$)"
)


def _has_julia_test_target(text: str) -> bool:
    lowered = text.lower()
    return "[targets]" in lowered and "test" in lowered and "[extras]" in lowered


def _has_bazel_test_target(context: ScanContext) -> bool:
    has_bazel_workspace = any(
        (context.root / name).exists()
        for name in ("WORKSPACE", "WORKSPACE.bazel", "MODULE.bazel", "bazel.rc", ".bazelrc")
    )
    if not has_bazel_workspace:
        return False
    for path in find_files(context, ["BUILD", "**/BUILD", "BUILD.bazel", "**/BUILD.bazel"]):
        if BAZEL_TEST_TARGET_RE.search(read_text(path)):
            return True
    return False


def _has_artifact_smoke_script(context: ScanContext) -> bool:
    explicit = find_files(
        context,
        ["verify*.sh", "smoke*.sh", "scripts/verify*.sh", "scripts/smoke*.sh"],
    )
    if explicit:
        return True

    readme = context.root / "README.md"
    analysis_scripts = find_files(context, ["analyze_all.sh", "scripts/analyze_all.sh"])
    if not readme.exists() or not analysis_scripts:
        return False
    text = read_text(readme)
    return bool(
        has_any_heading(text, ("kick the tires", "smoke test", "artifact check"))
        and ARTIFACT_ANALYSIS_COMMAND_RE.search(text)
    )


class TestsMissingRule(Rule):
    definition = definition(
        "RRD070",
        "No tests directory or test files found",
        Category.TESTING,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks for tests, smoke scripts, or documented artifact analysis checks.",
        "Even small smoke tests help reviewers catch broken reproduction steps.",
        "Add tests/, a verify/smoke script, or a documented Kick the Tires analysis check.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not find_files(context, TEST_FILE_PATTERNS) and not _has_artifact_smoke_script(context):
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
        "Checks for pytest/tox/nox/package scripts, Cargo/Julia/Bazel tests, artifact smoke "
        "scripts, or CI test invocation.",
        "Tests are most useful when maintainers know how to run them consistently.",
        "Document or configure a test runner such as pytest, cargo test, an artifact "
        "verify/smoke script, package scripts, or Julia Pkg.test.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        markers = []
        for name in (
            "pyproject.toml",
            "tox.ini",
            "noxfile.py",
            "package.json",
            "Project.toml",
            "DESCRIPTION",
            "tests/testthat.R",
        ):
            path = context.root / name
            if path.exists():
                markers.append(read_text(path).lower())
        for test_file in find_files(context, ["test/runtests.jl", "runtests.jl"]):
            markers.append(str(test_file.relative_to(context.root)).lower())
        for workflow in find_files(
            context, [".github/workflows/*.yml", ".github/workflows/*.yaml"]
        ):
            markers.append(read_text(workflow).lower())
        combined = "\n".join(markers)
        if (
            not any(term in combined for term in TEST_RUNNER_TERMS)
            and not _has_julia_test_target(combined)
            and not _has_bazel_test_target(context)
            and not _has_artifact_smoke_script(context)
        ):
            return [
                self.finding(
                    context,
                    message="No obvious test runner or test command configuration was detected.",
                    evidence=[
                        Evidence(
                            "Searched pyproject, tox/nox, package scripts, "
                            "Cargo/Julia project metadata, documented artifact checks, "
                            "and workflows."
                        )
                    ],
                )
            ]
        return []


RULES = [TestsMissingRule(), TestRunnerMissingRule()]
