from __future__ import annotations

import importlib.util
import subprocess
import sys
from base64 import b64decode
from pathlib import Path


def _load_public_readiness_script():
    path = Path("scripts/check_public_readiness.py")
    spec = importlib.util.spec_from_file_location("check_public_readiness", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_public_readiness_gate_passes_for_current_repository() -> None:
    script = _load_public_readiness_script()

    assert script.check_public_readiness(Path.cwd()) == []


def test_markdown_field_extracts_bold_report_values() -> None:
    script = _load_public_readiness_script()
    markdown = (
        "- Artifact readiness: **Reproduced-ready**\n"
        "- Heuristic score: **100/100**\n"
        "- Scanned successfully: 60\n"
    )

    assert script._markdown_field(markdown, "Artifact readiness") == "Reproduced-ready"
    assert script._markdown_field(markdown, "Heuristic score") == "100/100"
    assert script._markdown_count(markdown, "Scanned successfully") == 60


def test_action_reference_check_rejects_stale_release_tag(tmp_path) -> None:
    script = _load_public_readiness_script()
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'rrdoctor'\nversion = '0.2.21'\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "- uses: Tom409114/research-repo-doctor@v0.2.9\n",
        encoding="utf-8",
    )
    failures: list[str] = []

    script._check_action_references(tmp_path, ["README.md"], failures)

    assert failures == [
        "GitHub Action examples use stale rrdoctor release tags: "
        "README.md: Tom409114/research-repo-doctor@v0.2.9"
    ]


def test_action_reference_check_ignores_historical_release_notes(tmp_path) -> None:
    script = _load_public_readiness_script()
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'rrdoctor'\nversion = '0.2.21'\n",
        encoding="utf-8",
    )
    (tmp_path / "RELEASE_NOTES_v0.1.0.md").write_text(
        "- uses: Tom409114/research-repo-doctor@v0.1.0\n",
        encoding="utf-8",
    )
    failures: list[str] = []

    script._check_action_references(tmp_path, ["RELEASE_NOTES_v0.1.0.md"], failures)

    assert failures == []


def test_git_history_check_rejects_forbidden_historical_paths(tmp_path) -> None:
    script = _load_public_readiness_script()
    _init_repo(tmp_path)
    forbidden_path = b64decode("ZG9jcy9sYXVuY2gtY2hlY2tsaXN0Lm1k").decode("utf-8")
    path = tmp_path / forbidden_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("private release note\n", encoding="utf-8")
    _commit_all(tmp_path, "add forbidden historical path")
    path.unlink()
    _commit_all(tmp_path, "remove forbidden historical path")
    failures: list[str] = []

    script._check_git_history_internal_materials(tmp_path, failures)

    assert any("out-of-scope working files exist in git history" in item for item in failures)


def test_git_history_check_rejects_forbidden_historical_text(tmp_path) -> None:
    script = _load_public_readiness_script()
    _init_repo(tmp_path)
    forbidden_text = b64decode("QzpcVXNlcnNcdGh1YWg=").decode("utf-8")
    (tmp_path / "notes.md").write_text(f"local path: {forbidden_text}\n", encoding="utf-8")
    _commit_all(tmp_path, "add forbidden text")
    (tmp_path / "notes.md").write_text("clean\n", encoding="utf-8")
    _commit_all(tmp_path, "clean working tree")
    failures: list[str] = []

    script._check_git_history_internal_materials(tmp_path, failures)

    assert any("public git history leaks" in item for item in failures)


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "maintainer@example.invalid"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test Maintainer"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


def _commit_all(path: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
