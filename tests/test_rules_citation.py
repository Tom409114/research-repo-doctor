from __future__ import annotations

from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def _scan(root: Path, rule_id: str):
    return Scanner(DEFAULT_CONFIG, include={rule_id}).scan(root)


def test_citation_rule_accepts_citing_section(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "## Citing this work\n\n"
        "If you use this code or data, please cite the associated paper.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD020")

    assert not report.findings


def test_citation_rule_accepts_bibtex_entry(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n## BibTeX\n\n```bibtex\n@article{demo2026,\n  title = {Demo}\n}\n```\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD020")

    assert not report.findings


def test_citation_rule_accepts_doi_link(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nReference implementation for https://doi.org/10.1000/example.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD020")

    assert not report.findings


def test_citation_rule_flags_absent_guidance(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nUsage details are coming soon.\n", encoding="utf-8"
    )

    report = _scan(tmp_path, "RRD020")

    assert report.findings
