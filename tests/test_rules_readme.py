from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def test_missing_readme_rule() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD001"}).scan("tests/fixtures/missing-basics-repo")

    assert report.findings
    assert report.findings[0].rule_id == "RRD001"


def test_missing_license_rule() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD010"}).scan("tests/fixtures/missing-basics-repo")

    assert report.findings
    assert report.findings[0].rule_id == "RRD010"
