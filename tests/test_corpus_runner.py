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
                "expected_absent_violations": [],
            }
        ]
    )

    assert "Functional" in rendered
    assert "Review this table manually" in rendered
