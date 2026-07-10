"""Environment and dependency rules."""

from __future__ import annotations

import ast
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

from rrdoctor.models import Category, Evidence, Finding, ScanContext, Severity
from rrdoctor.rules.base import Rule, definition, parse_python_ast, read_text
from rrdoctor.rules.paths import has_file

DEPENDENCY_FILES = [
    # Python
    "pyproject.toml",
    "requirements.txt",
    "environment.yml",
    "environment.yaml",
    "conda.yml",
    "conda.yaml",
    "Pipfile",
    "poetry.lock",
    "uv.lock",
    "setup.py",
    "setup.cfg",
    # JavaScript
    "package.json",
    # R
    "renv.lock",
    "DESCRIPTION",
    "install.R",
    "install.r",
    # Julia
    "Project.toml",
    "Manifest.toml",
    # Rust
    "Cargo.toml",
    "Cargo.lock",
    # C and C++
    "CMakeLists.txt",
    "meson.build",
    "conanfile.txt",
    "conanfile.py",
    "vcpkg.json",
    # Reproducible environments
    "Dockerfile",
    "flake.nix",
    "flake.lock",
]
NESTED_MANIFEST_DIRS = ("package",)
SNAKEMAKE_ENV_LAYOUTS = (
    ("Snakefile", "envs"),
    ("workflow/Snakefile", "workflow/envs"),
    ("workflows/Snakefile", "workflows/envs"),
)
SNAKEMAKE_ENV_SUFFIXES = {".yaml", ".yml"}
RUNTIME_HINT_FILES = (
    "runtime.txt",
    ".python-version",
    ".node-version",
    ".nvmrc",
    "rust-toolchain",
    "rust-toolchain.toml",
)

# Patterns that indicate a documented runtime/language version across ecosystems.
RUNTIME_VERSION_RE = re.compile(
    r"(?i)("
    r"requires-python"  # pyproject
    r"|python_requires"  # setup.py / setup.cfg
    r"|python\s*[<>=~!]|python="  # requirements / conda
    r"|runtime"  # runtime.txt
    r"|node\s*[:=]"  # package.json engines
    r"|depends:\s*r\s*\(|r\s*\(\s*>="  # R DESCRIPTION: "Depends: R (>= 4.1)"
    r"|rversion|r-version"  # renv.lock R version field
    r"|julia\s*[<>=~]|\[compat\]"  # Julia Project.toml compat
    r"|rust-version\s*=|channel\s*=\s*['\"]\d"  # Cargo / rust-toolchain
    r"|cmake_minimum_required\s*\(\s*version"  # CMake runtime floor
    r"|(?m:^\s*from\s+(?:--platform=\S+\s+)?(?:\S+/)*[^/\s:@]+"
    r"(?::(?!latest(?:\s|$))[^@\s]+|@sha256:[0-9a-f]{16,})"
    r"(?:\s+as\s+\S+)?\s*$)"  # Versioned or digest-pinned container base image
    r")"
)
README_INSTALL_RE = re.compile(
    r"(?i)\b("
    r"pip\s+install|uv\s+pip\s+install|pipx\s+run|uvx\s+|"
    r"conda\s+env\s+create|mamba\s+env\s+create|poetry\s+install|"
    r"renv::restore|Rscript\s+|julia\s+--project|npm\s+install|"
    r"cargo\s+(?:install|build)|cmake\s+|docker\s+build|nix\s+(?:build|develop)"
    r")"
)


