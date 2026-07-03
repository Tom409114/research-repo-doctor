"""Scan a public research-repository corpus with rrdoctor.

The runner shallow-clones public repositories, runs rrdoctor's static scanner,
and writes aggregate JSON/Markdown summaries for maintainer review. It never
installs dependencies or executes code from target repositories.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from rrdoctor.config import DEFAULT_CONFIG, apply_cli_overrides
from rrdoctor.models import Finding, ScanReport, to_jsonable
from rrdoctor.scanner import Scanner

DEFAULT_MANIFEST = Path("evaluation/corpus.yml")
DEFAULT_OUTPUT = Path("evaluation/reports/corpus-scan.json")
DEFAULT_MARKDOWN = Path("evaluation/reports/corpus-summary.md")
DEFAULT_TIMEOUT_SECONDS = 90
DEFAULT_MAX_BYTES = 300 * 1024 * 1024


@dataclass(frozen=True)
class CorpusEntry:
    """One public repository in the evaluation corpus."""

    name: str
    url: str
    ecosystem: str
    reason: str
    expected_absent: tuple[str, ...]
    review_focus: tuple[str, ...]


def load_corpus(path: Path) -> list[CorpusEntry]:
    """Load the corpus manifest."""

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a mapping.")
    raw_entries = payload.get("repositories", [])
    if not isinstance(raw_entries, list):
        raise ValueError("`repositories` must be a list.")

    entries: list[CorpusEntry] = []
    for item in raw_entries:
        if not isinstance(item, dict):
            raise ValueError("Each repository entry must be a mapping.")
        entries.append(
            CorpusEntry(
                name=str(item["name"]),
                url=str(item["url"]),
                ecosystem=str(item.get("ecosystem", "unknown")),
                reason=str(item.get("reason", "")),
                expected_absent=tuple(
                    str(rule).upper() for rule in item.get("expected_absent", [])
                ),
                review_focus=tuple(str(focus) for focus in item.get("review_focus", [])),
            )
        )
    return entries


def _directory_size_bytes(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            total += path.stat().st_size
        except OSError:
            continue
    return total


def clone_repo(entry: CorpusEntry, root: Path, timeout: int, max_bytes: int) -> Path:
    """Shallow-clone a public repository for static scanning."""

    destination = root / entry.name
    if destination.exists():
        shutil.rmtree(destination)
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_LFS_SKIP_SMUDGE": "1"}
    command = [
        "git",
        "clone",
        "--depth",
        "1",
        "--single-branch",
        entry.url,
        str(destination),
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        env=env,
        text=True,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(detail[:500] or "git clone failed")

    size = _directory_size_bytes(destination)
    if size > max_bytes:
        shutil.rmtree(destination, ignore_errors=True)
        limit_mb = max_bytes // (1024 * 1024)
        raise RuntimeError(f"clone exceeds {limit_mb} MB size limit")
    return destination


def summarize_report(entry: CorpusEntry, report: ScanReport) -> dict[str, Any]:
    """Return a compact review summary for one scan."""

    expected_absent_violations = [
        finding.rule_id for finding in report.findings if finding.rule_id in entry.expected_absent
    ]
    return {
        "name": entry.name,
        "url": entry.url,
        "ecosystem": entry.ecosystem,
        "reason": entry.reason,
        "review_focus": list(entry.review_focus),
        "status": "scanned",
        "readiness": to_jsonable(report.readiness),
        "score": report.score,
        "summary": report.summary,
        "rules_evaluated": report.rules_evaluated,
        "expected_absent": list(entry.expected_absent),
        "expected_absent_violations": expected_absent_violations,
        "top_findings": [_finding_summary(finding) for finding in report.findings[:12]],
    }


def _finding_summary(finding: Finding) -> dict[str, Any]:
    return {
        "rule_id": finding.rule_id,
        "severity": finding.severity.value,
        "title": finding.title,
        "file": finding.file,
        "message": finding.message,
    }


def error_summary(entry: CorpusEntry, message: str) -> dict[str, Any]:
    """Return a compact failure summary for one repository."""

    return {
        "name": entry.name,
        "url": entry.url,
        "ecosystem": entry.ecosystem,
        "reason": entry.reason,
        "review_focus": list(entry.review_focus),
        "status": "error",
        "error": message,
        "expected_absent": list(entry.expected_absent),
    }


def scan_entries(
    entries: list[CorpusEntry],
    *,
    profile: str,
    timeout: int,
    max_bytes: int,
    cache_dir: Path | None,
) -> list[dict[str, Any]]:
    """Clone and scan corpus entries."""

    config = apply_cli_overrides(DEFAULT_CONFIG, profile=profile)
    scanner = Scanner(config)
    summaries: list[dict[str, Any]] = []

    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        work_root = cache_dir
        cleanup = False
    else:
        tempdir = tempfile.TemporaryDirectory(prefix="rrdoctor-corpus-")
        work_root = Path(tempdir.name)
        cleanup = True

    try:
        for entry in entries:
            try:
                repo_path = clone_repo(entry, work_root, timeout, max_bytes)
                summaries.append(summarize_report(entry, scanner.scan(repo_path)))
            except Exception as exc:
                summaries.append(error_summary(entry, str(exc)))
    finally:
        if cleanup:
            tempdir.cleanup()

    return summaries


def render_markdown(summaries: list[dict[str, Any]]) -> str:
    """Render a compact Markdown summary."""

    lines = [
        "# rrdoctor Corpus Scan Summary",
        "",
        "| Repository | Status | Readiness | Score | Errors | Warnings | "
        "Expected-absent violations |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for item in summaries:
        if item.get("status") != "scanned":
            lines.append(
                f"| [{item['name']}]({item['url']}) | error | - | - | - | - | "
                f"{item.get('error', '')} |"
            )
            continue
        readiness = item.get("readiness", {})
        level = readiness.get("level", "-") if isinstance(readiness, dict) else "-"
        summary = item.get("summary", {})
        errors = summary.get("error", 0) if isinstance(summary, dict) else 0
        warnings = summary.get("warning", 0) if isinstance(summary, dict) else 0
        violations = ", ".join(item.get("expected_absent_violations", [])) or "-"
        lines.append(
            f"| [{item['name']}]({item['url']}) | scanned | {level} | {item.get('score', '-')} | "
            f"{errors} | {warnings} | {violations} |"
        )
    lines.append("")
    lines.append(
        "Review this table manually before using the data in public posts. Expected-absent "
        "violations are regression candidates, not automatic bugs."
    )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--profile", default="standard")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--only", action="append", default=[], help="Entry name to scan.")
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-mb", type=int, default=DEFAULT_MAX_BYTES // (1024 * 1024))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    entries = load_corpus(args.manifest)
    if args.only:
        wanted = set(args.only)
        entries = [entry for entry in entries if entry.name in wanted]
    if args.limit is not None:
        entries = entries[: args.limit]

    max_bytes = args.max_mb * 1024 * 1024
    summaries = scan_entries(
        entries,
        profile=args.profile,
        timeout=args.timeout,
        max_bytes=max_bytes,
        cache_dir=args.cache_dir,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summaries, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(summaries), encoding="utf-8")
    print(f"Wrote {args.output} and {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
