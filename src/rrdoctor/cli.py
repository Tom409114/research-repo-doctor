"""Typer command-line interface for Research Repo Doctor."""

from __future__ import annotations

import importlib
import json
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from rrdoctor import __version__
from rrdoctor.baseline import diff_against_baseline
from rrdoctor.config import (
    FORMAT_VALUES,
    PROFILES,
    apply_cli_overrides,
    default_config_text,
    load_config,
)
from rrdoctor.fixers import apply_fix, fixable_rule_ids, infer_fix_context
from rrdoctor.models import DiffResult, ScanReport
from rrdoctor.reporting.agent import render_agent_json, render_agent_markdown
from rrdoctor.reporting.appendix import render_appendix, render_checklist
from rrdoctor.reporting.badge import render_badge_endpoint, render_badge_svg
from rrdoctor.reporting.json_report import render_json
from rrdoctor.reporting.markdown import render_markdown
from rrdoctor.reporting.sarif import render_sarif
from rrdoctor.rules.registry import all_rules, get_rule
from rrdoctor.scanner import Scanner
from rrdoctor.verification import build_steps, render_verification, verification_failed

app = typer.Typer(
    help="Audit research repositories for reproducibility readiness.",
    invoke_without_command=True,
)
console = Console()
err_console = Console(stderr=True)
PROFILE_HELP = "Profile: " + ", ".join(PROFILES) + "."


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"rrdoctor {__version__}")
        raise typer.Exit()


def _module_importable(module: str) -> bool:
    """Return true only when a module and its import-time dependencies load."""

    try:
        importlib.import_module(module)
    except Exception:
        return False
    return True


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the installed rrdoctor version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Audit research repositories for reproducibility readiness."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def _parse_rule_ids(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {item.strip().upper() for item in raw.split(",") if item.strip()}


def _render(report: ScanReport, output_format: str) -> str:
    if output_format == "markdown":
        return render_markdown(report)
    if output_format == "json":
        return render_json(report)
    if output_format == "sarif":
        return render_sarif(report)
    if output_format == "agent":
        return render_agent_markdown(report)
    raise typer.BadParameter(f"Unsupported format: {output_format}")


def _print_summary(report: ScanReport) -> None:
    table = Table(title="Research Repo Doctor Summary")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Profile", report.profile)
    table.add_row("Readiness", report.readiness.level)
    table.add_row("Score", f"{report.score}/100")
    table.add_row("Errors", str(report.summary["error"]))
    table.add_row("Warnings", str(report.summary["warning"]))
    table.add_row("Info", str(report.summary["info"]))
    table.add_row("Rules evaluated", str(report.rules_evaluated))
    err_console.print(table)


def _should_fail(report: ScanReport, fail_on: str) -> bool:
    if fail_on == "none":
        return False
    if fail_on == "error":
        return report.summary["error"] > 0
    if fail_on == "warning":
        return report.summary["error"] > 0 or report.summary["warning"] > 0
    return False


def _print_diff(diff: DiffResult) -> None:
    table = Table(title="Baseline comparison")
    table.add_column("Change")
    table.add_column("Count", justify="right")
    table.add_row("New findings", str(len(diff.new)))
    table.add_row("Fixed findings", str(len(diff.fixed)))
    table.add_row("Unchanged findings", str(len(diff.unchanged)))
    base = "n/a" if diff.baseline_score is None else str(diff.baseline_score)
    table.add_row("Score", f"{base} -> {diff.current_score}")
    err_console.print(table)
    for finding in diff.new:
        err_console.print(f"[red]NEW[/red] {finding.rule_id} {finding.title}")


def _diff_should_fail(diff: DiffResult, fail_on_new: str) -> bool:
    if fail_on_new == "none":
        return False
    levels = {finding.severity.value for finding in diff.new}
    if fail_on_new == "error":
        return "error" in levels
    if fail_on_new == "warning":
        return "error" in levels or "warning" in levels
    return False


