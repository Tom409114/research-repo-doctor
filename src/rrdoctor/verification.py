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

import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from rrdoctor.models import ScanReport
from rrdoctor.rules.base import read_text

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
    "tools/train.py",
    "tools/test.py",
    "tools/eval.py",
    "tools/evaluate.py",
    "tools/run.py",
    "tools/reproduce.py",
)


def _entrypoint_command(root: Path) -> tuple[list[str] | None, str]:
    """Return (runnable command, display) for the most likely entrypoint."""

    documented = _readme_entrypoint_command(root)
    if documented[1]:
        return documented
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


def _readme_entrypoint_command(root: Path) -> tuple[list[str] | None, str]:
    """Return a conservative README command that looks like a reproducibility entrypoint."""

    readme = root / "README.md"
    if not readme.exists():
        return None, ""
    console_scripts = _project_console_scripts(root)
    for line in _readme_command_lines(read_text(readme)):
        parsed = _parse_documented_entrypoint(line, root, console_scripts)
        if parsed[1]:
            return parsed
    return None, ""


def _readme_command_lines(text: str) -> list[str]:
    """Extract likely command lines from fenced blocks, inline code, and standalone lines."""

    lines: list[str] = []
    for block in re.findall(r"```[^\n]*\n(.*?)```", text, flags=re.DOTALL):
        lines.extend(block.splitlines())
    lines.extend(re.findall(r"`([^`\n]+)`", text))
    lines.extend(text.splitlines())
    return [_strip_command_prompt(line) for line in lines]


def _strip_command_prompt(line: str) -> str:
    stripped = line.strip()
    stripped = re.sub(r"^(?:\$|>|PS\s+[^>]+>|[A-Za-z]:\\[^>]+>)\s*", "", stripped)
    return stripped.strip()


def _parse_documented_entrypoint(
    line: str, root: Path, console_scripts: set[str] | None = None
) -> tuple[list[str] | None, str]:
    if not line or line.startswith("#"):
        return None, ""
    try:
        parts = shlex.split(line, comments=True)
    except ValueError:
        return None, ""
    if not parts:
        return None, ""

    command = parts[0].lower()
    if _is_python_command(command):
        return _parse_documented_python(parts, root)
    if command in {"bash", "sh"}:
        return _parse_documented_shell(parts, root)
    if command == "make":
        return _parse_documented_make(parts, root)
    if command == "snakemake":
        return _parse_documented_snakemake(parts, root)
    if command == "nextflow" and len(parts) > 1 and parts[1] == "run":
        return _parse_documented_nextflow(parts, root)
    if command == "rscript":
        return _parse_documented_script_runner(parts, root, {"run", "reproduce", "train", "eval"})
    if command == "julia":
        return _parse_documented_script_runner(parts, root, {"run", "reproduce", "train", "eval"})
    if console_scripts and command in console_scripts and len(parts) > 1:
        return parts, shlex.join(parts)
    return None, ""


def _parse_documented_python(parts: list[str], root: Path) -> tuple[list[str] | None, str]:
    script_index = _python_script_index(parts)
    if script_index is not None:
        script = _clean_relative(parts[script_index])
        if not _is_python_entrypoint(script) or not (root / script).exists():
            return None, ""
        runnable = [sys.executable, *parts[1:]]
        display = shlex.join(["python", *parts[1:]])
        return runnable, display

    module_index = _python_module_index(parts)
    if module_index is not None:
        module = parts[module_index]
        if _module_entrypoint_exists(module, root) or _module_runner_has_entrypoint_arg(
            parts[module_index + 1 :], root
        ):
            runnable = [sys.executable, *parts[1:]]
            display = shlex.join(["python", *parts[1:]])
            return runnable, display
    return None, ""


def _python_script_index(parts: list[str]) -> int | None:
    index = 1
    while index < len(parts) and parts[index] in {"-u", "-O", "-OO", "-B"}:
        index += 1
    if index >= len(parts) or parts[index] == "-m":
        return None
    return index


def _python_module_index(parts: list[str]) -> int | None:
    index = 1
    while index < len(parts) and parts[index] in {"-u", "-O", "-OO", "-B"}:
        index += 1
    if index >= len(parts) - 1 or parts[index] != "-m":
        return None
    return index + 1


