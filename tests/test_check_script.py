from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_check_script():
    path = Path("scripts/check.py")
    spec = importlib.util.spec_from_file_location("check_script", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_check_script_runs_project_quality_gates() -> None:
    script = _load_check_script()
    commands = [" ".join(command) for command in script.COMMANDS]

    assert commands[0] == "ruff format --check ."
    assert commands[1] == "ruff check ."
    assert any(" -m mypy" in command for command in commands)
    assert any(" -m pytest -q" in command for command in commands)
    assert any(" -m rrdoctor scan . --profile standard" in command for command in commands)
