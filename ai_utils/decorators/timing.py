"""Timing decorator for measuring execution time of async functions."""

import time
from functools import wraps
from typing import Callable


def measure_time(func: Callable) -> Callable:
    """
    Decorator that measures and prints the execution time of async functions.
    
    Usage:
        @measure_time
        async def my_function():
            # Your code here
            pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        func_name = func.__name__
        # Extract URL from args if available for better logging
        url_info = f" for {args[0]}" if args and isinstance(args[0], str) and args[0].startswith("http") else ""
        
        try:
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            print(f"⏱️  {func_name}{url_info} completed in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            print(f"⏱️  {func_name}{url_info} failed after {elapsed:.3f}s: {e}")
            raise
    return wrapper

