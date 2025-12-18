"""
Example demonstrating retry functionality.

Shows how the client handles:
- Failed requests
- Automatic retries
- Exponential backoff
"""

import asyncio

from ai_utils import AsyncAPIClient


async def main():
    print("=" * 60)
    print("Testing retry logic with failing endpoint")
    print("=" * 60)
    
    async with AsyncAPIClient(
        base_url="https://httpbin.org",
        timeout=5.0,
        max_retries=3
    ) as client:
        
        # This endpoint returns 500 error - will trigger retries
        try:
            print("\nAttempting request to /status/500 (will fail)...")
            response = await client.get("/status/500")
        except Exception as e:
            print(f"\n❌ Request failed after retries: {type(e).__name__}")
        
        print("\n" + "=" * 60)
        print("Testing successful request (no retries needed)")
        print("=" * 60)
        
        # This endpoint returns 200 - will succeed immediately
        print("\nAttempting request to /status/200 (will succeed)...")
        response = await client.get("/status/200")
        print("✅ Request succeeded!")
        
        print("\n" + "=" * 60)
        print("Testing timeout")
        print("=" * 60)
        
        # This endpoint delays 10 seconds, but we have 5s timeout
        try:
            print("\nAttempting request with delay > timeout...")
            response = await client.get("/delay/10")
        except asyncio.TimeoutError:
            print("❌ Request timed out (as expected)")


if __name__ == "__main__":
    asyncio.run(main())