def _module_entrypoint_exists(module: str, root: Path) -> bool:
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$", module):
        return False
    rel = Path(*module.split("."))
    candidates = (
        root / rel.with_suffix(".py"),
        root / rel / "__main__.py",
        root / "src" / rel.with_suffix(".py"),
        root / "src" / rel / "__main__.py",
    )
    return any(path.exists() for path in candidates)


def _module_runner_has_entrypoint_arg(args: list[str], root: Path) -> bool:
    for raw in args:
        if raw.startswith("-"):
            continue
        script = _clean_relative(raw)
        if _is_python_entrypoint(script) and (root / script).exists():
            return True
    return False


def _parse_documented_shell(parts: list[str], root: Path) -> tuple[list[str] | None, str]:
    if len(parts) < 2:
        return None, ""
    script = _clean_relative(parts[1])
    if not _is_shell_entrypoint(script) or not (root / script).exists():
        return None, ""
    return parts, shlex.join(parts)


def _parse_documented_make(parts: list[str], root: Path) -> tuple[list[str] | None, str]:
    if not (root / "Makefile").exists():
        return None, ""
    if len(parts) == 1:
        return parts, "make"
    target = parts[1]
    if target in {"all", "run", "train", "eval", "evaluate", "reproduce", "results"}:
        return parts, shlex.join(parts)
    return None, ""


def _parse_documented_snakemake(parts: list[str], root: Path) -> tuple[list[str] | None, str]:
    if (root / "Snakefile").exists():
        return parts, shlex.join(parts)
    return None, ""


def _parse_documented_nextflow(parts: list[str], root: Path) -> tuple[list[str] | None, str]:
    if len(parts) < 3:
        return None, ""
    workflow = _clean_relative(parts[2])
    if (root / workflow).exists() or (root / "nextflow.config").exists():
        return parts, shlex.join(parts)
    return None, ""


def _parse_documented_script_runner(
    parts: list[str], root: Path, allowed_stems: set[str]
) -> tuple[list[str] | None, str]:
    if len(parts) < 2:
        return None, ""
    script = _clean_relative(parts[1])
    if not (root / script).exists():
        return None, ""
    if Path(script).stem.lower() not in allowed_stems:
        return None, ""
    return parts, shlex.join(parts)


def _is_python_command(command: str) -> bool:
    return command in {"python", "python3", "python.exe", "py"}


def _is_python_entrypoint(path: str) -> bool:
    rel = path.replace("\\", "/")
    name = Path(rel).name.lower()
    return name in {
        "train.py",
        "main.py",
        "run.py",
        "reproduce.py",
        "eval.py",
        "evaluate.py",
    } or bool(
        re.match(
            r"(?i)(?:scripts|tools)/.*\.py$|src/.*(?:train|test|run|eval|evaluate|reproduce).*\.py$",
            rel,
        )
    )


def _project_console_scripts(root: Path) -> set[str]:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return set()
    text = read_text(pyproject)
    scripts: set[str] = set()
    current_table = ""
    for line in text.splitlines():
        stripped = line.strip()
        table_match = re.match(r"\[([^\]]+)\]", stripped)
        if table_match:
            current_table = table_match.group(1).strip()
            continue
        if current_table in {"project.scripts", "tool.poetry.scripts"}:
            script_match = re.match(r"""["']?([A-Za-z0-9_.-]+)["']?\s*=""", stripped)
            if script_match:
                scripts.add(script_match.group(1).lower())
        dotted_match = re.match(r"""scripts\.["']?([A-Za-z0-9_.-]+)["']?\s*=""", stripped)
        if current_table == "project" and dotted_match:
            scripts.add(dotted_match.group(1).lower())
    return scripts


def _is_shell_entrypoint(path: str) -> bool:
    rel = path.replace("\\", "/")
    return bool(re.match(r"(?i)(?:scripts/)?(?:run|reproduce|train|eval).*\.sh$", rel))


def _clean_relative(path: str) -> str:
    return path.replace("\\", "/").removeprefix("./")


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
