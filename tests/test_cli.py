from __future__ import annotations

import json

from typer.testing import CliRunner

from rrdoctor.cli import app

runner = CliRunner()


def test_scan_missing_basics_markdown_exits_zero_with_fail_none() -> None:
    result = runner.invoke(
        app,
        [
            "scan",
            "tests/fixtures/missing-basics-repo",
            "--format",
            "markdown",
            "--fail-on",
            "none",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert "# Research Repo Doctor Report" in result.stdout
    assert "RRD001" in result.stdout


def test_scan_missing_basics_fails_on_error() -> None:
    result = runner.invoke(app, ["scan", "tests/fixtures/missing-basics-repo", "--quiet"])

    assert result.exit_code == 1


def test_scan_healthy_json_is_valid() -> None:
    result = runner.invoke(
        app,
        [
            "scan",
            "tests/fixtures/healthy-research-repo",
            "--format",
            "json",
            "--fail-on",
            "none",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["profile"] == "standard"
    assert payload["score"] >= 70


def test_init_creates_config(tmp_path) -> None:
    config_path = tmp_path / "rrdoctor.yml"

    result = runner.invoke(app, ["init", "--output", str(config_path), "--profile", "minimal"])

    assert result.exit_code == 0
    assert "profile: minimal" in config_path.read_text(encoding="utf-8")


def test_list_rules_and_explain() -> None:
    list_result = runner.invoke(app, ["list-rules"])
    explain_result = runner.invoke(app, ["explain", "RRD001"])

    assert list_result.exit_code == 0
    assert list_result.stdout.count("RRD") >= 24
    assert explain_result.exit_code == 0
    assert "README missing" in explain_result.stdout


def test_mcp_help_preserves_extra_name() -> None:
    result = runner.invoke(app, ["mcp", "--help"])

    assert result.exit_code == 0
    assert "rrdoctor[mcp]" in result.stdout


def test_doctor_reports_mcp_optional_dependency() -> None:
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "mcp" in payload["optional_dependencies"]


def test_profile_help_lists_submission_profiles() -> None:
    scan = runner.invoke(app, ["scan", "--help"])
    init = runner.invoke(app, ["init", "--help"])

    assert scan.exit_code == 0
    assert init.exit_code == 0
    for profile in ("ml-paper", "neurips", "icml", "acm", "fair4rs", "joss"):
        assert profile in scan.stdout
        assert profile in init.stdout