def _build_report(path: Path, profile: str, config: Path | None = None) -> ScanReport:
    """Load config, apply the profile, and scan a path into a report."""

    loaded = load_config(config)
    effective = apply_cli_overrides(loaded, profile=profile)
    return Scanner(effective).scan(path)


def _write_or_echo(rendered: str, output: Path | None, label: str) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        err_console.print(f"Wrote {label} to [bold]{output}[/bold]")
    else:
        typer.echo(rendered)


@app.command()
def scan(
    path: Annotated[Path, typer.Argument(help="Repository path to scan.")] = Path("."),
    config: Annotated[Path | None, typer.Option("--config", help="Path to .rrdoctor.yml.")] = None,
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            help="Report format: markdown, json, sarif, or agent.",
            rich_help_panel="Report",
        ),
    ] = "markdown",
    output: Annotated[
        Path | None, typer.Option("--output", help="Write report to this path.")
    ] = None,
    fail_on: Annotated[
        str, typer.Option("--fail-on", help="Failure threshold: none, error, warning.")
    ] = "error",
    fail_on_new: Annotated[
        str | None,
        typer.Option(
            "--fail-on-new",
            help="With --baseline, fail only on newly introduced findings (none/error/warning).",
        ),
    ] = None,
    baseline: Annotated[
        Path | None,
        typer.Option(
            "--baseline", help="Compare against a JSON report and show new/fixed findings."
        ),
    ] = None,
    profile: Annotated[str, typer.Option("--profile", help=PROFILE_HELP)] = "standard",
    include: Annotated[
        str | None, typer.Option("--include", help="Comma-separated rule IDs to include.")
    ] = None,
    exclude: Annotated[
        str | None, typer.Option("--exclude", help="Comma-separated rule IDs to exclude.")
    ] = None,
    quiet: Annotated[bool, typer.Option("--quiet", help="Suppress Rich summary table.")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", help="Print scanner details.")] = False,
) -> None:
    """Scan a repository and emit a structured report."""

    if output_format not in FORMAT_VALUES:
        raise typer.BadParameter(f"--format must be one of: {', '.join(FORMAT_VALUES)}")
    if profile not in PROFILES:
        raise typer.BadParameter(f"--profile must be one of: {', '.join(PROFILES)}")
    if fail_on not in ("none", "error", "warning"):
        raise typer.BadParameter("--fail-on must be one of: none, error, warning")
    if fail_on_new is not None and fail_on_new not in ("none", "error", "warning"):
        raise typer.BadParameter("--fail-on-new must be one of: none, error, warning")
    if fail_on_new is not None and baseline is None:
        raise typer.BadParameter("--fail-on-new requires --baseline.")

    loaded = load_config(config)
    effective = apply_cli_overrides(
        loaded,
        profile=profile,
        output_format=output_format,
        output=str(output) if output else None,
        fail_on=fail_on,
    )
    scanner = Scanner(effective, include=_parse_rule_ids(include), exclude=_parse_rule_ids(exclude))
    report = scanner.scan(path)
    rendered = _render(report, output_format)

    if not quiet:
        _print_summary(report)
    if verbose:
        console.print(f"Scanned repository: {report.repository_path}")

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        if not quiet:
            err_console.print(f"Wrote {output_format} report to [bold]{output}[/bold]")
    else:
        typer.echo(rendered)

    diff: DiffResult | None = None
    if baseline is not None:
        if not baseline.exists():
            err_console.print(f"[red]Baseline not found:[/red] {baseline}")
            raise typer.Exit(2)
        diff = diff_against_baseline(report, baseline)
        if not quiet:
            _print_diff(diff)

    if diff is not None and fail_on_new is not None:
        if _diff_should_fail(diff, fail_on_new):
            raise typer.Exit(1)
        return

    if _should_fail(report, fail_on):
        raise typer.Exit(1)


