"""Tests for tools/fetch_wikipedia.py

The Wikipedia API is mocked via monkeypatching urllib.request.urlopen so the
tests are hermetic and offline.
"""

import io
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import fetch_wikipedia as fw  # noqa: E402


class _FakeResponse:
    def __init__(self, payload: dict):
        self._buf = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def read(self):
        return self._buf.read()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _patch_urlopen(monkeypatch, payload):
    def fake(req, timeout=None):
        return _FakeResponse(payload)
    monkeypatch.setattr(fw.urllib.request, "urlopen", fake)


def test_fetch_summary(monkeypatch):
    _patch_urlopen(monkeypatch, {
        "title": "Gradient descent",
        "extract": "Gradient descent is a first-order iterative optimization algorithm.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Gradient_descent"}},
    })
    out = fw.fetch_summary("Gradient descent")
    assert out["title"] == "Gradient descent"
    assert "first-order" in out["extract"]


def test_fetch_sections(monkeypatch):
    _patch_urlopen(monkeypatch, {
        "parse": {
            "sections": [
                {"index": 1, "line": "History", "level": "2"},
                {"index": 2, "line": "Variants", "level": "2"},
            ]
        }
    })
    sections = fw.fetch_sections("Gradient descent")
    assert len(sections) == 2
    assert sections[1]["line"] == "Variants"


def test_fetch_section_wikitext(monkeypatch):
    _patch_urlopen(monkeypatch, {
        "parse": {"wikitext": "==Variants==\nStochastic gradient descent..."}
    })
    text = fw.fetch_section("Gradient descent", 2)
    assert "Stochastic" in text


def test_fetch_wikitext_dict_form(monkeypatch):
    # Older API responses may wrap wikitext in {"*": "..."}
    _patch_urlopen(monkeypatch, {"parse": {"wikitext": {"*": "Full body wikitext"}}})
    assert fw.fetch_wikitext("X") == "Full body wikitext"


def test_404_exits_with_code_2(monkeypatch):
    import urllib.error

    def fake(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)
    monkeypatch.setattr(fw.urllib.request, "urlopen", fake)
    with pytest.raises(SystemExit) as exc:
        fw.fetch_summary("Nonexistent Page Title 12345")
    assert exc.value.code == 2


def test_api_missingtitle_exits_with_code_2(monkeypatch):
    _patch_urlopen(monkeypatch, {"error": {"code": "missingtitle", "info": "missing"}})
    with pytest.raises(SystemExit) as exc:
        fw.fetch_sections("Nope")
    assert exc.value.code == 2
