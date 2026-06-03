"""Markdown report renderer."""

from __future__ import annotations

from collections import defaultdict

from rrdoctor.models import Finding, ScanReport, Severity


def _finding_key(finding: Finding) -> tuple[int, str, str]:
    order = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}
    return (order[finding.severity], finding.category.value, finding.rule_id)


def render_markdown(report: ScanReport) -> str:
    """Render a scan report as Markdown."""

    lines: list[str] = [
        "# Research Repo Doctor Report",
        "",
        f"- Repository path: `{report.repository_path}`",
        f"- Generated: `{report.generated_at}`",
        f"- Profile: `{report.profile}`",
        f"- Overall score: **{report.score}/100**",
        f"- Rules evaluated: `{report.rules_evaluated}`",
        "",
        "> Heuristic note: " + report.heuristic_note,
        "",
        "## Summary by category",
        "",
        "| Category | Score | Errors | Warnings | Info |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for category_score in report.category_scores:
        lines.append(
            f"| {category_score.category.value} | {category_score.score} | "
            f"{category_score.errors} | {category_score.warnings} | {category_score.infos} |"
        )
    if not report.category_scores:
        lines.append("| all | 100 | 0 | 0 | 0 |")

    lines.extend(["", "## How to fix first", ""])
    priority = sorted(report.findings, key=_finding_key)[:8]
    if priority:
        for finding in priority:
            lines.append(f"- **{finding.rule_id}** {finding.title}: {finding.recommendation}")
    else:
        lines.append("- No findings. Keep the repository documentation and automation current.")

    grouped: dict[str, list[Finding]] = defaultdict(list)
    for finding in sorted(report.findings, key=_finding_key):
        grouped[f"{finding.severity.value} / {finding.category.value}"].append(finding)

    lines.extend(["", "## Findings", ""])
    if not grouped:
        lines.append("No findings were detected.")
    for group, findings in grouped.items():
        lines.extend([f"### {group}", ""])
        for finding in findings:
            location = ""
            if finding.file:
                location = (
                    f" (`{finding.file}:{finding.line}`)"
                    if finding.line
                    else f" (`{finding.file}`)"
                )
            lines.extend(
                [
                    f"#### {finding.rule_id}: {finding.title}{location}",
                    "",
                    finding.message,
                    "",
                    f"Recommendation: {finding.recommendation}",
                ]
            )
            if finding.evidence:
                lines.extend(["", "Evidence:"])
                for item in finding.evidence:
                    where = f" `{item.file}`" if item.file else ""
                    if item.line:
                        where += f":{item.line}"
                    value = f" `{item.value}`" if item.value else ""
                    lines.append(f"- {item.message}{where}{value}")
            lines.append("")

    lines.extend(["## Suggested GitHub issues", ""])
    if report.findings:
        for finding in sorted(report.findings, key=_finding_key)[:10]:
            lines.append(f"- [{finding.severity.value}] Fix {finding.rule_id}: {finding.title}")
    else:
        lines.append("- No issue suggestions from this scan.")

    lines.extend(
        [
            "",
            "## Reproducibility checklist",
            "",
            "- [ ] README explains setup, usage, and result reproduction.",
            "- [ ] Dependencies and runtime versions are documented.",
            "- [ ] Data availability and provenance are documented.",
            "- [ ] Experiment entrypoints and configuration are discoverable.",
            "- [ ] Notebooks are clean, ordered, and free of secrets.",
            "- [ ] Tests and CI provide a basic quality gate.",
            "- [ ] Citation, license, changelog, and release metadata are present.",
            "",
        ]
    )
    return "\n".join(lines)
