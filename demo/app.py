from __future__ import annotations

import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

CLONE_TIMEOUT_SECONDS = 60
SCAN_TIMEOUT_SECONDS = 60
MAX_CLONE_BYTES = 200 * 1024 * 1024
GITHUB_REPO = "https://github.com/Tom409114/research-repo-doctor"
SAMPLE_REPOSITORIES: tuple[tuple[str, str], ...] = (
    ("Scan rrdoctor", GITHUB_REPO),
    ("Scan nanoGPT", "https://github.com/karpathy/nanoGPT"),
)
SAFE_SCAN_NOTE = (
    "Safety note: this demo only runs the static `rrdoctor scan` command on cloned files. "
    "It never installs dependencies, imports target code, builds the project, or runs repo scripts."
)


class DemoError(Exception):
    """Friendly error shown in the Streamlit UI."""


@dataclass(frozen=True)
class RepoTarget:
    owner: str
    repo: str

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}.git"

    @property
    def web_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}"


def parse_github_url(raw_url: str) -> RepoTarget:
    """Return the GitHub owner/repo for a public HTTPS GitHub URL."""

    value = raw_url.strip()
    if not value:
        raise DemoError("Paste a public GitHub repository URL first.")

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        raise DemoError("Use a public GitHub URL like https://github.com/owner/repo.")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise DemoError("That URL does not include both an owner and a repository name.")

    owner = parts[0]
    repo = parts[1].removesuffix(".git")
    valid_name = re.compile(r"^[A-Za-z0-9_.-]+$")
    if not valid_name.match(owner) or not valid_name.match(repo):
        raise DemoError("That GitHub repository URL contains unsupported characters.")

    return RepoTarget(owner=owner, repo=repo)


