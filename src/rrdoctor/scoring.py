"""Transparent score calculation for scan reports."""

from __future__ import annotations

from collections import Counter, defaultdict

from rrdoctor.models import Category, CategoryScore, Finding, Severity


def score_findings(findings: list[Finding]) -> tuple[int, list[CategoryScore], dict[str, int]]:
    """Return overall score, per-category scores, and severity counts."""

    summary = Counter(finding.severity.value for finding in findings)
    penalty = summary[Severity.ERROR.value] * 12 + summary[Severity.WARNING.value] * 4
    score = max(0, 100 - penalty)

    by_category: dict[Category, list[Finding]] = defaultdict(list)
    for finding in findings:
        by_category[finding.category].append(finding)

    category_scores: list[CategoryScore] = []
    for category in sorted(by_category, key=lambda item: item.value):
        category_findings = by_category[category]
        counts = Counter(finding.severity.value for finding in category_findings)
        category_penalty = counts[Severity.ERROR.value] * 20 + counts[Severity.WARNING.value] * 8
        category_scores.append(
            CategoryScore(
                category=category,
                score=max(0, 100 - category_penalty),
                errors=counts[Severity.ERROR.value],
                warnings=counts[Severity.WARNING.value],
                infos=counts[Severity.INFO.value],
            )
        )

    return (
        score,
        category_scores,
        {
            "error": summary[Severity.ERROR.value],
            "warning": summary[Severity.WARNING.value],
            "info": summary[Severity.INFO.value],
        },
    )
