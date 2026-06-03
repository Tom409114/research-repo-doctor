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
