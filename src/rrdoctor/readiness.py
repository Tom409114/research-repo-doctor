"""Artifact Evaluation oriented readiness labels."""

from __future__ import annotations

from rrdoctor.models import ArtifactReadiness, Finding, Severity

AVAILABLE_BLOCKERS = {"RRD001", "RRD010"}
FUNCTIONAL_BLOCKERS = {"RRD030", "RRD040", "RRD050"}


def compute_readiness(findings: list[Finding]) -> ArtifactReadiness:
    """Map deterministic findings to an ACM-inspired artifact readiness level.

    The label is deliberately coarser than the numeric score. It is meant to
    communicate the artifact-reviewer question: is this public, runnable, and
    close to reproduction-ready?
    """

    actionable = [
        finding for finding in findings if finding.severity in {Severity.ERROR, Severity.WARNING}
    ]
    failed = {finding.rule_id for finding in actionable}
    errors = {finding.rule_id for finding in findings if finding.severity == Severity.ERROR}

    available_blockers = sorted(failed & AVAILABLE_BLOCKERS)
    if available_blockers:
        return ArtifactReadiness(
            level="Needs preparation",
            description="Public artifact basics such as README or license are still missing.",
            blocking_rule_ids=available_blockers,
        )

    functional_error_blockers = sorted(errors & FUNCTIONAL_BLOCKERS)
    if errors:
        return ArtifactReadiness(
            level="Available",
            description=(
                "The repository is present, but error-level findings still block a "
                "functional artifact review."
            ),
            blocking_rule_ids=functional_error_blockers or sorted(errors),
        )

    if actionable:
        return ArtifactReadiness(
            level="Functional",
            description=(
                "No blocking errors were detected; remaining findings are release or "
                "reproducibility hardening tasks before a deadline."
            ),
            blocking_rule_ids=[finding.rule_id for finding in actionable[:8]],
        )

    return ArtifactReadiness(
        level="Reproduced-ready",
        description=(
            "Static checks found no blocking findings. Run `rrdoctor verify --run` on a "
            "trusted machine for dynamic evidence."
        ),
        blocking_rule_ids=[],
    )