@app.command()
def fix(
    path: Annotated[Path, typer.Argument(help="Repository path to fix.")] = Path("."),
    config: Annotated[Path | None, typer.Option("--config", help="Path to .rrdoctor.yml.")] = None,
    profile: Annotated[str, typer.Option("--profile", help=PROFILE_HELP)] = "standard",
    write: Annotated[
        bool, typer.Option("--write", help="Apply fixes (default is a dry-run preview).")
    ] = False,
    only: Annotated[
        str | None, typer.Option("--only", help="Comma-separated rule IDs to fix.")
    ] = None,
    project_name: Annotated[
        str | None, typer.Option("--project-name", help="Project name for scaffolded files.")
    ] = None,
    author: Annotated[
        str | None,
        typer.Option(
            "--author",
            help="Author/copyright holder for scaffolded files. Defaults to project metadata.",
        ),
    ] = None,
) -> None:
    """Apply deterministic, idempotent auto-fixes for common reproducibility gaps.

    Only safe scaffolding is created (governance docs, citation metadata, data and
    results provenance notes, changelog, and ignore entries). Existing files are
    never overwritten. Run without --write to preview, then re-run with --write.
    """

    if profile not in PROFILES:
        raise typer.BadParameter(f"--profile must be one of: {', '.join(PROFILES)}")

    loaded = load_config(config)
    effective = apply_cli_overrides(loaded, profile=profile)
    scanner = Scanner(effective)
    report = scanner.scan(path)
    root = Path(path).resolve()

    fixable = fixable_rule_ids()
    only_ids = _parse_rule_ids(only)
    target_ids: list[str] = []
    for finding in report.findings:
        rid = finding.rule_id
        if rid in fixable and rid not in target_ids and (not only_ids or rid in only_ids):
            target_ids.append(rid)

    if not target_ids:
        console.print("No auto-fixable findings. Run `rrdoctor plan` for the remaining work.")
        return

    ctx = infer_fix_context(
        root,
        project_name=project_name,
        author=author,
        year=datetime.now(timezone.utc).year,
    )

    table = Table(title="rrdoctor fix" + ("" if write else " (dry-run)"))
    table.add_column("Rule")
    table.add_column("Action")
    table.add_column("Detail")
    applied = 0
    for rid in target_ids:
        if write:
            result = apply_fix(rid, ctx)
            if result is None:
                continue
            if result.action in ("created", "updated"):
                applied += 1
            table.add_row(result.rule_id, result.action, result.detail)
        else:
            rule = get_rule(rid)
            detail = rule.definition.remediation if rule else ""
            table.add_row(rid, "would fix", detail)
    console.print(table)
    if write:
        err_console.print(
            f"Applied {applied} fix(es). Re-run `rrdoctor scan` to verify, then review the diff."
        )
    else:
        err_console.print("Dry-run only. Re-run with --write to apply these fixes.")


@app.command()
def plan(
    path: Annotated[Path, typer.Argument(help="Repository path to plan.")] = Path("."),
    config: Annotated[Path | None, typer.Option("--config", help="Path to .rrdoctor.yml.")] = None,
    profile: Annotated[str, typer.Option("--profile", help=PROFILE_HELP)] = "standard",
    output_format: Annotated[
        str, typer.Option("--format", help="Plan format: markdown or json.")
    ] = "markdown",
    output: Annotated[
        Path | None, typer.Option("--output", help="Write the plan to this path.")
    ] = None,
) -> None:
    """Emit a tool-agnostic fix plan for any coding agent or human to execute."""

    if profile not in PROFILES:
        raise typer.BadParameter(f"--profile must be one of: {', '.join(PROFILES)}")
    if output_format not in ("markdown", "json"):
        raise typer.BadParameter("--format must be one of: markdown, json")

    loaded = load_config(config)
    effective = apply_cli_overrides(loaded, profile=profile)
    report = Scanner(effective).scan(path)
    rendered = (
        render_agent_json(report) if output_format == "json" else render_agent_markdown(report)
    )

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        err_console.print(f"Wrote plan to [bold]{output}[/bold]")
    else:
        typer.echo(rendered)


