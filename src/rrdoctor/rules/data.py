"""Data documentation and hygiene rules."""

from __future__ import annotations

import re

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, has_any_heading, mask_secret, read_text
from rrdoctor.rules.paths import first_absolute_path, text_files

DATA_README_TERMS = ("data availability", "data", "dataset", "datasets")
DATA_ACCESS_RE = re.compile(
    r"(?i)\b(download|prepare|preprocess|dataset|datasets|data/|wget|curl|kaggle|zenodo|doi)\b"
)
DATA_PREP_COMMAND_RE = re.compile(r"(?i)\b(python|Rscript|julia|bash)\s+[^\n`]*data/[^\n`]*prepare")


class DataDocsMissingRule(Rule):
    definition = definition(
        "RRD040",
        "Data availability documentation missing",
        Category.DATA,
        Severity.ERROR,
        ("minimal", "standard", "strict", "ml"),
        "Checks for data availability documentation.",
        "Research code should explain where data comes from and how it can be accessed.",
        "Add DATA.md, docs/data.md, data/README.md, or a README data availability section.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        candidates = [
            context.root / "DATA.md",
            context.root / "docs" / "data.md",
            context.root / "data" / "README.md",
        ]
        readme = context.root / "README.md"
        has_readme_data = readme.exists() and _readme_documents_data(read_text(readme))
        if not any(path.exists() for path in candidates) and not has_readme_data:
            return [self.finding(context, message="No data availability documentation was found.")]
        return []


def _readme_documents_data(text: str) -> bool:
    lowered = text.lower()
    if "data availability" in lowered:
        return True
    if has_any_heading(text, DATA_README_TERMS) and DATA_ACCESS_RE.search(text):
        return True
    return bool(DATA_PREP_COMMAND_RE.search(text)) and bool(DATA_ACCESS_RE.search(text))


class DataDirReadmeMissingRule(Rule):
    definition = definition(
        "RRD041",
        "data directory lacks README",
        Category.DATA,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks data/ directories for local documentation.",
        "Data folders need provenance, access, and preprocessing notes.",
        "Add data/README.md describing expected contents and access instructions.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        data_dir = context.root / "data"
        if data_dir.exists() and not (data_dir / "README.md").exists():
            return [
                self.finding(
                    context, message="data/ exists but data/README.md is missing.", file="data"
                )
            ]
        return []


class LargeDataFileRule(Rule):
    definition = definition(
        "RRD042",
        "Large data files detected",
        Category.DATA,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks for large files that may be committed data artifacts.",
        "Large raw artifacts make repositories harder to clone and review.",
        "Move large data to documented external storage or Git LFS, and document retrieval.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        threshold_mb = float(context.config.get("thresholds", {}).get("large_file_mb", 50))
        threshold = threshold_mb * 1024 * 1024
        findings = []
        for path in context.files:
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size > threshold:
                rel = context.rel(path)
                findings.append(
                    self.finding(
                        context,
                        message=f"Large file exceeds configured threshold of {threshold_mb:g} MB.",
                        evidence=[Evidence(f"{rel} is {size / 1024 / 1024:.1f} MB.", rel)],
                        file=rel,
                    )
                )
        return findings


class LocalAbsoluteDataPathRule(Rule):
    definition = definition(
        "RRD043",
        "Potential local absolute data path detected",
        Category.DATA,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks scripts and notebooks for machine-specific absolute paths.",
        "Absolute paths leak local assumptions and often break reproducibility.",
        "Replace local absolute paths with relative paths, configs, or environment variables.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        for path in text_files(context):
            text = read_text(path)
            result = first_absolute_path(text)
            if result:
                value, line = result
                rel = context.rel(path)
                return [
                    self.finding(
                        context,
                        message="A local absolute path appears in repository text.",
                        evidence=[
                            Evidence("Potential absolute path", rel, line, mask_secret(value))
                        ],
                        file=rel,
                        line=line,
                    )
                ]
        return []


RULES = [
    DataDocsMissingRule(),
    DataDirReadmeMissingRule(),
    LargeDataFileRule(),
    LocalAbsoluteDataPathRule(),
]
