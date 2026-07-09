"""License rule."""

from __future__ import annotations

from rrdoctor.models import Category, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition
from rrdoctor.rules.paths import has_file

LICENSE_FILENAMES = [
    "LICENSE",
    "LICENSE.md",
    "LICENSE.rst",
    "LICENSE.txt",
    "LICENCE",
    "LICENCE.md",
    "LICENCE.rst",
    "LICENCE.txt",
    "COPYING",
    "COPYING.md",
    "COPYING.rst",
    "COPYING.txt",
]


class LicenseMissingRule(Rule):
    definition = definition(
        "RRD010",
        "LICENSE missing",
        Category.GOVERNANCE,
        Severity.ERROR,
        ("minimal", "standard", "strict", "ml"),
        "Checks for a repository license.",
        "Without a license, reuse rights are ambiguous.",
        "Add an OSI-approved license such as MIT, BSD-3-Clause, or Apache-2.0.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not has_file(context.root, LICENSE_FILENAMES):
            return [self.finding(context, message="No LICENSE file was found.")]
        return []


RULES = [LicenseMissingRule()]
