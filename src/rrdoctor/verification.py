"""Reproducibility verification ladder (L1 static, L2 build, L3 execution).

L1 is fully deterministic and offline. With ``run=True`` (the CLI ``--run`` flag)
L2 actually shells out to a dependency resolver and L3 actually executes a
declared entrypoint, each under a timeout, capturing the real result. When a
tool is missing or execution is not requested, the step says so honestly instead
of pretending to have run.

Security note: ``--run`` executes code and resolvers from the target repository.
Only use it on repositories you trust.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from rrdoctor.models import ScanReport

DEFAULT_TIMEOUT = 300


@dataclass(frozen=True)
class LadderStep:
    """One rung of the verification ladder."""

    level: str
    title: str
    status: str  # "pass", "fail", "skipped", "blocked"
    detail: str
    commands: list[str] = field(default_factory=list)
    log: str = ""


def _run_command(cmd: list[str], cwd: Path, timeout: int) -> tuple[int | None, str]:
    """Run a command, returning (returncode, captured tail).

    returncode is None when the tool is not installed. A timeout maps to 124.
    """

    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return None, f"tool not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"
    output = (proc.stdout or "") + (proc.stderr or "")
    tail = "\n".join(output.strip().splitlines()[-12:])
    return proc.returncode, tail


def _l1_step(report: ScanReport) -> LadderStep:
    errors = report.summary.get("error", 0)
    warnings = report.summary.get("warning", 0)
    if errors:
        status, detail = "fail", f"{errors} error finding(s) block release hygiene."
    elif warnings:
        status, detail = "pass", f"No errors; {warnings} warning(s) to review."
    else:
        status, detail = "pass", "No error or warning findings."
    return LadderStep("L1", "Static release hygiene", status, detail)


def _build_plan(root: Path) -> tuple[list[str], str | None, str]:
    """Return (display commands, runnable argv-as-command, missing-tool name).

    The runnable command is the one L2 actually executes with ``--run``.
    """

    display: list[str] = []
    runnable: str | None = None
    missing = ""

    has_req = (root / "requirements.txt").exists()
    has_pyproject = (root / "pyproject.toml").exists()
    if has_req or has_pyproject:
        target = "requirements.txt" if has_req else "pyproject.toml"
        if shutil.which("uv"):
            display.append(f"uv pip compile {target}  # resolve Python dependencies")
            runnable = f"uv pip compile {target}"
        elif shutil.which("pip"):
            arg = f"-r {target}" if has_req else "."
            display.append(f"pip install --dry-run {arg}  # resolve Python dependencies")
            runnable = f"pip install --dry-run {arg}"
        else:
            missing = "uv or pip"
    elif (root / "environment.yml").exists() or (root / "conda.yml").exists():
        if shutil.which("conda") or shutil.which("mamba"):
            display.append("conda env create -f environment.yml --dry-run")
            runnable = "conda env create -f environment.yml --dry-run"
        else:
            missing = "conda/mamba"
    elif (root / "renv.lock").exists() or (root / "DESCRIPTION").exists():
        if shutil.which("Rscript"):
            display.append("Rscript -e 'renv::restore()'")
            runnable = "Rscript -e renv::restore()"
        else:
            missing = "Rscript (R)"

    return display, runnable, missing


def _l2_step(root: Path, run: bool, timeout: int) -> LadderStep:
    display, runnable, missing = _build_plan(root)
    if not display and not missing:
        return LadderStep(
            "L2",
            "Environment is resolvable",
            "skipped",
            "No dependency manifest detected to build.",
        )
    if missing:
        return LadderStep(
            "L2",
            "Environment is resolvable",
            "blocked",
            f"Required tooling not found: {missing}.",
            commands=display,
        )
    if not run:
        return LadderStep(
            "L2",
            "Environment is resolvable",
            "skipped",
            "Static mode. Re-run with --run to actually resolve dependencies.",
            commands=display,
        )

    assert runnable is not None
    code, log = _run_command(runnable.split(), root, timeout)
    if code is None:
        status, detail = "blocked", "Resolver tool disappeared between detection and run."
    elif code == 0:
        status, detail = "pass", "Dependencies resolved successfully."
    else:
        status, detail = "fail", f"Resolution failed (exit {code}). See log."
    return LadderStep("L2", "Environment is resolvable", status, detail, commands=display, log=log)


_PYTHON_ENTRYPOINTS = (
    "train.py",
    "main.py",
    "run.py",
    "reproduce.py",
    "eval.py",
    "evaluate.py",
    "scripts/train.py",
    "scripts/main.py",
    "scripts/run.py",
    "scripts/reproduce.py",
    "scripts/eval.py",
    "scripts/evaluate.py",
)


def _entrypoint_command(root: Path) -> tuple[list[str] | None, str]:
    """Return (runnable command, display) for the most likely entrypoint."""

    if (root / "scripts" / "reproduce.sh").exists():
        return ["bash", "scripts/reproduce.sh"], "bash scripts/reproduce.sh"
    if (root / "scripts" / "run.sh").exists():
        return ["bash", "scripts/run.sh"], "bash scripts/run.sh"
    if (root / "Makefile").exists():
        return ["make"], "make  # default target"
    for entrypoint in _PYTHON_ENTRYPOINTS:
        if (root / entrypoint).exists():
            return [sys.executable, entrypoint], f"python {entrypoint}"
    notebooks = sorted(root.rglob("*.ipynb"))
    if notebooks and shutil.which("papermill"):
        rel = notebooks[0].relative_to(root).as_posix()
        return ["papermill", rel, "-"], f"papermill {rel} (execute notebook)"
    if notebooks:
        rel = notebooks[0].relative_to(root).as_posix()
        return None, f"papermill {rel}  (papermill not installed)"
    return None, ""


def _l3_step(root: Path, run: bool, timeout: int) -> LadderStep:
    runnable, display = _entrypoint_command(root)
    if not display:
        return LadderStep(
            "L3",
            "Declared entrypoint produces output",
            "skipped",
            "No reproduction entrypoint or notebook detected.",
        )
    commands = [display]
    if not run:
        return LadderStep(
            "L3",
            "Declared entrypoint produces output",
            "skipped",
            "Static mode. Re-run with --run to execute the entrypoint (runs repo code).",
            commands=commands,
        )
    if runnable is None:
        return LadderStep(
            "L3",
            "Declared entrypoint produces output",
            "blocked",
            "Entrypoint detected but its runner is not installed.",
            commands=commands,
        )
    code, log = _run_command(runnable, root, timeout)
    if code is None:
        status, detail = "blocked", "Entrypoint runner is not installed."
    elif code == 0:
        status, detail = "pass", "Entrypoint executed without error."
    else:
        status, detail = "fail", f"Entrypoint failed (exit {code}). See log."
    return LadderStep(
        "L3", "Declared entrypoint produces output", status, detail, commands=commands, log=log
    )


_ICON = {"pass": "PASS", "fail": "FAIL", "skipped": "SKIP", "blocked": "BLOCKED"}


def build_steps(report: ScanReport, root: Path, run: bool, timeout: int) -> list[LadderStep]:
    """Compute all ladder steps."""

    return [_l1_step(report), _l2_step(root, run, timeout), _l3_step(root, run, timeout)]


def render_verification(
    report: ScanReport, root: Path, run: bool, timeout: int = DEFAULT_TIMEOUT
) -> str:
    """Render the verification ladder as Markdown."""

    steps = build_steps(report, root, run, timeout)
    lines = [
        "# Reproducibility verification",
        "",
        f"- Repository: `{report.repository_path}`",
        f"- Mode: {'dynamic (--run)' if run else 'static'}",
        "",
        "| Level | Check | Status |",
        "| --- | --- | --- |",
    ]
    for step in steps:
        lines.append(f"| {step.level} | {step.title} | {_ICON.get(step.status, step.status)} |")
    lines.append("")
    for step in steps:
        lines.append(f"## {step.level} - {step.title}")
        lines.append("")
        lines.append(step.detail)
        if step.commands:
            lines.append("")
            lines.append("```bash")
            lines.extend(step.commands)
            lines.append("```")
        if step.log:
            lines.append("")
            lines.append("<details><summary>log</summary>")
            lines.append("")
            lines.append("```")
            lines.append(step.log)
            lines.append("```")
            lines.append("")
            lines.append("</details>")
        lines.append("")
    if not run:
        lines.append(
            "> L1 is deterministic. L2/L3 are static here; pass --run to actually resolve "
            "dependencies and execute the entrypoint (only on repositories you trust)."
        )
        lines.append("")
    return "\n".join(lines)


def verification_failed(report: ScanReport) -> bool:
    """Whether L1 failed (used for exit codes)."""

    return report.summary.get("error", 0) > 0
