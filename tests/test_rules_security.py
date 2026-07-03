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


def test_gitignore_rule_allows_basic_research_coverage(tmp_path) -> None:
    (tmp_path / ".gitignore").write_text(
        "__pycache__/\n*.pyc\n.ipynb_checkpoints/\noutputs/\n.env\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD091"}).scan(tmp_path)

    assert not report.findings


def test_gitignore_rule_flags_low_coverage_file(tmp_path) -> None:
    (tmp_path / ".gitignore").write_text(".DS_Store\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD091"}).scan(tmp_path)

    assert report.findings
    assert "little coverage" in report.findings[0].message
