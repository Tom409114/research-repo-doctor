"""Typed models shared by the scanner, rules, and reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    """Finding severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Category(str, Enum):
    """Research repository audit categories."""

    DOCUMENTATION = "documentation"
    REPRODUCIBILITY = "reproducibility"
    DATA = "data"
    ENVIRONMENT = "environment"
    EXPERIMENTS = "experiments"
    NOTEBOOKS = "notebooks"
    CITATION = "citation"
    GOVERNANCE = "governance"
    TESTING = "testing"
    CI = "ci"
    SECURITY = "security"
    RELEASE = "release"
    METADATA = "metadata"


@dataclass(frozen=True)
class Evidence:
    """A small, masked piece of evidence supporting a finding."""

    message: str
    file: str | None = None
    line: int | None = None
    value: str | None = None


@dataclass(frozen=True)
class Finding:
    """A single actionable issue found during a repository scan."""

    id: str
    rule_id: str
    title: str
    category: Category
    severity: Severity
    message: str
    evidence: list[Evidence] = field(default_factory=list)
    recommendation: str = ""
    docs_url: str | None = None
    docs_anchor: str | None = None
    file: str | None = None
    line: int | None = None
    autofix_available: bool = False


@dataclass(frozen=True)
class RuleDefinition:
    """Static metadata for a rule."""

    id: str
    name: str
    category: Category
    severity: Severity
    profiles: tuple[str, ...]
    description: str
    rationale: str
    remediation: str
    examples: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuleResult:
    """Findings emitted by a rule."""

    rule: RuleDefinition
    findings: list[Finding] = field(default_factory=list)


@dataclass
class ScanContext:
    """Context object passed to rules during a scan."""

    root: Path
    config: dict[str, Any]
    files: list[Path]
    profile: str

    def rel(self, path: Path) -> str:
        """Return a stable repository-relative path."""

        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()

    def exists_any(self, candidates: list[str]) -> bool:
        """Return true when any candidate path exists under the root."""

        return any((self.root / candidate).exists() for candidate in candidates)

    def matching_files(self, suffixes: tuple[str, ...]) -> list[Path]:
        """Return scanned files whose names end with one of the given suffixes."""

        return [path for path in self.files if path.name.endswith(suffixes)]


@dataclass(frozen=True)
class CategoryScore:
    """Score summary for a category."""

    category: Category
    score: int
    errors: int
    warnings: int
    infos: int


@dataclass(frozen=True)
class ScanReport:
    """Complete scan report."""

    repository_path: str
    generated_at: str
    profile: str
    score: int
    category_scores: list[CategoryScore]
    findings: list[Finding]
    rules_evaluated: int
    summary: dict[str, int]
    heuristic_note: str = (
        "Research Repo Doctor uses deterministic heuristics. The score is a guide, "
        "not a substitute for peer review or maintainer judgment."
    )

    @classmethod
    def empty(cls, repository_path: str, profile: str) -> ScanReport:
        """Create an empty report."""

        return cls(
            repository_path=repository_path,
            generated_at=datetime.now(timezone.utc).isoformat(),
            profile=profile,
            score=100,
            category_scores=[],
            findings=[],
            rules_evaluated=0,
            summary={"error": 0, "warning": 0, "info": 0},
        )


def to_jsonable(value: Any) -> Any:
    """Convert dataclasses and enums to JSON-friendly values."""

    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return value.as_posix()
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    return value
