from pathlib import Path

import yaml


def test_action_exposes_dynamic_verify_gate() -> None:
    action = yaml.safe_load(Path("action.yml").read_text(encoding="utf-8"))

    inputs = action["inputs"]
    assert inputs["verify-run"]["default"] == "false"
    assert inputs["verify-fail-on"]["default"] == "none"
    assert "error" in inputs["verify-fail-on"]["description"]

    outputs = action["outputs"]
    assert outputs["verify-exit-code"]["value"] == "${{ steps.verify_step.outputs.code }}"

    steps = action["runs"]["steps"]
    verify_step = next(step for step in steps if step.get("id") == "verify_step")
    assert "RRD_VERIFY_FAIL_ON" in verify_step["env"]
    assert '--fail-on "$RRD_VERIFY_FAIL_ON"' in verify_step["run"]
    assert 'echo "code=$?"' in verify_step["run"]
    assert "exit 0" in verify_step["run"]

    enforce_step = steps[-1]
    assert enforce_step["name"] == "Enforce result"
    assert "RRD_VERIFY_CODE" in enforce_step["env"]
    assert 'exit "$RRD_VERIFY_CODE"' in enforce_step["run"]
