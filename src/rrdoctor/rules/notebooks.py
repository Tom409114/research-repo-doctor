"""Notebook hygiene rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import nbformat

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, mask_secret
from rrdoctor.rules.paths import ABSOLUTE_PATH_RE, find_files


def notebooks(context: ScanContext) -> list[Path]:
    """Return notebook files from the scan context."""

    return [path for path in context.files if path.suffix.lower() == ".ipynb"]


def read_notebook(path: Path) -> Any | None:
    """Best-effort notebook read."""

    try:
        return nbformat.read(path, as_version=4)  # type: ignore[no-untyped-call]
    except (OSError, nbformat.reader.NotJSONError, json.JSONDecodeError, ValueError):
        return None


class NotebookLargeOutputsRule(Rule):
    definition = definition(
        "RRD060",
        "Notebook files detected with large outputs",
        Category.NOTEBOOKS,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks notebook output payload size.",
        "Large outputs make diffs noisy and can hide stale results.",
        "Clear outputs before committing or keep a documented rendered artifact separately.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        threshold_kb = float(
            context.config.get("thresholds", {}).get("large_notebook_output_kb", 1024)
        )
        findings = []
        for path in notebooks(context):
            nb = read_notebook(path)
            if nb is None:
                continue
            output_size = 0
            for cell in nb.cells:
                for output in cell.get("outputs", []):
                    output_size += len(json.dumps(output, default=str))
            if output_size > threshold_kb * 1024:
                rel = context.rel(path)
                findings.append(
                    self.finding(
                        context,
                        message=f"Notebook output payload exceeds {threshold_kb:g} KB.",
                        evidence=[Evidence(f"Output payload is {output_size / 1024:.1f} KB.", rel)],
                        file=rel,
                    )
                )
        return findings


class NotebookExecutionOrderRule(Rule):
    definition = definition(
        "RRD061",
        "Notebook execution counts appear out of order",
        Category.NOTEBOOKS,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks execution counts for non-monotonic order.",
        "Out-of-order notebooks can indicate hidden state or unreproducible execution.",
        "Restart the kernel and execute notebooks top-to-bottom before committing.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        for path in notebooks(context):
            nb = read_notebook(path)
            if nb is None:
                continue
            counts = [
                cell.get("execution_count")
                for cell in nb.cells
                if cell.cell_type == "code" and cell.get("execution_count")
            ]
            if counts and counts != sorted(counts):
                rel = context.rel(path)
                return [
                    self.finding(
                        context,
                        message="Notebook execution counts are not monotonic.",
                        evidence=[Evidence(f"Execution counts: {counts}", rel)],
                        file=rel,
                    )
                ]
        return []


class NotebookAbsolutePathRule(Rule):
    definition = definition(
        "RRD062",
        "Notebook contains absolute local paths",
        Category.NOTEBOOKS,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks notebook cells for local absolute paths.",
        "Machine-specific notebook paths break on reviewers' computers.",
        "Use relative paths, configs, or environment variables for data locations.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        for path in notebooks(context):
            nb = read_notebook(path)
            if nb is None:
                continue
            for index, cell in enumerate(nb.cells, start=1):
                source = str(cell.get("source", ""))
                match = ABSOLUTE_PATH_RE.search(source)
                if match:
                    rel = context.rel(path)
                    return [
                        self.finding(
                            context,
                            message="Notebook contains a local absolute path.",
                            evidence=[
                                Evidence(
                                    "Potential absolute path in notebook cell.",
                                    rel,
                                    index,
                                    mask_secret(match.group(0)),
                                )
                            ],
                            file=rel,
                            line=index,
                        )
                    ]
        return []


class NotebookSecretOutputRule(Rule):
    definition = definition(
        "RRD063",
        "Notebook contains possible secret-like output",
        Category.SECURITY,
        Severity.ERROR,
        ("standard", "strict", "ml"),
        "Checks notebook outputs for conservative secret-like patterns.",
        "Notebook outputs can accidentally publish tokens or credentials.",
        "Clear notebook outputs, rotate exposed credentials, and add secret scanning to CI.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        for path in notebooks(context):
            nb = read_notebook(path)
            if nb is None:
                continue
            for cell_index, cell in enumerate(nb.cells, start=1):
                for output in cell.get("outputs", []):
                    text = json.dumps(output, default=str)
                    masked = mask_secret(text)
                    if masked != text:
                        rel = context.rel(path)
                        return [
                            self.finding(
                                context,
                                message="Notebook output contains a possible secret-like string.",
                                evidence=[
                                    Evidence("Secret-like output masked.", rel, cell_index, masked)
                                ],
                                file=rel,
                                line=cell_index,
                            )
                        ]
        return []


class NotebookPairedScriptRule(Rule):
    definition = definition(
        "RRD064",
        "Notebook has no paired script or execution instructions",
        Category.NOTEBOOKS,
        Severity.INFO,
        ("strict",),
        "Checks strict-profile notebooks for paired scripts or instructions.",
        "Paired scripts or explicit run instructions make notebook workflows reviewable.",
        "Add a paired script, jupytext file, or README instructions for notebook execution order.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not notebooks(context):
            return []
        if find_files(context, ["*.py", "scripts/*.py", "notebooks/*.py"]):
            return []
        readme = context.root / "README.md"
        if (
            readme.exists()
            and "notebook" in readme.read_text(encoding="utf-8", errors="replace").lower()
        ):
            return []
        return [
            self.finding(
                context,
                message="Notebook files exist without paired scripts or execution instructions.",
            )
        ]


RULES = [
    NotebookLargeOutputsRule(),
    NotebookExecutionOrderRule(),
    NotebookAbsolutePathRule(),
    NotebookSecretOutputRule(),
    NotebookPairedScriptRule(),
]
