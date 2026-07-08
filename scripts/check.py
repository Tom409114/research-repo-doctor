"""Run the local maintainer quality gate.

This script mirrors the CI/PR checklist without requiring GNU make, so it works
on Windows, macOS, and Linux as long as the development dependencies are
installed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS: tuple[tuple[str, ...], ...] = (
    ("ruff", "format", "--check", "."),
    ("ruff", "check", "."),
    (sys.executable, "-m", "mypy"),
    (sys.executable, "-m", "pytest", "-q"),
    (
        sys.executable,
        "-m",
        "rrdoctor",
        "scan",
        ".",
        "--profile",
        "standard",
        "--fail-on",
        "none",
        "--output",
        "examples/reports/self-scan-report.md",
    ),
)


def main() -> int:
    for command in COMMANDS:
        print("+ " + " ".join(command), flush=True)
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
