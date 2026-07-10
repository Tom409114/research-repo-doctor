from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any

from rrdoctor import mcp_server
from rrdoctor.models import ScanReport


class FakeFastMCP:
    """Tiny stand-in for the optional MCP dependency used by tests."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.tools: dict[str, Any] = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator

    def run(self) -> None:
        return None


def test_mcp_scan_discovers_target_repository_config(tmp_path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / ".rrdoctor.yml").write_text(
        "profile: minimal\nrules:\n  RRD001:\n    enabled: false\n",
        encoding="utf-8",
    )

    report = mcp_server._scan(str(repository), None)

    assert report.profile == "minimal"
    assert "RRD001" not in {finding.rule_id for finding in report.findings}

    overridden = mcp_server._scan(str(repository), "standard")

    assert overridden.profile == "standard"


def test_mcp_verify_passes_command_and_timeout(monkeypatch) -> None:
    fastmcp_module = types.ModuleType("mcp.server.fastmcp")
    fastmcp_module.FastMCP = FakeFastMCP
    monkeypatch.setitem(sys.modules, "mcp", types.ModuleType("mcp"))
    monkeypatch.setitem(sys.modules, "mcp.server", types.ModuleType("mcp.server"))
    monkeypatch.setitem(sys.modules, "mcp.server.fastmcp", fastmcp_module)
    captured: dict[str, Any] = {}

    def fake_scan(path: str, profile: str) -> ScanReport:
        captured["scan"] = (path, profile)
        return ScanReport.empty(path, profile)

    def fake_render_verification(
        report: ScanReport,
        root: Path,
        run: bool,
        timeout: int,
        steps=None,
        command: str | None = None,
    ) -> str:
        captured["verify"] = {
            "repository_path": report.repository_path,
            "root": root,
            "run": run,
            "timeout": timeout,
            "command": command,
        }
        return "verification"

    monkeypatch.setattr(mcp_server, "_scan", fake_scan)
    monkeypatch.setattr(mcp_server, "render_verification", fake_render_verification)

    server = mcp_server.build_server()
    result = server.tools["verify"](
        path=".",
        profile="acm",
        run=True,
        command="python train.py --quick",
        timeout=42,
    )

    assert result == "verification"
    assert captured["scan"] == (".", "acm")
    assert captured["verify"]["run"] is True
    assert captured["verify"]["timeout"] == 42
    assert captured["verify"]["command"] == "python train.py --quick"
