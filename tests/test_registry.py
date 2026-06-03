from __future__ import annotations

from pathlib import Path

from rrdoctor.rules.registry import all_rules, get_rule


def test_rule_registry_has_required_rules() -> None:
    rules = all_rules()

    assert len(rules) >= 24
    assert get_rule("RRD001") is not None
    assert get_rule("rrd001") is not None
    assert get_rule("RRD999") is None


def test_registered_rules_have_metadata_and_docs_entries() -> None:
    docs = Path("docs/checks.md").read_text(encoding="utf-8")

    for rule in all_rules():
        definition = rule.definition
        assert definition.id in docs
        assert definition.name
        assert definition.description
        assert definition.rationale
        assert definition.remediation
        assert definition.profiles
