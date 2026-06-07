from __future__ import annotations

from typer.testing import CliRunner

from rrdoctor.baseline import diff_against_baseline
from rrdoctor.cli import app
from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.reporting.json_report import render_json
from rrdoctor.scanner import Scanner

runner = CliRunner()


def test_diff_reports_fixed_and_no_new(tmp_path) -> None:
    baseline = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(render_json(baseline), encoding="utf-8")

    healthy = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/healthy-research-repo")
    diff = diff_against_baseline(healthy, baseline_path)

    assert not diff.new
    assert diff.fixed
    assert not diff.regressed
    assert diff.current_score >= (diff.baseline_score or 0)


def test_diff_detects_new_findings(tmp_path) -> None:
    baseline = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/healthy-research-repo")
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(render_json(baseline), encoding="utf-8")

    worse = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    diff = diff_against_baseline(worse, baseline_path)

    assert diff.new
    assert diff.regressed


def test_cli_fail_on_new_passes_when_only_fixed(tmp_path) -> None:
    baseline = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(render_json(baseline), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "scan",
            "tests/fixtures/healthy-research-repo",
            "--baseline",
            str(baseline_path),
            "--fail-on-new",
            "error",
            "--quiet",
        ],
    )
    assert result.exit_code == 0


def test_cli_fail_on_new_fails_on_regression(tmp_path) -> None:
    baseline = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/healthy-research-repo")
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(render_json(baseline), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "scan",
            "tests/fixtures/missing-basics-repo",
            "--baseline",
            str(baseline_path),
            "--fail-on-new",
            "error",
            "--quiet",
        ],
    )
    assert result.exit_code == 1


def test_cli_fail_on_new_requires_baseline() -> None:
    result = runner.invoke(
        app, ["scan", "tests/fixtures/healthy-research-repo", "--fail-on-new", "error"]
    )
    assert result.exit_code != 0
