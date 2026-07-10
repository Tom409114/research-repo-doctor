from __future__ import annotations

from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG, deep_merge
from rrdoctor.scanner import Scanner, collect_files

FIXTURES = Path("tests/fixtures")


def test_collect_files_respects_excludes(tmp_path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("ignored", encoding="utf-8")
    (tmp_path / "README.md").write_text("visible", encoding="utf-8")

    files = collect_files(tmp_path, DEFAULT_CONFIG)

    assert [path.name for path in files] == ["README.md"]


def test_collect_files_respects_included_directories(tmp_path) -> None:
    source = tmp_path / "src"
    generated = source / "generated"
    docs = tmp_path / "docs"
    generated.mkdir(parents=True)
    docs.mkdir()
    (source / "keep.py").write_text("print('keep')\n", encoding="utf-8")
    (generated / "skip.py").write_text("print('skip')\n", encoding="utf-8")
    (docs / "skip.md").write_text("skip\n", encoding="utf-8")
    config = deep_merge(
        DEFAULT_CONFIG,
        {"paths": {"include": ["src"], "exclude": ["src/generated"]}},
    )

    files = collect_files(tmp_path, config)

    assert [path.relative_to(tmp_path).as_posix() for path in files] == ["src/keep.py"]


def test_healthy_fixture_has_fewer_findings_than_missing_basics() -> None:
    scanner = Scanner(DEFAULT_CONFIG)

    healthy = scanner.scan(FIXTURES / "healthy-research-repo")
    missing = scanner.scan(FIXTURES / "missing-basics-repo")

    assert len(healthy.findings) < len(missing.findings)
    assert healthy.score > missing.score
    assert healthy.readiness.level == "Reproduced-ready"
    assert missing.readiness.level == "Needs preparation"


def test_include_runs_single_rule() -> None:
    scanner = Scanner(DEFAULT_CONFIG, include={"RRD001"})

    report = scanner.scan(FIXTURES / "missing-basics-repo")

    assert {finding.rule_id for finding in report.findings} == {"RRD001"}
    assert report.rules_evaluated == 1


def test_rule_severity_override() -> None:
    config = deep_merge(DEFAULT_CONFIG, {"rules": {"RRD001": {"severity": "warning"}}})
    scanner = Scanner(config, include={"RRD001"})

    report = scanner.scan(FIXTURES / "missing-basics-repo")

    assert report.findings[0].severity.value == "warning"
