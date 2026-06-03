from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def test_environment_detection_present() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD030", "RRD031"}).scan(
        "tests/fixtures/healthy-research-repo"
    )

    assert not report.findings


def test_environment_detection_missing() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD030"}).scan("tests/fixtures/missing-basics-repo")

    assert report.findings[0].rule_id == "RRD030"
