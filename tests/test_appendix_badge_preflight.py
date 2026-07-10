from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.reporting.appendix import render_appendix
from rrdoctor.scanner import Scanner


def test_appendix_doi_is_detected_but_not_treated_as_verified_archive(tmp_path) -> None:
    (tmp_path / "README.md").write_text("# DOI Demo\n", encoding="utf-8")
    (tmp_path / "CITATION.cff").write_text(
        "cff-version: 1.2.0\n"
        'title: "DOI Demo"\n'
        'message: "Cite this artifact."\n'
        "authors:\n"
        '  - name: "Example Lab"\n'
        'doi: "10.5281/zenodo.1234567"\n',
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG).scan(tmp_path)
    rendered = render_appendix(report)

    assert "DOI `10.5281/zenodo.1234567` detected; confirm it resolves" in rendered
    assert "confirm it identifies this artifact archive" in rendered
    assert "Publicly available?:** Yes" not in rendered
