"""
OpenRouter API Client with Metadata Tagging
Constitutional Principle II: Empirical Integrity
Constitutional Principle VI: Data Provenance
Constitutional Principle IV: Fail-Fast

Provides unified API access to multiple LLM providers with experiment tracking.
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class OpenRouterMessage(BaseModel):
    """OpenRouter chat message."""
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")


class OpenRouterRequest(BaseModel):
    """OpenRouter API request."""
    model: str = Field(..., description="Model identifier (e.g., anthropic/claude-sonnet-4.5)")
    messages: List[OpenRouterMessage] = Field(..., description="Conversation messages")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    max_tokens: int = Field(default=500, description="Maximum tokens to generate")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Experiment tracking metadata")


class OpenRouterResponse(BaseModel):
    """OpenRouter API response."""
    id: str
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, Any]  # Changed from Dict[str, int] to support nested structures like completion_tokens_details
    raw_response: Dict[str, Any] = Field(..., description="Complete raw API response")


class OpenRouterClient:
    """
    OpenRouter API client with metadata tagging.

    Supports experiment tracking via metadata for post-hoc cost analysis.

    Usage:
        client = OpenRouterClient()
        response = await client.complete(
            model="anthropic/claude-sonnet-4.5",
            messages=[{"role": "user", "content": "Hello"}],
            metadata={"experiment_id": "exp_phase1_step1_baseline_v1", "attack_id": "attack_001"}
        )
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not set. "
                "Set via: export OPENROUTER_API_KEY=your_key or pass to constructor"
            )

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def complete(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        metadata: Optional[Dict[str, str]] = None,
    ) -> OpenRouterResponse:
        """
        Call OpenRouter chat completion API.

        Args:
            model: Model identifier (e.g., "anthropic/claude-sonnet-4.5")
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            metadata: Experiment tracking metadata (experiment_id, attack_id, step, etc.)

        Returns:
            OpenRouterResponse with raw API response

        Raises:
            httpx.HTTPStatusError: On API errors (400, 429, 500, etc.)
            httpx.RequestError: On network errors
        """
        # Build request
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Add metadata if provided (Constitutional Principle VI: Data Provenance)
        if metadata:
            request_data["metadata"] = metadata

        try:
            response = await self.client.post(
                "/chat/completions",
                json=request_data,
            )
            response.raise_for_status()  # Fail-fast on HTTP errors

            raw_response = response.json()

            return OpenRouterResponse(
                id=raw_response.get("id", "unknown"),  # Handle missing id field
                model=raw_response.get("model", "unknown"),
                choices=raw_response.get("choices", []),
                usage=raw_response.get("usage", {}),
                raw_response=raw_response,
            )

        except httpx.HTTPStatusError as e:
            # Fail-fast with full context (Constitutional Principle IV)
            raise httpx.HTTPStatusError(
                message=f"OpenRouter API error for model {model}: {e.response.status_code} - {e.response.text}",
                request=e.request,
                response=e.response,
            )
        except httpx.RequestError as e:
            # Network errors
            raise httpx.RequestError(
                message=f"Network error calling OpenRouter for model {model}: {str(e)}",
            )

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Utility function for single completion
async def complete(
    model: str,
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 500,
    metadata: Optional[Dict[str, str]] = None,
) -> str:
    """
    Convenience function for single completion.

    Args:
        model: Model identifier
        prompt: User prompt text
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        metadata: Experiment tracking metadata

    Returns:
        Completion text

    Example:
        text = await complete(
            model="anthropic/claude-haiku-4.5",
            prompt="Classify this response...",
            metadata={"experiment_id": "exp_phase1_step1_baseline_v1"}
        )
    """
    async with OpenRouterClient() as client:
        response = await client.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            metadata=metadata,
        )
        return response.choices[0]["message"]["content"]
