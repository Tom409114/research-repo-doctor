from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def test_available_when_public_basics_exist_but_functional_blockers_remain(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nInstall and usage coming soon.\n", encoding="utf-8"
    )
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG).scan(tmp_path)

    assert report.readiness.level == "Available"
    assert "RRD030" in report.readiness.blocking_rule_ids


def test_functional_when_core_run_evidence_exists_but_release_hygiene_remains(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "## Install\n\n"
        "`pip install torch numpy`\n\n"
        "## Usage\n\n"
        "`python train.py config/default.py`\n\n"
        "## Data\n\n"
        "`python data/demo/prepare.py` downloads and prepares the dataset.\n",
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG).scan(tmp_path)

    assert report.summary["error"] == 0
    assert report.summary["warning"] > 0
    assert report.readiness.level == "Functional"


def test_any_error_blocks_functional_readiness(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "## Install\n\n"
        "`pip install numpy`\n\n"
        "## Usage\n\n"
        "`python train.py`\n\n"
        "## Data\n\n"
        "`python data/demo/prepare.py` downloads and prepares the dataset.\n",
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")
    secret_value = "abc123XYZ789" + "def456GHI"
    (tmp_path / "leak.py").write_text(f'api_key = "{secret_value}"\n', encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG).scan(tmp_path)

    assert report.summary["error"] > 0
    assert report.readiness.level == "Available"
