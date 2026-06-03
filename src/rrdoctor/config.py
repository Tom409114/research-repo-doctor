"""Configuration loading and profile handling."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

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
        "output": "rrdoctor-report.md",
    },
}

PROFILES = ("minimal", "standard", "strict", "ml")
FAIL_ON_VALUES = ("none", "error", "warning")
FORMAT_VALUES = ("markdown", "json", "sarif")


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge nested dictionaries without mutating either input."""

    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load configuration from a YAML file, returning defaults when absent."""

    config = deepcopy(DEFAULT_CONFIG)
    if path is None:
        default_path = Path.cwd() / ".rrdoctor.yml"
        path = default_path if default_path.exists() else None
    if path is None:
        return config
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Configuration must be a mapping: {path}")
    return deep_merge(config, loaded)


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
    return yaml.safe_dump(config, sort_keys=False)
