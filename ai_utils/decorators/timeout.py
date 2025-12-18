"""Timeout decorator for async functions."""

import asyncio
from functools import wraps
from typing import Callable


def timeout(seconds: float):
    """
    Decorator that adds timeout functionality to async functions.
    
    Usage:
        @timeout(seconds=3)
        async def my_function():
            # Your code here
            pass
    
    Args:
        seconds: Maximum time in seconds the function can run before timing out
        
    Raises:
        asyncio.TimeoutError: If the function exceeds the timeout duration
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
        return wrapper
    return decorator

