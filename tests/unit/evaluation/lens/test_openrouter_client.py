"""Unit tests for the OpenRouter client (mocked — no network)."""

import pytest

from src.evaluation.lens.openrouter_client import call_model, EmptyCompletionError


class _FakeResp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code != 200:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_call_model_returns_content(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResp(200, {"choices": [{"message": {"content": "hello"}}]})

    monkeypatch.setattr("src.evaluation.lens.openrouter_client.httpx.post", fake_post)
    out = call_model("any/model", [{"role": "user", "content": "hi"}], api_key="k")
    assert out == "hello"


def test_call_model_raises_on_empty(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResp(200, {"choices": [{"message": {"content": "  "}}]})

    monkeypatch.setattr("src.evaluation.lens.openrouter_client.httpx.post", fake_post)
    with pytest.raises(EmptyCompletionError):
        call_model("any/model", [{"role": "user", "content": "hi"}], api_key="k")
