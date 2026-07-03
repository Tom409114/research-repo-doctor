from __future__ import annotations

from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.models import Severity
from rrdoctor.scanner import Scanner


def _scan(root: Path, rule_id: str):
    return Scanner(DEFAULT_CONFIG, include={rule_id}).scan(root)


def test_changelog_missing_is_informational_for_standard_scans(tmp_path) -> None:
    report = _scan(tmp_path, "RRD100")

    assert report.findings
    assert report.findings[0].severity == Severity.INFO


def test_changelog_rule_passes_when_changelog_exists(tmp_path) -> None:
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## Unreleased\n", encoding="utf-8")

    report = _scan(tmp_path, "RRD100")

    assert not report.findings
