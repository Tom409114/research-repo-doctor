"""MCP server exposing rrdoctor as tools for coding agents.

This makes rrdoctor a deterministic "definition of done" that agents like Claude
Code, Cursor, or Copilot can call directly: scan, verify, and generate an
artifact appendix as MCP tools.

Requires the optional dependency: ``pip install rrdoctor[mcp]``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rrdoctor.config import apply_cli_overrides, load_config
from rrdoctor.models import ScanReport
from rrdoctor.reporting.appendix import render_appendix, render_checklist
from rrdoctor.reporting.markdown import render_markdown
from rrdoctor.scanner import Scanner
from rrdoctor.verification import render_verification


def _scan(path: str, profile: str) -> ScanReport:
    config = apply_cli_overrides(load_config(None), profile=profile)
    return Scanner(config).scan(path)


def build_server() -> Any:
    """Construct the FastMCP server with rrdoctor tools registered."""

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise SystemExit(
            "The MCP server needs the optional dependency. Install with:\n"
            "    pip install 'rrdoctor[mcp]'"
        ) from exc

    server = FastMCP("rrdoctor")

    @server.tool()
    def scan(path: str = ".", profile: str = "standard") -> str:
        """Audit a research repository and return a Markdown reproducibility report."""

        return render_markdown(_scan(path, profile))

    @server.tool()
    def verify(
        path: str = ".",
        profile: str = "standard",
        run: bool = False,
        command: str | None = None,
    ) -> str:
        """Run the L1/L2/L3 reproducibility verification ladder."""

        report = _scan(path, profile)
        return render_verification(report, Path(path).resolve(), run, command=command)

    @server.tool()
    def appendix(path: str = ".", profile: str = "acm") -> str:
        """Generate an ACM-style Artifact Appendix plus the ACM/NeurIPS checklist mapping."""

        report = _scan(path, profile)
        return render_appendix(report) + "\n\n" + render_checklist(report)

    return server


def run() -> None:
    """Run the MCP server over stdio."""

    build_server().run()
