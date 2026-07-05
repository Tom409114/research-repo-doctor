from __future__ import annotations

import json

from typer.testing import CliRunner

from rrdoctor.cli import app
from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.reporting.agent import build_fix_plan, render_agent_json, render_agent_markdown
from rrdoctor.reporting.badge import render_badge_endpoint, render_badge_svg
from rrdoctor.scanner import Scanner

runner = CliRunner()


def test_fix_plan_orders_errors_first() -> None:
    report = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    plan = build_fix_plan(report)

    assert plan.tasks
    assert plan.tasks[0].severity.value == "error"
    assert plan.autofixable >= 1


def test_agent_markdown_is_tool_agnostic() -> None:
    report = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    rendered = render_agent_markdown(report)

    assert "Reproducibility Fix Plan" in rendered
    assert "tool-agnostic" in rendered
    assert "Verify:" in rendered
    assert "rrdoctor appendix . --profile standard --output ARTIFACT_APPENDIX.md" in rendered
    assert "rrdoctor verify . --profile standard --run --timeout 600 --fail-on error" in rendered
    assert "Do not run dynamic verification on untrusted code" in rendered


def test_agent_json_is_valid() -> None:
    report = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    payload = json.loads(render_agent_json(report))

    assert payload["tasks"]
    assert "verification" in payload["tasks"][0]


def test_badge_endpoint_and_svg() -> None:
    report = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/healthy-research-repo")
    endpoint = json.loads(render_badge_endpoint(report))

    assert endpoint["schemaVersion"] == 1
    assert endpoint["label"] == "rrdoctor"
    assert endpoint["message"] == "Reproduced-ready"

    svg = render_badge_svg(report)
    assert svg.startswith("<svg")
    assert "Reproduced-ready" in svg


def test_cli_plan_and_badge() -> None:
    plan_result = runner.invoke(app, ["plan", "tests/fixtures/missing-basics-repo"])
    badge_result = runner.invoke(
        app, ["badge", "tests/fixtures/healthy-research-repo", "--format", "svg"]
    )
    scan_agent = runner.invoke(
        app,
        ["scan", "tests/fixtures/missing-basics-repo", "--format", "agent", "--fail-on", "none"],
    )

    assert plan_result.exit_code == 0
    assert "Fix Plan" in plan_result.stdout
    assert badge_result.exit_code == 0
    assert "<svg" in badge_result.stdout
    assert scan_agent.exit_code == 0
    assert "Fix Plan" in scan_agent.stdout
