"""Community governance rules."""

from __future__ import annotations

from rrdoctor.models import Category, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition
from rrdoctor.rules.paths import has_file


class ContributingMissingRule(Rule):
    definition = definition(
        "RRD011",
        "CONTRIBUTING guide missing",
        Category.GOVERNANCE,
        Severity.WARNING,
        ("strict",),
        "Checks for a contribution guide.",
        "Contribution docs reduce maintainer load and clarify expectations.",
        "Add CONTRIBUTING.md with setup, tests, rule contribution guidance, and review norms.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not has_file(context.root, ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"]):
            return [self.finding(context, message="No CONTRIBUTING guide was found.")]
        return []


class SecurityPolicyMissingRule(Rule):
    definition = definition(
        "RRD012",
        "SECURITY policy missing",
        Category.GOVERNANCE,
        Severity.WARNING,
        ("strict",),
        "Checks for a security policy.",
        "Research code can accidentally expose credentials or sensitive paths.",
        "Add SECURITY.md with vulnerability reporting guidance.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not has_file(context.root, ["SECURITY.md", ".github/SECURITY.md"]):
            return [self.finding(context, message="No SECURITY policy was found.")]
        return []


class CodeOfConductMissingRule(Rule):
    definition = definition(
        "RRD013",
        "CODE_OF_CONDUCT missing",
        Category.GOVERNANCE,
        Severity.INFO,
        ("strict",),
        "Checks for a code of conduct.",
        "A code of conduct helps make research software collaboration safer and clearer.",
        "Add CODE_OF_CONDUCT.md or link to a lab/community policy.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not has_file(context.root, ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"]):
            return [self.finding(context, message="No CODE_OF_CONDUCT file was found.")]
        return []


RULES = [ContributingMissingRule(), SecurityPolicyMissingRule(), CodeOfConductMissingRule()]
