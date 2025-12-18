"""Rate limiting utilities for controlling request frequency."""

import asyncio
import time
from typing import Optional


class RateLimiter:
    """
    Rate limiter to control the frequency of async operations.
    
    Supports two modes:
    - Semaphore-based: limits concurrent requests
    - Token bucket: limits requests per time window
    
    Usage:
        limiter = RateLimiter(max_requests=10, time_window=1.0)
        
        async with limiter:
            # Your API call here
            await client.request(...)
    """
    
    def __init__(
        self, 
        max_requests: int, 
        time_window: float = 1.0,
        mode: str = "token_bucket"
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds (for token_bucket mode)
            mode: "token_bucket" or "semaphore"
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.mode = mode
        
        if mode == "semaphore":
            self.semaphore = asyncio.Semaphore(max_requests)
        else:  # token_bucket
            self.tokens = max_requests
            self.last_update = time.monotonic()
            self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        if self.mode == "semaphore":
            await self.semaphore.acquire()
        else:  # token_bucket
            async with self.lock:
                now = time.monotonic()
                elapsed = now - self.last_update
                
                # Refill tokens based on elapsed time
                self.tokens = min(
                    self.max_requests,
                    self.tokens + elapsed * (self.max_requests / self.time_window)
                )
                self.last_update = now
                
                # Wait if no tokens available
                if self.tokens < 1:
                    wait_time = (1 - self.tokens) * (self.time_window / self.max_requests)
                    await asyncio.sleep(wait_time)
                    self.tokens = 0
                else:
                    self.tokens -= 1
    
    def release(self):
        """Release permission (only for semaphore mode)."""
        if self.mode == "semaphore":
            self.semaphore.release()
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False

