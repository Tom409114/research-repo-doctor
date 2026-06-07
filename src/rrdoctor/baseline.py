"""Compare a current scan against a stored baseline report.

This enables PR automation that gates only on *newly introduced* findings, so a
team can adopt the audit on a large legacy repository without having to fix
everything before the first green build.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rrdoctor.models import DiffResult, Finding, ScanReport


def load_baseline_fingerprints(path: Path) -> tuple[set[str], int | None]:
    """Load finding fingerprints and score from a baseline JSON report.

    The baseline is a report produced by ``rrdoctor scan --format json``. Only the
    rule id and location are used, so baselines stay stable across versions.
    """

    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Baseline must be a JSON object: {path}")
    fingerprints: set[str] = set()
    for finding in data.get("findings", []):
        if not isinstance(finding, dict):
            continue
        rule_id = str(finding.get("rule_id", ""))
        file = finding.get("file") or ""
        line = finding.get("line")
        line_part = str(line) if line else ""
        fingerprints.add(f"{rule_id}|{file}|{line_part}")
    score = data.get("score")
    return fingerprints, score if isinstance(score, int) else None


def diff_against_baseline(report: ScanReport, baseline_path: Path) -> DiffResult:
    """Return the difference between a current report and a baseline report."""

    baseline_fps, baseline_score = load_baseline_fingerprints(baseline_path)
    current_fps = {finding.fingerprint for finding in report.findings}

    new: list[Finding] = []
    unchanged: list[Finding] = []
    for finding in report.findings:
        if finding.fingerprint in baseline_fps:
            unchanged.append(finding)
        else:
            new.append(finding)

    fixed_fps = baseline_fps - current_fps
    fixed = [_placeholder_finding(fp) for fp in sorted(fixed_fps)]

    return DiffResult(
        new=new,
        fixed=fixed,
        unchanged=unchanged,
        baseline_score=baseline_score,
        current_score=report.score,
    )


def _placeholder_finding(fingerprint: str) -> Finding:
    """Reconstruct a minimal finding from a baseline fingerprint for reporting."""

    from rrdoctor.models import Category, Severity

    rule_id, file, line = [*fingerprint.split("|"), "", ""][:3]
    return Finding(
        id=f"{rule_id}-fixed",
        rule_id=rule_id,
        title="(resolved since baseline)",
        category=Category.METADATA,
        severity=Severity.INFO,
        message="This finding was present in the baseline and is no longer reported.",
        file=file or None,
        line=int(line) if line.isdigit() else None,
    )
