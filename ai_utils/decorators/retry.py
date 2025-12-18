"""Retry decorator with exponential backoff for async functions."""

import asyncio
from functools import wraps
from typing import Callable


def retry(max_retries: int = 3, backoff: str = "exponential"):
    """
    Decorator that adds retry functionality to async functions with backoff.
    
    Usage:
        @retry(max_retries=3, backoff="exponential")
        async def my_function():
            # Your code here
            pass
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        backoff: Backoff strategy - "exponential" (2^attempt) or "linear" (attempt+1)
        
    Raises:
        The last exception if all retries are exhausted
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            # Extract URL from args if available for better logging
            url_info = f" for {args[0]}" if args and isinstance(args[0], str) and args[0].startswith("http") else ""
            
            for attempt in range(max_retries):
                if backoff == "exponential":
                    delay = 2 ** attempt
                else:  # linear
                    delay = attempt + 1
                
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        # Last attempt failed, raise the exception
                        raise e
                    # Log retry attempt
                    print(f"🔄 Retry {attempt + 1}/{max_retries} in {delay}s{url_info}: {type(e).__name__}")
                    await asyncio.sleep(delay)
                    continue
        return wrapper
    return decorator

