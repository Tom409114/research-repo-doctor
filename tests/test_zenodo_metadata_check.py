from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_zenodo_script():
    path = Path("scripts/check_zenodo_metadata.py")
    spec = importlib.util.spec_from_file_location("check_zenodo_metadata", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _record(*, version: str = "v0.2.22", doi: str = "10.5281/zenodo.21285257") -> dict:
    return {
        "doi": doi,
        "conceptdoi": "10.5281/zenodo.21045161",
        "metadata": {
            "version": version,
            "creators": [{"name": "Maintainers, Research Repo Doctor"}],
            "related_identifiers": [
                {"identifier": "https://github.com/Tom409114/research-repo-doctor/tree/v0.2.22"}
            ],
        },
        "files": [{"key": "Tom409114/research-repo-doctor-v0.2.22.zip"}],
    }


def test_zenodo_metadata_accepts_current_release_and_warns_about_generic_creator() -> None:
    script = _load_zenodo_script()

    result = script.validate_record(_record(), "0.2.22", "10.5281/zenodo.21285257")

    assert result.ok is True
    assert "matches rrdoctor 0.2.22" in result.message
    assert "creator metadata is still generic" in result.warnings[0]


def test_zenodo_metadata_rejects_stale_release_version() -> None:
    script = _load_zenodo_script()

    result = script.validate_record(_record(version="v0.2.3"), "0.2.22", "10.5281/zenodo.21285257")

    assert result.ok is False
    assert "version is 0.2.3" in result.message


def test_zenodo_metadata_rejects_wrong_release_doi() -> None:
    script = _load_zenodo_script()

    result = script.validate_record(
        _record(doi="10.5281/zenodo.21045373"),
        "0.2.22",
        "10.5281/zenodo.21285257",
    )

    assert result.ok is False
    assert "expected 10.5281/zenodo.21285257" in result.message
