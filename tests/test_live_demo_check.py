from __future__ import annotations

import importlib.util
import sys
from email.message import Message
from pathlib import Path
from urllib.error import HTTPError


def _load_live_demo_script():
    path = Path("scripts/check_live_demo.py")
    spec = importlib.util.spec_from_file_location("check_live_demo", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _SuccessOpener:
    def open(self, request, timeout):
        return _Response()


class _AuthRedirectOpener:
    def open(self, request, timeout):
        headers = Message()
        headers["Location"] = "https://share.streamlit.io/-/auth/app?redirect_uri=demo"
        raise HTTPError(
            request.full_url,
            303,
            "See Other",
            headers,
            fp=None,
        )


def test_live_demo_check_accepts_anonymous_success(monkeypatch) -> None:
    script = _load_live_demo_script()
    monkeypatch.setattr(script, "build_opener", lambda handler: _SuccessOpener())

    result = script.check_demo_url("https://demo.example")

    assert result.ok is True
    assert "anonymously reachable" in result.message


def test_live_demo_check_rejects_streamlit_auth_redirect(monkeypatch) -> None:
    script = _load_live_demo_script()
    monkeypatch.setattr(script, "build_opener", lambda handler: _AuthRedirectOpener())

    result = script.check_demo_url("https://demo.example")

    assert result.ok is False
    assert "Streamlit auth" in result.message
