from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.rules.base import has_secret_like_value
from rrdoctor.scanner import Scanner


def test_secret_masking() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD090"}).scan("tests/fixtures/notebook-issues-repo")

    assert report.findings
    evidence = report.findings[0].evidence[0].value or ""
    assert "..." in evidence
    assert "abcdefghijklmnopqrstuvwxyz" not in evidence


def test_generator_token_marker_is_not_a_secret() -> None:
    assert not has_secret_like_value("# Generator token: 10BE3573-1514-4C36-9D1C-5A225CD40393")
    fake_secret = "abcdefghijklmnopqrstuvwxyz" + "123456"
    assert has_secret_like_value("token = " + fake_secret)


def test_uuid_token_value_is_not_a_secret() -> None:
    assert not has_secret_like_value("token: 10BE3573-1514-4C36-9D1C-5A225CD40393")
    assert not has_secret_like_value("secret = 10be3573-1514-4c36-9d1c-5a225cd40393")


def test_url_query_token_is_not_a_secret() -> None:
    signed_asset_url = (
        "url = 'https://example-cdn.invalid/image.jpg?token="
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.long-public-asset-token'"
    )

    assert not has_secret_like_value(signed_asset_url)


def test_token_function_call_is_not_a_secret() -> None:
    assert not has_secret_like_value("token = _emit_tpu_python_callback(")


def test_token_dotted_method_call_is_not_a_secret() -> None:
    assert not has_secret_like_value("token = _given_hyperparameters.set(hparams)")


def test_aws_key_substring_inside_biological_sequence_is_not_a_secret() -> None:
    sequence = "KRVHSFEELERHPDFALPFVLACQSRNAKIATIAIPTIHKLIMAGVV"

    assert not has_secret_like_value(sequence)


def test_standalone_aws_access_key_still_flags() -> None:
    key = "AKIA" + "1234567890ABCDEF"

    assert has_secret_like_value(f"AWS_ACCESS_KEY_ID={key}")


def test_generic_test_token_is_not_a_secret(tmp_path) -> None:
    source = tmp_path / "src" / "package"
    source.mkdir(parents=True)
    (source / "testing_utils.py").write_text(
        'TOKEN = "hf_94wBhPGp6KrrTH3KDchhKpRxZwd6dmHWLL"\n',
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD090"}).scan(tmp_path)

    assert not report.findings


def test_pkgdown_docsearch_key_is_not_a_secret(tmp_path) -> None:
    public_search_key = "ead918d7fe8467a2" + "fd38e97f5bbe3ecb"
    (tmp_path / "_pkgdown.yaml").write_text(
        f"template:\n  docsearch:\n    api_key: {public_search_key}\n    index_name: seurat\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD090"}).scan(tmp_path)

    assert not report.findings


def test_generic_api_key_still_flags(tmp_path) -> None:
    fake_secret = "ead918d7fe8467a2" + "fd38e97f5bbe3ecb"
    (tmp_path / "config.yml").write_text(
        f"api_key: {fake_secret}\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD090"}).scan(tmp_path)

    assert report.findings


def test_gitignore_rule() -> None:
    report = Scanner(DEFAULT_CONFIG, include={"RRD091"}).scan("tests/fixtures/missing-basics-repo")

    assert report.findings
    assert report.findings[0].rule_id == "RRD091"


def test_gitignore_rule_allows_basic_research_coverage(tmp_path) -> None:
    (tmp_path / ".gitignore").write_text(
        "__pycache__/\n*.pyc\n.ipynb_checkpoints/\noutputs/\n.env\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD091"}).scan(tmp_path)

    assert not report.findings


def test_gitignore_rule_flags_low_coverage_file(tmp_path) -> None:
    (tmp_path / ".gitignore").write_text(".DS_Store\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD091"}).scan(tmp_path)

    assert report.findings
    assert "little coverage" in report.findings[0].message
