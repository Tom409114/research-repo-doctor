"""Artifact readiness badge rendering.

Produces either a Shields.io endpoint document (for a live badge that reads a
committed JSON file) or a self-contained SVG. Both are deterministic and need no
network access.
"""

from __future__ import annotations

import json

from rrdoctor.models import ScanReport


def _color_for_readiness(level: str) -> str:
    if level == "Reproduced-ready":
        return "brightgreen"
    if level == "Functional":
        return "green"
    if level == "Available":
        return "yellow"
    return "orange"


_HEX = {
    "brightgreen": "#4c1",
    "green": "#97ca00",
    "yellowgreen": "#a4a61d",
    "yellow": "#dfb317",
    "orange": "#fe7d37",
    "red": "#e05d44",
}


def render_badge_endpoint(report: ScanReport) -> str:
    """Render a Shields.io endpoint JSON document."""

    payload = {
        "schemaVersion": 1,
        "label": "rrdoctor",
        "message": report.readiness.level,
        "color": _color_for_readiness(report.readiness.level),
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_badge_svg(report: ScanReport) -> str:
    """Render a self-contained SVG badge."""

    label = "rrdoctor"
    message = report.readiness.level
    color = _HEX[_color_for_readiness(report.readiness.level)]
    # Approximate width using a fixed per-character estimate; good enough for a badge.
    label_w = 6 + len(label) * 7
    msg_w = 10 + len(message) * 7
    total = label_w + msg_w
    label_mid = label_w / 2
    msg_mid = label_w + msg_w / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" '
        f'role="img" aria-label="{label}: {message}">'
        f"<title>{label}: {message}</title>"
        '<linearGradient id="s" x2="0" y2="100%">'
        '<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
        '<stop offset="1" stop-opacity=".1"/></linearGradient>'
        f'<rect rx="3" width="{total}" height="20" fill="#fff"/>'
        f'<rect rx="3" width="{label_w}" height="20" fill="#555"/>'
        f'<rect rx="3" x="{label_w}" width="{msg_w}" height="20" fill="{color}"/>'
        f'<rect rx="3" width="{total}" height="20" fill="url(#s)"/>'
        '<g fill="#fff" text-anchor="middle" '
        'font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">'
        f'<text x="{label_mid}" y="15" fill="#010101" fill-opacity=".3">{label}</text>'
        f'<text x="{label_mid}" y="14">{label}</text>'
        f'<text x="{msg_mid}" y="15" fill="#010101" fill-opacity=".3">{message}</text>'
        f'<text x="{msg_mid}" y="14">{message}</text>'
        "</g></svg>\n"
    )
