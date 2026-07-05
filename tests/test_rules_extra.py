from __future__ import annotations

from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def _scan(root: Path, rule_id: str):
    return Scanner(DEFAULT_CONFIG, include={rule_id}).scan(root)


def test_agents_guide_rule(tmp_path) -> None:
    missing = _scan(tmp_path, "RRD014")
    assert missing.findings and missing.findings[0].rule_id == "RRD014"

    (tmp_path / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
    present = _scan(tmp_path, "RRD014")
    assert not present.findings


def test_unpinned_dependencies_rule(tmp_path) -> None:
    (tmp_path / "requirements.txt").write_text(
        "numpy\npandas==2.0.0\n# comment\n-r other.txt\nscipy ; python_version > '3.9'\n",
        encoding="utf-8",
    )
    report = _scan(tmp_path, "RRD033")
    assert report.findings
    evidence = report.findings[0].evidence[0].message
    assert "numpy" in evidence
    assert "scipy" in evidence
    assert "pandas" not in evidence


def test_unpinned_dependencies_rule_all_pinned(tmp_path) -> None:
    (tmp_path / "requirements.txt").write_text("numpy==1.26.0\npandas>=2.0\n", encoding="utf-8")
    report = _scan(tmp_path, "RRD033")
    assert not report.findings


def test_readme_dataset_section_satisfies_data_docs_rule(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "## Datasets\n\n"
        "Download the Shakespeare data with "
        "`python data/shakespeare/prepare.py` before training.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD040")

    assert not report.findings


def test_readme_data_prepare_command_satisfies_data_docs_rule(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "## Quick start\n\n"
        "First download and tokenize the data:\n\n"
        "```sh\n"
        "python data/openwebtext/prepare.py\n"
        "```\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD040")

    assert not report.findings


def test_local_absolute_path_rule_flags_real_user_path(tmp_path) -> None:
    local_path = "/home/" + "alice/private-datasets/demo"
    (tmp_path / "README.md").write_text(
        f"# Demo\n\nSet `DATA_DIR={local_path}` before training.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert report.findings
    assert report.findings[0].rule_id == "RRD043"


def test_local_absolute_path_rule_ignores_placeholder_path(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nWrite outputs to `/home/user/absolute_path_to_the_output_dir`.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_notebook_checkpoints_rule(tmp_path) -> None:
    checkpoint_dir = tmp_path / "notebooks" / ".ipynb_checkpoints"
    checkpoint_dir.mkdir(parents=True)
    (checkpoint_dir / "demo-checkpoint.ipynb").write_text("{}", encoding="utf-8")

    report = _scan(tmp_path, "RRD065")
    assert report.findings and report.findings[0].rule_id == "RRD065"


def test_precommit_rule(tmp_path) -> None:
    missing = _scan(tmp_path, "RRD082")
    assert missing.findings and missing.findings[0].rule_id == "RRD082"

    (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
    present = _scan(tmp_path, "RRD082")
    assert not present.findings
