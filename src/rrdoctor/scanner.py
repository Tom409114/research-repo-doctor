"""Repository traversal and rule execution."""

from __future__ import annotations

import fnmatch
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rrdoctor.fixers import fixable_rule_ids
from rrdoctor.models import Finding, RuleResult, ScanContext, ScanReport, Severity
from rrdoctor.rules.registry import all_rules
from rrdoctor.scoring import score_findings


def _is_excluded(path: Path, root: Path, excludes: list[str]) -> bool:
    rel = "." if path == root else path.relative_to(root).as_posix()
    parts = set(path.relative_to(root).parts) if path != root else set()
    for pattern in excludes:
        normalized = pattern.rstrip("/")
        if (
            normalized in parts
            or rel == normalized
            or fnmatch.fnmatch(rel, normalized)
            or fnmatch.fnmatch(rel, f"{normalized}/**")
        ):
            return True
    return False


def collect_files(root: Path, config: dict[str, Any]) -> list[Path]:
    """Collect files under root while respecting configured excludes."""

    excludes = list(config.get("paths", {}).get("exclude", []))
    files: list[Path] = []
    for path in root.rglob("*"):
        if _is_excluded(path, root, excludes):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def rule_enabled(
    rule_id: str,
    profiles: tuple[str, ...],
    context: ScanContext,
    include: set[str],
    exclude: set[str],
) -> bool:
    """Determine whether a rule should run."""

    if rule_id in exclude:
        return False
    rule_config = context.config.get("rules", {}).get(rule_id, {})
    if include:
        return rule_id in include
    if "enabled" in rule_config:
        return bool(rule_config["enabled"])
    return context.profile in profiles


class Scanner:
    """Run deterministic rules over a repository."""

    def __init__(
        self,
        config: dict[str, Any],
        *,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ):
        self.config = config
        self.include = include or set()
        self.exclude = exclude or set()

    def scan(self, root: Path | str) -> ScanReport:
        """Scan a repository path and return a report."""

        resolved = Path(root).resolve()
        profile = str(self.config.get("profile", "standard"))
        files = collect_files(resolved, self.config)
        context = ScanContext(root=resolved, config=self.config, files=files, profile=profile)
        findings: list[Finding] = []
        results: list[RuleResult] = []

        for rule in all_rules():
            if not rule_enabled(
                rule.definition.id, rule.definition.profiles, context, self.include, self.exclude
            ):
                continue
            try:
                rule_findings = rule.check(context)
            except Exception as exc:
                rule_findings = [
                    rule.finding(
                        context,
                        message=f"Rule failed while scanning malformed or unexpected input: {exc}",
                        recommendation="Please report this as a bug with a minimal fixture.",
                    )
                ]
                rule_findings = [
                    Finding(
                        **{
                            **finding.__dict__,
                            "severity": Severity.WARNING,
                        }
                    )
                    for finding in rule_findings
                ]
            findings.extend(rule_findings)
            results.append(RuleResult(rule=rule.definition, findings=rule_findings))

        fixable = fixable_rule_ids()
        findings = [
            finding if finding.rule_id not in fixable else replace(finding, autofix_available=True)
            for finding in findings
        ]

        score, category_scores, summary = score_findings(findings)
        return ScanReport(
            repository_path=resolved.as_posix(),
            generated_at=datetime.now(timezone.utc).isoformat(),
            profile=profile,
            score=score,
            category_scores=category_scores,
            findings=findings,
            rules_evaluated=len(results),
            summary=summary,
        )
