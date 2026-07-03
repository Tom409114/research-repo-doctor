from __future__ import annotations

from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG, apply_cli_overrides
from rrdoctor.reporting.appendix import badge_status, render_appendix, render_checklist
from rrdoctor.scanner import Scanner
from rrdoctor.verification import (
    _entrypoint_command,
    _readme_entrypoint_command,
    _run_command,
    render_verification,
    verification_failed,
)


def _report(fixture: str, profile: str = "standard"):
    config = apply_cli_overrides(DEFAULT_CONFIG, profile=profile)
    return Scanner(config).scan(fixture)


def test_checklist_lists_acm_badges() -> None:
    report = _report("tests/fixtures/ml-project-repo", "acm")
    rendered = render_checklist(report)

    assert "ACM Artifact Evaluation badges" in rendered
    assert "Artifact Available" in rendered
    assert "Results Reproduced" in rendered
    assert "NeurIPS reproducibility checklist" in rendered


def test_appendix_has_required_sections() -> None:
    report = _report("tests/fixtures/ml-project-repo", "acm")
    rendered = render_appendix(report)

    for heading in ("# Artifact Appendix", "## Artifact check-list", "## Installation"):
        assert heading in rendered


def test_badge_status_blocks_on_missing_basics() -> None:
    report = _report("tests/fixtures/missing-basics-repo", "standard")
    tiers = {t.name: t for t in badge_status(report)}

    # A repo missing license/manifest cannot be Available or Functional.
    assert not tiers["Artifact Available"].ready
    assert not tiers["Artifact Functional"].ready


def test_verification_ladder_static_mode() -> None:
    report = _report("tests/fixtures/ml-project-repo", "standard")
    root = Path("tests/fixtures/ml-project-repo").resolve()
    rendered = render_verification(report, root, run=False)

    assert "L1" in rendered and "L2" in rendered and "L3" in rendered
    assert "static" in rendered
    assert "python scripts/train.py --config configs/default.yaml" in rendered
    # ml-project-repo has no error findings, so L1 should not be a failure.
    assert not verification_failed(report)


def test_verification_failed_on_missing_basics() -> None:
    report = _report("tests/fixtures/missing-basics-repo", "standard")

    assert verification_failed(report)


def test_run_command_missing_tool_returns_none(tmp_path) -> None:
    code, message = _run_command(["definitely-not-a-real-tool-xyz"], tmp_path, timeout=5)

    assert code is None
    assert "tool not found" in message


def test_verification_detects_root_python_entrypoint(tmp_path) -> None:
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")

    runnable, display = _entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[-1] == "train.py"
    assert display == "python train.py"


def test_verification_prefers_documented_readme_entrypoint(tmp_path) -> None:
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Demo\n\nRun `python train.py config/train_shakespeare_char.py`.\n",
        encoding="utf-8",
    )

    runnable, display = _readme_entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[-2:] == ["train.py", "config/train_shakespeare_char.py"]
    assert display == "python train.py config/train_shakespeare_char.py"


def test_verification_ignores_non_file_backed_readme_command(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nRun `make reproduce` after setting up the project.\n",
        encoding="utf-8",
    )

    runnable, display = _readme_entrypoint_command(tmp_path)

    assert runnable is None
    assert display == ""


def test_verification_detects_scripts_python_entrypoint(tmp_path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "run.py").write_text("print('run')\n", encoding="utf-8")

    runnable, display = _entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[-1] == "scripts/run.py"
    assert display == "python scripts/run.py"


def test_verification_detects_tools_python_entrypoint(tmp_path) -> None:
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "train.py").write_text("print('train')\n", encoding="utf-8")

    runnable, display = _entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[-1] == "tools/train.py"
    assert display == "python tools/train.py"


def test_verification_accepts_documented_scripts_python_command(tmp_path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "amg.py").write_text("print('generate masks')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Demo\n\n```bash\npython scripts/amg.py --input image.jpg --output masks/\n```\n",
        encoding="utf-8",
    )

    runnable, display = _readme_entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[1:] == ["scripts/amg.py", "--input", "image.jpg", "--output", "masks/"]
    assert display == "python scripts/amg.py --input image.jpg --output masks/"


def test_verification_accepts_documented_pyproject_console_script(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'demo'\n\n[project.scripts]\ndemo-transcribe = 'demo.cli:main'\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Demo\n\n```bash\ndemo-transcribe audio.wav --model tiny\n```\n",
        encoding="utf-8",
    )

    runnable, display = _readme_entrypoint_command(tmp_path)

    assert runnable == ["demo-transcribe", "audio.wav", "--model", "tiny"]
    assert display == "demo-transcribe audio.wav --model tiny"


def test_verification_ignores_console_script_name_only_inline_code(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'demo'\n\n[project.scripts]\ndemo-transcribe = 'demo.cli:main'\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Demo\n\nIf you use `demo-transcribe` in your work, please cite us.\n",
        encoding="utf-8",
    )

    runnable, display = _readme_entrypoint_command(tmp_path)

    assert runnable is None
    assert display == ""
