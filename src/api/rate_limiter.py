"""
Rate Limiter with Exponential Backoff
Constitutional Principle IV: Fail-Fast
NFR2: Fail-Fast error handling

Manages concurrent API requests and retry logic.
"""

import asyncio
import time
from typing import Callable, TypeVar, Any
import httpx
from functools import wraps

T = TypeVar('T')


class RateLimiter:
    """
    Rate limiter with semaphore-based concurrency control.

    Limits concurrent API requests and implements exponential backoff retry.

    Usage:
        rate_limiter = RateLimiter(max_concurrent=10, max_retries=3)

        @rate_limiter.limit
        async def call_api(...):
            return await client.complete(...)

        result = await call_api(...)
    """

    def __init__(
        self,
        max_concurrent: int = 10,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ):
        """
        Initialize rate limiter.

        Args:
            max_concurrent: Maximum concurrent requests
            max_retries: Maximum retry attempts on rate limit/server errors
            base_delay: Base delay for exponential backoff (seconds)
            max_delay: Maximum delay cap (seconds)
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def limit(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to apply rate limiting and retry logic.

        Args:
            func: Async function to rate limit

        Returns:
            Wrapped function with rate limiting

        Example:
            @rate_limiter.limit
            async def call_api(model, prompt):
                return await client.complete(model=model, messages=[...])
        """

        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            async with self.semaphore:
                return await self._retry_with_backoff(func, *args, **kwargs)

        return wrapper

    async def _retry_with_backoff(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Execute function with exponential backoff retry.

        Retries on:
        - 429 (Rate Limit)
        - 5xx (Server Errors)

        Raises:
        - Original exception after max_retries exhausted
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                last_exception = e

                # Retry on rate limit (429) and server errors (5xx)
                if status_code == 429 or 500 <= status_code < 600:
                    if attempt < self.max_retries:
                        delay = min(
                            self.base_delay * (2 ** attempt),
                            self.max_delay
                        )
                        print(
                            f"Rate limit/server error {status_code}, "
                            f"retrying in {delay:.1f}s (attempt {attempt + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(delay)
                        continue

                # Don't retry on client errors (4xx except 429)
                raise

            except httpx.RequestError as e:
                # Network errors - retry with backoff
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(
                        self.base_delay * (2 ** attempt),
                        self.max_delay
                    )
                    print(
                        f"Network error, retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries}): {str(e)}"
                    )
                    await asyncio.sleep(delay)
                    continue
                raise

        # All retries exhausted - fail-fast with context
        raise last_exception


# Global rate limiter instance
_rate_limiter = RateLimiter(max_concurrent=10, max_retries=3)


def get_rate_limiter() -> RateLimiter:
    """
    Get global rate limiter instance.

    Usage:
        from src.api.rate_limiter import get_rate_limiter

        rate_limiter = get_rate_limiter()

        @rate_limiter.limit
        async def my_api_call(...):
            ...
    """
    return _rate_limiter
