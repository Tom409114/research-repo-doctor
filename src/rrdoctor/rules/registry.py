"""Rule registry."""

from __future__ import annotations

from rrdoctor.rules import (
    ci,
    citation,
    data,
    environment,
    experiments,
    governance,
    license,
    notebooks,
    project_metadata,
    readme,
    release,
    security,
    tests,
)
from rrdoctor.rules.base import Rule

RULE_MODULES = (
    readme,
    license,
    governance,
    citation,
    environment,
    data,
    experiments,
    notebooks,
    tests,
    ci,
    security,
    release,
    project_metadata,
)


def all_rules() -> list[Rule]:
    """Return all registered rules in stable ID order."""

    rules: list[Rule] = []
    for module in RULE_MODULES:
        rules.extend(module.RULES)
    return sorted(rules, key=lambda rule: rule.definition.id)


def get_rule(rule_id: str) -> Rule | None:
    """Find a rule by ID."""

    normalized = rule_id.upper()
    for rule in all_rules():
        if rule.definition.id == normalized:
            return rule
    return None
