from __future__ import annotations

from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG, apply_cli_overrides
from rrdoctor.reporting.appendix import badge_status, render_appendix, render_checklist
from rrdoctor.scanner import Scanner
from rrdoctor.verification import _run_command, render_verification, verification_failed


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
    # ml-project-repo has no error findings, so L1 should not be a failure.
    assert not verification_failed(report)


def test_verification_failed_on_missing_basics() -> None:
    report = _report("tests/fixtures/missing-basics-repo", "standard")

    assert verification_failed(report)


def test_run_command_missing_tool_returns_none(tmp_path) -> None:
    code, message = _run_command(["definitely-not-a-real-tool-xyz"], tmp_path, timeout=5)

    assert code is None
    assert "tool not found" in message
