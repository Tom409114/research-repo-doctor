from __future__ import annotations

import re
from pathlib import Path

_LOCAL_MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
_LOCAL_MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def test_readme_local_links_and_images_exist() -> None:
    root = Path(".")
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    missing: list[str] = []

    for target in [*_LOCAL_MARKDOWN_LINK.findall(text), *_LOCAL_MARKDOWN_IMAGE.findall(text)]:
        normalized = target.split("#", 1)[0].strip()
        if not normalized or _is_external_or_anchor(normalized):
            continue
        path = root / normalized
        if not path.exists():
            missing.append(target)

    assert missing == []


def _is_external_or_anchor(target: str) -> bool:
    lowered = target.lower()
    return (
        lowered.startswith(("http://", "https://", "mailto:"))
        or lowered.startswith("#")
        or lowered.startswith("file:")
    )
