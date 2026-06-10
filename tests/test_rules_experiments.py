from __future__ import annotations

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def test_cuda_without_fallback_flagged(tmp_path) -> None:
    (tmp_path / "train.py").write_text("model = model.cuda()\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD054"}).scan(tmp_path)

    assert len(report.findings) == 1
    assert report.findings[0].rule_id == "RRD054"


def test_cuda_with_is_available_guard_passes(tmp_path) -> None:
    (tmp_path / "train.py").write_text(
        "import torch\n"
        "device = 'cuda' if torch.cuda.is_available() else 'cpu'\n"
        "model = model.to(device)\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD054"}).scan(tmp_path)

    assert not report.findings


def test_cuda_with_documented_requirement_passes(tmp_path) -> None:
    (tmp_path / "train.py").write_text("model = model.cuda()\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Demo\n\nRequires an NVIDIA GPU with CUDA 12.\n", encoding="utf-8"
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD054"}).scan(tmp_path)

    assert not report.findings
