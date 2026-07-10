from __future__ import annotations

from rrdoctor.config import apply_cli_overrides, deep_merge, load_config


def test_deep_merge_preserves_defaults() -> None:
    merged = deep_merge({"a": {"b": 1, "c": 2}}, {"a": {"b": 3}})

    assert merged == {"a": {"b": 3, "c": 2}}


def test_load_config_and_cli_override(tmp_path) -> None:
    config_path = tmp_path / ".rrdoctor.yml"
    config_path.write_text(
        """
version: 1
profile: minimal
thresholds:
  large_file_mb: 5
rules:
  RRD001:
    severity: warning
""",
        encoding="utf-8",
    )

    config = load_config(config_path)
    overridden = apply_cli_overrides(
        config, profile="strict", output_format="json", fail_on="warning"
    )

    assert config["thresholds"]["large_file_mb"] == 5
    assert config["rules"]["RRD001"]["severity"] == "warning"
    assert overridden["profile"] == "strict"
    assert overridden["report"]["format"] == "json"
    assert overridden["fail_on"] == "warning"


def test_load_config_discovers_target_repository_outside_cwd(tmp_path, monkeypatch) -> None:
    caller = tmp_path / "caller"
    repository = tmp_path / "repository"
    caller.mkdir()
    repository.mkdir()
    (repository / ".rrdoctor.yml").write_text(
        "thresholds:\n  large_file_mb: 7\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(caller)

    config = load_config(root=repository)

    assert config["thresholds"]["large_file_mb"] == 7


def test_explicit_config_takes_precedence_over_target_repository(tmp_path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / ".rrdoctor.yml").write_text(
        "thresholds:\n  large_file_mb: 7\n",
        encoding="utf-8",
    )
    explicit = tmp_path / "explicit.yml"
    explicit.write_text("thresholds:\n  large_file_mb: 11\n", encoding="utf-8")

    config = load_config(explicit, root=repository)

    assert config["thresholds"]["large_file_mb"] == 11
