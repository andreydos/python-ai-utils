"""
Demo script showing the python-ai-utils library in action.

This replaces the original prototype code with the new library.
For more examples, see the examples/ directory.
"""

import asyncio

from ai_utils import AsyncAPIClient


async def main():
    print("=" * 70)
    print("python-ai-utils - Production-Ready Async API Client")
    print("=" * 70)
    print()
    
    # Create client with all features enabled
    async with AsyncAPIClient(
        base_url="https://httpbin.org",
        timeout=10.0,
        max_retries=3,
        rate_limit=5,  # 5 requests per second
        enable_logging=True
    ) as client:
        
        print("🔹 Making test requests...\n")
        
        # Test 1: Simple GET
        print("1️⃣  GET /get")
        response = await client.get("/get", params={"test": "value"})
        print(f"   ✅ Success! Args: {response.get('args')}\n")
        
        # Test 2: POST with JSON
        print("2️⃣  POST /post")
        response = await client.post("/post", json={"message": "Hello!"})
        print(f"   ✅ Success! Sent: {response.get('json')}\n")
        
        # Test 3: Concurrent requests with rate limiting
        print("3️⃣  Making 5 concurrent requests (rate limited to 5/s)...")
        tasks = [client.get(f"/get?id={i}") for i in range(5)]
        results = await asyncio.gather(*tasks)
        print(f"   ✅ All {len(results)} requests completed!\n")
        
        # Test 4: Error handling (will retry and then fail)
        print("4️⃣  Testing error handling with /status/500...")
        try:
            await client.get("/status/500")
        except Exception as e:
            print(f"   ✅ Handled gracefully: {type(e).__name__}\n")
    
    print("=" * 70)
    print("✨ Demo complete! Check examples/ for more use cases.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
