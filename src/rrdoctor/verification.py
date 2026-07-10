"""Reproducibility verification ladder (L1 static, L2 build, L3 execution).

L1 is fully deterministic and offline. With ``run=True`` (the CLI ``--run`` flag)
L2 creates a temporary isolated environment and installs declared dependencies
for supported Python repositories. L3 then executes a declared entrypoint in
that environment. Other ecosystems retain an honest resolver preflight. Every
dynamic command runs under a timeout and captures the real result. When a tool
is missing or execution is not requested, the step says so instead of pretending
to have run.

Security note: ``--run`` executes code and resolvers from the target repository.
Only use it on repositories you trust.
"""

from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

from rrdoctor.models import ScanReport
from rrdoctor.rules.base import read_text

DEFAULT_TIMEOUT = 300
PYTHON_L2_MANIFESTS = (
    "requirements.txt",
    "requirements/base.txt",
    "requirements/main.txt",
    "requirements-dev.txt",
    "requirements/dev.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
)
CONDA_L2_MANIFESTS = ("environment.yml", "environment.yaml", "conda.yml", "conda.yaml")


@dataclass(frozen=True)
class LadderStep:
    """One rung of the verification ladder."""

    level: str
    title: str
    status: str  # "pass", "fail", "skipped", "blocked"
    detail: str
    commands: list[str] = field(default_factory=list)
    log: str = ""
    source: str = ""


@dataclass(frozen=True)
class _PythonRuntime:
    """Temporary Python environment shared by L2 and L3."""

    python: Path
    bin_dir: Path
    env: dict[str, str]
    temp_root: Path


def _run_command(
    cmd: list[str],
    cwd: Path,
    timeout: int,
    env: dict[str, str] | None = None,
) -> tuple[int | None, str]:
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
            env=env,
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

    python_manifest = _first_existing(root, PYTHON_L2_MANIFESTS)
    if python_manifest:
        target = python_manifest.as_posix()
        if target in {"setup.py", "setup.cfg"} and shutil.which("pip"):
            display.append("pip install --dry-run .  # resolve Python dependencies")
            runnable = "pip install --dry-run ."
        elif target in {"setup.py", "setup.cfg"}:
            missing = "pip"
        elif shutil.which("uv"):
            display.append(f"uv pip compile {target}  # resolve Python dependencies")
            runnable = f"uv pip compile {target}"
        elif shutil.which("pip"):
            arg = f"-r {target}" if target.endswith(".txt") else "."
            display.append(f"pip install --dry-run {arg}  # resolve Python dependencies")
            runnable = f"pip install --dry-run {arg}"
        else:
            missing = "uv or pip"

    elif conda_manifest := _first_existing(root, CONDA_L2_MANIFESTS):
        target = conda_manifest.as_posix()
        conda_tool = _first_available_tool(("conda", "mamba"))
        if conda_tool:
            display.append(f"{conda_tool} env create -f {target} --dry-run")
            runnable = f"{conda_tool} env create -f {target} --dry-run"
        else:
            missing = "conda/mamba"
    elif (root / "renv.lock").exists() or (root / "DESCRIPTION").exists():
        if shutil.which("Rscript"):
            display.append("Rscript -e 'renv::restore()'")
            runnable = "Rscript -e renv::restore()"
        else:
            missing = "Rscript (R)"

    return display, runnable, missing


