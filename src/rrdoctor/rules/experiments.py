"""Experiment entrypoint and provenance rules."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, read_text
from rrdoctor.rules.notebooks import read_notebook
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
        "Add scripts/reproduce.sh, scripts/run*.sh, a Makefile, or documented "
        "CLI/train/eval scripts.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        patterns = [
            "train*.py",
            "eval*.py",
            "evaluate*.py",
            "run*.py",
            "main.py",
            "main_*.py",
            "main-*.py",
            "reproduce*.py",
            "run*.sh",
            "reproduce*.sh",
            "scripts/run*.sh",
            "scripts/reproduce*.sh",
            "scripts/train*.py",
            "scripts/eval*.py",
            "scripts/evaluate*.py",
            "scripts/run*.py",
            "tools/train*.py",
            "tools/eval*.py",
            "tools/evaluate*.py",
            "tools/test*.py",
            "tools/run*.py",
            "src/**/train*.py",
            "src/**/eval*.py",
            "src/**/evaluate*.py",
            "src/**/run*.py",
            "Makefile",
            "noxfile.py",
            "tox.ini",
            "Snakefile",
            "workflow/Snakefile",
            "workflows/Snakefile",
            "*.nf",
            "workflow/*.nf",
            "workflows/*.nf",
            "nextflow.config",
        ]
        if not find_files(context, patterns) and not _has_documented_entrypoint(context):
            return [
                self.finding(
                    context, message="No experiment or reproduction entrypoint was detected."
                )
            ]
        return []


_DOCUMENTED_ENTRYPOINT_RE = re.compile(
    r"(?ix)"
    r"\b("
    r"python\s+-m\s+[A-Za-z0-9_.-]*(?:train|main|run|eval|evaluate|reproduce)[A-Za-z0-9_.-]*\b|"
    r"python(?:\s+-m)?\s+(?:\./)?(?:train|main|run|eval|evaluate|reproduce)(?:\.py)?\b|"
    r"python\s+(?:\./)?(?:train|main|run|eval|evaluate|reproduce)[_-][^\s`]+\.py\b|"
    r"python\s+(?:\./)?(?:scripts|tools)/[^\s`]+\.py\b|"
    r"python\s+(?:\./)?src/[^\s`]*(?:train|test|eval|evaluate|run|reproduce)[^\s`]*\.py\b|"
    r"bash\s+(?:\./)?(?:scripts/)?(?:run|reproduce|train|eval)[^\s`]*\.sh\b|"
    r"make\s+(?:all|run|train|eval|evaluate|reproduce|results)\b|"
    r"snakemake\b|"
    r"nextflow\s+run\b|"
    r"Rscript\s+[^\s`]+|"
    r"julia\s+[^\s`]+"
    r")"
)


def _has_documented_entrypoint(context: ScanContext) -> bool:
    readme = context.root / "README.md"
    if not readme.exists():
        return False
    text = read_text(readme)
    return bool(
        _DOCUMENTED_ENTRYPOINT_RE.search(text)
        or _has_documented_console_script(text, _project_console_scripts(context.root))
    )


def _project_console_scripts(root: Path) -> set[str]:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return set()
    text = read_text(pyproject)
    scripts: set[str] = set()
    current_table = ""
    for line in text.splitlines():
        stripped = line.strip()
        table_match = re.match(r"\[([^\]]+)\]", stripped)
        if table_match:
            current_table = table_match.group(1).strip()
            continue
        if current_table in {"project.scripts", "tool.poetry.scripts"}:
            script_match = re.match(r"""["']?([A-Za-z0-9_.-]+)["']?\s*=""", stripped)
            if script_match:
                scripts.add(script_match.group(1))
        dotted_match = re.match(r"""scripts\.["']?([A-Za-z0-9_.-]+)["']?\s*=""", stripped)
        if current_table == "project" and dotted_match:
            scripts.add(dotted_match.group(1))
    return scripts


def _has_documented_console_script(readme_text: str, scripts: set[str]) -> bool:
    for script in scripts:
        pattern = (
            rf"(?m)(?:^|\n)\s*(?:\$|>)?\s*{re.escape(script)}(?:\s|$)|"
            rf"`{re.escape(script)}\s+[^`]+`"
        )
        if re.search(pattern, readme_text):
            return True
    return False


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
        "Unseeded randomness in Python code",
        Category.REPRODUCIBILITY,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Uses AST analysis to find clear Python randomness without a seeding call.",
        "Uncontrolled randomness can make reported results hard to reproduce.",
        "Add random.seed(seed), np.random.seed(seed), torch.manual_seed(seed), "
        "tf.random.set_seed(seed), or pass random_state=seed / seed=seed to stochastic ML calls.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        scan = _scan_python_randomness(context)
        if not scan.randomness:
            return []
        if scan.seed_application:
            return []

        evidence = [scan.randomness]
        if scan.seed_declaration:
            evidence.insert(0, scan.seed_declaration)
            return [
                self.finding(
                    context,
                    message=(
                        "A seed option is declared, but randomness is used without applying that "
                        "value to any seeding function or stochastic random_state/seed parameter."
                    ),
                    evidence=evidence,
                    recommendation=(
                        "Wire the declared seed into random.seed(seed), np.random.seed(seed), "
                        "torch.manual_seed(seed), tf.random.set_seed(seed), and pass "
                        "random_state=seed / seed=seed to stochastic ML calls."
                    ),
                    file=scan.randomness.file,
                    line=scan.randomness.line,
                )
            ]

        return [
            self.finding(
                context,
                message="Randomness is used, but no deterministic seed application was detected.",
                evidence=evidence,
                file=scan.randomness.file,
                line=scan.randomness.line,
            )
        ]


@dataclass(frozen=True)
class _RandomnessScan:
    randomness: Evidence | None = None
    seed_application: Evidence | None = None
    seed_declaration: Evidence | None = None


@dataclass(frozen=True)
class _PythonSource:
    file: str
    text: str
    cell_index: int | None = None


class _RandomnessVisitor(ast.NodeVisitor):
    _PY_RANDOM_IGNORED: ClassVar[set[str]] = {"seed", "getstate", "setstate"}
    _TORCH_RANDOM_OPS: ClassVar[set[str]] = {
        "bernoulli",
        "multinomial",
        "normal",
        "poisson",
        "rand",
        "rand_like",
        "randint",
        "randint_like",
        "randn",
        "randn_like",
        "randperm",
    }
    _SKLEARN_RANDOM_CALLS: ClassVar[set[str]] = {
        "train_test_split",
        "KFold",
        "StratifiedKFold",
        "ShuffleSplit",
        "StratifiedShuffleSplit",
        "GroupShuffleSplit",
        "RepeatedKFold",
        "RepeatedStratifiedKFold",
        "shuffle",
        "resample",
        "ParameterSampler",
        "RandomizedSearchCV",
        "RandomForestClassifier",
        "RandomForestRegressor",
        "ExtraTreesClassifier",
        "ExtraTreesRegressor",
        "GradientBoostingClassifier",
        "GradientBoostingRegressor",
        "HistGradientBoostingClassifier",
        "HistGradientBoostingRegressor",
        "DecisionTreeClassifier",
        "DecisionTreeRegressor",
        "MLPClassifier",
        "MLPRegressor",
        "KMeans",
        "MiniBatchKMeans",
        "PCA",
        "TSNE",
    }
    _SEED_OPTION_NAMES: ClassVar[set[str]] = {"seed", "random-state", "random_state"}

    def __init__(self, source: _PythonSource):
        self.source = source
        self.aliases: dict[str, str] = {}
        self.randomness: Evidence | None = None
        self.seed_application: Evidence | None = None
        self.seed_declaration: Evidence | None = None

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            local = alias.asname or alias.name.split(".")[0]
            self.aliases[local] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            if alias.name == "*":
                continue
            local = alias.asname or alias.name
            self.aliases[local] = f"{module}.{alias.name}" if module else alias.name
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        full_name = self._canonical_name(node.func)
        if self.seed_declaration is None and self._declares_seed_option(full_name, node):
            self.seed_declaration = self._evidence(
                node, "Seed-like CLI/config option declared but not applied yet.", full_name
            )

        if full_name is not None:
            if self.seed_application is None and self._is_seed_application(full_name, node):
                self.seed_application = self._evidence(
                    node, f"Seed application detected via `{full_name}`.", full_name
                )
            if self.randomness is None and self._is_randomness_use(full_name, node):
                self.randomness = self._evidence(
                    node, f"Randomness call detected: `{full_name}`.", full_name
                )

        if full_name is not None and self._is_model_parameter_wrapper(full_name):
            return
        self.generic_visit(node)

    def _evidence(self, node: ast.Call, message: str, value: str | None = None) -> Evidence:
        line = self.source.cell_index if self.source.cell_index is not None else node.lineno
        if self.source.cell_index is not None:
            message = f"{message} Notebook code cell {self.source.cell_index}."
        return Evidence(message, self.source.file, line, value)

    def _canonical_name(self, node: ast.AST) -> str | None:
        raw = self._raw_name(node)
        if raw is None:
            return None
        parts = raw.split(".")
        if parts and parts[0] in self.aliases:
            return ".".join([*self.aliases[parts[0]].split("."), *parts[1:]])
        return raw

    def _raw_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = self._raw_name(node.value)
            return f"{parent}.{node.attr}" if parent else node.attr
        return None

    def _is_seed_application(self, full_name: str, node: ast.Call) -> bool:
        if full_name in {
            "random.seed",
            "numpy.random.seed",
            "torch.manual_seed",
            "torch.cuda.manual_seed",
            "torch.cuda.manual_seed_all",
            "tensorflow.random.set_seed",
            "tensorflow.keras.utils.set_random_seed",
        }:
            return True
        if full_name == "random.Random":
            return self._has_seed_argument(node)
        if full_name == "numpy.random.default_rng":
            return self._has_seed_argument(node)
        if self._is_known_stochastic_ml_call(full_name):
            return self._has_seed_keyword(node)
        if self._has_seed_keyword(node) and self._looks_like_seeded_operation(full_name):
            return True
        return self._is_tensorflow_stateless_random(full_name)

    def _is_randomness_use(self, full_name: str, node: ast.Call) -> bool:
        if full_name.startswith("random."):
            last = full_name.rsplit(".", 1)[-1]
            return last not in self._PY_RANDOM_IGNORED and not self._is_seed_application(
                full_name, node
            )
        if full_name.startswith("numpy.random."):
            last = full_name.rsplit(".", 1)[-1]
            return last not in {"seed"} and not self._is_seed_application(full_name, node)
        if full_name.startswith("torch."):
            last = full_name.rsplit(".", 1)[-1]
            return last in self._TORCH_RANDOM_OPS
        if full_name.startswith("tensorflow.random."):
            return not self._is_seed_application(full_name, node)
        return self._is_known_stochastic_ml_call(full_name)

    def _is_known_stochastic_ml_call(self, full_name: str) -> bool:
        if not full_name.startswith("sklearn."):
            return False
        return full_name.rsplit(".", 1)[-1] in self._SKLEARN_RANDOM_CALLS

    def _is_tensorflow_stateless_random(self, full_name: str) -> bool:
        return full_name.startswith("tensorflow.random.stateless_")

    def _is_model_parameter_wrapper(self, full_name: str) -> bool:
        return full_name in {
            "torch.nn.Parameter",
            "torch.nn.parameter.Parameter",
        }

    def _has_seed_argument(self, node: ast.Call) -> bool:
        return any(not _is_none_literal(arg) for arg in node.args) or self._has_seed_keyword(node)

    def _has_seed_keyword(self, node: ast.Call) -> bool:
        return any(
            keyword.arg in {"random_state", "random_seed", "seed"}
            and not _is_none_literal(keyword.value)
            for keyword in node.keywords
        )

    def _looks_like_seeded_operation(self, full_name: str) -> bool:
        leaf = full_name.rsplit(".", 1)[-1].lower()
        return leaf in {
            "evaluate",
            "fit",
            "predict",
            "process",
            "process_features",
            "run",
            "sample",
            "train",
        }

    def _declares_seed_option(self, full_name: str | None, node: ast.Call) -> bool:
        if full_name is None:
            return False
        if not (
            full_name.endswith(".add_argument")
            or full_name in {"click.option", "typer.Option", "typer.Argument"}
        ):
            return False
        for arg in node.args:
            if (
                isinstance(arg, ast.Constant)
                and isinstance(arg.value, str)
                and _is_seed_option_name(arg.value)
            ):
                return True
        for keyword in node.keywords:
            if (
                keyword.arg == "dest"
                and isinstance(keyword.value, ast.Constant)
                and isinstance(keyword.value.value, str)
                and _is_seed_option_name(keyword.value.value)
            ):
                return True
        return False


def _is_none_literal(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


def _is_seed_option_name(value: str) -> bool:
    normalized = value.strip().lower().lstrip("-").replace("_", "-")
    return normalized in _RandomnessVisitor._SEED_OPTION_NAMES


def _scan_python_randomness(context: ScanContext) -> _RandomnessScan:
    randomness: Evidence | None = None
    seed_application: Evidence | None = None
    seed_declaration: Evidence | None = None

    for source in _python_sources(context):
        try:
            tree = ast.parse(source.text)
        except SyntaxError:
            continue
        visitor = _RandomnessVisitor(source)
        visitor.visit(tree)
        randomness = randomness or visitor.randomness
        seed_application = seed_application or visitor.seed_application
        seed_declaration = seed_declaration or visitor.seed_declaration
        if randomness and seed_application:
            break

    return _RandomnessScan(
        randomness=randomness,
        seed_application=seed_application,
        seed_declaration=seed_declaration,
    )


def _python_sources(context: ScanContext) -> list[_PythonSource]:
    sources: list[_PythonSource] = []
    for path in context.files:
        if path.suffix.lower() == ".py":
            if _is_test_python_path(context.rel(path)):
                continue
            sources.append(_PythonSource(context.rel(path), read_text(path)))
        elif path.suffix.lower() == ".ipynb":
            nb = read_notebook(path)
            if nb is None:
                continue
            for index, cell in enumerate(nb.cells, start=1):
                if cell.get("cell_type") == "code":
                    sources.append(
                        _PythonSource(context.rel(path), str(cell.get("source", "")), index)
                    )
    return sources


def _is_test_python_path(rel: str) -> bool:
    normalized = rel.replace("\\", "/").lower()
    name = Path(normalized).name
    return (
        normalized.startswith("tests/")
        or "/tests/" in normalized
        or name.startswith("test_")
        or name.endswith("_test.py")
    )


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
