from __future__ import annotations

import json

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.reporting.json_report import render_json
from rrdoctor.reporting.markdown import render_markdown
from rrdoctor.reporting.sarif import render_sarif
from rrdoctor.scanner import Scanner


def test_markdown_report_generation() -> None:
    report = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    rendered = render_markdown(report)

    assert "# Research Repo Doctor Report" in rendered
    assert "How to fix first" in rendered
    assert "Suggested GitHub issues" in rendered


def test_json_report_generation() -> None:
    report = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/healthy-research-repo")
    payload = json.loads(render_json(report))

    assert payload["repository_path"]
    assert "findings" in payload


def test_sarif_report_generation() -> None:
    report = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    payload = json.loads(render_sarif(report))

    assert payload["version"] == "2.1.0"
    assert payload["runs"][0]["tool"]["driver"]["name"] == "Research Repo Doctor"
