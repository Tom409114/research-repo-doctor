from __future__ import annotations

import importlib.util
import sys
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
    markdown = "- Artifact readiness: **Reproduced-ready**\n- Heuristic score: **100/100**\n"

    assert script._markdown_field(markdown, "Artifact readiness") == "Reproduced-ready"
    assert script._markdown_field(markdown, "Heuristic score") == "100/100"
