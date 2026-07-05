from __future__ import annotations

from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def _scan(root: Path, rule_id: str):
    return Scanner(DEFAULT_CONFIG, include={rule_id}).scan(root)


def test_missing_readme_rule() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD001"}).scan("tests/fixtures/missing-basics-repo")

    assert report.findings
    assert report.findings[0].rule_id == "RRD001"


def test_missing_license_rule() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD010"}).scan("tests/fixtures/missing-basics-repo")

    assert report.findings
    assert report.findings[0].rule_id == "RRD010"


def test_setup_rule_accepts_install_command_without_heading(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nClone the repo, then run:\n\n```bash\npip install -e .\n```\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD002")

    assert not report.findings


def test_usage_rule_accepts_get_started_command_without_heading(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "If you just want to get started, run the training script:\n\n"
        "```bash\npython run_classifier.py --do_train=true\n```\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD003")

    assert not report.findings


def test_reproduce_rule_accepts_training_command(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "## Training\n\n"
        "Run the paper configuration:\n\n"
        "```bash\npython train.py config/train_shakespeare_char.py\n```\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD004")

    assert not report.findings


def test_reproduce_rule_accepts_evaluation_command(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n## Evaluation\n\n```bash\npython eval.py --checkpoint outputs/model.pt\n```\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD004")

    assert not report.findings


def test_reproduce_rule_does_not_accept_plain_install_command(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n## Installation\n\n```bash\npython -m pip install -e .\n```\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD004")

    assert report.findings
