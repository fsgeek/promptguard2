"""Thin OpenRouter chat-completions client. Single call, fails loud on empty."""

import os
from typing import List, Dict, Optional

import httpx

URL = "https://openrouter.ai/api/v1/chat/completions"


class EmptyCompletionError(RuntimeError):
    """Raised when the model returns empty content (no silent empty-string aggregation)."""


def call_model(
    model: str,
    messages: List[Dict[str, str]],
    api_key: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.0,
    timeout: float = 120.0,
) -> str:
    """One completion. Raises on non-200 or empty content."""
    key = api_key or os.environ["OPENROUTER_API_KEY"]
    resp = httpx.post(
        URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages,
              "max_tokens": max_tokens, "temperature": temperature},
        timeout=timeout,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise EmptyCompletionError(f"{model} returned empty content")
    return content.strip()
