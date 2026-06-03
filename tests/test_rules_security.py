from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def test_secret_masking() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD090"}).scan("tests/fixtures/notebook-issues-repo")

    assert report.findings
    evidence = report.findings[0].evidence[0].value or ""
    assert "..." in evidence
    assert "abcdefghijklmnopqrstuvwxyz" not in evidence


def test_gitignore_rule() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD091"}).scan("tests/fixtures/missing-basics-repo")

    assert report.findings
    assert report.findings[0].rule_id == "RRD091"
