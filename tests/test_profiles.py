from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG, PROFILES, apply_cli_overrides, profile_tags
from rrdoctor.scanner import Scanner


def test_new_profiles_registered() -> None:
    for name in ("ml-paper", "neurips", "icml", "acm", "fair4rs", "joss"):
        assert name in PROFILES


def test_profile_tags_inherit() -> None:
    # ml-paper inherits the ml and strict rule sets.
    tags = set(profile_tags("ml-paper"))
    assert {"ml-paper", "ml", "strict", "standard"} <= tags

    # Unknown profiles map to themselves.
    assert profile_tags("custom") == ("custom",)


def test_neurips_profile_runs_ml_rules() -> None:
    config = apply_cli_overrides(DEFAULT_CONFIG, profile="neurips")
    report = Scanner(config).scan("tests/fixtures/ml-project-repo")

    # neurips inherits ml-only rules such as RRD051 (config files) and RRD054 (CUDA).
    minimal = apply_cli_overrides(DEFAULT_CONFIG, profile="minimal")
    minimal_report = Scanner(minimal).scan("tests/fixtures/ml-project-repo")

    assert report.rules_evaluated > minimal_report.rules_evaluated
    assert report.profile == "neurips"
