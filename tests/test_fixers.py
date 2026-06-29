from __future__ import annotations

import shutil
from pathlib import Path

from typer.testing import CliRunner

from rrdoctor.cli import app
from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.fixers import FixContext, apply_fix, fixable_rule_ids
from rrdoctor.scanner import Scanner

runner = CliRunner()


def _ctx(root: Path) -> FixContext:
    return FixContext(root=root, project_name="demo", author="Demo Author", year=2026)


def _write_unseeded_package(root: Path) -> Path:
    package_dir = root / "src" / "demo"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "train.py").write_text(
        "import numpy as np\n\nsample = np.random.randn(4)\n",
        encoding="utf-8",
    )
    return package_dir


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


def test_repro_seed_helper_created_in_single_package_and_is_idempotent(tmp_path) -> None:
    package_dir = _write_unseeded_package(tmp_path)
    helper = package_dir / "_repro_seed.py"

    created = apply_fix("RRD052", _ctx(tmp_path))
    assert created is not None
    assert created.action == "created"
    assert created.path == "src/demo/_repro_seed.py"
    text = helper.read_text(encoding="utf-8")
    assert "def set_global_seed(seed: int) -> None" in text
    assert 'numpy = _optional_module("numpy")' in text
    assert "numpy.random.seed(seed)" in text
    assert "torch.manual_seed(seed)" in text
    assert "tensorflow.random.set_seed(seed)" in text
    assert "TODO: Call set_global_seed" in text

    before = {
        path.relative_to(tmp_path).as_posix(): path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    again = apply_fix("RRD052", _ctx(tmp_path))
    after = {
        path.relative_to(tmp_path).as_posix(): path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert again is not None and again.action == "skipped"
    assert before == after


def test_repro_seed_fix_falls_back_to_docs_note_without_clear_package(tmp_path) -> None:
    (tmp_path / "train.py").write_text(
        "import random\n\nvalue = random.random()\n",
        encoding="utf-8",
    )

    created = apply_fix("RRD052", _ctx(tmp_path))

    assert created is not None and created.action == "created"
    assert created.path == "docs/reproducibility-seed.md"
    text = (tmp_path / "docs" / "reproducibility-seed.md").read_text(encoding="utf-8")
    assert "def set_global_seed(seed: int) -> None" in text
    assert "TODO: Move this helper" in text


def test_repro_seed_fix_never_overwrites_existing_helper(tmp_path) -> None:
    package_dir = _write_unseeded_package(tmp_path)
    helper = package_dir / "_repro_seed.py"
    helper.write_text("# user-owned helper\n", encoding="utf-8")

    skipped = apply_fix("RRD052", _ctx(tmp_path))

    assert skipped is not None
    assert skipped.action == "skipped"
    assert "already exists" in skipped.detail
    assert helper.read_text(encoding="utf-8") == "# user-owned helper\n"


def test_cli_fix_creates_repro_seed_helper_when_rule_fires(tmp_path) -> None:
    repo = tmp_path / "repo"
    _write_unseeded_package(repo)
    helper = repo / "src" / "demo" / "_repro_seed.py"

    write = runner.invoke(app, ["fix", str(repo), "--write", "--only", "RRD052"])

    assert write.exit_code == 0
    assert helper.exists()
    assert "RRD052" in write.stdout


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
