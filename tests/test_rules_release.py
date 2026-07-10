from __future__ import annotations

from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG, apply_cli_overrides
from rrdoctor.models import Severity
from rrdoctor.scanner import Scanner


def _scan(root: Path, rule_id: str):
    return Scanner(DEFAULT_CONFIG, include={rule_id}).scan(root)


def test_changelog_missing_is_informational_for_standard_scans(tmp_path) -> None:
    report = _scan(tmp_path, "RRD100")

    assert report.findings
    assert report.findings[0].severity == Severity.INFO


def test_changelog_rule_passes_when_changelog_exists(tmp_path) -> None:
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## Unreleased\n", encoding="utf-8")

    report = _scan(tmp_path, "RRD100")

    assert not report.findings


def test_version_metadata_rule_accepts_loose_git_tag(tmp_path) -> None:
    tag_dir = tmp_path / ".git" / "refs" / "tags"
    tag_dir.mkdir(parents=True)
    (tag_dir / "v1.0.0").write_text("0123456789abcdef0123456789abcdef01234567\n", encoding="utf-8")

    report = _scan(tmp_path, "RRD101")

    assert not report.findings


def test_version_metadata_rule_accepts_packed_git_tag(tmp_path) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "packed-refs").write_text(
        "# pack-refs with: peeled fully-peeled sorted\n"
        "0123456789abcdef0123456789abcdef01234567 refs/tags/v1.0.0\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD101")

    assert not report.findings


def test_version_metadata_rule_accepts_cargo_package_version(tmp_path) -> None:
    (tmp_path / "Cargo.toml").write_text(
        '[package]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8"
    )

    report = _scan(tmp_path, "RRD101")

    assert not report.findings


def test_version_metadata_rule_flags_missing_version_evidence(tmp_path) -> None:
    report = _scan(tmp_path, "RRD101")

    assert report.findings
    assert report.findings[0].severity == Severity.INFO


def test_version_metadata_rule_is_warning_in_strict_profiles(tmp_path) -> None:
    config = apply_cli_overrides(DEFAULT_CONFIG, profile="acm")

    report = Scanner(config, include={"RRD101"}).scan(tmp_path)

    assert report.findings
    assert report.findings[0].severity == Severity.WARNING
