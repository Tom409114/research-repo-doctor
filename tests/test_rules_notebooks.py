from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG, deep_merge
from rrdoctor.scanner import Scanner


def test_notebook_large_output_detection() -> None:
    config = deep_merge(DEFAULT_CONFIG, {"thresholds": {"large_notebook_output_kb": 1}})
    report = Scanner(config, include={"RRD060"}).scan("tests/fixtures/notebook-issues-repo")

    assert any(finding.rule_id == "RRD060" for finding in report.findings)


def test_notebook_absolute_path_detection() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD062"}).scan("tests/fixtures/notebook-issues-repo")

    assert any(finding.rule_id == "RRD062" for finding in report.findings)


def test_notebook_out_of_order_detection() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD061"}).scan("tests/fixtures/notebook-issues-repo")

    assert any(finding.rule_id == "RRD061" for finding in report.findings)