class DependencyManifestMissingRule(Rule):
    definition = definition(
        "RRD030",
        "No dependency manifest found",
        Category.ENVIRONMENT,
        Severity.ERROR,
        ("minimal", "standard", "strict", "ml"),
        "Checks for dependency manifests.",
        "A repository without dependency metadata is hard to reproduce.",
        "Add a language manifest such as pyproject.toml/Cargo.toml, a container or "
        "build environment such as Dockerfile/CMakeLists.txt, or another supported manifest.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not _existing_dependency_manifests(context.root):
            readme = context.root / "README.md"
            if readme.exists() and README_INSTALL_RE.search(read_text(readme)):
                rel = context.rel(readme)
                return [
                    self.finding(
                        context,
                        message=(
                            "No supported dependency manifest was found, but README install "
                            "instructions were detected."
                        ),
                        evidence=[Evidence("README contains an install command.", rel)],
                        recommendation=(
                            "Promote the documented install command into requirements.txt, "
                            "pyproject.toml, Cargo.toml/Cargo.lock, environment.yml/.yaml, "
                            "renv.lock, or another lockable manifest."
                        ),
                        file=rel,
                        severity=Severity.WARNING,
                    )
                ]
            return [self.finding(context, message="No supported dependency manifest was found.")]
        return []


class PythonVersionHintMissingRule(Rule):
    definition = definition(
        "RRD031",
        "Dependency manifest lacks version hint",
        Category.ENVIRONMENT,
        Severity.WARNING,
        ("minimal", "standard", "strict", "ml"),
        "Checks dependency manifests for a language/runtime version hint.",
        "Language/runtime versions (Python, R, Julia, Node, Rust, containers, and CMake) "
        "are part of the environment.",
        "Add requires-python, an R/Julia/Rust version, a versioned container base, "
        "cmake_minimum_required, runtime.txt, or another documented runtime version.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        existing = _existing_dependency_manifests(context.root)
        if not existing:
            return []
        runtime_hints = _existing_runtime_hints(context.root)
        combined = "\n".join(read_text(path) for path in [*existing, *runtime_hints])
        if not RUNTIME_VERSION_RE.search(combined):
            evidence = [
                Evidence(
                    "Manifest exists but no runtime version hint was detected.",
                    context.rel(existing[0]),
                )
            ]
            return [
                self.finding(
                    context,
                    message="Dependency manifest lacks a runtime/environment version hint.",
                    evidence=evidence,
                    file=context.rel(existing[0]),
                )
            ]
        return []


def _unpinned_requirements(text: str) -> list[str]:
    """Return requirement names that declare no version at all."""

    unpinned: list[str] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        # Drop environment markers and inline options.
        spec = line.split(";", 1)[0].strip()
        if not spec or spec[0] in "<>=~!@" or not spec[0].isascii() or not spec[0].isalnum():
            continue
        name = re.split(r"[\[<>=~!@ ]", spec, maxsplit=1)[0]
        if not any(op in spec for op in ("==", ">=", "<=", "~=", "!=", "<", ">", "@")):
            unpinned.append(name)
    return unpinned


class UnpinnedDependenciesRule(Rule):
    definition = definition(
        "RRD033",
        "Unpinned dependencies in requirements file",
        Category.ENVIRONMENT,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Checks requirements.txt files for dependencies declared without any version.",
        "Unpinned dependencies can resolve to different versions over time, which "
        "silently changes results and breaks reproduction.",
        "Pin versions (prefer ==) or document a tested version range and a lockfile.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        for name in ("requirements.txt", "requirements/base.txt", "requirements/main.txt"):
            path = context.root / name
            if not path.exists():
                continue
            unpinned = _unpinned_requirements(read_text(path))
            if unpinned:
                rel = context.rel(path)
                preview = ", ".join(unpinned[:6])
                return [
                    self.finding(
                        context,
                        message=f"{len(unpinned)} dependency line(s) declare no version.",
                        evidence=[Evidence(f"Unpinned: {preview}", rel)],
                        file=rel,
                    )
                ]
        return []


class ContainerMissingStrictRule(Rule):
    definition = definition(
        "RRD032",
        "Dockerfile or devcontainer missing",
        Category.ENVIRONMENT,
        Severity.INFO,
        ("strict",),
        "Checks strict-profile repositories for containerized environment docs.",
        "Containers are not required, but help reviewers rebuild complex environments.",
        "Add a Dockerfile, .devcontainer/devcontainer.json, or document why one is not needed.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        if not has_file(context.root, ["Dockerfile", ".devcontainer/devcontainer.json"]):
            return [
                self.finding(
                    context, message="Strict profile expects a Dockerfile or devcontainer."
                )
            ]
        return []


# Maps the name used in `import X` to the distribution name on PyPI when they differ.
IMPORT_TO_DISTRIBUTION = {
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "skimage": "scikit-image",
    "pil": "pillow",
    "yaml": "pyyaml",
    "bs4": "beautifulsoup4",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "erfa": "pyerfa",
    "github": "pygithub",
    "torch": "torch",
    "tensorflow": "tensorflow",
    "google": "protobuf",
    "imwatermark": "invisible-watermark",
    "mpl_toolkits": "matplotlib",
    "openssl": "pyopenssl",
    "setuptools_scm": "setuptools-scm",
}

_REQ_NAME_RE = re.compile(r"^[A-Za-z0-9_.\-]+")
_EGG_NAME_RE = re.compile(r"[#&]egg=([A-Za-z0-9_.\-]+)")


def _normalize(name: str) -> str:
    """PEP 503-style normalization so cv2/CV2/c.v.2 compare equal."""

    return re.sub(r"[-_.]+", "-", name.strip().lower())


def _declared_name_from_requirement_spec(spec: str) -> str | None:
    stripped = spec.strip()
    if not stripped or stripped.startswith("#"):
        return None
    egg = _EGG_NAME_RE.search(stripped)
    if egg:
        return _normalize(egg.group(1))
    if stripped.startswith("-"):
        return None
    match = _REQ_NAME_RE.match(stripped)
    if match:
        return _normalize(match.group(0))
    return None


def _declared_distributions(context: ScanContext) -> set[str]:
    """Best-effort set of declared dependency distribution names (normalized)."""

    declared: set[str] = set()

    for req in _candidate_manifest_paths(context.root, ("requirements.txt",)):
        if not req.exists():
            continue
        for line in read_text(req).splitlines():
            stripped = line.strip()
            name = _declared_name_from_requirement_spec(stripped)
            if name:
                declared.add(name)

    for pyproject in _candidate_manifest_paths(context.root, ("pyproject.toml",)):
        if not pyproject.exists():
            continue
        text = read_text(pyproject)
        parsed = _declared_from_pyproject_toml(text)
        if parsed:
            declared.update(parsed)
        else:
            declared.update(_declared_from_pyproject_text(text))

    for env_name in ("environment.yml", "environment.yaml", "conda.yml", "conda.yaml"):
        for env in _candidate_manifest_paths(context.root, (env_name,)):
            if env.exists():
                for line in read_text(env).splitlines():
                    stripped = line.strip().lstrip("-").strip()
                    match = _REQ_NAME_RE.match(stripped)
                    if match and match.group(0) not in {
                        "dependencies",
                        "pip",
                        "name",
                        "channels",
                    }:
                        name = _declared_name_from_requirement_spec(stripped)
                        if name:
                            declared.add(name)

    return declared


def _existing_dependency_manifests(root: Path) -> list[Path]:
    manifests = [
        path for path in _candidate_manifest_paths(root, tuple(DEPENDENCY_FILES)) if path.exists()
    ]
    manifests.extend(snakemake_environment_manifests(root))
    return manifests


def snakemake_environment_manifests(root: Path) -> list[Path]:
    """Return per-rule Conda environments from conventional Snakemake layouts.

    RRD034 does not use this list because it cannot yet map each script to its
    rule-specific environment without parsing the workflow graph.
    """

    manifests: list[Path] = []
    for snakefile, env_dir in SNAKEMAKE_ENV_LAYOUTS:
        if not (root / snakefile).is_file():
            continue
        base = root / env_dir
        if not base.is_dir():
            continue
        manifests.extend(
            path
            for path in sorted(base.rglob("*"), key=lambda candidate: candidate.as_posix())
            if path.is_file() and path.suffix.lower() in SNAKEMAKE_ENV_SUFFIXES
        )
    return manifests


def _existing_runtime_hints(root: Path) -> list[Path]:
    return [root / name for name in RUNTIME_HINT_FILES if (root / name).exists()]


def _candidate_manifest_paths(root: Path, names: tuple[str, ...]) -> list[Path]:
    paths = [root / name for name in names]
    for base in NESTED_MANIFEST_DIRS:
        paths.extend(root / base / name for name in names)
    return paths


def _declared_from_pyproject_toml(text: str) -> set[str]:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return set()

    declared: set[str] = set()
    project = _as_mapping(data.get("project"))
    _add_requirement_specs(declared, project.get("dependencies"))

    build_system = _as_mapping(data.get("build-system"))
    _add_requirement_specs(declared, build_system.get("requires"))

    optional = _as_mapping(project.get("optional-dependencies"))
    for specs in optional.values():
        _add_requirement_specs(declared, specs)

    poetry = _as_mapping(_as_mapping(data.get("tool")).get("poetry"))
    poetry_dependencies = _as_mapping(poetry.get("dependencies"))
    for name in poetry_dependencies:
        if str(name).lower() != "python":
            declared.add(_normalize(str(name)))

    poetry_groups = _as_mapping(poetry.get("group"))
    for group in poetry_groups.values():
        group_dependencies = _as_mapping(_as_mapping(group).get("dependencies"))
        for name in group_dependencies:
            if str(name).lower() != "python":
                declared.add(_normalize(str(name)))

    return declared


def _declared_from_pyproject_text(text: str) -> set[str]:
    declared: set[str] = set()
    # Fallback for malformed TOML: pull quoted requirement specs out of dependency arrays.
    for block in re.findall(r"dependencies\s*=\s*\[(.*?)\]", text, re.DOTALL):
        for spec in re.findall(r"['\"]([^'\"]+)['\"]", block):
            _add_requirement_specs(declared, [spec])
    optional = re.search(r"(?ms)^\[project\.optional-dependencies\](.*?)(?:^\[|\Z)", text)
    if optional:
        for block in re.findall(r"(?m)^\w[\w-]*\s*=\s*\[(.*?)\]", optional.group(1), re.DOTALL):
            for spec in re.findall(r"['\"]([^'\"]+)['\"]", block):
                _add_requirement_specs(declared, [spec])
    return declared


def _add_requirement_specs(declared: set[str], specs: Any) -> None:
    if not isinstance(specs, Iterable) or isinstance(specs, (str, bytes)):
        return
    for spec in specs:
        if not isinstance(spec, str):
            continue
        name = _declared_name_from_requirement_spec(spec)
        if name:
            declared.add(name)


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _local_modules(context: ScanContext) -> set[str]:
    """Top-level module/package names defined inside the repository."""

    local: set[str] = set()
    for path in context.files:
        if path.suffix != ".py":
            continue
        parts = context.rel(path).split("/")
        if not parts:
            continue
        stem = path.stem
        if stem != "__init__":
            local.add(_normalize(stem))
        first = parts[0]
        if first == "src" and len(parts) > 1:
            local.add(_normalize(parts[1].removesuffix(".py")))
            if len(parts) > 2 and parts[-1] == "__init__.py":
                local.add(_normalize(parts[-2]))
        else:
            local.add(_normalize(first.removesuffix(".py")))
            if len(parts) > 1 and parts[-1] == "__init__.py":
                local.add(_normalize(parts[-2]))
    return local


def _python_import_roots(text: str) -> set[str]:
    """Return top-level modules imported by real Python import statements."""

    tree = parse_python_ast(text)
    if tree is None:
        # Be conservative for generated or version-specific files: a regex
        # fallback is too noisy because it also scans comments and docstrings.
        return set()

    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".", 1)[0]
                if top:
                    roots.add(top)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                continue
            if node.module:
                roots.add(node.module.split(".", 1)[0])
    return roots


_IMPORT_SCAN_EXCLUDED_PARTS = {
    ".eggs",
    ".git",
    ".github",
    ".hg",
    ".nox",
    ".pyinstaller",
    ".spin",
    ".tox",
    "bench",
    "benchmark",
    "benchmarks",
    "build",
    "build_tools",
    "ci",
    "doc",
    "docs",
    "example",
    "examples",
    "extern",
    "external",
    "externals",
    "maint_tools",
    "site",
    "test",
    "tests",
    "third_party",
    "thirdparty",
    "vendor",
    "vendored",
}


def _is_runtime_import_file(context: ScanContext, path: Any) -> bool:
    """Return true for Python files likely to represent runtime code."""

    rel = context.rel(path)
    name = rel.rsplit("/", 1)[-1].lower()
    if name == "conftest.py" or name.startswith("test_") or name.endswith("_test.py"):
        return False
    parts = [part.lower() for part in rel.split("/")[:-1]]
    return not any(part in _IMPORT_SCAN_EXCLUDED_PARTS for part in parts)


class UndeclaredImportRule(Rule):
    definition = definition(
        "RRD034",
        "Imported package not in dependency manifest",
        Category.ENVIRONMENT,
        Severity.WARNING,
        ("standard", "strict", "ml"),
        "Cross-checks third-party imports against declared dependencies (deptry-style).",
        "Importing a package that no manifest declares is the most common reason a "
        "fresh environment fails to reproduce results.",
        "Add the missing package to requirements.txt/pyproject.toml, or remove the import.",
    )

    def check(self, context: ScanContext) -> list[Finding]:
        declared = _declared_distributions(context)
        if not declared:
            # No parseable manifest to compare against; RRD030 covers that case.
            return []

        stdlib: frozenset[str] = getattr(sys, "stdlib_module_names", frozenset())
        local = _local_modules(context)

        seen: dict[str, str] = {}
        for path in context.files:
            if path.suffix.lower() not in {".py"}:
                continue
            if not _is_runtime_import_file(context, path):
                continue
            text = read_text(path)
            for top in _python_import_roots(text):
                if not top or top.startswith("_"):
                    continue
                if top in stdlib:
                    continue
                norm = _normalize(top)
                if norm in local:
                    continue
                distribution = IMPORT_TO_DISTRIBUTION.get(norm, norm)
                if _normalize(distribution) in declared:
                    continue
                seen.setdefault(top, context.rel(path))

        if not seen:
            return []

        names = sorted(seen)
        evidence = [
            Evidence(f"`import {name}` is not declared in any manifest.", seen[name])
            for name in names[:5]
        ]
        listed = ", ".join(names[:8])
        return [
            self.finding(
                context,
                message=f"Imported package(s) not found in any dependency manifest: {listed}.",
                evidence=evidence,
            )
        ]


RULES = [
    DependencyManifestMissingRule(),
    PythonVersionHintMissingRule(),
    UnpinnedDependenciesRule(),
    UndeclaredImportRule(),
    ContainerMissingStrictRule(),
]
