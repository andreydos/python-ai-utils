"""
Example of using decorators independently (without AsyncAPIClient).

Shows how to use:
- @timeout decorator
- @retry decorator
- @measure_time decorator
"""

import asyncio

import aiohttp

from ai_utils.decorators import measure_time, retry, timeout


# Example 1: Using @timeout decorator
@timeout(seconds=3)
async def fetch_with_timeout(url: str) -> str:
    """Fetch URL with 3-second timeout."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


# Example 2: Using @retry decorator
@retry(max_retries=3, backoff="exponential")
async def fetch_with_retry(url: str) -> dict:
    """Fetch URL with automatic retries on failure."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status >= 400:
                raise Exception(f"HTTP {response.status}")
            return await response.json()


# Example 3: Combining decorators
@retry(max_retries=3, backoff="exponential")
@measure_time
@timeout(seconds=5)
async def fetch_with_all(url: str) -> dict:
    """Fetch URL with timeout, retries, and timing measurement."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()


# Example 4: Custom async function with timing
@measure_time
async def slow_computation():
    """Simulate a slow async computation."""
    await asyncio.sleep(2)
    return "Computation complete!"


async def main():
    print("=" * 60)
    print("Example 1: @timeout decorator")
    print("=" * 60)
    
    try:
        # This should succeed (fast endpoint)
        result = await fetch_with_timeout("https://httpbin.org/get")
        print("✅ Fast request succeeded\n")
    except asyncio.TimeoutError:
        print("❌ Request timed out\n")
    
    print("=" * 60)
    print("Example 2: @retry decorator")
    print("=" * 60)
    
    try:
        # This will retry on 500 error
        result = await fetch_with_retry("https://httpbin.org/status/500")
    except Exception as e:
        print(f"❌ Failed after all retries: {e}\n")
    
    print("=" * 60)
    print("Example 3: Combining all decorators")
    print("=" * 60)
    
    try:
        result = await fetch_with_all("https://httpbin.org/json")
        print(f"✅ Request succeeded! Got {len(result)} keys\n")
    except Exception as e:
        print(f"❌ Request failed: {e}\n")
    
    print("=" * 60)
    print("Example 4: @measure_time on custom function")
    print("=" * 60)
    
    result = await slow_computation()
    print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())

