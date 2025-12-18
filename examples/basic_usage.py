"""
Basic usage example of AsyncAPIClient.

Demonstrates:
- Simple GET/POST requests
- Context manager usage
- Error handling
"""

import asyncio

from ai_utils import AsyncAPIClient


async def main():
    # Create client with context manager (auto-closes connection)
    async with AsyncAPIClient(
        base_url="https://httpbin.org",
        timeout=10.0
    ) as client:
        
        print("=" * 60)
        print("Example 1: Simple GET request")
        print("=" * 60)
        
        # GET request
        response = await client.get("/get", params={"foo": "bar"})
        print(f"Response: {response.get('args')}")
        
        print("\n" + "=" * 60)
        print("Example 2: POST request with JSON")
        print("=" * 60)
        
        # POST request with JSON data
        response = await client.post(
            "/post",
            json={"message": "Hello from python-ai-utils!"}
        )
        print(f"Sent: {response.get('json')}")
        
        print("\n" + "=" * 60)
        print("Example 3: Request with custom headers")
        print("=" * 60)
        
        # Request with custom headers
        response = await client.get(
            "/headers",
            headers={"X-Custom-Header": "MyValue"}
        )
        print(f"Headers received by server: {response.get('headers', {}).get('X-Custom-Header')}")


if __name__ == "__main__":
    asyncio.run(main())

