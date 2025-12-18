"""
python-ai-utils: Async utilities for building reliable AI API clients.

Main components:
- AsyncAPIClient: Async HTTP client with retries, timeouts, and rate limiting
- Decorators: timeout, retry, measure_time
- RateLimiter: Control request rate
- StructuredLogger: JSON-formatted logging for production
"""

from ai_utils.client import AsyncAPIClient
from ai_utils.decorators import measure_time, retry, timeout
from ai_utils.logging import StructuredLogger
from ai_utils.rate_limit import RateLimiter

__version__ = "0.1.0"

__all__ = [
    "AsyncAPIClient",
    "timeout",
    "retry",
    "measure_time",
    "RateLimiter",
    "StructuredLogger",
]

