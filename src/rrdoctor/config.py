"""Configuration loading and profile handling."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "profile": "standard",
    "paths": {
        "include": ["."],
        "exclude": [
            ".git",
            ".venv",
            "node_modules",
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            "dist",
            "build",
        ],
    },
    "thresholds": {
        "large_file_mb": 50,
        "large_notebook_output_kb": 1024,
    },
    "rules": {
        "RRD032": {"enabled": False},
        "RRD042": {"severity": "warning"},
    },
    "fail_on": "error",
    "report": {
        "format": "markdown",
    },
}

PROFILES = (
    "minimal",
    "standard",
    "strict",
    "ml",
    "ml-paper",
    "neurips",
    "icml",
    "acm",
    "fair4rs",
    "joss",
)
FAIL_ON_VALUES = ("none", "error", "warning")
FORMAT_VALUES = ("markdown", "json", "sarif", "agent")

# Each profile activates a set of rule "tags". Base profiles map to themselves.
# Composite profiles (the submission-deadline profiles) inherit base tags so they
# reuse the existing rule set without every rule having to enumerate them.
PROFILE_TAGS: dict[str, tuple[str, ...]] = {
    "minimal": ("minimal",),
    "standard": ("standard",),
    "strict": ("strict",),
    "ml": ("ml",),
    # ML paper artifact: everything strict + ml, plus paper-specific rules.
    "ml-paper": ("ml-paper", "ml", "strict", "standard"),
    # NeurIPS reproducibility checklist superset of ml-paper.
    "neurips": ("neurips", "ml-paper", "ml", "strict", "standard"),
    # ICML shares the ML reproducibility expectations.
    "icml": ("icml", "ml-paper", "ml", "strict", "standard"),
    # ACM Artifact Evaluation (Available / Functional / Reproduced).
    "acm": ("acm", "strict", "standard"),
    # FAIR for Research Software: license, citation, metadata, governance.
    "fair4rs": ("fair4rs", "strict", "standard"),
    # JOSS review checklist: docs, tests, license, contributing.
    "joss": ("joss", "strict", "standard"),
}


def profile_tags(profile: str) -> tuple[str, ...]:
    """Return the rule tags activated by a profile.

    Unknown profiles map to themselves so custom profiles keep working.
    """

    return PROFILE_TAGS.get(profile, (profile,))


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge nested dictionaries without mutating either input."""

    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: Path | None = None, *, root: str | Path | None = None) -> dict[str, Any]:
    """Load YAML configuration, discovering it from ``root`` when provided."""

    config = deepcopy(DEFAULT_CONFIG)
    if path is None:
        search_root = Path(root) if root is not None else Path.cwd()
        default_path = search_root.resolve() / ".rrdoctor.yml"
        path = default_path if default_path.exists() else None
    if path is None:
        return config
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Configuration must be a mapping: {path}")
    return deep_merge(config, cast(dict[str, Any], loaded))


def apply_cli_overrides(
    config: dict[str, Any],
    *,
    profile: str | None = None,
    output_format: str | None = None,
    output: str | None = None,
    fail_on: str | None = None,
) -> dict[str, Any]:
    """Apply command-line overrides to loaded configuration."""

    merged = deepcopy(config)
    if profile:
        merged["profile"] = profile
    if fail_on:
        merged["fail_on"] = fail_on
    if output_format:
        merged.setdefault("report", {})["format"] = output_format
    if output:
        merged.setdefault("report", {})["output"] = output
    return merged


def default_config_text(profile: str = "standard") -> str:
    """Return a documented default config file."""

    config = deepcopy(DEFAULT_CONFIG)
    config["profile"] = profile
    config.setdefault("report", {})["output"] = "rrdoctor-report.md"
    return str(yaml.safe_dump(config, sort_keys=False))