def directory_size_bytes(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            total += path.stat().st_size
        except OSError:
            continue
        if total > MAX_CLONE_BYTES:
            return total
    return total


def clone_repo(target: RepoTarget, destination: Path) -> Path:
    repo_dir = destination / target.repo
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_LFS_SKIP_SMUDGE": "1",
    }
    command = [
        "git",
        "clone",
        "--depth",
        "1",
        "--single-branch",
        target.clone_url,
        str(repo_dir),
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            env=env,
            text=True,
            timeout=CLONE_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise DemoError("Git is not installed in this demo environment.") from exc
    except subprocess.TimeoutExpired as exc:
        raise DemoError(
            "Cloning took too long for the web demo limit. Try `uvx rrdoctor scan .`."
        ) from exc

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        if "Repository not found" in detail or "Authentication failed" in detail:
            raise DemoError(
                "GitHub could not clone that repository. It may be private or not exist."
            )
        raise DemoError(f"Git clone failed: {detail[:500] or 'unknown error'}")

    size = directory_size_bytes(repo_dir)
    if size > MAX_CLONE_BYTES:
        shutil.rmtree(repo_dir, ignore_errors=True)
        mb = MAX_CLONE_BYTES // (1024 * 1024)
        raise DemoError(f"That repository is larger than this demo's {mb} MB shallow-clone limit.")

    return repo_dir


def run_rrdoctor_scan(repo_dir: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "rrdoctor",
        "scan",
        str(repo_dir),
        "--format",
        "json",
        "--fail-on",
        "none",
        "--quiet",
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=SCAN_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise DemoError("The static scan took too long for this web demo.") from exc

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise DemoError(f"rrdoctor scan failed: {detail[:500] or 'unknown error'}")

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise DemoError("rrdoctor returned an unreadable JSON report.") from exc

    if not isinstance(payload, dict):
        raise DemoError("rrdoctor returned an unexpected report shape.")
    return payload


def scan_public_repo(raw_url: str) -> tuple[RepoTarget, dict[str, Any]]:
    target = parse_github_url(raw_url)
    with tempfile.TemporaryDirectory(prefix="rrdoctor-demo-") as tmp:
        repo_dir = clone_repo(target, Path(tmp))
        report = run_rrdoctor_scan(repo_dir)
    return target, report


def prioritize_findings(findings: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    severity_rank = {"error": 0, "warning": 1, "info": 2}

    def sort_key(item: tuple[int, dict[str, Any]]) -> tuple[int, int, int]:
        index, finding = item
        rule_id = str(finding.get("rule_id", ""))
        severity = str(finding.get("severity", "info"))
        seed_rank = 0 if rule_id == "RRD052" else 1
        return (seed_rank, severity_rank.get(severity, 3), index)

    ordered = [finding for _, finding in sorted(enumerate(findings), key=sort_key)]
    return ordered[:limit]


def _summary_value(report: dict[str, Any], key: str) -> int:
    summary = report.get("summary", {})
    if isinstance(summary, dict):
        value = summary.get(key, 0)
        if isinstance(value, int):
            return value
    return 0


def rrdoctor_version_label() -> str:
    try:
        return package_version("rrdoctor")
    except PackageNotFoundError:
        pass

    try:
        rrdoctor_module = importlib.import_module("rrdoctor")
    except ImportError:
        return "unknown"

    return str(getattr(rrdoctor_module, "__version__", "unknown"))


def sample_repository_urls() -> tuple[str, ...]:
    return tuple(url for _label, url in SAMPLE_REPOSITORIES)


def main() -> None:
    st = importlib.import_module("streamlit")
    rrdoctor_version = rrdoctor_version_label()

    st.set_page_config(page_title="rrdoctor web demo", layout="centered")
    st.title("Research Repo Doctor")
    st.caption("Paste a public GitHub repo URL. Get an AE-style readiness level and top findings.")
    st.caption(f"Powered by rrdoctor {rrdoctor_version}. Static, key-free scan.")
    st.info(SAFE_SCAN_NOTE)

    st.session_state.setdefault("repo_url", "")
    sample_url = ""
    sample_columns = st.columns(len(SAMPLE_REPOSITORIES))
    for column, (label, url) in zip(sample_columns, SAMPLE_REPOSITORIES, strict=True):
        if column.button(label, use_container_width=True):
            st.session_state["repo_url"] = url
            sample_url = url

    with st.form("scan-form"):
        repo_url = st.text_input(
            "Public GitHub repository URL",
            placeholder="https://github.com/owner/repo",
            key="repo_url",
        )
        submitted = st.form_submit_button("Scan repository")

    if sample_url:
        repo_url = sample_url
        submitted = True

    if not submitted:
        st.markdown(f"Run locally any time: `uvx rrdoctor scan .`  \n[GitHub repo]({GITHUB_REPO})")
        return

    try:
        with st.spinner("Cloning shallow copy and running static rrdoctor scan..."):
            target, report = scan_public_repo(repo_url)
    except DemoError as exc:
        st.error(str(exc))
        st.markdown(f"Run locally instead: `uvx rrdoctor scan .`  \n[GitHub repo]({GITHUB_REPO})")
        return

    score = int(report.get("score", 0) or 0)
    readiness = report.get("readiness", {})
    readiness_level = "Unknown"
    readiness_note = ""
    if isinstance(readiness, dict):
        readiness_level = str(readiness.get("level") or readiness_level)
        readiness_note = str(readiness.get("description") or "")
    st.subheader(f"Results for [{target.owner}/{target.repo}]({target.web_url})")
    st.metric("Artifact readiness", readiness_level)
    if readiness_note:
        st.caption(readiness_note)
    st.metric("Heuristic score", f"{score}/100")
    st.progress(max(0, min(score, 100)) / 100)

    col1, col2, col3 = st.columns(3)
    col1.metric("Errors", _summary_value(report, "error"))
    col2.metric("Warnings", _summary_value(report, "warning"))
    col3.metric("Info", _summary_value(report, "info"))

    findings = report.get("findings", [])
    if not isinstance(findings, list) or not findings:
        st.success("No findings for this profile. Nice.")
    else:
        st.subheader("Top findings")
        for finding in prioritize_findings([item for item in findings if isinstance(item, dict)]):
            rule_id = finding.get("rule_id", "unknown")
            severity = finding.get("severity", "info")
            title = finding.get("title", "Finding")
            message = finding.get("message", "")
            recommendation = finding.get("recommendation", "")
            st.markdown(f"**{rule_id}** - `{severity}` - {title}")
            if message:
                st.write(message)
            if recommendation:
                st.markdown(f"How to fix: {recommendation}")
            st.divider()

    st.markdown(
        f"Run this on your own machine: `uvx rrdoctor scan .`  \n[GitHub repo]({GITHUB_REPO})"
    )
    st.caption(f"This web demo is running rrdoctor {rrdoctor_version}.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive Streamlit Cloud fallback
        try:
            st = importlib.import_module("streamlit")
        except Exception:
            raise

        st.error("The web demo hit an unexpected startup issue.")
        st.write(
            "The scanner itself is still available locally and does not require an API key "
            "or a hosted service."
        )
        st.code("uvx rrdoctor scan .", language="bash")
        st.markdown(f"[GitHub repo]({GITHUB_REPO})")
        st.caption(f"Startup detail for maintainers: {type(exc).__name__}: {exc}")
