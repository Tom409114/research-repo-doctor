"""Experiment entrypoint and provenance rules."""

from __future__ import annotations

import re

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
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

    def check(self, context: ScanContext) -> list[Finding]:
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

    def check(self, context: ScanContext) -> list[Finding]:
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

    def check(self, context: ScanContext) -> list[Finding]:
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

    def check(self, context: ScanContext) -> list[Finding]:
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


class CudaAssumptionRule(Rule):
    definition = definition(
        "RRD054",
        "Hardcoded GPU/CUDA assumption without a documented requirement",
        Category.REPRODUCIBILITY,
        Severity.WARNING,
        ("ml",),
        "Checks for code that assumes a CUDA GPU without a fallback or a documented requirement.",
        "A pinned GPU device with no CPU fallback or stated hardware requirement is a "
        "frequent reason reviewers cannot reproduce ML results on their machines.",
        "Guard device selection with torch.cuda.is_available() (or similar) and document the "
        "required GPU/CUDA version in the README.",
    )

    _USES_CUDA = re.compile(
        r"(\.cuda\(|['\"]cuda(:\d+)?['\"]|cuda_visible_devices|\.to\(\s*['\"]cuda)"
    )
    _HAS_FALLBACK = re.compile(
        r"(cuda\.is_available|is_available\(\)|device\s*=.*cpu|torch\.device)"
    )

    def check(self, context: ScanContext) -> list[Finding]:
        uses_cuda = False
        evidence_file = None
        for path in text_files(context):
            if path.suffix.lower() not in {".py", ".ipynb", ".r", ".jl"}:
                continue
            text = read_text(path)
            if self._USES_CUDA.search(text):
                uses_cuda = True
                evidence_file = context.rel(path)
                if self._HAS_FALLBACK.search(text):
                    return []  # A guarded usage somewhere is good enough.
        if not uses_cuda:
            return []

        # Allow an explicit, documented hardware requirement to satisfy the rule.
        readme = context.root / "README.md"
        documented = readme.exists() and re.search(r"(?i)(cuda|gpu|nvidia)", read_text(readme))
        if documented:
            return []

        return [
            self.finding(
                context,
                message="GPU/CUDA usage was detected with no CPU fallback or documented "
                "hardware requirement.",
                evidence=[Evidence("Hardcoded CUDA usage", evidence_file)] if evidence_file else [],
                file=evidence_file,
            )
        ]


RULES = [
    ExperimentEntrypointMissingRule(),
    ConfigFilesMissingRule(),
    RandomnessWithoutSeedRule(),
    ResultsProvenanceMissingRule(),
    CudaAssumptionRule(),
]
