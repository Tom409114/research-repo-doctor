"""Security hygiene rules."""

from __future__ import annotations

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, has_secret_like_value, mask_secret, read_text
from rrdoctor.rules.paths import text_files

COMMON_GITIGNORE_TERMS = (
    ".env",
    "__pycache__",
    ".ipynb_checkpoints",
    "data/raw",
    "outputs",
    "checkpoints",
    "wandb",
    "mlruns",
)
GITIGNORE_COVERAGE_GROUPS = {
    "credentials": (".env", "*.env", ".env*", "secret", "secrets", "credentials"),
    "python_caches": ("__pycache__", "*.pyc", "*.pyo", "*.pyd", ".pytest_cache"),
    "notebook_checkpoints": (".ipynb_checkpoints", "ipynb_checkpoints"),
    "generated_outputs": ("outputs", "output", "results", "checkpoints", "wandb", "mlruns"),
}


class PotentialSecretRule(Rule):
    definition = definition(
        "RRD090",
        "Potential committed secret detected",
        Category.SECURITY,
        Severity.ERROR,
        ("standard", "strict", "ml"),
        "Checks text files for conservative secret-like patterns.",
        "Accidentally committed credentials can compromise accounts and data.",
        "Remove and rotate the secret; store credentials in env vars or secret managers.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        for path in text_files(context):
            if path.suffix.lower() in {".cff"}:
                continue
            text = read_text(path)
            for line_number, line in enumerate(text.splitlines(), start=1):
                if has_secret_like_value(line):
                    rel = context.rel(path)
                    return [
                        self.finding(
                            context,
                            message="A possible committed secret was detected. Evidence is masked.",
                            evidence=[
                                Evidence(
                                    "Potential secret-like string.",
                                    rel,
                                    line_number,
                                    mask_secret(line),
                                )
                            ],
                            file=rel,
                            line=line_number,
                        )
                    ]
        return []


class GitignoreResearchArtifactsRule(Rule):
    definition = definition(
        "RRD091",
        ".gitignore missing common research artifacts",
        Category.SECURITY,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks .gitignore for basic generated-artifact and credential hygiene.",
        "Ignoring generated outputs reduces accidental data and credential leakage.",
        "Add entries for .env, caches, notebook checkpoints, generated outputs, and raw data.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        gitignore = context.root / ".gitignore"
        if not gitignore.exists():
            return [self.finding(context, message=".gitignore is missing.")]
        text = read_text(gitignore)
        covered = _gitignore_coverage_groups(text)
        if len(covered) < 2:
            missing = sorted(set(GITIGNORE_COVERAGE_GROUPS) - covered)
            return [
                self.finding(
                    context,
                    message=".gitignore has little coverage for generated or sensitive artifacts.",
                    evidence=[
                        Evidence(
                            "Missing coverage groups: " + ", ".join(missing),
                            ".gitignore",
                        )
                    ],
                    file=".gitignore",
                )
            ]
        return []


def _gitignore_coverage_groups(text: str) -> set[str]:
    lowered = text.lower()
    covered: set[str] = set()
    for group, terms in GITIGNORE_COVERAGE_GROUPS.items():
        if any(term.lower() in lowered for term in terms):
            covered.add(group)
    return covered


RULES = [PotentialSecretRule(), GitignoreResearchArtifactsRule()]
