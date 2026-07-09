from __future__ import annotations

import nbformat

from rrdoctor.config import DEFAULT_CONFIG, deep_merge
from rrdoctor.scanner import Scanner


def test_notebook_large_output_detection() -> None:
    config = deep_merge(DEFAULT_CONFIG, {"thresholds": {"large_notebook_output_kb": 1}})
    report = Scanner(config, include={"RRD060"}).scan("tests/fixtures/notebook-issues-repo")

    assert any(finding.rule_id == "RRD060" for finding in report.findings)


def test_notebook_absolute_path_detection() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD062"}).scan("tests/fixtures/notebook-issues-repo")

    assert any(finding.rule_id == "RRD062" for finding in report.findings)


def test_notebook_absolute_path_ignores_placeholder(tmp_path) -> None:
    notebook_path = tmp_path / "analysis.ipynb"
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell(
                "Write outputs to `/home/user/absolute_path_to_the_output_dir`."
            )
        ]
    )
    nbformat.write(notebook, notebook_path)

    report = Scanner(DEFAULT_CONFIG, include={"RRD062"}).scan(tmp_path)

    assert not report.findings


def test_notebook_absolute_path_ignores_url_path_segments(tmp_path) -> None:
    notebook_path = tmp_path / "analysis.ipynb"
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell(
                "See http://mc-stan.org/users/documentation/case-studies/example.html."
            )
        ]
    )
    nbformat.write(notebook, notebook_path)

    report = Scanner(DEFAULT_CONFIG, include={"RRD062"}).scan(tmp_path)

    assert not report.findings


def test_notebook_out_of_order_detection() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD061"}).scan("tests/fixtures/notebook-issues-repo")

    assert any(finding.rule_id == "RRD061" for finding in report.findings)


def test_notebook_secret_output_ignores_non_secret_token_text(tmp_path) -> None:
    notebook_path = tmp_path / "scaling_laws.ipynb"
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_code_cell(
                "print('tokenizer')",
                outputs=[
                    nbformat.v4.new_output(
                        "stream",
                        name="stdout",
                        text="token: GPT2BPETokenizer\nnum_tokens: 50331648\n",
                    )
                ],
            )
        ]
    )
    nbformat.write(notebook, notebook_path)

    report = Scanner(DEFAULT_CONFIG, include={"RRD063"}).scan(tmp_path)

    assert not report.findings


def test_notebook_secret_output_flags_high_confidence_secret(tmp_path) -> None:
    notebook_path = tmp_path / "analysis.ipynb"
    secret_value = "abc123XYZ789" + "def456GHI"
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_code_cell(
                "print('secret')",
                outputs=[
                    nbformat.v4.new_output(
                        "stream",
                        name="stdout",
                        text=f"api_key: {secret_value}\n",
                    )
                ],
            )
        ]
    )
    nbformat.write(notebook, notebook_path)

    report = Scanner(DEFAULT_CONFIG, include={"RRD063"}).scan(tmp_path)

    assert len(report.findings) == 1
    assert report.findings[0].rule_id == "RRD063"


def test_notebook_secret_output_ignores_low_entropy_placeholder(tmp_path) -> None:
    notebook_path = tmp_path / "analysis.ipynb"
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_code_cell(
                "print('placeholder token')",
                outputs=[
                    nbformat.v4.new_output(
                        "stream",
                        name="stdout",
                        text="api_key: abcabcabcabcabcabcabcabc123456\n",
                    )
                ],
            )
        ]
    )
    nbformat.write(notebook, notebook_path)

    report = Scanner(DEFAULT_CONFIG, include={"RRD063"}).scan(tmp_path)

    assert not report.findings


def test_notebook_secret_output_ignores_generic_fixture_token(tmp_path) -> None:
    fixture_dir = tmp_path / "tests" / "fixtures"
    fixture_dir.mkdir(parents=True)
    notebook_path = fixture_dir / "example.ipynb"
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_code_cell(
                "print('fake token')",
                outputs=[
                    nbformat.v4.new_output(
                        "stream",
                        name="stdout",
                        text="api_key: abc123XYZ789def456GHI\n",
                    )
                ],
            )
        ]
    )
    nbformat.write(notebook, notebook_path)

    report = Scanner(DEFAULT_CONFIG, include={"RRD063"}).scan(tmp_path)

    assert not report.findings


def test_notebook_secret_output_still_flags_provider_key_in_fixture(tmp_path) -> None:
    fixture_dir = tmp_path / "tests" / "fixtures"
    fixture_dir.mkdir(parents=True)
    notebook_path = fixture_dir / "example.ipynb"
    key = "AKIA" + "1234567890ABCDEF"
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_code_cell(
                "print('provider key')",
                outputs=[
                    nbformat.v4.new_output(
                        "stream",
                        name="stdout",
                        text=f"AWS_ACCESS_KEY_ID={key}\n",
                    )
                ],
            )
        ]
    )
    nbformat.write(notebook, notebook_path)

    report = Scanner(DEFAULT_CONFIG, include={"RRD063"}).scan(tmp_path)

    assert len(report.findings) == 1
    assert report.findings[0].rule_id == "RRD063"
