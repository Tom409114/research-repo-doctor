"""Base classes and helpers for deterministic rules."""

from __future__ import annotations

import re
from pathlib import Path

from rrdoctor.models import Category, Evidence, Finding, RuleDefinition, ScanContext, Severity

SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
)


def mask_secret(value: str) -> str:
    """Mask long secret-like values before evidence is reported."""

    def repl(match: re.Match[str]) -> str:
        text = match.group(0)
        if len(text) <= 8:
            return "***"
        return f"{text[:4]}...{text[-4:]}"

    masked = value
    for pattern in SECRET_PATTERNS:
        masked = pattern.sub(repl, masked)
    if len(masked) > 180:
        return f"{masked[:177]}..."
    return masked


def read_text(path: Path) -> str:
    """Best-effort text read that never raises for malformed files."""

    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def has_any_heading(text: str, words: tuple[str, ...]) -> bool:
    """Return true if Markdown-ish text contains one of the words in headings."""

    lowered = text.lower()
    return any(re.search(rf"(^|\n)\s*#+\s*.*{re.escape(word.lower())}", lowered) for word in words)


def line_for(text: str, needle_pattern: str) -> int | None:
    """Return the first line matching a regex pattern."""

    pattern = re.compile(needle_pattern, re.IGNORECASE)
    for index, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            return index
    return None


class Rule:
    """Base class for repository audit rules."""

    definition: RuleDefinition

    def check(self, context: ScanContext) -> list[Finding]:
        """Run a rule against a scan context."""

        raise NotImplementedError

    def severity(self, context: ScanContext) -> Severity:
        """Return severity after config overrides."""

        rule_config = context.config.get("rules", {}).get(self.definition.id, {})
        raw = rule_config.get("severity", self.definition.severity.value)
        return Severity(raw)

    def finding(
        self,
        context: ScanContext,
        *,
        message: str,
        evidence: list[Evidence] | None = None,
        recommendation: str | None = None,
        file: str | None = None,
        line: int | None = None,
    ) -> Finding:
        """Create a finding using rule metadata."""

        return Finding(
            id=f"{self.definition.id}-001",
            rule_id=self.definition.id,
            title=self.definition.name,
            category=self.definition.category,
            severity=self.severity(context),
            message=message,
            evidence=evidence or [],
            recommendation=recommendation or self.definition.remediation,
            docs_anchor=f"#{self.definition.id.lower()}",
            file=file,
            line=line,
        )


def definition(
    rule_id: str,
    name: str,
    category: Category,
    severity: Severity,
    profiles: tuple[str, ...],
    description: str,
    rationale: str,
    remediation: str,
    examples: tuple[str, ...] = (),
) -> RuleDefinition:
    """Compact helper for rule metadata."""

    return RuleDefinition(
        id=rule_id,
        name=name,
        category=category,
        severity=severity,
        profiles=profiles,
        description=description,
        rationale=rationale,
        remediation=remediation,
        examples=examples,
    )
