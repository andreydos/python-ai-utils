"""
Example demonstrating rate limiting.

Shows how to:
- Limit requests per second
- Make concurrent requests safely
- Avoid API rate limit errors
"""

import asyncio
import time

from ai_utils import AsyncAPIClient


async def make_request(client: AsyncAPIClient, request_num: int):
    """Make a single request and track timing."""
    start = time.time()
    try:
        await client.get(f"/get?request={request_num}")
        elapsed = time.time() - start
        print(f"✅ Request {request_num:2d} completed in {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Request {request_num:2d} failed after {elapsed:.2f}s: {e}")


async def main():
    print("=" * 60)
    print("Example: Rate limiting (5 requests per second)")
    print("=" * 60)
    
    # Create client with rate limiting
    async with AsyncAPIClient(
        base_url="https://httpbin.org",
        timeout=10.0,
        rate_limit=5  # Maximum 5 requests per second
    ) as client:
        
        print("\nMaking 10 concurrent requests...")
        print("(Rate limiter will ensure max 5 req/s)\n")
        
        start_time = time.time()
        
        # Create 10 concurrent requests
        tasks = [make_request(client, i+1) for i in range(10)]
        await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        print(f"\n✨ All 10 requests completed in {total_time:.2f}s")
        print(f"   Average rate: {10/total_time:.2f} req/s (should be ~5 req/s)")
    
    print("\n" + "=" * 60)
    print("Example: Without rate limiting (faster but risky)")
    print("=" * 60)
    
    # Same requests without rate limiting
    async with AsyncAPIClient(
        base_url="https://httpbin.org",
        timeout=10.0,
        rate_limit=None  # No rate limiting
    ) as client:
        
        print("\nMaking 10 concurrent requests without rate limiting...\n")
        
        start_time = time.time()
        
        tasks = [make_request(client, i+1) for i in range(10)]
        await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        print(f"\n✨ All 10 requests completed in {total_time:.2f}s")
        print(f"   Average rate: {10/total_time:.2f} req/s (much faster!)")


if __name__ == "__main__":
    asyncio.run(main())

