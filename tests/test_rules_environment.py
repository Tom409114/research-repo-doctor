from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def test_environment_detection_present() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD030", "RRD031"}).scan(
        "tests/fixtures/healthy-research-repo"
    )

    assert not report.findings


def test_environment_detection_missing() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD030"}).scan("tests/fixtures/missing-basics-repo")

    assert report.findings[0].rule_id == "RRD030"
    assert report.findings[0].severity.value == "error"


def test_readme_install_command_downgrades_missing_manifest(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nInstall dependencies with `pip install torch numpy tqdm`.\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD030"}).scan(tmp_path)

    assert len(report.findings) == 1
    assert report.findings[0].rule_id == "RRD030"
    assert report.findings[0].severity.value == "warning"


def test_r_description_satisfies_manifest_and_version_hint(tmp_path) -> None:
    (tmp_path / "DESCRIPTION").write_text(
        "Package: demo\nDepends: R (>= 4.1)\nImports: dplyr\n", encoding="utf-8"
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD030", "RRD031"}).scan(tmp_path)

    assert not report.findings


def test_undeclared_import_flagged(tmp_path) -> None:
    (tmp_path / "requirements.txt").write_text("numpy\n", encoding="utf-8")
    (tmp_path / "main.py").write_text(
        "import os\nimport numpy as np\nimport requests\n", encoding="utf-8"
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD034"}).scan(tmp_path)

    assert len(report.findings) == 1
    message = report.findings[0].message
    assert "requests" in message  # undeclared third-party
    assert "numpy" not in message  # declared
    assert "os" not in message  # stdlib


def test_undeclared_import_alias_resolves(tmp_path) -> None:
    # cv2 is provided by the opencv-python distribution.
    (tmp_path / "requirements.txt").write_text("opencv-python\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("import cv2\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD034"}).scan(tmp_path)

    assert not report.findings


def test_undeclared_import_alias_resolves_case_insensitive_import(tmp_path) -> None:
    # PIL is provided by the Pillow distribution.
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["Pillow>=10"]\n',
        encoding="utf-8",
    )
    (tmp_path / "main.py").write_text("from PIL import Image\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD034"}).scan(tmp_path)

    assert not report.findings


def test_undeclared_import_reads_optional_dependencies(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'dependencies = ["rich"]\n'
        "\n"
        "[project.optional-dependencies]\n"
        'dev = ["pytest>=8"]\n',
        encoding="utf-8",
    )
    (tmp_path / "test_demo.py").write_text("import pytest\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD034"}).scan(tmp_path)

    assert not report.findings


def test_undeclared_import_reads_marker_dependencies(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        "dependencies = [\n"
        '  "rich>=13.7",\n'
        "  \"tomli>=2.0; python_version < '3.11'\",\n"
        '  "typer>=0.12",\n'
        "]\n",
        encoding="utf-8",
    )
    (tmp_path / "main.py").write_text("import typer\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD034"}).scan(tmp_path)

    assert not report.findings


def test_undeclared_import_reads_poetry_dependencies(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.poetry]\n"
        'name = "demo"\n'
        'version = "0.1.0"\n'
        "\n"
        "[tool.poetry.dependencies]\n"
        'python = ">=3.10"\n'
        'requests = "^2.32"\n'
        "\n"
        "[tool.poetry.group.dev.dependencies]\n"
        'pytest = "^8.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "main.py").write_text("import requests\nimport pytest\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD034"}).scan(tmp_path)

    assert not report.findings


def test_undeclared_import_skipped_without_manifest(tmp_path) -> None:
    (tmp_path / "main.py").write_text("import requests\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD034"}).scan(tmp_path)

    assert not report.findings


def test_undeclared_import_ignores_comments_and_docstrings(tmp_path) -> None:
    (tmp_path / "requirements.txt").write_text("numpy\n", encoding="utf-8")
    (tmp_path / "main.py").write_text(
        '"""Example text:\n'
        "import requests\n"
        "from 10000 samples are drawn\n"
        '"""\n'
        "# from missing_package import demo\n"
        "import numpy as np\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD034"}).scan(tmp_path)

    assert not report.findings


def test_undeclared_import_skips_unparseable_python_files(tmp_path) -> None:
    (tmp_path / "requirements.txt").write_text("numpy\n", encoding="utf-8")
    (tmp_path / "generated.py").write_text(
        'def broken(:\n    """from missing_package import demo"""\n',
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD034"}).scan(tmp_path)

    assert not report.findings
