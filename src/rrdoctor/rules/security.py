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
        "Checks .gitignore for common generated research artifacts.",
        "Ignoring generated outputs reduces accidental data and credential leakage.",
        "Add entries for .env, caches, raw data, checkpoints, wandb, and mlruns.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        gitignore = context.root / ".gitignore"
        if not gitignore.exists():
            return [self.finding(context, message=".gitignore is missing.")]
        text = read_text(gitignore)
        missing = [term for term in COMMON_GITIGNORE_TERMS if term not in text]
        if missing:
            return [
                self.finding(
                    context,
                    message=".gitignore is missing common research artifact entries.",
                    evidence=[Evidence("Missing entries: " + ", ".join(missing[:6]), ".gitignore")],
                    file=".gitignore",
                )
            ]
        return []


RULES = [PotentialSecretRule(), GitignoreResearchArtifactsRule()]
