from __future__ import annotations

import re
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


def test_readme_citation_matches_citation_cff() -> None:
    citation = Path("CITATION.cff").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    match = re.search(r'^doi:\s*"?([^"\s]+)"?\s*$', citation, re.MULTILINE)

    assert match is not None
    doi = match.group(1)
    assert f"[{doi}](https://doi.org/{doi})" in readme
    assert f"doi = {{{doi}}}" in readme


def test_github_action_examples_use_current_release_tag() -> None:
    version = _project_version()
    expected = f"Tom409114/research-repo-doctor@v{version}"
    checked_files = [
        Path("README.md"),
        *Path("docs").glob("*.md"),
        *Path("examples").glob("*workflow.yml"),
    ]

    for path in checked_files:
        text = path.read_text(encoding="utf-8")
        for match in re.findall(r"Tom409114/research-repo-doctor@v[0-9][^\s`'\"]*", text):
            assert match == expected, f"{path} uses stale action tag {match}"
