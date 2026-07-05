"""Agent-ready fix-plan rendering.

The fix plan turns a deterministic scan into a tool-agnostic work order. It can
be handed to any coding agent or worked through by hand, and every task names the
deterministic check that verifies it. This keeps the scanner as the source of
truth while making its output directly actionable.
"""

from __future__ import annotations

import json

from rrdoctor.models import Finding, FixPlan, FixTask, ScanReport, Severity, to_jsonable

_SEVERITY_ORDER = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}


def _task_key(finding: Finding) -> tuple[int, str, str]:
    return (_SEVERITY_ORDER[finding.severity], finding.category.value, finding.rule_id)


def build_fix_plan(report: ScanReport) -> FixPlan:
    """Derive an ordered, tool-agnostic fix plan from a scan report."""

    tasks: list[FixTask] = []
    for finding in sorted(report.findings, key=_task_key):
        targets = [finding.file] if finding.file else []
        targets.extend(
            item.file for item in finding.evidence if item.file and item.file not in targets
        )
        tasks.append(
            FixTask(
                rule_id=finding.rule_id,
                title=finding.title,
                category=finding.category,
                severity=finding.severity,
                instruction=finding.recommendation,
                verification=(
                    f"Re-run `rrdoctor scan` and confirm {finding.rule_id} no longer reports "
                    "a finding."
                ),
                targets=targets,
                autofix_available=finding.autofix_available,
            )
        )
    autofixable = sum(1 for task in tasks if task.autofix_available)
    return FixPlan(
        repository_path=report.repository_path,
        generated_at=report.generated_at,
        profile=report.profile,
        readiness_level=report.readiness.level,
        score=report.score,
        tasks=tasks,
        autofixable=autofixable,
    )


def render_agent_markdown(report: ScanReport) -> str:
    """Render a fix plan as a tool-agnostic Markdown prompt."""

    plan = build_fix_plan(report)
    lines: list[str] = [
        "# Reproducibility Fix Plan",
        "",
        f"- Repository: `{plan.repository_path}`",
        f"- Profile: `{plan.profile}`",
        f"- Current readiness: **{plan.readiness_level}**",
        f"- Heuristic score: **{plan.score}/100**",
        f"- Tasks: `{len(plan.tasks)}` ({plan.autofixable} auto-fixable)",
        "",
        "## How to use this plan",
        "",
        "This plan is tool-agnostic: hand it to any coding agent or work through it by "
        "hand. Each task names the deterministic check that verifies it. The audit is the "
        "source of truth, so apply a change and then re-run the check.",
        "",
        "1. Apply the mechanical fixes first: `rrdoctor fix --write`.",
        "2. Work the remaining tasks below, smallest blast radius first.",
        "3. Verify with `rrdoctor scan <path> --fail-on none` and aim to improve readiness.",
        "",
    ]

    if not plan.tasks:
        lines.extend(
            [
                "## Tasks",
                "",
                "No findings. The repository already passes the configured checks. Keep the "
                "documentation, environment metadata, and automation current.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(["## Tasks", ""])
    for index, task in enumerate(plan.tasks, start=1):
        flag = " (auto-fixable: `rrdoctor fix`)" if task.autofix_available else ""
        targets = ", ".join(f"`{target}`" for target in task.targets) or "(repository root)"
        lines.extend(
            [
                f"### {index}. {task.rule_id} {task.title} [{task.severity.value}]{flag}",
                "",
                f"- Category: {task.category.value}",
                f"- Files: {targets}",
                f"- Do: {task.instruction}",
                f"- Verify: {task.verification}",
                "",
            ]
        )

    lines.extend(
        [
            "## Acceptance",
            "",
            "When the plan is complete, re-run the audit. The resolved tasks should no "
            "longer appear, readiness should improve, and the heuristic score should "
            "increase. Use a baseline to gate regressions in CI:",
            "",
            "```bash",
            "rrdoctor scan . --format json --output rrdoctor-baseline.json --fail-on none",
            "# ...apply changes...",
            "rrdoctor scan . --baseline rrdoctor-baseline.json --fail-on-new error",
            "```",
            "",
            "For Artifact Evaluation packages, also generate reviewer-facing evidence:",
            "",
            "```bash",
            f"rrdoctor appendix . --profile {plan.profile} --output ARTIFACT_APPENDIX.md",
            f"rrdoctor verify . --profile {plan.profile} --fail-on none",
            "```",
            "",
            "For repositories you trust, optionally run the dynamic path check:",
            "",
            "```bash",
            f"rrdoctor verify . --profile {plan.profile} --run --timeout 600 --fail-on error",
            "```",
            "",
            "Do not run dynamic verification on untrusted code.",
            "",
        ]
    )
    return "\n".join(lines)


def render_agent_json(report: ScanReport) -> str:
    """Render a fix plan as stable JSON."""

    plan = build_fix_plan(report)
    return json.dumps(to_jsonable(plan), indent=2, sort_keys=True) + "\n"
