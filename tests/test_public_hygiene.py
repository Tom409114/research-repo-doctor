from __future__ import annotations

import subprocess
from base64 import b64decode
from pathlib import Path

FORBIDDEN_TRACKED_PATH_PARTS = (
    "Y29kZXgtZm9yLW9zcy1hcHBsaWNhdGlvbg==",
    "aW5pdGlhbC1pc3N1ZXM=",
    "bGF1bmNoLWNoZWNrbGlzdA==",
    "Q09OVFJJQl9hd2Vzb21lX2VudHJ5",
    "TUFLSU5HX1RIRV9HSUY=",
)

FORBIDDEN_PUBLIC_TEXT = (
    "QzpcVXNlcnNcdGh1YWg=",
    "ZmlsZXMtbWVudGlvbmVkLWJ5LXRoZS11c2VyLXR4dA==",
    "LmNvZGV4L2F0dGFjaG1lbnRz",
    "Y29kZXgtZm9yLW9zcy1hcHBsaWNhdGlvbg==",
    "ZG9jcy9pbml0aWFsLWlzc3Vlcy5tZA==",
    "ZG9jcy9sYXVuY2gtY2hlY2tsaXN0Lm1k",
    "Q09OVFJJQl9hd2Vzb21lX2VudHJ5Lm1k",
    "b25jZSB0aGUgcHVibGljIHJlcG8gaXMgbGF1bmNoZWQ=",
    "QE9XTkVS",
)

TEXT_SUFFIXES = {
    ".cff",
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def _decode_public_guard_terms(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(b64decode(value).decode("utf-8") for value in values)


def test_out_of_scope_working_files_are_not_tracked() -> None:
    tracked = _tracked_files()
    forbidden_path_parts = _decode_public_guard_terms(FORBIDDEN_TRACKED_PATH_PARTS)

    leaked_paths = [
        path
        for path in tracked
        if any(part.lower() in path.lower() for part in forbidden_path_parts)
    ]

    assert leaked_paths == []


def test_public_text_files_do_not_expose_local_workspace_or_working_notes() -> None:
    leaks: list[str] = []
    forbidden_text = _decode_public_guard_terms(FORBIDDEN_PUBLIC_TEXT)

    for tracked_path in _tracked_files():
        path = Path(tracked_path)
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in forbidden_text:
            if forbidden in text:
                leaks.append(f"{tracked_path}: {forbidden}")

    assert leaks == []


def test_readme_demo_gif_is_committed_and_nonempty() -> None:
    demo = Path("docs/demo.gif")

    assert demo.exists()
    assert demo.stat().st_size > 100_000
    assert demo.read_bytes()[:6] in {b"GIF87a", b"GIF89a"}


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]
