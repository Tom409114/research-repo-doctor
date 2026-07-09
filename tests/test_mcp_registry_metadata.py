from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib


def test_mcp_registry_metadata_matches_package_and_launches_optional_extra() -> None:
    manifest = json.loads(Path("server.json").read_text(encoding="utf-8"))
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    readme = Path("README.md").read_text(encoding="utf-8")
    project = pyproject["project"]
    version = project["version"]

    assert manifest["$schema"] == (
        "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
    )
    assert manifest["name"] == "io.github.Tom409114/rrdoctor"
    assert f"<!-- mcp-name: {manifest['name']} -->" in readme
    assert manifest["version"] == version
    assert len(manifest["description"]) <= 100

    package = manifest["packages"][0]
    assert package["registryType"] == "pypi"
    assert package["registryBaseUrl"] == "https://pypi.org"
    assert package["identifier"] == project["name"] == "rrdoctor"
    assert package["version"] == version
    assert package["runtimeHint"] == "uvx"
    assert package["transport"] == {"type": "stdio"}
    assert "environmentVariables" not in package

    runtime_args = [argument["value"] for argument in package["runtimeArguments"]]
    package_args = [argument["value"] for argument in package["packageArguments"]]
    assert ["uvx", *runtime_args, *package_args] == [
        "uvx",
        "--from",
        f"rrdoctor[mcp]=={version}",
        "rrdoctor",
        "mcp",
    ]

    core_dependencies = project["dependencies"]
    assert not any(dependency.startswith("mcp") for dependency in core_dependencies)
    assert project["optional-dependencies"]["mcp"] == ["mcp>=1.0"]
