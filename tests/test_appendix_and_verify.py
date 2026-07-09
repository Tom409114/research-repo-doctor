from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG, apply_cli_overrides
from rrdoctor.models import ScanReport
from rrdoctor.reporting.appendix import badge_status, render_appendix, render_checklist
from rrdoctor.scanner import Scanner
from rrdoctor.verification import (
    LadderStep,
    _build_plan,
    _entrypoint_command,
    _l2_step,
    _readme_entrypoint_command,
    _run_command,
    build_steps,
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
    assert "This artifact package contains `ml-project-repo`" in rendered
    assert "ML fixture" in rendered
    assert "`pyproject.toml`" in rendered
    assert "`data/README.md`" in rendered
    assert "`results/README.md`" in rendered
    assert "`configs/default.yaml`" in rendered
    assert "python scripts/train.py --config configs/default.yaml" in rendered


def test_appendix_uses_setup_py_metadata_without_executing(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Setup Py Demo\n\nA tiny legacy package artifact.\n\n```bash\npython train.py\n```\n",
        encoding="utf-8",
    )
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup\n\n"
        'NAME = "setup-py-demo"\n'
        'VERSION = "0.5.0"\n'
        'raise RuntimeError("appendix must never execute setup.py")\n'
        "setup(\n"
        "    name=NAME,\n"
        "    version=VERSION,\n"
        '    url="git@github.com:example/setup-py-demo.git",\n'
        ")\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG).scan(tmp_path)
    rendered = render_appendix(report)

    assert "This artifact package contains `setup-py-demo`" in rendered
    assert "Repository URL: <https://github.com/example/setup-py-demo>." in rendered
    assert "Version: `0.5.0`." in rendered


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
    assert "Gate outcome: **PASS**" in rendered
    assert "Failure threshold: `error`" in rendered
    assert "static mode did not execute target-repository code" in rendered
    assert "L3 command source: README command." in rendered
    assert "Static mode. L3 command source: README command." in rendered
    assert "Recommended rerun:" in rendered
    assert "cd <repository-root>" in rendered
    assert "rrdoctor verify . --profile standard --timeout 300 --fail-on error" in rendered
    assert str(root) not in rendered
    assert "python scripts/train.py --config configs/default.yaml" in rendered
    # ml-project-repo has no error findings, so L1 should not be a failure.
    assert not verification_failed(report)


def test_verification_ladder_accepts_specified_l3_command(tmp_path) -> None:
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")
    (tmp_path / "smoke.py").write_text("print('smoke')\n", encoding="utf-8")
    report = Scanner(DEFAULT_CONFIG).scan(tmp_path)

    steps = build_steps(report, tmp_path, run=False, timeout=30, command="python smoke.py --quick")
    rendered = render_verification(
        report,
        tmp_path,
        run=False,
        timeout=30,
        steps=steps,
        command="python smoke.py --quick",
    )

    assert steps[2].commands == ["python smoke.py --quick"]
    assert "python train.py" not in rendered
    assert "- L3 command: `python smoke.py --quick`" in rendered
    assert "L3 command source: specified --command." in rendered
    assert "rrdoctor verify . --profile standard --timeout 30 --fail-on error --command" in rendered


def test_verification_summary_reports_dynamic_failure() -> None:
    report = _report("tests/fixtures/ml-project-repo", "standard")
    root = Path("tests/fixtures/ml-project-repo").resolve()
    steps = [
        LadderStep("L1", "Static release hygiene", "pass", "ok"),
        LadderStep("L2", "Environment is resolvable", "pass", "ok"),
        LadderStep(
            "L3",
            "Declared entrypoint produces output",
            "fail",
            "Entrypoint failed (exit 7). Command source: README command. See log.",
            source="README command",
        ),
    ]

    rendered = render_verification(report, root, run=True, timeout=10, steps=steps)

    assert "Gate outcome: **FAIL**" in rendered
    assert "dynamic mode executed target-repository commands" in rendered
    assert "L3 command source: README command." in rendered
    assert (
        "| L3 | Declared entrypoint produces output | FAIL | "
        "Entrypoint failed (exit 7). Command source: README command. See log. |"
    ) in rendered
    assert "rrdoctor verify . --profile standard --timeout 10 --fail-on error --run" in rendered


def test_verification_failed_on_missing_basics() -> None:
    report = _report("tests/fixtures/missing-basics-repo", "standard")

    assert verification_failed(report)


def test_verification_failed_includes_dynamic_step_failures() -> None:
    report = _report("tests/fixtures/ml-project-repo", "standard")
    steps = [
        LadderStep("L1", "Static release hygiene", "pass", "ok"),
        LadderStep("L2", "Environment is resolvable", "pass", "ok"),
        LadderStep("L3", "Declared entrypoint produces output", "fail", "exit 7"),
    ]

    assert verification_failed(report, steps)


def test_verification_failed_respects_warning_threshold() -> None:
    report = replace(
        ScanReport.empty(".", "standard"),
        summary={"error": 0, "warning": 1, "info": 0},
    )

    assert not verification_failed(report, fail_on="none")
    assert not verification_failed(report, fail_on="error")
    assert verification_failed(report, fail_on="warning")


def test_run_command_missing_tool_returns_none(tmp_path) -> None:
    code, message = _run_command(["definitely-not-a-real-tool-xyz"], tmp_path, timeout=5)

    assert code is None
    assert "tool not found" in message


def test_verification_l2_detects_nested_requirements_file(tmp_path, monkeypatch) -> None:
    requirements = tmp_path / "requirements"
    requirements.mkdir()
    (requirements / "base.txt").write_text("numpy==1.26.0\n", encoding="utf-8")
    monkeypatch.setattr(
        "rrdoctor.verification.shutil.which",
        lambda tool: "pip" if tool == "pip" else None,
    )

    display, runnable, missing = _build_plan(tmp_path)

    assert missing == ""
    assert display == [
        "pip install --dry-run -r requirements/base.txt  # resolve Python dependencies"
    ]
    assert runnable == "pip install --dry-run -r requirements/base.txt"


def test_verification_l2_detects_environment_yaml(tmp_path, monkeypatch) -> None:
    (tmp_path / "environment.yaml").write_text("name: demo\n", encoding="utf-8")
    monkeypatch.setattr(
        "rrdoctor.verification.shutil.which",
        lambda tool: "mamba" if tool == "mamba" else None,
    )

    display, runnable, missing = _build_plan(tmp_path)

    assert missing == ""
    assert display == ["mamba env create -f environment.yaml --dry-run"]
    assert runnable == "mamba env create -f environment.yaml --dry-run"


def test_verification_l2_dynamic_uses_parsed_argument_vector(tmp_path, monkeypatch) -> None:
    requirements = tmp_path / "requirements"
    requirements.mkdir()
    (requirements / "main.txt").write_text("numpy==1.26.0\n", encoding="utf-8")
    captured: dict[str, list[str]] = {}
    monkeypatch.setattr(
        "rrdoctor.verification.shutil.which",
        lambda tool: "pip" if tool == "pip" else None,
    )

    def fake_run_command(cmd, cwd, timeout):
        captured["cmd"] = cmd
        return 0, "ok"

    monkeypatch.setattr("rrdoctor.verification._run_command", fake_run_command)

    step = _l2_step(tmp_path, run=True, timeout=30)

    assert step.status == "pass"
    assert captured["cmd"] == ["pip", "install", "--dry-run", "-r", "requirements/main.txt"]


def test_verification_detects_root_python_entrypoint(tmp_path) -> None:
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")

    runnable, display = _entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[-1] == "train.py"
    assert display == "python train.py"


def test_verification_detects_root_main_variant_entrypoint(tmp_path) -> None:
    (tmp_path / "main_finetune.py").write_text("print('fine-tune')\n", encoding="utf-8")

    runnable, display = _entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[-1] == "main_finetune.py"
    assert display == "python main_finetune.py"


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


def test_verification_accepts_documented_main_variant_command(tmp_path) -> None:
    (tmp_path / "main_finetune.py").write_text("print('fine-tune')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Demo\n\n```bash\npython main_finetune.py --eval --data_path ${IMAGENET_DIR}\n```\n",
        encoding="utf-8",
    )

    runnable, display = _readme_entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[1:] == ["main_finetune.py", "--eval", "--data_path", "${IMAGENET_DIR}"]
    assert display == "python main_finetune.py --eval --data_path '${IMAGENET_DIR}'"


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


def test_verification_accepts_documented_python_module_entrypoint(tmp_path) -> None:
    package = tmp_path / "demo"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "train.py").write_text("print('train')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Demo\n\n```bash\npython -m demo.train --config configs/default.yaml\n```\n",
        encoding="utf-8",
    )

    runnable, display = _readme_entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[1:] == ["-m", "demo.train", "--config", "configs/default.yaml"]
    assert display == "python -m demo.train --config configs/default.yaml"


def test_verification_accepts_documented_python_module_runner_with_script(tmp_path) -> None:
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Demo\n\n```bash\npython -m torch.distributed.run train.py --epochs 1\n```\n",
        encoding="utf-8",
    )

    runnable, display = _readme_entrypoint_command(tmp_path)

    assert runnable is not None
    assert runnable[1:] == ["-m", "torch.distributed.run", "train.py", "--epochs", "1"]
    assert display == "python -m torch.distributed.run train.py --epochs 1"


def test_verification_rejects_non_local_python_module_command(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nInstall with `python -m pip install -e .`.\n",
        encoding="utf-8",
    )

    runnable, display = _readme_entrypoint_command(tmp_path)

    assert runnable is None
    assert display == ""


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
