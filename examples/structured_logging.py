"""
Example demonstrating structured logging.

Shows:
- JSON-formatted logs
- Request tracing with IDs
- Production-ready logging patterns
"""

import asyncio

from ai_utils import AsyncAPIClient, StructuredLogger


async def main():
    print("=" * 60)
    print("Example: Structured Logging (JSON output)")
    print("=" * 60)
    print("\nAll logs below are in JSON format - perfect for production!\n")
    
    # Create client with logging enabled (default)
    async with AsyncAPIClient(
        base_url="https://httpbin.org",
        timeout=10.0,
        enable_logging=True  # This is default
    ) as client:
        
        # Make requests - each will be logged with structured data
        print("Making requests...\n")
        
        await client.get("/get")
        await client.post("/post", json={"test": "data"})
        
        # This will log an error
        try:
            await client.get("/status/404")
        except Exception:
            pass
    
    print("\n" + "=" * 60)
    print("Example: Using StructuredLogger directly")
    print("=" * 60 + "\n")
    
    # You can also use the logger independently
    logger = StructuredLogger(name="my_app")
    
    logger.info("Application started", version="0.1.0", env="development")
    logger.warning("Rate limit approaching", current_rate=95, limit=100)
    logger.error("Failed to connect", service="database", error="Connection timeout")
    
    # Log a request manually
    logger.log_request(
        request_id="req_abc123",
        url="https://api.example.com/chat",
        method="POST",
        status=200,
        latency_ms=234.5
    )
    
    # Log a retry attempt
    logger.log_retry(
        request_id="req_def456",
        attempt=2,
        max_attempts=3,
        error="Connection timeout",
        delay_seconds=4.0
    )


if __name__ == "__main__":
    asyncio.run(main())

