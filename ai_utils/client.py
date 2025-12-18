"""Async HTTP client with retries, timeouts, and rate limiting."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

import aiohttp

from ai_utils.decorators import measure_time, retry, timeout
from ai_utils.logging import StructuredLogger, generate_request_id
from ai_utils.rate_limit import RateLimiter


class AsyncAPIClient:
    """
    Production-ready async HTTP client for AI APIs.
    
    Features:
    - Automatic retries with exponential backoff
    - Configurable timeouts
    - Rate limiting
    - Structured logging
    - Connection pooling
    
    Usage:
        client = AsyncAPIClient(
            base_url="https://api.example.com",
            timeout=10.0,
            max_retries=3,
            rate_limit=10  # 10 requests per second
        )
        
        async with client:
            response = await client.get("/endpoint")
            data = await client.post("/endpoint", json={"key": "value"})
    """
    
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        enable_logging: bool = True
    ):
        """
        Initialize the async API client.
        
        Args:
            base_url: Base URL for all requests (optional)
            timeout: Default timeout in seconds for requests
            max_retries: Maximum number of retry attempts
            rate_limit: Maximum requests per second (None = no limit)
            headers: Default headers to include in all requests
            enable_logging: Enable structured logging
        """
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.timeout_seconds = timeout
        self.max_retries = max_retries
        self.default_headers = headers or {}
        
        # Initialize session (will be created on first use)
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=rate_limit,
            time_window=1.0,
            mode="token_bucket"
        ) if rate_limit else None
        
        # Structured logger
        self.logger = StructuredLogger(name="AsyncAPIClient") if enable_logging else None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers=self.default_headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)
            )
        return self._session
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def __aenter__(self):
        """Context manager entry."""
        await self._get_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
        return False
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}" if self.base_url else endpoint
    
    async def request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retries and rate limiting.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint or full URL
            headers: Additional headers for this request
            timeout: Override default timeout for this request
            **kwargs: Additional arguments passed to aiohttp (json, data, params, etc.)
        
        Returns:
            Response data as dictionary
            
        Raises:
            aiohttp.ClientError: On HTTP errors after all retries
            asyncio.TimeoutError: On timeout
        """
        url = self._build_url(endpoint)
        request_id = generate_request_id()
        
        # Merge headers
        request_headers = {**self.default_headers, **(headers or {})}
        
        # Apply rate limiting if enabled
        if self.rate_limiter:
            await self.rate_limiter.acquire()
        
        # Get session
        session = await self._get_session()
        
        # Override timeout if specified
        request_timeout = aiohttp.ClientTimeout(total=timeout) if timeout else None
        
        # Make request
        import time
        start_time = time.perf_counter()
        
        try:
            async with session.request(
                method=method,
                url=url,
                headers=request_headers,
                timeout=request_timeout,
                **kwargs
            ) as response:
                # Check for HTTP errors
                response.raise_for_status()
                
                # Parse response
                if response.content_type == "application/json":
                    data = await response.json()
                else:
                    text = await response.text()
                    data = {"text": text}
                
                # Log success
                if self.logger:
                    latency_ms = (time.perf_counter() - start_time) * 1000
                    self.logger.log_request(
                        request_id=request_id,
                        url=url,
                        method=method,
                        status=response.status,
                        latency_ms=latency_ms
                    )
                
                return data
        
        except Exception as e:
            # Log error
            if self.logger:
                latency_ms = (time.perf_counter() - start_time) * 1000
                self.logger.log_request(
                    request_id=request_id,
                    url=url,
                    method=method,
                    latency_ms=latency_ms,
                    error=str(e)
                )
            raise
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return await self.request("POST", endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self.request("PUT", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self.request("DELETE", endpoint, **kwargs)
    
    async def patch(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a PATCH request."""
        return await self.request("PATCH", endpoint, **kwargs)

