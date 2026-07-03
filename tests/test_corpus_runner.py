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
                "actionable_findings_by_rule": {"RRD030": 1, "RRD050": 2},
                "findings_by_severity": {"warning": 3},
                "expected_absent_violations": [],
                "manual_review": {
                    "false_positives": [{"rule_id": "RRD030", "evidence": "fixture"}],
                    "false_negatives": [],
                },
            }
        ]
    )

    assert "Aggregate Overview" in rendered
    assert "Manually reviewed: 1" in rendered
    assert "Functional" in rendered
    assert "Top actionable rule frequencies" in rendered
    assert "RRD050" in rendered
    assert "False positive" in rendered
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
                "actionable_findings_by_rule": {"RRD050": 2},
                "findings_by_severity": {"error": 1, "warning": 2},
                "expected_absent_violations": ["RRD050"],
                "manual_review": {
                    "false_positives": [{"rule_id": "RRD030", "evidence": "fixture"}],
                    "false_negatives": [{"rule_id": "RRD052", "evidence": "fixture"}],
                },
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
    assert aggregate["reviewed_repositories"] == 1
    assert aggregate["pending_review_repositories"] == 0
    assert aggregate["readiness"] == {"Functional": 1}
    assert aggregate["rules"]["RRD050"] == 2
    assert aggregate["actionable_rules"] == {"RRD050": 2}
    assert aggregate["top_actionable_rules"] == [{"key": "RRD050", "count": 2}]
    assert aggregate["severities"] == {"error": 1, "warning": 2}
    assert aggregate["false_positive_rules"] == {"RRD030": 1}
    assert aggregate["false_negative_rules"] == {"RRD052": 1}
    assert aggregate["expected_absent_violations"] == [
        {
            "name": "one",
            "url": "https://example.invalid/one",
            "violations": ["RRD050"],
        }
    ]


def test_expected_absent_failure_message_lists_regressions() -> None:
    runner = _load_runner()

    message = runner.expected_absent_failure_message(
        {
            "expected_absent_violations": [
                {
                    "name": "nanoGPT",
                    "url": "https://github.com/karpathy/nanoGPT",
                    "violations": ["RRD050", "RRD063"],
                }
            ]
        }
    )

    assert message is not None
    assert "Expected-absent rule regression" in message
    assert "nanoGPT: RRD050, RRD063" in message


def test_expected_absent_failure_message_is_empty_without_regressions() -> None:
    runner = _load_runner()

    message = runner.expected_absent_failure_message({"expected_absent_violations": []})

    assert message is None


def test_pending_review_stubs_do_not_count_as_reviewed() -> None:
    runner = _load_runner()

    aggregate = runner.aggregate_summaries(
        [
            {
                "name": "demo",
                "url": "https://example.invalid/demo",
                "ecosystem": "python-ml",
                "status": "scanned",
                "readiness": {"level": "Functional"},
                "score": 64,
                "findings_by_rule": {},
                "actionable_findings_by_rule": {},
                "findings_by_severity": {},
                "expected_absent_violations": [],
                "manual_review": {
                    "status": "needs-review",
                    "false_positives": [],
                    "false_negatives": [],
                },
            }
        ]
    )

    assert aggregate["reviewed_repositories"] == 0
    assert aggregate["pending_review_repositories"] == 1


def test_review_notes_are_loaded_and_attached(tmp_path) -> None:
    runner = _load_runner()
    review_dir = tmp_path / "reviews"
    review_dir.mkdir()
    (review_dir / "demo.yml").write_text(
        "version: 1\n"
        "repository: demo\n"
        "status: reviewed\n"
        "false_positives:\n"
        "  - rule_id: RRD030\n"
        "    evidence: dependency manifest is documented elsewhere\n"
        "confirmed_absent:\n"
        "  - RRD050\n",
        encoding="utf-8",
    )

    reviews = runner.load_review_notes(review_dir)
    summaries = runner.attach_review_notes(
        [{"name": "demo", "status": "scanned"}],
        reviews,
    )

    assert summaries[0]["manual_review"]["false_positives"] == [
        {
            "rule_id": "RRD030",
            "evidence": "dependency manifest is documented elsewhere",
        }
    ]
    assert summaries[0]["manual_review"]["confirmed_absent"] == [
        {"rule_id": "RRD050", "evidence": ""}
    ]


def test_review_stubs_are_written_without_overwrite(tmp_path) -> None:
    runner = _load_runner()
    summaries = [
        {
            "name": "Demo Repo",
            "url": "https://example.invalid/demo",
            "status": "scanned",
            "readiness": {"level": "Functional"},
            "score": 64,
            "summary": {"error": 1, "warning": 2},
            "review_focus": ["entrypoint-detection"],
            "expected_absent": ["RRD050"],
            "top_findings": [
                {
                    "rule_id": "RRD030",
                    "severity": "warning",
                    "title": "No dependency manifest found",
                    "file": "README.md",
                    "message": "Dependency metadata is missing.",
                }
            ],
        }
    ]

    written = runner.write_review_stubs(summaries, tmp_path)
    again = runner.write_review_stubs(summaries, tmp_path)

    assert len(written) == 1
    assert again == []
    payload = runner.yaml.safe_load(written[0].read_text(encoding="utf-8"))
    assert payload["repository"] == "Demo Repo"
    assert payload["status"] == "needs-review"
    assert payload["scan"]["errors"] == 1
    assert payload["candidate_findings"][0]["rule_id"] == "RRD030"
    assert payload["false_positives"] == []
