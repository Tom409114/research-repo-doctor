from __future__ import annotations

import importlib.util
import os
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
    assert any("scripts/check_public_readiness.py" in command for command in commands)


def test_check_script_prioritizes_current_checkout_source(monkeypatch) -> None:
    script = _load_check_script()
    calls = []

    class Completed:
        returncode = 0

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Completed()

    monkeypatch.setenv("PYTHONPATH", "existing-source")
    monkeypatch.setattr(script.subprocess, "run", fake_run)

    assert script.main() == 0
    expected = str(script.ROOT / "src")
    assert len(calls) == len(script.COMMANDS)
    assert all(call[1]["cwd"] == script.ROOT for call in calls)
    assert all(
        call[1]["env"]["PYTHONPATH"].split(os.pathsep) == [expected, "existing-source"]
        for call in calls
    )
