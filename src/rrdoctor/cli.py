"""Typer command-line interface for Research Repo Doctor."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from rrdoctor import __version__
from rrdoctor.config import (
    FORMAT_VALUES,
    PROFILES,
    apply_cli_overrides,
    default_config_text,
    load_config,
)
from rrdoctor.models import ScanReport
from rrdoctor.reporting.json_report import render_json
from rrdoctor.reporting.markdown import render_markdown
from rrdoctor.reporting.sarif import render_sarif
from rrdoctor.rules.registry import all_rules, get_rule
from rrdoctor.scanner import Scanner

app = typer.Typer(
    help="Audit research repositories for reproducibility readiness.", no_args_is_help=True
)
console = Console()
err_console = Console(stderr=True)


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
    raise typer.BadParameter(f"Unsupported format: {output_format}")


def _print_summary(report: ScanReport) -> None:
    table = Table(title="Research Repo Doctor Summary")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Profile", report.profile)
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


@app.command()
def scan(
    path: Annotated[Path, typer.Argument(help="Repository path to scan.")] = Path("."),
    config: Annotated[Path | None, typer.Option("--config", help="Path to .rrdoctor.yml.")] = None,
    output_format: Annotated[
        str,
        typer.Option(
            "--format", help="Report format: markdown, json, or sarif.", rich_help_panel="Report"
        ),
    ] = "markdown",
    output: Annotated[
        Path | None, typer.Option("--output", help="Write report to this path.")
    ] = None,
    fail_on: Annotated[
        str, typer.Option("--fail-on", help="Failure threshold: none, error, warning.")
    ] = "error",
    profile: Annotated[
        str, typer.Option("--profile", help="Profile: minimal, standard, strict, ml.")
    ] = "standard",
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

    if _should_fail(report, fail_on):
        raise typer.Exit(1)


@app.command()
def init(
    profile: Annotated[
        str, typer.Option("--profile", help="Profile for the generated config.")
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
            "nbformat": importlib.util.find_spec("nbformat") is not None,
            "yaml": importlib.util.find_spec("yaml") is not None,
            "rich": importlib.util.find_spec("rich") is not None,
        },
    }
    console.print_json(json.dumps(payload))
