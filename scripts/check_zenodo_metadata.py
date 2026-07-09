"""Verify that citation metadata points to the current Zenodo release archive."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_TIMEOUT_SECONDS = 30
ZENODO_API = "https://zenodo.org/api/records/{record_id}"
VERSION_RE = re.compile(r'^version = "([^"]+)"$', re.MULTILINE)
DOI_RE = re.compile(r'^doi:\s*"?([^"\s]+)"?\s*$', re.MULTILINE)
ZENODO_DOI_RE = re.compile(r"^10\.5281/zenodo\.(\d+)$", re.IGNORECASE)


@dataclass(frozen=True)
class ZenodoCheck:
    ok: bool
    message: str
    warnings: tuple[str, ...] = ()


def read_release_reference(project_root: Path) -> tuple[str, str]:
    pyproject = (project_root / "pyproject.toml").read_text(encoding="utf-8")
    citation = (project_root / "CITATION.cff").read_text(encoding="utf-8")

    version_match = VERSION_RE.search(pyproject)
    if version_match is None:
        raise ValueError("pyproject.toml is missing a project version")

    doi_match = DOI_RE.search(citation)
    if doi_match is None:
        raise ValueError("CITATION.cff is missing a DOI")

    return version_match.group(1), doi_match.group(1)


def zenodo_record_id(doi: str) -> str:
    match = ZENODO_DOI_RE.fullmatch(doi)
    if match is None:
        raise ValueError(f"CITATION.cff DOI is not a Zenodo DOI: {doi}")
    return match.group(1)


def fetch_record(record_id: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict[str, Any]:
    request = Request(
        ZENODO_API.format(record_id=record_id),
        headers={"Accept": "application/json", "User-Agent": "rrdoctor-zenodo-check/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError("Zenodo returned an unexpected response")
    return payload


def validate_record(
    payload: dict[str, Any], expected_version: str, expected_doi: str
) -> ZenodoCheck:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        return ZenodoCheck(False, "Zenodo record is missing metadata.")

    actual_doi = str(payload.get("doi") or metadata.get("doi") or "")
    if actual_doi.lower() != expected_doi.lower():
        return ZenodoCheck(
            False,
            f"Zenodo record DOI is {actual_doi or 'missing'}, expected {expected_doi}.",
        )

    actual_version = str(metadata.get("version") or "").removeprefix("v")
    normalized_expected = expected_version.removeprefix("v")
    if actual_version != normalized_expected:
        return ZenodoCheck(
            False,
            f"Zenodo record version is {actual_version or 'missing'}, "
            f"expected {normalized_expected}.",
        )

    expected_tag = f"/tree/v{normalized_expected}"
    related = metadata.get("related_identifiers")
    related_urls = [
        str(item.get("identifier") or "") for item in related or [] if isinstance(item, dict)
    ]
    if not any(expected_tag in url for url in related_urls):
        return ZenodoCheck(
            False, f"Zenodo record does not reference GitHub tag v{normalized_expected}."
        )

    files = payload.get("files")
    file_names = [str(item.get("key") or "") for item in files or [] if isinstance(item, dict)]
    if not any(f"v{normalized_expected}" in name for name in file_names):
        return ZenodoCheck(
            False, f"Zenodo archive filename does not identify v{normalized_expected}."
        )

    warnings: list[str] = []
    creators = metadata.get("creators")
    creator_names = [
        str(item.get("name") or "") for item in creators or [] if isinstance(item, dict)
    ]
    if not creator_names or all(_generic_creator(name) for name in creator_names):
        warnings.append(
            "Zenodo creator metadata is still generic; replace it with consented author names "
            "and affiliations when available."
        )

    concept_doi = str(payload.get("conceptdoi") or "")
    concept_text = f"; concept DOI {concept_doi}" if concept_doi else ""
    return ZenodoCheck(
        True,
        f"Zenodo {actual_doi} matches rrdoctor {normalized_expected}{concept_text}.",
        tuple(warnings),
    )


def _generic_creator(name: str) -> bool:
    lowered = name.casefold()
    return any(marker in lowered for marker in ("maintainer", "the authors", "project team"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that CITATION.cff points to the current Zenodo release archive."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root containing pyproject.toml and CITATION.cff",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args(argv)

    try:
        version, doi = read_release_reference(args.project_root)
        payload = fetch_record(zenodo_record_id(doi), timeout=args.timeout)
        result = validate_record(payload, version, doi)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Zenodo metadata check failed: {exc}")
        return 1

    print(result.message)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
