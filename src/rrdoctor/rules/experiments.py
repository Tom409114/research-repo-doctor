"""Experiment entrypoint and provenance rules."""

from __future__ import annotations

import re

from rrdoctor.models import Category, Evidence, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, read_text
from rrdoctor.rules.paths import find_files, text_files


class ExperimentEntrypointMissingRule(Rule):
    definition = definition(
        "RRD050",
        "No experiment entrypoint found",
        Category.EXPERIMENTS,
        Severity.ERROR,
        ("minimal", "standard", "strict", "ml"),
        "Checks for scripts or commands that reproduce experiments.",
        "Reviewers need an obvious entrypoint for rerunning experiments.",
        "Add scripts/reproduce.sh, scripts/run*.sh, a Makefile, or documented train/eval scripts.",
    )

    def check(self, context: ScanContext):
        patterns = [
            "scripts/run*.sh",
            "scripts/reproduce*.sh",
            "scripts/train*.py",
            "src/**/train*.py",
            "Makefile",
            "noxfile.py",
            "tox.ini",
        ]
        if not find_files(context, patterns):
            return [
                self.finding(
                    context, message="No experiment or reproduction entrypoint was detected."
                )
            ]
        return []


class ConfigFilesMissingRule(Rule):
    definition = definition(
        "RRD051",
        "No configuration files found",
        Category.EXPERIMENTS,
        Severity.WARNING,
        ("ml",),
        "Checks ML/research projects for experiment configuration files.",
        "Configurations make experiments easier to compare and rerun.",
        "Add configs/*.yaml, config/*.toml, JSON config files, or document fixed parameters.",
    )

    def check(self, context: ScanContext):
        patterns = [
            "configs/*.yml",
            "configs/*.yaml",
            "config/*.toml",
            "config/*.yaml",
            "*.hydra/**",
            "*.json",
        ]
        if not find_files(context, patterns):
            return [
                self.finding(context, message="No experiment configuration files were detected.")
            ]
        return []


class RandomnessWithoutSeedRule(Rule):
    definition = definition(
        "RRD052",
        "Randomness used without obvious seed setting",
        Category.REPRODUCIBILITY,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks for common randomness APIs without visible seed setting.",
        "Uncontrolled randomness can make reported results hard to reproduce.",
        "Set and document seeds for Python, NumPy, PyTorch, TensorFlow, or other random sources.",
    )

    def check(self, context: ScanContext):
        combined = []
        for path in text_files(context):
            if path.suffix.lower() in {".py", ".ipynb", ".r", ".jl"}:
                combined.append(read_text(path))
        text = "\n".join(combined)
        uses_random = re.search(r"\b(random\.|np\.random|torch\.rand|tensorflow|tf\.random)", text)
        sets_seed = re.search(r"\b(seed|manual_seed|set_seed|random_state)\b", text, re.IGNORECASE)
        if uses_random and not sets_seed:
            return [
                self.finding(
                    context,
                    message="Randomness APIs appear to be used, but seed-setting was not obvious.",
                )
            ]
        return []


class ResultsProvenanceMissingRule(Rule):
    definition = definition(
        "RRD053",
        "Results provenance documentation missing",
        Category.EXPERIMENTS,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks results/ directories for provenance documentation.",
        "Stored results should explain how they were produced.",
        "Add results/README.md with command, commit, data version, and environment details.",
    )

    def check(self, context: ScanContext):
        results = context.root / "results"
        if results.exists() and not (results / "README.md").exists():
            return [
                self.finding(
                    context,
                    message="results/ exists but no results/README.md provenance note was found.",
                    evidence=[Evidence("results/ directory exists without README.", "results")],
                    file="results",
                )
            ]
        return []


RULES = [
    ExperimentEntrypointMissingRule(),
    ConfigFilesMissingRule(),
    RandomnessWithoutSeedRule(),
    ResultsProvenanceMissingRule(),
]