@app.command()
def badge(
    path: Annotated[Path, typer.Argument(help="Repository path to summarize.")] = Path("."),
    config: Annotated[Path | None, typer.Option("--config", help="Path to .rrdoctor.yml.")] = None,
    profile: Annotated[str, typer.Option("--profile", help=PROFILE_HELP)] = "standard",
    output_format: Annotated[
        str, typer.Option("--format", help="Badge format: endpoint (Shields.io JSON) or svg.")
    ] = "endpoint",
    output: Annotated[
        Path | None, typer.Option("--output", help="Write the badge to this path.")
    ] = None,
) -> None:
    """Emit an artifact-readiness badge (Shields.io endpoint JSON or SVG)."""

    if profile not in PROFILES:
        raise typer.BadParameter(f"--profile must be one of: {', '.join(PROFILES)}")
    if output_format not in ("endpoint", "svg"):
        raise typer.BadParameter("--format must be one of: endpoint, svg")

    loaded = load_config(config)
    effective = apply_cli_overrides(loaded, profile=profile)
    report = Scanner(effective).scan(path)
    rendered = render_badge_svg(report) if output_format == "svg" else render_badge_endpoint(report)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        err_console.print(f"Wrote badge to [bold]{output}[/bold]")
    else:
        typer.echo(rendered)


@app.command()
def init(
    profile: Annotated[
        str, typer.Option("--profile", help=PROFILE_HELP + " Used for the generated config.")
    ] = "standard",
    output: Annotated[Path, typer.Option("--output", help="Config file path.")] = Path(
        ".rrdoctor.yml"
    ),
    force: Annotated[
        bool, typer.Option("--force", help="Overwrite an existing config file.")
    ] = False,
) -> None:
    """Create a documented .rrdoctor.yml file."""

    if profile not in PROFILES:
        raise typer.BadParameter(f"--profile must be one of: {', '.join(PROFILES)}")
    if output.exists() and not force:
        err_console.print(f"[red]Refusing to overwrite existing config:[/red] {output}")
        raise typer.Exit(1)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(default_config_text(profile), encoding="utf-8")
    console.print(f"Created {output}")


@app.command()
def verify(
    path: Annotated[Path, typer.Argument(help="Repository path to verify.")] = Path("."),
    config: Annotated[Path | None, typer.Option("--config", help="Path to .rrdoctor.yml.")] = None,
    profile: Annotated[
        str, typer.Option("--profile", help=PROFILE_HELP + " Default: standard.")
    ] = "standard",
    run: Annotated[
        bool,
        typer.Option(
            "--run",
            help="Actually resolve deps (L2) and execute the entrypoint (L3). Runs repo code.",
        ),
    ] = False,
    timeout: Annotated[
        int, typer.Option("--timeout", help="Per-step timeout in seconds for --run.")
    ] = 300,
    output: Annotated[
        Path | None, typer.Option("--output", help="Write the report to this path.")
    ] = None,
    command: Annotated[
        str | None,
        typer.Option(
            "--command",
            help="Override the detected L3 entrypoint command. Only executes with --run.",
        ),
    ] = None,
    fail_on: Annotated[
        str, typer.Option("--fail-on", help="Failure threshold: none, error.")
    ] = "error",
) -> None:
    """Run the reproducibility verification ladder (L1 static, L2 build, L3 run).

    L1 is deterministic. With --run, L2 resolves dependencies and L3 executes a
    declared entrypoint under a timeout (only use --run on repositories you trust).
    """

    if profile not in PROFILES:
        raise typer.BadParameter(f"--profile must be one of: {', '.join(PROFILES)}")
    if fail_on not in ("none", "error"):
        raise typer.BadParameter("--fail-on must be one of: none, error")
    if command is not None:
        if not command.strip():
            raise typer.BadParameter("--command cannot be empty")
        try:
            shlex.split(command)
        except ValueError as exc:
            raise typer.BadParameter(f"--command could not be parsed: {exc}") from exc

    report = _build_report(path, profile, config)
    root = Path(path).resolve()
    steps = build_steps(report, root, run, timeout, command)
    rendered = render_verification(report, root, run, timeout, steps=steps, command=command)
    _write_or_echo(rendered, output, "verification report")

    if fail_on == "error" and verification_failed(report, steps if run else None):
        raise typer.Exit(1)