def _first_existing(root: Path, candidates: tuple[str, ...]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.exists():
            return Path(candidate)
    return None


def _first_available_tool(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if shutil.which(candidate):
            return candidate
    return None


def _python_runtime_paths(venv_root: Path) -> tuple[Path, Path]:
    bin_dir = venv_root / ("Scripts" if sys.platform == "win32" else "bin")
    python = bin_dir / ("python.exe" if sys.platform == "win32" else "python")
    return python, bin_dir


def _python_runtime_environment(venv_root: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env["VIRTUAL_ENV"] = str(venv_root)
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    env["PYTHONNOUSERSITE"] = "1"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    return env


def _read_pyproject(root: Path) -> tuple[dict[str, Any], str]:
    path = root / "pyproject.toml"
    try:
        parsed = tomllib.loads(read_text(path))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return {}, f"Could not parse pyproject.toml: {exc}"
    return parsed, ""


def _python_install_plan(
    root: Path,
    manifest: Path,
    runtime_python: Path,
) -> tuple[list[str] | None, str, str]:
    """Return install argv, display command, and a planning error."""

    target = manifest.as_posix()
    base = [
        str(runtime_python),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-input",
    ]
    display_base = [
        "python",
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-input",
    ]

    if target.endswith(".txt"):
        args = ["-r", target]
        return [*base, *args], shlex.join([*display_base, *args]), ""

    if target in {"setup.py", "setup.cfg"}:
        return [*base, "."], shlex.join([*display_base, "."]), ""

    if target != "pyproject.toml":
        return None, "", f"Unsupported Python dependency manifest: {target}"

    parsed, error = _read_pyproject(root)
    if error:
        return None, "", error

    if isinstance(parsed.get("build-system"), dict):
        return [*base, "."], shlex.join([*display_base, "."]), ""

    project = parsed.get("project")
    dependencies = project.get("dependencies", []) if isinstance(project, dict) else []
    if not isinstance(dependencies, list) or not all(
        isinstance(dependency, str) for dependency in dependencies
    ):
        return None, "", "pyproject.toml project.dependencies must be a list of strings"
    if dependencies:
        return [*base, *dependencies], shlex.join([*display_base, *dependencies]), ""
    return None, "", ""


def _sanitize_runtime_log(log: str, temp_root: Path, repo_root: Path | None = None) -> str:
    sanitized = log
    replacements = [(temp_root, "<temporary-environment>")]
    if repo_root is not None:
        replacements.append((repo_root, "<repository-root>"))
    replacements.append((Path.home(), "<home>"))
    flags = re.IGNORECASE if sys.platform == "win32" else 0
    for path, label in replacements:
        variants = {str(path), path.as_posix(), str(path).replace("\\", "/")}
        for value in sorted(variants, key=len, reverse=True):
            sanitized = re.sub(re.escape(value), label, sanitized, flags=flags)
    return sanitized


def _prepare_python_runtime(
    root: Path,
    manifest: Path,
    temp_root: Path,
    timeout: int,
) -> tuple[LadderStep, _PythonRuntime | None]:
    venv_root = temp_root / "venv"
    commands = ["python -m venv <temporary-environment>"]
    create_code, create_log = _run_command(
        [sys.executable, "-m", "venv", str(venv_root)],
        root,
        timeout,
    )
    create_log = _sanitize_runtime_log(create_log, temp_root, root)
    if create_code is None:
        return (
            LadderStep(
                "L2",
                "Environment is installable",
                "blocked",
                "The current Python interpreter could not create an isolated environment.",
                commands=commands,
                log=create_log,
            ),
            None,
        )
    if create_code != 0:
        return (
            LadderStep(
                "L2",
                "Environment is installable",
                "fail",
                f"Creating the isolated Python environment failed (exit {create_code}).",
                commands=commands,
                log=create_log,
            ),
            None,
        )

    runtime_python, bin_dir = _python_runtime_paths(venv_root)
    runtime = _PythonRuntime(
        runtime_python,
        bin_dir,
        _python_runtime_environment(venv_root, bin_dir),
        temp_root,
    )
    install_argv, install_display, plan_error = _python_install_plan(root, manifest, runtime_python)
    if plan_error:
        return (
            LadderStep(
                "L2",
                "Environment is installable",
                "fail",
                plan_error,
                commands=commands,
                log=create_log,
            ),
            None,
        )
    if install_argv is None:
        return (
            LadderStep(
                "L2",
                "Environment is installable",
                "pass",
                "Created an isolated Python environment; no runtime dependencies were declared.",
                commands=commands,
                log=create_log,
            ),
            runtime,
        )

    commands.append(install_display)
    install_code, install_log = _run_command(
        install_argv,
        root,
        timeout,
        env=runtime.env,
    )
    log = _sanitize_runtime_log(
        "\n".join(part for part in (create_log, install_log) if part),
        temp_root,
        root,
    )
    if install_code is None:
        return (
            LadderStep(
                "L2",
                "Environment is installable",
                "blocked",
                "pip is unavailable inside the isolated Python environment.",
                commands=commands,
                log=log,
            ),
            None,
        )
    if install_code != 0:
        return (
            LadderStep(
                "L2",
                "Environment is installable",
                "fail",
                f"Installing declared dependencies failed (exit {install_code}). See log.",
                commands=commands,
                log=log,
            ),
            None,
        )
    return (
        LadderStep(
            "L2",
            "Environment is installable",
            "pass",
            "Created an isolated Python environment and installed declared dependencies.",
            commands=commands,
            log=log,
        ),
        runtime,
    )


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
            "Static mode. Re-run with --run to prepare the dynamic environment.",
            commands=display,
        )

    assert runnable is not None
    code, log = _run_command(shlex.split(runnable), root, timeout)
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
    "infer.py",
    "inference.py",
    "predict.py",
    "sample.py",
    "generate.py",
    "demo.py",
    "scripts/train.py",
    "scripts/main.py",
    "scripts/run.py",
    "scripts/reproduce.py",
    "scripts/eval.py",
    "scripts/evaluate.py",
    "scripts/infer.py",
    "scripts/inference.py",
    "scripts/predict.py",
    "scripts/sample.py",
    "scripts/generate.py",
    "scripts/demo.py",
    "tools/train.py",
    "tools/test.py",
    "tools/eval.py",
    "tools/evaluate.py",
    "tools/infer.py",
    "tools/inference.py",
    "tools/predict.py",
    "tools/sample.py",
    "tools/generate.py",
    "tools/demo.py",
    "tools/run.py",
    "tools/reproduce.py",
)
SCRIPT_ENTRYPOINT_STEMS = {
    "run",
    "reproduce",
    "train",
    "eval",
    "evaluate",
    "infer",
    "inference",
    "predict",
    "sample",
    "generate",
    "demo",
}


def _entrypoint_command(root: Path) -> tuple[list[str] | None, str]:
    """Return (runnable command, display) for the most likely entrypoint."""

    runnable, display, _source = _entrypoint_command_with_source(root)
    return runnable, display


def _entrypoint_command_with_source(root: Path) -> tuple[list[str] | None, str, str]:
    """Return (runnable command, display, source) for the most likely entrypoint."""

    documented = _readme_entrypoint_command(root)
    if documented[1]:
        return documented[0], documented[1], "README command"
    if (root / "scripts" / "reproduce.sh").exists():
        return ["bash", "scripts/reproduce.sh"], "bash scripts/reproduce.sh", "scripts/reproduce.sh"
    if (root / "scripts" / "run.sh").exists():
        return ["bash", "scripts/run.sh"], "bash scripts/run.sh", "scripts/run.sh"
    if (root / "Makefile").exists():
        return ["make"], "make  # default target", "Makefile default target"
    for entrypoint in _PYTHON_ENTRYPOINTS:
        if (root / entrypoint).exists():
            return (
                [sys.executable, entrypoint],
                f"python {entrypoint}",
                f"common entrypoint `{entrypoint}`",
            )
    for entrypoint in _candidate_root_python_entrypoints(root):
        return (
            [sys.executable, entrypoint],
            f"python {entrypoint}",
            f"root paper script `{entrypoint}`",
        )
    notebooks = sorted(root.rglob("*.ipynb"))
    if notebooks and shutil.which("papermill"):
        rel = notebooks[0].relative_to(root).as_posix()
        return (
            ["papermill", rel, "-"],
            f"papermill {rel} (execute notebook)",
            f"first notebook `{rel}`",
        )
    if notebooks:
        rel = notebooks[0].relative_to(root).as_posix()
        return None, f"papermill {rel}  (papermill not installed)", f"first notebook `{rel}`"
    return None, "", ""


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
        return _parse_documented_script_runner(parts, root, SCRIPT_ENTRYPOINT_STEMS)
    if command == "julia":
        return _parse_documented_script_runner(parts, root, SCRIPT_ENTRYPOINT_STEMS)
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
    if target in {"all", "results", *SCRIPT_ENTRYPOINT_STEMS}:
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
    executable = Path(command).name.casefold()
    return executable in {"py", "py.exe"} or bool(
        re.fullmatch(r"python(?:\d+(?:\.\d+)?)?(?:\.exe)?", executable)
    )


def _is_python_entrypoint(path: str) -> bool:
    rel = path.replace("\\", "/")
    name = Path(rel).name.lower()
    return (
        name
        in {
            "train.py",
            "main.py",
            "run.py",
            "reproduce.py",
            "eval.py",
            "evaluate.py",
            "infer.py",
            "inference.py",
            "predict.py",
            "sample.py",
            "generate.py",
            "demo.py",
        }
        or bool(
            re.match(
                r"(?i)^(?:train|main|run|reproduce|eval|evaluate|infer|inference|predict|sample|generate|demo)[_-].+\.py$",
                name,
            )
        )
        or bool(
            re.match(
                r"(?i)(?:scripts|tools)/.*\.py$|src/.*(?:train|test|run|eval|evaluate|infer|inference|predict|sample|generate|demo|reproduce).*\.py$",
                rel,
            )
        )
    )


def _candidate_root_python_entrypoints(root: Path) -> list[str]:
    candidates: list[str] = []
    for pattern in (
        "main_*.py",
        "main-*.py",
        "train_*.py",
        "train-*.py",
        "run_*.py",
        "run-*.py",
        "eval_*.py",
        "eval-*.py",
        "evaluate_*.py",
        "evaluate-*.py",
        "reproduce_*.py",
        "reproduce-*.py",
    ):
        candidates.extend(path.name for path in root.glob(pattern) if path.is_file())
    return sorted(set(candidates))


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


def _specified_entrypoint_command(command: str | None) -> tuple[list[str] | None, str]:
    """Parse a user-specified entrypoint command without invoking a shell."""

    if command is None:
        return None, ""
    try:
        parts = shlex.split(command)
    except ValueError:
        return None, ""
    if not parts:
        return None, ""
    return parts, shlex.join(parts)


def _runtime_argv(runnable: list[str], runtime: _PythonRuntime) -> list[str]:
    if not runnable:
        return runnable
    executable = Path(runnable[0]).name.casefold()
    if _is_python_command(executable) and executable not in {"py", "py.exe"}:
        return [str(runtime.python), *runnable[1:]]
    if executable in {"py", "py.exe"}:
        args = runnable[1:]
        if args and re.fullmatch(r"-\d+(?:\.\d+)?", args[0]):
            args = args[1:]
        return [str(runtime.python), *args]
    return runnable


def _l3_step(
    root: Path,
    run: bool,
    timeout: int,
    command: str | None = None,
    runtime: _PythonRuntime | None = None,
) -> LadderStep:
    specified = command is not None
    if specified:
        runnable, display = _specified_entrypoint_command(command)
        source = "specified --command"
    else:
        runnable, display, source = _entrypoint_command_with_source(root)
    source_label = source or "entrypoint"
    if not display:
        return LadderStep(
            "L3",
            "Declared entrypoint produces output",
            "blocked" if specified else "skipped",
            "The specified command could not be parsed."
            if specified
            else "No reproduction entrypoint or notebook detected.",
            source=source,
        )
    commands = [display]
    if not run:
        return LadderStep(
            "L3",
            "Declared entrypoint produces output",
            "skipped",
            f"Static mode. L3 command source: {source_label}. "
            "Re-run with --run to execute it (runs repo code).",
            commands=commands,
            source=source,
        )
    if runnable is None:
        return LadderStep(
            "L3",
            "Declared entrypoint produces output",
            "blocked",
            f"Entrypoint detected from {source_label}, but its runner is not installed.",
            commands=commands,
            source=source,
        )
    executed = _runtime_argv(runnable, runtime) if runtime is not None else runnable
    code, log = _run_command(
        executed,
        root,
        timeout,
        env=runtime.env if runtime is not None else None,
    )
    if runtime is not None:
        log = _sanitize_runtime_log(log, runtime.temp_root, root)
    environment = " in the isolated Python environment" if runtime is not None else ""
    if code is None:
        status, detail = (
            "blocked",
            f"Entrypoint runner is not installed{environment}. Command source: {source_label}.",
        )
    elif code == 0:
        status, detail = (
            "pass",
            f"Entrypoint executed without error{environment}. Command source: {source_label}.",
        )
    else:
        status, detail = (
            "fail",
            f"Entrypoint failed (exit {code}){environment}. "
            f"Command source: {source_label}. See log.",
        )
    return LadderStep(
        "L3",
        "Declared entrypoint produces output",
        status,
        detail,
        commands=commands,
        log=log,
        source=source,
    )


_ICON = {"pass": "PASS", "fail": "FAIL", "skipped": "SKIP", "blocked": "BLOCKED"}


def build_steps(
    report: ScanReport,
    root: Path,
    run: bool,
    timeout: int,
    command: str | None = None,
) -> list[LadderStep]:
    """Compute all ladder steps."""

    l1 = _l1_step(report)
    python_manifest = _first_existing(root, PYTHON_L2_MANIFESTS)
    if run and python_manifest is not None:
        with tempfile.TemporaryDirectory(prefix="rrdoctor-verify-") as temp_dir:
            l2, runtime = _prepare_python_runtime(
                root,
                python_manifest,
                Path(temp_dir),
                timeout,
            )
            if runtime is None:
                l3 = LadderStep(
                    "L3",
                    "Declared entrypoint produces output",
                    "blocked",
                    "L3 was not executed because isolated Python environment preparation failed.",
                )
            else:
                l3 = _l3_step(root, run, timeout, command, runtime)
        return [l1, l2, l3]

    return [
        l1,
        _l2_step(root, run, timeout),
        _l3_step(root, run, timeout, command),
    ]


def render_verification(
    report: ScanReport,
    root: Path,
    run: bool,
    timeout: int = DEFAULT_TIMEOUT,
    steps: list[LadderStep] | None = None,
    command: str | None = None,
    fail_on: str = "error",
) -> str:
    """Render the verification ladder as Markdown."""

    steps = steps or build_steps(report, root, run, timeout, command)
    failed = verification_failed(report, steps if run else None, fail_on)
    l3_source = _l3_source(steps)
    repo_label = root.name or "."
    outcome = "FAIL" if failed else "PASS"
    if not run:
        outcome += " (L1 static only)"
    lines = [
        "# Reproducibility verification",
        "",
        f"- Repository: `{repo_label}`",
        f"- Mode: {'dynamic (--run)' if run else 'static'}",
        f"- Gate outcome: **{outcome}**",
        f"- Failure threshold: `{fail_on}`",
        f"- Timeout per dynamic step: `{timeout}s`",
    ]
    if command is not None:
        lines.append(f"- L3 command: `{command}`")
    lines.extend(
        [
            "",
            "## Evidence summary",
            "",
            "- L1 always uses deterministic local static checks.",
            "- L2 creates a temporary isolated environment and installs declared Python "
            "dependencies when dynamic mode is enabled and a supported Python manifest exists.",
            "- L2 uses an ecosystem resolver preflight when isolated installation is not "
            "supported for the detected manifest.",
            "- L3 executes the detected or specified entrypoint only when dynamic mode is enabled.",
            f"- L3 command source: {l3_source}."
            if l3_source
            else "- L3 command source: none detected.",
            (
                "- Trust boundary: dynamic mode executed target-repository commands in this "
                "checkout and may also have executed dependency build/install hooks."
                if run
                else "- Trust boundary: static mode did not execute target-repository code."
            ),
            (
                "- Dynamic verification: attempted; see L2/L3 results below."
                if run
                else "- Dynamic verification: not attempted; L2/L3 remain unverified."
            ),
            "",
            f"Reproduce this {'dynamic gate' if run else 'static report'}:",
            "",
            "```bash",
            *(_rerun_commands(root, report.profile, run, timeout, command, fail_on)),
            "```",
            "",
        ]
    )
    if not run:
        dynamic_fail_on = "error" if fail_on == "none" else fail_on
        lines.extend(
            [
                "Trusted-repository dynamic gate (installs dependencies and runs code):",
                "",
                "```bash",
                *(
                    _rerun_commands(
                        root,
                        report.profile,
                        True,
                        timeout,
                        command,
                        dynamic_fail_on,
                    )
                ),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "| Level | Check | Status | Detail |",
            "| --- | --- | --- | --- |",
        ]
    )
    for step in steps:
        detail = step.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {step.level} | {step.title} | {_ICON.get(step.status, step.status)} | {detail} |"
        )
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
            "> L1 is deterministic. L2/L3 are static here; pass --run to prepare the "
            "dynamic environment and execute the entrypoint (only on repositories you trust)."
        )
        lines.append("")
    return "\n".join(lines)


def _l3_source(steps: list[LadderStep]) -> str:
    for step in steps:
        if step.level == "L3":
            return step.source
    return ""


def _rerun_commands(
    root: Path,
    profile: str,
    run: bool,
    timeout: int,
    command: str | None,
    fail_on: str,
) -> list[str]:
    args = [
        "rrdoctor",
        "verify",
        ".",
        "--profile",
        profile,
        "--timeout",
        str(timeout),
        "--fail-on",
        fail_on,
    ]
    if command is not None:
        args.extend(["--command", command])
    if run:
        args.append("--run")
    return ["cd <repository-root>", shlex.join(args)]


def verification_failed(
    report: ScanReport, steps: list[LadderStep] | None = None, fail_on: str = "error"
) -> bool:
    """Whether verification should fail the CLI gate."""

    if fail_on == "none":
        return False
    if fail_on == "warning" and (
        report.summary.get("error", 0) > 0 or report.summary.get("warning", 0) > 0
    ):
        return True
    if fail_on == "error" and report.summary.get("error", 0) > 0:
        return True
    if steps is None:
        return False
    return any(step.status in {"fail", "blocked"} for step in steps)
