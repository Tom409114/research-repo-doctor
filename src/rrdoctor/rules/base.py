"""Base classes and helpers for deterministic rules."""

from __future__ import annotations

import re
from math import log2
from pathlib import Path

from rrdoctor.models import Category, Evidence, Finding, RuleDefinition, ScanContext, Severity

GENERIC_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-+/=]{16,})"
)
UUID_RE = re.compile(r"(?i)^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
PYTHON_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MIN_GENERIC_SECRET_ENTROPY = 3.0
PROVIDER_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"(?<![0-9A-Z])AKIA[0-9A-Z]{16}(?![0-9A-Z])"),
)
SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    GENERIC_SECRET_ASSIGNMENT_RE,
    *PROVIDER_SECRET_PATTERNS,
)


def _looks_like_random_secret(value: str) -> bool:
    stripped = value.strip("'\"` ,;)]}")
    if len(stripped) < 20:
        return False
    if UUID_RE.fullmatch(stripped):
        return False
    classes = sum(
        (
            any(char.islower() for char in stripped),
            any(char.isupper() for char in stripped),
            any(char.isdigit() for char in stripped),
            any(char in "_-+/=" for char in stripped),
        )
    )
    return (
        classes >= 2
        and len(set(stripped)) >= 8
        and _shannon_entropy_per_char(stripped) >= MIN_GENERIC_SECRET_ENTROPY
    )


def _shannon_entropy_per_char(value: str) -> float:
    if not value:
        return 0.0
    length = len(value)
    return -sum(
        (value.count(char) / length) * log2(value.count(char) / length) for char in set(value)
    )


def iter_secret_matches(value: str) -> list[re.Match[str]]:
    """Return high-confidence secret-like matches in a text fragment."""

    matches: list[re.Match[str]] = []
    for pattern in PROVIDER_SECRET_PATTERNS:
        matches.extend(pattern.finditer(value))
    for match in GENERIC_SECRET_ASSIGNMENT_RE.finditer(value):
        if _is_generated_token_marker(value, match):
            continue
        if _is_url_query_token(value, match):
            continue
        if _is_code_function_reference(value, match):
            continue
        if _looks_like_random_secret(match.group(2)):
            matches.append(match)
    return matches


def is_generic_secret_match(match: re.Match[str]) -> bool:
    """Return true when a match came from the generic key/value heuristic."""

    return match.re is GENERIC_SECRET_ASSIGNMENT_RE


def is_test_fixture_path(rel: str) -> bool:
    """Return true for paths where generic fake tokens are common test data."""

    normalized = rel.replace("\\", "/").lower()
    parts = normalized.split("/")
    fixture_dirs = {"test", "tests", "testing", "fixture", "fixtures", "testdata"}
    if any(part in fixture_dirs for part in parts):
        return True
    name = parts[-1] if parts else normalized
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith("_tests.py")
        or name in {"testing_utils.py", "testing.py"}
    )


def _is_generated_token_marker(value: str, match: re.Match[str]) -> bool:
    """Avoid treating generator provenance markers as credentials."""

    prefix = value[: match.start()].strip().lower()
    key = match.group(1).lower()
    return key == "token" and prefix.endswith("generator")


def _is_url_query_token(value: str, match: re.Match[str]) -> bool:
    """Avoid treating public asset URL query tokens as account credentials."""

    key = match.group(1).lower()
    if key != "token":
        return False
    prefix = value[: match.start()].lower()
    url_start = max(prefix.rfind("http://"), prefix.rfind("https://"))
    if url_start == -1:
        return False
    query_start = max(prefix.rfind("?"), prefix.rfind("&"))
    return query_start > url_start


def _is_code_function_reference(value: str, match: re.Match[str]) -> bool:
    """Avoid treating assignments from local function calls as credentials."""

    candidate = match.group(2).strip("'\"` ,;)]}")
    if not PYTHON_IDENTIFIER_RE.fullmatch(candidate):
        return False
    suffix = value[match.end(2) :].lstrip()
    if suffix.startswith("("):
        return True
    return bool(re.match(r"^\.[A-Za-z_][A-Za-z0-9_]*\s*\(", suffix))


def has_secret_like_value(value: str) -> bool:
    """Return true when text contains a high-confidence secret-like value."""

    return bool(iter_secret_matches(value))


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
        severity: Severity | None = None,
    ) -> Finding:
        """Create a finding using rule metadata."""

        return Finding(
            id=f"{self.definition.id}-001",
            rule_id=self.definition.id,
            title=self.definition.name,
            category=self.definition.category,
            severity=severity or self.severity(context),
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
