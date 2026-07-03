from __future__ import annotations

import shutil
from pathlib import Path

from typer.testing import CliRunner

from rrdoctor.cli import app
from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.fixers import FixContext, apply_fix, fixable_rule_ids, infer_fix_context
from rrdoctor.scanner import Scanner

runner = CliRunner()


def _ctx(root: Path) -> FixContext:
    return FixContext(root=root, project_name="demo", author="Demo Author", year=2026)


def test_apply_fix_creates_and_is_idempotent(tmp_path) -> None:
    created = apply_fix("RRD012", _ctx(tmp_path))
    assert created is not None
    assert created.action == "created"
    assert (tmp_path / "SECURITY.md").exists()

    again = apply_fix("RRD012", _ctx(tmp_path))
    assert again is not None
    assert again.action == "skipped"


def test_license_uses_author_and_year(tmp_path) -> None:
    apply_fix("RRD010", _ctx(tmp_path))
    text = (tmp_path / "LICENSE").read_text(encoding="utf-8")
    assert "Demo Author" in text
    assert "2026" in text


def test_citation_fix_uses_pyproject_metadata(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "paper-demo"\n'
        'version = "1.2.3"\n'
        'authors = [{ name = "Example Lab" }]\n'
        "\n"
        "[project.urls]\n"
        'Repository = "https://github.com/example/paper-demo"\n',
        encoding="utf-8",
    )

    apply_fix("RRD020", infer_fix_context(tmp_path, year=2026))

    text = (tmp_path / "CITATION.cff").read_text(encoding="utf-8")
    assert 'title: "paper-demo"' in text
    assert 'name: "Example Lab"' in text
    assert 'version: "1.2.3"' in text
    assert 'repository-code: "https://github.com/example/paper-demo"' in text
    assert "The Authors" not in text


def test_gitignore_created_then_appended(tmp_path) -> None:
    created = apply_fix("RRD091", _ctx(tmp_path))
    assert created is not None and created.action == "created"
    assert ".env" in (tmp_path / ".gitignore").read_text(encoding="utf-8")

    # Replace with a partial ignore file and re-run: it should append the rest.
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")
    updated = apply_fix("RRD091", _ctx(tmp_path))
    assert updated is not None and updated.action == "updated"
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "wandb" in text and text.count(".env") == 1


def test_data_readme_only_when_dir_exists(tmp_path) -> None:
    skipped = apply_fix("RRD041", _ctx(tmp_path))
    assert skipped is not None and skipped.action == "skipped"

    (tmp_path / "data").mkdir()
    created = apply_fix("RRD041", _ctx(tmp_path))
    assert created is not None and created.action == "created"
    assert (tmp_path / "data" / "README.md").exists()


def test_apply_fix_unknown_rule_returns_none(tmp_path) -> None:
    assert apply_fix("RRD001", _ctx(tmp_path)) is None


def test_fixable_findings_are_flagged() -> None:
    report = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    fixable = fixable_rule_ids()
    for finding in report.findings:
        assert finding.autofix_available == (finding.rule_id in fixable)


def test_cli_fix_dry_run_then_write(tmp_path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree("tests/fixtures/missing-basics-repo", repo)

    dry = runner.invoke(app, ["fix", str(repo)])
    assert dry.exit_code == 0
    assert "dry-run" in dry.stdout
    assert not (repo / "LICENSE").exists()

    write = runner.invoke(app, ["fix", str(repo), "--write", "--author", "Lab"])
    assert write.exit_code == 0
    assert (repo / "LICENSE").exists()
    assert (repo / "CHANGELOG.md").exists()

    before = Scanner(DEFAULT_CONFIG).scan("tests/fixtures/missing-basics-repo")
    after = Scanner(DEFAULT_CONFIG).scan(repo)
    assert after.score > before.score
