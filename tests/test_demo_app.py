from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from subprocess import CompletedProcess
from types import SimpleNamespace

import pytest


def _load_demo_app():
    path = Path("demo/app.py")
    spec = importlib.util.spec_from_file_location("rrdoctor_demo_app", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_github_url_accepts_common_repo_forms() -> None:
    app = _load_demo_app()

    target = app.parse_github_url("https://github.com/Tom409114/research-repo-doctor.git")

    assert target.owner == "Tom409114"
    assert target.repo == "research-repo-doctor"
    assert target.clone_url == "https://github.com/Tom409114/research-repo-doctor.git"


def test_demo_requirements_pin_does_not_exceed_project_version() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    requirements = Path("demo/requirements.txt").read_text(encoding="utf-8")

    version_line = next(line for line in pyproject.splitlines() if line.startswith("version = "))
    version = version_line.split('"', 2)[1]

    match = re.search(r"(?m)^rrdoctor==(\d+\.\d+\.\d+)$", requirements)

    assert match is not None
    demo_version = tuple(int(part) for part in match.group(1).split("."))
    project_version = tuple(int(part) for part in version.split("."))
    assert demo_version <= project_version


def test_demo_version_label_uses_installed_package_metadata(monkeypatch) -> None:
    app = _load_demo_app()

    monkeypatch.setattr(app, "package_version", lambda package_name: "9.8.7")

    assert app.rrdoctor_version_label() == "9.8.7"


def test_demo_version_label_falls_back_to_module_version(monkeypatch) -> None:
    app = _load_demo_app()

    def missing_package(_package_name):
        raise app.PackageNotFoundError

    monkeypatch.setattr(app, "package_version", missing_package)
    monkeypatch.setattr(
        app.importlib,
        "import_module",
        lambda module_name: SimpleNamespace(__version__="1.2.3"),
    )

    assert app.rrdoctor_version_label() == "1.2.3"


def test_parse_github_url_rejects_non_github_url() -> None:
    app = _load_demo_app()

    with pytest.raises(app.DemoError):
        app.parse_github_url("https://example.com/not/a-repo")


def test_sample_repository_urls_are_valid_github_targets() -> None:
    app = _load_demo_app()

    sample_urls = app.sample_repository_urls()

    assert "https://github.com/Tom409114/research-repo-doctor" in sample_urls
    assert sample_urls
    for url in sample_urls:
        target = app.parse_github_url(url)
        assert target.owner
        assert target.repo


def test_prioritize_findings_puts_unseeded_randomness_first() -> None:
    app = _load_demo_app()
    findings = [
        {"rule_id": "RRD070", "severity": "error"},
        {"rule_id": "RRD091", "severity": "warning"},
        {"rule_id": "RRD052", "severity": "warning"},
    ]

    ordered = app.prioritize_findings(findings)

    assert [item["rule_id"] for item in ordered] == ["RRD052", "RRD070", "RRD091"]


def test_prioritize_findings_limits_output() -> None:
    app = _load_demo_app()
    findings = [{"rule_id": f"RRD{i:03d}", "severity": "warning"} for i in range(10)]

    assert len(app.prioritize_findings(findings, limit=5)) == 5


def test_scan_command_uses_static_json_rrdoctor_scan(monkeypatch, tmp_path) -> None:
    app = _load_demo_app()
    captured: dict[str, list[str]] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        return CompletedProcess(
            command,
            0,
            stdout='{"score": 100, "summary": {}, "findings": []}',
            stderr="",
        )

    monkeypatch.setattr(app.subprocess, "run", fake_run)

    report = app.run_rrdoctor_scan(tmp_path)

    assert report["score"] == 100
    assert captured["command"][1:4] == ["-m", "rrdoctor", "scan"]
    assert "--format" in captured["command"]
    assert "json" in captured["command"]
    assert "--fail-on" in captured["command"]
    assert "none" in captured["command"]
    assert "--quiet" in captured["command"]
    assert "verify" not in captured["command"]


def test_demo_avoids_streamlit_metric_frontend_component() -> None:
    source = Path("demo/app.py").read_text(encoding="utf-8")

    assert ".metric(" not in source


def test_demo_links_scan_results_to_trial_report_form() -> None:
    app = _load_demo_app()
    source = Path("demo/app.py").read_text(encoding="utf-8")

    assert app.TRIAL_REPORT_URL == (
        "https://github.com/Tom409114/research-repo-doctor/issues/new?template=trial_report.yml"
    )
    assert "Share a 10-minute trial report" in source
