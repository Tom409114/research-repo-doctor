from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def _load_runner():
    path = Path("scripts/scan_corpus.py")
    spec = importlib.util.spec_from_file_location("scan_corpus", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_load_corpus_manifest() -> None:
    runner = _load_runner()

    entries = runner.load_corpus(Path("evaluation/corpus.yml"))

    assert len(entries) >= 50
    assert any(entry.name == "nanoGPT" for entry in entries)
    ecosystems = {entry.ecosystem for entry in entries}
    assert any(ecosystem.startswith("python-ml") for ecosystem in ecosystems)
    assert "nextflow" in ecosystems
    assert any(ecosystem.startswith("r-") for ecosystem in ecosystems)
    assert any(ecosystem.startswith("julia-") for ecosystem in ecosystems)


def test_expected_absent_violations_are_reported() -> None:
    runner = _load_runner()
    entry = runner.CorpusEntry(
        name="missing",
        url="https://example.invalid/missing",
        ecosystem="fixture",
        reason="test",
        expected_absent=("RRD001",),
        review_focus=(),
    )
    report = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")

    summary = runner.summarize_report(entry, report)

    assert summary["expected_absent_violations"] == ["RRD001"]


def test_markdown_summary_mentions_manual_review() -> None:
    runner = _load_runner()
    rendered = runner.render_markdown(
        [
            {
                "name": "demo",
                "url": "https://example.invalid/demo",
                "status": "scanned",
                "readiness": {"level": "Functional"},
                "score": 64,
                "summary": {"error": 0, "warning": 2},
                "findings_by_rule": {"RRD030": 1, "RRD050": 2},
                "findings_by_severity": {"warning": 3},
                "expected_absent_violations": [],
            }
        ]
    )

    assert "Aggregate Overview" in rendered
    assert "Functional" in rendered
    assert "RRD050" in rendered
    assert "Review this table manually" in rendered


def test_aggregate_summaries_counts_rules_and_violations() -> None:
    runner = _load_runner()

    aggregate = runner.aggregate_summaries(
        [
            {
                "name": "one",
                "url": "https://example.invalid/one",
                "ecosystem": "python-ml",
                "status": "scanned",
                "readiness": {"level": "Functional"},
                "score": 64,
                "findings_by_rule": {"RRD030": 1, "RRD050": 2},
                "findings_by_severity": {"error": 1, "warning": 2},
                "expected_absent_violations": ["RRD050"],
            },
            {
                "name": "two",
                "url": "https://example.invalid/two",
                "ecosystem": "r-bioinformatics",
                "status": "error",
                "error": "clone failed",
                "expected_absent": [],
            },
        ]
    )

    assert aggregate["total_repositories"] == 2
    assert aggregate["scanned_repositories"] == 1
    assert aggregate["error_repositories"] == 1
    assert aggregate["average_score"] == 64.0
    assert aggregate["readiness"] == {"Functional": 1}
    assert aggregate["rules"]["RRD050"] == 2
    assert aggregate["severities"] == {"error": 1, "warning": 2}
    assert aggregate["expected_absent_violations"] == [
        {
            "name": "one",
            "url": "https://example.invalid/one",
            "violations": ["RRD050"],
        }
    ]
