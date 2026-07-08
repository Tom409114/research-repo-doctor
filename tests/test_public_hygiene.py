from __future__ import annotations

import subprocess
from pathlib import Path

FORBIDDEN_TRACKED_PATH_PARTS = (
    "codex-for-oss" + "-application",
    "initial" + "-issues",
    "launch" + "-checklist",
    "CONTRIB" + "_awesome_entry",
    "MAKING" + "_THE_GIF",
)

FORBIDDEN_PUBLIC_TEXT = (
    "C:" + "\\" + "Users" + "\\" + "thuah",
    "files-mentioned-by-the-user" + "-txt",
    ".codex" + "/" + "attachments",
    "codex-for-oss" + "-application",
    "docs" + "/" + "starter-issues.md",
    "docs" + "/" + "release-checklist.md",
    "CONTRIB" + "_awesome_entry.md",
    "once the public repo" + " is launched",
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


def test_internal_launch_materials_are_not_tracked() -> None:
    tracked = _tracked_files()

    leaked_paths = [
        path
        for path in tracked
        if any(part.lower() in path.lower() for part in FORBIDDEN_TRACKED_PATH_PARTS)
    ]

    assert leaked_paths == []


def test_public_text_files_do_not_expose_local_workspace_or_internal_application_notes() -> None:
    leaks: list[str] = []

    for tracked_path in _tracked_files():
        path = Path(tracked_path)
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_PUBLIC_TEXT:
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
