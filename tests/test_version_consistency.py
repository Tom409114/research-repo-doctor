from __future__ import annotations

from pathlib import Path

import rrdoctor


def _project_version() -> str:
    for line in Path("pyproject.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("version = "):
            return line.split('"', 2)[1]
    raise AssertionError("pyproject.toml is missing project version")


def test_package_version_metadata_is_consistent() -> None:
    version = _project_version()

    assert rrdoctor.__version__ == version
    assert f"version: {version}" in Path("CITATION.cff").read_text(encoding="utf-8")
    assert f"rrdoctor=={version}" in Path("demo/requirements.txt").read_text(encoding="utf-8")
