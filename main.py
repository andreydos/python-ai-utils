import asyncio
from typing import Any, Coroutine, Callable
from functools import wraps
import time
import aiohttp


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
            print(f"⏱️  {func_name}{url_info} completed in {elapsed:.3f} seconds")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            print(f"⏱️  {func_name}{url_info} failed after {elapsed:.3f} seconds: {e}")
            raise
    return wrapper


def retry(max_retries: int = 3, backoff: str = "exponential"):
    """
    Decorator that adds retry functionality to async functions with exponential backoff.
    
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
                    print(f"Retry {attempt + 1} of {max_retries} in {delay} seconds{url_info}: {type(e).__name__}")
                    await asyncio.sleep(delay)
                    continue
        return wrapper
    return decorator


# Helper function with timeout decorator applied to GET request
@timeout(seconds=10)
async def get_with_timeout(session: aiohttp.ClientSession, url: str):
    """Get request with 10-second timeout"""
    return await session.get(url)

@retry(max_retries=5, backoff="exponential")
@measure_time
async def fetch(url: str) -> str:
    """
    Fetch URL with retry logic for HTTP errors.
    Note: @retry decorator handles all exceptions (including HTTP errors and timeouts).
    """
    async with aiohttp.ClientSession() as session:
        response = await get_with_timeout(session, url)
        async with response:
            print(f"Response status: {response.status} for {url}")
            if response.status >= 400:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"HTTP {response.status} error for {url}"
                )
            return await response.text()

    

@measure_time
async def main():
    urls: list[str] = [
        "https://postman-echo.com/delay/7",
    ]

    tasks: list[Coroutine[Any, Any, str]] = [fetch(url) for url in urls]
    # Handle errors for each request
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            print(f"Error for {url}: {result}")
        else:
            print(f"Response length for {url}: {len(result)}")

asyncio.run(main())