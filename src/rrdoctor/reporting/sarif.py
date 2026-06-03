"""Experimental SARIF-compatible report renderer."""

from __future__ import annotations

import json

from rrdoctor.models import ScanReport
from rrdoctor.rules.registry import all_rules


def render_sarif(report: ScanReport) -> str:
    """Render a minimal SARIF-like JSON report."""

    rules = [
        {
            "id": rule.definition.id,
            "name": rule.definition.name,
            "shortDescription": {"text": rule.definition.description},
            "help": {"text": rule.definition.remediation},
            "properties": {
                "category": rule.definition.category.value,
                "severity": rule.definition.severity.value,
                "profiles": list(rule.definition.profiles),
            },
        }
        for rule in all_rules()
    ]
    results = []
    for finding in report.findings:
        location = {"physicalLocation": {"artifactLocation": {"uri": finding.file or "."}}}
        if finding.line:
            location["physicalLocation"]["region"] = {"startLine": finding.line}
        results.append(
            {
                "ruleId": finding.rule_id,
                "level": "error" if finding.severity.value == "error" else "warning",
                "message": {"text": finding.message},
                "locations": [location],
                "properties": {
                    "category": finding.category.value,
                    "recommendation": finding.recommendation,
                },
            }
        )
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Research Repo Doctor",
                        "informationUri": (
                            "https://github.com/research-repo-doctor/research-repo-doctor"
                        ),
                        "rules": rules,
                    }
                },
                "results": results,
                "properties": {
                    "profile": report.profile,
                    "score": report.score,
                    "heuristicNote": report.heuristic_note,
                },
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
