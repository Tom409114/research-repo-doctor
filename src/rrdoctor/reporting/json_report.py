"""JSON report renderer."""

from __future__ import annotations

import json

from rrdoctor.models import ScanReport, to_jsonable


def render_json(report: ScanReport) -> str:
    """Render a scan report as stable JSON."""

    return json.dumps(to_jsonable(report), indent=2, sort_keys=True) + "\n"
