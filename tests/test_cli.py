from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

import rrdoctor
from rrdoctor import cli as cli_module
from rrdoctor.cli import app
from rrdoctor.verification import LadderStep

runner = CliRunner()


def test_version_option_reports_package_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"rrdoctor {rrdoctor.__version__}"


def test_no_args_shows_help() -> None:
    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "scan" in result.stdout


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


def test_module_importable_requires_successful_import(monkeypatch) -> None:
    def fail_import(module: str) -> None:
        raise ModuleNotFoundError(f"{module} missing transitive dependency")

    monkeypatch.setattr(cli_module.importlib, "import_module", fail_import)

    assert not cli_module._module_importable("mcp.server.fastmcp")


def test_doctor_reports_unusable_mcp_as_false(monkeypatch) -> None:
    def fake_importable(module: str) -> bool:
        return module != "mcp.server.fastmcp"

    monkeypatch.setattr(cli_module, "_module_importable", fake_importable)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["optional_dependencies"]["mcp"] is False


def test_verify_run_exits_nonzero_when_dynamic_step_fails(monkeypatch) -> None:
    original_build_report = cli_module._build_report

    def fake_build_report(path, profile, config):
        return original_build_report("tests/fixtures/ml-project-repo", profile, config)

    def fake_build_steps(report, root, run, timeout, command=None):
        assert run is True
        assert command is None
        return [
            LadderStep("L1", "Static release hygiene", "pass", "ok"),
            LadderStep("L2", "Environment is resolvable", "pass", "ok"),
            LadderStep("L3", "Declared entrypoint produces output", "fail", "exit 7"),
        ]

    monkeypatch.setattr(cli_module, "_build_report", fake_build_report)
    monkeypatch.setattr(cli_module, "build_steps", fake_build_steps)

    result = runner.invoke(app, ["verify", ".", "--run"])

    assert result.exit_code == 1
    assert "FAIL" in result.stdout


def test_verify_command_override_is_passed_to_ladder(monkeypatch) -> None:
    original_build_report = cli_module._build_report

    def fake_build_report(path, profile, config):
        return original_build_report("tests/fixtures/ml-project-repo", profile, config)

    def fake_build_steps(report, root, run, timeout, command=None):
        assert run is False
        assert command == "python smoke.py --quick"
        return [
            LadderStep("L1", "Static release hygiene", "pass", "ok"),
            LadderStep("L2", "Environment is resolvable", "skipped", "static"),
            LadderStep(
                "L3",
                "Declared entrypoint produces output",
                "skipped",
                "static",
                commands=["python smoke.py --quick"],
            ),
        ]

    monkeypatch.setattr(cli_module, "_build_report", fake_build_report)
    monkeypatch.setattr(cli_module, "build_steps", fake_build_steps)

    result = runner.invoke(app, ["verify", ".", "--command", "python smoke.py --quick"])

    assert result.exit_code == 0
    assert "- L3 command: `python smoke.py --quick`" in result.stdout
    assert "python smoke.py --quick" in result.stdout


def test_verify_command_rejects_unparseable_command() -> None:
    result = runner.invoke(app, ["verify", ".", "--command", "python 'unterminated"])

    assert result.exit_code != 0
    assert "Usage:" in result.stderr


def test_prepare_writes_ae_packet(tmp_path) -> None:
    out_dir = tmp_path / "packet"

    result = runner.invoke(
        app,
        [
            "prepare",
            "tests/fixtures/ml-project-repo",
            "--profile",
            "acm",
            "--out-dir",
            str(out_dir),
            "--command",
            "python scripts/train.py --config configs/default.yaml",
        ],
    )

    assert result.exit_code == 0
    expected = {
        "README.md",
        "rrdoctor-report.md",
        "rrdoctor-plan.md",
        "ARTIFACT_APPENDIX.md",
        "rrdoctor-verify.md",
    }
    assert {path.name for path in out_dir.iterdir()} == expected
    index = (out_dir / "README.md").read_text(encoding="utf-8")
    verify = (out_dir / "rrdoctor-verify.md").read_text(encoding="utf-8")
    assert "Artifact Evaluation Prep Packet" in index
    assert "rrdoctor-plan.md" in index
    assert "python scripts/train.py --config configs/default.yaml" in verify
    assert "- L3 command: `python scripts/train.py --config configs/default.yaml`" in verify


def test_prepare_fail_on_error_writes_packet_then_exits_nonzero(tmp_path) -> None:
    out_dir = tmp_path / "packet"

    result = runner.invoke(
        app,
        [
            "prepare",
            "tests/fixtures/missing-basics-repo",
            "--out-dir",
            str(out_dir),
            "--fail-on",
            "error",
        ],
    )

    assert result.exit_code == 1
    assert (out_dir / "rrdoctor-report.md").exists()
    assert "Needs preparation" in (out_dir / "README.md").read_text(encoding="utf-8")


def test_prepare_accepts_warning_failure_threshold(tmp_path) -> None:
    out_dir = tmp_path / "packet"

    result = runner.invoke(
        app,
        [
            "prepare",
            "tests/fixtures/ml-project-repo",
            "--profile",
            "standard",
            "--out-dir",
            str(out_dir),
            "--fail-on",
            "warning",
        ],
    )

    assert result.exit_code == 0
    assert (out_dir / "rrdoctor-report.md").exists()


def test_prepare_refuses_repository_root_output_dir() -> None:
    readme = Path("tests/fixtures/ml-project-repo/README.md")
    original = readme.read_text(encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "prepare",
            "tests/fixtures/ml-project-repo",
            "--out-dir",
            "tests/fixtures/ml-project-repo",
        ],
    )

    assert result.exit_code != 0
    assert "Usage:" in result.stderr
    assert readme.read_text(encoding="utf-8") == original


def test_profile_help_lists_submission_profiles() -> None:
    scan = runner.invoke(app, ["scan", "--help"])
    init = runner.invoke(app, ["init", "--help"])

    assert scan.exit_code == 0
    assert init.exit_code == 0
    for profile in ("ml-paper", "neurips", "icml", "acm", "fair4rs", "joss"):
        assert profile in scan.stdout
        assert profile in init.stdout
    assert "prepare" in runner.invoke(app, ["--help"]).stdout
