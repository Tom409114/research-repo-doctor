"""Generate docs/demo.gif from a real rrdoctor command.

This is a maintainer utility, not part of the rrdoctor runtime. It avoids a
fragile terminal recorder dependency by capturing the command output and
rendering a compact terminal-style animation with Pillow.
"""

from __future__ import annotations

import re
import subprocess
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - maintainer utility
    raise SystemExit(
        "Install Pillow to regenerate docs/demo.gif: python -m pip install Pillow"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "demo.gif"
COMMAND = "rrdoctor scan examples/unseeded-ml-repo --include RRD052,RRD091,RRD070 --fail-on none"
WIDTH = 1180
HEIGHT = 760
PADDING_X = 32
PADDING_Y = 28
FONT_SIZE = 21
LINE_HEIGHT = 30
FRAMES = 12


def main() -> int:
    output = subprocess.check_output(
        COMMAND,
        cwd=ROOT,
        shell=True,
        text=True,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
    )
    lines = prepare_lines(output)
    frames = [render_frame(lines, visible_rows) for visible_rows in visible_steps(lines)]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=[220, 180, 160, 150, 150, 150, 150, 150, 150, 150, 150, 1700],
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


def prepare_lines(raw: str) -> list[str]:
    normalized = re.sub(r"\x1b\[[0-9;]*m", "", raw)
    selected: list[str] = [
        "$ " + COMMAND,
        "",
    ]
    keep_prefixes = (
        "- Repository:",
        "- Artifact readiness:",
        "- Heuristic score:",
        "- Rules evaluated:",
        "## How to fix first",
        "- **RRD052**",
        "- **RRD091**",
        "- **RRD070**",
        "### warning / reproducibility",
        "#### RRD052:",
        "A seed option is declared",
        "Recommendation:",
    )
    for line in normalized.splitlines():
        clean = line.rstrip()
        if not clean:
            continue
        if clean.startswith(keep_prefixes):
            selected.extend(wrap(clean))
        if len(selected) >= 23:
            break
    return selected[:23]


def wrap(line: str) -> list[str]:
    return textwrap.wrap(
        line,
        width=88,
        subsequent_indent="  ",
        break_long_words=False,
        break_on_hyphens=False,
    )


def visible_steps(lines: list[str]) -> list[int]:
    target = len(lines)
    if target <= FRAMES:
        return list(range(1, target + 1))
    return [round(1 + (target - 1) * i / (FRAMES - 1)) for i in range(FRAMES)]


def render_frame(lines: list[str], visible_rows: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#0d1117")
    draw = ImageDraw.Draw(image)
    font = load_font()
    bold = load_font(bold=True)

    draw.rounded_rectangle((18, 18, WIDTH - 18, HEIGHT - 18), radius=16, fill="#111827")
    draw.ellipse((40, 42, 54, 56), fill="#ff5f57")
    draw.ellipse((64, 42, 78, 56), fill="#ffbd2e")
    draw.ellipse((88, 42, 102, 56), fill="#28c840")
    draw.text((PADDING_X, 80), "Research Repo Doctor", fill="#8b949e", font=bold)

    y = 124
    for line in lines[:visible_rows]:
        fill = color_for(line)
        line_font = bold if line.startswith(("##", "####")) else font
        draw.text((PADDING_X, y), line, fill=fill, font=line_font)
        y += LINE_HEIGHT
    return image


def color_for(line: str) -> str:
    if line.startswith("$"):
        return "#7ee787"
    if "RRD052" in line:
        return "#f2cc60"
    if "RRD091" in line or "RRD070" in line:
        return "#d29922"
    if "Functional" in line or "88/100" in line:
        return "#79c0ff"
    if line.startswith("##") or line.startswith("####"):
        return "#ffa657"
    return "#c9d1d9"


def load_font(*, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/CascadiaMono.ttf"),
        Path("C:/Windows/Fonts/lucon.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), FONT_SIZE)
    return ImageFont.load_default()


if __name__ == "__main__":
    raise SystemExit(main())
