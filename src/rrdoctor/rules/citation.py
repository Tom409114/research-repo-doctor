"""Citation rules."""

from __future__ import annotations

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, read_text
from rrdoctor.rules.paths import has_file
from rrdoctor.rules.readme import readme_path


class CitationMissingRule(Rule):
    definition = definition(
        "RRD020",
        "Citation instructions missing",
        Category.CITATION,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks for CITATION.cff or citation instructions.",
        "Citation metadata helps research software receive credit and be indexed.",
        "Add CITATION.cff or a clear citation section in the README.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        path = readme_path(context)
        readme = read_text(path).lower() if path else ""
        if not has_file(context.root, ["CITATION.cff", "CITATION.md"]) and "citation" not in readme:
            return [
                self.finding(context, message="No CITATION.cff or citation guidance was found.")
            ]
        return []


class PaperMetadataMissingRule(Rule):
    definition = definition(
        "RRD021",
        "Paper metadata not documented",
        Category.CITATION,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks paper-like repositories for DOI, arXiv, or reference metadata.",
        "Paper-linked code should make the associated publication discoverable.",
        "Document DOI, arXiv ID, paper title, or reference metadata in README or CITATION.cff.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        path = readme_path(context)
        text = read_text(path) if path else ""
        lower = text.lower()
        paper_related = any(
            term in lower for term in ("paper", "publication", "preprint", "accepted at")
        )
        has_metadata = any(term in lower for term in ("doi", "arxiv", "bibtex", "citation.cff"))
        if paper_related and not has_metadata:
            return [
                self.finding(
                    context,
                    message=(
                        "Repository appears paper-related but no DOI/arXiv/reference metadata "
                        "was found."
                    ),
                    evidence=[
                        Evidence(
                            "README mentions a paper/publication without DOI, arXiv, or BibTeX.",
                            context.rel(path),
                        )
                    ]
                    if path
                    else [],
                    file=context.rel(path) if path else None,
                )
            ]
        return []


RULES = [CitationMissingRule(), PaperMetadataMissingRule()]
