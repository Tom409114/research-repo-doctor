"""Shared path and content helpers for rules."""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

from rrdoctor.models import ScanContext
from rrdoctor.rules.base import read_text

TEXT_SUFFIXES = {
    ".cfg",
    ".cff",
    ".ini",
    ".ipynb",
    ".json",
    ".md",
    ".py",
    ".r",
    ".rmd",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

CODE_SUFFIXES = (".py", ".r", ".R", ".jl", ".m", ".sh", ".ipynb", ".yaml", ".yml", ".json")
ABSOLUTE_PATH_RE = re.compile(
    r"(?i)(/users/[a-z0-9._-][^\s'\"`]+|/home/[a-z0-9._-][^\s'\"`]+|"
    r"/mnt/[a-z]/[^\s'\"`]+|[a-z]:\\+(?:users|documents and settings|program files|"
    r"tmp|temp|data|workspace|repo|[a-z0-9._-]+(?: [a-z0-9._-]+)*)\\+[^\s'\"`]+)"
)


def has_file(root: Path, names: list[str]) -> bool:
    """Return true when one of the path names exists."""

    lowered = {name.lower() for name in names}
    for child in root.iterdir() if root.exists() else []:
        if child.name.lower() in lowered:
            return True
    return any((root / name).exists() for name in names)


def find_files(context: ScanContext, patterns: list[str]) -> list[Path]:
    """Return scanned files matching fnmatch patterns."""

    matches: list[Path] = []
    for path in context.files:
        rel = context.rel(path)
        if any(fnmatch.fnmatch(rel, pattern) for pattern in patterns):
            matches.append(path)
    return matches


def text_files(context: ScanContext) -> list[Path]:
    """Return likely text files from the scanned file set."""

    return [path for path in context.files if path.suffix.lower() in TEXT_SUFFIXES]


def contains_any(path: Path, terms: tuple[str, ...]) -> bool:
    """Return true when a file contains any case-insensitive term."""

    text = read_text(path).lower()
    return any(term.lower() in text for term in terms)


def first_absolute_path(text: str) -> tuple[str, int] | None:
    """Return first absolute local path-like string and line number."""

    for index, line in enumerate(text.splitlines(), start=1):
        match = ABSOLUTE_PATH_RE.search(line)
        if (
            match
            and not is_embedded_path_segment(line, match.start())
            and not is_placeholder_absolute_path(match.group(0))
        ):
            return match.group(0), index
    return None


def is_embedded_path_segment(line: str, start: int) -> bool:
    """Return true when a match is embedded in a URL or larger path segment."""

    if start <= 0:
        return False
    previous = line[start - 1]
    return previous.isalnum() or previous in {"/", ".", "-", "_", ":"}


def is_placeholder_absolute_path(value: str) -> bool:
    """Return true for documentation examples rather than leaked local paths."""

    normalized = re.sub(r"/+", "/", value.replace("\\", "/").lower())
    return (
        normalized.startswith("/home/user/")
        or normalized.startswith("/home/joe/")
        or normalized.startswith("/home/me/")
        or normalized.startswith("/home/docs/")
        or normalized.startswith("/home/xyz/")
        or normalized.startswith("/users/user/")
        or normalized.startswith("/users/me/")
        or normalized == "c:/users/myuser"
        or normalized.startswith("c:/users/myuser/")
        or normalized.startswith("c:/program files/")
        or normalized.startswith("c:/program files (x86)/")
        or normalized.startswith("c:/folder")
        or normalized.startswith("c:/local_folder")
        or normalized.startswith("/home/...")
        or normalized.startswith("/users/...")
        or "/<user>/" in normalized
        or "/<your_user>/" in normalized
        or "/<username>" in normalized
        or "\\<user>\\" in value.lower()
        or "/absolute_path" in normalized
        or "/path_to_" in normalized
        or "/path/to/" in normalized
    )
