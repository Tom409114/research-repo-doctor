from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


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
    url = "https://demo.example"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.url


class _SuccessOpener:
    def open(self, request, timeout):
        return _Response()


class _StreamlitHandshakeOpener:
    def open(self, request, timeout):
        response = _Response()
        response.url = request.full_url
        return response


class _AuthLandingResponse(_Response):
    url = "https://share.streamlit.io/-/auth/app?redirect_uri=https%3A%2F%2Fdemo.example%2F"


class _AuthLandingOpener:
    def open(self, request, timeout):
        return _AuthLandingResponse()


def test_live_demo_check_accepts_anonymous_success(monkeypatch) -> None:
    script = _load_live_demo_script()
    monkeypatch.setattr(script, "build_opener", lambda handler: _SuccessOpener())

    result = script.check_demo_url("https://demo.example")

    assert result.ok is True
    assert "anonymously reachable" in result.message


def test_live_demo_check_accepts_streamlit_redirect_handshake(monkeypatch) -> None:
    script = _load_live_demo_script()
    monkeypatch.setattr(script, "build_opener", lambda handler: _StreamlitHandshakeOpener())

    result = script.check_demo_url("https://demo.example")

    assert result.ok is True
    assert "after redirects" in result.message


def test_live_demo_check_rejects_streamlit_auth_landing(monkeypatch) -> None:
    script = _load_live_demo_script()
    monkeypatch.setattr(script, "build_opener", lambda handler: _AuthLandingOpener())

    result = script.check_demo_url("https://demo.example")

    assert result.ok is False
    assert "Streamlit auth" in result.message