@app.command()
def appendix(
    path: Annotated[Path, typer.Argument(help="Repository path to scan.")] = Path("."),
    config: Annotated[Path | None, typer.Option("--config", help="Path to .rrdoctor.yml.")] = None,
    profile: Annotated[
        str, typer.Option("--profile", help=PROFILE_HELP + " Default: acm.")
    ] = "acm",
    section: Annotated[
        str,
        typer.Option("--section", help="Which artifact to emit: appendix, checklist, or both."),
    ] = "both",
    output: Annotated[
        Path | None, typer.Option("--output", help="Write output to this path.")
    ] = None,
) -> None:
    """Generate an ACM-style Artifact Appendix and submission checklist mapping.

    Maps findings to ACM Artifact Evaluation badges and the NeurIPS reproducibility
    checklist so you can fill the artifact paperwork before a deadline.
    """

    if profile not in PROFILES:
        raise typer.BadParameter(f"--profile must be one of: {', '.join(PROFILES)}")
    if section not in ("appendix", "checklist", "both"):
        raise typer.BadParameter("--section must be one of: appendix, checklist, both")

    report = _build_report(path, profile, config)

    parts: list[str] = []
    if section in ("appendix", "both"):
        parts.append(render_appendix(report))
    if section in ("checklist", "both"):
        parts.append(render_checklist(report))
    rendered = "\n\n".join(parts)

    _write_or_echo(rendered, output, "artifact appendix")


@app.command()
def mcp() -> None:
    r"""Start the MCP server so coding agents can call scan/verify/appendix as tools.

    Requires the optional dependency: pip install "rrdoctor\[mcp]".
    """

    from rrdoctor.mcp_server import run as run_server

    run_server()


@app.command("list-rules")
def list_rules() -> None:
    """List registered rules."""

    table = Table(title="Research Repo Doctor Rules")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Severity")
    table.add_column("Profiles")
    for rule in all_rules():
        table.add_row(
            rule.definition.id,
            rule.definition.name,
            rule.definition.category.value,
            rule.definition.severity.value,
            ", ".join(rule.definition.profiles),
        )
    console.print(table)


@app.command()
def explain(rule_id: Annotated[str, typer.Argument(help="Rule ID, for example RRD001.")]) -> None:
    """Explain a rule and how to remediate it."""

    rule = get_rule(rule_id)
    if rule is None:
        console.print(f"[red]Unknown rule:[/red] {rule_id}")
        raise typer.Exit(1)
    definition = rule.definition
    console.print(f"[bold]{definition.id}: {definition.name}[/bold]")
    console.print(f"Category: {definition.category.value}")
    console.print(f"Severity: {definition.severity.value}")
    console.print(f"Profiles: {', '.join(definition.profiles)}")
    console.print("")
    console.print(definition.description)
    console.print("")
    console.print(f"[bold]Why it matters[/bold]\n{definition.rationale}")
    console.print("")
    console.print(f"[bold]Remediation[/bold]\n{definition.remediation}")
    if definition.examples:
        console.print("")
        console.print("[bold]Examples[/bold]")
        for example in definition.examples:
            console.print(f"- {example}")


@app.command()
def doctor() -> None:
    """Run rrdoctor self-diagnostics."""

    payload = {
        "rrdoctor_version": __version__,
        "python": sys.version.split()[0],
        "cwd": str(Path.cwd()),
        "cwd_readable": Path.cwd().exists(),
        "optional_dependencies": {
            "nbformat": _module_importable("nbformat"),
            "yaml": _module_importable("yaml"),
            "rich": _module_importable("rich"),
            "mcp": _module_importable("mcp.server.fastmcp"),
        },
    }
    console.print_json(json.dumps(payload))
